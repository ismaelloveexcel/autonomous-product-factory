"""Customer Service Agent - Monitors feedback and handles issues."""

import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import openai
from database.models import (
    AgentType, SessionLocal, Project, Feedback, 
    ProjectStatus, Metric
)
from agents.base_agent import BaseAgent
from utils.config import config
from utils.cost_tracker import CostTracker


class CustomerServiceAgent(BaseAgent):
    """Monitors user feedback and app performance."""
    
    def __init__(self):
        super().__init__(AgentType.CUSTOMER_SERVICE)
        openai.api_key = config.openai_api_key
    
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Monitor and respond to feedback.
        
        Returns:
            Dict with: sentiment_summary, action_needed, recommendations
        """
        
        session = SessionLocal()
        project = session.query(Project).filter_by(id=project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Analyze recent feedback
        feedback_analysis = await self._analyze_feedback(session, project)
        
        # Check performance metrics
        performance_check = await self._check_performance(session, project)
        
        # Determine if app should be killed
        should_kill = self._should_kill_app(project, performance_check)
        
        # Update project if needed
        try:
            if should_kill:
                project.status = ProjectStatus.KILLED
                project.killed_at = datetime.utcnow()
                
                self.logger.info(
                    "app_killed",
                    project_id=project.id,
                    reason=performance_check.get("kill_reason")
                )
            
            session.commit()
        finally:
            session.close()
        
        return {
            "feedback_analysis": feedback_analysis,
            "performance_check": performance_check,
            "should_kill": should_kill,
            "action_needed": should_kill or len(feedback_analysis.get("critical_issues", [])) > 0
        }
    
    async def _analyze_feedback(self, session, project: Project) -> Dict[str, Any]:
        """Analyze user feedback using GPT-4."""
        
        # Get recent feedback
        recent_feedback = session.query(Feedback).filter_by(
            project_id=project.id
        ).order_by(Feedback.created_at.desc()).limit(50).all()
        
        if not recent_feedback:
            return {
                "total_feedback": 0,
                "sentiment_summary": "No feedback yet",
                "critical_issues": [],
                "feature_requests": []
            }
        
        # Prepare feedback for analysis
        feedback_text = "\n".join([
            f"[{fb.sentiment or 'unknown'}] {fb.feedback_text}" 
            for fb in recent_feedback if fb.feedback_text
        ])
        
        if not feedback_text:
            return {"total_feedback": 0, "sentiment_summary": "No text feedback"}
        
        prompt = f"""
Analyze this user feedback for youth app "{project.name}":

Feedback:
{feedback_text[:3000]}

Identify:
1. Overall sentiment (positive/negative/mixed)
2. Critical issues (bugs, safety concerns, confusion)
3. Feature requests
4. User satisfaction level

Respond in JSON:
{{
    "overall_sentiment": "positive|negative|mixed",
    "satisfaction_score": 0-100,
    "critical_issues": ["issue1", ...],
    "feature_requests": ["request1", ...],
    "common_complaints": ["complaint1", ...],
    "common_praise": ["praise1", ...],
    "safety_concerns": ["concern1", ...],
    "recommended_actions": ["action1", ...]
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a customer feedback analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        analysis["total_feedback"] = len(recent_feedback)
        
        return analysis
    
    async def _check_performance(self, session, project: Project) -> Dict[str, Any]:
        """Check app performance metrics."""
        
        # Get recent metrics
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        recent_metrics = session.query(Metric).filter(
            Metric.project_id == project.id,
            Metric.timestamp >= week_ago
        ).all()
        
        # Calculate average DAU
        dau_metrics = [m for m in recent_metrics if m.metric_name == "dau"]
        avg_dau = sum(m.metric_value for m in dau_metrics) / len(dau_metrics) if dau_metrics else 0
        
        # Calculate engagement rate
        engagement_metrics = [m for m in recent_metrics if m.metric_name == "engagement_rate"]
        avg_engagement = sum(m.metric_value for m in engagement_metrics) / len(engagement_metrics) if engagement_metrics else 0
        
        # Check last activity
        days_since_activity = (now - project.last_activity_at).days if project.last_activity_at else 999
        
        return {
            "avg_dau_7d": avg_dau,
            "avg_engagement_7d": avg_engagement,
            "days_since_activity": days_since_activity,
            "meets_dau_threshold": avg_dau >= config.min_dau_for_survival,
            "meets_engagement_threshold": avg_engagement >= config.min_engagement_rate,
            "is_active": days_since_activity <= config.kill_after_days_inactive
        }
    
    def _should_kill_app(self, project: Project, performance: Dict) -> bool:
        """Determine if app should be killed based on performance."""
        
        if project.status == ProjectStatus.KILLED:
            return False  # Already killed
        
        # Kill if inactive too long
        if performance["days_since_activity"] > config.kill_after_days_inactive:
            performance["kill_reason"] = f"Inactive for {performance['days_since_activity']} days"
            return True
        
        # Kill if DAU too low (after 30 days live)
        if project.deployed_at:
            days_live = (datetime.utcnow() - project.deployed_at).days
            if days_live > 30 and not performance["meets_dau_threshold"]:
                performance["kill_reason"] = f"Low DAU: {performance['avg_dau_7d']} < {config.min_dau_for_survival}"
                return True
        
        # Kill if engagement too low
        if not performance["meets_engagement_threshold"] and performance["avg_engagement_7d"] > 0:
            performance["kill_reason"] = f"Low engagement: {performance['avg_engagement_7d']:.2%} < {config.min_engagement_rate:.2%}"
            return True
        
        return False
