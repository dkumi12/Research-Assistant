from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api import app

client = TestClient(app)

# The @patch decorator intercepts 'research_graph.invoke' inside your api.py file.
# You must adjust the path 'src.api.research_graph.invoke' to exactly match where it is imported in api.py.
@patch("src.api.research_graph.invoke")
def test_successful_research_run(mock_invoke):
    """Test a successful research request with a mocked AI graph."""
    
    # 1. Define what the fake graph should return so we don't spend API credits
    mock_invoke.return_value = {
        "report": "This is a mocked research report.",
        "search_rounds": 2,
        "sources": [
            {"title": "Mock Source 1", "url": "https://example.com/1", "content": "Mock content."}
        ]
    }

    # 2. Fire the test request at the FastAPI endpoint
    response = client.post(
        "/api/research",
        json={
            "question": "What are the benefits of the Turkish Get-Up?",
            "depth": "standard"
        }
    )

    # 3. Assert the API responds perfectly
    assert response.status_code == 200
    
    response_data = response.json()
    assert "report" in response_data
    assert response_data["report"] == "This is a mocked research report."
    assert response_data["search_rounds"] == 2

    # 4. Verify that the mocked graph was actually called with the right inputs
    mock_invoke.assert_called_once()
    called_args = mock_invoke.call_args[0][0]
    assert called_args["question"] == "What are the benefits of the Turkish Get-Up?"