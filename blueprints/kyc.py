from flask import Blueprint, render_template, redirect, url_for
from forms import DriverOnboardingForm, CustomerOnboardingForm

kyc_bp = Blueprint("kyc", __name__)


@kyc_bp.route("/onboarding/driver", methods=["GET", "POST"])
def driver_onboarding():
    form = DriverOnboardingForm()
    if form.validate_on_submit():
        # Add driver onboarding logic here
        return redirect(url_for("index"))
    return render_template("kyc/onboarding/driver.html", form=form)


@kyc_bp.route("/onboarding/customer", methods=["GET", "POST"])
def customer_onboarding():
    form = CustomerOnboardingForm()
    if form.validate_on_submit():
        # Add customer onboarding logic here
        return redirect(url_for("index"))
    return render_template("kyc/onboarding/customer.html", form=form)
