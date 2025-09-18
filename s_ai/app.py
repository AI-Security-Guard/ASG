# s_ai/app.py
from flask import Flask
from database import init_db, db
from routes import analyze_bp
from flask_cors import CORS

ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def create_app():
    app = Flask(__name__)
    init_db(app)

    # 전역 CORS (성공/실패 응답 모두에 헤더 자동 부착)
    CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)

    # 개발용: 테이블 없으면 생성 (migrate 쓰면 제거 가능)
    with app.app_context():
        from models.analysis import Job, ClipSummary

        db.create_all()

    app.register_blueprint(analyze_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
