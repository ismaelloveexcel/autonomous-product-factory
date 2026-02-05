"""Auto-healing system for deployed apps."""

import json
from typing import Dict, Any, Optional, List
import openai
from database.models import SessionLocal, Project
from utils.config import config
from utils.logger import get_logger

logger = get_logger("utils.auto_healing")


class AutoHealer:
    """Automatically detects and fixes issues in deployed apps."""
    
    def __init__(self):
        openai.api_key = config.openai_api_key
    
    async def diagnose_issue(self, project_id: int, error_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose an issue in a deployed app.
        
        Args:
            project_id: Project ID
            error_report: Dict with error details (stack trace, user reports, etc.)
        
        Returns:
            Dict with: diagnosis, severity, suggested_fix, auto_fixable
        """
        
        session = SessionLocal()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            prompt = self._build_diagnosis_prompt(project, error_report)
            
            response = openai.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert frontend debugger specializing in React apps."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Very low for precise debugging
                response_format={"type": "json_object"}
            )
            
            diagnosis = json.loads(response.choices[0].message.content)
            
            logger.info(
                "issue_diagnosed",
                project_id=project_id,
                severity=diagnosis.get("severity"),
                auto_fixable=diagnosis.get("auto_fixable")
            )
            
            return diagnosis
        
        finally:
            session.close()
    
    async def generate_fix(self, project_id: int, diagnosis: Dict[str, Any], original_code: str) -> Dict[str, Any]:
        """
        Generate a fix for diagnosed issue.
        
        Returns:
            Dict with: fixed_code, changes_made[], test_cases[]
        """
        
        prompt = f"""
Fix this React code issue:

Diagnosis: {diagnosis.get('diagnosis')}
Root Cause: {diagnosis.get('root_cause')}
Suggested Fix: {diagnosis.get('suggested_fix')}

Original Code:
```jsx
{original_code[:3000]}
```

Requirements:
- Fix ONLY the identified issue
- Don't refactor unrelated code
- Maintain original functionality
- Add defensive checks to prevent regression
- Keep code style consistent

Respond in JSON:
{{
    "fixed_code": "Complete fixed code",
    "changes_made": ["change1", "change2", ...],
    "explanation": "Why this fixes the issue",
    "test_cases": [
        {{"scenario": "test case", "expected": "expected result"}},
        ...
    ],
    "risk_level": "low|medium|high",
    "rollback_needed": "true|false"
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert code fixer. Output working, tested code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        fix = json.loads(response.choices[0].message.content)
        
        logger.info(
            "fix_generated",
            project_id=project_id,
            changes_count=len(fix.get("changes_made", [])),
            risk_level=fix.get("risk_level")
        )
        
        return fix
    
    async def validate_fix(self, fixed_code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """
        Validate that fix actually works.
        
        Returns:
            Dict with: valid, test_results[], confidence
        """
        
        # In production, would:
        # 1. Deploy to staging environment
        # 2. Run automated tests
        # 3. Simulate user interactions
        # 4. Check for regressions
        
        # For now, use GPT-4 to validate
        prompt = f"""
Validate this fixed code:

Code:
```jsx
{fixed_code[:2000]}
```

Test Cases:
{json.dumps(test_cases, indent=2)}

Check for:
1. Syntax errors
2. Logic errors
3. Edge cases not handled
4. Potential regressions
5. Performance issues

Respond in JSON:
{{
    "valid": true/false,
    "confidence": 0-100,
    "test_results": [
        {{"test": "test name", "passed": true/false, "notes": "..."}},
        ...
    ],
    "concerns": ["concern1", ...],
    "recommendation": "deploy|needs_revision|manual_review"
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a code reviewer focused on correctness and safety."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        validation = json.loads(response.choices[0].message.content)
        
        logger.info(
            "fix_validated",
            valid=validation.get("valid"),
            confidence=validation.get("confidence")
        )
        
        return validation
    
    def _build_diagnosis_prompt(self, project: Project, error_report: Dict) -> str:
        """Build diagnosis prompt."""
        
        return f"""
Diagnose this issue in a youth app:

App: {project.name}
Category: {project.category}

Error Report:
{json.dumps(error_report, indent=2)}

Analyze:
1. What is the root cause?
2. How severe is this? (affects how many users?)
3. Can this be auto-fixed with high confidence?
4. What's the quickest fix?

Respond in JSON:
{{
    "diagnosis": "Brief description of the problem",
    "root_cause": "Technical root cause",
    "severity": "critical|high|medium|low",
    "user_impact": "How many users affected and how?",
    "auto_fixable": true/false,
    "suggested_fix": "Specific fix to apply",
    "alternative_fixes": ["fix1", "fix2", ...],
    "requires_manual_review": true/false,
    "urgency": "immediate|high|medium|low"
}}
"""


class PerformanceOptimizer:
    """Automatically optimizes app performance."""
    
    def __init__(self):
        openai.api_key = config.openai_api_key
    
    async def analyze_performance(self, project_id: int, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze app performance and suggest optimizations.
        
        Args:
            metrics: Dict with load time, bundle size, render counts, etc.
        
        Returns:
            Dict with: score, bottlenecks[], optimizations[]
        """
        
        prompt = f"""
Analyze performance metrics for a React app:

Metrics:
{json.dumps(metrics, indent=2)}

Identify:
1. Performance bottlenecks
2. Quick wins (easy optimizations with big impact)
3. Code splitting opportunities
4. Unnecessary re-renders
5. Image/asset optimization needs

Respond in JSON:
{{
    "performance_score": 0-100,
    "bottlenecks": [
        {{"issue": "name", "impact": "high|medium|low", "location": "where in code"}},
        ...
    ],
    "optimizations": [
        {{
            "optimization": "What to do",
            "effort": "easy|medium|hard",
            "impact": "How much faster",
            "priority": "critical|high|medium|low",
            "code_example": "Example implementation"
        }},
        ...
    ],
    "estimated_improvement": "X% faster load time",
    "auto_applicable": ["Which optimizations can be auto-applied"]
}}
"""
        
        response = openai.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "You are a frontend performance expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        logger.info(
            "performance_analyzed",
            project_id=project_id,
            score=analysis.get("performance_score"),
            bottlenecks=len(analysis.get("bottlenecks", []))
        )
        
        return analysis
