# API Reference

## Core Classes

### Database Models

#### Project

Represents an app project in the factory.

```python
from database.models import Project, ProjectStatus

project = Project(
    name="Math Quest",
    description="Educational math game for kids",
    category="education",
    target_age_min=8,
    target_age_max=12,
    status=ProjectStatus.IDEA
)
```

**Fields**:
- `id` (int): Primary key
- `name` (str): App name
- `description` (str): App description
- `status` (ProjectStatus): Current state
- `target_age_min` (int): Minimum age (default: 8)
- `target_age_max` (int): Maximum age (default: 25)
- `github_repo_url` (str): GitHub repository URL
- `vercel_url` (str): Deployed app URL
- `total_cost` (float): Total cost in USD
- `daily_active_users` (int): DAU count
- `engagement_rate` (float): Engagement rate (0-1)
- `aesthetic_score` (float): UI/UX score (0-100)
- `created_at` (datetime): Creation timestamp
- `deployed_at` (datetime): Deployment timestamp

**Relationships**:
- `tasks`: List of Task records
- `metrics`: List of Metric records
- `feedbacks`: List of Feedback records

---

#### Task

Records agent execution attempts.

```python
from database.models import Task, AgentType

task = Task(
    project_id=1,
    agent_type=AgentType.MARKET_RESEARCH,
    status="completed",
    input_data={"param": "value"},
    output_data={"result": "data"},
    cost=0.05
)
```

**Fields**:
- `id` (int): Primary key
- `project_id` (int): Foreign key to Project
- `agent_type` (AgentType): Which agent ran
- `status` (str): pending|running|completed|failed
- `input_data` (dict): Input parameters
- `output_data` (dict): Result data
- `error_message` (str): Error if failed
- `cost` (float): Cost in USD
- `duration_seconds` (float): Execution time

---

### Agents

#### BaseAgent

All agents inherit from this class.

```python
from agents.base_agent import BaseAgent
from database.models import AgentType

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.CUSTOM)
    
    async def execute(self, project_id: int, input_data: dict) -> dict:
        # Your logic here
        return {"result": "data"}

# Usage
agent = MyAgent()
result = await agent.run(project_id=1)

if result["success"]:
    print(result["data"])
else:
    print(result["error"])
```

**Methods**:

##### `async run(project_id, input_data=None)`

Execute agent with full error handling, logging, and health tracking.

**Parameters**:
- `project_id` (int): Project to process
- `input_data` (dict, optional): Input from previous agent

**Returns**:
```python
{
    "success": bool,
    "data": dict or None,
    "error": str or None
}
```

##### `async execute(project_id, input_data=None)` (abstract)

Override this method in your agent.

**Parameters**:
- `project_id` (int): Project to process
- `input_data` (dict, optional): Input data

**Returns**: dict with agent-specific output

---

#### MarketResearchAgent

```python
from agents import MarketResearchAgent

agent = MarketResearchAgent()
result = await agent.run(project_id=1)

# Output
{
    "success": true,
    "data": {
        "app_idea": {
            "app_name": "Math Adventure",
            "description": "...",
            "category": "education",
            "keywords": ["math", "game"],
            ...
        },
        "cost": 0.05
    }
}
```

---

#### ViabilityAgent

```python
from agents import ViabilityAgent

agent = ViabilityAgent()
result = await agent.run(project_id=1, input_data=research_result["data"])

# Output
{
    "success": true,
    "data": {
        "validation": {
            "viable": true,
            "safety_score": 85,
            "coppa_compliant": true,
            "issues": [],
            ...
        }
    }
}
```

---

#### DevelopmentAgent

```python
from agents import DevelopmentAgent

agent = DevelopmentAgent()
result = await agent.run(project_id=1)

# Output
{
    "success": true,
    "data": {
        "repo_url": "https://github.com/...",
        "code_files": {
            "src/App.jsx": "...",
            ...
        },
        "github_sources_used": [...]
    }
}
```

---

### Orchestration

#### AgentPipeline

Runs the full agent pipeline.

```python
from orchestration.pipeline import AgentPipeline

pipeline = AgentPipeline()

# Run full pipeline (idea → launch)
result = await pipeline.run_full_pipeline()

# Output
{
    "project_id": 1,
    "success": true,
    "stages": {
        "research": {...},
        "viability": {...},
        "development": {...},
        "aesthetic": {...},
        "marketing": {...},
        "launch": {...}
    },
    "deployed_url": "https://...",
    "total_cost": 2.45
}

# Monitor existing project
result = await pipeline.run_monitoring_cycle(project_id=1)
```

**Methods**:

##### `async run_full_pipeline(project_id=None)`

Execute complete pipeline from research to launch.

**Parameters**:
- `project_id` (int, optional): Existing project ID, or None to create new

**Returns**: dict with pipeline results and deployed URL

##### `async run_monitoring_cycle(project_id)`

Run customer service monitoring for a live app.

**Parameters**:
- `project_id` (int): Live project to monitor

**Returns**: dict with feedback analysis and performance check

---

### Utilities

#### CostTracker

Track and manage API costs.

```python
from utils.cost_tracker import CostTracker

# Calculate OpenAI cost
cost = CostTracker.calculate_openai_cost(
    model="gpt-4-turbo-preview",
    input_tokens=1000,
    output_tokens=500
)

# Record cost
CostTracker.record_cost(
    project_id=1,
    task_id=123,
    cost=0.05,
    service="openai"
)

# Get monthly budget
budget = CostTracker.get_monthly_budget()
# Returns: {
#     "month": "2026-02",
#     "total_spent": 45.50,
#     "total_limit": 1000.0,
#     "remaining": 954.50,
#     "percentage_used": 4.55,
#     "exceeded": false
# }

# Check if budget available
if CostTracker.check_budget_available(required_cost=10.0):
    # Proceed with operation
    pass
```

---

#### PredictiveScorer

Predict app success before building.

```python
from utils.predictive_scoring import PredictiveScorer

scorer = PredictiveScorer()
result = await scorer.score_app_idea(project_id=1)

# Output
{
    "success_score": 75,
    "confidence": 80,
    "market_saturation": "medium",
    "trend_momentum": "growing",
    "risk_factors": [
        {
            "factor": "Competition",
            "severity": "medium",
            "description": "Several similar apps exist"
        }
    ],
    "opportunities": [...],
    "recommendation": "proceed"
}
```

---

#### TrendDetector

Detect emerging trends.

```python
from utils.predictive_scoring import TrendDetector

detector = TrendDetector()
trends = await detector.detect_trending_topics(limit=5)

# Output
{
    "trends": [
        {
            "topic": "AI Art Generation",
            "target_age": "13-17",
            "momentum": "growing",
            "app_angle": "Simple AI drawing assistant",
            "estimated_interest": 85
        },
        ...
    ]
}
```

---

#### AutoHealer

Automatically fix deployed app issues.

```python
from utils.auto_healing import AutoHealer

healer = AutoHealer()

# Diagnose issue
diagnosis = await healer.diagnose_issue(
    project_id=1,
    error_report={
        "error": "TypeError: Cannot read property 'map' of undefined",
        "stack_trace": "...",
        "frequency": "50% of users"
    }
)

# Generate fix
fix = await healer.generate_fix(
    project_id=1,
    diagnosis=diagnosis,
    original_code=code
)

# Validate fix
validation = await healer.validate_fix(
    fixed_code=fix["fixed_code"],
    test_cases=fix["test_cases"]
)

if validation["valid"] and validation["confidence"] > 80:
    # Deploy fix
    pass
```

---

#### ABTestingEngine

Create and analyze A/B tests.

```python
from utils.ab_testing import ABTestingEngine

engine = ABTestingEngine()

# Generate variations
variations = await engine.generate_variations(
    project_id=1,
    variation_count=3
)

# Analyze results
analysis = await engine.analyze_test_results(
    project_id=1,
    variation_metrics=[
        {
            "variation_id": "var_1_0",
            "impressions": 1000,
            "clicks": 120,
            "engagement_time": 45.3,
            "conversion_rate": 0.12
        },
        ...
    ]
)

# Output
{
    "winner": "var_1_2",
    "confidence": 95,
    "statistical_significance": true,
    "key_insights": [
        "Minimal design performed best",
        "Bright colors reduced engagement"
    ]
}
```

---

## Configuration

### Config Class

```python
from utils.config import config

# Access configuration
print(config.openai_api_key)
print(config.max_cost_per_app)
print(config.min_dau_for_survival)

# Validate configuration
config.validate()  # Raises ValueError if required vars missing
```

**Available Settings**:

```python
# API Keys
config.openai_api_key
config.github_token
config.vercel_token

# Limits
config.max_cost_per_app         # Default: 50.0
config.max_monthly_budget        # Default: 1000.0
config.max_concurrent_builds     # Default: 3

# Scheduling
config.research_interval_hours   # Default: 6
config.health_check_interval_minutes  # Default: 15

# Safety
config.min_age_target            # Default: 8
config.max_age_target            # Default: 25
config.enable_coppa_validation   # Default: true
config.enable_content_moderation # Default: true

# Performance
config.min_dau_for_survival      # Default: 10
config.min_engagement_rate       # Default: 0.15
config.kill_after_days_inactive  # Default: 30
```

---

## Database Queries

### Common Queries

```python
from database.models import SessionLocal, Project, ProjectStatus, Task

session = SessionLocal()

# Get all live projects
live_projects = session.query(Project).filter_by(
    status=ProjectStatus.LIVE
).all()

# Get projects built today
from datetime import datetime, timedelta
today = datetime.utcnow().date()
projects_today = session.query(Project).filter(
    Project.created_at >= today
).all()

# Get failed tasks for debugging
failed_tasks = session.query(Task).filter_by(
    status="failed"
).order_by(Task.created_at.desc()).limit(10).all()

# Get top performing projects
top_projects = session.query(Project).filter(
    Project.status == ProjectStatus.LIVE,
    Project.daily_active_users > 0
).order_by(Project.daily_active_users.desc()).limit(10).all()

# Calculate total spend
from sqlalchemy import func
total_spent = session.query(func.sum(Project.total_cost)).scalar() or 0.0

session.close()
```

---

## Logging

### Structured Logging

```python
from utils.logger import get_logger

logger = get_logger("my_module")

# Log with context
logger.info(
    "event_name",
    project_id=1,
    status="completed",
    duration=45.3
)

# Log errors
logger.error(
    "operation_failed",
    project_id=1,
    error=str(e),
    exc_info=True  # Include stack trace
)

# Log warnings
logger.warning(
    "budget_threshold_reached",
    current_spend=850.0,
    limit=1000.0
)
```

**Output** (JSON):
```json
{
    "event": "event_name",
    "level": "info",
    "timestamp": "2026-02-05T10:30:00Z",
    "project_id": 1,
    "status": "completed",
    "duration": 45.3
}
```

---

## Error Handling

### Standard Error Response

All agents return consistent error format:

```python
{
    "success": false,
    "data": null,
    "error": "Detailed error message"
}
```

### Custom Exceptions

```python
class BudgetExceededException(Exception):
    """Raised when budget limit is exceeded."""
    pass

class SafetyViolationException(Exception):
    """Raised when content fails safety checks."""
    pass
```

---

## Testing

### Unit Tests

```python
import pytest
from agents import MarketResearchAgent

@pytest.mark.asyncio
async def test_market_research_agent():
    agent = MarketResearchAgent()
    result = await agent.run(project_id=1)
    
    assert result["success"] == True
    assert "app_idea" in result["data"]
    assert result["data"]["app_idea"]["app_name"] != ""
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_pipeline():
    from orchestration.pipeline import AgentPipeline
    
    pipeline = AgentPipeline()
    result = await pipeline.run_full_pipeline()
    
    assert result["success"] == True
    assert result["deployed_url"] is not None
    assert result["total_cost"] > 0
```

---

## Rate Limits

### OpenAI API
- GPT-4: ~10 requests/minute (tier dependent)
- Handle with exponential backoff

### GitHub API
- 5000 requests/hour (authenticated)
- Cache search results

### Vercel API
- 100 deployments/hour (free tier)
- Batch when possible
