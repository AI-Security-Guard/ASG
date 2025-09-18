# routes.py
import os
from flask import Blueprint, request, jsonify, abort, Response
from database import db
from models.analysis import Job, ClipSummary
from analyze import analyze_video_pure as run_analysis, CLIPS_DIR

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/analyze", methods=["POST"])
def start_analyze():
    data = request.get_json(silent=True) or {}
    video_path = data.get("video_path")
    if not video_path:
        return jsonify({"error": "video_path required"}), 400

    job = Job(video_path=video_path, status="running", progress=0.0)
    db.session.add(job)
    db.session.commit()

    try:
        run_analysis(job.id, video_path)
        job.status = "done"
        job.progress = 100.0
        db.session.commit()
        return jsonify({"job_id": job.id, "status": job.status})
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.session.commit()
        return (
            jsonify(
                {"job_id": job.id, "status": job.status, "error": job.error_message}
            ),
            500,
        )


@analyze_bp.route("/event_clips/<path:fname>", methods=["GET"])
def serve_event_clip(fname: str):
    safe = os.path.normpath(fname).replace("\\", "/")
    full_path = os.path.join(CLIPS_DIR, safe)
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
        return resp

    # Partial content (Range) 응답
    try:
        start = int(rng.replace("bytes=", "").split("-")[0])
    except Exception:
        start = 0
    end = min(start + 1024 * 512, file_size - 1)  # 512KB 청크

    with open(full_path, "rb") as f:
        f.seek(start)
        data = f.read(end - start + 1)

    resp = Response(data, 206, mimetype="video/mp4")
    resp.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    resp.headers["Accept-Ranges"] = "bytes"
    resp.headers["Content-Length"] = str(end - start + 1)
    return resp
