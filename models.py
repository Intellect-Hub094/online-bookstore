from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer")
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    def __repr__(self):
        return f"<User {self.id}>"


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    license_number = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    vehicle_info = db.Column(db.String(100), nullable=False)
    license_image = db.Column(db.String(255), nullable=False)  # New field
    # Add driver-specific fields

    user = db.relationship("User", backref=db.backref("driver", uselist=False))

    def __repr__(self):
        return f"<Driver {self.user.id}>"


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    phone = db.Column(db.String(20), nullable=False)  # New field
    address = db.Column(db.Text, nullable=False)  # New field
    student_id = db.Column(db.String(50))  # New field
    # Add customer-specific fields like address, phone number, etc.

    user = db.relationship("User", backref=db.backref("customer", uselist=False))

    def __repr__(self):
        return f"<Customer {self.user.id}>"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", backref=db.backref("admin", uselist=False))

    def __repr__(self):
        return f"<Admin {self.user.id}>"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    faculty = db.Column(db.String(50), nullable=False)

    @staticmethod
    def get_low_stock_books(threshold=10):  
        return Book.query.filter(Book.stock <= threshold).all()

    def __repr__(self):
        return f"<Book {self.title}>"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")
    cancellation_reason = db.Column(db.Text)
    shipping_address = db.Column(db.Text, nullable=False)
    
    customer = db.relationship("Customer", backref="orders")
    user = db.relationship("User", backref="orders")
    order_items = db.relationship("Purchase", backref="order", lazy=True)
    
    @property
    def can_cancel(self):
        return self.status == "pending"
    
    def calculate_total(self):
        return sum(item.subtotal for item in self.order_items)

    def __repr__(self):
        return f"<Order {self.id}>"


class Purchase(db.Model):  # OrderItem
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at the time of purchase

    book = db.relationship("Book", backref="purchases")
    
    @property
    def subtotal(self):
        return self.quantity * self.price

    def __repr__(self):
        return f"<Purchase {self.quantity} x {self.book.title}>"


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    customer = db.relationship("Customer", backref="cart_items")
    book = db.relationship("Book", backref="cart_entries")

    def __repr__(self):
        return f"<Cart Item: {self.book.title}>"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_provider = db.Column(db.String(50), nullable=False)  # e.g., "PayFast", "Stripe"
    transaction_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")
    reference_number = db.Column(db.String(100), unique=True)
    payment_details = db.Column(db.JSON)  # Store provider-specific payment details

    order = db.relationship("Order", backref=db.backref("transaction", uselist=False))

    @staticmethod
    def create_transaction(order, payment_method, payment_provider):
        from datetime import datetime
        transaction = Transaction(
            order_id=order.id,
            payment_method=payment_method,
            payment_provider=payment_provider,
            transaction_date=datetime.utcnow(),
            amount=order.total_amount,
            status="pending"
        )
        return transaction

    def mark_as_paid(self, reference_number, payment_details=None):
        self.status = "completed"
        self.reference_number = reference_number
        if payment_details:
            self.payment_details = payment_details
        self.order.status = "processing"

    def __repr__(self):
        return f"<Transaction {self.id}>"


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    added_date = db.Column(db.DateTime, nullable=False)

    customer = db.relationship("Customer", backref="wishlist_items")
    book = db.relationship("Book", backref="wishlist_entries")

    def __repr__(self):
        return f"<Wishlist Item: {self.book.title}>"
