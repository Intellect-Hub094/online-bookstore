# models/book.py
from extensions import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    feedbacks = db.relationship("Feedback", backref="book", lazy=True)
    transactions = db.relationship("Transaction", secondary="transaction_books", back_populates="books")