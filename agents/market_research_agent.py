"""Market Research Agent - Discovers app ideas from trends and market gaps."""

import json
from typing import Dict, Any, Optional
import openai
from database.models import AgentType, SessionLocal, Project, ProjectStatus
from agents.base_agent import BaseAgent
from utils.config import config
from utils.cost_tracker import CostTracker


class MarketResearchAgent(BaseAgent):
    """Discovers trending app ideas for youth audience."""
    
    def __init__(self):
        super().__init__(AgentType.MARKET_RESEARCH)
        openai.api_key = config.openai_api_key
    
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Research and generate app ideas.
        
        Returns:
            Dict with: app_idea, description, keywords, category, target_age
        """
        
        # Use GPT-4 to generate app ideas based on current trends
        prompt = self._build_research_prompt()
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a youth app trend analyst specializing in ages 8-25."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.openai_temperature,
            response_format={"type": "json_object"}
        )
        
        # Track cost
        usage = response.usage
        cost = CostTracker.calculate_openai_cost(
            config.openai_model,
            usage.prompt_tokens,
            usage.completion_tokens
        )
        
        # Parse response
        idea_data = json.loads(response.choices[0].message.content)
        
        # Update project with research findings
        session = SessionLocal()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                project.name = idea_data.get("app_name", "Untitled App")
                project.description = idea_data.get("description", "")
                project.keywords = idea_data.get("keywords", [])
                project.category = idea_data.get("category", "entertainment")
                project.target_age_min = idea_data.get("target_age_min", 8)
                project.target_age_max = idea_data.get("target_age_max", 25)
                project.idea_source = "ai_market_research"
                project.status = ProjectStatus.VALIDATING
            session.commit()
        finally:
            session.close()
        
        return {
            "app_idea": idea_data,
            "cost": cost,
            "tokens_used": usage.total_tokens
        }
    
    def _build_research_prompt(self) -> str:
        """Build research prompt for GPT-4."""
        return """
Generate a unique, safe, and engaging app idea for youth (ages 8-25).

Requirements:
- Must be simple enough to build as MVP in <6 hours
- No social features (no chat, comments, friend lists)
- No personal data collection beyond basic analytics
- Educational, creative, or entertainment focused
- Must have clear value proposition
- Should leverage existing open-source code patterns

Respond in JSON format:
{
    "app_name": "Creative app name",
    "description": "2-3 sentence description",
    "category": "education|entertainment|creativity|productivity",
    "target_age_min": 8-25,
    "target_age_max": 8-25,
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "core_features": ["feature1", "feature2", "feature3"],
    "github_search_terms": ["react", "game", "etc"],
    "value_proposition": "Why users will love this"
}

Think creatively! Consider:
- Current trending topics (but evergreen appeal)
- Underserved niches in youth apps
- Educational value disguised as fun
- Accessibility and inclusivity
"""
