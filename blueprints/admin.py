from flask import Blueprint, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Cart, Book, db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def index():
    return render_template("admin/index.html")
