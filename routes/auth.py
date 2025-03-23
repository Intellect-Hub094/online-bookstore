# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from forms.login_form import LoginForm  # Corrected import path
from forms.registration_form import RegistrationForm  # Corrected import path
from models.user import User  # Corrected import path
from extensions import db, login_manager  # Corrected import path

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("user.home"))
        else:
            flash("Invalid email or password.", "error")
    return render_template("login.html", form=form)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            profile_id=form.profile_id.data,
            email=form.email.data,
            password=form.password.data,
            full_name=form.full_name.data,
            phone_number=form.phone_number.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            marital_status=form.marital_status.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))