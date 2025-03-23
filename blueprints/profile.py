from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Order

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/")
# @login_required
def list_orders():
    return render_template("profile.html")
