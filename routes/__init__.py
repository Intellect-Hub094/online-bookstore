# routes/__init__.py
from flask import Blueprint
from .auth import auth_bp
from .admin import admin_bp
from .user import user_bp
from .book import book_bp
from .transaction import transaction_bp

# Register all blueprints
routes = Blueprint("routes", __name__)
routes.register_blueprint(auth_bp)
routes.register_blueprint(admin_bp)
routes.register_blueprint(user_bp)
routes.register_blueprint(book_bp)
routes.register_blueprint(transaction_bp)