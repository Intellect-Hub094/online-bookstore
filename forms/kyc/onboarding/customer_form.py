from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email


class CustomerOnboardingForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired()])
    address = TextAreaField("Delivery Address", validators=[DataRequired()])
    student_id = StringField("Student ID")
    terms = BooleanField("I agree to the Terms and Conditions", validators=[DataRequired()])
    submit = SubmitField("Complete Registration")
