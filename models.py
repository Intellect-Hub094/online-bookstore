# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy (will be linked to the app in app.py)
db = SQLAlchemy()

# User model (for students, admins, and suppliers)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.String(50), unique=True, nullable=False)  # Unique profile ID
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'admin', 'supplier'
    full_name = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    profile_picture = db.Column(db.String(250), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    marital_status = db.Column(db.String(50), nullable=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)

# Category model (for book categorization)
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# Book-Category association table (many-to-many)
book_category = db.Table('book_category',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# Faculty model (DUT-specific)
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    departments = db.relationship('Department', backref='faculty', lazy=True)

# Department model (DUT-specific)
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    courses = db.relationship('Course', backref='department', lazy=True)

# Course model (DUT-specific)
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    books = db.relationship('Book', backref='course', lazy=True)

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)  # Optional for non-course books
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    isbn = db.Column(db.String(13), unique=True, nullable=True)
    image_url = db.Column(db.String(250), nullable=True)
    publication_date = db.Column(db.Date, nullable=True)
    categories = db.relationship('Category', secondary=book_category, backref='books')
    reviews = db.relationship('Review', backref='book', lazy=True)
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='book', lazy=True)

# Review model (replaces Feedback)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.String(500), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# Wishlist model (for favorites)
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_code = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)  # Total order amount
    payment_status = db.Column(db.String(50), default='pending', nullable=False)  # 'pending', 'paid', 'failed'
    items = db.relationship('OrderItem', backref='order', lazy=True)
    delivery = db.relationship('Delivery', backref='order', uselist=False)

# OrderItem model (books in an order)
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of order

# Delivery model (delivery or pickup)
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    delivery_type = db.Column(db.String(20), nullable=False)  # 'delivery' or 'pickup'
    address = db.Column(db.String(250), nullable=True)  # For delivery
    pickup_location = db.Column(db.String(100), nullable=True)  # For pickup (e.g., DUT campus)
    status = db.Column(db.String(50), default='pending', nullable=False)  # 'pending', 'shipped', 'delivered'
    delivery_date = db.Column(db.DateTime, nullable=True)

# Payment model (for Stripe integration)
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    stripe_payment_id = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'pending', 'completed', 'failed'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    order = db.relationship('Order', backref='payment', uselist=False)

# SupplierStock model (for book suppliers)
class SupplierStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity_supplied = db.Column(db.Integer, nullable=False)
    supplied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    supplier = db.relationship('User', backref='supplied_stocks')
    book = db.relationship('Book', backref='supplied_stocks')