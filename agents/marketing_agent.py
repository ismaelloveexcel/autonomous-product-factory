"""Marketing Agent - Generates marketing content."""

import json
from typing import Dict, Any, Optional
import openai
from database.models import AgentType, SessionLocal, Project, ProjectStatus
from agents.base_agent import BaseAgent
from utils.config import config
from utils.cost_tracker import CostTracker


class MarketingAgent(BaseAgent):
    """Generates marketing content and launch strategy."""
    
    def __init__(self):
        super().__init__(AgentType.MARKETING)
        openai.api_key = config.openai_api_key
    
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate marketing materials.
        
        Returns:
            Dict with: tagline, description, meta_tags, launch_strategy
        """
        
        session = SessionLocal()
        project = session.query(Project).filter_by(id=project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Generate marketing content
        marketing_content = await self._generate_marketing_content(project)
        
        # Update project status
        try:
            project.status = ProjectStatus.DEPLOYING
            session.commit()
        finally:
            session.close()
        
        return marketing_content
    
    async def _generate_marketing_content(self, project: Project) -> Dict[str, Any]:
        """Generate marketing materials using GPT-4."""
        
        prompt = f"""
Create marketing content for this youth app:

App: {project.name}
Description: {project.description}
Category: {project.category}
Target Age: {project.target_age_min}-{project.target_age_max}

Generate:
1. Catchy tagline (5-8 words)
2. App store description (100-150 words)
3. Meta tags for SEO
4. Social media post suggestions
5. Launch strategy

Focus on:
- Age-appropriate language
- Safety and trust (for parents)
- Fun and value (for kids/teens)
- No hype or misleading claims

Respond in JSON:
{{
    "tagline": "Short catchy tagline",
    "app_store_description": "Full description...",
    "meta_title": "SEO title",
    "meta_description": "SEO description",
    "keywords_seo": ["keyword1", ...],
    "social_posts": [
        {{"platform": "twitter", "text": "..."}},
        {{"platform": "instagram", "text": "..."}}
    ],
    "launch_strategy": {{
        "target_channels": ["reddit", "youtube", ...],
        "key_messages": ["message1", ...],
        "parent_pitch": "Why parents should trust this",
        "kid_pitch": "Why kids will love this"
    }},
    "unique_value_prop": "What makes this different"
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a youth marketing expert who understands both parents and kids."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        usage = response.usage
        cost = CostTracker.calculate_openai_cost(
            config.openai_model,
            usage.prompt_tokens,
            usage.completion_tokens
        )
        
        marketing = json.loads(response.choices[0].message.content)
        marketing["cost"] = cost
        
        return marketing
