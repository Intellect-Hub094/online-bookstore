from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')  # Ensure SECRET_KEY comes from environment
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:syabonga%40030715105507@localhost/online_bookstore_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Flask-Login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

# Feedback model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    received = db.Column(db.Boolean, default=False, nullable=False)
    comments = db.Column(db.String(500), nullable=True)

# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    order_code = db.Column(db.String(50), unique=True, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)

# Faculty model
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    departments = db.relationship('Department', backref='faculty', lazy=True)

# Department model
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    courses = db.relationship('Course', backref='department', lazy=True)

# Course model
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
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    feedbacks = db.relationship('Feedback', backref='book', lazy=True)

# Registration Form
class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if not email.data.endswith('@dut4life.ac.za'):
            raise ValidationError('Only DUT4Life emails are allowed.')

# Login Form
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Payment Method Selection Form
class PaymentMethodForm(FlaskForm):
    payment_method = SelectField('Select Payment Method', 
                                  choices=[('debit_card', 'Debit Card'), 
                                           ('paypal', 'PayPal'), 
                                           ('stripe', 'Stripe')], 
                                  validators=[DataRequired()])
    submit = SubmitField('Proceed')

# Delivery Address Form
class DeliveryAddressForm(FlaskForm):
    address = StringField('Delivery Address', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Confirm and Pay')

# Feedback Form
class FeedbackForm(FlaskForm):
    book_id = SelectField('Select Book', coerce=int, validators=[DataRequired()])
    received = SelectField('Did you receive the book?', 
                           choices=[('yes', 'Yes'), ('no', 'No')], 
                           validators=[DataRequired()])
    comments = StringField('Comments (if any)')
    submit = SubmitField('Submit Feedback')

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
                'title': book.title,
                'author': book.author,
                'price': book.price,
                'quantity': cart_items[book_id]
            }
    return books_info

def process_payment(payment_method, bank_details):
    return True  # Simulated payment processing logic, assume payment is successful

def generate_order_code():
    return 'ORD-' + str(random.randint(1000, 9999))  # Generate a random Order Code

def send_confirmation_email(recipient_email, order_code):
    # Gmail SMTP Configuration
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # For Gmail
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = 'Order Confirmation'
        body = f"Your order has been confirmed. Your order code is {order_code}."
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(EMAIL_ADDRESS, recipient_email, message)
        server.quit()
    except Exception as e:
        print("Failed to send the email:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home' if not user.is_admin else 'admin_dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'error')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    form.book_id.choices = [(book.id, book.title) for book in Book.query.all()]

    if form.validate_on_submit():
        new_feedback = Feedback(
            user_id=current_user.id,
            book_id=form.book_id.data,
            received=form.received.data == 'yes',
            comments=form.comments.data
        )
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('feedback.html', form=form)

@app.route('/my_feedback')
@login_required
def my_feedback():
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).all()
    return render_template('my_feedback.html', feedbacks=feedbacks)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    users = User.query.all()
    books = Book.query.all()
    feedbacks = Feedback.query.all()
    orders = Order.query.all()  # Fetching orders for admin
    return render_template('admin_dashboard.html', users=users, books=books, feedbacks=feedbacks, orders=orders)

@app.route('/admin/manage_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    form = RegistrationForm(obj=user)

    if form.validate_on_submit():
        user.email = form.email.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', form=form, user=user)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Book')

@app.route('/admin/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))

    form = AddBookForm()
    form.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            price=form.price.data,
            course_id=form.course_id.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_book.html', form=form)

@app.route('/admin/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    book = Book.query.get_or_404(book_id)
    form = AddBookForm(obj=book)
    form.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.price = form.price.data
        book.course_id = form.course_id.data
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_book.html', form=form, book=book)

@app.route('/admin/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/select_faculty', methods=['GET'])
@login_required
def select_faculty():
    faculties = Faculty.query.all()
    return render_template('select_faculty.html', faculties=faculties)

@app.route('/select_department/<int:faculty_id>', methods=['GET'])
@login_required
def select_department(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return render_template('select_department.html', departments=departments)

@app.route('/select_course/<int:department_id>', methods=['GET'])
@login_required
def select_course(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    return render_template('select_course.html', courses=courses, department_id=department_id)

@app.route('/books/<int:course_id>', methods=['GET'])
@login_required
def course_books(course_id):
    course = Course.query.get_or_404(course_id)
    books = Book.query.filter_by(course_id=course_id).all()
    return render_template('course_books.html', books=books, course=course)

@app.route('/cart', methods=['GET'])
@login_required
def cart():
    cart_items = session.get('cart', {})
    total_price = calculate_total_price(cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    cart = session.get('cart', {})
    cart[str(book_id)] = cart.get(str(book_id), 0) + 1
    session['cart'] = cart
    flash(f'{book.title} has been added to your cart!', 'success')
    return redirect(url_for('course_books', course_id=book.course_id))

@app.route('/remove_from_cart/<int:book_id>', methods=['POST'])
@login_required
def remove_from_cart(book_id):
    cart = session.get('cart', {})
    if str(book_id) in cart:
        del cart[str(book_id)]
        session['cart'] = cart
        flash('Book removed from the cart!', 'success')
    else:
        flash('Book not found in the cart!', 'error')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))

    total_price = calculate_total_price(cart_items)
    books_info = get_books_info(cart_items)

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, books_info=books_info)

@app.route('/payment_method', methods=['GET', 'POST'])
@login_required
def payment_method():
    form = PaymentMethodForm()
    if form.validate_on_submit():
        session['payment_method'] = form.payment_method.data
        return redirect(url_for('delivery_address'))
    return render_template('payment_method.html', form=form)

@app.route('/delivery_address', methods=['GET', 'POST'])
@login_required
def delivery_address():
    form = DeliveryAddressForm()
    if form.validate_on_submit():
        address = form.address.data
        email = form.email.data
        order_code = generate_order_code()  # Generate unique order code
        payment_method = session.get('payment_method')

        # Save the order to the database
        new_order = Order(user_id=current_user.id, address=address, email=email, order_code=order_code, payment_method=payment_method)
        db.session.add(new_order)
        db.session.commit()

        # Process the payment (simulation)
        payment_success = process_payment(payment_method, form.data)
        if payment_success:
            send_confirmation_email(email, order_code)  # Send email notification
            flash('Payment successful! Your order has been confirmed.', 'success')
            return redirect(url_for('success_page'))
        else:
            flash('Payment failed. Please try again.', 'error')

    return render_template('delivery_address.html', form=form)

@app.route('/success')
@login_required
def success_page():
    return render_template('success.html', message='Your order has been successfully placed!')

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    return render_template('contact.html')  # Update if you implement the contact form

# Create tables if they don't exist (initial setup)
if __name__ == '__main__':
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
            book1 = Book(title="Python Programming", author="Author A", course_id=course1.id, price=150.0, image_url='path/to/image1.jpg')
            book2 = Book(title="Engineering Mechanics", author="Author B", course_id=course2.id, price=200.0, image_url='path/to/image2.jpg')
            db.session.add_all([book1, book2])
            db.session.commit()

    app.run(debug=True)