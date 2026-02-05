"""Base agent class for all factory agents."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from database.models import SessionLocal, Task, AgentType, AgentHealth
from utils.logger import get_logger
from utils.cost_tracker import CostTracker


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = get_logger(f"agent.{agent_type.value}")
    
    @abstractmethod
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute agent logic.
        
        Args:
            project_id: ID of the project to process
            input_data: Input data from previous agent (optional)
        
        Returns:
            Dict containing output data and status
        """
        pass
    
    async def run(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run agent with error handling, logging, and health tracking.
        
        Returns:
            Dict with keys: success (bool), data (dict), error (str)
        """
        session = SessionLocal()
        task = None
        
        try:
            # Create task record
            task = Task(
                project_id=project_id,
                agent_type=self.agent_type,
                status="running",
                input_data=input_data,
                started_at=datetime.utcnow()
            )
            session.add(task)
            session.commit()
            
            self.logger.info(
                "agent_started",
                agent=self.agent_type.value,
                project_id=project_id,
                task_id=task.id
            )
            
            # Execute agent logic
            start_time = datetime.utcnow()
            result = await self.execute(project_id, input_data)
            end_time = datetime.utcnow()
            
            # Update task record
            task.status = "completed"
            task.output_data = result
            task.completed_at = end_time
            task.duration_seconds = (end_time - start_time).total_seconds()
            
            # Update agent health
            self._update_health(session, success=True, duration=task.duration_seconds)
            
            session.commit()
            
            self.logger.info(
                "agent_completed",
                agent=self.agent_type.value,
                project_id=project_id,
                task_id=task.id,
                duration=task.duration_seconds
            )
            
            return {
                "success": True,
                "data": result,
                "error": None
            }
            
        except Exception as e:
            error_msg = str(e)
            
            if task:
                task.status = "failed"
                task.error_message = error_msg
                task.completed_at = datetime.utcnow()
            
            self._update_health(session, success=False, error=error_msg)
            
            session.commit()
            
            self.logger.error(
                "agent_failed",
                agent=self.agent_type.value,
                project_id=project_id,
                error=error_msg,
                exc_info=True
            )
            
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
        
        finally:
            session.close()
    
    def _update_health(self, session, success: bool, duration: float = 0.0, error: str = None):
        """Update agent health metrics."""
        health = session.query(AgentHealth).filter_by(agent_type=self.agent_type).first()
        
        if not health:
            health = AgentHealth(agent_type=self.agent_type)
            session.add(health)
        
        health.total_executions += 1
        
        if success:
            health.total_successes += 1
            health.last_success_at = datetime.utcnow()
            health.consecutive_failures = 0
            health.is_healthy = True
            
            # Update average duration
            if health.avg_duration_seconds == 0:
                health.avg_duration_seconds = duration
            else:
                health.avg_duration_seconds = (health.avg_duration_seconds * 0.9) + (duration * 0.1)
        else:
            health.total_failures += 1
            health.last_failure_at = datetime.utcnow()
            health.consecutive_failures += 1
            health.last_error = error
            
            # Mark unhealthy after 3 consecutive failures
            if health.consecutive_failures >= 3:
                health.is_healthy = False
        
        health.updated_at = datetime.utcnow()
    
    def record_cost(self, task_id: int, project_id: int, cost: float, service: str = "openai"):
        """Helper to record cost."""
        CostTracker.record_cost(project_id, task_id, cost, service)
