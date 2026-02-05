"""Tests for cost tracking."""

import pytest
from datetime import datetime
from utils.cost_tracker import CostTracker
from database.models import SessionLocal, Project, Task, Budget, AgentType, init_db


@pytest.fixture
def db_session():
    """Create a test database session."""
    init_db()
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_project_and_task(db_session):
    """Create test project and task."""
    project = Project(name="Test App", description="Test")
    db_session.add(project)
    db_session.commit()
    
    task = Task(
        project_id=project.id,
        agent_type=AgentType.MARKET_RESEARCH,
        status="running"
    )
    db_session.add(task)
    db_session.commit()
    
    return project, task


def test_calculate_openai_cost():
    """Test OpenAI cost calculation."""
    cost = CostTracker.calculate_openai_cost(
        model="gpt-4-turbo-preview",
        input_tokens=1000,
        output_tokens=500
    )
    
    # 1000 * 0.01/1000 + 500 * 0.03/1000 = 0.01 + 0.015 = 0.025
    assert cost == 0.025


def test_record_cost(test_project_and_task):
    """Test cost recording."""
    project, task = test_project_and_task
    
    # Record cost
    CostTracker.record_cost(
        project_id=project.id,
        task_id=task.id,
        cost=5.0,
        service="openai"
    )
    
    # Verify
    session = SessionLocal()
    
    updated_project = session.query(Project).filter_by(id=project.id).first()
    updated_task = session.query(Task).filter_by(id=task.id).first()
    
    assert updated_project.total_cost == 5.0
    assert updated_project.openai_cost == 5.0
    assert updated_task.cost == 5.0
    
    # Check budget updated
    current_month = datetime.utcnow().strftime("%Y-%m")
    budget = session.query(Budget).filter_by(month=current_month).first()
    
    assert budget is not None
    assert budget.total_spent == 5.0
    assert budget.openai_spent == 5.0
    
    session.close()


def test_monthly_budget():
    """Test monthly budget tracking."""
    budget_info = CostTracker.get_monthly_budget()
    
    assert "total_spent" in budget_info
    assert "total_limit" in budget_info
    assert "remaining" in budget_info
    assert "percentage_used" in budget_info
    assert "exceeded" in budget_info


def test_check_budget_available():
    """Test budget availability check."""
    # Should be available initially
    assert CostTracker.check_budget_available(required_cost=10.0) == True
    
    # Create excessive spending
    session = SessionLocal()
    current_month = datetime.utcnow().strftime("%Y-%m")
    budget = session.query(Budget).filter_by(month=current_month).first()
    
    if not budget:
        from utils.config import config
        budget = Budget(
            month=current_month,
            total_limit=config.max_monthly_budget
        )
        session.add(budget)
    
    budget.total_spent = budget.total_limit + 100
    budget.budget_exceeded = True
    session.commit()
    session.close()
    
    # Should not be available now
    assert CostTracker.check_budget_available() == False
