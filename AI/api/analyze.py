import os
import torch
import cv2
import time
from flask import Blueprint, request, jsonify
from torchvision import transforms
from models.models import DFGAR as DFWSGARModel
from utils.video_utils import frames_to_time
from utils.model_utils import get_model_and_args

analyze_bp = Blueprint('analyze', __name__)

model, args, device = get_model_and_args()

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('video')
    if file is None:
        return jsonify({"error": "No video uploaded"}), 400

    video_path = os.path.join("uploads", file.filename)
    file.save(video_path)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((360, 640))
    ])

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = transform(frame)
        frames.append(frame)
    cap.release()

    if len(frames) < args.num_frame:
        return jsonify({"error": "Video too short"}), 400

    stride = 5
    results = []
    for i in range(0, len(frames) - args.num_frame + 1, stride):
        clip = torch.stack(frames[i:i + args.num_frame]).unsqueeze(0).to(device)
        with torch.no_grad():
            output = model(clip)
            pred = torch.argmax(output, dim=1).item()
            results.append((i, pred))

    raw_ranges = []
    start = None
    for idx, pred in results:
        if pred == 1 and start is None:
            start = idx
        elif pred == 0 and start is not None:
            raw_ranges.append((start, idx + args.num_frame - 1))
            start = None
    if start is not None:
        raw_ranges.append((start, len(frames) - 1))

    min_frames = int(fps * 1)
    merge_gap = int(fps * 1)

    merged_ranges = []
    for rng in raw_ranges:
        if not merged_ranges:
            merged_ranges.append(rng)
        else:
            prev_start, prev_end = merged_ranges[-1]
            curr_start, curr_end = rng
            if curr_start - prev_end <= merge_gap:
                merged_ranges[-1] = (prev_start, curr_end)
            else:
                merged_ranges.append(rng)

    assault_ranges = [(s, e) for s, e in merged_ranges if (e - s + 1) >= min_frames]

    response = []
    for s, e in assault_ranges:
        response.append({
            "start_frame": int(s),
            "end_frame": int(e),
            "start_time": frames_to_time(s, fps),
            "end_time": frames_to_time(e, fps)
        })

    return jsonify({"assault_intervals": response})
