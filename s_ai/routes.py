import os
import uuid
import threading
from flask import Response, Blueprint, request, jsonify, make_response, abort, url_for
from analyze import (
    db_get_job,
)
from models.analysis import Job, Clip
from analyze import CLIPS_DIR
from flask import current_app

analyze_bp = Blueprint("analyze", __name__)


# 분석하기
@analyze_bp.route("/analyze", methods=["POST"])
def analyze_video():
    try:
        data = request.get_json(silent=True) or {}
        video_path = data.get("video_path")

        from analyze import (
            model,
            processing_jobs,
            analyze_video_pure,
            db_upsert_job,
        )  # 안전하게 재확인 import

        if model is None:
            job_id = str(uuid.uuid4())
            # 최소 필드로 스냅샷 저장 (status=error, message 활용)
            db_upsert_job(
                {
                    "job_id": job_id,
                    "status": "error",
                    "progress": 0.0,
                    "message": "Model not loaded",
                }
            )
            return make_response(
                jsonify({"job_id": job_id, "detail": "Model not loaded"}), 503
            )

        if not video_path or not os.path.exists(video_path):
            job_id = str(uuid.uuid4())
            db_upsert_job(
                {
                    "job_id": job_id,
                    "status": "error",
                    "progress": 0.0,
                    "video_path": video_path or "",
                    "message": f"Video file not found: {video_path}",
                }
            )
            return make_response(
                jsonify(
                    {"job_id": job_id, "detail": f"Video file not found: {video_path}"}
                ),
                404,
            )

        job_id = str(uuid.uuid4())
        processing_jobs[job_id] = {
            "job_id": job_id,
            "status": "running",
            "progress": 0.0,
            "results": None,
            "video_path": video_path,
        }
        db_upsert_job(processing_jobs[job_id])

        app = current_app._get_current_object()

        def _bg(app, job_id, video_path):
            with app.app_context():
                analyze_video_pure(job_id, video_path)

        th = threading.Thread(target=_bg, args=(app, job_id, video_path), daemon=True)
        th.start()

        resp = make_response(
            jsonify(
                {"job_id": job_id, "status": "running", "progress": 0, "results": None}
            ),
            202,
        )
        resp.headers["Location"] = f"/jobs/{job_id}"
        return resp

    except Exception as e:
        # 콘솔에도 출력
        import traceback

        traceback.print_exc()
        # 프론트로 상세를 내려줌
        return jsonify({"detail": "Internal Server Error", "error": str(e)}), 500


# 진행도 확인
@analyze_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id: str):
    job = db_get_job(job_id)
    if not job:
        return jsonify({"detail": "Job not found"}), 404

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


@analyze_bp.route("/jobs/<job_id>/clips", methods=["GET"])
def get_clips_by_job(job_id):
    job = Job.query.filter_by(job_id=job_id).first()
    if not job:
        return jsonify({"detail": "Job not found"}), 404

    clips = Clip.query.filter_by(job_id=job_id).order_by(Clip.start_time).all()
    result = {
        "job_id": job.job_id,
        "video_path": job.video_path,
        "count": len(clips),
        "clips": [],
    }

    for c in clips:
        d = c.to_dict()
        if d.get("clip_name"):
            d["clip_url"] = url_for(
                "analyze.serve_event_clip", fname=d["clip_name"], _external=False
            )
        else:
            d["clip_url"] = None
        result["clips"].append(d)

    return jsonify(result), 200
