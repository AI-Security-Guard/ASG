import os
import uuid
import threading
from flask import Response, Blueprint, request, jsonify, make_response, abort
from analyze import (
    model,
    processing_jobs,
    analyze_video_pure,
    db_get_job,
    db_upsert_job,
)
from analyze import CLIPS_DIR

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/analyze", methods=["POST"])
def analyze_video():
    data = request.get_json(silent=True) or {}
    video_path = data.get("video_path")

    if model is None:
        job_id = str(uuid.uuid4())
        payload = {"job_id": job_id, "results": None}
        db_upsert_job(payload)
        return make_response(
            jsonify({"job_id": job_id, "detail": "Model not loaded"}), 503
        )

    if not video_path or not os.path.exists(video_path):
        job_id = str(uuid.uuid4())
        payload = {"job_id": job_id, "results": None}
        db_upsert_job(payload)
        return make_response(
            jsonify(
                {"job_id": job_id, "detail": f"Video file not found: {video_path}"}
            ),
            404,
        )

    # 항상 비동기: 초기 payload 저장(최소)
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {"job_id": job_id, "results": None}
    db_upsert_job(processing_jobs[job_id])

    th = threading.Thread(
        target=analyze_video_pure, args=(job_id, video_path), daemon=True
    )
    th.start()

    resp = make_response(jsonify({"job_id": job_id}), 202)
    resp.headers["Location"] = f"/jobs/{job_id}"
    return resp


@analyze_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id: str):
    job = db_get_job(job_id)
    if not job:
        return jsonify({"detail": "Job not found"}), 404

    # 'eresults' 오타 보정
    if "eresults" in job and "results" not in job:
        job["results"] = job.pop("eresults")

    res = job.get("results") or {}

    # DB에 clips_info가 없으면 clips_info_json 파일을 읽어 주입
    if "clips_info" not in res:
        info_path = res.get("clips_info_json")
        if info_path:
            try:
                import os, json

                # 역슬래시 → OS 구분자로 통일
                norm = info_path.replace("\\", os.sep)
                # 후보 경로들 (존재하는 것 찾으면 사용)
                base_dir = os.path.dirname(os.path.abspath(__file__))  # routes.py 기준
                cwd_dir = os.getcwd()  # 현재 작업 디렉토리
                candidates = []
                # 절대경로면 그 자체, 아니면 base_dir/cwd_dir 기준 상대경로
                if os.path.isabs(norm):
                    candidates.append(norm)
                else:
                    candidates.append(os.path.join(base_dir, norm))
                    candidates.append(os.path.join(cwd_dir, norm))

                abs_path = None
                for c in candidates:
                    if os.path.exists(c):
                        abs_path = c
                        break

                if abs_path is None:
                    raise FileNotFoundError(
                        f"clips_info_json not found. tried={candidates}"
                    )

                with open(abs_path, "r", encoding="utf-8") as f:
                    res["clips_info"] = json.load(f)

                job["results"] = res
                # 디버그 힌트 (원하면 지워도 됨)
                job["_debug"] = {
                    "cwd": cwd_dir,
                    "base_dir": base_dir,
                    "chosen_path": abs_path,
                }

            except Exception as e:
                job.setdefault("_warn", {})["clips_info_load"] = str(e)
                job.setdefault("_warn", {})["clips_info_json"] = info_path

    return jsonify(job)


def _send_mp4_partial(full_path: str):
    if not os.path.exists(full_path):
        abort(404)
    file_size = os.path.getsize(full_path)
    rng = request.headers.get("Range")
    if not rng:
        with open(full_path, "rb") as f:
            data = f.read()
        resp = Response(data, 200, mimetype="video/mp4")
        resp.headers["Accept-Ranges"] = "bytes"
        resp.headers["Content-Length"] = str(file_size)
        resp.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        return resp

    # Range: bytes=start-end
    byte1, byte2 = 0, None
    parts = rng.replace("bytes=", "").split("-")
    if parts[0]:
        byte1 = int(parts[0])
    if len(parts) > 1 and parts[1]:
        byte2 = int(parts[1])

    length = file_size - byte1 if byte2 is None else byte2 - byte1 + 1
    with open(full_path, "rb") as f:
        f.seek(byte1)
        data = f.read(length)

    resp = Response(data, 206, mimetype="video/mp4", direct_passthrough=True)
    resp.headers["Content-Range"] = f"bytes {byte1}-{byte1+length-1}/{file_size}"
    resp.headers["Accept-Ranges"] = "bytes"
    resp.headers["Content-Length"] = str(length)
    resp.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    return resp


@analyze_bp.route("/event_clips/<path:fname>", methods=["GET"])
def serve_event_clip(fname: str):
    # routes.py 기준 절대경로로 변환
    base_dir = os.path.dirname(os.path.abspath(__file__))
    clips_dir = CLIPS_DIR
    if not os.path.isabs(clips_dir):
        clips_dir = os.path.join(base_dir, clips_dir)

    # 보안: 상위 경로 차단
    safe = os.path.normpath(fname).replace("\\", "/")
    full_path = os.path.join(clips_dir, safe)
    return _send_mp4_partial(full_path)
