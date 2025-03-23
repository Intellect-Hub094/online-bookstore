from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, NumberRange

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    author = StringField('Author', validators=[DataRequired(), Length(max=100)])
    isbn = StringField('ISBN', validators=[DataRequired(), Length(max=13)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cover_image = FileField('Cover Image')
