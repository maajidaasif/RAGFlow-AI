import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database directory
DATABASE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "database")
)

# Automatically create database folder if it doesn't exist
os.makedirs(DATABASE_DIR, exist_ok=True)


class Config:

    SECRET_KEY = "researchmind_ai_secret_key"

    JWT_SECRET_KEY = "researchmind_jwt_secret_key"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(DATABASE_DIR, "researchmind.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False