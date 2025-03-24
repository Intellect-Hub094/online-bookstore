from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Transaction, Order, db
from datetime import datetime

transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route("/")
@login_required
def list_transactions():
    # Get all transactions for the current user's orders
    transactions = Transaction.query.join(Order).filter(
        Order.user_id == current_user.id
    ).all()
    return render_template("transactions/list.html", transactions=transactions)

@transactions_bp.route("/<int:transaction_id>")
@login_required
def view_transaction(transaction_id):
    # Get transaction and verify it belongs to the current user
    transaction = Transaction.query.join(Order).filter(
        Transaction.id == transaction_id,
        Order.user_id == current_user.id
    ).first_or_404()
    return render_template("transactions/view.html", transaction=transaction)

@transactions_bp.route("/process/<int:order_id>", methods=["POST"])
@login_required
def process_payment(order_id):
    order = Order.query.filter_by(
        id=order_id, 
        user_id=current_user.id
    ).first_or_404()
    
    if order.status != "pending":
        flash("This order cannot be paid for", "error")
        return redirect(url_for("orders.view_order", order_id=order_id))

    # Create transaction
    transaction = Transaction.create_transaction(
        order=order,
        payment_method=request.form.get("payment_method"),
        payment_provider=request.form.get("payment_provider")
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Here you would integrate with your payment provider
    # For now, we'll just simulate a successful payment
    return redirect(url_for("transactions.view_transaction", transaction_id=transaction.id))
