"""Tests for OpenRouter API client."""

import pytest
from unittest.mock import patch, MagicMock
from openrouter_client import OpenRouterClient, PaperRecommendation

@pytest.fixture
def client():
    """Create a test client with dummy API key."""
    return OpenRouterClient(api_key="test_key")

def test_init_without_api_key():
    """Test initialization without API key raises error."""
    with pytest.raises(ValueError):
        OpenRouterClient()

def test_init_with_api_key():
    """Test successful initialization with API key."""
    client = OpenRouterClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert "Bearer test_key" in client.headers["Authorization"]

@patch('requests.post')
def test_analyze_papers_success(mock_post, client):
    """Test successful paper analysis."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "Example response content"
            }
        }]
    }
    mock_post.return_value = mock_response
    
    results = client.analyze_papers("AI", "general")
    assert isinstance(results, list)
    
    # Verify API call
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "deepseek-chat" in str(call_args)
    assert "AI" in str(call_args)

@patch('requests.post')
def test_analyze_papers_api_error(mock_post, client):
    """Test API error handling."""
    mock_post.side_effect = Exception("API Error")
    
    with pytest.raises(Exception):
        client.analyze_papers("AI", "general")
