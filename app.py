from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SubmitField,
    SelectField,
    FloatField,
    BooleanField,
    IntegerField,
    TextAreaField,
    FileField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
import smtplib
import os
import logging
from wtforms import DateField
from datetime import datetime
from flask import jsonify

# from dotenv import load_dotenv
# load_dotenv()
import stripe

# from flask_mail import Message, Email

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://postgres.ofwhjskhwnxfkrolxnue:ofwhjskhwnxfkrolxnue@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"  # Folder to store uploaded images
# Load Stripe keys from environment variables
app.config["STRIPE_PUBLIC_KEY"] = (
    "pk_test_51R40Iu4ZxyYyj0NLBbeVrUgsFf9o4dbuQ9TYp72qZcHVfyjq4ahYYexOj8GsbxzQ0AWZ9vswMjXzQsVv7DjtLSg00NREbh3lZ"
)
app.config["STRIPE_SECRET_KEY"] = (
    "sk_test_51R40Iu4ZxyYyj0NLFEeZLk1vIWVYgY9IjqzFLi2HallW4zoggXE70F6Ode93CNmXU2xKSmwpHwXTesJVGlHLhhXP00Xg5IiuLj"
)

stripe.api_key = app.config["STRIPE_SECRET_KEY"]
stripe_publishable_key = "pk_test_51R40Iu4ZxyYyj0NLSYS8HCFxvKrINdUpEluiVRKYEDRIK4qsyyWnu7aU1pblsM78CXr0TsEER2LrqwYy3ux3rplT00mng1htOL"  # Your publishable key


# Initialize SQLAlchemy and Flask-Login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Ensure the upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# User model
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


# Feedback model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    received = db.Column(db.Boolean, default=False, nullable=False)
    comments = db.Column(db.String(500), nullable=True)


# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    order_code = db.Column(db.String(50), unique=True, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)


# Faculty model
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    departments = db.relationship("Department", backref="faculty", lazy=True)


# Department model
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    courses = db.relationship("Course", backref="department", lazy=True)


# Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(
        db.Integer, db.ForeignKey("department.id"), nullable=False
    )
    books = db.relationship("Book", backref="course", lazy=True)


# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    feedbacks = db.relationship("Feedback", backref="book", lazy=True)
    transactions = db.relationship(
        "Transaction", secondary="transaction_books", back_populates="books"
    )


# Transaction model
class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Define back_populates in the Transaction model
    user = db.relationship("User", back_populates="transactions")

    # Relationship with 'Book' model through 'transaction_books' association table
    books = db.relationship(
        "Book", secondary="transaction_books", back_populates="transactions"
    )

    def __repr__(self):
        return f"<Transaction {self.id}>"


# TransactionBooks association table for many-to-many relationship between transactions and books
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


# Registration Form
from wtforms import DateField


# Registration Form
class RegistrationForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    profile_picture = FileField("Profile Picture")
    date_of_birth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[DataRequired()]
    )
    marital_status = SelectField(
        "Marital Status",
        choices=[
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
        ],
        validators=[DataRequired()],
    )
    full_name = StringField("Full Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Register")


# Login Form
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Delivery Address Form
class DeliveryAddressForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    cellphone = StringField(
        "Cellphone Number", validators=[DataRequired(), Length(min=10, max=15)]
    )
    address = StringField("Address", validators=[DataRequired(), Length(max=200)])
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    state = StringField("State/Province", validators=[DataRequired(), Length(max=100)])
    postal_code = StringField(
        "Postal Code", validators=[DataRequired(), Length(max=20)]
    )
    country = StringField("Country", validators=[DataRequired(), Length(max=100)])
    notes = TextAreaField("Additional Notes", validators=[Length(max=500)])
    submit = SubmitField("Submit Order")


# Feedback Form
class FeedbackForm(FlaskForm):
    book_id = SelectField("Select Book", coerce=int, validators=[DataRequired()])
    received = SelectField(
        "Did you receive the book?",
        choices=[("yes", "Yes"), ("no", "No")],
        validators=[DataRequired()],
    )
    comments = StringField("Comments (if any)")
    submit = SubmitField("Submit Feedback")


# Add Book Form
class AddBookForm(FlaskForm):
    faculty = SelectField("Faculty", coerce=int, validators=[DataRequired()])
    department = SelectField("Department", coerce=int, validators=[DataRequired()])
    course = SelectField("Course", coerce=int, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    image = FileField("Book Image", validators=[DataRequired()])
    submit = SubmitField("Add Book")

    # Profile Form


class ProfileForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    profile_picture = FileField("Update Profile Picture")
    date_of_birth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[DataRequired()]
    )
    marital_status = SelectField(
        "Marital Status",
        choices=[
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
        ],
        validators=[DataRequired()],
    )
    full_name = StringField("Full Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Update Profile")


class EditUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    is_admin = BooleanField("Is Admin")
    submit = SubmitField("Update User")


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Helper functions
def calculate_total_price(cart_items):
    total = 0
    for book_id, quantity in cart_items.items():
        book = Book.query.get(book_id)
        if book:
            total += book.price * quantity
    return total


def get_books_info(cart_items):
    books_info = {}
    for book_id in cart_items.keys():
        book = Book.query.get(book_id)
        if book:
            books_info[book_id] = {
                "title": book.title,
                "author": book.author,
                "price": book.price,
                "quantity": cart_items[book_id],
            }
    return books_info

    # def process_payment(payment_method, payment_details):
    # Simulated payment processing logic
    return True  # Assume payment is successful


def generate_order_code():
    return "ORD-" + str(random.randint(1000, 9999))  # Generate a random Order Code


def send_confirmation_email(recipient_email, order_code):
    # Gmail SMTP Configuration
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # For Gmail
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = "Order Confirmation"
        body = f"Your order has been confirmed. Your order code is {order_code}."
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL_ADDRESS, recipient_email, message)
        server.quit()
    except Exception as e:
        print("Failed to send the email:", e)


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home" if not user.is_admin else "admin_dashboard"))
        else:
            flash("Login failed. Check your email and password.", "error")

    return render_template("login.html", form=form)


from datetime import datetime


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Handle profile picture upload
        profile_picture_url = None
        if form.profile_picture.data:
            profile_picture = form.profile_picture.data
            filename = secure_filename(profile_picture.filename)
            profile_picture_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            profile_picture.save(profile_picture_path)
            profile_picture_url = f"uploads/{filename}"

        # Create a new user
        hashed_password = generate_password_hash(
            form.password.data, method="pbkdf2:sha256"
        )
        new_user = User(
            profile_id=form.profile_id.data,  # If not auto-generated
            email=form.email.data,
            password=hashed_password,
            profile_picture=profile_picture_url,
            date_of_birth=form.date_of_birth.data,
            marital_status=form.marital_status.data,
            full_name=form.full_name.data,
            phone_number=form.phone_number.data,
            address=form.address.data,
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedbackForm()
    form.book_id.choices = [(book.id, book.title) for book in Book.query.all()]

    if form.validate_on_submit():
        new_feedback = Feedback(
            user_id=current_user.id,
            book_id=form.book_id.data,
            received=form.received.data == "yes",
            comments=form.comments.data,
        )
        db.session.add(new_feedback)
        db.session.commit()
        flash("Feedback submitted successfully!", "success")
        return redirect(url_for("home"))

    return render_template("feedback.html", form=form)


@app.route("/my_feedback")
@login_required
def my_feedback():
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).all()
    return render_template("my_feedback.html", feedbacks=feedbacks)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        # Handle profile picture upload
        if form.profile_picture.data:
            profile_picture = form.profile_picture.data
            filename = secure_filename(profile_picture.filename)
            profile_picture_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            profile_picture.save(profile_picture_path)
            current_user.profile_picture = f"uploads/{filename}"

        # Update profile fields
        current_user.email = form.email.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.marital_status = form.marital_status.data
        current_user.full_name = form.full_name.data
        current_user.phone_number = form.phone_number.data
        current_user.address = form.address.data

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    # Pre-fill the form with current user data
    form.email.data = current_user.email
    form.date_of_birth.data = current_user.date_of_birth
    form.marital_status.data = current_user.marital_status
    form.full_name.data = current_user.full_name
    form.phone_number.data = current_user.phone_number
    form.address.data = current_user.address
    return render_template("profile.html", form=form, user=current_user)


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))

    users = User.query.all()
    books = Book.query.all()
    feedbacks = Feedback.query.all()
    orders = Order.query.all()  # Fetching orders for admin
    return render_template(
        "admin_dashboard.html",
        users=users,
        books=books,
        feedbacks=feedbacks,
        orders=orders,
    )


@app.route("/admin/manage_users")
@login_required
def manage_users():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    users = User.query.all()
    return render_template("manage_users.html", users=users)


@app.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)  # Use the EditUserForm

    if form.validate_on_submit():
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("manage_users"))

    return render_template("edit_user.html", form=form, user=user)


from flask import render_template, request, redirect, url_for, flash


@app.route("/admin/manage-transactions")
def manage_transactions():
    transactions = Transaction.query.all()  # Get all transactions from the database
    return render_template("admin/manage_transactions.html", transactions=transactions)


@app.route("/admin/update-transaction-status/<int:transaction_id>", methods=["POST"])
def update_transaction_status(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    # Update the payment status from the form
    new_status = request.form["payment_status"]
    transaction.payment_status = new_status
    db.session.commit()

    flash("Transaction status updated successfully!", "success")
    return redirect(url_for("manage_transactions"))


@app.route("/create-transaction", methods=["POST"])
def create_transaction():
    # Example: Assume that the user has ordered books
    user_id = 1  # Get the logged-in user's ID
    books = Book.query.filter(
        Book.id.in_(request.form.getlist("book_ids"))
    ).all()  # Get the books ordered
    total_amount = sum([book.price for book in books])  # Calculate total amount

    # Create a new transaction
    transaction = Transaction(
        user_id=user_id, total_amount=total_amount, payment_status="Pending"
    )
    db.session.add(transaction)
    db.session.commit()

    # Add the books to the transaction (many-to-many relationship)
    transaction.books.extend(books)
    db.session.commit()

    flash("Transaction created successfully! Please proceed with payment.", "success")
    return redirect(url_for("view_transaction", transaction_id=transaction.id))


@app.route("/admin/transaction/<int:transaction_id>")
def view_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template("admin/view_transaction.html", transaction=transaction)


@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for("manage_users"))


@app.route("/admin/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    form = AddBookForm()

    # Populate faculty dropdown
    form.faculty.choices = [(f.id, f.name) for f in Faculty.query.all()]
    form.department.choices = []  # Initially empty, populated via JavaScript
    form.course.choices = []  # Initially empty, populated via JavaScript

    if form.validate_on_submit():
        # Handle file upload
        image = form.image.data
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)
        image_url = f"uploads/{filename}"

        # Create a new book
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            course_id=form.course.data,
            price=form.price.data,
            image_url=image_url,
        )
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for("books"))

    return render_template("add_book.html", form=form)


@app.route("/get_departments/<int:faculty_id>")
def get_departments(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    departments_list = [{"id": d.id, "name": d.name} for d in departments]
    return jsonify(departments_list)


@app.route("/get_courses/<int:department_id>")
def get_courses(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    courses_list = [{"id": c.id, "name": c.name} for c in courses]
    return jsonify(courses_list)


@app.route("/admin/delete_book/<int:book_id>", methods=["POST"])
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/edit_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    book = Book.query.get_or_404(book_id)
    form = AddBookForm(obj=book)  # Reuse the AddBookForm for editing

    # Populate the course dropdown
    form.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

    if form.validate_on_submit():
        try:
            # Handle file upload
            if form.image.data:
                image = form.image.data
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(image_path)
                book.image_url = f"uploads/{filename}"  # Update image URL

            # Update book details
            book.title = form.title.data
            book.author = form.author.data
            book.price = form.price.data
            book.course_id = form.course_id.data
            db.session.commit()
            flash("Book updated successfully!", "success")
            return redirect(url_for("books"))
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update book. Error: {str(e)}", "error")

    return render_template("edit_book.html", form=form, book=book)


@app.route("/select_faculty", methods=["GET"])
@login_required
def select_faculty():
    faculties = Faculty.query.all()
    return render_template("select_faculty.html", faculties=faculties)


@app.route("/select_department/<int:faculty_id>", methods=["GET"])
@login_required
def select_department(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return render_template("select_department.html", departments=departments)


@app.route("/select_course/<int:department_id>", methods=["GET"])
@login_required
def select_course(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    return render_template(
        "select_course.html", courses=courses, department_id=department_id
    )


@app.route("/books/<int:course_id>", methods=["GET"])
@login_required
def course_books(course_id):
    course = Course.query.get_or_404(course_id)
    books = Book.query.filter_by(course_id=course_id).all()
    return render_template("course_books.html", books=books, course=course)


def calculate_total_price(cart_items):
    total = 0.0
    for book_id, item in cart_items.items():
        # Ensure item is a dictionary and has 'price' and 'quantity' keys
        if isinstance(item, dict) and "price" in item and "quantity" in item:
            total += item["price"] * item["quantity"]
        else:
            # Log an error or handle invalid items
            print(f"Invalid item in cart: {item}")
    return total


@app.route("/cart", methods=["GET"])
@login_required
def cart():
    # Retrieve the cart from the session or initialize it as an empty dictionary
    cart_items = session.get("cart", {})

    # Ensure the cart is a dictionary (in case it was corrupted or improperly set)
    if not isinstance(cart_items, dict):
        cart_items = {}

    # Validate and clean up cart_items to ensure proper structure
    cleaned_cart_items = {}
    for book_id, item in cart_items.items():
        if isinstance(item, dict) and "price" in item and "quantity" in item:
            # Ensure price is a float and quantity is an integer
            cleaned_cart_items[book_id] = {
                "title": item.get("title", "Unknown Title"),
                "author": item.get("author", "Unknown Author"),
                "price": float(item["price"]),
                "quantity": int(item["quantity"]),
                "image_url": item.get("image_url", "uploads/default_book.jpg"),
            }
        else:
            # Log invalid items and skip them
            print(f"Invalid item in cart (skipping): {item}")

    # Calculate the total price of the cart
    total_price = calculate_total_price(cleaned_cart_items)

    # Save the cleaned cart back to the session (optional)
    session["cart"] = cleaned_cart_items

    # Render the cart page with the cart items and total price
    return render_template(
        "cart.html", cart_items=cleaned_cart_items, total_price=total_price
    )


@app.route("/add_to_cart/<int:book_id>", methods=["POST"])
@login_required
def add_to_cart(book_id):
    try:
        # Fetch the book from the database or return a 404 error if not found
        book = Book.query.get_or_404(book_id)

        # Retrieve the cart from the session or initialize it as an empty dictionary
        cart = session.get("cart", {})

        # Ensure the cart is a dictionary (in case it was corrupted or improperly set)
        if not isinstance(cart, dict):
            cart = {}

        # If the book is already in the cart, increment the quantity
        if str(book_id) in cart:
            # Ensure the cart entry for this book is a dictionary
            if isinstance(cart[str(book_id)], dict):
                cart[str(book_id)]["quantity"] += 1
            else:
                # If it's not a dictionary, reset it to a proper structure
                cart[str(book_id)] = {
                    "title": book.title,
                    "author": book.author,
                    "price": float(book.price),  # Ensure price is a float
                    "quantity": 1,
                    "image_url": book.image_url,  # Include image URL
                }
        else:
            # If the book is not in the cart, add it with a quantity of 1 and its details
            cart[str(book_id)] = {
                "title": book.title,
                "author": book.author,
                "price": float(book.price),  # Ensure price is a float
                "quantity": 1,
                "image_url": book.image_url,  # Include image URL
            }

        # Save the updated cart back to the session
        session["cart"] = cart

        # Flash a success message to the user
        flash(f"{book.title} has been added to your cart!", "success")

    except Exception as e:
        # Log the error and flash a user-friendly message
        print(f"Error adding to cart: {e}")
        flash(
            "An error occurred while adding the book to your cart. Please try again.",
            "error",
        )

    # Redirect the user to the course books page
    return redirect(url_for("course_books", course_id=book.course_id))


@app.route("/remove_from_cart/<int:book_id>", methods=["POST"])
@login_required
def remove_from_cart(book_id):
    cart = session.get("cart", {})
    if str(book_id) in cart:
        del cart[str(book_id)]
        session["cart"] = cart
        flash("Book removed from the cart!", "success")
    else:
        flash("Book not found in the cart!", "error")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_items = session.get("cart", {})

    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("course_books"))

    total_price = sum(item["price"] * item["quantity"] for item in cart_items.values())

    try:
        # Create a PaymentIntent for Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Convert amount to cents
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        client_secret = intent.client_secret
    except stripe.error.StripeError as e:
        flash("Failed to create payment intent. Please try again.", "error")
        return redirect(url_for("course_books"))

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_price=total_price,
        client_secret=client_secret,
        stripe_publishable_key=stripe_publishable_key,  # Make sure you pass your Stripe publishable key
    )


@app.route("/payment_intent_confirm", methods=["POST"])
@login_required
def payment_intent_confirm():
    try:
        # Get payment intent ID and payment method ID from the form
        payment_intent_id = request.form["payment_intent_id"]
        payment_method_id = request.form["payment_method_id"]

        # Confirm the PaymentIntent with Stripe
        intent = stripe.PaymentIntent.confirm(
            payment_intent_id, payment_method=payment_method_id
        )

        # Check if the payment succeeded
        if intent.status == "succeeded":
            flash("Payment Successful! Thank you for your purchase.", "success")
            session.pop("cart", None)  # Clear the cart after payment success
            return redirect(url_for("order_success"))  # Redirect to order success page
        else:
            flash("Payment failed. Please try again.", "error")
            return redirect(url_for("checkout"))

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("checkout"))


@app.route("/payment-success")
def payment_success():
    payment_intent_id = request.args.get("payment_intent")

    if payment_intent_id:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            amount = payment_intent.amount_received / 100  # Convert cents to dollars

            # Clear the cart after successful payment
            session.pop("cart", None)

            # Redirect to the success page with payment details
            return redirect(
                url_for(
                    "success_page", payment_intent_id=payment_intent.id, amount=amount
                )
            )
        except stripe.error.StripeError as e:
            return render_template("success.html", error=str(e))
    else:
        return render_template("success.html", error="Payment details not found.")


@app.route("/success")
def success_page():
    payment_intent_id = request.args.get("payment_intent_id")
    amount = request.args.get("amount")

    # Retrieve the payment intent details from Stripe (optional, if you want to display more details)
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return render_template(
            "success.html", payment_intent=payment_intent, amount=amount
        )
    except stripe.error.StripeError as e:
        return render_template("success.html", error=str(e))


@app.route("/delivery_address", methods=["GET", "POST"])
@login_required
def delivery_address():
    form = DeliveryAddressForm()

    if form.validate_on_submit():
        # Save the order details to the database
        new_order = Order(
            user_id=current_user.id,
            full_name=form.full_name.data,
            email=form.email.data,
            cellphone=form.cellphone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            notes=form.notes.data,
            order_code=generate_order_code(),
            payment_method="stripe",
        )
        db.session.add(new_order)
        db.session.commit()

        # Clear the cart
        session.pop("cart", None)

        # Send confirmation email
        send_confirmation_email(new_order)

        flash("Order confirmed! A confirmation email has been sent.", "success")
        return redirect(url_for("success_page"))

    return render_template("delivery_address.html", form=form)


def send_confirmation_email(order):
    msg = Message(
        subject="Order Confirmation",
        sender="your_email@example.com",  # Replace with your email
        recipients=[order.email],
        reply_to="your_email@example.com",  # Allow user to reply to this email
    )
    msg.body = f"""
    Thank you for your order, {order.full_name}!

    Order Details:
    - Order Code: {order.order_code}
    - Address: {order.address}, {order.city}, {order.state}, {order.postal_code}, {order.country}
    - Cellphone: {order.cellphone}
    - Notes: {order.notes}

    If you have any questions, please reply to this email.

    Thank you for shopping with us!
    """


# mail.send(msg)


@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    try:
        # Get the total price from the cart (you can calculate it dynamically)
        cart_items = session.get("cart", {})
        total_price = calculate_total_price(
            cart_items
        )  # Assuming this function returns the total price in dollars

        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Convert total price to cents
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )

        # Return the client secret to the frontend
        return {"client_secret": intent.client_secret}
    except Exception as e:
        return str(e), 400


# @app.route('/payment-success')
# def payment_success():
# return render_template('payment_success.html')


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    return render_template("contact.html")


# Create tables if they don't exist (initial setup)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Faculty.query.first():
            faculty1 = Faculty(name="Engineering")
            faculty2 = Faculty(name="Arts")
            db.session.add_all([faculty1, faculty2])
            db.session.commit()

            # Add Departments
            department1 = Department(name="Computer Science", faculty_id=faculty1.id)
            department2 = Department(name="Mechanical", faculty_id=faculty1.id)
            department3 = Department(name="Fine Arts", faculty_id=faculty2.id)
            db.session.add_all([department1, department2, department3])
            db.session.commit()

            # Add Courses
            course1 = Course(name="Data Structures", department_id=department1.id)
            course2 = Course(name="Thermodynamics", department_id=department2.id)
            db.session.add_all([course1, course2])
            db.session.commit()

            # Adding sample books
            book1 = Book(
                title="Python Programming",
                author="Author A",
                course_id=course1.id,
                price=150.0,
                image_url="path/to/image1.jpg",
            )
            book2 = Book(
                title="Engineering Mechanics",
                author="Author B",
                course_id=course2.id,
                price=200.0,
                image_url="path/to/image2.jpg",
            )
            db.session.add_all([book1, book2])
            db.session.commit()

    app.run(debug=True)
