from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20), default="customer"
    )  # e.g., 'admin', 'customer', 'driver'
    # Add other common fields like first_name, last_name, etc.

    def __repr__(self):
        return f"<User {self.username}>"


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    license_number = db.Column(db.String(50), unique=True)
    # Add driver-specific fields

    user = db.relationship("User", backref=db.backref("driver", uselist=False))

    def __repr__(self):
        return f"<Driver {self.user.username}>"


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # Add customer-specific fields like address, phone number, etc.

    user = db.relationship("User", backref=db.backref("customer", uselist=False))

    def __repr__(self):
        return f"<Customer {self.user.username}>"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", backref=db.backref("admin", uselist=False))

    def __repr__(self):
        return f"<Admin {self.user.username}>"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    # Add other book-related fields like publication date, genre, etc.

    def __repr__(self):
        return f"<Book {self.title}>"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20), default="pending"
    )  # e.g., 'pending', 'shipped', 'delivered'
    # Add order-related fields like shipping address, etc.

    customer = db.relationship("Customer", backref="orders")
    order_items = db.relationship("Purchase", backref="order", lazy=True)

    def __repr__(self):
        return f"<Order {self.id}>"


class Purchase(db.Model):  # OrderItem
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at the time of purchase

    book = db.relationship("Book", backref="purchases")

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
    payment_method = db.Column(db.String(50))
    transaction_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20), default="pending"
    )  # e.g., 'pending', 'completed', 'failed'

    order = db.relationship("Order", backref=db.backref("transaction", uselist=False))

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
