"""Automated scheduler for the product factory."""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database.models import SessionLocal, Project, ProjectStatus, init_db
from orchestration.pipeline import AgentPipeline
from utils.logger import get_logger
from utils.config import config
from utils.cost_tracker import CostTracker

logger = get_logger("orchestration.scheduler")


class FactoryScheduler:
    """Automated scheduler for running the product factory."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.pipeline = AgentPipeline()
    
    def start(self):
        """Start the scheduler."""
        
        # Initialize database
        init_db()
        logger.info("database_initialized")
        
        # Schedule jobs
        self._schedule_jobs()
        
        # Start scheduler
        self.scheduler.start()
        logger.info("scheduler_started")
        
        try:
            # Keep running
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            self.stop()
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("scheduler_stopped")
    
    def _schedule_jobs(self):
        """Schedule all jobs."""
        
        # Job 1: Generate new app ideas
        self.scheduler.add_job(
            self.generate_new_app,
            trigger=CronTrigger(hour=f"*/{config.research_interval_hours}"),
            id="generate_new_app",
            name="Generate New App",
            replace_existing=True
        )
        
        # Job 2: Monitor live apps
        self.scheduler.add_job(
            self.monitor_live_apps,
            trigger=CronTrigger(minute=f"*/{config.health_check_interval_minutes}"),
            id="monitor_live_apps",
            name="Monitor Live Apps",
            replace_existing=True
        )
        
        # Job 3: Check agent health
        self.scheduler.add_job(
            self.check_agent_health,
            trigger=CronTrigger(hour="*/1"),
            id="check_agent_health",
            name="Check Agent Health",
            replace_existing=True
        )
        
        logger.info("jobs_scheduled", job_count=len(self.scheduler.get_jobs()))
    
    async def generate_new_app(self):
        """Generate and launch a new app."""
        
        logger.info("job_started", job="generate_new_app")
        
        try:
            # Check budget first
            if not CostTracker.check_budget_available():
                logger.warning("budget_exceeded", job="generate_new_app")
                return
            
            # Check concurrent builds limit
            session = SessionLocal()
            try:
                building_count = session.query(Project).filter(
                    Project.status.in_([
                        ProjectStatus.RESEARCHING,
                        ProjectStatus.VALIDATING,
                        ProjectStatus.BUILDING,
                        ProjectStatus.REVIEWING,
                        ProjectStatus.MARKETING,
                        ProjectStatus.DEPLOYING
                    ])
                ).count()
                
                if building_count >= config.max_concurrent_builds:
                    logger.warning(
                        "max_concurrent_builds_reached",
                        count=building_count,
                        limit=config.max_concurrent_builds
                    )
                    return
            finally:
                session.close()
            
            # Run the pipeline
            result = await self.pipeline.run_full_pipeline()
            
            if result["success"]:
                logger.info(
                    "app_generated_successfully",
                    project_id=result["project_id"],
                    url=result.get("deployed_url"),
                    cost=result.get("total_cost")
                )
            else:
                logger.warning(
                    "app_generation_failed",
                    project_id=result["project_id"],
                    reason=result.get("error") or result.get("stopped_reason")
                )
        
        except Exception as e:
            logger.error("job_failed", job="generate_new_app", error=str(e), exc_info=True)
    
    async def monitor_live_apps(self):
        """Monitor all live apps."""
        
        logger.info("job_started", job="monitor_live_apps")
        
        try:
            session = SessionLocal()
            try:
                # Get all live apps
                live_apps = session.query(Project).filter_by(
                    status=ProjectStatus.LIVE
                ).all()
                
                logger.info("monitoring_apps", count=len(live_apps))
                
                # Monitor each app
                for project in live_apps:
                    try:
                        result = await self.pipeline.run_monitoring_cycle(project.id)
                        
                        if result["success"] and result["data"].get("should_kill"):
                            logger.info(
                                "app_killed",
                                project_id=project.id,
                                name=project.name
                            )
                    
                    except Exception as e:
                        logger.error(
                            "monitoring_failed",
                            project_id=project.id,
                            error=str(e)
                        )
            
            finally:
                session.close()
        
        except Exception as e:
            logger.error("job_failed", job="monitor_live_apps", error=str(e), exc_info=True)
    
    async def check_agent_health(self):
        """Check health of all agents."""
        
        logger.info("job_started", job="check_agent_health")
        
        try:
            from database.models import AgentHealth
            
            session = SessionLocal()
            try:
                unhealthy_agents = session.query(AgentHealth).filter_by(
                    is_healthy=False
                ).all()
                
                if unhealthy_agents:
                    logger.warning(
                        "unhealthy_agents_detected",
                        count=len(unhealthy_agents),
                        agents=[a.agent_type.value for a in unhealthy_agents]
                    )
                else:
                    logger.info("all_agents_healthy")
            
            finally:
                session.close()
        
        except Exception as e:
            logger.error("job_failed", job="check_agent_health", error=str(e), exc_info=True)


def main():
    """Main entry point."""
    scheduler = FactoryScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
