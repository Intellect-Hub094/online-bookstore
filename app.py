from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
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
    image_url = db.Column(db.String(250), nullable=True)  # URL for the book's image

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
    payment_method = SelectField('Select Payment Method', choices=[('credit_card', 'Credit Card'), ('bank_transfer', 'Bank Transfer')], validators=[DataRequired()])
    submit = SubmitField('Proceed')

# Bank Details Form
class BankDetailsForm(FlaskForm):
    account_number = StringField('Account Number', validators=[DataRequired()])
    routing_number = StringField('Routing Number', validators=[DataRequired()])
    submit = SubmitField('Pay')

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
    # Placeholder for actual payment processing logic
    # You can implement real payment processing here
    return True  # Return True if payment succeeds

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
            return redirect(url_for('home'))
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

# Routes for Faculty, Department, and Course Selection
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

    if request.method == 'POST':
        return redirect(url_for('payment_method'))  # Redirect to payment method selection

    total_price = calculate_total_price(cart_items)
    books_info = get_books_info(cart_items)

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, books_info=books_info)

@app.route('/payment_method', methods=['GET', 'POST'])
@login_required
def payment_method():
    form = PaymentMethodForm()
    if form.validate_on_submit():
        session['payment_method'] = form.payment_method.data
        return redirect(url_for('bank_details'))
    return render_template('payment_method.html', form=form)

@app.route('/bank_details', methods=['GET', 'POST'])
@login_required
def bank_details():
    form = BankDetailsForm()
    if form.validate_on_submit():
        payment_method = session.get('payment_method')
        if process_payment(payment_method, form.data):
            flash('Payment successful!', 'success')
            return redirect(url_for('success_page'))  # Redirect to success page
        else:
            flash('Payment failed. Please try again.', 'error')

    return render_template('bank_details.html', form=form)

@app.route('/success')
@login_required
def success_page():
    return render_template('success.html')  # Render success message page

@app.route('/delivery', methods=['GET', 'POST'])
@login_required
def delivery():
    if request.method == 'POST':
        address = request.form.get('address')
        delivery_supplier = request.form.get('supplier')
        flash('Delivery details saved!', 'success')
        return redirect(url_for('home'))

    suppliers = ['Supplier 1', 'Supplier 2']  # Example suppliers
    return render_template('delivery.html', suppliers=suppliers)

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    # Assuming you have a ContactForm defined somewhere; if not, remove or modify this section
    return render_template('contact.html')  # Update if you implement the contact form

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Sample faculties, departments, courses, and books for initial setup
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