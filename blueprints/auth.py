from flask import Blueprint, render_template, redirect, url_for
from forms import LoginForm, RegistrationForm, ResetPasswordForm, UpdatePasswordForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Add login logic here
        return redirect(url_for("index"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    # Add logout logic here
    return redirect(url_for("index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Add registration logic here
        return redirect(url_for("login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Add reset password logic here
        return redirect(url_for("login"))
    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/update-password", methods=["GET", "POST"])
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        # Add update password logic here
        return redirect(url_for("index"))
    return render_template("auth/update_password.html", form=form)
