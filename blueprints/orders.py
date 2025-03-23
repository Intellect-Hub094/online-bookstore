from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Order

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/")
# @login_required
def list_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("orders/list.html", orders=orders)


@orders_bp.route("/<int:order_id>")
# @login_required
def view_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("orders/view.html", order=order)
