from flask import Blueprint, jsonify

api_v1_bp = Blueprint("api/v1", __name__)

@api_v1_bp.route("/")
def index():
    return("<h1>Welcome to the University Bookstore API v1!</h1>")
