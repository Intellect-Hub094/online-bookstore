from flask import Blueprint, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Cart, Book, db

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/")
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render_template("cart/view.html", cart_items=cart_items, total=total)


@cart_bp.route("/add/<int:book_id>")
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    cart_item = Cart.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=current_user.id, book_id=book_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash("Book added to cart!", "success")
    return redirect(url_for("books.view_book", book_id=book_id))


@cart_bp.route("/delete/<int:book_id>")
@login_required
def delete_from_cart(book_id):
    cart_item = Cart.query.filter_by(
        user_id=current_user.id, book_id=book_id
    ).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash("Item deleted from cart!", "success")
    return redirect(url_for("cart.view_cart"))
