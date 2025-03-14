from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
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


# Category model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    books = db.relationship('Book', backref='category', lazy=True)


# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)


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


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')


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
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/categories')
@login_required
def categories():
    all_categories = Category.query.all()
    return render_template('categories.html', categories=all_categories)


@app.route('/category/<int:category_id>')
@login_required
def category_books(category_id):
    category = Category.query.get_or_404(category_id)
    books = Book.query.filter_by(category_id=category_id).all()
    return render_template('category_books.html', category=category, books=books)


@app.route('/books')
@login_required
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)


@app.route('/cart', methods=['GET'])
@login_required
def cart():
    cart_items = session.get('cart', {})
    total_price = 0
    for book_id, quantity in cart_items.items():
        book = Book.query.get(book_id)
        if book:
            total_price += quantity * 10  # Assuming each book costs R10
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    cart = session.get('cart', {})
    cart[str(book_id)] = cart.get(str(book_id), 0) + 1
    session['cart'] = cart
    flash(f'{book.title} has been added to your cart!', 'success')
    return redirect(url_for('category_books', category_id=book.category_id))


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

    total_price = sum(quantity * 10 for book_id, quantity in cart_items.items())  # Assuming each book costs R10

    if request.method == 'POST':
        session['cart'] = {}  # Clear the cart after checkout
        flash('Checkout successful! Thank you for your purchase.', 'success')
        return redirect(url_for('home'))

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Process the form data (e.g., save to database or send email)
        flash('Your message has been sent!', 'success')
        return redirect(url_for('home'))
    return render_template('contact.html', form=form)


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
   # message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Category.query.first():
            category1 = Category(name="Fiction")
            category2 = Category(name="Non-Fiction")
            db.session.add_all([category1, category2])
            db.session.commit()

        if not Book.query.first():
            book1 = Book(title="Fiction Book 1", author="Author 1", category_id=1)
            book2 = Book(title="Non-Fiction Book 1", author="Author 2", category_id=2)
            db.session.add_all([book1, book2])
            db.session.commit()

    app.run(debug=True)