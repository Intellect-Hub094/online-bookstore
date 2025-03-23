import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database connection string
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    # PayFast keys
    PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID")
    PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY")

    # Email configuration
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    # Flask secret key
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Disable Flask-SQLAlchemy modification tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder to store uploaded images
    UPLOAD_FOLDER = "static/uploads"
