from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from forms import LoginForm, RegistrationForm, ResetPasswordForm, UpdatePasswordForm
from utils import _clear_flashes

auth_bp = Blueprint("auth", __name__)


def _redirect_based_on_role():
    if current_user.role == "admin":
        return redirect(url_for("admin.admin_index"))
    if current_user.role == "driver":
        return redirect(url_for("orders.list_orders"))
    if current_user.role == "customer":
        return redirect(url_for("books.list_books"))
    return redirect(url_for("index"))


def role_based_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return _redirect_based_on_role()
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
@role_based_redirect
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            _clear_flashes()

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)

            return _redirect_based_on_role()
        else:
            flash("Invalid email or password")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@auth_bp.route("/register", methods=["GET", "POST"])
@role_based_redirect
def register():
    form = RegistrationForm()
    role = request.args.get("role") or "customer"
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        _clear_flashes()
        flash("Registration successful. Please login.")
        return redirect(url_for("auth.login", role=user.role))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}")
    return render_template("auth/register.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            _clear_flashes()
            flash("Password reset instructions have been sent to your email.")
            return redirect(url_for("auth.login"))
        flash("Email address not found")
    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/update-password", methods=["GET", "POST"])
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            _clear_flashes()
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Your password has been updated.")
            return redirect(url_for("index"))
        flash("Current password is incorrect")
    return render_template("auth/update_password.html", form=form)
