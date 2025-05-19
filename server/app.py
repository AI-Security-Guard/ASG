# server/app.py
from flask import Flask
from auth import register_auth_blueprints

app = Flask(__name__)

# 블루프린트 등록
register_auth_blueprints(app)

if __name__ == "__main__":
    app.run(debug=True)
