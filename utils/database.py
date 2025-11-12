import os
from datetime import datetime, timezone

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import validates

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
    """Training configuration model with validation and indexing."""
    __tablename__ = "training_config"
    __table_args__ = (
        db.Index("idx_model_type", "model_type"),
        db.Index("idx_dataset_name", "dataset_name"),
        db.Index("idx_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(50), nullable=False)
    dataset_name = db.Column(db.String(100), nullable=False)
    batch_size = db.Column(db.Integer, nullable=False)
    learning_rate = db.Column(db.Float, nullable=False)
    epochs = db.Column(db.Integer, nullable=False)
    max_seq_length = db.Column(db.Integer, nullable=False)
    warmup_steps = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    metrics = db.relationship(
        "TrainingMetric",
        backref="config",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @validates("batch_size")
    def validate_batch_size(self, key, value):
        """Validate batch size is positive."""
        if value <= 0:
            raise ValueError(f"batch_size must be positive, got {value}")
        if value > 1024:
            raise ValueError(f"batch_size too large (max 1024), got {value}")
        return value

    @validates("learning_rate")
    def validate_learning_rate(self, key, value):
        """Validate learning rate is in valid range."""
        if value <= 0 or value >= 1:
            raise ValueError(f"learning_rate must be between 0 and 1, got {value}")
        return value

    @validates("epochs")
    def validate_epochs(self, key, value):
        """Validate epochs is positive."""
        if value <= 0:
            raise ValueError(f"epochs must be positive, got {value}")
        if value > 1000:
            raise ValueError(f"epochs too large (max 1000), got {value}")
        return value

    @validates("max_seq_length")
    def validate_max_seq_length(self, key, value):
        """Validate max sequence length is positive."""
        if value <= 0:
            raise ValueError(f"max_seq_length must be positive, got {value}")
        if value > 8192:
            raise ValueError(f"max_seq_length too large (max 8192), got {value}")
        return value

    @validates("warmup_steps")
    def validate_warmup_steps(self, key, value):
        """Validate warmup steps is non-negative."""
        if value < 0:
            raise ValueError(f"warmup_steps must be non-negative, got {value}")
        return value

    def __repr__(self):
        return f"<TrainingConfig(id={self.id}, model={self.model_type}, dataset={self.dataset_name})>"


class TrainingMetric(db.Model):
    """Training metric model with validation and indexing."""
    __tablename__ = "training_metric"
    __table_args__ = (
        db.Index("idx_config_epoch", "config_id", "epoch"),
        db.Index("idx_timestamp", "timestamp"),
    )

    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(
        db.Integer, db.ForeignKey("training_config.id"), nullable=False
    )
    epoch = db.Column(db.Integer, nullable=False)
    step = db.Column(db.Integer, nullable=False)
    train_loss = db.Column(db.Float, nullable=False)
    eval_loss = db.Column(db.Float, nullable=False)
    process_rank = db.Column(
        db.Integer, nullable=True
    )  # Added for distributed training
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @validates("epoch")
    def validate_epoch(self, key, value):
        """Validate epoch is non-negative."""
        if value < 0:
            raise ValueError(f"epoch must be non-negative, got {value}")
        return value

    @validates("step")
    def validate_step(self, key, value):
        """Validate step is non-negative."""
        if value < 0:
            raise ValueError(f"step must be non-negative, got {value}")
        return value

    @validates("train_loss", "eval_loss")
    def validate_loss(self, key, value):
        """Validate loss values are non-negative and finite."""
        if value < 0:
            raise ValueError(f"{key} must be non-negative, got {value}")
        if not (-1e10 < value < 1e10):  # Check for reasonable bounds
            raise ValueError(f"{key} value out of reasonable range: {value}")
        return value

    def __repr__(self):
        return f"<TrainingMetric(id={self.id}, config_id={self.config_id}, epoch={self.epoch}, step={self.step})>"
