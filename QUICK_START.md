# ⚡ Quick Start Guide

## 🎯 What Just Happened

Your repository has been **completely transformed** from a README-only concept into a **production-ready autonomous product factory** with:

- ✅ **7 AI agents** fully implemented and working
- ✅ **5 creative enhancements** (predictive scoring, auto-healing, A/B testing, etc.)
- ✅ **Complete dashboard** with monitoring and controls
- ✅ **Comprehensive documentation** (4 detailed guides)
- ✅ **Test suite** with CI/CD pipeline
- ✅ **Docker deployment** ready to go

---

## 🚀 Try It Right Now (3 Steps)

### Step 1: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Add your API keys to .env
OPENAI_API_KEY=sk-your-key-here
GITHUB_TOKEN=ghp-your-token-here
```

**Get API keys**:
- OpenAI: https://platform.openai.com/api-keys
- GitHub: https://github.com/settings/tokens (select `repo` and `read:packages` scopes)

### Step 2: Deploy

```bash
# One-command deployment
./deploy.sh
```

This will:
- Install all dependencies
- Initialize the database
- Run tests
- Set up directories

### Step 3: Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Then visit http://localhost:8501 and click **"🚀 Generate New App"**

---

## 📁 What's New (50+ Files Added)

### Core System
```
agents/
├── base_agent.py              # Base class for all agents
├── market_research_agent.py   # Trend discovery
├── viability_agent.py         # Safety validation
├── development_agent.py       # Code generation
├── aesthetic_agent.py         # UI/UX review
├── marketing_agent.py         # Content generation
├── launch_agent.py            # Vercel deployment
└── customer_service_agent.py  # Monitoring & kill logic
```

### Creative Enhancements 🎯
```
utils/
├── predictive_scoring.py      # ML-based idea validation
├── auto_healing.py            # Automatic bug fixing
└── ab_testing.py              # UI variation testing
```

### Infrastructure
```
database/models.py             # SQLAlchemy models
orchestration/pipeline.py      # Agent coordination
orchestration/scheduler.py     # Automated execution
dashboard/app.py               # Streamlit UI
```

### Documentation 📚
```
docs/
├── architecture.md            # System design
├── agents.md                  # Agent specifications
├── deployment.md              # Production guide
└── api.md                     # API reference
```

---

## 🎮 Usage Examples

### Example 1: Generate an App Automatically

```bash
# Start the scheduler (runs every 6 hours)
python orchestration/scheduler.py
```

It will:
1. Research trending topics
2. Generate app idea
3. Validate safety
4. Build React MVP
5. Review aesthetics
6. Generate marketing
7. Deploy to Vercel
8. Monitor performance

### Example 2: Manual Pipeline Execution

```python
import asyncio
from orchestration.pipeline import AgentPipeline

async def main():
    pipeline = AgentPipeline()
    result = await pipeline.run_full_pipeline()
    
    if result["success"]:
        print(f"✅ App deployed: {result['deployed_url']}")
        print(f"💰 Total cost: ${result['total_cost']:.2f}")
    else:
        print(f"❌ Failed: {result.get('error')}")

asyncio.run(main())
```

### Example 3: Predictive Scoring (Before Building)

```python
import asyncio
from utils.predictive_scoring import PredictiveScorer
from database.models import SessionLocal, Project

async def main():
    # Create test project
    session = SessionLocal()
    project = Project(
        name="Math Adventure",
        description="Educational math game",
        category="education",
        keywords=["math", "game", "education"]
    )
    session.add(project)
    session.commit()
    
    # Score the idea
    scorer = PredictiveScorer()
    result = await scorer.score_app_idea(project.id)
    
    print(f"Success Score: {result['success_score']}/100")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Risk Factors: {result['risk_factors']}")
    
    session.close()

asyncio.run(main())
```

### Example 4: A/B Testing

```python
import asyncio
from utils.ab_testing import ABTestingEngine

async def main():
    engine = ABTestingEngine()
    
    # Generate 3 UI variations
    variations = await engine.generate_variations(
        project_id=1,
        variation_count=3
    )
    
    for var in variations:
        print(f"\n{var['variation_name']}:")
        print(f"  Colors: {var['color_palette']}")
        print(f"  Target Emotion: {var['target_emotion']}")

asyncio.run(main())
```

---

## 🐳 Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access dashboard at http://localhost:8501

---

## 📊 Monitoring

### Check Agent Health

```python
from database.models import SessionLocal, AgentHealth

session = SessionLocal()
agents = session.query(AgentHealth).all()

for agent in agents:
    status = "✅" if agent.is_healthy else "❌"
    success_rate = (agent.total_successes / agent.total_executions * 100) if agent.total_executions > 0 else 0
    print(f"{status} {agent.agent_type.value}: {success_rate:.1f}% success rate")

session.close()
```

### Check Budget

```python
from utils.cost_tracker import CostTracker

budget = CostTracker.get_monthly_budget()
print(f"Spent: ${budget['total_spent']:.2f} / ${budget['total_limit']:.2f}")
print(f"Remaining: ${budget['remaining']:.2f}")
print(f"Usage: {budget['percentage_used']:.1f}%")
```

### View Projects

```python
from database.models import SessionLocal, Project, ProjectStatus

session = SessionLocal()

live_apps = session.query(Project).filter_by(status=ProjectStatus.LIVE).all()
print(f"\n🟢 Live Apps ({len(live_apps)}):")
for app in live_apps:
    print(f"  • {app.name} - {app.vercel_url}")
    print(f"    DAU: {app.daily_active_users}, Cost: ${app.total_cost:.2f}")

session.close()
```

---

## 🧪 Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test file
pytest tests/test_agents.py -v

# Specific test
pytest tests/test_agents.py::test_market_research_agent_success -v
```

---

## 📖 Read More

- **[README.md](README.md)** - Overview and features
- **[ANALYSIS.md](ANALYSIS.md)** - Detailed analysis and proposal
- **[ENHANCEMENTS_SUMMARY.md](ENHANCEMENTS_SUMMARY.md)** - What was built
- **[docs/architecture.md](docs/architecture.md)** - System design
- **[docs/agents.md](docs/agents.md)** - Agent details
- **[docs/deployment.md](docs/deployment.md)** - Production deployment
- **[docs/api.md](docs/api.md)** - API reference

---

## 🎯 Next Steps

1. **Test the system**: Run `./deploy.sh` and launch dashboard
2. **Generate first app**: Click "Generate New App" button
3. **Review code**: Explore the agent implementations
4. **Customize**: Adjust thresholds in `.env`
5. **Deploy to prod**: Follow `docs/deployment.md` for Railway/Render
6. **Monitor**: Track costs and performance in dashboard

---

## ⚠️ Important Notes

### Budget Protection
- Default limit: $1000/month
- Per-app limit: $50
- Adjust in `.env`: `MAX_MONTHLY_BUDGET` and `MAX_COST_PER_APP`

### Safety First
- All apps validated for COPPA compliance
- Content moderation enabled by default
- Aesthetic score must be ≥70/100
- Apps auto-killed if DAU <10 after 30 days

### API Rate Limits
- OpenAI: ~10 req/min for GPT-4 (tier dependent)
- GitHub: 5000 req/hour (authenticated)
- Vercel: 100 deploys/hour (free tier)

---

## 🐛 Troubleshooting

### Database locked?
```bash
# Increase timeout
DATABASE_URL=sqlite:///data/factory.db?timeout=30.0
```

### Agent unhealthy?
```python
# Reset health
from database.models import SessionLocal, AgentHealth, AgentType

session = SessionLocal()
health = session.query(AgentHealth).filter_by(
    agent_type=AgentType.MARKET_RESEARCH
).first()
health.is_healthy = True
health.consecutive_failures = 0
session.commit()
session.close()
```

### Budget exceeded?
```python
# Reset budget
from database.models import SessionLocal, Budget

session = SessionLocal()
budget = session.query(Budget).filter_by(month='2026-02').first()
budget.budget_exceeded = False
session.commit()
session.close()
```

---

## 🤝 Need Help?

- **Documentation**: Check `docs/` folder first
- **Issues**: Create GitHub issue
- **Discussions**: GitHub Discussions for questions

---

**You're ready to generate apps autonomously! 🚀**
