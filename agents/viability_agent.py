"""Viability Agent - Validates safety and feasibility."""

import json
from typing import Dict, Any, Optional
import openai
from database.models import AgentType, SessionLocal, Project, ProjectStatus
from agents.base_agent import BaseAgent
from utils.config import config
from utils.cost_tracker import CostTracker


class ViabilityAgent(BaseAgent):
    """Validates app safety, legality, and feasibility."""
    
    def __init__(self):
        super().__init__(AgentType.VIABILITY)
        openai.api_key = config.openai_api_key
    
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate project viability.
        
        Returns:
            Dict with: viable (bool), safety_score, issues[], recommendations[]
        """
        
        session = SessionLocal()
        project = session.query(Project).filter_by(id=project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Build validation prompt
        prompt = self._build_validation_prompt(project)
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a child safety and legal compliance expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent validation
            response_format={"type": "json_object"}
        )
        
        # Track cost
        usage = response.usage
        cost = CostTracker.calculate_openai_cost(
            config.openai_model,
            usage.prompt_tokens,
            usage.completion_tokens
        )
        
        # Parse validation result
        validation = json.loads(response.choices[0].message.content)
        
        # Check content moderation if enabled
        if config.enable_content_moderation:
            moderation_result = await self._check_content_moderation(project)
            validation["content_moderation"] = moderation_result
            validation["viable"] = validation["viable"] and moderation_result["safe"]
        
        # Update project
        try:
            project.coppa_compliant = validation.get("coppa_compliant", False)
            project.content_moderation_passed = validation.get("content_moderation", {}).get("safe", False)
            
            if validation.get("viable", False):
                project.status = ProjectStatus.BUILDING
            else:
                project.status = ProjectStatus.FAILED
            
            session.commit()
        finally:
            session.close()
        
        return {
            "validation": validation,
            "cost": cost,
            "tokens_used": usage.total_tokens
        }
    
    def _build_validation_prompt(self, project: Project) -> str:
        """Build validation prompt."""
        return f"""
Validate this app idea for safety and legal compliance:

App Name: {project.name}
Description: {project.description}
Target Age: {project.target_age_min}-{project.target_age_max}
Category: {project.category}

Check for:
1. COPPA compliance (Children's Online Privacy Protection Act)
2. GDPR considerations
3. Age-appropriate content
4. Safety risks (predators, harmful content, addiction patterns)
5. Feasibility (can it be built as MVP in <6 hours?)
6. Ethical concerns

Respond in JSON:
{{
    "viable": true/false,
    "safety_score": 0-100,
    "coppa_compliant": true/false,
    "gdpr_considerations": ["consideration1", ...],
    "age_appropriate": true/false,
    "issues": ["issue1", "issue2", ...],
    "recommendations": ["rec1", "rec2", ...],
    "risk_level": "low|medium|high",
    "feasibility_score": 0-100,
    "reasoning": "Brief explanation of decision"
}}

Be strict - if there's any safety concern, mark as not viable.
"""
    
    async def _check_content_moderation(self, project: Project) -> Dict[str, Any]:
        """Use OpenAI Moderation API to check content."""
        try:
            text_to_check = f"{project.name} {project.description}"
            
            response = openai.moderations.create(input=text_to_check)
            result = response.results[0]
            
            return {
                "safe": not result.flagged,
                "categories": {cat: score for cat, score in result.category_scores.model_dump().items() if score > 0.01},
                "flagged_categories": [cat for cat, flagged in result.categories.model_dump().items() if flagged]
            }
        except Exception as e:
            self.logger.error("content_moderation_failed", error=str(e))
            return {"safe": True, "error": str(e)}  # Fail open
