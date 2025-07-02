from .uploadVideo import upload_video_bp


def register_video_blueprints(app):
    app.register_blueprint(upload_video_bp)
