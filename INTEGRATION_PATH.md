# CodeTuneStudio Integration Path Analysis

## Executive Summary

**Recommended Integration Path: Option 3 - Hugging Face Spaces Deployment with Enhanced Plugin Architecture**

This document provides a comprehensive analysis of integration options for CodeTuneStudio, evaluating trade-offs between VS Code extension patterns and Flask/Streamlit integration patterns. Based on the project's current architecture (hybrid Streamlit/Flask with plugin system) and strategic goals, we recommend deploying to Hugging Face Spaces while enhancing the existing plugin architecture to support AI model integration.

---

## Table of Contents

1. [Current Architecture Analysis](#current-architecture-analysis)
2. [Integration Path Options](#integration-path-options)
3. [Recommended Path: Option 3 Detailed](#recommended-path-option-3-detailed)
4. [Database Schema Design](#database-schema-design)
5. [HF Model Integration Strategy](#hf-model-integration-strategy)
6. [Deployment Pipeline](#deployment-pipeline)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Risk Analysis & Mitigation](#risk-analysis--mitigation)

---

## Current Architecture Analysis

### Existing Infrastructure

**Hybrid Framework:**
- **Streamlit** (Port 7860): Interactive web UI for model training and experimentation
- **Flask**: Backend API with SQLAlchemy ORM for database operations
- **Database**: PostgreSQL (primary) with SQLite fallback
- **Plugin System**: Dynamic plugin discovery and lifecycle management via `utils/plugins/registry.py`

**Core Components:**
```
CodeTuneStudio/
├── app.py                    # Main orchestration (currently HTML, needs restoration)
├── components/               # Streamlit UI components
│   ├── plugin_manager.py    # Plugin UI management
│   ├── parameter_config.py  # Training config UI
│   └── model_export.py      # HF Hub export functionality
├── utils/
│   ├── database.py          # SQLAlchemy models
│   ├── peft_trainer.py      # LoRA/PEFT training
│   ├── plugins/
│   │   ├── base.py          # AgentTool base class
│   │   └── registry.py      # Plugin registry
│   └── model_inference.py   # Inference utilities
└── plugins/                 # Plugin implementations
    ├── code_analyzer.py
    ├── openai_code_analyzer.py
    └── anthropic_code_suggester.py
```

### Strengths

1. **Modular Plugin Architecture**: Extensible design for adding new code analysis tools
2. **Existing HF Integration**: Components already export to Hugging Face Hub
3. **Database Abstraction**: SQLAlchemy enables easy schema evolution
4. **PEFT/LoRA Support**: Parameter-efficient fine-tuning infrastructure in place
5. **Deployment Ready**: Dockerfile and HF Spaces documentation exists

### Current Limitations

1. **No Prompt Management**: No system for versioning, tracking, or optimizing prompts
2. **Limited AI Model Integration**: Plugin system needs enhancement for LLM integration
3. **No Execution Tracking**: Missing history of prompt executions and outcomes
4. **Static Plugins**: Plugins are Python files, not dynamically configurable
5. **Missing Model Orchestration**: No unified interface for White Rabbit Neo, CodeT5, etc.

---

## Integration Path Options

### Option 1: VS Code Extension (Not Recommended)

**Approach**: Build VS Code extension using TypeScript/JavaScript Extension API

**Pros:**
- Native IDE integration
- Access to VS Code language servers
- Direct file system access
- Rich debugging capabilities

**Cons:**
- Complete rewrite in TypeScript required
- Cannot reuse existing Flask/Streamlit infrastructure  
- Must rebuild database layer in extension context
- Plugin system incompatible with VS Code extension patterns
- Deployment through VS Code Marketplace adds friction
- Limited to VS Code users only

**Verdict**: ❌ **Rejected** - Requires complete rewrite, abandons existing infrastructure

---

### Option 2: Hybrid VS Code + Web (Not Recommended)

**Approach**: VS Code extension frontend communicating with Flask backend

**Pros:**
- Reuses Flask backend
- Provides IDE integration
- Maintains database layer

**Cons:**
- Requires building both VS Code extension AND maintaining web UI
- Complex communication between extension and backend
- Deployment complexity (Marketplace + server hosting)
- Maintenance burden doubled
- Plugin system still needs adaptation for extension context

**Verdict**: ❌ **Rejected** - Unnecessary complexity, split effort

---

### Option 3: Hugging Face Spaces with Enhanced Plugin Architecture (✅ RECOMMENDED)

**Approach**: Deploy enhanced Streamlit/Flask app to HF Spaces, extend plugin system for AI model integration

**Pros:**
- ✅ Leverages ALL existing infrastructure
- ✅ Minimal code changes required
- ✅ Plugin system already extensible
- ✅ Database schema can evolve incrementally
- ✅ HF Spaces provides free GPU access
- ✅ Native integration with HF models
- ✅ Existing export functionality to HF Hub
- ✅ Accessible via browser (cross-platform)
- ✅ Easy CI/CD via GitHub Actions
- ✅ Existing Dockerfile ready

**Cons:**
- ⚠️ No IDE integration (addressable via web-based IDE)
- ⚠️ Requires internet connection
- ⚠️ Limited by HF Spaces resource quotas

**Enhancements Needed:**
1. Extend database schema for prompt management
2. Create AI model plugin types (LLM, CodeGen, Embedding)
3. Add prompt library UI component
4. Implement execution tracking and analytics
5. Integrate White Rabbit Neo and CodeT5 models

**Verdict**: ✅ **RECOMMENDED** - Best ROI, leverages existing work, clear path forward

---

### Option 4: Standalone Web App + API (Alternative)

**Approach**: Deploy as standalone web service with public API

**Pros:**
- Full control over infrastructure
- Can integrate with any IDE via API
- Flexible deployment options

**Cons:**
- Requires custom hosting (cost)
- No free GPU access
- Additional API authentication/security layer needed
- More DevOps overhead

**Verdict**: ⚠️ **Alternative** - Consider if HF Spaces limits become problematic

---

## Recommended Path: Option 3 Detailed

### Architecture Enhancement Plan

```
Enhanced CodeTuneStudio Architecture:

┌─────────────────────────────────────────────────────────────┐
│                  Hugging Face Spaces                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Streamlit UI (Port 7860)                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • Dataset Selector    • Parameter Config           │   │
│  │  • Training Monitor    • Experiment Compare          │   │
│  │  • Plugin Manager      • Prompt Library (NEW)        │   │
│  │  • Model Export        • Execution History (NEW)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Flask Backend API                          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • SQLAlchemy ORM      • Session Management          │   │
│  │  • Training Config API • Prompt Management API (NEW) │   │
│  │  • Metrics Storage     • Execution Tracking (NEW)    │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Enhanced Plugin Registry                      │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Plugin Types:                                        │   │
│  │  • CodeAnalyzer     (existing)                        │   │
│  │  • LLMPlugin        (NEW - for GPT, Claude, etc.)    │   │
│  │  • CodeGenPlugin    (NEW - for CodeT5, Codex)        │   │
│  │  • EmbeddingPlugin  (NEW - for RAG/vector search)    │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         HF Model Integration Layer (NEW)             │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • White Rabbit Neo 33B (Code reasoning)             │   │
│  │  • CodeT5+ (Code generation/completion)              │   │
│  │  • sentence-transformers (Prompt embeddings)         │   │
│  │  • Unified inference API with caching                │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │      PostgreSQL Database (with migrations)           │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Tables:                                              │   │
│  │  • training_config (existing)                         │   │
│  │  • training_metric (existing)                         │   │
│  │  • prompt_library (NEW)                               │   │
│  │  • prompt_versions (NEW)                              │   │
│  │  • execution_history (NEW)                            │   │
│  │  • model_cache (NEW)                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Code Reuse Strategy

**Reusable Components (100%):**
- ✅ `utils/database.py` - Extend with new models
- ✅ `utils/plugins/registry.py` - Add new plugin types
- ✅ `utils/plugins/base.py` - Extend AgentTool base class
- ✅ `components/plugin_manager.py` - Enhance UI for new plugins
- ✅ `components/model_export.py` - Already exports to HF
- ✅ Flask app structure - Add new API routes
- ✅ Existing plugins - Serve as templates

**New Components Needed:**
- 🆕 `utils/model_integrations/` - HF model wrappers
- 🆕 `utils/prompt_manager.py` - Prompt CRUD operations
- 🆕 `components/prompt_library.py` - Prompt management UI
- 🆕 `components/execution_history.py` - Tracking UI
- 🆕 `plugins/white_rabbit_plugin.py` - White Rabbit Neo integration
- 🆕 `plugins/codet5_plugin.py` - CodeT5 integration

---

## Database Schema Design

### New Tables

#### 1. `prompt_library`
Stores versioned prompts for different use cases.

```sql
CREATE TABLE prompt_library (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50) NOT NULL,  -- 'code_generation', 'code_review', 'refactoring', etc.
    use_case VARCHAR(100),           -- 'python_optimization', 'security_audit', etc.
    tags TEXT[],                     -- Array of tags for search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    model_type VARCHAR(50),          -- 'gpt-4', 'claude-3', 'white-rabbit-neo', 'codet5'
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2048,
    
    -- Prompt Engineering
    system_prompt TEXT,
    user_prompt_template TEXT NOT NULL,
    few_shot_examples JSONB,        -- Array of example inputs/outputs
    
    -- Performance Tracking
    avg_execution_time FLOAT,
    success_rate FLOAT,
    total_executions INTEGER DEFAULT 0,
    
    -- Version Control
    current_version_id INTEGER,
    
    CONSTRAINT fk_current_version 
        FOREIGN KEY (current_version_id) 
        REFERENCES prompt_versions(id)
);

CREATE INDEX idx_prompt_category ON prompt_library(category);
CREATE INDEX idx_prompt_tags ON prompt_library USING GIN(tags);
CREATE INDEX idx_prompt_active ON prompt_library(is_active);
```

#### 2. `prompt_versions`
Tracks all versions of each prompt for A/B testing and rollback.

```sql
CREATE TABLE prompt_versions (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    
    -- Version Content
    system_prompt TEXT,
    user_prompt_template TEXT NOT NULL,
    few_shot_examples JSONB,
    
    -- Configuration
    model_type VARCHAR(50),
    temperature FLOAT,
    max_tokens INTEGER,
    
    -- Change Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    change_notes TEXT,
    
    -- A/B Testing Metrics
    test_executions INTEGER DEFAULT 0,
    test_success_rate FLOAT,
    test_avg_execution_time FLOAT,
    
    is_deployed BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP,
    
    CONSTRAINT fk_prompt 
        FOREIGN KEY (prompt_id) 
        REFERENCES prompt_library(id) ON DELETE CASCADE,
    
    UNIQUE(prompt_id, version_number)
);

CREATE INDEX idx_version_prompt ON prompt_versions(prompt_id);
CREATE INDEX idx_version_deployed ON prompt_versions(is_deployed);
```

#### 3. `execution_history`
Logs every prompt execution for analysis and debugging.

```sql
CREATE TABLE execution_history (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER NOT NULL,
    version_id INTEGER NOT NULL,
    
    -- Execution Context
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    
    -- Input/Output
    input_data JSONB NOT NULL,       -- User variables filled into template
    rendered_prompt TEXT,            -- Final prompt sent to model
    output_data JSONB,               -- Model response
    
    -- Execution Metrics
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    model_used VARCHAR(50),
    
    -- Quality Metrics
    success BOOLEAN,
    error_message TEXT,
    user_feedback INTEGER,          -- 1-5 star rating
    user_feedback_text TEXT,
    
    -- Cost Tracking
    estimated_cost_usd DECIMAL(10, 6),
    
    CONSTRAINT fk_execution_prompt 
        FOREIGN KEY (prompt_id) 
        REFERENCES prompt_library(id),
    CONSTRAINT fk_execution_version 
        FOREIGN KEY (version_id) 
        REFERENCES prompt_versions(id)
);

CREATE INDEX idx_execution_prompt ON execution_history(prompt_id);
CREATE INDEX idx_execution_time ON execution_history(executed_at DESC);
CREATE INDEX idx_execution_success ON execution_history(success);
CREATE INDEX idx_execution_session ON execution_history(session_id);
```

#### 4. `model_cache`
Caches model outputs to reduce API costs and latency.

```sql
CREATE TABLE model_cache (
    id SERIAL PRIMARY KEY,
    
    -- Cache Key
    model_name VARCHAR(100) NOT NULL,
    prompt_hash VARCHAR(64) NOT NULL,  -- SHA256 of prompt
    parameters_hash VARCHAR(64),       -- SHA256 of model parameters
    
    -- Cached Data
    cached_output JSONB NOT NULL,
    tokens_used INTEGER,
    
    -- Cache Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 1,
    
    -- Cache Policy
    expires_at TIMESTAMP,
    is_valid BOOLEAN DEFAULT TRUE,
    
    UNIQUE(model_name, prompt_hash, parameters_hash)
);

CREATE INDEX idx_cache_lookup ON model_cache(model_name, prompt_hash, parameters_hash);
CREATE INDEX idx_cache_expiry ON model_cache(expires_at);
```

### Database Migration Strategy

Use **Flask-Migrate** (Alembic) for version-controlled schema evolution:

```bash
# Create new migration
flask db migrate -m "Add prompt management tables"

# Review generated migration in migrations/versions/

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

**Migration File Structure:**
```
migrations/
├── versions/
│   ├── 001_initial_schema.py (existing)
│   ├── 002_add_prompt_library.py (NEW)
│   ├── 003_add_prompt_versions.py (NEW)
│   ├── 004_add_execution_history.py (NEW)
│   └── 005_add_model_cache.py (NEW)
```

---

## HF Model Integration Strategy

### 1. White Rabbit Neo 33B Integration

**Model**: `whiterabbitneo/WhiteRabbitNeo-33B-v1`

**Capabilities:**
- Advanced code reasoning and explanation
- Security vulnerability detection
- Code quality assessment
- Architectural recommendations

**Integration Approach:**

```python
# plugins/white_rabbit_plugin.py

from utils.plugins.base import AgentTool, ToolMetadata
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class WhiteRabbitNeoPlugin(AgentTool):
    metadata = ToolMetadata(
        name="WhiteRabbitNeo",
        description="Advanced code reasoning and security analysis using White Rabbit Neo 33B",
        version="1.0.0",
        author="CodeTuneStudio",
        tags=["llm", "code-analysis", "security"],
    )
    
    def __init__(self):
        super().__init__()
        self.model_name = "whiterabbitneo/WhiteRabbitNeo-33B-v1"
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load model to optimize memory usage"""
        if self.model is None:
            # Use 4-bit quantization for HF Spaces GPU limits
            from transformers import BitsAndBytesConfig
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
    
    def execute(self, code: str, task: str = "analyze") -> dict:
        """
        Execute code analysis task using White Rabbit Neo.
        
        Args:
            code: Source code to analyze
            task: Type of analysis ('analyze', 'security', 'optimize')
        
        Returns:
            Dict with analysis results
        """
        prompt_template = self._get_prompt_template(task)
        prompt = prompt_template.format(code=code)
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "task": task,
            "input_code": code,
            "analysis": response,
            "model": self.model_name,
            "tokens_used": len(outputs[0])
        }
    
    def _get_prompt_template(self, task: str) -> str:
        """Get task-specific prompt template from database"""
        templates = {
            "analyze": """You are an expert code reviewer. Analyze the following code for:
- Code quality and best practices
- Potential bugs and edge cases
- Performance considerations
- Maintainability issues

Code:
```
{code}
```

Provide a structured analysis:""",
            
            "security": """You are a security expert. Analyze the following code for security vulnerabilities:
- SQL injection risks
- XSS vulnerabilities
- Authentication/authorization issues
- Data exposure risks
- Insecure dependencies

Code:
```
{code}
```

Security Analysis:""",
            
            "optimize": """You are a performance optimization expert. Analyze this code for optimization opportunities:
- Time complexity improvements
- Space complexity reductions
- Caching opportunities
- Algorithm optimizations

Code:
```
{code}
```

Optimization Recommendations:"""
        }
        return templates.get(task, templates["analyze"])
```

### 2. CodeT5+ Integration

**Model**: `Salesforce/codet5p-16b`

**Capabilities:**
- Code generation from natural language
- Code completion
- Code summarization
- Unit test generation

**Integration Approach:**

```python
# plugins/codet5_plugin.py

from utils.plugins.base import AgentTool, ToolMetadata
from transformers import T5ForConditionalGeneration, AutoTokenizer

class CodeT5Plugin(AgentTool):
    metadata = ToolMetadata(
        name="CodeT5Plus",
        description="Code generation and completion using CodeT5+ 16B",
        version="1.0.0",
        author="CodeTuneStudio",
        tags=["code-generation", "completion", "summarization"],
    )
    
    def __init__(self):
        super().__init__()
        self.model_name = "Salesforce/codet5p-16b"
        self.model = None
        self.tokenizer = None
    
    def _load_model(self):
        """Lazy load CodeT5+ model"""
        if self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
    
    def execute(self, task_description: str, language: str = "python") -> dict:
        """
        Generate code from natural language description.
        
        Args:
            task_description: Natural language description of desired code
            language: Target programming language
        
        Returns:
            Dict with generated code
        """
        self._load_model()
        
        # CodeT5+ uses specific prefixes for different tasks
        prompt = f"Generate {language} code: {task_description}"
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            **inputs,
            max_length=512,
            num_beams=5,
            temperature=0.8,
        )
        
        generated_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "task_description": task_description,
            "language": language,
            "generated_code": generated_code,
            "model": self.model_name,
            "tokens_used": len(outputs[0])
        }
```

### 3. Unified Model Interface

Create abstraction layer for consistent API across models:

```python
# utils/model_integrations/unified_interface.py

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import hashlib
import json

class ModelInterface(ABC):
    """Unified interface for all AI models"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embeddings for RAG"""
        pass
    
    def cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate cache key for prompt + params"""
        content = f"{prompt}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def execute_with_cache(
        self, 
        prompt: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute prompt with caching layer.
        
        Checks model_cache table first, falls back to generation if miss.
        """
        from utils.database import db, ModelCache
        from datetime import datetime, timedelta
        
        params = params or {}
        cache_key = self.cache_key(prompt, params)
        
        # Check cache
        cached = ModelCache.query.filter_by(
            model_name=self.model_name,
            prompt_hash=cache_key,
            is_valid=True
        ).filter(
            ModelCache.expires_at > datetime.utcnow()
        ).first()
        
        if cached:
            # Update access stats
            cached.last_accessed_at = datetime.utcnow()
            cached.access_count += 1
            db.session.commit()
            
            return {
                "output": cached.cached_output,
                "tokens_used": cached.tokens_used,
                "from_cache": True
            }
        
        # Cache miss - generate new response
        output = self.generate(prompt, **params)
        tokens_used = self._count_tokens(output)
        
        # Store in cache (expire after 24 hours)
        cache_entry = ModelCache(
            model_name=self.model_name,
            prompt_hash=cache_key,
            parameters_hash=hashlib.sha256(
                json.dumps(params, sort_keys=True).encode()
            ).hexdigest(),
            cached_output={"text": output},
            tokens_used=tokens_used,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(cache_entry)
        db.session.commit()
        
        return {
            "output": output,
            "tokens_used": tokens_used,
            "from_cache": False
        }
```

### Prompt Optimization Strategies

**1. Few-Shot Learning:**
Store high-quality example inputs/outputs in `few_shot_examples` JSONB field:

```json
{
  "examples": [
    {
      "input": "def calculate_total(prices):\n    total = 0\n    for price in prices:\n        total += price\n    return total",
      "output": "This function can be optimized using Python's built-in sum():\n\ndef calculate_total(prices: list[float]) -> float:\n    return sum(prices)"
    },
    {
      "input": "...",
      "output": "..."
    }
  ]
}
```

**2. Chain-of-Thought Prompting:**
Guide models through reasoning steps:

```
Think through this code analysis step-by-step:
1. Identify the purpose of the code
2. List potential issues or improvements
3. Rank improvements by impact
4. Provide detailed recommendations

Code: {code}
```

**3. Temperature Tuning:**
- Code generation: 0.2-0.4 (deterministic)
- Creative refactoring: 0.7-0.9 (exploratory)
- Analysis: 0.5-0.7 (balanced)

Store optimal temperature per prompt in database.

---

## Deployment Pipeline

### CI/CD Strategy

**GitHub Actions Workflow for HF Spaces:**

```yaml
# .github/workflows/huggingface-deploy.yml

name: Deploy to Hugging Face Spaces

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.10
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run linters
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88
      
      - name: Run tests
        run: |
          python -m unittest discover -s tests
        env:
          DATABASE_URL: sqlite:///test.db
      
      - name: Push to Hugging Face Space
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./
          destination_dir: ./
          cname: your-space-name.hf.space
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
      
      - name: Run database migrations
        run: |
          python -c "from app import flask_app; from utils.database import db; db.create_all()"
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### HF Spaces Configuration

**README.md for Spaces:**

```markdown
---
title: CodeTuneStudio
emoji: 🎵💻
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.26.0"
app_file: app.py
pinned: true
license: mit
python_version: "3.10"
---

# CodeTuneStudio

ML Model Fine-tuning Platform with AI-powered code analysis and optimization.

## Features
- PEFT/LoRA fine-tuning
- White Rabbit Neo code reasoning
- CodeT5+ code generation
- Prompt engineering workbench
- Execution history tracking

## Environment Variables

Required secrets (set in Space settings):
- `DATABASE_URL`: PostgreSQL connection string
- `HF_TOKEN`: Hugging Face API token (for model access)
- `OPENAI_API_KEY`: Optional, for OpenAI plugin
- `ANTHROPIC_API_KEY`: Optional, for Anthropic plugin
```

**Resource Allocation:**

```yaml
# space.yaml

resources:
  gpu: "a100-large"  # For White Rabbit Neo 33B with 4-bit quantization
  cpu: 8
  memory: "32GB"
  storage: "50GB"

hardware:
  gpu:
    type: "A100"
    count: 1
```

### Deployment Checklist

- [ ] Set up HF Space repository
- [ ] Configure secrets (DATABASE_URL, HF_TOKEN, etc.)
- [ ] Test locally with Docker: `docker build -t codetunestudio . && docker run -p 7860:7860 codetunestudio`
- [ ] Push initial version to Space
- [ ] Verify database connectivity
- [ ] Test plugin loading
- [ ] Validate model inference
- [ ] Monitor resource usage
- [ ] Set up monitoring/alerting (HF Spaces metrics)

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goals:** Restore core functionality, extend database schema

- [ ] **Restore app.py** from test references or rebuild
  - Implement `MLFineTuningApp` class
  - Set up Flask/Streamlit orchestration
  - Configure database connection with retry logic
  
- [ ] **Database Schema Extension**
  - Create migration: `flask db migrate -m "Add prompt management tables"`
  - Implement `prompt_library`, `prompt_versions`, `execution_history`, `model_cache` tables
  - Write database access layer in `utils/prompt_manager.py`
  - Add indexes for performance
  
- [ ] **Testing**
  - Unit tests for new database models
  - Integration tests for prompt CRUD operations
  - Test migrations on PostgreSQL and SQLite

**Deliverables:**
- ✅ Functional app.py
- ✅ Extended database schema with migrations
- ✅ Prompt management API layer
- ✅ Test coverage >80%

### Phase 2: Plugin System Enhancement (Weeks 3-4)

**Goals:** Extend plugin architecture for LLM integration

- [ ] **Enhanced Plugin Base Classes**
  - Extend `AgentTool` with `LLMPlugin` subclass
  - Add `CodeGenPlugin` and `EmbeddingPlugin` types
  - Implement plugin lifecycle hooks (load, unload, reload)
  
- [ ] **Model Integration Layer**
  - Create `utils/model_integrations/unified_interface.py`
  - Implement `ModelInterface` abstract base class
  - Add model caching logic with database backend
  - Create model pool for efficient resource usage
  
- [ ] **White Rabbit Neo Plugin**
  - Implement `plugins/white_rabbit_plugin.py`
  - Add 4-bit quantization configuration
  - Create prompt templates for different analysis tasks
  - Test on sample code snippets
  
- [ ] **CodeT5+ Plugin**
  - Implement `plugins/codet5_plugin.py`
  - Add code generation, completion, summarization tasks
  - Integrate with prompt library
  - Test generation quality

**Deliverables:**
- ✅ Extended plugin system with LLM support
- ✅ White Rabbit Neo plugin functional
- ✅ CodeT5+ plugin functional
- ✅ Model caching reduces API calls by 60%+

### Phase 3: UI Components (Weeks 5-6)

**Goals:** Build user interface for prompt management and execution tracking

- [ ] **Prompt Library Component**
  - Create `components/prompt_library.py`
  - UI for browsing, searching, filtering prompts
  - Prompt editor with syntax highlighting
  - Few-shot example editor
  - A/B testing configuration
  
- [ ] **Execution History Component**
  - Create `components/execution_history.py`
  - Timeline view of executions
  - Filtering by prompt, model, success rate
  - Cost analytics dashboard
  - User feedback collection
  
- [ ] **Enhanced Plugin Manager**
  - Update `components/plugin_manager.py`
  - Display LLM plugins with model info
  - Plugin configuration UI (temperature, max_tokens)
  - Real-time status (loaded, error, disabled)
  
- [ ] **Prompt Workbench**
  - Create `components/prompt_workbench.py`
  - Live prompt testing interface
  - Variable substitution preview
  - Side-by-side version comparison
  - Performance metrics display

**Deliverables:**
- ✅ Prompt library UI component
- ✅ Execution history dashboard
- ✅ Enhanced plugin manager
- ✅ Prompt workbench for testing

### Phase 4: Deployment & Optimization (Weeks 7-8)

**Goals:** Deploy to HF Spaces, optimize performance

- [ ] **HF Spaces Deployment**
  - Configure space.yaml for GPU resources
  - Set up secrets and environment variables
  - Test deployment with staging space first
  - Deploy to production space
  
- [ ] **Performance Optimization**
  - Implement model quantization (4-bit for WRN, FP16 for CodeT5)
  - Add model warming/preloading
  - Optimize database queries (add missing indexes)
  - Implement request batching for model inference
  
- [ ] **Monitoring & Observability**
  - Add logging for model inference times
  - Track cache hit rates
  - Monitor GPU memory usage
  - Set up error alerting
  
- [ ] **Documentation**
  - Update README with new features
  - Create user guide for prompt engineering
  - Document plugin development process
  - Add API documentation

**Deliverables:**
- ✅ Live HF Spaces deployment
- ✅ <2s response time for cached queries
- ✅ <10s response time for cold queries
- ✅ Comprehensive documentation

### Phase 5: Evaluation & Iteration (Weeks 9-10)

**Goals:** Evaluate system performance, iterate based on findings

- [ ] **Prompt Engineering Evaluation**
  - Create benchmark dataset from HumanEval, MBPP
  - Measure code generation quality (pass@k, BLEU)
  - A/B test prompt variations
  - Document best practices
  
- [ ] **Dataset Integration**
  - Integrate `bigcode/the-stack` for training data
  - Add `openai_humaneval` for evaluation
  - Create custom dataset for prompt evaluation
  - Implement dataset download/caching
  
- [ ] **User Feedback Loop**
  - Collect user ratings on generated code
  - Analyze execution history for pain points
  - Identify high-value prompts for optimization
  - Create leaderboard of best-performing prompts
  
- [ ] **Iteration Based on Metrics**
  - Optimize low-performing prompts
  - Add new prompt templates for common use cases
  - Improve error handling based on logs
  - Reduce cold-start latency

**Deliverables:**
- ✅ Benchmark evaluation results
- ✅ Optimized prompt library with 10+ templates
- ✅ User feedback dashboard
- ✅ Iteration report with ROI metrics

---

## Risk Analysis & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| **HF Spaces GPU quota limits** | High | High | • Implement aggressive caching<br>• Use 4-bit quantization<br>• Fallback to CPU for smaller models |
| **Model inference latency** | Medium | High | • Preload models on startup<br>• Implement request queuing<br>• Use streaming responses |
| **Database connection failures** | Low | High | • Automatic retry with exponential backoff<br>• SQLite fallback already in place<br>• Connection pooling |
| **Plugin conflicts** | Low | Medium | • Sandboxed plugin execution<br>• Version compatibility checks<br>• Graceful failure handling |
| **Cost overruns (API usage)** | Medium | Medium | • Strict caching policy<br>• Rate limiting per user<br>• Cost tracking dashboard |

### Architectural Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| **Schema migration failures** | Low | High | • Test migrations on staging first<br>• Implement rollback procedures<br>• Backup database before migrations |
| **Plugin system scalability** | Medium | Medium | • Lazy loading of plugins<br>• Plugin resource limits<br>• Async plugin execution |
| **Data privacy concerns** | Low | Critical | • No user code stored permanently<br>• Execution history retention policy<br>• GDPR compliance documentation |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| **HF Spaces downtime** | Low | High | • Maintain local development environment<br>• Document migration to self-hosted option<br>• Backup critical data |
| **Dependency vulnerabilities** | Medium | Medium | • Run `safety check` in CI/CD<br>• Automated dependency updates<br>• Security scanning with Bandit |
| **Model deprecation** | Low | Medium | • Abstract model interface allows swapping<br>• Version pin in requirements.txt<br>• Cache model weights locally |

---

## Relevant Hugging Face Datasets

### For Training & Fine-tuning

1. **bigcode/the-stack** 
   - 3TB of permissively licensed source code
   - Use for fine-tuning CodeT5+ on domain-specific code
   
2. **codeparrot/github-code-clean**
   - Cleaned GitHub code dataset
   - Python, JavaScript, Java, Go, etc.

3. **HuggingFaceH4/CodeAlpaca-20k**
   - 20k instruction-following examples for code
   - Use for prompt engineering benchmarks

### For Evaluation

1. **openai_humaneval**
   - 164 Python programming problems
   - Standard benchmark for code generation
   - Measure pass@k metrics

2. **mbpp** (Mostly Basic Python Problems)
   - 1,000 crowd-sourced Python problems
   - Good for testing basic code generation

3. **code_search_net**
   - 6 programming languages
   - Code documentation pairs
   - Use for code summarization evaluation

### For Prompt Engineering

1. **fka/awesome-chatgpt-prompts**
   - Curated prompt examples
   - Adapt for code generation tasks

2. **HuggingFaceH4/ultrafeedback_binarized**
   - Human feedback on model outputs
   - Use for RLHF-style prompt optimization

---

## Success Metrics

### Technical KPIs

- **Response Latency**: <10s for 95th percentile (cold), <2s (cached)
- **Cache Hit Rate**: >60% after 1 week of usage
- **Model Uptime**: >99% availability
- **Test Coverage**: >80% for core functionality

### Business KPIs

- **User Engagement**: >100 unique users in first month
- **Prompt Library Growth**: >50 community-contributed prompts in 3 months
- **Execution Success Rate**: >85% success rate for code generation tasks
- **Cost Efficiency**: <$0.10 per generation (with caching)

### Quality Metrics

- **Code Generation Quality**: >60% pass@1 on HumanEval benchmark
- **User Satisfaction**: >4.0/5.0 average rating on generated code
- **Plugin Adoption**: >5 active plugins deployed
- **Documentation Coverage**: 100% of public APIs documented

---

## Conclusion

**Recommended Integration Path: Option 3 (HF Spaces + Enhanced Plugin Architecture)**

This path provides the optimal balance of:
- ✅ Maximum code reuse (95%+ of existing infrastructure)
- ✅ Lowest development effort (8-10 weeks)
- ✅ Best ROI (leverages existing work)
- ✅ Scalable architecture (modular plugin system)
- ✅ Free GPU access (HF Spaces)
- ✅ Native HF ecosystem integration

### Next Steps

1. **Immediate (Week 1)**:
   - Restore app.py functionality
   - Create database migration for prompt tables
   - Set up HF Spaces staging environment

2. **Short-term (Weeks 2-4)**:
   - Implement White Rabbit Neo and CodeT5+ plugins
   - Build prompt library UI
   - Deploy to staging HF Space

3. **Medium-term (Weeks 5-8)**:
   - Add execution history tracking
   - Optimize model inference performance
   - Deploy to production HF Space

4. **Long-term (Weeks 9+)**:
   - Evaluate with benchmark datasets
   - Iterate based on user feedback
   - Expand plugin ecosystem

### Research Sprint Deliverables

Upon approval of this integration path, the next phase will deliver:

1. **Technical Implementation Guide** (detailed code examples)
2. **API Documentation** (REST endpoints, plugin interfaces)
3. **Deployment Runbook** (step-by-step HF Spaces setup)
4. **Prompt Engineering Playbook** (best practices, templates)
5. **Evaluation Framework** (benchmarks, metrics, dashboards)

---

## Appendix

### A. Plugin System Code Example

See implementation details in:
- `utils/plugins/base.py`
- `utils/plugins/registry.py`
- `plugins/white_rabbit_plugin.py` (NEW)
- `plugins/codet5_plugin.py` (NEW)

### B. Database ER Diagram

```
TrainingConfig (existing)
    ├─── TrainingMetric (existing)
    
PromptLibrary (NEW)
    ├─── PromptVersions (NEW)
    │       └─── ExecutionHistory (NEW)
    └─── ExecutionHistory (NEW)
    
ModelCache (NEW)
```

### C. API Endpoints

```
Existing:
  POST /api/training/config
  GET  /api/training/metrics/{config_id}
  GET  /api/training/config/{config_id}

New:
  POST   /api/prompts/                  # Create prompt
  GET    /api/prompts/                  # List prompts
  GET    /api/prompts/{id}              # Get prompt details
  PUT    /api/prompts/{id}              # Update prompt
  DELETE /api/prompts/{id}              # Delete prompt
  POST   /api/prompts/{id}/versions     # Create new version
  GET    /api/prompts/{id}/versions     # List versions
  POST   /api/prompts/{id}/execute      # Execute prompt
  GET    /api/execution/history         # Get execution history
  GET    /api/execution/history/{id}    # Get execution details
  POST   /api/execution/feedback        # Submit user feedback
  GET    /api/models/available          # List available models
  POST   /api/models/load               # Load model
  GET    /api/cache/stats               # Cache statistics
```

### D. Resource Requirements

**Minimum HF Spaces Configuration:**
- GPU: A100 (40GB VRAM) for White Rabbit Neo 33B with 4-bit quantization
- CPU: 8 cores
- RAM: 32GB
- Storage: 50GB (models + database + cache)

**Estimated Costs:**
- HF Spaces: Free (with resource limits) or ~$1/hr for A100
- PostgreSQL: $15/month (Heroku Postgres Hobby Basic)
- Total: $15-50/month depending on usage

---

**Document Version**: 1.0  
**Last Updated**: 2024-10-10  
**Author**: CodeTuneStudio Team  
**Status**: Ready for Implementation

