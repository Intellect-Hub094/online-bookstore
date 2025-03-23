# models/transaction_books.py
from extensions import db

class TransactionBooks(db.Model):
    __tablename__ = "transaction_books"
    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("transactions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    book_id = db.Column(
        db.Integer, db.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True
    )