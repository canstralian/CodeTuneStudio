# CodeTuneStudio Architecture

This document provides an overview of the CodeTuneStudio architecture, including system components, data flow, and design decisions.

## System Overview

CodeTuneStudio is a web-based machine learning fine-tuning platform built with Python, Flask, and Streamlit. It provides a user-friendly interface for dataset management, model configuration, training monitoring, and experiment comparison.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CodeTuneStudio Web Interface                 │
│                        (Streamlit)                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                  Application Layer (Flask)                     │
├─────────────────────────────────────────────────────────────────┤
│  Components          │  Utils              │  Plugins          │
│  ├─dataset_selector  │  ├─config_validator │  ├─code_analyzer  │
│  ├─parameter_config  │  ├─database         │  ├─anthropic_*    │
│  ├─training_monitor  │  ├─model_versioning │  └─[extensible]   │
│  ├─experiment_compare│  ├─distributed_*    │                   │
│  └─plugin_manager    │  └─visualization    │                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   Data Layer                                    │
├─────────────────────────────────────────────────────────────────┤
│  Database (SQLAlchemy)     │  External APIs                     │
│  ├─TrainingConfig         │  ├─HuggingFace Hub                 │
│  ├─TrainingMetric         │  ├─Argilla                         │
│  └─Model Versions         │  ├─Anthropic API                   │
│                            │  └─OpenAI API                      │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Application Entry Point (`app.py`)
- **Purpose**: Main application initialization and configuration
- **Responsibilities**:
  - Flask and Streamlit setup
  - Database connection management with retry logic
  - Plugin loading and caching
  - UI layout management
- **Key Features**:
  - Exponential backoff for database connections
  - CSS caching for performance
  - Error boundary handling

### 2. Components Layer

#### Dataset Selector (`components/dataset_selector.py`)
- **Purpose**: Dataset discovery, validation, and preview
- **Features**:
  - HuggingFace dataset integration
  - Argilla dataset support
  - Dataset name validation with regex patterns
  - Preview functionality

#### Parameter Configuration (`components/parameter_config.py`)
- **Purpose**: Training parameter setup and validation
- **Features**:
  - Interactive parameter forms
  - Real-time validation
  - Tooltip documentation
  - Configuration persistence

#### Training Monitor (`components/training_monitor.py`)
- **Purpose**: Real-time training progress tracking
- **Features**:
  - Distributed training support
  - Metrics visualization
  - Resource monitoring
  - Process management

#### Experiment Comparison (`components/experiment_compare.py`)
- **Purpose**: Compare multiple training runs
- **Features**:
  - Side-by-side comparisons
  - Metric trend analysis
  - Configuration diff views
  - Export capabilities

### 3. Utilities Layer

#### Configuration Validator (`utils/config_validator.py`)
- **Purpose**: Input validation and sanitization
- **Current Features**:
  - String sanitization
  - Numeric range validation
  - Required field checking
- **Planned Improvements**:
  - Pydantic model integration
  - Schema-driven validation

#### Database Layer (`utils/database.py`)
- **Purpose**: Data persistence and model definitions
- **Models**:
  - `TrainingConfig`: Training parameters and metadata
  - `TrainingMetric`: Training progress metrics
- **Features**:
  - SQLAlchemy ORM
  - Alembic migrations
  - Connection pooling

#### Model Versioning (`utils/model_versioning.py`)
- **Purpose**: Model lifecycle management
- **Features**:
  - Hash-based versioning
  - Metadata tracking
  - Configuration snapshots
  - File management

### 4. Plugin System

#### Base Classes (`utils/plugins/base.py`)
- **Purpose**: Plugin interface definition
- **Components**:
  - `AgentTool`: Base plugin class
  - `ToolMetadata`: Plugin metadata container
- **Features**:
  - Standardized plugin interface
  - Metadata validation
  - Input/output contracts

#### Plugin Registry (`utils/plugins/registry.py`)
- **Purpose**: Dynamic plugin discovery and management
- **Features**:
  - Automatic plugin discovery
  - Class introspection
  - Error handling and logging
  - Plugin lifecycle management

## Data Flow

### 1. Training Configuration Flow
```
User Input → Parameter Config → Validation → Database Storage → Training Execution
```

### 2. Plugin Execution Flow
```
Plugin Discovery → Registration → UI Integration → User Interaction → Plugin Execution → Result Display
```

### 3. Training Monitoring Flow
```
Training Process → Metrics Collection → Database Storage → Real-time UI Updates
```

## Security Architecture

### Input Validation
- Multi-layer validation (UI → Utils → Database)
- Sanitization of user inputs
- Type checking and range validation

### Plugin Security
- **Current**: Basic validation and error handling
- **Planned**: Sandboxed execution environments

### Secrets Management
- Environment variable configuration
- No secrets in codebase
- Validated secret presence

## Database Schema

### TrainingConfig Table
```sql
id (Primary Key)
model_type (String, 50)
dataset_name (String, 100)
batch_size (Integer)
learning_rate (Float)
epochs (Integer)
max_seq_length (Integer)
warmup_steps (Integer)
created_at (DateTime)
```

### TrainingMetric Table
```sql
id (Primary Key)
config_id (Foreign Key)
epoch (Integer)
step (Integer)
train_loss (Float)
eval_loss (Float)
process_rank (Integer, nullable)
timestamp (DateTime)
```

## Performance Considerations

### Caching Strategy
- CSS caching with `@lru_cache`
- Plugin loading optimization
- Database connection pooling

### Resource Management
- Context managers for database sessions
- Proper cleanup in training processes
- Memory management for large datasets

### Scalability
- Distributed training support
- Modular component architecture
- Plugin system for extensibility

## Error Handling

### Application Level
- Try-catch blocks with logging
- User-friendly error messages
- Fallback mechanisms (SQLite fallback)

### Database Level
- Transaction management
- Connection retry logic
- Data validation before persistence

### Plugin Level
- Plugin sandboxing (planned)
- Error isolation
- Graceful degradation

## Configuration Management

### Environment Variables
- `DATABASE_URL`: Database connection string
- `SQL_DEBUG`: Database query logging
- API keys for external services

### Application Configuration
- Flask configuration
- SQLAlchemy settings
- Streamlit customization

## Deployment Architecture

### Development
- Local SQLite database
- File-based model storage
- Development server

### Production (Planned)
- PostgreSQL database
- Cloud storage integration
- Container deployment
- Load balancing
- Monitoring and logging

## Extension Points

### Custom Components
- New UI components in `components/`
- Integration with existing layout

### Custom Utilities
- Helper functions in `utils/`
- Database model extensions

### Custom Plugins
- Implement `AgentTool` interface
- Automatic discovery and registration

## Future Enhancements

### Planned Improvements
1. Pydantic configuration models
2. Plugin sandboxing
3. Advanced security scanning
4. Comprehensive test coverage
5. API documentation generation
6. Performance monitoring
7. Cloud deployment templates

### Architectural Goals
- Microservices architecture
- Event-driven communication
- Horizontal scalability
- Enhanced security
- Comprehensive observability