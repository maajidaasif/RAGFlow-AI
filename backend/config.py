import os
from dotenv import load_dotenv

# Load variables from backend/.env into the process environment.
# Must happen before the Config class is evaluated.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Database directory
DATABASE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "database")
)

# Automatically create database folder if it doesn't exist
os.makedirs(DATABASE_DIR, exist_ok=True)


# ============================================================
# SECRET KEY VALIDATION
# Fail immediately at import time if required secrets are
# missing. Never use hardcoded fallbacks.
# ============================================================

_SECRET_KEY = os.getenv("SECRET_KEY")
_JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

_missing = []

if not _SECRET_KEY:
    _missing.append("SECRET_KEY")

if not _JWT_SECRET_KEY:
    _missing.append("JWT_SECRET_KEY")

if _missing:
    raise RuntimeError(
        "\n\n"
        "============================================================\n"
        "CONFIGURATION ERROR — Missing required environment variables\n"
        "============================================================\n"
        f"Missing: {', '.join(_missing)}\n\n"
        "Steps to fix:\n"
        "  1. Copy backend/.env.example to backend/.env\n"
        "  2. Generate secure keys:\n"
        "       python -c \"import secrets; print(secrets.token_hex(32))\"\n"
        "  3. Set the generated values in backend/.env\n"
        "  4. Restart the application.\n"
        "============================================================\n"
    )


class Config:

    # --------------------------------------------------------
    # Debug mode
    # Reads FLASK_DEBUG from the environment.
    # Only enabled when explicitly set to "true" (case-insensitive).
    # Defaults to False so production is always safe.
    # --------------------------------------------------------
    DEBUG = os.getenv("FLASK_DEBUG", "false").strip().lower() == "true"

    SECRET_KEY = _SECRET_KEY

    JWT_SECRET_KEY = _JWT_SECRET_KEY

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(DATABASE_DIR, "researchmind.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Maximum allowed upload body size (50 MB).
    # Flask raises 413 automatically if the body exceeds this.
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # Absolute path to the uploads directory.
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")