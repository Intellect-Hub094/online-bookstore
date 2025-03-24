from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField,
    FloatField,
    IntegerField,
    TextAreaField,
    FileField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError


class BookForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Title is required"),
            Length(max=100, message="Title must be less than 100 characters"),
        ],
    )
    author = StringField(
        "Author",
        validators=[
            DataRequired(message="Author is required"),
            Length(max=100, message="Author name must be less than 100 characters"),
        ],
    )
    isbn = StringField(
        "ISBN",
        validators=[
            DataRequired(message="ISBN is required"),
            Length(min=10, max=13, message="ISBN must be between 10 and 13 characters"),
        ],
    )
    price = FloatField(
        "Price",
        validators=[
            DataRequired(message="Price is required"),
            NumberRange(min=0, message="Price must be greater than 0"),
        ],
    )
    stock = IntegerField(
        "Stock",
        validators=[
            DataRequired(message="Stock quantity is required"),
            NumberRange(min=0, message="Stock cannot be negative"),
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(message="Description is required"),
            Length(min=10, message="Description must be at least 10 characters"),
        ],
    )
    cover_image = FileField(
        "Cover Image", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    category = SelectField(
        "Category",
        choices=[
            ("", "Select a category"),
            ("Textbooks", "Textbooks"),
            ("Research Papers", "Research Papers"),
            ("Journals", "Journals"),
        ],
        validators=[DataRequired(message="Please select a category")],
    )
    faculty = SelectField(
        "Faculty",
        choices=[
            ("", "Select a faculty"),
            ("Engineering", "Engineering"),
            ("Science", "Science"),
            ("Arts", "Arts"),
            ("Commerce", "Commerce"),
        ],
        validators=[DataRequired(message="Please select a faculty")],
    )
