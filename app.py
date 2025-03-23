# app.py
from flask import Flask
from extensions import db, login_manager, Migrate
from config import Config
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.book import book_bp
from routes.transaction import transaction_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
Migrate.init_app(app, db)  # Initialize Flask-Migrate with app and db

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(book_bp)
app.register_blueprint(transaction_bp)

if __name__ == "__main__":
    app.run(debug=True)