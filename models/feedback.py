from extensions import db
# Feedback model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    received = db.Column(db.Boolean, default=False, nullable=False)
    comments = db.Column(db.String(500), nullable=True)
