import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _create_test_case(priority: str = "HIGH") -> str:
    unique_id = str(uuid.uuid4())[:8]

    response = client.post(
        "/cases",
        json={
            "customer_id": f"CUST-OPS-{unique_id}",
            "transaction_id": f"TXN-OPS-{unique_id}",
            "case_type": "SUSPICIOUS_TRANSACTION",
            "description": "Customer reports an unknown card transaction after a suspicious login attempt.",
            "priority": priority,
        },
        headers={"Idempotency-Key": f"operations-test-{unique_id}"},
    )

    assert response.status_code in [200, 201]
    return response.json()["case"]["id"]


def test_operations_metrics_endpoint_works():
    response = client.get("/operations/metrics")

    assert response.status_code == 200

    data = response.json()

    assert "total_cases" in data
    assert "cases_by_state" in data
    assert "human_review_pending_count" in data
    assert "closed_cases_count" in data
    assert "high_or_critical_risk_count" in data
    assert "total_agent_runs" in data
    assert "total_workflow_events" in data
    assert "average_confidence_score" in data

    assert isinstance(data["total_cases"], int)
    assert isinstance(data["cases_by_state"], dict)


def test_simulate_failure_endpoint_marks_case_failed():
    case_id = _create_test_case()

    response = client.post(
        f"/operations/cases/{case_id}/simulate-failure",
        json={
            "failure_reason": "Simulated downstream notification failure during test"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case_id
    assert data["previous_state"] == "CREATED"
    assert data["current_state"] == "FAILED"
    assert data["event_logged"] == "WORKFLOW_FAILED"
    assert "Simulated downstream notification failure" in data["failure_reason"]


def test_retry_closed_case_is_blocked():
    case_id = _create_test_case()

    workflow_response = client.post(f"/workflows/cases/{case_id}/run")

    assert workflow_response.status_code == 200
    assert workflow_response.json()["current_state"] == "WAITING_FOR_HUMAN"

    review_response = client.post(
        f"/workflows/cases/{case_id}/human-review",
        json={
            "review_status": "ESCALATED",
            "reviewer_notes": "Fraud indicators confirmed during operations test.",
            "final_decision": "ESCALATE_TO_FRAUD_TEAM",
        },
    )

    assert review_response.status_code == 200
    assert review_response.json()["current_state"] == "CLOSED"

    retry_response = client.post(f"/operations/cases/{case_id}/retry")

    assert retry_response.status_code == 200

    retry_data = retry_response.json()

    assert retry_data["case_id"] == case_id
    assert retry_data["retry_allowed"] is False
    assert retry_data["previous_state"] == "CLOSED"
    assert retry_data["current_state"] == "CLOSED"
    assert "already closed" in retry_data["message"].lower()


def test_compensation_endpoint_records_simulated_action():
    case_id = _create_test_case()

    response = client.post(
        f"/operations/cases/{case_id}/compensate",
        json={
            "compensation_action": "NOTIFY_OPERATIONS_TEAM",
            "reason": "Operations should review the case after a simulated workflow issue.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case_id
    assert data["compensation_action"] == "NOTIFY_OPERATIONS_TEAM"
    assert data["event_logged"] == "WORKFLOW_FAILED"
    assert "No real banking action was executed" in data["message"]