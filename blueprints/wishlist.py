from flask import Blueprint, render_template, redirect, url_for, flash, g
from flask_login import login_required, current_user
from models import Wishlist, db, Book
from datetime import datetime

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.route("/")
@login_required
def view_wishlist():
    wishlist_items = Wishlist.query.filter_by(
        customer_id=current_user.customer.id
    ).all()
    return render_template("wishlist.html", wishlist_items=wishlist_items)


def get_wishlist_book_ids():
    """Helper function to get list of book IDs in user's wishlist"""
    if current_user.is_authenticated:
        if current_user.role == "customer" and current_user.customer:
            return [
                item.book_id
                for item in Wishlist.query.filter_by(
                    customer_id=current_user.customer.id
                ).all()
            ]
    return []


@wishlist_bp.before_app_request
def inject_wishlist_data():
    """Make wishlist data available to all templates"""
    if current_user.is_authenticated:
        g.wishlist_book_ids = get_wishlist_book_ids()
    else:
        g.wishlist_book_ids = []


@wishlist_bp.route("/add/<int:book_id>")
@login_required
def add_to_wishlist(book_id):
    existing_item = Wishlist.query.filter_by(
        customer_id=current_user.customer.id, book_id=book_id
    ).first()

    if not existing_item:
        wishlist_item = Wishlist(
            customer_id=current_user.customer.id,
            book_id=book_id,
            added_date=datetime.now(),
        )
        db.session.add(wishlist_item)
        db.session.commit()
        flash("Book added to wishlist!", "success")
    else:
        flash("Book is already in your wishlist!", "info")

    return redirect(url_for("books.view_book", book_id=book_id))


@wishlist_bp.route("/remove/<int:book_id>")
@login_required
def remove_from_wishlist(book_id):
    Wishlist.query.filter_by(
        customer_id=current_user.customer.id, book_id=book_id
    ).delete()
    db.session.commit()
    flash("Book removed from wishlist!", "success")
    return redirect(url_for("wishlist.view_wishlist"))
