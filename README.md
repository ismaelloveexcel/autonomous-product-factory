# 🏭 Autonomous Product Factory

**Production-ready multi-agent system for discovering, building, and launching youth-focused apps (ages 8-25) with minimal human oversight.**

[![Tests](https://github.com/ismaelloveexcel/autonomous-product-factory/workflows/CI/badge.svg)](https://github.com/ismaelloveexcel/autonomous-product-factory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 What This Does

Transforms app ideas into deployed products automatically:

1. **🔍 Discovers** trending app ideas using AI market research
2. **✅ Validates** safety (COPPA/GDPR) and feasibility 
3. **⚡ Builds** MVPs by reusing GitHub code + GPT-4 generation
4. **🎨 Reviews** UI/UX quality with strict aesthetic standards
5. **📣 Markets** with AI-generated content and launch strategy
6. **🚢 Deploys** to Vercel automatically
7. **📊 Monitors** performance and kills underperforming apps

**Zero to deployed app in <6 hours, fully automated.**

---

## ✨ Key Features

### Core System
- ✅ **7 Specialized Agents**: Market Research, Viability, Development, Aesthetic, Marketing, Launch, Customer Service
- ✅ **Real Integrations**: GitHub API, OpenAI GPT-4/Vision, Vercel deployment
- ✅ **State Persistence**: SQLAlchemy (SQLite/PostgreSQL)
- ✅ **Cost Tracking**: Real-time budget monitoring with circuit breakers
- ✅ **Health Monitoring**: Agent performance tracking and auto-recovery
- ✅ **Automated Scheduler**: APScheduler-based pipeline orchestration

### Safety & Compliance
- ✅ **COPPA Validation**: Age-appropriate content checks
- ✅ **Content Moderation**: OpenAI Moderation API integration
- ✅ **Privacy-First**: No social features, minimal data collection
- ✅ **Aesthetic Enforcement**: Strict UI/UX standards (no generic dashboards)

### 🎯 Creative Enhancements
- 🔮 **Predictive Success Scoring**: ML-based idea validation before building
- 🔧 **Auto-Healing System**: Detects and fixes deployed app issues automatically
- 📊 **A/B Testing Engine**: Generates and analyzes UI variations
- 📈 **Trend Detection**: Real-time youth culture trend monitoring
- 🎯 **Competitive Intelligence**: Market gap analysis and differentiation

---

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key ([get one](https://platform.openai.com/api-keys))
- GitHub personal access token ([create](https://github.com/settings/tokens))

### Installation

```bash
# 1. Clone repository
git clone https://github.com/ismaelloveexcel/autonomous-product-factory.git
cd autonomous-product-factory

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, GITHUB_TOKEN)

# 3. Run deployment script
./deploy.sh

# 4. Launch dashboard
streamlit run dashboard/app.py
```

Visit http://localhost:8501 and click **"🚀 Generate New App"**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                         │
│          Pipeline Coordinator + Scheduler (APScheduler)          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AGENT LAYER                              │
│  Market Research → Viability → Development → Aesthetic          │
│       ↓                                          ↓               │
│  Marketing → Launch → Customer Service                          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                            │
│     OpenAI GPT-4/Vision  │  GitHub API  │  Vercel API           │
└─────────────────────────────────────────────────────────────────┘
```

### Pipeline Flow

```python
IDEA → Research → Validate → Build → Review → Market → Deploy → Monitor
                     ↓                                              ↓
                  FAILED                                         KILLED
```

**Each app goes through**:
1. Market research discovers trending idea
2. Viability validates safety + feasibility
3. Development builds React MVP
4. Aesthetic scores UI/UX (must be ≥70/100)
5. Marketing generates content
6. Launch deploys to Vercel
7. Customer service monitors and kills if underperforming

---

## 📖 Documentation

- **[Architecture Overview](docs/architecture.md)** - System design and patterns
- **[Agent Specifications](docs/agents.md)** - Detailed agent documentation
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[API Reference](docs/api.md)** - Complete API documentation
- **[Analysis Report](ANALYSIS.md)** - Repository analysis and enhancement proposal

---

## 🎨 Dashboard

**Simple, purposeful UI (following strict UX standards):**

- **Home**: ONE primary action - "Generate New App" button
- **Projects**: Visual timeline of all apps (Live, Building, Killed)
- **Agents**: Real-time health status of all 7 agents
- **Costs**: Budget tracking with alerts

No generic SaaS templates. Every screen has ONE clear action.

---

## 🔧 Configuration

Key settings in `.env`:

```bash
# Required
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...

# Budget Limits
MAX_COST_PER_APP=50.0           # Max spend per app
MAX_MONTHLY_BUDGET=1000.0       # Total monthly limit

# Performance Thresholds
MIN_DAU_FOR_SURVIVAL=10         # Minimum daily active users
MIN_ENGAGEMENT_RATE=0.15        # Minimum engagement (15%)
KILL_AFTER_DAYS_INACTIVE=30     # Auto-kill after X days

# Scheduling
RESEARCH_INTERVAL_HOURS=6       # Generate new app every 6 hours
```

See [.env.example](.env.example) for full configuration.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_agents.py::test_market_research_agent_success
```

---

## 🐳 Docker Deployment

```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or build manually
docker build -t autonomous-factory .
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-... \
  -e GITHUB_TOKEN=ghp_... \
  autonomous-factory
```

---

## 📊 Monitoring

### Agent Health
Dashboard shows real-time agent health:
- ✅ Healthy (success rate >70%)
- ❌ Unhealthy (3+ consecutive failures)

### Cost Tracking
- Real-time budget usage
- Per-project cost breakdown
- Automatic circuit breaker at budget limit

### Performance Metrics
- Daily Active Users (DAU)
- Engagement rate
- Survival rate (% apps still live after 30 days)

---

## 🛡️ Safety & Compliance

**Built-in safeguards**:
- ✅ COPPA compliance checks (age 13+ gates)
- ✅ OpenAI content moderation
- ✅ No social features allowed
- ✅ No personal data collection
- ✅ Guest mode preferred
- ✅ Age-appropriate content validation

**Apps are rejected if**:
- Safety score <70/100
- Content moderation fails
- COPPA non-compliant
- Feasibility score <50/100

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Automation Rate | >70% (apps launched without human intervention) |
| Time-to-Launch | <6 hours (idea → deployed) |
| Survival Rate | >40% (apps live after 30 days) |
| Cost per App | <$50 |
| DAU/MAU Ratio | >20% |

---

## 🚀 Advanced Features

### Predictive Scoring
```python
from utils.predictive_scoring import PredictiveScorer

scorer = PredictiveScorer()
score = await scorer.score_app_idea(project_id=1)
# Returns success probability, risk factors, market gaps
```

### Auto-Healing
```python
from utils.auto_healing import AutoHealer

healer = AutoHealer()
diagnosis = await healer.diagnose_issue(project_id=1, error_report)
fix = await healer.generate_fix(project_id=1, diagnosis, code)
# Automatically fixes deployed app issues
```

### A/B Testing
```python
from utils.ab_testing import ABTestingEngine

engine = ABTestingEngine()
variations = await engine.generate_variations(project_id=1, count=3)
# Generates multiple UI variations for testing
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 and GPT-4 Vision
- GitHub for code search API
- Vercel for deployment platform
- Streamlit for rapid dashboard development

---

## 📧 Support

- **Documentation**: See `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/ismaelloveexcel/autonomous-product-factory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ismaelloveexcel/autonomous-product-factory/discussions)

---

**Built with ❤️ for the next generation of young creators**
