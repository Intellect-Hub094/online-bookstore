from datetime import datetime
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Book, db, Wishlist
from forms.books import BookForm
from functools import wraps

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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Access denied.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function

@books_bp.route("/a/create/new", methods=["GET", "POST"])
@login_required
@admin_required
def admin_create_book():
    form = BookForm()
    if request.method == "POST":
        cover_image = request.files.get("cover")
        filename = None
        if cover_image:
            filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        
        book = Book(
            title=form.title.data,
            author=form.author.data,
            isbn=form.isbn.data,
            price=float(form.price.data),
            stock=int(form.stock.data),
            description=form.description.data,
            category=form.category.data,
            faculty=form.faculty.data,
            cover_image=filename,
            created_at=datetime.now()
        )
        db.session.add(book)
        db.session.commit()
        flash("Book created successfully!", "success")
        return redirect(url_for("books.admin_list_books"))
    return render_template("books/create.html", form=form)

@books_bp.route("/a/list")
@login_required
@admin_required
def admin_list_books():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template("books/admin_list.html", books=books)

@books_bp.route("/a/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        book.title = request.form["title"]
        book.author = request.form["author"]
        book.isbn = request.form["isbn"]
        book.price = float(request.form["price"])
        book.stock = int(request.form["stock"])
        book.description = request.form["description"]
        book.category = request.form["category"]
        book.faculty = request.form["faculty"]

        cover_image = request.files.get("cover")
        if cover_image:
            if book.cover_image:
                old_image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], book.cover_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            book.cover_image = filename

        db.session.commit()
        flash("Book updated successfully!", "success")
        return redirect(url_for("books.admin_list_books"))
    return render_template("books/edit.html", book=book)

@books_bp.route("/a/delete/<int:book_id>")
@login_required
@admin_required
def admin_delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.cover_image:
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], book.cover_image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "success")
    return redirect(url_for("books.admin_list_books"))
