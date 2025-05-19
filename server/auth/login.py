# server/auth/login.py
from flask import Blueprint, request, jsonify
from models import db, User  # DB에서 사용자 가져오기

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    # DB에서 사용자 조회
    user = User.query.filter_by(username=username).first()

    # 사용자가 존재하고 비밀번호가 일치할 경우
    if user and user.password == password:
        return jsonify({"message": "Login successful", "user": user.to_dict()}), 200

    return jsonify({"error": "Invalid credentials"}), 401
