# forms/delivery_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class DeliveryAddressForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    cellphone = StringField("Cellphone", validators=[DataRequired(), Length(min=10, max=20)])
    address = StringField("Address", validators=[DataRequired(), Length(min=2, max=250)])
    city = StringField("City", validators=[DataRequired(), Length(min=2, max=100)])
    state = StringField("State", validators=[DataRequired(), Length(min=2, max=100)])
    postal_code = StringField("Postal Code", validators=[DataRequired(), Length(min=2, max=20)])
    country = StringField("Country", validators=[DataRequired(), Length(min=2, max=100)])
    notes = TextAreaField("Notes", validators=[Length(max=500)])
    submit = SubmitField("Place Order")