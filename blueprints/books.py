from datetime import datetime
import os
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
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
        wishlist_items = Wishlist.query.filter_by(
            customer_id=current_user.customer.id
        ).all()
        wishlist_book_ids = [item.book_id for item in wishlist_items]
    return render_template(
        "books/view.html", book=book, wishlist_book_ids=wishlist_book_ids
    )


@books_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_book():
    if not current_user.role == "admin":
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for("main.index"))

    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            isbn=form.isbn.data.strip(),
            price=form.price.data,
            stock=form.stock.data,
            description=form.description.data,
            category=form.category.data,
            faculty=form.faculty.data,
            created_at=datetime.now(),
        )

        # Check for duplicate ISBN
        if Book.query.filter_by(isbn=book.isbn).first():
            flash("A book with this ISBN already exists.", "danger")
            return render_template("books/create.html", form=form)

        book.id = Book.query.count() + 1

        db.session.add(book)

        if form.cover_image.data:
            try:
                filename = secure_filename(f"{book.id}.jpg")
                filepath = os.path.join(
                    current_app.config["BOOKS_UPLOAD_FOLDER"], filename
                )
                form.cover_image.data.save(filepath)
                book.cover_image = filename
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Error saving cover image: {str(e)}")
                flash("Book created but cover image could not be saved.", "error")
                return redirect(url_for("books.create_book"))

        flash("Book created successfully!", "success")
        return redirect(url_for("books.list_books"))

    return render_template("books/create.html", form=form)


@books_bp.route("/admin/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
def admin_edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.isbn = form.isbn.data
        book.price = form.price.data
        book.stock = form.stock.data
        book.description = form.description.data
        book.category = form.category.data
        book.faculty = form.faculty.data
        book.updated_at = datetime.now()
        db.session.commit()

        if form.cover_image.data:
            filename = secure_filename(f"{book.id}.jpg")
            form.cover_image.data.save(
                os.path.join(current_app.config["BOOKS_UPLOAD_FOLDER"], filename)
            )
            book.cover_image = filename
            db.session.commit()

        flash("Book updated successfully!", "success")
        return redirect(url_for("books.list_books"))
    return render_template("books/edit.html", form=form, book=book)


@books_bp.route("/admin/delete/<int:book_id>", methods=["GET", "DELETE"])
@login_required
def admin_delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "success")
    return redirect(url_for("books.list_books"))
