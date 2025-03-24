from flask import Blueprint, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Cart, Book, db, Customer
from forms.cart import EditCartItemForm

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/")
@login_required
def view_cart():
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    cart_items = Cart.query.filter_by(customer_id=customer.id).all()
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render_template("cart/view.html", cart_items=cart_items, total=total)

@cart_bp.route("/add/<int:book_id>")
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    cart_item = Cart.query.filter_by(customer_id=customer.id, book_id=book_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(customer_id=customer.id, book_id=book_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash("Book added to cart!", "success")
    return redirect(url_for("books.view_book", book_id=book_id))

@cart_bp.route("/delete/<int:book_id>")
@login_required
def delete_from_cart(book_id):
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    cart_item = Cart.query.filter_by(
        customer_id=customer.id, book_id=book_id
    ).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash("Item deleted from cart!", "success")
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_cart_item(book_id):
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    cart_item = Cart.query.filter_by(customer_id=customer.id, book_id=book_id).first_or_404()
    form = EditCartItemForm()

    if form.validate_on_submit():
        if form.quantity.data == 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = form.quantity.data
        db.session.commit()
        flash("Cart updated!", "success")
        return redirect(url_for("cart.view_cart"))

    form.quantity.data = cart_item.quantity
    return render_template("cart/edit.html", form=form, cart_item=cart_item)
