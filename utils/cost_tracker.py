"""Cost tracking utilities."""

from datetime import datetime
from typing import Dict
from database.models import SessionLocal, Budget, Project, Task


class CostTracker:
    """Track and manage API costs."""
    
    # Pricing (as of Feb 2026, adjust as needed)
    PRICING = {
        "gpt-4-turbo-preview": {
            "input": 0.01 / 1000,   # per token
            "output": 0.03 / 1000,
        },
        "gpt-4-vision-preview": {
            "input": 0.01 / 1000,
            "output": 0.03 / 1000,
        },
        "gpt-3.5-turbo": {
            "input": 0.0005 / 1000,
            "output": 0.0015 / 1000,
        }
    }
    
    @staticmethod
    def calculate_openai_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for OpenAI API call."""
        if model not in CostTracker.PRICING:
            model = "gpt-4-turbo-preview"  # default
        
        pricing = CostTracker.PRICING[model]
        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])
        return round(cost, 4)
    
    @staticmethod
    def record_cost(project_id: int, task_id: int, cost: float, service: str = "openai"):
        """Record cost to database."""
        session = SessionLocal()
        try:
            # Update task cost
            task = session.query(Task).filter_by(id=task_id).first()
            if task:
                task.cost += cost
            
            # Update project cost
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                project.total_cost += cost
                if service == "openai":
                    project.openai_cost += cost
                elif service == "vercel":
                    project.vercel_cost += cost
            
            # Update monthly budget
            current_month = datetime.utcnow().strftime("%Y-%m")
            budget = session.query(Budget).filter_by(month=current_month).first()
            
            if not budget:
                from utils.config import config
                budget = Budget(
                    month=current_month,
                    total_limit=config.max_monthly_budget
                )
                session.add(budget)
            
            budget.total_spent += cost
            if service == "openai":
                budget.openai_spent += cost
            elif service == "vercel":
                budget.vercel_spent += cost
            
            # Check if budget exceeded
            if budget.total_spent >= budget.total_limit:
                budget.budget_exceeded = True
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_monthly_budget() -> Dict:
        """Get current month's budget status."""
        session = SessionLocal()
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            budget = session.query(Budget).filter_by(month=current_month).first()
            
            if not budget:
                from utils.config import config
                return {
                    "month": current_month,
                    "total_spent": 0.0,
                    "total_limit": config.max_monthly_budget,
                    "remaining": config.max_monthly_budget,
                    "percentage_used": 0.0,
                    "exceeded": False
                }
            
            return {
                "month": budget.month,
                "total_spent": budget.total_spent,
                "total_limit": budget.total_limit,
                "remaining": max(0, budget.total_limit - budget.total_spent),
                "percentage_used": (budget.total_spent / budget.total_limit * 100) if budget.total_limit > 0 else 0,
                "exceeded": budget.budget_exceeded
            }
        finally:
            session.close()
    
    @staticmethod
    def check_budget_available(required_cost: float = 0) -> bool:
        """Check if budget is available for operation."""
        budget_info = CostTracker.get_monthly_budget()
        return not budget_info["exceeded"] and budget_info["remaining"] >= required_cost
