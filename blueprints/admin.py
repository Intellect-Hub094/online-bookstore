from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Book, Order, Customer, User, Driver
from datetime import datetime, timedelta
from app import db
from forms.auth.login_form import LoginForm
from forms.kyc.onboarding.customer_form import CustomerOnboardingForm
from forms.kyc.onboarding.driver_form import DriverOnboardingForm

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def admin_index():
    # Get dashboard statistics
    total_books = Book.query.count()
    total_orders = Order.query.count()
    total_customers = Customer.query.count()
    low_stock_books = Book.get_low_stock_books()
    low_stock_count = len(low_stock_books)

    # Get recent orders (last 7 days)
    recent_orders = (
        Order.query.filter(Order.order_date >= datetime.now() - timedelta(days=7))
        .order_by(Order.order_date.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "admin/index.html",
        total_books=total_books,
        total_orders=total_orders,
        total_customers=total_customers,
        low_stock_count=low_stock_count,
        low_stock_books=low_stock_books,
        recent_orders=recent_orders,
    )


@admin_bp.route("/users")
@login_required
def list_users():
    users = User.query.all()
    return render_template("admin/users/list.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
def create_user():
    role = request.args.get('role', 'customer')
    
    if role == 'customer':
        form = CustomerOnboardingForm()
    elif role == 'driver':
        form = DriverOnboardingForm()
    else:
        form = LoginForm()
    
    if form.validate_on_submit():
        user = User(
            email=form.email.data if hasattr(form, 'email') else '',
            role=role
        )
        user.set_password(form.password.data if hasattr(form, 'password') else 'default123')
        db.session.add(user)
        
        if role == 'customer':
            customer = Customer(
                user=user,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                address=form.address.data,
                student_id=form.student_id.data
            )
            db.session.add(customer)
            
        elif role == 'driver':
            driver = Driver(
                user=user,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                license_number=form.license_number.data,
                vehicle_info=form.vehicle_info.data,
                license_image=form.license_image.data.filename
            )
            db.session.add(driver)
            
        db.session.commit()
        flash(f"New {role} created successfully!", "success")
        return redirect(url_for("admin.list_users"))
        
    return render_template("admin/users/create.html", form=form, role=role)


@admin_bp.route("/users/view/<int:user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("admin/users/view.html", user=user)


@admin_bp.route("/users/dashboard")
@login_required
def users_dashboard():
    total_users = User.query.count()
    customer_count = User.query.filter_by(role='customer').count()
    driver_count = User.query.filter_by(role='driver').count()
    admin_count = User.query.filter_by(role='admin').count()
    
    # Get recent user registrations
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    return render_template(
        "admin/users/index.html",
        total_users=total_users,
        customer_count=customer_count,
        driver_count=driver_count,
        admin_count=admin_count,
        recent_users=recent_users
    )
