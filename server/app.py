# server/app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from auth import register_auth_blueprints
from video import register_video_blueprints
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# SQLite DB 설정
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# DB 초기화
db.init_app(app)

# 블루프린트 등록
register_auth_blueprints(app)
register_video_blueprints(app)

# DB 테이블 생성
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
