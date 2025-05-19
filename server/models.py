# server/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    video = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "video": self.video,
        }
