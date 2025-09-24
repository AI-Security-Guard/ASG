import os, threading, traceback
from flask import Blueprint, request, jsonify, abort, Response, current_app
from database import db
from models.analysis import Job
from analyze import analyze_video_pure as run_analysis, CLIPS_DIR

analyze_bp = Blueprint("analyze", __name__)


# -----------------------------
# DB 업데이트 헬퍼 (0~100 스케일 고정)
# -----------------------------
def set_job(job_id, **fields):
    j = Job.query.get(job_id)
    if not j:
        return
    for k, v in fields.items():
        setattr(j, k, v)
    db.session.commit()


def set_progress(job_id, pct: float):
    """pct는 0~100 float"""
    pct = max(0.0, min(100.0, float(pct)))
    set_job(job_id, progress=pct)


# -----------------------------
# 백그라운드 워커
# -----------------------------
def _run_in_background(app, job_id, path):
    # 스레드에서 반드시 앱 컨텍스트!
    with app.app_context():
        try:
            print(f"[BG] start job={job_id}, path={path}", flush=True)
            set_job(job_id, status="running", progress=0.0)

            # analyze 모듈이 on_progress 콜백을 지원하면 붙이고,
            # 아니면 그냥 호출 (TypeError 무시)
            def on_progress(p):  # p는 0~1 또는 0~100 둘 다 허용
                try:
                    val = float(p)
                    if val <= 1.0:
                        val *= 100.0
                    set_progress(job_id, val)
                    print(f"[BG] progress={val:.1f}%", flush=True)
                except Exception:
                    traceback.print_exc()

            try:
                run_analysis(job_id, path, on_progress=on_progress)
            except TypeError:
                # 구버전 시그니처: (job_id, path)
                run_analysis(job_id, path)

            set_job(job_id, status="done", progress=100.0)
            print(f"[BG] done job={job_id}", flush=True)
        except Exception as e:
            print(f"[BG][ERROR] job={job_id}: {e}", flush=True)
            traceback.print_exc()
            set_job(job_id, status="failed", progress=0.0)
            # models.Job에 error_message 컬럼이 있다면 남김
            try:
                set_job(job_id, error_message=str(e))
            except Exception:
                pass
        finally:
            # 스레드 세션 정리 (SQLite 잠금/세션 누수 예방)
            try:
                db.session.remove()
            except Exception:
                pass


# -----------------------------
# 엔드포인트
# -----------------------------
@analyze_bp.route("/analyze", methods=["POST", "OPTIONS"])
def start_analyze():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    video_path = data.get("video_path")
    if not video_path:
        return jsonify({"error": "video_path required"}), 400

    # Job 생성 (status/진행률 초기화는 여기서 확정)
    job = Job(video_path=video_path, status="queued", progress=0.0)
    db.session.add(job)
    db.session.commit()

    # 현재 앱 객체를 캡처해서 스레드로 전달
    app = current_app._get_current_object()
    threading.Thread(
        target=_run_in_background, args=(app, job.id, video_path), daemon=True
    ).start()

    # 프론트가 바로 폴링 시작할 수 있게 202로 즉시 반환
    return jsonify({"job_id": str(job.id), "status": "running", "progress": 0.0}), 202


@analyze_bp.route("/jobs/<job_id>", methods=["GET", "OPTIONS"])
def get_job(job_id):
    if request.method == "OPTIONS":
        return ("", 204)

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    payload = {
        "job_id": str(job.id),
        "status": job.status,  # "queued" | "running" | "done" | "failed"
        "progress": float(job.progress or 0),  # 0~100 기준
    }
    # 선택 필드
    if hasattr(job, "results") and job.results:
        payload["results"] = job.results
    if hasattr(job, "error_message") and job.error_message:
        payload["error"] = job.error_message

    return jsonify(payload), 200


@analyze_bp.route("/event_clips/<path:fname>", methods=["GET"])
def serve_event_clip(fname: str):
    # 경로 탈출 방지: CLIPS_DIR 기준 절대경로 확정 후 prefix 검사
    base = os.path.abspath(CLIPS_DIR)
    target = os.path.abspath(os.path.join(base, fname))
    if not target.startswith(base + os.sep) and target != base:
        abort(403)

    if not os.path.exists(target):
        abort(404)

    file_size = os.path.getsize(target)
    rng = request.headers.get("Range")

    if not rng:
        with open(target, "rb") as f:
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

    if file_size <= 0:
        abort(416)  # Range Not Satisfiable

    chunk = 1024 * 512  # 512KB
    end = min(start + chunk, file_size - 1)
    if start > end:
        abort(416)

    with open(target, "rb") as f:
        f.seek(start)
        data = f.read(end - start + 1)

    resp = Response(data, 206, mimetype="video/mp4")
    resp.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    resp.headers["Accept-Ranges"] = "bytes"
    resp.headers["Content-Length"] = str(end - start + 1)
    return resp
