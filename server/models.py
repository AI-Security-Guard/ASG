# server/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    text,
)
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    video = db.Column(db.String(200), nullable=True)
    original_video = db.Column(db.String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "video": self.video,
        }


class Job(db.Model):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)  # UUID 문자열 사용 가정
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    video_path = Column(Text, nullable=False)
    status = Column(
        String(20), nullable=False, server_default=text("'queued'")
    )  # queued|running|done|error
    progress = Column(Float, nullable=False, server_default=text("0"))

    annotated_video = Column(Text, nullable=True)  # 결과 영상 경로
    message = Column(Text, nullable=True)  # 에러/로그(옵션)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # jobs → clips
    clips = relationship(
        "Clip",
        back_populates="job",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # jobs → users
    user = relationship("User", back_populates="jobs", lazy="selectin")

    __table_args__ = (
        CheckConstraint(
            "progress >= 0 AND progress <= 100", name="ck_jobs_progress_0_100"
        ),
        Index("ix_jobs_status", "status"),
    )

    def to_dict(self, include_clips: bool = False):
        data = {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "video_path": self.video_path,
            "status": self.status,
            "progress": float(self.progress or 0),
            "annotated_video": self.annotated_video,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_clips:
            data["clips"] = [c.to_dict() for c in (self.clips or [])]
        return data


class Clip(db.Model):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, autoincrement=True)  # clip_id
    job_id = Column(
        String,
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 분류 결과 클래스 (예: "normal", "assault" …)
    class_name = Column(String(50), nullable=False, index=True)
    checked = Column(Boolean, nullable=False, server_default=text("0"))

    # "HH:MM:SS" 형태 권장
    start_time = Column(String(16), nullable=False, index=True)

    # 시작 BBox (x, y, w, h) — 응답에서 [x1,y1,x2,y2]로 변환
    start_x = Column(Integer, nullable=True)
    start_y = Column(Integer, nullable=True)
    start_w = Column(Integer, nullable=True)
    start_h = Column(Integer, nullable=True)

    # 파일 정보
    clip_name = Column(Text, nullable=False)
    clip_path = Column(Text, nullable=False)

    # 클립별 썸네일 경로
    thumbnail = Column(Text, nullable=True)

    # clips → jobs
    job = relationship("Job", back_populates="clips", lazy="selectin")

    __table_args__ = (Index("ix_clips_class_time", "class_name", "start_time"),)

    def to_dict(self):
        start_bbox = None
        if None not in (self.start_x, self.start_y, self.start_w, self.start_h):
            x1, y1 = self.start_x, self.start_y
            x2, y2 = x1 + self.start_w, y1 + self.start_h
            start_bbox = [x1, y1, x2, y2]

        return {
            "clip_id": self.id,
            "job_id": self.job_id,
            "class_name": self.class_name,
            "checked": bool(self.checked),
            "start_time": self.start_time,
            "start_bbox": start_bbox,  # [x1,y1,x2,y2] or null
            "clip_name": self.clip_name,
            "clip_path": self.clip_path,
            "thumbnail": self.thumbnail,
        }
