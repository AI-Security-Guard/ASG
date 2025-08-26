# app.py
from flask import Flask
from routes import analyze_bp
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.register_blueprint(analyze_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
