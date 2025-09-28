# models/analysis.py
from datetime import datetime
from database import db


class Job(db.Model):
    __tablename__ = "jobs"
    job_id = db.Column(db.String(36), primary_key=True)  # UUID 문자열
    video_path = db.Column(db.String, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="running"
    )  # running | done | error
    progress = db.Column(db.Float, nullable=False, default=0.0)
    message = db.Column(db.String, nullable=True)  # 에러 메시지 등
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    clips = db.relationship(
        "Clip", backref="job", cascade="all, delete-orphan", lazy=True
    )


class Clip(db.Model):
    __tablename__ = "clips"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(
        db.String(36), db.ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False
    )

    class_name = db.Column(db.String(50), nullable=False)  # ex) "assault"
    start_time = db.Column(
        db.String(12), nullable=False
    )  # "HH:MM:SS" (원하면 Float(초) 컬럼 추가 가능)
    start_x = db.Column(db.Integer, nullable=True)
    start_y = db.Column(db.Integer, nullable=True)
    start_w = db.Column(db.Integer, nullable=True)
    start_h = db.Column(db.Integer, nullable=True)

    clip_name = db.Column(db.String, nullable=False)
    clip_path = db.Column(db.String, nullable=False)  # "event_clips/xxx.mp4"
