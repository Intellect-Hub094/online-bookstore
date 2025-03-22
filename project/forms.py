from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, SelectField, FloatField, BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    profile_picture = FileField("Profile Picture")
    date_of_birth = DateField("Date of Birth", format="%Y-%m-%d", validators=[DataRequired()])
    marital_status = SelectField("Marital Status", choices=[("single", "Single"), ("married", "Married"), ("divorced", "Divorced")], validators=[DataRequired()])
    full_name = StringField("Full Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class DeliveryAddressForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    cellphone = StringField("Cellphone Number", validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField("Address", validators=[DataRequired(), Length(max=200)])
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    state = StringField("State/Province", validators=[DataRequired(), Length(max=100)])
    postal_code = StringField("Postal Code", validators=[DataRequired(), Length(max=20)])
    country = StringField("Country", validators=[DataRequired(), Length(max=100)])
    notes = TextAreaField("Additional Notes", validators=[Length(max=500)])
    submit = SubmitField("Submit Order")

class FeedbackForm(FlaskForm):
    book_id = SelectField("Select Book", coerce=int, validators=[DataRequired()])
    received = SelectField("Did you receive the book?", choices=[("yes", "Yes"), ("no", "No")], validators=[DataRequired()])
    comments = StringField("Comments (if any)")
    submit = SubmitField("Submit Feedback")

class AddBookForm(FlaskForm):
    faculty = SelectField("Faculty", coerce=int, validators=[DataRequired()])
    department = SelectField("Department", coerce=int, validators=[DataRequired()])
    course = SelectField("Course", coerce=int, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    image = FileField("Book Image", validators=[DataRequired()])
    submit = SubmitField("Add Book")

class ProfileForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    profile_picture = FileField("Update Profile Picture")
    date_of_birth = DateField("Date of Birth", format="%Y-%m-%d", validators=[DataRequired()])
    marital_status = SelectField("Marital Status", choices=[("single", "Single"), ("married", "Married"), ("divorced", "Divorced")], validators=[DataRequired()])
    full_name = StringField("Full Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Update Profile")

class EditUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    is_admin = BooleanField("Is Admin")
    submit = SubmitField("Update User")
