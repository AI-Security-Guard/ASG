from typing import List, Dict, Any, Tuple
import numpy as np
import cv2
import os

# 시각화/토큰 관련 상수 (유틸 내부에서만 사용)
TOKENS_FUSE = "max"
TOP_PCT = 0.15
ALPHA_HM = 0.20
ALPHA_PT = 0.25
JUMP_MAX_PIX = 60
JUMP_BLEND = 0.35
BOX_FRAC_W = 0.26
BOX_FRAC_H = 0.32

__all__ = [
    "split_tokens_spatial", "fuse_tokens_spatial",
    "heatmap_to_point", "smooth_point", "calculate_box_coordinates",
    "render_annotated_video",
    "TOP_PCT", "ALPHA_HM", "ALPHA_PT", "JUMP_MAX_PIX", "JUMP_BLEND",
    "BOX_FRAC_W", "BOX_FRAC_H"
]

def split_tokens_spatial(att_t, oh, ow):
    # att_t: [Q,HW] or [H,Q,K]
    if att_t.dim() == 3:
        att_t = att_t.mean(dim=0)  # [Q,K]
    outs = []
    for q in range(att_t.shape[0]):
        m = att_t[q].view(oh, ow)
        m = m - m.min()
        den = float(m.max() + 1e-8)
        if den > 0:
            m = m / den
        outs.append(m.detach().cpu().numpy())
    return outs

def fuse_tokens_spatial(att_t_qk, oh, ow):
    a = att_t_qk
    if a.dim() == 2:  # [Q, HW]
        s = a.sum(dim=0) if TOKENS_FUSE == "sum" else a.max(dim=0)[0]
        m = s.view(oh, ow)
    elif a.dim() == 3:  # [H, Q, K]
        a = a.mean(dim=0)  # [Q, K]
        s = a.sum(dim=0) if TOKENS_FUSE == "sum" else a.max(dim=0)[0]
        m = s.view(oh, ow)
    else:
        raise RuntimeError(f"Unexpected att_t_qk shape: {tuple(a.shape)}")
    m = m - m.min()
    den = float(m.max() + 1e-8)
    if den > 0:
        m = m / den
    return m.detach().cpu().numpy()

def heatmap_to_point(hm, mode='centroid', top_pct=TOP_PCT) -> Tuple[float, float]:
    H, W = hm.shape
    if mode == 'argmax':
        idx = int(np.argmax(hm)); cy, cx = divmod(idx, W)
        return float(cx), float(cy)
    flat = hm.reshape(-1)
    k = max(1, int(len(flat) * top_pct))
    if k <= 1:
        idx = int(np.argmax(flat)); cy, cx = divmod(idx, W)
        return float(cx), float(cy)
    thr_val = np.partition(flat, -k)[-k]
    mask = (hm >= thr_val).astype(np.float32)
    if mask.sum() < 1:
        idx = int(np.argmax(flat)); cy, cx = divmod(idx, W)
        return float(cx), float(cy)
    ys, xs = np.nonzero(mask)
    weights = hm[ys, xs]
    wsum = float(weights.sum()) + 1e-6
    cx = float((xs * weights).sum() / wsum)
    cy = float((ys * weights).sum() / wsum)
    return cx, cy

def smooth_point(prev, curr, alpha=ALPHA_PT, jump_max=JUMP_MAX_PIX, jump_blend=JUMP_BLEND):
    if prev is None:
        return curr
    px, py = prev; cx, cy = curr
    dx, dy = cx - px, cy - py
    if (dx*dx + dy*dy) ** 0.5 > jump_max:
        cx = (1 - jump_blend) * px + jump_blend * cx
        cy = (1 - jump_blend) * py + jump_blend * cy
    sx = (1 - alpha) * px + alpha * cx
    sy = (1 - alpha) * py + alpha * cy
    return (sx, sy)

def calculate_box_coordinates(pt, frame_w, frame_h, box_frac_w=BOX_FRAC_W, box_frac_h=BOX_FRAC_H):
    if pt is None:
        return None
    bw = int(frame_w * box_frac_w)
    bh = int(frame_h * box_frac_h)
    cx, cy = pt
    cx_i, cy_i = int(round(cx)), int(round(cy))
    x1 = max(0, cx_i - bw // 2)
    y1 = max(0, cy_i - bh // 2)
    x2 = min(frame_w - 1, x1 + bw)
    y2 = min(frame_h - 1, y1 + bh)
    return (x1, y1, x2, y2)

def render_annotated_video(
    *,
    video_path: str,
    detections: List[Dict[str, Any]],
    output_path: str,
    resize_w: int,
    resize_h: int,
    class_names: List[str],
    positive_class_names: List[str] | None = None,
    box_color_bgr=(0, 0, 255),
    box_thickness: int = 2,
) -> str:

    if positive_class_names is None:
        positive_class_names = [c for c in class_names if c.lower() != "normal"]

    det_by_frame: Dict[int, Dict[str, Any]] = {d["frame_idx"]: d for d in detections}

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (orig_w, orig_h))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(f"Failed to open VideoWriter: {output_path}")

    sx = orig_w / float(resize_w)
    sy = orig_h / float(resize_h)

    frame_idx = 0
    pos_set = {c.lower() for c in positive_class_names}
    while True:
        ret, frame_bgr = cap.read()
        if not ret:
            break

        det = det_by_frame.get(frame_idx)
        if det is not None:
            is_positive = bool(det.get("is_assault", False))
            top1_name = str(det.get("top1_class_name", "")).lower()
            if is_positive or (top1_name in pos_set):
                for tok in det.get("tokens", []):
                    box = tok.get("box")
                    if not box:
                        continue
                    x1, y1, x2, y2 = box
                    X1 = int(round(x1 * sx))
                    Y1 = int(round(y1 * sy))
                    X2 = int(round(x2 * sx))
                    Y2 = int(round(y2 * sy))
                    cv2.rectangle(frame_bgr, (X1, Y1), (X2, Y2), box_color_bgr, box_thickness)

        writer.write(frame_bgr)
        frame_idx += 1

    cap.release()
    writer.release()
    return output_path
