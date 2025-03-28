import hashlib
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from flask import (
    Blueprint,
    redirect,
    url_for,
    flash,
    render_template,
    request,
    current_app,
)
from flask_login import login_required, current_user
from models import Cart, db, Order, Purchase, Customer
from payfast import create_payfast_payment

checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/")
@login_required
def checkout():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    cart_items = Cart.query.filter_by(customer_id=customer.id).all()
    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("cart.view_cart"))
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render_template("checkout.html", cart_items=cart_items, total=total)


@checkout_bp.route("/process", methods=["POST"])
@login_required
def process_checkout():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    cart_items = Cart.query.filter_by(customer_id=customer.id).all()
    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("cart.view_cart"))

    total = sum(item.book.price * item.quantity for item in cart_items)
    order = Order(
        user_id=current_user.id,
        customer_id=customer.id,
        total_amount=total,
        status="pending",
        order_date=datetime.now(),
        shipping_address=customer.address,
    )
    db.session.add(order)
    db.session.commit()

    payfast_url = create_payfast_payment(order, current_user)
    if not payfast_url:
        flash("Payment gateway configuration error.", "error")
        return redirect(url_for("checkout.checkout"))
    return redirect(payfast_url)


@checkout_bp.route("/return")
@login_required
def payfast_return():
    order_id = request.args.get("order_id")
    order = Order.query.get(order_id)
    order.status = "paid"

    customer = Customer.query.filter_by(user_id=order.user_id).first()
    cart_items = Cart.query.filter_by(customer_id=customer.id).all()

    for item in cart_items:
        purchase = Purchase(
            order_id=order.id,
            book_id=item.book_id,
            quantity=item.quantity,
            price=item.book.price,
        )

        db.session.add(purchase)

        book = item.book
        book.stock -= item.quantity

        db.session.delete(item)
    db.session.commit()
    flash("Payment successful!", "success")
    return redirect(url_for("orders.view_order", order_id=order.id))


@checkout_bp.route("/cancel")
@login_required
def payfast_cancel():
    flash("Payment was cancelled.", "warning")
    return redirect(url_for("cart.view_cart"))


@checkout_bp.route("/notify", methods=["POST"])
def payfast_notify():
    data = request.form.to_dict()
    signature = hashlib.md5(urlencode(data, quote_via=quote_plus).encode()).hexdigest()
    if signature == data.get("signature"):
        order_id = int(data.get("m_payment_id"))
        order = Order.query.get(order_id)
        if order and data.get("payment_status") == "COMPLETE":
            order.status = "paid"
            customer = Customer.query.filter_by(user_id=order.user_id).first()
            cart_items = Cart.query.filter_by(customer_id=customer.id).all()
            for item in cart_items:
                purchase = Purchase(
                    order_id=order.id,
                    book_id=item.book_id,
                    quantity=item.quantity,
                    price=item.book.price,
                )
                db.session.add(purchase)
                book = item.book
                book.stock -= item.quantity
                db.session.delete(item)
            db.session.commit()
    return "", 200
