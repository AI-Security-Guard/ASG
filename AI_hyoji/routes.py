import os
import uuid
import threading
from flask import Blueprint, request, jsonify, make_response
from analyze import (
    model, processing_jobs,
    analyze_video_pure, db_get_job, db_upsert_job
)

analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.route("/analyze", methods=["POST"])
def analyze_video():
    data = request.get_json(silent=True) or {}
    video_path = data.get("video_path")

    if model is None:
        job_id = str(uuid.uuid4())
        payload = {"job_id": job_id, "results": None}
        db_upsert_job(payload)
        return make_response(jsonify({"job_id": job_id, "detail": "Model not loaded"}), 503)

    if not video_path or not os.path.exists(video_path):
        job_id = str(uuid.uuid4())
        payload = {"job_id": job_id, "results": None}
        db_upsert_job(payload)
        return make_response(jsonify({"job_id": job_id, "detail": f"Video file not found: {video_path}"}), 404)

    # 항상 비동기: 초기 payload 저장(최소)
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {"job_id": job_id, "results": None}
    db_upsert_job(processing_jobs[job_id])

    th = threading.Thread(target=analyze_video_pure, args=(job_id, video_path), daemon=True)
    th.start()

    resp = make_response(jsonify({"job_id": job_id}), 202)
    resp.headers["Location"] = f"/jobs/{job_id}"
    return resp


@analyze_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id: str):
    job = db_get_job(job_id)
    if not job:
        return jsonify({"detail": "Job not found"}), 404
    return jsonify(job)
