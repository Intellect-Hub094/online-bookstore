# routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from forms.profile_form import ProfileForm
from forms.feedback_form import FeedbackForm
from forms.delivery_form import DeliveryAddressForm
from models.user import User
from models.feedback import Feedback
from models.order import Order
from extensions import db

user_bp = Blueprint("user", __name__)

@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.full_name = form.full_name.data
        current_user.phone_number = form.phone_number.data
        current_user.address = form.address.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.marital_status = form.marital_status.data
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("user.profile"))
    return render_template("profile.html", form=form)

@user_bp.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            user_id=current_user.id,
            book_id=form.book_id.data,
            received=form.received.data == "yes",
            comments=form.comments.data,
        )
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback submitted successfully!", "success")
        return redirect(url_for("user.home"))
    return render_template("feedback.html", form=form)

@user_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    form = DeliveryAddressForm()
    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            address=form.address.data,
            email=form.email.data,
            order_code="ORD-1234",  # Generate a unique order code
            payment_method="Stripe",
        )
        db.session.add(order)
        db.session.commit()
        flash("Order placed successfully!", "success")
        return redirect(url_for("user.order_success"))
    return render_template("checkout.html", form=form)