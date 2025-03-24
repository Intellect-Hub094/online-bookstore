from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Order, db

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/")
@login_required
def list_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("orders/list.html", orders=orders)


@orders_bp.route("/<int:order_id>")
@login_required
def view_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("orders/view.html", order=order)


@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if order.status != "cancelled":
        order.status = "cancelled"
        order.cancellation_reason = request.form.get("reason")
        db.session.commit()
        flash("Order has been cancelled.", "success")
    else:
        flash("Order is already cancelled.", "warning")
    return redirect(url_for("orders.view_order", order_id=order.id))
