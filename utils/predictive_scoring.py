"""Predictive success scoring for app ideas before building."""

import json
from typing import Dict, Any
import openai
from database.models import SessionLocal, Project
from utils.config import config
from utils.logger import get_logger

logger = get_logger("utils.predictive_scoring")


class PredictiveScorer:
    """Predicts app success probability before building."""
    
    def __init__(self):
        openai.api_key = config.openai_api_key
    
    async def score_app_idea(self, project_id: int) -> Dict[str, Any]:
        """
        Score an app idea for predicted success.
        
        Returns:
            Dict with: success_score (0-100), risk_factors[], opportunities[], recommendation
        """
        
        session = SessionLocal()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Use GPT-4 to analyze market viability
            prompt = self._build_scoring_prompt(project)
            
            response = openai.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a startup success prediction expert with deep knowledge of youth app markets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more analytical results
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            logger.info(
                "app_idea_scored",
                project_id=project_id,
                score=result.get("success_score"),
                recommendation=result.get("recommendation")
            )
            
            return result
        
        finally:
            session.close()
    
    def _build_scoring_prompt(self, project: Project) -> str:
        """Build scoring prompt."""
        
        return f"""
Predict the success probability of this app idea:

App: {project.name}
Description: {project.description}
Category: {project.category}
Target Age: {project.target_age_min}-{project.target_age_max}
Keywords: {', '.join(project.keywords or [])}

Analyze:
1. Market saturation (how many similar apps exist?)
2. Trend momentum (is this category growing or declining?)
3. Audience alignment (does this match target age interests?)
4. Retention potential (will users come back?)
5. Viral coefficient (will users share it?)
6. Monetization difficulty (can this be profitable?)
7. Competition strength (who are we up against?)
8. Implementation risk (can we build this well?)

Respond in JSON:
{{
    "success_score": 0-100,
    "confidence": 0-100,
    "market_saturation": "low|medium|high",
    "trend_momentum": "declining|stable|growing|explosive",
    "retention_potential": 0-100,
    "viral_coefficient": 0-100,
    "risk_factors": [
        {{"factor": "name", "severity": "low|medium|high", "description": "..."}},
        ...
    ],
    "opportunities": [
        {{"opportunity": "name", "impact": "low|medium|high", "description": "..."}},
        ...
    ],
    "competitive_gaps": ["gap1", "gap2", ...],
    "recommendation": "proceed|proceed_with_caution|skip",
    "reasoning": "Detailed explanation of score",
    "alternative_angles": ["If we're skipping, suggest 2-3 alternative approaches"]
}}

Be data-driven and realistic. Don't inflate scores.
"""


class TrendDetector:
    """Detects emerging trends in youth culture."""
    
    def __init__(self):
        openai.api_key = config.openai_api_key
    
    async def detect_trending_topics(self, limit: int = 5) -> Dict[str, Any]:
        """
        Detect trending topics for youth apps.
        
        Returns:
            Dict with: trends[], trend_explanations
        """
        
        prompt = """
Identify 5 trending topics in youth culture (ages 8-25) right now that could inspire apps.

Focus on:
- Emerging interests (not mainstream yet)
- Educational angles disguised as entertainment
- Creative tools and self-expression
- Underserved niches
- Seasonal opportunities (next 3 months)

Avoid:
- Social media clones
- Anything requiring user-generated content moderation
- Fads that will die in <30 days

Respond in JSON:
{
    "trends": [
        {
            "topic": "Trend name",
            "description": "What is this trend?",
            "target_age": "8-12|13-17|18-25",
            "momentum": "emerging|growing|peaking",
            "longevity": "days|weeks|months|years",
            "app_angle": "How could this become a safe, simple app?",
            "keywords": ["keyword1", "keyword2", ...],
            "difficulty": "easy|medium|hard",
            "estimated_interest": "0-100 (how many kids would care)"
        },
        ...
    ],
    "zeitgeist": "What's the overall vibe in youth culture right now?",
    "avoid": ["Topics to avoid because they're declining or problematic"]
}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a youth culture trend analyst tracking Gen Z and Gen Alpha."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher creativity for trend detection
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        logger.info("trends_detected", trend_count=len(result.get("trends", [])))
        
        return result


class CompetitiveIntelligence:
    """Monitors competitors and market gaps."""
    
    def __init__(self):
        openai.api_key = config.openai_api_key
    
    async def analyze_competitive_landscape(self, project_id: int) -> Dict[str, Any]:
        """
        Analyze competitive landscape for an app idea.
        
        Returns:
            Dict with: competitors[], gaps[], differentiators[]
        """
        
        session = SessionLocal()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            prompt = f"""
Analyze the competitive landscape for this app:

App: {project.name}
Description: {project.description}
Category: {project.category}
Target Age: {project.target_age_min}-{project.target_age_max}

Research:
1. Who are the top 3-5 competitors? (real or likely apps)
2. What features do they have?
3. What are their weaknesses?
4. What gaps exist in the market?
5. How can we differentiate?

Respond in JSON:
{{
    "competitors": [
        {{
            "name": "Competitor name (real or hypothetical)",
            "strengths": ["strength1", ...],
            "weaknesses": ["weakness1", ...],
            "estimated_users": "scale estimate"
        }},
        ...
    ],
    "market_gaps": [
        {{"gap": "What's missing?", "opportunity": "How we can fill it"}},
        ...
    ],
    "differentiators": [
        {{"feature": "What makes us different", "value": "Why users will care"}},
        ...
    ],
    "defensibility": "How hard would it be for competitors to copy us?",
    "market_position": "blue_ocean|differentiated|crowded|red_ocean"
}}
"""
            
            response = openai.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a competitive intelligence analyst for mobile apps."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            logger.info(
                "competitive_analysis_complete",
                project_id=project_id,
                competitor_count=len(result.get("competitors", [])),
                market_position=result.get("market_position")
            )
            
            return result
        
        finally:
            session.close()
