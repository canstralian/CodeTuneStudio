
import os
import sys
from flask import Flask
from utils.database import init_db, db

def check_database():
    """Utility to check database connection"""
    print("Checking database connection...")
    
    app = Flask(__name__)
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    print(f"Using database URL: {database_url}")
    
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    
    try:
        with app.app_context():
            init_db(app)
            # Check connection
            result = db.session.execute("SELECT 1").scalar()
            if result == 1:
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
