# routes/book.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from forms.book_form import AddBookForm, EditBookForm
from models.book import Book
from models.course import Course
from extensions import db

book_bp = Blueprint("book", __name__)

@book_bp.route("/books")
@login_required
def books():
    books = Book.query.all()
    return render_template("books.html", books=books)

@book_bp.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("user.home"))

    form = AddBookForm()
    form.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            price=form.price.data,
            course_id=form.course_id.data,
            image_url="uploads/default.jpg",  # Save the uploaded file path here
        )
        db.session.add(book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for("book.books"))

    return render_template("add_book.html", form=form)

@book_bp.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("user.home"))

    book = Book.query.get_or_404(book_id)
    form = EditBookForm(obj=book)
    form.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.price = form.price.data
        book.course_id = form.course_id.data
        db.session.commit()
        flash("Book updated successfully!", "success")
        return redirect(url_for("book.books"))

    return render_template("edit_book.html", form=form, book=book)

@book_bp.route("/delete_book/<int:book_id>", methods=["POST"])
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("user.home"))

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "success")
    return redirect(url_for("book.books"))