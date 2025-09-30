import os
from datetime import datetime

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = None


def init_db(app):
    global migrate
    # Use get() with fallback to prevent KeyError if DATABASE_URL not set
    if "SQLALCHEMY_DATABASE_URI" not in app.config:
        database_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    return app


class TrainingConfig(db.Model):
    __tablename__ = "training_config"

    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(50), nullable=False, index=True)
    dataset_name = db.Column(db.String(100), nullable=False, index=True)
    batch_size = db.Column(db.Integer, nullable=False)
    learning_rate = db.Column(db.Float, nullable=False)
    epochs = db.Column(db.Integer, nullable=False)
    max_seq_length = db.Column(db.Integer, nullable=False)
    warmup_steps = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    metrics = db.relationship("TrainingMetric", backref="config", lazy=True)


class TrainingMetric(db.Model):
    __tablename__ = "training_metric"
    __table_args__ = (
        db.Index("idx_config_epoch", "config_id", "epoch"),
        db.Index("idx_timestamp", "timestamp"),
    )

    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(
        db.Integer, db.ForeignKey("training_config.id"), nullable=False, index=True
    )
    epoch = db.Column(db.Integer, nullable=False)
    step = db.Column(db.Integer, nullable=False)
    train_loss = db.Column(db.Float, nullable=False)
    eval_loss = db.Column(db.Float, nullable=False)
    process_rank = db.Column(
        db.Integer, nullable=True
    )  # Added for distributed training
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
