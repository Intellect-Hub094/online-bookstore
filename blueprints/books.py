import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Book, db, Wishlist
from forms.books import BookForm

books_bp = Blueprint("books", __name__)


@books_bp.route("/")
def list_books():
    search_query = request.args.get("search", "")
    category = request.args.get("category", "")
    sort_by = request.args.get("sort_by", "")
    faculty = request.args.get("faculty", "")

    books = Book.query

    if search_query:
        books = books.filter(Book.title.ilike(f"%{search_query}%"))
    if category:
        books = books.filter(Book.category == category)
    if faculty:
        books = books.filter(Book.faculty == faculty)

    if sort_by == "price_asc":
        books = books.order_by(Book.price.asc())
    elif sort_by == "price_desc":
        books = books.order_by(Book.price.desc())
    elif sort_by == "newest":
        books = books.order_by(Book.id.desc())

    books = books.all()

    return render_template("books/list.html", books=books)


@books_bp.route("/<int:book_id>")
def view_book(book_id):
    book = Book.query.get_or_404(book_id)
    wishlist_book_ids = []
    if current_user.is_authenticated:
        wishlist_items = Wishlist.query.filter_by(customer_id=current_user.customer.id).all()
        wishlist_book_ids = [item.book_id for item in wishlist_items]
    return render_template("books/view.html", book=book, wishlist_book_ids=wishlist_book_ids)


@books_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            isbn=form.isbn.data,
            price=form.price.data,
            stock=form.stock.data,
            description=form.description.data,
        )
        if form.cover_image.data:
            filename = secure_filename(form.cover_image.data.filename)
            form.cover_image.data.save(os.path.join("static/uploads", filename))
            book.cover_image = filename

        db.session.add(book)
        db.session.commit()
        flash("Book created successfully!", "success")
        return redirect(url_for("books.list_books"))
    return render_template("books/create.html", form=form)
