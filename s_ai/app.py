import os
from flask import Flask
from database import db
from flask_cors import CORS
from routes import analyze_bp


def create_app():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "jobs.db")

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(
        app,
        resources={
            r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}
        },
        supports_credentials=False,
        allow_headers=["Content-Type"],
        methods=["GET", "POST", "OPTIONS"],
        max_age=600,
    )
    db.init_app(app)

    # 모델 import 후 테이블 생성
    with app.app_context():
        from models.analysis import Job, Clip  # noqa

        db.create_all()

    # 블루프린트 등록
    from routes import analyze_bp

    app.register_blueprint(analyze_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
