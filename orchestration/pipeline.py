"""Orchestration pipeline for agent execution."""

from typing import Dict, Any, Optional
from datetime import datetime
from database.models import SessionLocal, Project, ProjectStatus
from agents import (
    MarketResearchAgent,
    ViabilityAgent,
    DevelopmentAgent,
    AestheticAgent,
    MarketingAgent,
    LaunchAgent,
    CustomerServiceAgent
)
from utils.logger import get_logger
from utils.cost_tracker import CostTracker

logger = get_logger("orchestration.pipeline")


class AgentPipeline:
    """Orchestrates the full agent pipeline for app creation."""
    
    def __init__(self):
        self.agents = {
            "research": MarketResearchAgent(),
            "viability": ViabilityAgent(),
            "development": DevelopmentAgent(),
            "aesthetic": AestheticAgent(),
            "marketing": MarketingAgent(),
            "launch": LaunchAgent(),
            "customer_service": CustomerServiceAgent()
        }
    
    async def run_full_pipeline(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the full pipeline from idea to launch.
        
        Args:
            project_id: Existing project ID, or None to create new
        
        Returns:
            Dict with pipeline results
        """
        
        # Create or get project
        if project_id is None:
            project_id = self._create_project()
        
        logger.info("pipeline_started", project_id=project_id)
        
        results = {
            "project_id": project_id,
            "stages": {},
            "success": False,
            "total_cost": 0.0
        }
        
        try:
            # Stage 1: Market Research
            logger.info("stage_started", stage="research", project_id=project_id)
            research_result = await self.agents["research"].run(project_id)
            results["stages"]["research"] = research_result
            
            if not research_result["success"]:
                raise Exception(f"Research failed: {research_result['error']}")
            
            # Stage 2: Viability Check
            logger.info("stage_started", stage="viability", project_id=project_id)
            viability_result = await self.agents["viability"].run(
                project_id, 
                research_result["data"]
            )
            results["stages"]["viability"] = viability_result
            
            if not viability_result["success"]:
                raise Exception(f"Viability check failed: {viability_result['error']}")
            
            if not viability_result["data"]["validation"].get("viable", False):
                logger.warning("project_not_viable", project_id=project_id)
                results["stopped_reason"] = "Not viable"
                return results
            
            # Stage 3: Development
            logger.info("stage_started", stage="development", project_id=project_id)
            dev_result = await self.agents["development"].run(
                project_id,
                viability_result["data"]
            )
            results["stages"]["development"] = dev_result
            
            if not dev_result["success"]:
                raise Exception(f"Development failed: {dev_result['error']}")
            
            # Stage 4: Aesthetic Review
            logger.info("stage_started", stage="aesthetic", project_id=project_id)
            aesthetic_result = await self.agents["aesthetic"].run(
                project_id,
                dev_result["data"]
            )
            results["stages"]["aesthetic"] = aesthetic_result
            
            if not aesthetic_result["success"]:
                raise Exception(f"Aesthetic review failed: {aesthetic_result['error']}")
            
            # If aesthetic score too low, could iterate here
            if not aesthetic_result["data"].get("approved", False):
                logger.warning("aesthetic_rejected", project_id=project_id)
                results["stopped_reason"] = "Aesthetic score too low"
                # In production, could trigger iteration
                return results
            
            # Stage 5: Marketing
            logger.info("stage_started", stage="marketing", project_id=project_id)
            marketing_result = await self.agents["marketing"].run(
                project_id,
                aesthetic_result["data"]
            )
            results["stages"]["marketing"] = marketing_result
            
            if not marketing_result["success"]:
                raise Exception(f"Marketing failed: {marketing_result['error']}")
            
            # Stage 6: Launch
            logger.info("stage_started", stage="launch", project_id=project_id)
            launch_result = await self.agents["launch"].run(
                project_id,
                {**dev_result["data"], **marketing_result["data"]}
            )
            results["stages"]["launch"] = launch_result
            
            if not launch_result["success"]:
                raise Exception(f"Launch failed: {launch_result['error']}")
            
            # Success!
            results["success"] = True
            results["deployed_url"] = launch_result["data"].get("url")
            
            logger.info(
                "pipeline_completed",
                project_id=project_id,
                url=results["deployed_url"]
            )
            
        except Exception as e:
            logger.error("pipeline_failed", project_id=project_id, error=str(e), exc_info=True)
            results["error"] = str(e)
            results["success"] = False
        
        # Calculate total cost
        session = SessionLocal()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                results["total_cost"] = project.total_cost
        finally:
            session.close()
        
        return results
    
    async def run_monitoring_cycle(self, project_id: int) -> Dict[str, Any]:
        """
        Run monitoring cycle for a live app.
        
        Should be called periodically for live projects.
        """
        
        logger.info("monitoring_started", project_id=project_id)
        
        result = await self.agents["customer_service"].run(project_id)
        
        if result["success"]:
            data = result["data"]
            if data.get("should_kill", False):
                logger.warning("app_killed_by_monitoring", project_id=project_id)
        
        return result
    
    def _create_project(self) -> int:
        """Create a new project."""
        session = SessionLocal()
        try:
            project = Project(
                name="New App Idea",
                description="",
                status=ProjectStatus.IDEA
            )
            session.add(project)
            session.commit()
            return project.id
        finally:
            session.close()
