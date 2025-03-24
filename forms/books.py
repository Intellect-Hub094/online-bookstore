from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import (
    StringField,
    FloatField,
    IntegerField,
    TextAreaField,
    FileField,
    SelectField,
    DateField,
)
from wtforms.validators import DataRequired, Length, NumberRange


class BookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    author = StringField("Author", validators=[DataRequired(), Length(max=100)])
    isbn = StringField("ISBN", validators=[DataRequired(), Length(max=13)])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField("Description", validators=[DataRequired()])
    cover_image = FileField(
        "Cover Image",
        validators=[
            FileRequired(message="Please upload a cover image"),
            FileAllowed(["jpg"], ".jpg Images only!"),
        ],
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
    publication_date = DateField("Publication Date", format='%Y-%m-%d', validators=[DataRequired()])
