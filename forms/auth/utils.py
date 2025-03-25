from wtforms.validators import ValidationError


def dut4life_email(form, field):
    if "@dut4life.ac.za" not in field.data:
        raise ValidationError("Must be a dut4life email address")
