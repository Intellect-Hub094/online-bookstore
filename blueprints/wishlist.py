from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Wishlist

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.route("/<int:wishlist_id>")
# @login_required
def view_order(wishlist_id):
    order = Wishlist.query.filter_by(
        id=wishlist_id, user_id=current_user.id
    ).first_or_404()
    return render_template("wishlist.html", order=order)
