from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from auth import register_auth_blueprints
from video import register_video_blueprints
from flask_cors import CORS
from video.deleteVideo import delete_video_bp
from flask_jwt_extended import JWTManager


app = Flask(__name__)
CORS(app)

# SQLite DB 설정
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ JWT 설정 추가
app.config["JWT_SECRET_KEY"] = "CHANGE_THIS_TO_ENV_SECRET"  # 👉 환경변수로 빼는 게 안전
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)

# DB 초기화
db.init_app(app)

# 블루프린트 등록
register_auth_blueprints(app)
register_video_blueprints(app)
app.register_blueprint(delete_video_bp)

# DB 테이블 생성
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
