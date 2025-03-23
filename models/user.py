# models/user.py
from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(
        db.String(50), unique=True, nullable=False
    )  # Unique profile ID
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(250), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)  # Date of birth
    marital_status = db.Column(db.String(50), nullable=True)  # Marital status
    full_name = db.Column(db.String(150), nullable=True)  # Full name
    phone_number = db.Column(db.String(20), nullable=True)  # Phone number
    address = db.Column(db.String(250), nullable=True)  # Address
    feedbacks = db.relationship("Feedback", backref="user", lazy=True)
    orders = db.relationship("Order", backref="user", lazy=True)

    # Define back_populates in the User model
    transactions = db.relationship("Transaction", back_populates="user", lazy=True)

