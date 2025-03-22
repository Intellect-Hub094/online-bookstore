from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import random
import smtplib
import os
import stripe

from project import db, login_manager
from project.models import User, Feedback, Order, Faculty, Department, Course, Book, Transaction, TransactionBooks
from project.forms import RegistrationForm, LoginForm, DeliveryAddressForm, FeedbackForm, AddBookForm, ProfileForm, EditUserForm

routes = Blueprint('routes', __name__)

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLIC_KEY")

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

def generate_order_code():
    return "ORD-" + str(random.randint(1000, 9999))

def send_confirmation_email(recipient_email, order_code):
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
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
@routes.route("/")
def index():
    return render_template("index.html")

@routes.route("/about")
def about():
    return render_template("about.html")

@routes.route("/login", methods=["GET", "POST"])
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

@routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        profile_picture_url = None
        if form.profile_picture.data:
            profile_picture = form.profile_picture.data
            filename = secure_filename(profile_picture.filename)
            profile_picture_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            profile_picture.save(profile_picture_path)
            profile_picture_url = f"uploads/{filename}"

        hashed_password = generate_password_hash(form.password.data, method="pbkdf2:sha256")
        new_user = User(
            profile_id=form.profile_id.data,
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

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@routes.route("/home")
@login_required
def home():
    return render_template("home.html")

@routes.route("/feedback", methods=["GET", "POST"])
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

@routes.route("/my_feedback")
@login_required
def my_feedback():
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).all()
    return render_template("my_feedback.html", feedbacks=feedbacks)

@routes.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            profile_picture = form.profile_picture.data
            filename = secure_filename(profile_picture.filename)
            profile_picture_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            profile_picture.save(profile_picture_path)
            current_user.profile_picture = f"uploads/{filename}"

        current_user.email = form.email.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.marital_status = form.marital_status.data
        current_user.full_name = form.full_name.data
        current_user.phone_number = form.phone_number.data
        current_user.address = form.address.data

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    form.email.data = current_user.email
    form.date_of_birth.data = current_user.date_of_birth
    form.marital_status.data = current_user.marital_status
    form.full_name.data = current_user.full_name
    form.phone_number.data = current_user.phone_number
    form.address.data = current_user.address
    return render_template("profile.html", form=form, user=current_user)

@routes.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))

    users = User.query.all()
    books = Book.query.all()
    feedbacks = Feedback.query.all()
    orders = Order.query.all()
    return render_template("admin_dashboard.html", users=users, books=books, feedbacks=feedbacks, orders=orders)

@routes.route("/admin/manage_users")
@login_required
def manage_users():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    users = User.query.all()
    return render_template("manage_users.html", users=users)

@routes.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("manage_users"))

    return render_template("edit_user.html", form=form, user=user)

@routes.route("/admin/manage-transactions")
def manage_transactions():
    transactions = Transaction.query.all()
    return render_template("admin/manage_transactions.html", transactions=transactions)

@routes.route("/admin/update-transaction-status/<int:transaction_id>", methods=["POST"])
def update_transaction_status(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    new_status = request.form["payment_status"]
    transaction.payment_status = new_status
    db.session.commit()
    flash("Transaction status updated successfully!", "success")
    return redirect(url_for("manage_transactions"))

@routes.route("/create-transaction", methods=["POST"])
def create_transaction():
    user_id = 1
    books = Book.query.filter(Book.id.in_(request.form.getlist("book_ids"))).all()
    total_amount = sum([book.price for book in books])

    transaction = Transaction(user_id=user_id, total_amount=total_amount, payment_status="Pending")
    db.session.add(transaction)
    db.session.commit()

    transaction.books.extend(books)
    db.session.commit()

    flash("Transaction created successfully! Please proceed with payment.", "success")
    return redirect(url_for("view_transaction", transaction_id=transaction.id))

@routes.route("/admin/transaction/<int:transaction_id>")
def view_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template("admin/view_transaction.html", transaction=transaction)

@routes.route("/admin/delete_user/<int:user_id>", methods=["POST"])
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

@routes.route("/admin/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    form = AddBookForm()
    form.faculty.choices = [(f.id, f.name) for f in Faculty.query.all()]
    form.department.choices = []
    form.course.choices = []

    if form.validate_on_submit():
        image = form.image.data
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)
        image_url = f"uploads/{filename}"

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

@routes.route("/get_departments/<int:faculty_id>")
def get_departments(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    departments_list = [{"id": d.id, "name": d.name} for d in departments]
    return jsonify(departments_list)

@routes.route("/get_courses/<int:department_id>")
def get_courses(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    courses_list = [{"id": c.id, "name": c.name} for c in courses]
    return jsonify(courses_list)

@routes.route("/admin/delete_book/<int:book_id>", methods=["POST"])
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

@routes.route("/admin/edit_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("index"))

    book = Book.query.get_or_404(book_id)
    form = AddBookForm(obj=book)

    form.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

    if form.validate_on_submit():
        try:
            if form.image.data:
                image = form.image.data
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(image_path)
                book.image_url = f"uploads/{filename}"

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

@routes.route("/select_faculty", methods=["GET"])
@login_required
def select_faculty():
    faculties = Faculty.query.all()
    return render_template("select_faculty.html", faculties=faculties)

@routes.route("/select_department/<int:faculty_id>", methods=["GET"])
@login_required
def select_department(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return render_template("select_department.html", departments=departments)

@routes.route("/select_course/<int:department_id>", methods=["GET"])
@login_required
def select_course(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    return render_template("select_course.html", courses=courses, department_id=department_id)

@routes.route("/books/<int:course_id>", methods=["GET"])
@login_required
def course_books(course_id):
    course = Course.query.get_or_404(course_id)
    books = Book.query.filter_by(course_id=course_id).all()
    return render_template("course_books.html", books=books, course=course)

@routes.route("/cart", methods=["GET"])
@login_required
def cart():
    cart_items = session.get("cart", {})
    if not isinstance(cart_items, dict):
        cart_items = {}

    cleaned_cart_items = {}
    for book_id, item in cart_items.items():
        if isinstance(item, dict) and "price" in item and "quantity" in item:
            cleaned_cart_items[book_id] = {
                "title": item.get("title", "Unknown Title"),
                "author": item.get("author", "Unknown Author"),
                "price": float(item["price"]),
                "quantity": int(item["quantity"]),
                "image_url": item.get("image_url", "uploads/default_book.jpg"),
            }
        else:
            print(f"Invalid item in cart: {item}")

    total_price = calculate_total_price(cleaned_cart_items)
    session["cart"] = cleaned_cart_items
    return render_template("cart.html", cart_items=cleaned_cart_items, total_price=total_price)

@routes.route("/add_to_cart/<int:book_id>", methods=["POST"])
@login_required
def add_to_cart(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        cart = session.get("cart", {})
        if not isinstance(cart, dict):
            cart = {}

        if str(book_id) in cart:
            if isinstance(cart[str(book_id)], dict):
                cart[str(book_id)]["quantity"] += 1
            else:
                cart[str(book_id)] = {
                    "title": book.title,
                    "author": book.author,
                    "price": float(book.price),
                    "quantity": 1,
                    "image_url": book.image_url,
                }
        else:
            cart[str(book_id)] = {
                "title": book.title,
                "author": book.author,
                "price": float(book.price),
                "quantity": 1,
                "image_url": book.image_url,
            }

        session["cart"] = cart
        flash(f"{book.title} has been added to your cart!", "success")
    except Exception as e:
        print(f"Error adding to cart: {e}")
        flash("An error occurred while adding the book to your cart. Please try again.", "error")

    return redirect(url_for("course_books", course_id=book.course_id))

@routes.route("/remove_from_cart/<int:book_id>", methods=["POST"])
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

@routes.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_items = session.get("cart", {})
    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("course_books"))

    total_price = sum(item["price"] * item["quantity"] for item in cart_items.values())

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        client_secret = intent.client_secret
    except stripe.error.StripeError as e:
        flash("Failed to create payment intent. Please try again.", "error")
        return redirect(url_for("course_books"))

    return render_template("checkout.html", cart_items=cart_items, total_price=total_price, client_secret=client_secret, stripe_publishable_key=stripe_publishable_key)

@routes.route("/payment_intent_confirm", methods=["POST"])
@login_required
def payment_intent_confirm():
    try:
        payment_intent_id = request.form["payment_intent_id"]
        payment_method_id = request.form["payment_method_id"]

        intent = stripe.PaymentIntent.confirm(payment_intent_id, payment_method=payment_method_id)

        if intent.status == "succeeded":
            flash("Payment Successful! Thank you for your purchase.", "success")
            session.pop("cart", None)
            return redirect(url_for("order_success"))
        else:
            flash("Payment failed. Please try again.", "error")
            return redirect(url_for("checkout"))

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("checkout"))

@routes.route("/payment-success")
def payment_success():
    payment_intent_id = request.args.get("payment_intent")
    if payment_intent_id:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            amount = payment_intent.amount_received / 100
            session.pop("cart", None)
            return redirect(url_for("success_page", payment_intent_id=payment_intent.id, amount=amount))
        except stripe.error.StripeError as e:
            return render_template("success.html", error=str(e))
    else:
        return render_template("success.html", error="Payment details not found.")

@routes.route("/success")
def success_page():
    payment_intent_id = request.args.get("payment_intent_id")
    amount = request.args.get("amount")
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return render_template("success.html", payment_intent=payment_intent, amount=amount)
    except stripe.error.StripeError as e:
        return render_template("success.html", error=str(e))

@routes.route("/delivery_address", methods=["GET", "POST"])
@login_required
def delivery_address():
    form = DeliveryAddressForm()
    if form.validate_on_submit():
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
        session.pop("cart", None)
        send_confirmation_email(new_order)
        flash("Order confirmed! A confirmation email has been sent.", "success")
        return redirect(url_for("success_page"))

    return render_template("delivery_address.html", form=form)

@routes.route("/payment")
def payment():
    return render_template("payment.html")

@routes.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    try:
        cart_items = session.get("cart", {})
        total_price = calculate_total_price(cart_items)
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        return str(e), 400

@routes.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    return render_template("contact.html")
