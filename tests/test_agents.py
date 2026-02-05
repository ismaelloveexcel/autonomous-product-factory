"""Tests for agents."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from agents import MarketResearchAgent, ViabilityAgent
from database.models import SessionLocal, Project, ProjectStatus, init_db


@pytest.fixture
def db_session():
    """Create a test database session."""
    init_db()
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_project(db_session):
    """Create a test project."""
    project = Project(
        name="Test App",
        description="Test description",
        category="education",
        status=ProjectStatus.IDEA
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.mark.asyncio
async def test_market_research_agent_success(test_project):
    """Test successful market research."""
    agent = MarketResearchAgent()
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"app_name": "Math Quest", "description": "Educational game", "category": "education", "target_age_min": 8, "target_age_max": 12, "keywords": ["math", "game"], "core_features": ["feature1"], "github_search_terms": ["react"], "value_proposition": "Fun learning"}'))]
    mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200, total_tokens=300)
    
    with patch('openai.chat.completions.create', return_value=mock_response):
        result = await agent.run(test_project.id)
    
    assert result["success"] == True
    assert "app_idea" in result["data"]
    assert result["data"]["app_idea"]["app_name"] == "Math Quest"


@pytest.mark.asyncio
async def test_viability_agent_valid(test_project):
    """Test viability check for valid app."""
    agent = ViabilityAgent()
    
    # Set project details
    session = SessionLocal()
    project = session.query(Project).filter_by(id=test_project.id).first()
    project.name = "Math Quest"
    project.description = "Educational math game"
    session.commit()
    session.close()
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"viable": true, "safety_score": 90, "coppa_compliant": true, "gdpr_considerations": [], "age_appropriate": true, "issues": [], "recommendations": [], "risk_level": "low", "feasibility_score": 85, "reasoning": "Safe and feasible"}'))]
    mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200, total_tokens=300)
    
    # Mock moderation
    mock_moderation = Mock()
    mock_moderation.results = [Mock(
        flagged=False,
        categories=Mock(),
        category_scores=Mock()
    )]
    mock_moderation.results[0].categories.model_dump = Mock(return_value={})
    mock_moderation.results[0].category_scores.model_dump = Mock(return_value={})
    
    with patch('openai.chat.completions.create', return_value=mock_response), \
         patch('openai.moderations.create', return_value=mock_moderation):
        result = await agent.run(test_project.id)
    
    assert result["success"] == True
    assert result["data"]["validation"]["viable"] == True
    assert result["data"]["validation"]["safety_score"] == 90


@pytest.mark.asyncio
async def test_viability_agent_invalid(test_project):
    """Test viability check for invalid app."""
    agent = ViabilityAgent()
    
    # Set project details
    session = SessionLocal()
    project = session.query(Project).filter_by(id=test_project.id).first()
    project.name = "Social Chat"
    project.description = "Chat with strangers"
    session.commit()
    session.close()
    
    # Mock OpenAI response (not viable)
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"viable": false, "safety_score": 30, "coppa_compliant": false, "age_appropriate": false, "issues": ["Social features dangerous"], "risk_level": "high", "reasoning": "Unsafe for children"}'))]
    mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200, total_tokens=300)
    
    # Mock moderation (flagged)
    mock_moderation = Mock()
    mock_moderation.results = [Mock(flagged=True)]
    mock_moderation.results[0].categories.model_dump = Mock(return_value={"hate": True})
    mock_moderation.results[0].category_scores.model_dump = Mock(return_value={"hate": 0.8})
    
    with patch('openai.chat.completions.create', return_value=mock_response), \
         patch('openai.moderations.create', return_value=mock_moderation):
        result = await agent.run(test_project.id)
    
    assert result["success"] == True
    assert result["data"]["validation"]["viable"] == False


def test_agent_health_tracking(test_project):
    """Test agent health tracking."""
    from database.models import AgentHealth, AgentType
    
    session = SessionLocal()
    
    health = session.query(AgentHealth).filter_by(
        agent_type=AgentType.MARKET_RESEARCH
    ).first()
    
    # Should be created during init_db
    assert health is not None
    assert health.is_healthy == True
    
    session.close()
