# server/auth/signup.py
from flask import Blueprint, request, jsonify

register_bp = Blueprint("register", __name__)


@register_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    password_check = data.get("passwordCheck")

    # 필수 입력 확인
    if not username or not password or not password_check:
        return jsonify({"error": "Missing fields"}), 400

    # 비밀번호 확인
    if password != password_check:
        return jsonify({"error": "Passwords do not match"}), 400

    # user 객체에 passwordCheck는 포함시키지 않음
    user = {
        "username": username,
        "password": password,
        "video": "",
    }

    return (
        jsonify({"message": f"{username} signed up successfully!", "user": user}),
        201,
    )
