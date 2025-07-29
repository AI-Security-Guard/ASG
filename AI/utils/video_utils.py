import os
import subprocess
from uuid import uuid4

def frames_to_time(f_idx, fps):
    seconds = f_idx / fps
    return f"{int(seconds // 60):02}:{int(seconds % 60):02}"

def extract_clips(video_path, intervals, output_dir="clips"):
    os.makedirs(output_dir, exist_ok=True)
    clip_paths = []

    for interval in intervals:
        start = interval['start']
        duration = interval['end'] - interval['start']
        clip_name = f"{uuid4().hex}.mp4"
        out_path = os.path.join(output_dir, clip_name)

        command = [
            "ffmpeg", "-y", "-ss", str(start), "-i", video_path,
            "-t", str(duration), "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-loglevel", "error", out_path
        ]
        subprocess.run(command)
        clip_paths.append(out_path)

    return clip_paths
