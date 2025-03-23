# routes/transaction.py
from flask import Blueprint, render_template, redirect, session, url_for, flash, request
from flask_login import login_required
import stripe
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_items = session.get("cart", {})
    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("book.books"))
    total_price = sum(item["price"] * item["quantity"] for item in cart_items.values())
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Convert amount to cents
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        client_secret = intent.client_secret
    except stripe.error.StripeError as e:
        flash("Failed to create payment intent. Please try again.", "error")
        return redirect(url_for("book.books"))
    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total_price=total_price,
        client_secret=client_secret,
        stripe_publishable_key=Config.STRIPE_PUBLIC_KEY,
    )

@transaction_bp.route("/payment_intent_confirm", methods=["POST"])
@login_required
def payment_intent_confirm():
    try:
        payment_intent_id = request.form["payment_intent_id"]
        payment_method_id = request.form["payment_method_id"]
        intent = stripe.PaymentIntent.confirm(
            payment_intent_id, payment_method=payment_method_id
        )
        if intent.status == "succeeded":
            flash("Payment Successful! Thank you for your purchase.", "success")
            session.pop("cart", None)  # Clear the cart after payment success
            return redirect(url_for("transaction.order_success"))
        else:
            flash("Payment failed. Please try again.", "error")
            return redirect(url_for("transaction.checkout"))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("transaction.checkout"))