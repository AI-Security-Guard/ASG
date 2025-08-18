import os
import cv2
import time
import json
import math
import sqlite3
import numpy as np
from collections import deque
from typing import List, Dict, Any
import torch
from torchvision import transforms
from models.models import DFGAR as DFWSGARModel
from utils.utils import (
    fuse_tokens_spatial,
    heatmap_to_point,
    smooth_point,
    calculate_box_coordinates,
    TOP_PCT, ALPHA_HM, ALPHA_PT, JUMP_MAX_PIX, JUMP_BLEND,
    BOX_FRAC_W, BOX_FRAC_H
)

# 전역 설정/상수
CLASS_NAMES: List[str] = ["normal", "assault"]

RESIZE_W, RESIZE_H = 640, 360
STRIDE = 6
TEMP = 2.0
PROB_THRESH = 0.80
MARGIN_THRESH = 1.00
USE_EMA = True
EMA_ALPHA_P = 0.15
EMA_RESET_EACH_WINDOW = False

MODEL_PATH = "model/best_model.pth"
THRESHOLD_PATH = "model/best_threshold.txt"

# 디스크 저장 폴더
ANNOTATED_DIR = "analyzed_videos"      # 주석(박스) 영상
CLIPS_DIR = "event_clips"              # 비정상 구간 클립 모음 (주석영상에서 추출)
CLIPS_INFO_DIR = "clip_summaries"      # 클립 메타정보(JSON)
os.makedirs(ANNOTATED_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(CLIPS_INFO_DIR, exist_ok=True)

# DB (SQLite) — 최소 payload만 저장
DB_PATH = "jobs.db"


# DB 유틸 (최소 필드만 보존)
def _db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs(
        job_id TEXT PRIMARY KEY,
        payload TEXT NOT NULL
    )
    """)
    return conn

_DB_CONN = _db()

def _sanitize_job_for_db(job: Dict[str, Any]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {"job_id": job.get("job_id")}
    res = job.get("results")
    if isinstance(res, dict):
        allowed = {"video_path", "annotated_video", "num_clips", "clips_info_json"}
        safe["results"] = {k: v for k, v in res.items() if k in allowed}
    else:
        safe["results"] = None
    return safe

def db_upsert_job(job: Dict[str, Any]):
    payload = json.dumps(_sanitize_job_for_db(job), ensure_ascii=False)
    cur = _DB_CONN.cursor()
    cur.execute("""
        INSERT INTO jobs (job_id, payload)
        VALUES (?, ?)
        ON CONFLICT(job_id) DO UPDATE SET payload=excluded.payload
    """, (job.get("job_id"), payload))
    _DB_CONN.commit()

def db_get_job(job_id: str) -> Dict[str, Any] | None:
    cur = _DB_CONN.cursor()
    cur.execute("SELECT payload FROM jobs WHERE job_id = ?", (job_id,))
    row = cur.fetchone()
    if not row:
        return None
    return json.loads(row[0])

# 유틸
def idx_of(name: str) -> int:
    try:
        return CLASS_NAMES.index(name)
    except ValueError:
        return -1

def build_args_for_model():
    class Args:
        def __init__(self):
            self.dataset = 'optimized_dataset'
            self.num_activities = 2
            self.num_frame = 18
            self.hidden_dim = 256
            self.num_tokens = 6
            self.nheads_agg = 4
            self.drop_rate = 0.1
            self.position_embedding = 'sine'
            self.dilation = False
            self.nheads = 8
            self.ffn_dim = 512
            self.enc_layers = 1
            self.pre_norm = False
            self.backbone = 'resnet18'
            self.motion = True
            self.motion_layer = 3
            self.multi_corr = True
            self.corr_dim = 64
            self.neighbor_size = 2
            self.task_mode = 'group_activity'
    return Args()

def frames_to_tensor_batch(frames_bgr, device):
    xt = [transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])(
        transforms.functional.to_tensor(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    ) for f in frames_bgr]
    x = torch.stack(xt, dim=0)[None].to(device)  # [1,T,3,H,W]
    return x

def _render_annotated_video_inline(video_path: str, detections: list, out_path: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30.0
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (orig_w, orig_h))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(f"Failed to open VideoWriter: {out_path}")
    sx = orig_w / float(RESIZE_W); sy = orig_h / float(RESIZE_H)
    det_by_frame = {d["frame_idx"]: d for d in detections}
    fidx = 0
    while True:
        ok, frame = cap.read()
        if not ok: break
        det = det_by_frame.get(fidx)
        if det is not None:
            is_positive = bool(det.get("is_assault", False)) or (str(det.get("top1_class_name","")).lower() != "normal")
            if is_positive:
                toks = det.get("tokens", [])
                if toks:
                    box = toks[0].get("box")
                    if box:
                        x1,y1,x2,y2 = box
                        X1 = int(round(x1 * sx)); Y1 = int(round(y1 * sy))
                        X2 = int(round(x2 * sx)); Y2 = int(round(y2 * sy))
                        cv2.rectangle(frame, (X1, Y1), (X2, Y2), (0,0,255), 2)
        writer.write(frame); fidx += 1
    cap.release(); writer.release()
    return out_path

def _format_time_hhmmss(seconds: float) -> str:
    if seconds < 0: seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(round(seconds % 60))
    return f"{h:02d}:{m:02d}:{s:02d}"

def _find_positive_segments(detections: List[Dict[str, Any]]) -> List[Dict[str, int]]:
    segs = []
    in_seg = False
    seg_start = None
    seg_class = None
    for det in detections:
        fidx = det["frame_idx"]
        top1 = str(det.get("top1_class_name","")).lower()
        is_pos = (top1 != "normal") or bool(det.get("is_assault", False))
        if is_pos and not in_seg:
            in_seg = True
            seg_start = fidx
            seg_class = det.get("top1_class_name", "unknown")
        elif (not is_pos) and in_seg:
            segs.append({"start": seg_start, "end": fidx - 1, "class_name": seg_class})
            in_seg = False
    if in_seg and len(detections) > 0:
        segs.append({"start": seg_start, "end": detections[-1]["frame_idx"], "class_name": seg_class})
    return segs

def _merge_segments_with_tolerance(segs: List[Dict[str,int]], fps: float, tol_sec: float = 2.0) -> List[Dict[str,int]]:
    if not segs:
        return []
    tol_frames = int(math.ceil((fps if fps > 0 else 30.0) * tol_sec))  # 2.0초까지 포함
    merged = [segs[0].copy()]
    for s in segs[1:]:
        prev = merged[-1]
        same_cls = (str(prev["class_name"]).lower() == str(s["class_name"]).lower())
        gap = s["start"] - prev["end"] - 1  # 사이 normal 프레임 수
        if same_cls and gap <= tol_frames:
            prev["end"] = max(prev["end"], s["end"])
        else:
            merged.append(s.copy())
    return merged

def _first_bbox_on_frame(det: Dict[str, Any]) -> tuple | None:
    toks = det.get("tokens", [])
    if not toks:
        return None
    return toks[0].get("box")

def _write_clip(video_path: str, start_f: int, end_f: int, out_path: str, fps_hint: float | None = None) -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video for clipping: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or (fps_hint or 30.0)
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (orig_w, orig_h))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(f"Failed to open VideoWriter for clip: {out_path}")
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, start_f))
    fidx = start_f
    while fidx <= end_f:
        ok, frame = cap.read()
        if not ok: break
        writer.write(frame)
        fidx += 1
    cap.release(); writer.release()
    return out_path

def _generate_event_clips_and_info(
    *,
    video_path_for_meta: str,             # 메타에 기록할 원본 경로(표시용)
    clip_source_video_path: str,          # 실제로 자를 소스(주석 영상 경로 사용!)
    detections: List[Dict[str, Any]],
    resize_w: int,
    resize_h: int,
    clips_dir: str,
    info_dir: str,
    fps: float
) -> tuple[list, str]:

    base = os.path.splitext(os.path.basename(video_path_for_meta))[0]

    # 1) 연속 구간 → 2초 이하 normal 간격 병합
    segs_raw = _find_positive_segments(detections)
    segs = _merge_segments_with_tolerance(segs_raw, fps=fps, tol_sec=2.0)

    if not segs:
        info_path = os.path.join(info_dir, f"{base}_clips.json")
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump({"video": video_path_for_meta, "num_clips": 0, "clips": []}, f, ensure_ascii=False, indent=2)
        return [], info_path

    # 2) 프레임->det, 스케일
    det_map = {d["frame_idx"]: d for d in detections}

    cap = cv2.VideoCapture(video_path_for_meta)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video for meta: {video_path_for_meta}")
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    sx = orig_w / float(resize_w)
    sy = orig_h / float(resize_h)

    clips_meta = []
    clip_id = 1

    for seg in segs:
        s, e = seg["start"], seg["end"]
        cls_name = seg["class_name"]

        # 시작 프레임 박스 (주석 영상에 이미 그려지지만, 메타에는 원본 좌표로 기록)
        det0 = det_map.get(s)
        start_box_resize = _first_bbox_on_frame(det0) if det0 else None
        if start_box_resize:
            x1,y1,x2,y2 = start_box_resize
            start_box_orig = [int(round(x1*sx)), int(round(y1*sy)),
                              int(round(x2*sx)), int(round(y2*sy))]
        else:
            start_box_orig = None

        clip_name = f"{base}_clip{clip_id}.mp4"
        clip_path = os.path.join(clips_dir, clip_name)

        # ✅ 주석 영상(clip_source_video_path)에서 자르기 → 박스가 출력에 포함됨
        _write_clip(clip_source_video_path, s, e, clip_path, fps_hint=fps)

        start_time_str = _format_time_hhmmss(s / fps if fps > 0 else 0.0)

        meta = {
            "clip_id": clip_id,
            "class_name": cls_name,
            "start_time": start_time_str,
            "start_bbox": start_box_orig,
            "clip_name": clip_name,
            "clip_path": clip_path
        }
        clips_meta.append(meta)
        clip_id += 1

    info_obj = {"video": video_path_for_meta, "num_clips": len(clips_meta), "clips": clips_meta}
    info_path = os.path.join(info_dir, f"{base}_clips.json")
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info_obj, f, ensure_ascii=False, indent=2)

    return clips_meta, info_path


# 디바이스/모델 로드
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #GPU 사용시 활성화 ( CPU 사용시 주석 처리 필수! )
device = torch.device("cpu") #CPU 사용시 활성화( GPU 사용시 주석 처리 필수! )

_args = build_args_for_model()
model = DFWSGARModel(_args).to(device).eval()

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

ck = torch.load(MODEL_PATH, map_location=device)
if not (isinstance(ck, dict) and "state_dict" in ck):
    raise KeyError(f"Expected checkpoint with key 'state_dict', got keys={list(ck.keys()) if isinstance(ck, dict) else type(ck)}")
sd = {(k[7:] if k.startswith("module.") else k): v for k, v in ck["state_dict"].items()}
_ = model.load_state_dict(sd, strict=False)

prob_threshold: float = float(PROB_THRESH)
if os.path.exists(THRESHOLD_PATH):
    try:
        with open(THRESHOLD_PATH, "r") as f:
            prob_threshold = float(f.read().strip())
    except Exception:
        pass

torch.set_grad_enabled(False)

# 작업 상태 (메모리 최소)
processing_jobs: Dict[str, Dict[str, Any]] = {}

# 핵심: 동기 분석 (비동기 스레드에서 호출)
def analyze_video_pure(job_id: str, video_path: str):
    try:
        # 초기 스냅샷 저장
        db_upsert_job({"job_id": job_id, "results": None})

        threshold = prob_threshold

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"비디오 열기 실패: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        assault_mask = np.zeros(max(total_frames, 1), dtype=np.uint8)

        buf_bgr = deque(maxlen=_args.num_frame)
        while len(buf_bgr) < _args.num_frame:
            ok, f = cap.read()
            if not ok:
                break
            f = cv2.resize(f, (RESIZE_W, RESIZE_H), interpolation=cv2.INTER_AREA)
            buf_bgr.append(f)

        # 단일 토큰(1개)만 추적 (fuse 사용)
        prev_pt = None
        hm_ema  = None

        frame_base_idx = 0
        p_assault_ema = None
        win_counter = 0

        detections = []   # 주석/클립 생성용 내부 결과
        assault_frames = 0
        processed_frames = 0

        while len(buf_bgr) == _args.num_frame:
            if EMA_RESET_EACH_WINDOW:
                p_assault_ema = None

            frames_list = list(buf_bgr)
            x_bthwc = frames_to_tensor_batch(frames_list, device)  # [1,T,3,H,W]
            x_btchw = x_bthwc[0]                                    # [T,3,H,W]

            logits = model(x_bthwc) / TEMP
            probs = torch.softmax(logits, dim=1)[0].detach().cpu().numpy()
            pred_idx = int(np.argmax(probs))
            top1_name = CLASS_NAMES[pred_idx] if 0 <= pred_idx < len(CLASS_NAMES) else str(pred_idx)
            top1_prob = float(probs[pred_idx])

            aid = idx_of("assault")
            p_assault_raw = float(probs[aid]) if 0 <= aid < len(probs) else 0.0

            # margin
            if aid >= 0 and logits.shape[1] > 1 and aid < logits.shape[1]:
                logit_vec = logits[0]
                if logit_vec.shape[0] > 1:
                    other_left = logit_vec[:aid]
                    other_right = logit_vec[aid+1:]
                    candidates = []
                    if other_left.numel() > 0: candidates.append(torch.max(other_left).item())
                    if other_right.numel() > 0: candidates.append(torch.max(other_right).item())
                    best_other = max(candidates) if candidates else 0.0
                else:
                    best_other = 0.0
                margin = float(logit_vec[aid].item() - best_other)
            else:
                margin = 0.0

            # EMA
            p_assault_ema = p_assault_raw if (p_assault_ema is None or not USE_EMA) \
                else (1 - EMA_ALPHA_P) * p_assault_ema + EMA_ALPHA_P * p_assault_raw

            # 판정
            is_assault_base = (aid >= 0) and (p_assault_ema >= threshold) and (margin >= MARGIN_THRESH)

            st, ed = frame_base_idx, frame_base_idx + _args.num_frame - 1
            if is_assault_base and st < len(assault_mask):
                assault_mask[st: min(ed + 1, len(assault_mask))] = 1

            # 백본/어텐션 → 단일 히트맵(fuse)
            src, pos = model.backbone(x_btchw)                      # [T,C,oh,ow], [T,C,oh,ow]
            T_, C_, oh, ow = src.shape
            src_proj = model.input_proj(src)                        # [T,D,oh,ow]
            _, att = model.token_encoder(src_proj, None, model.query_embed.weight, pos)
            if att.dim() == 5:
                att = att[0]

            write_range = range(T_) if frame_base_idx == 0 else range(T_ - STRIDE, T_)

            for t in range(T_):
                fidx = frame_base_idx + t
                if fidx >= len(assault_mask):
                    assault_mask = np.pad(assault_mask, (0, (fidx + 1 - len(assault_mask))), constant_values=0)

                # 단일 히트맵 생성
                if att.dim() == 3:       # [T,Q,HW]
                    att_t = att[t]       # [Q,HW]
                elif att.dim() == 4:     # [T,H,Q,K]
                    att_t = att[t]       # [H,Q,K]
                else:
                    raise RuntimeError(f"Unexpected att shape: {tuple(att.shape)}")

                p_map = fuse_tokens_spatial(att_t, oh, ow)
                p_up  = cv2.resize(p_map, (RESIZE_W, RESIZE_H), interpolation=cv2.INTER_LINEAR)
                p_up  = np.clip(p_up, 0.0, 1.0)

                hm_ema = p_up.copy() if hm_ema is None else (1 - ALPHA_HM) * hm_ema + ALPHA_HM * p_up
                cx, cy = heatmap_to_point(hm_ema, mode='centroid', top_pct=TOP_PCT)
                prev_pt = smooth_point(prev_pt, (cx, cy), alpha=ALPHA_PT,
                                       jump_max=JUMP_MAX_PIX, jump_blend=JUMP_BLEND)
                box = calculate_box_coordinates(prev_pt, RESIZE_W, RESIZE_H, BOX_FRAC_W, BOX_FRAC_H)

                if t in write_range:
                    top1_is_normal = (str(top1_name).lower() == "normal")
                    detections.append({
                        "frame_idx": fidx,
                        "timestamp": fidx / fps if fps > 0 else 0.0,
                        "p_assault_raw": float(p_assault_raw),
                        "p_assault_ema": float(p_assault_ema),
                        "margin": float(margin),
                        "is_assault": bool(assault_mask[fidx]),
                        "window_assault": is_assault_base,
                        "top1_class_index": pred_idx,
                        "top1_class_name": top1_name,
                        "top1_prob": top1_prob,
                        # ✅ 단일 박스만 기록
                        "tokens": [{
                            "token_id": 0,
                            "cx": float(prev_pt[0]),
                            "cy": float(prev_pt[1]),
                            "box": box
                        }]
                    })

                    if assault_mask[fidx] or (not top1_is_normal):
                        assault_frames += 1
                    processed_frames += 1

            # 슬라이드
            advanced = 0
            for _ in range(STRIDE):
                ok, f = cap.read()
                if not ok: break
                f = cv2.resize(f, (RESIZE_W, RESIZE_H), interpolation=cv2.INTER_AREA)
                buf_bgr.append(f); advanced += 1
            frame_base_idx += STRIDE
            if advanced < STRIDE: break

            win_counter += 1
            if win_counter % 10 == 0:
                time.sleep(0.001)

        cap.release()

        # (A) 주석 영상 생성 (단일 박스)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        annotated_path = os.path.join(ANNOTATED_DIR, f"{base_name}_analyze.mp4")
        _render_annotated_video_inline(video_path, detections, annotated_path)

        # (B) 주석 영상에서 클립 생성 + 메타 JSON 저장 (2초 이내 동일 클래스 병합)
        clips_meta, clips_info_path = _generate_event_clips_and_info(
            video_path_for_meta=video_path,
            clip_source_video_path=annotated_path,  # ✅ 박스가 그려진 영상에서 추출
            detections=detections,
            resize_w=RESIZE_W,
            resize_h=RESIZE_H,
            clips_dir=CLIPS_DIR,
            info_dir=CLIPS_INFO_DIR,
            fps=fps
        )

        # (C) DB/응답 결과(최소)
        result = {
            "video_path": video_path,
            "annotated_video": annotated_path,
            "num_clips": len(clips_meta),
            "clips_info_json": clips_info_path
        }

        processing_jobs[job_id] = {"job_id": job_id, "results": result}
        db_upsert_job(processing_jobs[job_id])

    except Exception:
        processing_jobs[job_id] = {"job_id": job_id, "results": None}
        db_upsert_job(processing_jobs[job_id])
