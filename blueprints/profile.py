from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from forms import ProfileForm
from models import db, Order
from utils import _clear_flashes

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        if form.password.data:
            if current_user.password == generate_password_hash(form.password.data):
                pass
            else:
                current_user.password = generate_password_hash(form.password.data)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.profile"))

    orders = (
        Order.query.filter_by(customer_id=current_user.id)
        .order_by(Order.order_date.desc())
        .all()
    )
    return render_template("profile.html", form=form, orders=orders)
