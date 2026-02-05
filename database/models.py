"""Database models for Autonomous Product Factory."""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    DateTime, Text, Enum, ForeignKey, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from utils.config import config

Base = declarative_base()


class ProjectStatus(PyEnum):
    """Project lifecycle states."""
    IDEA = "idea"
    RESEARCHING = "researching"
    VALIDATING = "validating"
    BUILDING = "building"
    REVIEWING = "reviewing"
    MARKETING = "marketing"
    DEPLOYING = "deploying"
    LIVE = "live"
    KILLED = "killed"
    FAILED = "failed"


class AgentType(PyEnum):
    """Agent types in the system."""
    MARKET_RESEARCH = "market_research"
    VIABILITY = "viability"
    DEVELOPMENT = "development"
    AESTHETIC = "aesthetic"
    MARKETING = "marketing"
    LAUNCH = "launch"
    CUSTOMER_SERVICE = "customer_service"


class Project(Base):
    """Represents an app project in the factory."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.IDEA, nullable=False)
    
    # Target audience
    target_age_min = Column(Integer, default=8)
    target_age_max = Column(Integer, default=25)
    
    # URLs and deployment
    github_repo_url = Column(String(500))
    vercel_url = Column(String(500))
    vercel_deployment_id = Column(String(200))
    
    # Metadata
    idea_source = Column(String(200))  # e.g., "trending_topic", "market_gap"
    keywords = Column(JSON)  # List of keywords
    category = Column(String(100))
    
    # Costs and metrics
    total_cost = Column(Float, default=0.0)
    openai_cost = Column(Float, default=0.0)
    vercel_cost = Column(Float, default=0.0)
    
    # Performance metrics
    daily_active_users = Column(Integer, default=0)
    total_users = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    last_activity_at = Column(DateTime)
    
    # Safety flags
    coppa_compliant = Column(Boolean, default=False)
    content_moderation_passed = Column(Boolean, default=False)
    aesthetic_score = Column(Float)  # 0-100 from GPT-4 Vision
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    deployed_at = Column(DateTime)
    killed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="project", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.id}: {self.name} ({self.status.value})>"


class Task(Base):
    """Agent task execution records."""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Cost tracking
    cost = Column(Float, default=0.0)
    api_calls = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task {self.id}: {self.agent_type.value} for Project {self.project_id}>"


class Metric(Base):
    """Time-series metrics for projects."""
    
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    metric_name = Column(String(100), nullable=False)  # e.g., "dau", "engagement_rate"
    metric_value = Column(Float, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="metrics")
    
    def __repr__(self):
        return f"<Metric {self.metric_name}={self.metric_value} for Project {self.project_id}>"


class Feedback(Base):
    """User feedback from deployed apps."""
    
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    user_age = Column(Integer)
    feedback_text = Column(Text)
    sentiment = Column(String(50))  # positive, negative, neutral
    sentiment_score = Column(Float)  # -1 to 1
    
    source = Column(String(100))  # e.g., "webhook", "manual"
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback {self.id} for Project {self.project_id}: {self.sentiment}>"


class AgentHealth(Base):
    """Agent health monitoring."""
    
    __tablename__ = "agent_health"
    
    id = Column(Integer, primary_key=True)
    agent_type = Column(Enum(AgentType), nullable=False, unique=True)
    
    is_healthy = Column(Boolean, default=True)
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)
    consecutive_failures = Column(Integer, default=0)
    
    total_executions = Column(Integer, default=0)
    total_successes = Column(Integer, default=0)
    total_failures = Column(Integer, default=0)
    
    avg_duration_seconds = Column(Float, default=0.0)
    avg_cost = Column(Float, default=0.0)
    
    last_error = Column(Text)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentHealth {self.agent_type.value}: {'healthy' if self.is_healthy else 'unhealthy'}>"


class Budget(Base):
    """Budget tracking and limits."""
    
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True)
    month = Column(String(7), nullable=False, unique=True)  # e.g., "2026-02"
    
    total_spent = Column(Float, default=0.0)
    openai_spent = Column(Float, default=0.0)
    vercel_spent = Column(Float, default=0.0)
    github_spent = Column(Float, default=0.0)
    
    total_limit = Column(Float, nullable=False)
    
    alert_sent = Column(Boolean, default=False)
    budget_exceeded = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Budget {self.month}: ${self.total_spent:.2f}/${self.total_limit:.2f}>"


# Database initialization
engine = create_engine(config.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize database schema."""
    Base.metadata.create_all(bind=engine)
    
    # Initialize agent health records
    session = SessionLocal()
    try:
        for agent_type in AgentType:
            existing = session.query(AgentHealth).filter_by(agent_type=agent_type).first()
            if not existing:
                health = AgentHealth(agent_type=agent_type)
                session.add(health)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_db():
    """Get database session (for dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
