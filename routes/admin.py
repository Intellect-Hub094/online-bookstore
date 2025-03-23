# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from forms.book_form import AddBookForm, EditBookForm
from forms.edit_user_form import EditUserForm
from models.user import User
from models.book import Book
from extensions import db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("user.home"))
    users = User.query.all()
    books = Book.query.all()
    return render_template("admin_dashboard.html", users=users, books=books)

@admin_bp.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("user.home"))
    form = AddBookForm()
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
        return redirect(url_for("admin.dashboard"))
    return render_template("add_book.html", form=form)