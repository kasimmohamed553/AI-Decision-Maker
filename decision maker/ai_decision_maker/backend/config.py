from dotenv import load_dotenv
load_dotenv()  # reads variables from a .env file in the project root, if present

import os

# ==========================================
# Project Configuration
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder where uploaded files will be stored
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

# Maximum upload size (20 MB)
MAX_CONTENT_LENGTH = 20 * 1024 * 1024

# Flask Settings
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

# Auth / DB Settings
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-this-in-.env")
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Decision Engine identifier (shown in API responses)
ENGINE_NAME = "Rule-Based Decision Engine v1.0"

# Required columns in uploaded sales dataset
REQUIRED_COLUMNS = [
    "Product",
    "Category",
    "Region",
    "Order_Date",
    "Order_Amount",
    "No_of_Items",
]
