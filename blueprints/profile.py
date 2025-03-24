from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import Order, db, Customer, Driver
from forms.profile import ProfileForm

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if current_user.role == "customer" and current_user.customer:
        form.phone.data = current_user.customer.phone
        form.address.data = current_user.customer.address
        form.student_id.data = current_user.customer.student_id
    elif current_user.role == "driver" and current_user.driver:
        form.phone.data = current_user.driver.phone
        form.license_number.data = current_user.driver.license_number
        form.vehicle_info.data = current_user.driver.vehicle_info

    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.order_date.desc())
        .all()
    )

    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        if form.password.data:
            current_user.password = generate_password_hash(form.password.data)

        # Update role-specific information
        if current_user.role == "customer":
            if not current_user.customer:
                customer = Customer(user_id=current_user.id)
                db.session.add(customer)
            else:
                customer = current_user.customer
            customer.phone = form.phone.data
            customer.address = form.address.data
            customer.student_id = form.student_id.data
        elif current_user.role == "driver":
            if not current_user.driver:
                driver = Driver(user_id=current_user.id)
                db.session.add(driver)
            else:
                driver = current_user.driver
            driver.phone = form.phone.data
            driver.license_number = form.license_number.data
            driver.vehicle_info = form.vehicle_info.data
            if form.license_image.data:
                # Handle license image upload here
                pass

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.profile"))
    return render_template("profile.html", form=form, orders=orders)
