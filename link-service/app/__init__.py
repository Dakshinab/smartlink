from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# This is the database object - we use it in models.py
db = SQLAlchemy()

def create_app():
    """
    This function creates and configures our Flask app.
    Using a function (called 'app factory pattern') is best practice -
    it makes testing easier and avoids circular imports.
    """
    app = Flask(__name__)

    # Database config - reads from .env file
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", 
        "sqlite:///links.db"  # fallback: use SQLite locally for development
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # Connect database to our app
    db.init_app(app)

    # Register our routes (API endpoints)
    from app.routes import links_bp
    app.register_blueprint(links_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app