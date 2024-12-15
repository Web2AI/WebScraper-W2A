import os

import chromadb
from flask import Flask
from flask_apscheduler import APScheduler
from langchain_huggingface import HuggingFaceEmbeddings

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

    app.chromadb_client = chromadb.HttpClient(
        host=os.getenv("CHROMADB_HOST", "chatbot-chromadb"),
        port=int(os.getenv("CHROMADB_PORT", "8000")),
        settings=chromadb.Settings(allow_reset=True, anonymized_telemetry=False),
    )

    app.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

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
