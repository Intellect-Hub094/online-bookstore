import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database connection string
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    # PayFast keys
    PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID")
    PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY")
    PAYFAST_PASSPHRASE = os.getenv("PAYFAST_PASSPHRASE")
    PAYFAST_RETURN_URL = os.getenv(
        "PAYFAST_RETURN_URL", "http://localhost:5000/checkout/return"
    )
    PAYFAST_CANCEL_URL = os.getenv(
        "PAYFAST_CANCEL_URL", "http://localhost:5000/checkout/cancel"
    )
    PAYFAST_NOTIFY_URL = os.getenv(
        "PAYFAST_NOTIFY_URL", "http://localhost:5000/checkout/notify"
    )

    # Email configuration
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    # Flask secret key
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Disable Flask-SQLAlchemy modification tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder to store uploaded images
    BOOKS_UPLOAD_FOLDER = "static/uploads/books"
    DRIVER_LICENSE_UPLOAD_FOLDER = "static/uploads/driver_license"
