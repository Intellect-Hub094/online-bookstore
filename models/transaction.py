# models/transaction.py
from datetime import datetime
from extensions import db

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="transactions")
    books = db.relationship("Book", secondary="transaction_books", back_populates="transactions")