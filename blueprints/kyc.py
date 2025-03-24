import os
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import current_user
from forms.kyc.onboarding.driver_form import DriverOnboardingForm
from forms.kyc.onboarding.customer_form import CustomerOnboardingForm
from models import db, User, Driver, Customer

kyc_bp = Blueprint("kyc", __name__)


def save_license_image(file):
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "licenses")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    return os.path.join("uploads", "licenses", filename)


@kyc_bp.route("/onboarding/driver", methods=["GET", "POST"])
def driver_onboarding():
    form = DriverOnboardingForm()
    if form.validate_on_submit():
        # Handle license image upload
        license_image_path = save_license_image(form.license_image.data)

        user = User.query.filter_by(email=current_user.email).first()

        driver = Driver(
            user=user,
            phone=form.phone.data,
            license_number=form.license_number.data,
            vehicle_info=form.vehicle_info.data,
            license_image=license_image_path,
        )

        try:
            db.session.add(user)
            db.session.add(driver)
            db.session.commit()
            flash("Driver registration successful!", "success")
            return redirect(url_for("orders.list_orders"))
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please try again.", "danger")
            return redirect(url_for("kyc.driver_onboarding"))

    return render_template("kyc/onboarding/driver.html", form=form)


@kyc_bp.route("/onboarding/customer", methods=["GET", "POST"])
def customer_onboarding():
    form = CustomerOnboardingForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        customer = Customer(
            user=user,
            phone=form.phone.data,
            address=form.address.data,
            student_id=form.student_id.data,
        )

        try:
            db.session.add(user)
            db.session.add(customer)
            db.session.commit()
            flash("Customer registration successful!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please try again.", "danger")
            return redirect(url_for("kyc.customer_onboarding"))

    return render_template("kyc/onboarding/customer.html", form=form)
