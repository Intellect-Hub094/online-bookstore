from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class DriverOnboardingForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    license_number = StringField("Driver's License Number", validators=[DataRequired()])
    submit = SubmitField("Submit")
