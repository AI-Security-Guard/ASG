# # models/analysis.py
# from datetime import datetime
# from database import db


# class Job(db.Model):
#     __tablename__ = "jobs"
#     job_id = db.Column(db.String(36), primary_key=True)  # UUID 문자열
#     video_path = db.Column(db.String, nullable=False)
#     status = db.Column(
#         db.String(20), nullable=False, default="running"
#     )  # running | done | error
#     progress = db.Column(db.Float, nullable=False, default=0.0)
#     message = db.Column(db.String, nullable=True)  # 에러 메시지 등
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     updated_at = db.Column(
#         db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
#     )

#     clips = db.relationship(
#         "Clip", backref="job", cascade="all, delete-orphan", lazy=True
#     )


# class Clip(db.Model):
#     __tablename__ = "clips"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     job_id = db.Column(
#         db.String(36), db.ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False
#     )

#     class_name = db.Column(db.String(50), nullable=False)  # ex) "assault"
#     start_time = db.Column(
#         db.String(12), nullable=False
#     )  # "HH:MM:SS" (원하면 Float(초) 컬럼 추가 가능)
#     start_x = db.Column(db.Integer, nullable=True)
#     start_y = db.Column(db.Integer, nullable=True)
#     start_w = db.Column(db.Integer, nullable=True)
#     start_h = db.Column(db.Integer, nullable=True)

#     clip_name = db.Column(db.String, nullable=False)
#     clip_path = db.Column(db.String, nullable=False)  # "event_clips/xxx.mp4"

# models/analysis.py
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import db


# models/analysis.py
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import db


class Job(db.Model):
    __tablename__ = "jobs"
    job_id = Column(String, primary_key=True)
    video_path = Column(Text, nullable=False)
    status = Column(
        String, nullable=False, default="queued"
    )  # queued|running|done|error
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 ~ 1.0
    annotated_video = Column(Text, nullable=True)  # 결과 영상 경로
    message = Column(Text, nullable=True)  # (옵션) 에러/로그

    clips = relationship(
        "Clip",
        backref="job",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Clip(db.Model):
    __tablename__ = "clips"
    id = Column(Integer, primary_key=True, autoincrement=True)  # -> clip_id
    job_id = Column(
        String, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False
    )

    # 요청 예시: "00:00:12" 형태 그대로 저장
    start_time = Column(String(16), nullable=False)

    # DB 저장은 (x, y, w, h)
    start_x = Column(Integer, nullable=True)
    start_y = Column(Integer, nullable=True)
    start_w = Column(Integer, nullable=True)
    start_h = Column(Integer, nullable=True)

    # 파일 정보
    clip_name = Column(Text, nullable=True)
    clip_path = Column(Text, nullable=True)

    # ✅ 응답 변환용 헬퍼
    def to_dict(self):
        start_bbox = None
        if (
            self.start_x is not None
            and self.start_y is not None
            and self.start_w is not None
            and self.start_h is not None
        ):
            x1, y1 = self.start_x, self.start_y
            x2, y2 = self.start_x + self.start_w, self.start_y + self.start_h
            start_bbox = [x1, y1, x2, y2]

        return {
            "clip_id": self.id,
            "start_time": self.start_time,
            "start_bbox": start_bbox,  # [x1,y1,x2,y2] 또는 null
            "clip_name": self.clip_name,
            "clip_path": self.clip_path,
        }
