import os

from flask import Flask
from flask_apscheduler import APScheduler

from log_utils import configure_logger
from models import db


def create_app():
    # Configure logger
    configure_logger()

    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object("scheduled_jobs_config")

    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SCHEDULER_API_ENABLED"] = True

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Configure and initialize APScheduler
    scheduler = APScheduler()
    scheduler.init_app(app)

    # Register blueprints
    from .routes import main

    app.register_blueprint(main)

    # Create the database tables within the application context
    with app.app_context():
        db.create_all()

    # Start the scheduler
    scheduler.start()

    return app
