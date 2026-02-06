"""Launch Agent - Deploys apps to Vercel."""

import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from database.models import AgentType, SessionLocal, Project, ProjectStatus
from agents.base_agent import BaseAgent
from utils.config import config


class LaunchAgent(BaseAgent):
    """Deploys apps to Vercel and manages launch."""
    
    def __init__(self):
        super().__init__(AgentType.LAUNCH)
        self.vercel_api_base = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {config.vercel_token}",
            "Content-Type": "application/json"
        }
    
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Deploy app to Vercel.
        
        Returns:
            Dict with: deployment_url, deployment_id, status
        """
        
        session = SessionLocal()
        project = session.query(Project).filter_by(id=project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # In production, would:
        # 1. Create GitHub repo with code
        # 2. Connect repo to Vercel
        # 3. Trigger deployment
        # 4. Monitor deployment status
        
        # For now, simulate deployment
        deployment_result = await self._simulate_deployment(project, input_data)
        
        # Update project
        try:
            project.vercel_url = deployment_result["url"]
            project.vercel_deployment_id = deployment_result["deployment_id"]
            project.status = ProjectStatus.LIVE
            project.deployed_at = datetime.utcnow()
            session.commit()
        finally:
            session.close()
        
        return deployment_result
    
    async def _simulate_deployment(self, project: Project, input_data: Dict) -> Dict[str, Any]:
        """
        Simulate Vercel deployment.
        
        In production, would use Vercel API:
        https://vercel.com/docs/rest-api/endpoints
        """
        
        project_name = project.name.lower().replace(" ", "-")
        deployment_url = f"https://{config.vercel_project_prefix}{project_name}.vercel.app"
        deployment_id = f"dpl_{project.id}_{int(datetime.utcnow().timestamp())}"
        
        self.logger.info(
            "deployment_simulated",
            project_id=project.id,
            url=deployment_url,
            deployment_id=deployment_id
        )
        
        # In production, would call:
        # self._create_vercel_project(project_name)
        # self._deploy_to_vercel(project_name, code_files)
        # self._wait_for_deployment(deployment_id)
        
        return {
            "url": deployment_url,
            "deployment_id": deployment_id,
            "status": "ready",
            "simulated": True
        }
    
    async def _create_vercel_project(self, project_name: str) -> Dict[str, Any]:
        """Create Vercel project (production implementation)."""
        
        if not config.vercel_token:
            raise ValueError("VERCEL_TOKEN not configured")
        
        url = f"{self.vercel_api_base}/v9/projects"
        payload = {
            "name": project_name,
            "framework": "vite",
            "gitRepository": {
                "type": "github",
                "repo": f"{config.vercel_org_id}/{project_name}"
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    async def _deploy_to_vercel(self, project_name: str, code_files: Dict[str, str]) -> Dict[str, Any]:
        """Trigger Vercel deployment (production implementation)."""
        
        url = f"{self.vercel_api_base}/v13/deployments"
        
        # Prepare files for deployment
        files = []
        for file_path, content in code_files.items():
            files.append({
                "file": file_path,
                "data": content
            })
        
        payload = {
            "name": project_name,
            "files": files,
            "projectSettings": {
                "framework": "vite",
                "buildCommand": "npm run build",
                "outputDirectory": "dist"
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return response.json()
