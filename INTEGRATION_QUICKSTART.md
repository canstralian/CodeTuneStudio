# Integration Path Quick Start Guide

## TL;DR - What You Need to Know

**Recommended Approach**: Deploy to Hugging Face Spaces with enhanced plugin architecture (Option 3)

**Why This Path?**
- ✅ Reuses 95% of your existing code
- ✅ 8-10 weeks to full implementation
- ✅ Free GPU access from HF Spaces
- ✅ Already have HF integration code in place

---

## Immediate Next Steps (This Week)

### 1. Set Up HF Space (30 minutes)

```bash
# Create new HF Space
Visit: https://huggingface.co/spaces
Click "Create new Space"
- Name: codetunestudio
- SDK: Streamlit
- Hardware: A100 (for White Rabbit Neo)
- Visibility: Public

# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/codetunestudio
cd codetunestudio

# Copy project files
cp -r /path/to/CodeTuneStudio/* .
git add .
git commit -m "Initial deployment"
git push
```

### 2. Configure Secrets (10 minutes)

In your HF Space settings, add these secrets:
- `DATABASE_URL`: Your PostgreSQL URL (or use Heroku free tier)
- `HF_TOKEN`: Your Hugging Face API token
- `OPENAI_API_KEY`: (Optional) For OpenAI plugin
- `ANTHROPIC_API_KEY`: (Optional) For Anthropic plugin

### 3. Create Database Migrations (1 hour)

```bash
# Install Flask-Migrate if not already
pip install Flask-Migrate

# Create new migration for prompt tables
flask db init  # If not already initialized
flask db migrate -m "Add prompt management tables"

# Review the generated migration file
cat migrations/versions/*_add_prompt_management_tables.py

# Apply migration
flask db upgrade
```

**What This Creates:**
- `prompt_library` table: Stores your prompts
- `prompt_versions` table: Tracks prompt versions
- `execution_history` table: Logs every execution
- `model_cache` table: Caches model outputs

---

## Week-by-Week Breakdown

### Week 1-2: Foundation
**Goal**: Get basic infrastructure working

**Tasks**:
1. Restore/verify app.py functionality
2. Add new database tables via migrations
3. Create `utils/prompt_manager.py` for CRUD operations
4. Write tests for new database models

**Time Commitment**: 20-30 hours

**Success Criteria**:
- ✓ Can create/read/update/delete prompts
- ✓ Database migrations work on both PostgreSQL and SQLite
- ✓ Tests pass

### Week 3-4: AI Model Integration
**Goal**: Integrate White Rabbit Neo and CodeT5+

**Tasks**:
1. Create `plugins/white_rabbit_plugin.py`
2. Create `plugins/codet5_plugin.py`
3. Implement model caching
4. Add 4-bit quantization for GPU efficiency

**Time Commitment**: 30-40 hours

**Success Criteria**:
- ✓ Can analyze code with White Rabbit Neo
- ✓ Can generate code with CodeT5+
- ✓ Cache reduces API calls by 60%+
- ✓ Models fit in HF Spaces GPU memory

### Week 5-6: UI Components
**Goal**: Build prompt management interface

**Tasks**:
1. Create `components/prompt_library.py`
2. Create `components/execution_history.py`
3. Update `components/plugin_manager.py`
4. Add prompt testing workbench

**Time Commitment**: 25-35 hours

**Success Criteria**:
- ✓ Can browse and edit prompts in UI
- ✓ Can see execution history
- ✓ Can test prompts interactively
- ✓ UI is intuitive and responsive

### Week 7-8: Deployment & Optimization
**Goal**: Production-ready deployment

**Tasks**:
1. Deploy to HF Spaces
2. Optimize model loading
3. Add monitoring/logging
4. Write documentation

**Time Commitment**: 20-30 hours

**Success Criteria**:
- ✓ Live on HF Spaces
- ✓ <10s response time (cold)
- ✓ <2s response time (cached)
- ✓ Documentation complete

### Week 9-10: Evaluation & Iteration
**Goal**: Measure and improve

**Tasks**:
1. Run benchmarks (HumanEval, MBPP)
2. Collect user feedback
3. Optimize prompts
4. Add new templates

**Time Commitment**: 15-25 hours

**Success Criteria**:
- ✓ >60% pass@1 on HumanEval
- ✓ >4.0/5.0 user ratings
- ✓ 10+ high-quality prompt templates

---

## Code Examples to Get Started

### Example 1: Create Your First Prompt

```python
# utils/prompt_manager.py

from utils.database import db, PromptLibrary
from datetime import datetime

def create_prompt(name, description, category, template, **kwargs):
    """Create a new prompt in the library"""
    
    prompt = PromptLibrary(
        name=name,
        description=description,
        category=category,
        user_prompt_template=template,
        model_type=kwargs.get('model_type', 'gpt-4'),
        temperature=kwargs.get('temperature', 0.7),
        max_tokens=kwargs.get('max_tokens', 2048),
        tags=kwargs.get('tags', []),
        created_at=datetime.utcnow()
    )
    
    db.session.add(prompt)
    db.session.commit()
    
    return prompt.id

# Usage
prompt_id = create_prompt(
    name="Python Optimization",
    description="Optimizes Python code for performance",
    category="code_optimization",
    template="""Optimize the following Python code:

Code:
```python
{code}
```

Provide optimized version with explanation:""",
    model_type="white-rabbit-neo",
    temperature=0.5,
    tags=["python", "optimization", "performance"]
)
```

### Example 2: Execute a Prompt

```python
# utils/prompt_executor.py

from utils.database import db, ExecutionHistory
from utils.plugins.registry import registry
import time

def execute_prompt(prompt_id, input_variables):
    """Execute a prompt with given variables"""
    
    from utils.database import PromptLibrary
    
    # Get prompt
    prompt = PromptLibrary.query.get(prompt_id)
    if not prompt:
        raise ValueError(f"Prompt {prompt_id} not found")
    
    # Render template
    rendered_prompt = prompt.user_prompt_template.format(**input_variables)
    
    # Get appropriate plugin
    plugin_class = registry.get_tool(prompt.model_type)
    plugin = plugin_class()
    
    # Execute
    start_time = time.time()
    try:
        result = plugin.execute(rendered_prompt)
        execution_time = int((time.time() - start_time) * 1000)
        
        # Log execution
        history = ExecutionHistory(
            prompt_id=prompt_id,
            version_id=prompt.current_version_id,
            executed_at=datetime.utcnow(),
            input_data=input_variables,
            rendered_prompt=rendered_prompt,
            output_data=result,
            execution_time_ms=execution_time,
            model_used=prompt.model_type,
            success=True
        )
        
        db.session.add(history)
        db.session.commit()
        
        return result
        
    except Exception as e:
        # Log failure
        history = ExecutionHistory(
            prompt_id=prompt_id,
            version_id=prompt.current_version_id,
            executed_at=datetime.utcnow(),
            input_data=input_variables,
            rendered_prompt=rendered_prompt,
            error_message=str(e),
            success=False
        )
        db.session.add(history)
        db.session.commit()
        
        raise

# Usage
result = execute_prompt(
    prompt_id=1,
    input_variables={
        "code": "def sum(list):\n    total = 0\n    for i in list:\n        total += i\n    return total"
    }
)
print(result['analysis'])
```

### Example 3: Simple White Rabbit Neo Plugin

```python
# plugins/white_rabbit_plugin.py (Minimal Version)

from utils.plugins.base import AgentTool, ToolMetadata
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class WhiteRabbitNeoPlugin(AgentTool):
    metadata = ToolMetadata(
        name="WhiteRabbitNeo",
        description="Code analysis with White Rabbit Neo",
        version="1.0.0",
        tags=["llm", "code-analysis"],
    )
    
    def __init__(self):
        super().__init__()
        self.model_name = "whiterabbitneo/WhiteRabbitNeo-33B-v1"
        self.model = None
        self.tokenizer = None
    
    def execute(self, prompt: str) -> dict:
        """Execute code analysis"""
        if self.model is None:
            self._load_model()
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.7,
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "analysis": response,
            "model": self.model_name
        }
    
    def _load_model(self):
        """Load model with 4-bit quantization"""
        from transformers import BitsAndBytesConfig
        
        config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=config,
            device_map="auto"
        )
```

---

## Common Issues & Solutions

### Issue: "Model doesn't fit in GPU memory"

**Solution**: Use 4-bit quantization

```python
from transformers import BitsAndBytesConfig

config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=config,
    device_map="auto"
)
```

### Issue: "Database migration fails"

**Solution**: Check PostgreSQL vs SQLite compatibility

```python
# In migration file, use database-agnostic types
from sqlalchemy import Text, JSON

# Instead of PostgreSQL-specific JSONB
output_data = db.Column(JSON)  # Works on both

# For arrays, use JSON serialization on SQLite
tags = db.Column(JSON)  # Store as JSON array
```

### Issue: "HF Spaces times out"

**Solution**: Implement async loading

```python
import streamlit as st

@st.cache_resource
def load_model(model_name):
    """Load model once and cache"""
    return AutoModelForCausalLM.from_pretrained(model_name)

# Use in app
model = load_model("whiterabbitneo/WhiteRabbitNeo-33B-v1")
```

---

## Resources & References

### Documentation
- **Full Analysis**: See `INTEGRATION_PATH.md` for comprehensive details
- **Current Architecture**: See `CLAUDE.md` for existing system docs
- **HF Deployment**: See `HUGGINGFACE.md` for deployment guide

### Hugging Face Resources
- White Rabbit Neo: https://huggingface.co/whiterabbitneo/WhiteRabbitNeo-33B-v1
- CodeT5+: https://huggingface.co/Salesforce/codet5p-16b
- HF Spaces Docs: https://huggingface.co/docs/hub/spaces

### Datasets for Evaluation
- HumanEval: https://huggingface.co/datasets/openai_humaneval
- MBPP: https://huggingface.co/datasets/mbpp
- The Stack: https://huggingface.co/datasets/bigcode/the-stack

### Community
- HF Discord: https://hf.co/join/discord
- Transformers Forum: https://discuss.huggingface.co/

---

## Success Metrics to Track

### Week 1-2
- [ ] Database migrations succeed on PostgreSQL and SQLite
- [ ] Can create/read/update prompts via API
- [ ] Test coverage >80%

### Week 3-4
- [ ] White Rabbit Neo plugin loads and executes
- [ ] CodeT5+ plugin generates code
- [ ] Cache hit rate >50%

### Week 5-6
- [ ] Prompt library UI functional
- [ ] Can browse and edit prompts
- [ ] Execution history displays correctly

### Week 7-8
- [ ] Deployed to HF Spaces
- [ ] Response time <10s (cold)
- [ ] Response time <2s (cached)

### Week 9-10
- [ ] >60% pass@1 on HumanEval
- [ ] >4.0/5.0 user rating
- [ ] 10+ prompt templates

---

## Questions?

For detailed technical specifications, see `INTEGRATION_PATH.md`.

For implementation questions, refer to:
- Database schema: Section 4 of INTEGRATION_PATH.md
- Model integration: Section 5 of INTEGRATION_PATH.md
- Deployment: Section 6 of INTEGRATION_PATH.md
- Risk mitigation: Section 8 of INTEGRATION_PATH.md

**Ready to start? Begin with Week 1-2 tasks above!**
