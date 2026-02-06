"""Development Agent - Builds MVPs using GitHub code reuse."""

import json
import os
from typing import Dict, Any, Optional, List
import openai
from github import Github
from database.models import AgentType, SessionLocal, Project, ProjectStatus
from agents.base_agent import BaseAgent
from utils.config import config
from utils.cost_tracker import CostTracker


class DevelopmentAgent(BaseAgent):
    """Builds app MVPs by reusing GitHub code and GPT-4 generation."""
    
    def __init__(self):
        super().__init__(AgentType.DEVELOPMENT)
        openai.api_key = config.openai_api_key
        self.github_client = Github(config.github_token)
    
    async def execute(self, project_id: int, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build app MVP.
        
        Returns:
            Dict with: repo_url, code_files, github_sources_used
        """
        
        session = SessionLocal()
        project = session.query(Project).filter_by(id=project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Step 1: Find relevant GitHub repos
        github_sources = []
        if config.github_code_reuse_enabled:
            github_sources = await self._search_github_repos(project)
        
        # Step 2: Generate code architecture
        architecture = await self._generate_architecture(project, github_sources)
        
        # Step 3: Generate actual code files
        code_files = await self._generate_code_files(project, architecture)
        
        # Step 4: Create GitHub repo (simulated - would need GitHub App in production)
        repo_url = f"https://github.com/{config.vercel_org_id or 'factory'}/{project.name.lower().replace(' ', '-')}"
        
        # Update project
        try:
            project.github_repo_url = repo_url
            project.status = ProjectStatus.REVIEWING
            session.commit()
        finally:
            session.close()
        
        return {
            "repo_url": repo_url,
            "code_files": code_files,
            "github_sources_used": github_sources,
            "architecture": architecture
        }
    
    async def _search_github_repos(self, project: Project) -> List[Dict[str, Any]]:
        """Search GitHub for relevant repos."""
        search_terms = project.keywords[:3] if project.keywords else [project.category]
        sources = []
        
        try:
            for term in search_terms:
                query = f"{term} language:javascript stars:>100"
                repos = self.github_client.search_repositories(query=query, sort="stars")
                
                for repo in repos[:config.github_search_limit]:
                    sources.append({
                        "name": repo.full_name,
                        "url": repo.html_url,
                        "stars": repo.stargazers_count,
                        "description": repo.description,
                        "topics": repo.get_topics()
                    })
                    
                    if len(sources) >= config.github_search_limit:
                        break
                
                if len(sources) >= config.github_search_limit:
                    break
        
        except Exception as e:
            self.logger.warning("github_search_failed", error=str(e))
        
        return sources
    
    async def _generate_architecture(self, project: Project, github_sources: List[Dict]) -> Dict[str, Any]:
        """Generate app architecture using GPT-4."""
        
        sources_summary = "\n".join([
            f"- {s['name']}: {s['description']}" for s in github_sources[:5]
        ]) if github_sources else "No GitHub sources found"
        
        prompt = f"""
Design the architecture for this youth app:

App: {project.name}
Description: {project.description}
Category: {project.category}
Target Age: {project.target_age_min}-{project.target_age_max}

Relevant GitHub Projects:
{sources_summary}

Requirements:
- Simple React app with Vite
- No backend (use localStorage or browser APIs)
- Mobile-responsive
- Accessible (keyboard navigation, screen reader friendly)
- Fast (<2s load time)
- Works offline where possible

Respond in JSON:
{{
    "tech_stack": ["react", "vite", "tailwindcss", ...],
    "file_structure": ["src/App.jsx", "src/components/...", ...],
    "key_components": ["ComponentName: purpose", ...],
    "state_management": "localStorage|context|none",
    "styling_approach": "tailwind|css-modules|styled-components",
    "features_breakdown": ["feature1", "feature2", ...],
    "accessibility_features": ["feature1", ...],
    "deployment_notes": "Any special Vercel config needed"
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert frontend architect specializing in youth apps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        usage = response.usage
        cost = CostTracker.calculate_openai_cost(
            config.openai_model,
            usage.prompt_tokens,
            usage.completion_tokens
        )
        
        architecture = json.loads(response.choices[0].message.content)
        return architecture
    
    async def _generate_code_files(self, project: Project, architecture: Dict) -> Dict[str, str]:
        """Generate actual code files using GPT-4."""
        
        files = {}
        
        # Generate package.json
        files["package.json"] = await self._generate_package_json(project, architecture)
        
        # Generate index.html
        files["index.html"] = await self._generate_index_html(project)
        
        # Generate main App component
        files["src/App.jsx"] = await self._generate_app_component(project, architecture)
        
        # Generate README
        files["README.md"] = await self._generate_readme(project)
        
        # Note: In production, would generate all components
        # For now, keeping it minimal to manage costs
        
        return files
    
    async def _generate_package_json(self, project: Project, architecture: Dict) -> str:
        """Generate package.json file."""
        tech_stack = architecture.get("tech_stack", ["react", "vite"])
        
        return json.dumps({
            "name": project.name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.2.0",
                "vite": "^5.0.0",
                "tailwindcss": "^3.4.0" if "tailwindcss" in tech_stack else None
            }
        }, indent=2)
    
    async def _generate_index_html(self, project: Project) -> str:
        """Generate index.html."""
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{project.description}" />
    <title>{project.name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""
    
    async def _generate_app_component(self, project: Project, architecture: Dict) -> str:
        """Generate main App component using GPT-4."""
        
        prompt = f"""
Generate a React App component for this youth app:

App: {project.name}
Description: {project.description}
Features: {', '.join(architecture.get('features_breakdown', []))}

Requirements:
- Functional React component
- Tailwind CSS for styling
- Clean, minimal UI (no generic dashboards)
- ONE primary action per screen
- 5-second comprehension test (immediately clear what to do)
- Mobile-responsive
- No complex state management (use useState)

Generate ONLY the App.jsx code, no explanations.
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert React developer. Output only code, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        code = response.choices[0].message.content
        # Remove markdown code blocks if present
        if "```" in code:
            code = code.split("```")[1]
            if code.startswith("jsx") or code.startswith("javascript"):
                code = "\n".join(code.split("\n")[1:])
        
        return code.strip()
    
    async def _generate_readme(self, project: Project) -> str:
        """Generate README."""
        return f"""# {project.name}

{project.description}

## For Ages {project.target_age_min}-{project.target_age_max}

### Features
- Safe and age-appropriate
- No personal data collection
- Works offline

### Development
```bash
npm install
npm run dev
```

### Deployment
Built and deployed automatically by Autonomous Product Factory.

---
*Generated by AI • Open Source*
"""
