# Architecture Overview

## System Design

The Autonomous Product Factory is a multi-agent system that automates the entire app lifecycle from idea discovery to deployment and monitoring.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                          │
│  ┌──────────────────┐              ┌─────────────────┐             │
│  │  Pipeline        │              │   Scheduler     │             │
│  │  Coordinator     │◄────────────►│   (APScheduler) │             │
│  └──────────────────┘              └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           AGENT LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Market   │─►│ Viability│─►│  Develop │─►│ Aesthetic│           │
│  │ Research │  │  Agent   │  │  Agent   │  │ Gateway  │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│       │                                           │                 │
│       ▼                                           ▼                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                         │
│  │Marketing │─►│  Launch  │─►│ Customer │                         │
│  │  Agent   │  │  Agent   │  │ Service  │                         │
│  └──────────┘  └──────────┘  └──────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         INTEGRATION LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ OpenAI   │  │ GitHub   │  │  Vercel  │  │ Webhooks │           │
│  │   API    │  │   API    │  │   API    │  │          │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                  │
│  ┌──────────────────────────────────────────────────────┐           │
│  │  SQLite/PostgreSQL Database                          │           │
│  │  - Projects  - Tasks  - Metrics  - Feedback         │           │
│  │  - Agent Health  - Budgets                          │           │
│  └──────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent Pipeline

Each app goes through this pipeline:

1. **Market Research Agent** → Discovers trending app ideas
2. **Viability Agent** → Validates safety and feasibility
3. **Development Agent** → Builds MVP using GitHub code reuse
4. **Aesthetic Gatekeeper** → Reviews UI/UX quality (GPT-4 Vision)
5. **Marketing Agent** → Generates content and launch strategy
6. **Launch Agent** → Deploys to Vercel
7. **Customer Service Agent** → Monitors feedback and performance

## Data Flow

```python
# 1. New project created
project = Project(status=IDEA)

# 2. Market Research
research_result = MarketResearchAgent.run(project.id)
# → Updates project with name, description, keywords

# 3. Viability Check
viability_result = ViabilityAgent.run(project.id, research_result)
# → Runs safety checks (COPPA, content moderation)
# → Either advances to BUILDING or marks as FAILED

# 4. Development
dev_result = DevelopmentAgent.run(project.id, viability_result)
# → Searches GitHub for reusable code
# → Generates React app with GPT-4
# → Creates repo structure

# 5. Aesthetic Review
aesthetic_result = AestheticAgent.run(project.id, dev_result)
# → Reviews code for UI/UX quality
# → Scores 0-100, must be ≥70 to proceed

# 6. Marketing
marketing_result = MarketingAgent.run(project.id, aesthetic_result)
# → Generates tagline, description, meta tags

# 7. Launch
launch_result = LaunchAgent.run(project.id, {dev_result, marketing_result})
# → Deploys to Vercel
# → Sets status to LIVE

# 8. Monitoring (periodic)
CustomerServiceAgent.run(project.id)
# → Analyzes feedback
# → Checks performance metrics
# → Kills app if underperforming
```

## State Machine

```
IDEA → RESEARCHING → VALIDATING → BUILDING → REVIEWING → MARKETING → DEPLOYING → LIVE
                         ↓                                                           ↓
                      FAILED                                                     KILLED
```

## Technology Stack

- **Backend**: Python 3.11+
- **Framework**: Async/await with asyncio
- **Database**: SQLAlchemy ORM (SQLite dev, PostgreSQL prod)
- **Orchestration**: APScheduler (async scheduler)
- **Dashboard**: Streamlit
- **LLM**: OpenAI GPT-4 + GPT-4 Vision
- **Code Reuse**: GitHub API (PyGithub)
- **Deployment**: Vercel API
- **Logging**: Structlog (JSON structured logging)
- **Monitoring**: Custom health checks + cost tracking

## Design Patterns

### 1. Agent Pattern
- Each agent is stateless
- Communicates via database (event sourcing)
- Inherits from `BaseAgent` with standard `execute()` method

### 2. Repository Pattern
- Database access abstracted through SQLAlchemy models
- Session management via context managers

### 3. Circuit Breaker
- Agents track health (consecutive failures)
- Marked unhealthy after 3 failures
- Prevents cascading failures

### 4. Cost Tracking
- Every API call records cost
- Budget limits enforced at monthly level
- Circuit breaker on budget exceeded

### 5. Task Queue (Implicit)
- Scheduler manages task timing
- Database tracks task state
- Retry logic in agents

## Scalability Considerations

### Current Architecture (MVP)
- Single process
- SQLite database
- Suitable for 1-10 apps/day

### Production Scale
- **Horizontal scaling**: Multiple scheduler instances
- **Database**: PostgreSQL with connection pooling
- **Queue**: Redis + Celery for task distribution
- **Caching**: Redis for API response caching
- **Monitoring**: Prometheus + Grafana
- **Logging**: Centralized (ELK stack or DataDog)

## Security

- API keys stored in environment variables
- No hardcoded secrets
- Content moderation via OpenAI Moderation API
- COPPA compliance checks
- No personal data storage (apps are guest-mode)

## Monitoring

- **Agent Health**: Tracks success/failure rates
- **Cost Tracking**: Real-time cost per project
- **Performance Metrics**: DAU, engagement rate, survival rate
- **Alerts**: Budget exceeded, unhealthy agents

## Error Handling

- All agents wrapped in try/except
- Errors logged with full context
- Failed tasks recorded in database
- No silent failures
- Exponential backoff on retries
