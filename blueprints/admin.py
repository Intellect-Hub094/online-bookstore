from flask import Blueprint, render_template
from flask_login import login_required
from models import Book, Order, Customer, User
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def admin_index():
    # Get dashboard statistics
    total_books = Book.query.count()
    total_orders = Order.query.count()
    total_customers = Customer.query.count()
    low_stock_books = Book.get_low_stock_books()
    low_stock_count = len(low_stock_books)

    # Get recent orders (last 7 days)
    recent_orders = (
        Order.query.filter(Order.order_date >= datetime.now() - timedelta(days=7))
        .order_by(Order.order_date.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "admin/index.html",
        total_books=total_books,
        total_orders=total_orders,
        total_customers=total_customers,
        low_stock_count=low_stock_count,
        low_stock_books=low_stock_books,
        recent_orders=recent_orders,
    )
