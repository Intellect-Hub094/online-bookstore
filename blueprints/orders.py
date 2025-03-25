from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Book, Order, Purchase, db

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/")
@login_required
def list_orders():
    if current_user.role in ["admin", "driver"]:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("orders/list.html", orders=orders)


@orders_bp.route("/<int:order_id>")
@login_required
def view_order(order_id):
    if current_user.role in ["admin", "driver"]:
        order = Order.query.get_or_404(order_id)
        purchases = Purchase.query.filter_by(order_id=order.id).all()
        book_ids = [purchase.book_id for purchase in purchases]
        books = Book.query.filter(Book.id.in_(book_ids)).all()
        purchases_books = dict(zip(book_ids, books))
    else:
        order = Order.query.filter_by(
            id=order_id, user_id=current_user.id
        ).first_or_404()
        purchases = Purchase.query.filter_by(order_id=order.id).all()
        book_ids = [purchase.book_id for purchase in purchases]
        books = Book.query.filter(Book.id.in_(book_ids)).all()
        purchases_books = dict(zip(book_ids, books))
    return render_template("orders/view.html", order=order, purchases=purchases, purchases_books=purchases_books)


@orders_bp.route("/<int:order_id>/edit", methods=["GET", "POST"])
@login_required
def edit_order(order_id):
    if current_user.role not in ["admin", "driver"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("orders.list_orders"))

    order = Order.query.get_or_404(order_id)
    if request.method == "POST":
        new_status = request.form.get("status")
        # Only allow specific status transitions for drivers
        if current_user.role == "driver" and new_status not in ["shipped", "delivered"]:
            flash("You can only update orders to shipped or delivered status", "error")
            return redirect(url_for("orders.edit_order", order_id=order.id))
        
        order.status = new_status
        db.session.commit()
        flash("Order status updated successfully", "success")
        return redirect(url_for("orders.view_order", order_id=order.id))

    return render_template("orders/edit.html", order=order)


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
