# Database Migration Guide

This document provides comprehensive guidance for managing database migrations in CodeTuneStudio.

## Table of Contents

1. [Overview](#overview)
2. [Database Schema](#database-schema)
3. [Migration Setup](#migration-setup)
4. [Creating Migrations](#creating-migrations)
5. [Applying Migrations](#applying-migrations)
6. [Rollback Procedures](#rollback-procedures)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

CodeTuneStudio uses Flask-Migrate (Alembic) for database migrations. The system supports both PostgreSQL (production) and SQLite (development/fallback).

### Supported Databases
- **PostgreSQL** (Recommended for production)
- **SQLite** (Development and automatic fallback)

### Migration Tool
- **Flask-Migrate**: Alembic-based migration framework for Flask-SQLAlchemy

## Database Schema

### Current Schema Version: 1.0.0

#### Tables

##### `training_config`
Stores configuration for training experiments.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | Integer | Primary key | AUTO_INCREMENT, NOT NULL |
| `model_type` | String(50) | Model architecture name | NOT NULL |
| `dataset_name` | String(100) | Dataset identifier | NOT NULL |
| `batch_size` | Integer | Training batch size | NOT NULL |
| `learning_rate` | Float | Learning rate | NOT NULL |
| `epochs` | Integer | Number of training epochs | NOT NULL |
| `max_seq_length` | Integer | Maximum sequence length | NOT NULL |
| `warmup_steps` | Integer | Learning rate warmup steps | NOT NULL |
| `created_at` | DateTime | Creation timestamp | DEFAULT utcnow() |

**Indexes**: Primary key on `id`

##### `training_metric`
Stores metrics collected during training.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | Integer | Primary key | AUTO_INCREMENT, NOT NULL |
| `config_id` | Integer | Foreign key to training_config | NOT NULL, FK |
| `epoch` | Integer | Training epoch number | NOT NULL |
| `step` | Integer | Training step number | NOT NULL |
| `train_loss` | Float | Training loss value | NOT NULL |
| `eval_loss` | Float | Evaluation loss value | NOT NULL |
| `process_rank` | Integer | Distributed training rank | NULLABLE |
| `timestamp` | DateTime | Metric timestamp | DEFAULT utcnow() |

**Indexes**: 
- Primary key on `id`
- Foreign key on `config_id` referencing `training_config(id)`

**Relationships**:
- `training_metric.config_id` → `training_config.id` (Many-to-One)

### Entity Relationship Diagram

```
training_config (1) ----< (N) training_metric
     |                           |
     +-- id                      +-- id
     +-- model_type              +-- config_id (FK)
     +-- dataset_name            +-- epoch
     +-- batch_size              +-- step
     +-- learning_rate           +-- train_loss
     +-- epochs                  +-- eval_loss
     +-- max_seq_length          +-- process_rank
     +-- warmup_steps            +-- timestamp
     +-- created_at
```

## Migration Setup

### Initial Setup

1. **Set Database URL**:
   ```bash
   # PostgreSQL (Production)
   export DATABASE_URL="postgresql://username:password@host:5432/dbname"
   
   # SQLite (Development)
   export DATABASE_URL="sqlite:///database.db"
   ```

2. **Initialize Migration Repository** (if not exists):
   ```bash
   flask db init
   ```
   
   This creates the `migrations/` directory with:
   - `alembic.ini`: Alembic configuration
   - `env.py`: Migration environment script
   - `versions/`: Migration scripts directory

3. **Verify Setup**:
   ```bash
   flask db current
   ```

## Creating Migrations

### Automatic Migration Generation

When you modify SQLAlchemy models in `utils/database.py`:

1. **Generate migration script**:
   ```bash
   flask db migrate -m "Description of changes"
   ```
   
   This creates a new file in `migrations/versions/` like:
   ```
   abc123def456_description_of_changes.py
   ```

2. **Review the generated script**:
   - Check upgrade() function for forward migration
   - Check downgrade() function for rollback
   - Verify data type conversions
   - Add data migrations if needed

3. **Example migration script**:
   ```python
   """Add process_rank to training_metric
   
   Revision ID: abc123def456
   Revises: xyz789abc123
   Create Date: 2024-12-19 10:00:00.000000
   """
   from alembic import op
   import sqlalchemy as sa
   
   # revision identifiers, used by Alembic
   revision = 'abc123def456'
   down_revision = 'xyz789abc123'
   branch_labels = None
   depends_on = None
   
   def upgrade():
       op.add_column('training_metric', 
           sa.Column('process_rank', sa.Integer(), nullable=True))
   
   def downgrade():
       op.drop_column('training_metric', 'process_rank')
   ```

### Manual Migration Creation

For complex data migrations:

```bash
flask db revision -m "Custom data migration"
```

Then edit the generated file to add custom logic:

```python
def upgrade():
    # Create temporary column
    op.add_column('training_config', 
        sa.Column('temp_field', sa.String(100)))
    
    # Migrate data
    connection = op.get_bind()
    connection.execute(
        "UPDATE training_config SET temp_field = UPPER(model_type)"
    )
    
    # Clean up
    op.drop_column('training_config', 'model_type')
    op.alter_column('training_config', 'temp_field', 
                   new_column_name='model_type')

def downgrade():
    # Reverse the migration
    op.alter_column('training_config', 'model_type', 
                   new_column_name='temp_field')
    op.add_column('training_config', 
        sa.Column('model_type', sa.String(50)))
    
    connection = op.get_bind()
    connection.execute(
        "UPDATE training_config SET model_type = LOWER(temp_field)"
    )
    
    op.drop_column('training_config', 'temp_field')
```

## Applying Migrations

### Upgrade Database

Apply all pending migrations:

```bash
flask db upgrade
```

Apply specific migration:

```bash
flask db upgrade <revision_id>
```

### Check Migration Status

```bash
# Show current version
flask db current

# Show migration history
flask db history

# Show pending migrations
flask db show
```

### Dry Run (PostgreSQL only)

Generate SQL without executing:

```bash
flask db upgrade --sql > migration.sql
```

Review the SQL and apply manually if needed.

## Rollback Procedures

### Simple Rollback

Downgrade one version:

```bash
flask db downgrade
```

Downgrade to specific version:

```bash
flask db downgrade <revision_id>
```

Downgrade to base (empty database):

```bash
flask db downgrade base
```

### Emergency Rollback Procedure

1. **Backup current database**:
   ```bash
   # PostgreSQL
   pg_dump -h host -U user -d dbname > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # SQLite
   cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db
   ```

2. **Stop the application**:
   ```bash
   # Stop Streamlit process
   pkill -f "streamlit run"
   ```

3. **Rollback migration**:
   ```bash
   flask db downgrade
   ```

4. **Verify database integrity**:
   ```bash
   # PostgreSQL
   psql -h host -U user -d dbname -c "\dt"
   
   # SQLite
   sqlite3 database.db ".schema"
   ```

5. **Restart application**:
   ```bash
   python app.py
   ```

### Rollback with Data Preservation

For migrations that delete columns:

1. **Before migration**: Export data
   ```sql
   COPY (SELECT * FROM training_config) TO '/tmp/training_config_backup.csv' CSV HEADER;
   ```

2. **Apply migration**

3. **If rollback needed**: Restore data
   ```sql
   COPY training_config FROM '/tmp/training_config_backup.csv' CSV HEADER;
   ```

## Best Practices

### Migration Development

1. **Always review auto-generated migrations**
   - Check for unintended changes
   - Verify data type compatibility
   - Ensure indexes are preserved

2. **Test migrations in development first**
   ```bash
   # Use SQLite for quick testing
   export DATABASE_URL="sqlite:///test.db"
   flask db upgrade
   flask db downgrade
   ```

3. **Write reversible migrations**
   - Every `upgrade()` should have corresponding `downgrade()`
   - Test both directions
   - Preserve data when possible

4. **Use batch operations for large tables**
   ```python
   from alembic import op
   
   def upgrade():
       with op.batch_alter_table('training_metric') as batch_op:
           batch_op.add_column(sa.Column('new_field', sa.String(100)))
   ```

### Production Migrations

1. **Always backup before migrating**

2. **Run migrations during maintenance window**

3. **Monitor migration progress**:
   ```bash
   # Check PostgreSQL activity
   SELECT * FROM pg_stat_activity WHERE state = 'active';
   ```

4. **Have rollback plan ready**

5. **Coordinate with application deployment**

### Version Control

1. **Commit migration files to git**:
   ```bash
   git add migrations/versions/abc123def456_*.py
   git commit -m "Add migration: description"
   ```

2. **Never modify existing migrations** in production

3. **Create new migration** to fix issues

## Troubleshooting

### Common Issues

#### "Target database is not up to date"

**Problem**: Migration history mismatch

**Solution**:
```bash
# Check current version
flask db current

# Stamp database with correct version
flask db stamp <revision_id>

# Try upgrade again
flask db upgrade
```

#### "Table already exists"

**Problem**: Database and migrations out of sync

**Solution**:
```bash
# Option 1: Stamp current state
flask db stamp head

# Option 2: Reset migrations (DESTRUCTIVE)
flask db downgrade base
flask db upgrade
```

#### "Column does not exist"

**Problem**: Missing migration or failed previous migration

**Solution**:
```bash
# Check migration history
flask db history

# Identify missing migration
flask db upgrade <specific_revision>
```

#### Connection Timeout

**Problem**: Migration taking too long

**Solution**:
```python
# Increase timeout in app.py
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout': 300,  # 5 minutes
    'pool_recycle': 3600
}
```

### Recovery Procedures

#### Corrupt Migration State

1. **Drop alembic_version table**:
   ```sql
   DROP TABLE alembic_version;
   ```

2. **Recreate and stamp**:
   ```bash
   flask db stamp head
   ```

#### Split-brain (multiple heads)

```bash
# Identify heads
flask db heads

# Merge migrations
flask db merge -m "Merge heads" <revision1> <revision2>
```

## Migration Checklist

Before applying migration in production:

- [ ] Migration tested in development environment
- [ ] Database backup created
- [ ] Downgrade procedure tested
- [ ] Migration SQL reviewed (if complex)
- [ ] Maintenance window scheduled
- [ ] Rollback plan documented
- [ ] Team notified of maintenance
- [ ] Monitoring alerts configured
- [ ] Post-migration verification plan ready

## Additional Resources

- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [PostgreSQL Migration Best Practices](https://www.postgresql.org/docs/)

## Support

For migration issues:
1. Check this guide
2. Review Alembic logs in `migrations/`
3. Open GitHub issue with:
   - Migration file content
   - Error messages
   - Database version
   - `flask db history` output

---

**Last Updated**: 2024-12-19
**Schema Version**: 1.0.0
