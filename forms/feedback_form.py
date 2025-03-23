# forms/feedback_form.py
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from models.book import Book

class FeedbackForm(FlaskForm):
    book_id = SelectField("Book", coerce=int, validators=[DataRequired()])
    received = SelectField("Did you receive the book?", choices=[("yes", "Yes"), ("no", "No")], validators=[DataRequired()])
    comments = TextAreaField("Comments", validators=[Length(max=500)])
    submit = SubmitField("Submit Feedback")

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.book_id.choices = [(book.id, book.title) for book in Book.query.all()]