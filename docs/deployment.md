# Deployment Guide

## Quick Start (Local)

### Prerequisites

- Python 3.11+
- Git
- OpenAI API key
- GitHub personal access token
- (Optional) Vercel token

### Step 1: Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/autonomous-product-factory.git
cd autonomous-product-factory

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
# Run deployment script
chmod +x deploy.sh
./deploy.sh

# Or manually:
python -c "from database.models import init_db; init_db()"
```

### Step 4: Run Dashboard

```bash
streamlit run dashboard/app.py
```

Visit http://localhost:8501

### Step 5: Run Scheduler (Optional)

```bash
# In a separate terminal
python orchestration/scheduler.py
```

---

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t autonomous-factory .

# Run dashboard
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-... \
  -e GITHUB_TOKEN=ghp_... \
  -v $(pwd)/data:/app/data \
  autonomous-factory

# Or use docker-compose
docker-compose up -d
```

### Docker Compose Services

- **dashboard**: Streamlit UI on port 8501
- **scheduler**: Automated pipeline runner

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Production Deployment

### Option 1: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Set environment variables
railway variables set OPENAI_API_KEY=sk-...
railway variables set GITHUB_TOKEN=ghp-...

# Deploy
railway up
```

### Option 2: Render

1. Create account at render.com
2. New Web Service → Connect repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run dashboard/app.py --server.address 0.0.0.0`
   - **Environment Variables**: Add from .env.example
4. Deploy

### Option 3: DigitalOcean App Platform

```bash
# Create doctl
doctl apps create --spec app.yaml

# app.yaml:
name: autonomous-factory
services:
  - name: dashboard
    source:
      repo: https://github.com/yourusername/autonomous-product-factory
      branch: main
    run_command: streamlit run dashboard/app.py --server.address 0.0.0.0
    envs:
      - key: OPENAI_API_KEY
        value: sk-...
```

### Option 4: AWS ECS (Advanced)

```bash
# 1. Build and push to ECR
aws ecr create-repository --repository-name autonomous-factory
docker tag autonomous-factory:latest <account>.dkr.ecr.us-east-1.amazonaws.com/autonomous-factory:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/autonomous-factory:latest

# 2. Create ECS task definition
# 3. Create ECS service
# 4. Configure ALB
```

---

## Environment Variables

### Required

```bash
OPENAI_API_KEY=sk-...           # OpenAI API key
GITHUB_TOKEN=ghp_...            # GitHub personal access token
```

### Optional

```bash
VERCEL_TOKEN=...                # Vercel deployment token
DATABASE_URL=...                # Database connection string
MAX_COST_PER_APP=50.0          # Budget limit per app
MAX_MONTHLY_BUDGET=1000.0      # Total monthly budget
MAX_CONCURRENT_BUILDS=3         # Parallel builds
RESEARCH_INTERVAL_HOURS=6       # How often to generate new apps
```

See `.env.example` for full list.

---

## Database Migration (SQLite → PostgreSQL)

### Step 1: Export Data

```bash
# Backup SQLite database
sqlite3 data/factory.db .dump > backup.sql
```

### Step 2: Set up PostgreSQL

```bash
# Install PostgreSQL
# Create database
createdb autonomous_factory

# Update .env
DATABASE_URL=postgresql://user:pass@localhost:5432/autonomous_factory
```

### Step 3: Migrate

```bash
# Initialize new schema
python -c "from database.models import init_db; init_db()"

# Import data (manual or use migration script)
```

---

## Monitoring Setup

### Logs

```bash
# View logs (Docker)
docker-compose logs -f

# View logs (local)
tail -f logs/*.log
```

### Health Checks

```bash
# Dashboard health
curl http://localhost:8501/_stcore/health

# Agent health
python -c "from database.models import SessionLocal, AgentHealth; \
  session = SessionLocal(); \
  agents = session.query(AgentHealth).all(); \
  print([a.agent_type.value for a in agents if not a.is_healthy])"
```

### Cost Tracking

Access dashboard → Budget tab to view:
- Total monthly spend
- Cost per app
- Budget remaining
- Trend charts

---

## Scaling Considerations

### Horizontal Scaling

1. **Multiple Schedulers**:
   ```python
   # Use distributed lock (Redis)
   from redis import Redis
   redis = Redis()
   
   if redis.set('lock:generate_app', 1, nx=True, ex=3600):
       # Run job
       pass
   ```

2. **Task Queue**:
   ```bash
   # Replace APScheduler with Celery
   pip install celery redis
   celery -A orchestration.celery worker --loglevel=info
   ```

### Database Optimization

```python
# Add indexes
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);

# Connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(url, poolclass=QueuePool, pool_size=10)
```

### Caching

```python
# Cache GitHub search results
import redis
cache = redis.Redis()

def search_github(query):
    cached = cache.get(f"github:{query}")
    if cached:
        return json.loads(cached)
    
    result = github_api.search(query)
    cache.setex(f"github:{query}", 3600, json.dumps(result))
    return result
```

---

## Troubleshooting

### Issue: Budget Exceeded

```bash
# Reset monthly budget
python -c "from database.models import SessionLocal, Budget; \
  session = SessionLocal(); \
  budget = session.query(Budget).filter_by(month='2026-02').first(); \
  budget.budget_exceeded = False; \
  session.commit()"
```

### Issue: Agent Stuck

```bash
# Check running tasks
python -c "from database.models import SessionLocal, Task; \
  session = SessionLocal(); \
  tasks = session.query(Task).filter_by(status='running').all(); \
  print([(t.id, t.agent_type.value, t.started_at) for t in tasks])"

# Mark as failed
python -c "from database.models import SessionLocal, Task; \
  session = SessionLocal(); \
  task = session.query(Task).filter_by(id=123).first(); \
  task.status = 'failed'; \
  session.commit()"
```

### Issue: Database Locked (SQLite)

```bash
# Increase timeout
DATABASE_URL=sqlite:///data/factory.db?timeout=30.0

# Or switch to PostgreSQL (recommended for production)
```

---

## Backup Strategy

### Daily Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
sqlite3 data/factory.db .dump > backups/factory_$DATE.sql
tar -czf backups/data_$DATE.tar.gz data/

# Upload to S3
aws s3 cp backups/factory_$DATE.sql s3://bucket/backups/
```

### Restore

```bash
# Restore from backup
sqlite3 data/factory.db < backups/factory_20260205.sql
```

---

## Security Best Practices

1. **API Keys**: Never commit .env file
2. **HTTPS**: Use SSL in production
3. **Rate Limiting**: Implement request throttling
4. **Input Validation**: Sanitize all user inputs
5. **Database**: Use parameterized queries (SQLAlchemy handles this)
6. **Secrets Management**: Use environment variables or secrets manager

---

## Performance Tuning

### Database

```python
# Enable WAL mode (SQLite)
PRAGMA journal_mode=WAL;

# Increase cache size
PRAGMA cache_size=-64000;  # 64MB
```

### API Optimization

```python
# Batch GitHub API calls
def batch_search(queries):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(search_github, queries))
    return results
```

### Dashboard

```python
# Add caching to Streamlit
@st.cache_data(ttl=60)
def get_projects():
    session = SessionLocal()
    return session.query(Project).all()
```
