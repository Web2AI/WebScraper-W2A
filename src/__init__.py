import os

from flask import Flask

from log_utils import configure_logger
from models import db


def create_app():
    configure_logger()

    app = Flask(__name__)

    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Register blueprints
    from .routes import main

    app.register_blueprint(main)

    # Create the database tables within the application context
    with app.app_context():
        db.create_all()

    return app
