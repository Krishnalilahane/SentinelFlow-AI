from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_policy_search_returns_relevant_results():
    response = client.post(
        "/policies/search",
        json={
            "query": "new device login and suspicious transaction",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "new device login and suspicious transaction"
    assert data["top_k"] == 3
    assert "results" in data
    assert len(data["results"]) > 0

    first_result = data["results"][0]

    assert "source_file" in first_result
    assert "policy_name" in first_result
    assert "chunk_text" in first_result
    assert "relevance_score" in first_result

    combined_results = " ".join(
        result["chunk_text"].lower() for result in data["results"]
    )

    assert "device" in combined_results
    assert "transaction" in combined_results