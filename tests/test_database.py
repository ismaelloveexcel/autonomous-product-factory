"""Tests for database models."""

import pytest
from datetime import datetime
from database.models import (
    SessionLocal, Project, Task, Metric, Feedback,
    AgentHealth, Budget, ProjectStatus, AgentType, init_db
)


@pytest.fixture
def db_session():
    """Create a test database session."""
    init_db()
    session = SessionLocal()
    yield session
    session.close()


def test_create_project(db_session):
    """Test project creation."""
    project = Project(
        name="Test App",
        description="Test description",
        category="education",
        target_age_min=8,
        target_age_max=12
    )
    
    db_session.add(project)
    db_session.commit()
    
    assert project.id is not None
    assert project.status == ProjectStatus.IDEA
    assert project.total_cost == 0.0


def test_create_task(db_session):
    """Test task creation."""
    project = Project(name="Test App", description="Test")
    db_session.add(project)
    db_session.commit()
    
    task = Task(
        project_id=project.id,
        agent_type=AgentType.MARKET_RESEARCH,
        status="pending",
        input_data={"test": "data"}
    )
    
    db_session.add(task)
    db_session.commit()
    
    assert task.id is not None
    assert task.project_id == project.id


def test_project_relationships(db_session):
    """Test project relationships."""
    project = Project(name="Test App", description="Test")
    db_session.add(project)
    db_session.commit()
    
    # Add task
    task = Task(
        project_id=project.id,
        agent_type=AgentType.DEVELOPMENT,
        status="completed"
    )
    db_session.add(task)
    
    # Add metric
    metric = Metric(
        project_id=project.id,
        metric_name="dau",
        metric_value=100
    )
    db_session.add(metric)
    
    db_session.commit()
    
    # Check relationships
    assert len(project.tasks) == 1
    assert len(project.metrics) == 1
    assert project.tasks[0].agent_type == AgentType.DEVELOPMENT


def test_budget_tracking(db_session):
    """Test budget tracking."""
    budget = Budget(
        month="2026-02",
        total_limit=1000.0,
        total_spent=0.0
    )
    
    db_session.add(budget)
    db_session.commit()
    
    # Add spending
    budget.total_spent += 50.0
    budget.openai_spent += 30.0
    budget.vercel_spent += 20.0
    
    db_session.commit()
    
    assert budget.total_spent == 50.0
    assert not budget.budget_exceeded


def test_agent_health(db_session):
    """Test agent health tracking."""
    health = AgentHealth(
        agent_type=AgentType.MARKET_RESEARCH,
        is_healthy=True,
        total_executions=0
    )
    
    db_session.add(health)
    db_session.commit()
    
    # Record success
    health.total_executions += 1
    health.total_successes += 1
    health.last_success_at = datetime.utcnow()
    health.consecutive_failures = 0
    
    db_session.commit()
    
    assert health.total_executions == 1
    assert health.total_successes == 1
    assert health.is_healthy
