from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from database import db


def _uuid():
    return str(uuid.uuid4())


def _json_type():
    try:
        eng = db.engine
        if eng and eng.url.drivername.startswith("postgres"):
            return JSONB
    except Exception:
        pass
    return JSON


JSONType = _json_type()


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    video_path = db.Column(db.String(1024), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="queued")
    progress = db.Column(db.Float, nullable=False, default=0.0)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    clips = db.relationship(
        "ClipSummary", backref="job", lazy=True, cascade="all, delete-orphan"
    )


class ClipSummary(db.Model):
    __tablename__ = "clip_summaries"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(36), db.ForeignKey("jobs.id"), nullable=False)

    frame_start = db.Column(db.Integer, nullable=True)
    frame_end = db.Column(db.Integer, nullable=True)

    start_sec = db.Column(db.Float, nullable=True)
    end_sec = db.Column(db.Float, nullable=True)

    class_name = db.Column(db.String(64), nullable=False)
    score = db.Column(db.Float, nullable=True)

    bbox = db.Column(JSONType, nullable=True)
    meta = db.Column(JSONType, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.Index("ix_clip_job", "job_id"),
        db.Index("ix_clip_start_sec", "start_sec"),
    )
