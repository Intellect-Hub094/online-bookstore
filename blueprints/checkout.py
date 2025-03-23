from datetime import datetime

from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Cart, db, Order, Purchase

checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/")
# @login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("cart.view_cart"))

    total = sum(item.book.price * item.quantity for item in cart_items)

    order = Order(
        user_id=current_user.id,
        total_amount=total,
        status="pending",
        order_date=datetime.now(),
    )
    db.session.add(order)

    for item in cart_items:
        purchase = Purchase(
            order_id=order.id,
            book_id=item.book_id,
            quantity=item.quantity,
            price=item.book.price,
        )
        db.session.add(purchase)

        # Update book stock
        book = item.book
        book.stock -= item.quantity

        # Clear cart
        db.session.delete(item)

    db.session.commit()
    flash("Order placed successfully!", "success")
    return redirect(url_for("orders.view_order", order_id=order.id))
