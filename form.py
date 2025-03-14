from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    author = StringField('Author', validators=[DataRequired(), Length(min=2, max=100)])
    price = IntegerField('Price', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, choices=[], validators=[DataRequired()])  # Add category_id
    submit = SubmitField('Add Book')

