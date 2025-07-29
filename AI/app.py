from flask import Flask
from api.analyze import analyze_bp
from api.upload import upload_bp

app = Flask(__name__)

app.register_blueprint(upload_bp)
app.register_blueprint(analyze_bp)

if __name__ == '__main__':
    app.run(debug=True)