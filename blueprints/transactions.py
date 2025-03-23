from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Transaction

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/")
# @login_required
def list_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template("transactions/list.html", transactions=transactions)


@transactions_bp.route("/<int:transaction_id>")
# @login_required
def view_transaction(transaction_id):
    transaction = Transaction.query.filter_by(
        id=transaction_id, user_id=current_user.id
    ).first_or_404()
    return render_template("transactions/view.html", transaction=transaction)
