from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CustomerOnboardingForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    student_id = StringField("Student ID", validators=[DataRequired()])
    submit = SubmitField("Submit")
