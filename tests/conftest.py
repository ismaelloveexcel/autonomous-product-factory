"""Pytest configuration and shared fixtures."""

import pytest
import os
from database.models import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["DATABASE_URL"] = "sqlite:///test_factory.db"
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    os.environ["GITHUB_TOKEN"] = "ghp_test_token"
    os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise in tests
    
    # Initialize test database
    init_db()
    
    yield
    
    # Cleanup
    if os.path.exists("test_factory.db"):
        os.remove("test_factory.db")


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    from unittest.mock import Mock
    
    response = Mock()
    response.choices = [Mock(message=Mock(content='{"result": "test"}'))]
    response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    
    return response
