# forms/book_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from models.course import Course

class AddBookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=2, max=100)])
    author = StringField("Author", validators=[DataRequired(), Length(min=2, max=100)])
    price = FloatField("Price", validators=[DataRequired()])
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    image = FileField("Book Image", validators=[DataRequired()])
    submit = SubmitField("Add Book")

    def __init__(self, *args, **kwargs):
        super(AddBookForm, self).__init__(*args, **kwargs)
        self.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

class EditBookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=2, max=100)])
    author = StringField("Author", validators=[DataRequired(), Length(min=2, max=100)])
    price = FloatField("Price", validators=[DataRequired()])
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    image = FileField("Book Image")
    submit = SubmitField("Update Book")

    def __init__(self, *args, **kwargs):
        super(EditBookForm, self).__init__(*args, **kwargs)
        self.course_id.choices = [(course.id, course.name) for course in Course.query.all()]