# 🏭 Autonomous Product Factory

Multi-agent system for discovering, building, and launching youth-focused apps (ages 8-25) with minimal human oversight.

## Overview

This system automates the entire product lifecycle:
- **Discover** app ideas through market research
- **Validate** with safety and viability checks
- **Build** MVPs by reusing GitHub code
- **Review** aesthetics with GPT-4 Vision
- **Launch** with automated deployment
- **Monitor** and kill based on performance signals

## Key Features

✅ Real GitHub API integration for code reuse
✅ GPT-4 Vision for aesthetic enforcement
✅ Automated Vercel deployment
✅ State persistence (SQLite + JSON)
✅ Cost tracking per app
✅ Age safety validation (COPPA-aware)
✅ Feedback webhook system
✅ Automated scheduler
✅ Agent health monitoring
✅ Portfolio decision engine

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/ismaelloveexcel/autonomous-product-factory.git
cd autonomous-product-factory

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Run dashboard
streamlit run dashboard/app.py

# 5. Start scheduler (optional)
python orchestration/scheduler.py
```

## Architecture

```
Market Research Agent → Viability Agent → Development Agent → Aesthetic Gatekeeper → Marketing Agent → Launch → Customer Service Agent
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Agent Specifications](docs/agents.md)
- [Deployment Guide](docs/deployment.md)
- [API Reference](docs/api.md)

## Safety First

- No social features
- No personal data collection
- Guest mode preferred
- COPPA/GDPR aware
- Age-appropriate content validation

## License

MIT License - See LICENSE file for details
