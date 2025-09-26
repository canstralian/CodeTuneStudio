from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from typing import Optional

db = SQLAlchemy()
migrate: Optional[Migrate] = None


def init_db(app):
    """Initialize database with improved error handling and validation."""
    global migrate
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Validate database URL format
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    return app


class TrainingConfig(db.Model):
    """Model for storing training configuration parameters."""
    __tablename__ = 'training_config'

    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(50), nullable=False)
    dataset_name = db.Column(db.String(100), nullable=False)
    batch_size = db.Column(db.Integer, nullable=False)
    learning_rate = db.Column(db.Float, nullable=False)
    epochs = db.Column(db.Integer, nullable=False)
    max_seq_length = db.Column(db.Integer, nullable=False)
    warmup_steps = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship to metrics
    metrics = db.relationship('TrainingMetric', backref='config', lazy=True,
                              cascade='all, delete-orphan')

    # Add indexes for frequently queried columns
    __table_args__ = (
        db.Index('ix_training_config_model_dataset', 'model_type', 'dataset_name'),
        db.Index('ix_training_config_created_at', 'created_at'),
    )

    def __repr__(self):
        return (f'<TrainingConfig {self.id}: {self.model_type} '
                f'on {self.dataset_name}>')


class TrainingMetric(db.Model):
    """Model for storing training progress metrics."""
    __tablename__ = 'training_metric'

    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('training_config.id'),
                          nullable=False, index=True)
    epoch = db.Column(db.Integer, nullable=False)
    step = db.Column(db.Integer, nullable=False)
    train_loss = db.Column(db.Float, nullable=False)
    eval_loss = db.Column(db.Float, nullable=False)
    process_rank = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Add composite indexes for efficient queries
    __table_args__ = (
        db.Index('ix_training_metric_config_epoch', 'config_id', 'epoch'),
        db.Index('ix_training_metric_config_timestamp', 'config_id', 'timestamp'),
    )

    def __repr__(self):
        return (f'<TrainingMetric {self.id}: Config {self.config_id} '
                f'Epoch {self.epoch}>')