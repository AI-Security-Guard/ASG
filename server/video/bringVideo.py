import os
from flask import Blueprint, request, jsonify
from models import User
from flask import send_file


bring_video_bp = Blueprint("bringVideo", __name__)
UPLOAD_FOLDER = "uploaded_videos"


@bring_video_bp.route("/bringVideo", methods=["GET"])
def bring_video():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "username이 없음"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "유저가 없음"}), 404

    # 파일이 실제 존재하는지 확인
    if not os.path.exists(user.video):
        return jsonify({"error": "video 파일 경로가 잘못되었거나 없음"}), 404

    return send_file(user.video, as_attachment=True)
