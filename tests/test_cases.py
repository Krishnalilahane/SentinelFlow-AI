import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_case_and_duplicate_idempotency_behavior():
    unique_id = str(uuid.uuid4())[:8]

    payload = {
        "customer_id": f"CUST-TEST-{unique_id}",
        "transaction_id": f"TXN-TEST-{unique_id}",
        "case_type": "SUSPICIOUS_TRANSACTION",
        "description": "Customer reports an unknown card transaction after a suspicious login attempt.",
        "priority": "HIGH",
    }

    first_response = client.post("/cases", json=payload)

    assert first_response.status_code == 201

    first_data = first_response.json()

    assert first_data["duplicate"] is False
    assert first_data["message"] == "Case created successfully."
    assert first_data["case"]["customer_id"] == payload["customer_id"]
    assert first_data["case"]["transaction_id"] == payload["transaction_id"]
    assert first_data["case"]["state"] == "CREATED"

    first_case_id = first_data["case"]["id"]

    second_response = client.post("/cases", json=payload)

    assert second_response.status_code == 201

    second_data = second_response.json()

    assert second_data["duplicate"] is True
    assert second_data["case"]["id"] == first_case_id


def test_case_events_are_logged():
    unique_id = str(uuid.uuid4())[:8]

    payload = {
        "customer_id": f"CUST-EVENT-{unique_id}",
        "transaction_id": f"TXN-EVENT-{unique_id}",
        "case_type": "AML_ESCALATION",
        "description": "AML review required after unusual transaction pattern across multiple payment attempts.",
        "priority": "MEDIUM",
    }

    create_response = client.post("/cases", json=payload)

    assert create_response.status_code == 201

    case_id = create_response.json()["case"]["id"]

    events_response = client.get(f"/cases/{case_id}/events")

    assert events_response.status_code == 200

    events = events_response.json()
    event_types = [event["event_type"] for event in events]

    assert "CASE_CREATED" in event_types