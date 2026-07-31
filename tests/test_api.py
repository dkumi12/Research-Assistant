from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api import app

client = TestClient(app)

@patch("src.api.research_graph.invoke")
def test_successful_research_run(mock_invoke):
    """Test a successful research request with a mocked AI graph."""
    
    # 1. Supply ALL fields required by your ResearchResponse Pydantic schema
    mock_invoke.return_value = {
        "question": "What are the benefits of the Turkish Get-Up?",
        "report": "This is a mocked research report.",
        "search_rounds": 2,
        "evidence_score": 85,
        "sources": [
            {"title": "Mock Source 1", "url": "https://example.com/1", "content": "Mock content."}
        ]
    }

    # 2. Trigger the endpoint
    response = client.post(
        "/api/research",
        json={
            "question": "What are the benefits of the Turkish Get-Up?",
            "depth": "standard"
        }
    )

    # 3. Assert a successful 200 OK response
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data["report"] == "This is a mocked research report."
    assert response_data["question"] == "What are the benefits of the Turkish Get-Up?"
    assert response_data["evidence_score"] == 85
    assert response_data["search_rounds"] == 2

    # 4. Confirm the graph invocation
    mock_invoke.assert_called_once()