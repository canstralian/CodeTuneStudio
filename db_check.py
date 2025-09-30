import os
import sys

from flask import Flask

from utils.database import db, init_db  # noqa: F401


def check_database() -> bool:
    """
    Check the database connection by setting up a Flask application with SQLAlchemy.

    This function retrieves the database URL from the environment variable
    'DATABASE_URL', defaulting to 'sqlite:///database.db' if not set. It configures
    a Flask app with SQLAlchemy, initializes the database, and attempts to execute a
    simple query ("SELECT 1") to verify the connection. It prints status messages to
    the console and returns True if the connection is successful, or False if it
    fails or returns an unexpected result.

    Returns:
        bool: True if the database connection is successful, False otherwise.

    Raises:
        Exception: Any exception encountered during the connection attempt is caught,
        printed, and results in a False return value.
    """
    print("Checking database connection...")

    app = Flask(__name__)
    database_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    print(f"Using database URL: {database_url}")

    app.config.update(
        {
            "SQLALCHEMY_DATABASE_URI": database_url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    try:
        with app.app_context():
            # Check connection
            from sqlalchemy import text

            result = db.session.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("Database connection successful!")
                print("Database connection successful!")
            else:
                print("Database connection check returned unexpected result")
                return False
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
