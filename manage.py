from flask.cli import FlaskGroup
from app import flask_app

cli = FlaskGroup(flask_app)

if __name__ == '__main__':
    cli()
