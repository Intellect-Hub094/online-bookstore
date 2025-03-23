from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        app.config.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///:memory:"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = app.config.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    )
    db.init_app(app)

    with app.app_context():
        db.create_all()
