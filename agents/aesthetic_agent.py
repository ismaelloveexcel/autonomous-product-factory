"""Aesthetic Gatekeeper - Reviews UI using GPT-4 Vision."""

import json
import base64
from typing import Dict, Any, Optional
import openai
from database.models import AgentType, SessionLocal, Project, ProjectStatus
from agents.base_agent import BaseAgent
from utils.config import config
from utils.cost_tracker import CostTracker


class AestheticAgent(BaseAgent):
    """Reviews and scores app aesthetics using GPT-4 Vision."""
    
    def __init__(self):
        super().__init__(AgentType.AESTHETIC)
        openai.api_key = config.openai_api_key
    
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Review app aesthetics.
        
        Returns:
            Dict with: aesthetic_score, feedback, approved, issues[]
        """
        
        session = SessionLocal()
        project = session.query(Project).filter_by(id=project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # In production, would capture screenshot of deployed preview
        # For now, we'll analyze the code structure
        code_review = await self._review_code_aesthetics(project, input_data)
        
        # If we had a screenshot, we'd use GPT-4 Vision:
        # vision_review = await self._review_visual_aesthetics(screenshot_url)
        
        aesthetic_score = code_review.get("score", 50)
        approved = aesthetic_score >= 70
        
        # Update project
        try:
            project.aesthetic_score = aesthetic_score
            
            if approved:
                project.status = ProjectStatus.MARKETING
            else:
                project.status = ProjectStatus.REVIEWING  # Needs iteration
            
            session.commit()
        finally:
            session.close()
        
        return {
            "aesthetic_score": aesthetic_score,
            "approved": approved,
            "feedback": code_review.get("feedback", []),
            "issues": code_review.get("issues", []),
            "recommendations": code_review.get("recommendations", [])
        }
    
    async def _review_code_aesthetics(self, project: Project, input_data: Dict) -> Dict[str, Any]:
        """Review code for aesthetic quality (code-based analysis)."""
        
        code_files = input_data.get("code_files", {}) if input_data else {}
        app_code = code_files.get("src/App.jsx", "")
        
        prompt = f"""
Review this React app for UI/UX quality according to STRICT standards:

App: {project.name}
Target Age: {project.target_age_min}-{project.target_age_max}

Code:
```jsx
{app_code[:2000]}  
```

STRICT UI/UX Standards:
❌ REJECT:
- Generic SaaS templates or dashboards
- Multiple primary actions competing for attention
- Unclear hierarchy (user confused what to do)
- Visual noise, excessive colors
- Template-looking design
- More than 5 seconds to understand what to do

✅ APPROVE:
- ONE clear primary action per screen
- Clear visual hierarchy: headline → action → secondary
- Minimal color palette (2-3 colors max)
- Intentional spacing and rhythm
- Icons reinforce meaning (not decoration)
- 5-second comprehension test passes
- Age-appropriate visual style

Score 0-100:
- 90-100: Exceptional, unique design
- 70-89: Good, approve with minor suggestions
- 50-69: Average/generic, needs improvement
- 0-49: Poor, reject

Respond in JSON:
{{
    "score": 0-100,
    "approved": true/false,
    "feedback": ["specific observation 1", ...],
    "issues": ["critical issue 1", ...],
    "recommendations": ["actionable suggestion 1", ...],
    "hierarchy_clear": true/false,
    "primary_action_obvious": true/false,
    "visual_noise_level": "low|medium|high",
    "age_appropriate": true/false,
    "reasoning": "Brutally honest critique"
}}

Be STRICT. No praise padding. Call out anything generic or template-like.
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a brutally honest UI/UX critic with extremely high standards."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        usage = response.usage
        cost = CostTracker.calculate_openai_cost(
            config.openai_model,
            usage.prompt_tokens,
            usage.completion_tokens
        )
        
        review = json.loads(response.choices[0].message.content)
        return review
    
    async def _review_visual_aesthetics(self, screenshot_url: str) -> Dict[str, Any]:
        """
        Review visual aesthetics using GPT-4 Vision.
        
        Note: This requires a deployed preview with screenshot capability.
        Placeholder for production implementation.
        """
        
        # Would be used in production:
        # response = openai.chat.completions.create(
        #     model=config.openai_vision_model,
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": [
        #                 {"type": "text", "text": "Review this app UI..."},
        #                 {"type": "image_url", "image_url": screenshot_url}
        #             ]
        #         }
        #     ]
        # )
        
        return {
            "note": "Visual review requires deployed preview (production feature)"
        }
