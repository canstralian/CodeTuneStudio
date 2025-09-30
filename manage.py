"""
Flask CLI management script for the CodeTuneStudio application.

This script initializes a FlaskGroup CLI instance with the main Flask app,
enabling command-line operations such as running the development server,
managing database migrations, and other Flask-related tasks.

Usage:
    python manage.py <command>

Example commands:
    - run: Start the development server.
    - shell: Open an interactive shell with app context.
    - db: Database migration commands (if Flask-Migrate is used).
"""

from flask.cli import FlaskGroup

from app import get_flask_app

cli = FlaskGroup(create_app=get_flask_app)

if __name__ == "__main__":
    cli()
