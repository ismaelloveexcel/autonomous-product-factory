# Agent Specifications

## Base Agent

All agents inherit from `BaseAgent` which provides:

- Standard `execute()` method
- Automatic error handling and logging
- Cost tracking integration
- Health monitoring
- Task recording

```python
class BaseAgent(ABC):
    async def execute(self, project_id: int, input_data: Dict) -> Dict:
        """Override this in each agent"""
        pass
    
    async def run(self, project_id: int, input_data: Dict) -> Dict:
        """Handles error catching, logging, health tracking"""
        # Creates task record
        # Calls execute()
        # Records result
        # Updates agent health
```

---

## 1. Market Research Agent

**Purpose**: Discovers trending app ideas for youth audience

**Input**: None (or trend hints)

**Output**:
```json
{
    "app_idea": {
        "app_name": "Creative name",
        "description": "2-3 sentence description",
        "category": "education|entertainment|creativity|productivity",
        "target_age_min": 8,
        "target_age_max": 25,
        "keywords": ["keyword1", "keyword2"],
        "core_features": ["feature1", "feature2"],
        "github_search_terms": ["react", "game"],
        "value_proposition": "Why users will love this"
    },
    "cost": 0.05,
    "tokens_used": 1200
}
```

**Key Logic**:
1. Uses GPT-4 to generate app ideas based on current trends
2. Focuses on simplicity (buildable in <6 hours)
3. Ensures safety (no social features, no PII)
4. Updates project record with idea details

**Prompt Strategy**:
- Asks for JSON response
- Constrains to safe, simple apps
- Encourages educational value
- Requests GitHub search terms for code reuse

---

## 2. Viability Agent

**Purpose**: Validates safety, legality, and feasibility

**Input**: Project with idea from Market Research

**Output**:
```json
{
    "validation": {
        "viable": true,
        "safety_score": 85,
        "coppa_compliant": true,
        "age_appropriate": true,
        "issues": [],
        "recommendations": ["rec1"],
        "risk_level": "low",
        "feasibility_score": 90
    },
    "content_moderation": {
        "safe": true,
        "flagged_categories": []
    }
}
```

**Key Logic**:
1. Checks COPPA compliance (age 13+ gates)
2. Validates age-appropriate content
3. Runs OpenAI Moderation API
4. Assesses feasibility (can we build this?)
5. Marks project as FAILED if not viable

**Safety Checks**:
- ✅ COPPA compliance
- ✅ GDPR considerations
- ✅ Age-appropriate content
- ✅ No predatory patterns
- ✅ Ethical concerns
- ✅ Content moderation

---

## 3. Development Agent

**Purpose**: Builds MVP by reusing GitHub code + GPT-4 generation

**Input**: Validated project

**Output**:
```json
{
    "repo_url": "https://github.com/...",
    "code_files": {
        "package.json": "...",
        "src/App.jsx": "...",
        "index.html": "...",
        "README.md": "..."
    },
    "github_sources_used": [
        {
            "name": "repo/name",
            "url": "https://...",
            "stars": 5000,
            "topics": ["react", "game"]
        }
    ],
    "architecture": {
        "tech_stack": ["react", "vite", "tailwindcss"],
        "file_structure": ["src/App.jsx", "..."],
        "state_management": "localStorage"
    }
}
```

**Key Logic**:
1. **Search GitHub** for relevant repos (based on keywords)
2. **Generate architecture** using GPT-4 (tech stack, components)
3. **Generate code files**:
   - `package.json`
   - `index.html`
   - `src/App.jsx` (main component)
   - `README.md`
4. Create repo structure (simulated, would use GitHub API in prod)

**Code Generation Strategy**:
- Uses GitHub repos as inspiration
- GPT-4 generates clean, simple code
- Tailwind CSS for styling
- No backend (localStorage only)
- Mobile-responsive by default

---

## 4. Aesthetic Gatekeeper

**Purpose**: Reviews UI/UX quality using strict standards

**Input**: Project with generated code

**Output**:
```json
{
    "aesthetic_score": 75,
    "approved": true,
    "feedback": ["Clear hierarchy", "Good use of whitespace"],
    "issues": ["Button could be more prominent"],
    "recommendations": ["Increase CTA size by 20%"],
    "hierarchy_clear": true,
    "primary_action_obvious": true,
    "visual_noise_level": "low"
}
```

**Key Logic**:
1. Analyzes code for UI/UX quality
2. Applies STRICT standards (per UI_EXCELLENCE_STANDARD)
3. Scores 0-100:
   - ≥70: Approved
   - <70: Needs improvement
4. In production, would use GPT-4 Vision on screenshots

**Review Criteria**:
- ❌ Generic dashboards
- ❌ Multiple primary actions
- ❌ Unclear hierarchy
- ❌ Visual noise
- ✅ ONE clear action per screen
- ✅ 5-second comprehension test
- ✅ Minimal color palette
- ✅ Age-appropriate design

---

## 5. Marketing Agent

**Purpose**: Generates marketing content and launch strategy

**Input**: Approved project

**Output**:
```json
{
    "tagline": "Short catchy tagline",
    "app_store_description": "Full description...",
    "meta_title": "SEO title",
    "meta_description": "SEO description",
    "keywords_seo": ["keyword1", "keyword2"],
    "social_posts": [
        {"platform": "twitter", "text": "..."}
    ],
    "launch_strategy": {
        "target_channels": ["reddit", "youtube"],
        "key_messages": ["message1"],
        "parent_pitch": "Why parents should trust this",
        "kid_pitch": "Why kids will love this"
    }
}
```

**Key Logic**:
1. Generates age-appropriate marketing copy
2. Creates dual messaging (parents + kids)
3. SEO optimization
4. Launch strategy tailored to app category

---

## 6. Launch Agent

**Purpose**: Deploys apps to Vercel

**Input**: Project with code + marketing

**Output**:
```json
{
    "url": "https://youthapp-appname.vercel.app",
    "deployment_id": "dpl_123",
    "status": "ready"
}
```

**Key Logic**:
1. Creates GitHub repo (production)
2. Connects repo to Vercel
3. Triggers deployment
4. Updates project with URL
5. Marks status as LIVE

**Production Implementation**:
```python
# Would use Vercel API:
POST /v13/deployments
{
    "name": "project-name",
    "files": [...],
    "projectSettings": {
        "framework": "vite"
    }
}
```

---

## 7. Customer Service Agent

**Purpose**: Monitors feedback and performance, kills underperforming apps

**Input**: Live project

**Output**:
```json
{
    "feedback_analysis": {
        "overall_sentiment": "positive",
        "satisfaction_score": 78,
        "critical_issues": [],
        "feature_requests": ["request1"]
    },
    "performance_check": {
        "avg_dau_7d": 45,
        "avg_engagement_7d": 0.22,
        "meets_thresholds": true
    },
    "should_kill": false
}
```

**Key Logic**:
1. **Analyze feedback** using GPT-4 sentiment analysis
2. **Check performance metrics**:
   - DAU (Daily Active Users)
   - Engagement rate
   - Last activity timestamp
3. **Kill app if**:
   - Inactive >30 days
   - DAU <10 after 30 days live
   - Engagement rate <15%

**Monitoring Cycle**:
- Runs every 15 minutes (configurable)
- Analyzes recent feedback (last 50 entries)
- Checks 7-day average metrics
- Auto-kills zombies

---

## Agent Health Tracking

Each agent tracks:

- `total_executions`: Count of runs
- `total_successes`: Successful runs
- `total_failures`: Failed runs
- `consecutive_failures`: Current failure streak
- `is_healthy`: Boolean (false after 3+ consecutive failures)
- `avg_duration_seconds`: Average execution time
- `last_success_at`: Timestamp
- `last_failure_at`: Timestamp

**Health Alerts**:
- Unhealthy agents logged every hour
- Can trigger manual intervention
- Prevents running unhealthy agents (optional)
