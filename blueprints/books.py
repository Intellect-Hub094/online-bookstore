from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Book, db
from forms.books import BookForm
import os

books_bp = Blueprint("books", __name__)


@books_bp.route("/")
def list_books():
    books = Book.query.all()
    return render_template("books/list.html", books=books)


@books_bp.route("/<int:book_id>")
def view_book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template("books/view.html", book=book)


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
