from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(250), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    marital_status = db.Column(db.String(50), nullable=True)
    full_name = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    feedbacks = db.relationship("Feedback", backref="user", lazy=True)
    orders = db.relationship("Order", backref="user", lazy=True)
    transactions = db.relationship("Transaction", back_populates="user", lazy=True)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    received = db.Column(db.Boolean, default=False, nullable=False)
    comments = db.Column(db.String(500), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    order_code = db.Column(db.String(50), unique=True, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    departments = db.relationship("Department", backref="faculty", lazy=True)

class Department(db.Model):
    id = db.Column(db.Integer, primary key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    courses = db.relationship("Course", backref="department", lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=False)
    books = db.relationship("Book", backref="course", lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    feedbacks = db.relationship("Feedback", backref="book", lazy=True)
    transactions = db.relationship("Transaction", secondary="transaction_books", back_populates="books")

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="transactions")
    books = db.relationship("Book", secondary="transaction_books", back_populates="transactions")

class TransactionBooks(db.Model):
    __tablename__ = "transaction_books"
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id", ondelete="CASCADE"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True)
