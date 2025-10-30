# models/analysis.py
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import db
from sqlalchemy import text


class Job(db.Model):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)
    video_path = Column(Text, nullable=False)
    status = Column(
        String, nullable=False, default="queued"
    )  # queued|running|done|error
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 ~ 100.0 권장
    annotated_video = Column(Text, nullable=True)  # 결과 영상 경로
    message = Column(Text, nullable=True)  # (옵션) 에러/로그
    # 🔁 더 이상 jobs 단위 썸네일은 사용하지 않음 (컬럼 제거)

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

    # 분류 결과 클래스 (예: "normal", "assault" …)
    class_name = Column(String(50), nullable=False)
    checked = db.Column(
        db.Boolean, nullable=False, default=False, server_default=text("0")
    )
    # "00:00:12" 형태로 저장
    start_time = Column(String(16), nullable=False)

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

    # API 응답 변환용
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
            "class_name": self.class_name,
            "start_time": self.start_time,
            "start_bbox": start_bbox,  # [x1,y1,x2,y2] or null
            "clip_name": self.clip_name,
            "clip_path": self.clip_path,
            "thumbnail": self.thumbnail,
        }
