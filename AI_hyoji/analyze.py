import os
import cv2
import json
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
CLIPS_DIR = "event_clips"              # 비정상 구간 클립 모음 (주석영상에서 즉시 추출, 1패스)
CLIPS_INFO_DIR = "clip_summaries"      # 클립 메타정보(JSON)
os.makedirs(ANNOTATED_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(CLIPS_INFO_DIR, exist_ok=True)

# DB (SQLite) — payload에 최소 데이터 + 진행률(progress) 포함
DB_PATH = "jobs.db"


# DB 유틸 (최소 필드 + progress)
def _db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs(
        job_id  TEXT PRIMARY KEY,
        payload TEXT NOT NULL
    )
    """)
    return conn

_DB_CONN = _db()

def _sanitize_job_for_db(job: Dict[str, Any]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {"job_id": job.get("job_id")}
    if "progress" in job and isinstance(job["progress"], (int, float)):
        safe["progress"] = float(job["progress"])
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

def _format_time_hhmmss(seconds: float) -> str:
    if seconds < 0: seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(round(seconds % 60))
    return f"{h:02d}:{m:02d}:{s:02d}"


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


# 1패스 분석 + 주석영상 스트리밍 + 클립 동시 생성
def analyze_video_pure(job_id: str, video_path: str):
    try:
        # 초기 DB 스냅샷 (progress 포함)
        processing_jobs[job_id] = {"job_id": job_id, "progress": 0.0, "results": None}
        db_upsert_job(processing_jobs[job_id])

        threshold = prob_threshold

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"비디오 열기 실패: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 주석 영상 writer (원본 해상도)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        annotated_path = os.path.join(ANNOTATED_DIR, f"{base_name}_analyze.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        annot_writer = cv2.VideoWriter(annotated_path, fourcc, fps, (orig_w, orig_h))
        if not annot_writer.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open VideoWriter: {annotated_path}")

        # 2초 병합용 tol 프레임 수
        tol_frames = int(round((fps if fps > 0 else 30.0) * 2.0))

        # 슬라이딩 버퍼 (원본/리사이즈 둘 다)
        buf_small = deque(maxlen=_args.num_frame)  # 640x360
        buf_orig  = deque(maxlen=_args.num_frame)  # 원본 해상도

        # 초기 버퍼 채우기
        while len(buf_small) < _args.num_frame:
            ok, fr = cap.read()
            if not ok:
                break
            fr_orig = fr  # 원본 프레임
            fr_small = cv2.resize(fr_orig, (RESIZE_W, RESIZE_H), interpolation=cv2.INTER_AREA)
            buf_small.append(fr_small)
            buf_orig.append(fr_orig)

        # 토큰 융합 기반 단일 박스 추적용 상태
        prev_pt = None
        hm_ema  = None

        frame_base_idx = 0
        p_assault_ema = None

        # 진행률 저장용
        written_frames = 0
        last_saved_progress = -1.0  # DB 쓰기 빈도 줄이기

        # 클립 상태머신 (1패스)
        clips_meta: List[Dict[str, Any]] = []
        clip_id = 0
        active_clip = None           # cv2.VideoWriter | None
        active_class = None          # 현재 녹화중 클래스명
        in_gap = False
        gap_buf = []                 # 주석 프레임 임시 보관 (RAM)
        start_bbox_orig = None       # 새 클립 시작 bbox(원본 좌표)

        def _open_clip(start_time_sec: float):
            nonlocal clip_id, active_clip
            clip_id += 1
            name = f"{base_name}_clip{clip_id}.mp4"
            path = os.path.join(CLIPS_DIR, name)
            active_clip = cv2.VideoWriter(path, fourcc, fps, (orig_w, orig_h))
            if not active_clip.isOpened():
                raise RuntimeError(f"Failed to open clip writer: {path}")
            clips_meta.append({
                "clip_id": clip_id,
                "class_name": active_class,
                "start_time": _format_time_hhmmss(start_time_sec),
                "start_bbox": start_bbox_orig,          # [x1,y1,x2,y2] or None
                "clip_name": name,
                "clip_path": path
            })

        def _close_clip():
            nonlocal active_clip, in_gap, gap_buf, start_bbox_orig
            if active_clip and active_clip.isOpened():
                active_clip.release()
            active_clip = None
            in_gap = False
            gap_buf.clear()
            start_bbox_orig = None

        # 어설트 마스크 (창 판정 기반 프레임 마스크)
        assault_mask = np.zeros(max(total_frames, 1), dtype=np.uint8)

        while len(buf_small) == _args.num_frame:
            # EMA 초기화 옵션
            if EMA_RESET_EACH_WINDOW:
                p_assault_ema = None

            frames_small = list(buf_small)
            frames_orig  = list(buf_orig)

            # 모델 입력/추론
            x_bthwc = frames_to_tensor_batch(frames_small, device)  # [1,T,3,H,W]
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

            # 창 판정
            is_assault_base = (aid >= 0) and (p_assault_ema >= threshold) and (margin >= MARGIN_THRESH)

            # 백본/어텐션 → 단일 히트맵(fuse)
            src, pos = model.backbone(x_btchw)                      # [T,C,oh,ow], [T,C,oh,ow]
            T_, C_, oh, ow = src.shape
            src_proj = model.input_proj(src)                        # [T,D,oh,ow]
            _, att = model.token_encoder(src_proj, None, model.query_embed.weight, pos)
            if att.dim() == 5:
                att = att[0]

            # 어떤 프레임을 "이번 창에서 실제로 쓸지" (중복 방지)
            write_range = range(T_) if frame_base_idx == 0 else range(T_ - STRIDE, T_)

            # 스케일 팩터 (640x360 → 원본)
            sx = orig_w / float(RESIZE_W)
            sy = orig_h / float(RESIZE_H)

            for t in range(T_):
                fidx = frame_base_idx + t
                # assault_mask 크기 안전
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
                box_small = calculate_box_coordinates(prev_pt, RESIZE_W, RESIZE_H, BOX_FRAC_W, BOX_FRAC_H)

                # 창 판정 결과를 프레임 마스크로 확장
                st, ed = frame_base_idx, frame_base_idx + _args.num_frame - 1
                if is_assault_base and st < len(assault_mask):
                    assault_mask[st: min(ed + 1, len(assault_mask))] = 1

                if t not in write_range:
                    continue  # 이번 창에서 이 프레임은 이미 쓴 적 있음

                # === 여기서부터 "한 번만" 쓰는 섹션 (주석 + 클립 상태머신) ===
                # 원본 프레임 꺼내서 박스 그려 주석 프레임 만들기
                frame_orig = frames_orig[t].copy()
                # positive 여부: assault 마스크 또는 top-1이 normal이 아님
                is_positive = bool(assault_mask[fidx]) or (str(top1_name).lower() != "normal")

                if is_positive and box_small:
                    x1,y1,x2,y2 = box_small
                    X1 = int(round(x1 * sx)); Y1 = int(round(y1 * sy))
                    X2 = int(round(x2 * sx)); Y2 = int(round(y2 * sy))
                    cv2.rectangle(frame_orig, (X1, Y1), (X2, Y2), (0,0,255), 2)
                    box_orig = [X1, Y1, X2, Y2]
                else:
                    box_orig = None

                # (A) 주석 영상에 바로 write
                annot_writer.write(frame_orig)
                written_frames += 1

                # (B) 클립 상태머신 (2초 병합 유지)
                cls_name = top1_name
                if is_positive:
                    if active_clip is None:
                        # 새 클립 시작
                        active_class = cls_name
                        start_bbox_orig = box_orig
                        _open_clip(start_time_sec=(fidx / fps if fps > 0 else 0.0))
                        active_clip.write(frame_orig)
                    else:
                        if in_gap:
                            # 같은 클래스 복귀 + gap ≤ tol → 버퍼 flush + 이어쓰기
                            if cls_name.lower() == active_class.lower() and len(gap_buf) <= tol_frames:
                                for fr in gap_buf: active_clip.write(fr)
                                gap_buf.clear()
                                in_gap = False
                                active_clip.write(frame_orig)
                            else:
                                # 다른 클래스 or tol 초과 → 이전 종료 후 새로
                                _close_clip()
                                active_class = cls_name
                                start_bbox_orig = box_orig
                                _open_clip(start_time_sec=(fidx / fps if fps > 0 else 0.0))
                                active_clip.write(frame_orig)
                        else:
                            # 녹화 중 같은 클래스면 그대로
                            if cls_name.lower() == active_class.lower():
                                active_clip.write(frame_orig)
                            else:
                                # 클래스 변경 → 이전 종료, 새로 시작
                                _close_clip()
                                active_class = cls_name
                                start_bbox_orig = box_orig
                                _open_clip(start_time_sec=(fidx / fps if fps > 0 else 0.0))
                                active_clip.write(frame_orig)
                else:
                    if active_clip is not None:
                        # gap 진입/유지
                        if not in_gap:
                            in_gap = True
                            gap_buf = [frame_orig]
                        else:
                            gap_buf.append(frame_orig)
                            if len(gap_buf) > tol_frames:
                                # 2초 초과 → 이전 클립 종료, 버퍼 폐기
                                _close_clip()

                # (C) 진행률 저장 (DB write 빈도 줄여서 업데이트)
                if total_frames > 0:
                    progress = min(99.0, (written_frames / total_frames) * 100.0)
                else:
                    progress = 0.0
                # 1% 이상 변할 때만 저장
                if progress - last_saved_progress >= 1.0:
                    processing_jobs[job_id]["progress"] = float(progress)
                    db_upsert_job(processing_jobs[job_id])
                    last_saved_progress = progress

            # 다음 창으로 슬라이드
            advanced = 0
            for _ in range(STRIDE):
                ok, fr = cap.read()
                if not ok: break
                fr_orig = fr
                fr_small = cv2.resize(fr_orig, (RESIZE_W, RESIZE_H), interpolation=cv2.INTER_AREA)
                buf_small.append(fr_small)
                buf_orig.append(fr_orig)
                advanced += 1
            frame_base_idx += STRIDE
            if advanced < STRIDE:
                break

        # 스트림 종료 → gap flush(≤2초면 붙여쓰기) 후 클립 닫기
        if active_clip is not None:
            if in_gap and len(gap_buf) <= tol_frames:
                for fr in gap_buf: active_clip.write(fr)
            _close_clip()

        # writer/캡쳐 정리
        annot_writer.release()
        cap.release()

        # (마무리) 클립 메타 JSON 저장
        info_path = os.path.join(CLIPS_INFO_DIR, f"{base_name}_clips.json")
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump({"video": video_path, "num_clips": len(clips_meta), "clips": clips_meta},
                      f, ensure_ascii=False, indent=2)

        # 최종 결과 저장 (progress=100)
        result = {
            "video_path": video_path,
            "annotated_video": annotated_path,
            "num_clips": len(clips_meta),
            "clips_info_json": info_path
        }
        processing_jobs[job_id] = {"job_id": job_id, "progress": 100.0, "results": result}
        db_upsert_job(processing_jobs[job_id])

    except Exception:
        # 실패 시에도 progress 포함해 저장
        processing_jobs[job_id] = {"job_id": job_id, "progress": 0.0, "results": None}
        db_upsert_job(processing_jobs[job_id])
