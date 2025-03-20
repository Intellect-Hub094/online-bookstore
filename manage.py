# manage.py
from flask_migrate import Migrate, init, migrate, upgrade
from app import app, db  # Import app and db

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        init()  # Run once to initialize migrations
        migrate()  # Create migration scripts
        upgrade()  # Apply migrations
