import os
import uuid
import sqlite3
import threading
from flask import (
    send_file,
    Response,
    Blueprint,
    request,
    jsonify,
    make_response,
    abort,
    url_for,
)
from analyze import (
    db_get_job,
)
from models.analysis import Job, Clip
from analyze import THUMB_DIR
from analyze import CLIPS_DIR
from flask import current_app
from database import db


analyze_bp = Blueprint("analyze", __name__)


# 분석하기
@analyze_bp.route("/analyze", methods=["POST"])
def analyze_video():
    try:
        data = request.get_json(silent=True) or {}
        video_path = data.get("video_path")
        username = data.get("username")

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
            "username": username,
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
    clips = Clip.query.filter_by(job_id=job_id).order_by(Clip.start_time).all()

    def _bbox_from(c: Clip):
        if (
            c.start_x is None
            or c.start_y is None
            or c.start_w is None
            or c.start_h is None
        ):
            return None
        x1, y1 = c.start_x, c.start_y
        x2, y2 = x1 + c.start_w, y1 + c.start_h
        return [x1, y1, x2, y2]

    result_list = []
    for c in clips:
        d = c.to_dict() if hasattr(c, "to_dict") else {}
        clip_name = getattr(c, "clip_name", None)
        thumb_path = getattr(c, "thumbnail", None)

        clip_url = (
            url_for("analyze.serve_event_clip", fname=clip_name, _external=False)
            if clip_name
            else None
        )

        # 썸네일은 파일명만 빼서 /event_thumbs/<fname>로 서빙
        thumb_url = None
        if thumb_path:
            from os.path import basename

            thumb_url = url_for(
                "analyze.serve_event_thumb", fname=basename(thumb_path), _external=False
            )

        result_list.append(
            {
                "clip_id": c.id,
                "class_name": c.class_name,
                "start_time": c.start_time,  # "00:00:12"
                "bbox": _bbox_from(c),  # [x1, y1, x2, y2] 또는 null
                "clip_url": clip_url,  # "/event_clips/xxx.mp4"
                "thumb_url": thumb_url,  # "/event_thumbs/xxx.jpg" 또는 null
                "checked": bool(c.checked),
            }
        )

    # 응답 모양 맞추기: result 키로 내려주고, 기존의 results 키는 제거
    resp = dict(job)
    resp.pop("results", None)  # 혹시 jobs.results가 있어도 숨김
    resp["result"] = result_list

    return jsonify(resp), 200


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


@analyze_bp.route("/event_thumbs/<path:fname>", methods=["GET"])
def serve_event_thumb(fname: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # ✅ 썸네일은 THUMB_DIR 기준!
    thumbs_dir = THUMB_DIR
    if not os.path.isabs(thumbs_dir):
        thumbs_dir = os.path.join(base_dir, thumbs_dir)

    # ../ 차단 + 정규화
    safe = os.path.normpath(fname).replace("\\", "/")

    # 클라이언트가 'thumbnails/파일명' 형태로 줄 때도 처리
    if safe.startswith("thumbnails/"):
        safe = safe.split("/", 1)[1]

    full_path = os.path.join(thumbs_dir, safe)

    if not os.path.exists(full_path):
        return jsonify({"detail": f"thumbnail not found: {safe}"}), 404

    return send_file(full_path, mimetype="image/jpeg")


@analyze_bp.route("/event_clips/<path:fname>", methods=["GET"])
def serve_event_clip(fname: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    clips_dir = (
        CLIPS_DIR if os.path.isabs(CLIPS_DIR) else os.path.join(base_dir, CLIPS_DIR)
    )
    safe = os.path.normpath(fname).replace("\\", "/")
    full_path = os.path.join(clips_dir, safe)
    return _send_mp4_partial(full_path)  # ← Range 지원


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

        d["checked"] = bool(getattr(c, "checked", 0))

        # 1) 동영상 URL (기존 코드 유지)
        if d.get("clip_name"):
            d["clip_url"] = url_for(
                "analyze.serve_event_clip", fname=d["clip_name"], _external=False
            )
        else:
            d["clip_url"] = None

        # 2) ✅ 썸네일 URL 추가 (여기에 넣기)
        thumb_name = d.get("thumbnail") or d.get("thumb_path")
        if thumb_name:
            from os.path import basename

            # 'thumbnails/xxx.jpg'처럼 들어오면 파일명만 추출해서 라우트에 전달
            d["thumb_url"] = url_for(
                "analyze.serve_event_thumb", fname=basename(thumb_name), _external=False
            )
        else:
            d["thumb_url"] = None

        result["clips"].append(d)

    return jsonify(result), 200


@analyze_bp.route("/clips/<int:clip_id>/check", methods=["PATCH"])
def mark_clip_checked(clip_id):
    clip = Clip.query.get(clip_id)
    if not clip:
        return jsonify({"error": "Clip not found"}), 404
    clip.checked = True

    db.session.commit()
    return jsonify(
        {"message": "checked set to true", "clip_id": clip_id, "checked": True}
    )


@analyze_bp.route("/jobs/latest", methods=["GET"])
def get_latest_job_for_user():
    username = request.args.get("username")
    if not username:
        return jsonify({"detail": "username is required"}), 400

    # jobs.db 에서 이 사용자걸 최신순으로 하나만
    conn = sqlite3.connect("jobs.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT job_id FROM jobs WHERE username = ? ORDER BY rowid DESC LIMIT 1",
        (username,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"detail": "no jobs for this user"}), 404

    return jsonify({"job_id": row[0]}), 200
