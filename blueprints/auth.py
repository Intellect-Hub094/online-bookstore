from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from forms import LoginForm, RegistrationForm, ResetPasswordForm, UpdatePasswordForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data, role=request.args.get("role")
        ).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            session["_flashes"].clear()
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        flash("Invalid email, password, or role")
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
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=request.args.get("role") or "customer",
        )
        db.session.add(user)
        db.session.commit()
        session["_flashes"].clear()
        flash("Registration successful. Please login.")
        return redirect(url_for("auth.login"))
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
            session["_flashes"].clear()
            flash("Password reset instructions have been sent to your email.")
            return redirect(url_for("auth.login"))
        flash("Email address not found")
    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/update-password", methods=["GET", "POST"])
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            session["_flashes"].clear()
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Your password has been updated.")
            return redirect(url_for("index"))
        flash("Current password is incorrect")
    return render_template("auth/update_password.html", form=form)
