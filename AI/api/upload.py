import os
from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload', __name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('video')
    if file is None:
        return jsonify({"error": "No video uploaded"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    return jsonify({"message": "Upload successful", "video_path": save_path})