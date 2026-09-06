import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required

from config import *
from models import db, bcrypt
from auth import auth_bp
from analyzer import analyze_sales_data
from decision_engine import generate_ai_decision
from recommendation_engine import generate_recommendations

app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------
# Home Route
# ---------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "AI Decision Maker Backend Running",
        "engine": ENGINE_NAME
    })


# ---------------------------------------
# Upload & Analyze Route (protected)
# ---------------------------------------
@app.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "Please choose a file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Only CSV, XLSX and XLS files are allowed"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    try:
        summary = analyze_sales_data(filepath)
        recommendations = generate_recommendations(summary)
        decision = generate_ai_decision(summary)

        return jsonify({
            "success": True,
            "filename": file.filename,
            "summary": summary,
            "recommendations": recommendations,
            "decision": decision
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        # clean up uploaded file after processing
        if os.path.exists(filepath):
            os.remove(filepath)


# ---------------------------------------
# Health Check
# ---------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Running",
        "Engine": ENGINE_NAME,
        "Backend": "Flask",
        "Version": "1.0"
    })


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
