"""Configuration management for Autonomous Product Factory."""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Central configuration class."""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    vercel_token: str = os.getenv("VERCEL_TOKEN", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/factory.db")
    
    # Limits & Budgets
    max_cost_per_app: float = float(os.getenv("MAX_COST_PER_APP", "50.0"))
    max_monthly_budget: float = float(os.getenv("MAX_MONTHLY_BUDGET", "1000.0"))
    max_concurrent_builds: int = int(os.getenv("MAX_CONCURRENT_BUILDS", "3"))
    
    # Scheduling
    research_interval_hours: int = int(os.getenv("RESEARCH_INTERVAL_HOURS", "6"))
    health_check_interval_minutes: int = int(os.getenv("HEALTH_CHECK_INTERVAL_MINUTES", "15"))
    
    # Safety
    min_age_target: int = int(os.getenv("MIN_AGE_TARGET", "8"))
    max_age_target: int = int(os.getenv("MAX_AGE_TARGET", "25"))
    enable_coppa_validation: bool = os.getenv("ENABLE_COPPA_VALIDATION", "true").lower() == "true"
    enable_content_moderation: bool = os.getenv("ENABLE_CONTENT_MODERATION", "true").lower() == "true"
    
    # Performance Thresholds
    min_dau_for_survival: int = int(os.getenv("MIN_DAU_FOR_SURVIVAL", "10"))
    min_engagement_rate: float = float(os.getenv("MIN_ENGAGEMENT_RATE", "0.15"))
    kill_after_days_inactive: int = int(os.getenv("KILL_AFTER_DAYS_INACTIVE", "30"))
    
    # GitHub
    github_search_limit: int = int(os.getenv("GITHUB_SEARCH_LIMIT", "10"))
    github_code_reuse_enabled: bool = os.getenv("GITHUB_CODE_REUSE_ENABLED", "true").lower() == "true"
    
    # OpenAI
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    openai_vision_model: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Vercel
    vercel_org_id: str = os.getenv("VERCEL_ORG_ID", "")
    vercel_project_prefix: str = os.getenv("VERCEL_PROJECT_PREFIX", "youthapp-")
    
    # Webhook endpoints
    feedback_webhook_url: Optional[str] = os.getenv("FEEDBACK_WEBHOOK_URL")
    alert_webhook_url: Optional[str] = os.getenv("ALERT_WEBHOOK_URL")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_structured_logging: bool = os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true"
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN is required")
        return True


# Global config instance
config = Config()
