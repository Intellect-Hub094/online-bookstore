from flask import Flask, render_template
from flask_migrate import Migrate

from db import init_db

app = Flask(__name__)
db = init_db(app)
migrate = Migrate(app, db)

# Register blueprints
from blueprints.auth import auth_bp
from blueprints.kyc import kyc_bp
from blueprints.api.v1 import api_v1_bp

app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(kyc_bp, url_prefix="/kyc")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
