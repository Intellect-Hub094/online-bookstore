from flask import Flask, render_template, g, session
from flask_migrate import Migrate
from flask_login import LoginManager

from config import Config
from models import db, User

from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.kyc import kyc_bp
from blueprints.api.v1 import api_v1_bp
from blueprints.books import books_bp
from blueprints.cart import cart_bp
from blueprints.orders import orders_bp
from blueprints.checkout import checkout_bp
from blueprints.wishlist import wishlist_bp
from blueprints.profile import profile_bp


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(kyc_bp, url_prefix="/kyc")
app.register_blueprint(books_bp, url_prefix="/books")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(checkout_bp, url_prefix="/checkout")
app.register_blueprint(wishlist_bp, url_prefix="/wishlist")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(admin_bp, url_prefix="/admin")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def load_user():
    g.user = None
    if "_user_id" in session:
        g.user = User.query.get(session["_user_id"])


@app.context_processor
def inject_user():
    return dict(user=g.user)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms_and_conditions.html")


if __name__ == "__main__":
    app.run(debug=True)
