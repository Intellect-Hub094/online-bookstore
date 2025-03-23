# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Secret key for Flask sessions
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

    # Database connection string
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "postgresql+psycopg2://postgres.ofwhjskhwnxfkrolxnue:ofwhjskhwnxfkrolxnue@aws-0-eu-central-1.pooler.supabase.com:6543/postgres",
    )

    # Disable Flask-SQLAlchemy modification tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder to store uploaded images
    UPLOAD_FOLDER = "static/uploads"

    # Stripe keys
    STRIPE_PUBLIC_KEY = os.getenv(
        "STRIPE_PUBLIC_KEY",
        "pk_test_51R40Iu4ZxyYyj0NLBbeVrUgsFf9o4dbuQ9TYp72qZcHVfyjq4ahYYexOj8GsbxzQ0AWZ9vswMjXzQsVv7DjtLSg00NREbh3lZ",
    )
    STRIPE_SECRET_KEY = os.getenv(
        "STRIPE_SECRET_KEY",
        "sk_test_51R40Iu4ZxyYyj0NLFEeZLk1vIWVYgY9IjqzFLi2HallW4zoggXE70F6Ode93CNmXU2xKSmwpHwXTesJVGlHLhhXP00Xg5IiuLj",
    )

    # Email configuration
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")