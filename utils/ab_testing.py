"""A/B testing system for app variations."""

import json
from typing import Dict, Any, List
from datetime import datetime
import openai
from database.models import SessionLocal, Project
from utils.config import config
from utils.logger import get_logger

logger = get_logger("utils.ab_testing")


class ABTestingEngine:
    """Generates and manages A/B test variations of apps."""
    
    def __init__(self):
        openai.api_key = config.openai_api_key
    
    async def generate_variations(self, project_id: int, variation_count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple UI variations for A/B testing.
        
        Args:
            project_id: Project to create variations for
            variation_count: Number of variations to generate
        
        Returns:
            List of variation definitions
        """
        
        session = SessionLocal()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            variations = []
            
            for i in range(variation_count):
                variation = await self._generate_single_variation(project, i)
                variations.append(variation)
            
            logger.info(
                "variations_generated",
                project_id=project_id,
                count=len(variations)
            )
            
            return variations
        
        finally:
            session.close()
    
    async def _generate_single_variation(self, project: Project, variation_number: int) -> Dict[str, Any]:
        """Generate a single UI variation."""
        
        strategies = [
            {
                "name": "Minimal",
                "approach": "Extreme simplicity, ONE action, no distractions"
            },
            {
                "name": "Playful",
                "approach": "Fun animations, bright colors, gamification elements"
            },
            {
                "name": "Educational",
                "approach": "Learning-focused, progress tracking, achievement system"
            },
            {
                "name": "Calm",
                "approach": "Muted colors, generous spacing, zen-like experience"
            }
        ]
        
        strategy = strategies[variation_number % len(strategies)]
        
        prompt = f"""
Create a UI variation for this app using the "{strategy['name']}" strategy:

App: {project.name}
Description: {project.description}
Target Age: {project.target_age_min}-{project.target_age_max}

Strategy: {strategy['approach']}

Generate a complete design variation including:
1. Color palette (2-3 colors)
2. Typography choices
3. Layout approach
4. Primary action presentation
5. Unique differentiators from other variations

Respond in JSON:
{{
    "variation_name": "{strategy['name']}",
    "color_palette": {{
        "primary": "#hex",
        "secondary": "#hex",
        "background": "#hex"
    }},
    "typography": {{
        "headline_font": "font name",
        "body_font": "font name",
        "headline_size": "size in rem",
        "body_size": "size in rem"
    }},
    "layout_strategy": "Description of layout approach",
    "primary_action_style": "How the main CTA is presented",
    "unique_elements": ["element1", "element2", ...],
    "target_emotion": "What feeling this evokes",
    "expected_performance": {{
        "engagement": "high|medium|low with reasoning",
        "conversion": "high|medium|low with reasoning",
        "retention": "high|medium|low with reasoning"
    }},
    "css_framework": "tailwind classes or custom CSS approach",
    "component_examples": {{
        "button": "CSS/Tailwind classes",
        "card": "CSS/Tailwind classes",
        "header": "CSS/Tailwind classes"
    }}
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a UI/UX designer specializing in A/B testing for youth apps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher creativity for variations
            response_format={"type": "json_object"}
        )
        
        variation = json.loads(response.choices[0].message.content)
        variation["variation_id"] = f"var_{project.id}_{variation_number}"
        variation["created_at"] = datetime.utcnow().isoformat()
        
        return variation
    
    async def analyze_test_results(
        self, 
        project_id: int, 
        variation_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze A/B test results and determine winner.
        
        Args:
            variation_metrics: List of metrics for each variation
                [
                    {
                        "variation_id": "var_1_0",
                        "impressions": 1000,
                        "clicks": 120,
                        "engagement_time": 45.3,
                        "conversion_rate": 0.12,
                        "bounce_rate": 0.35
                    },
                    ...
                ]
        
        Returns:
            Analysis with winning variation
        """
        
        prompt = f"""
Analyze these A/B test results:

Variations:
{json.dumps(variation_metrics, indent=2)}

Determine:
1. Which variation performed best overall?
2. Statistical significance
3. Why did it win?
4. Learnings for future designs

Respond in JSON:
{{
    "winner": "variation_id",
    "confidence": 0-100,
    "statistical_significance": true/false,
    "p_value": "0.05 or actual value",
    "performance_comparison": [
        {{
            "variation_id": "id",
            "rank": 1-N,
            "strengths": ["strength1", ...],
            "weaknesses": ["weakness1", ...]
        }},
        ...
    ],
    "key_insights": [
        "insight1",
        "insight2",
        ...
    ],
    "recommendations": [
        "Apply X from winning variation",
        "Avoid Y from losing variation",
        ...
    ],
    "next_test_ideas": [
        "Test idea 1",
        "Test idea 2",
        ...
    ]
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a data analyst specializing in A/B testing and statistical significance."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        logger.info(
            "ab_test_analyzed",
            project_id=project_id,
            winner=analysis.get("winner"),
            confidence=analysis.get("confidence")
        )
        
        return analysis


class ExperimentManager:
    """Manages experiment lifecycle for continuous optimization."""
    
    def __init__(self):
        self.logger = get_logger("utils.experiment_manager")
    
    async def design_experiment(self, hypothesis: str, project_id: int) -> Dict[str, Any]:
        """
        Design an experiment to test a hypothesis.
        
        Args:
            hypothesis: "Changing X will improve Y because Z"
            project_id: Project to experiment on
        
        Returns:
            Experiment design
        """
        
        prompt = f"""
Design an experiment to test this hypothesis:

"{hypothesis}"

Project ID: {project_id}

Create a rigorous experiment design:

Respond in JSON:
{{
    "hypothesis": "Restated clearly",
    "independent_variable": "What we're changing",
    "dependent_variable": "What we're measuring",
    "control_group": "Description of control",
    "treatment_group": "Description of treatment",
    "sample_size_needed": "Minimum users per group",
    "duration_days": "How long to run test",
    "success_metrics": ["metric1", "metric2", ...],
    "guardrail_metrics": ["metrics we must not hurt"],
    "expected_effect_size": "Predicted improvement %",
    "risks": ["risk1", "risk2", ...],
    "implementation_steps": ["step1", "step2", ...],
    "analysis_plan": "How we'll analyze results"
}}
"""
        
        openai.api_key = config.openai_api_key
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are an experiment design expert for digital products."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        
        design = json.loads(response.choices[0].message.content)
        
        self.logger.info(
            "experiment_designed",
            hypothesis=hypothesis,
            project_id=project_id
        )
        
        return design
    
    def calculate_sample_size(
        self, 
        baseline_rate: float, 
        minimum_detectable_effect: float,
        significance_level: float = 0.05,
        power: float = 0.80
    ) -> int:
        """
        Calculate required sample size for A/B test.
        
        Args:
            baseline_rate: Current conversion rate (e.g., 0.10 for 10%)
            minimum_detectable_effect: Smallest change we want to detect (e.g., 0.02 for 2pp increase)
            significance_level: Alpha (typically 0.05)
            power: Statistical power (typically 0.80)
        
        Returns:
            Required sample size per variation
        """
        
        # Simplified calculation (in production, use statsmodels)
        # This is an approximation
        
        import math
        
        z_alpha = 1.96  # for 95% confidence
        z_beta = 0.84   # for 80% power
        
        p1 = baseline_rate
        p2 = baseline_rate + minimum_detectable_effect
        p_avg = (p1 + p2) / 2
        
        numerator = (z_alpha + z_beta) ** 2 * 2 * p_avg * (1 - p_avg)
        denominator = (p2 - p1) ** 2
        
        sample_size = math.ceil(numerator / denominator)
        
        self.logger.info(
            "sample_size_calculated",
            baseline_rate=baseline_rate,
            mde=minimum_detectable_effect,
            sample_size=sample_size
        )
        
        return sample_size
