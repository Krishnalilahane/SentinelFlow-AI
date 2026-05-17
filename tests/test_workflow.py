import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_workflow_run_high_risk_case_moves_to_human_review():
    unique_id = str(uuid.uuid4())[:8]

    case_response = client.post(
        "/cases",
        json={
            "customer_id": f"CUST-WF-{unique_id}",
            "transaction_id": f"TXN-WF-{unique_id}",
            "case_type": "SUSPICIOUS_TRANSACTION",
            "description": "Customer reports an unknown card transaction of €487.20 after three failed login attempts and a new device login yesterday.",
            "priority": "HIGH",
        },
        headers={"Idempotency-Key": f"workflow-test-high-risk-{unique_id}"},
    )

    assert case_response.status_code in [200, 201]

    case_data = case_response.json()["case"]
    case_id = case_data["id"]

    workflow_response = client.post(f"/workflows/cases/{case_id}/run")

    assert workflow_response.status_code == 200

    workflow_data = workflow_response.json()

    assert workflow_data["case_id"] == case_id
    assert workflow_data["requires_human_review"] is True
    assert workflow_data["current_state"] == "WAITING_FOR_HUMAN"

    assert workflow_data["risk_summary"]["overall_risk_level"] in ["HIGH", "CRITICAL"]
    assert workflow_data["decision_summary"]["requires_human_review"] is True

    status_response = client.get(f"/workflows/cases/{case_id}/status")

    assert status_response.status_code == 200

    status_data = status_response.json()

    assert status_data["case_id"] == case_id
    assert status_data["current_state"] == "WAITING_FOR_HUMAN"
    assert status_data["human_review_status"] == "PENDING"
    assert len(status_data["latest_agent_runs"]) > 0


def test_human_review_endpoint_closes_case():
    unique_id = str(uuid.uuid4())[:8]

    case_response = client.post(
        "/cases",
        json={
            "customer_id": f"CUST-WF-{unique_id}",
            "transaction_id": f"TXN-WF-{unique_id}",
            "case_type": "SUSPICIOUS_TRANSACTION",
            "description": "Customer reports an unknown card transaction after a new device login.",
            "priority": "HIGH",
        },
        headers={"Idempotency-Key": f"workflow-test-human-review-{unique_id}"},
    )

    assert case_response.status_code in [200, 201]

    case_id = case_response.json()["case"]["id"]

    workflow_response = client.post(f"/workflows/cases/{case_id}/run")

    assert workflow_response.status_code == 200
    assert workflow_response.json()["current_state"] == "WAITING_FOR_HUMAN"

    review_response = client.post(
        f"/workflows/cases/{case_id}/human-review",
        json={
            "review_status": "ESCALATED",
            "reviewer_notes": "Fraud indicators confirmed. Escalate to fraud operations.",
            "final_decision": "ESCALATE_TO_FRAUD_TEAM",
        },
    )

    assert review_response.status_code == 200

    review_data = review_response.json()

    assert review_data["case_id"] == case_id
    assert review_data["review_status"] == "ESCALATED"
    assert review_data["final_decision"] == "ESCALATE_TO_FRAUD_TEAM"
    assert review_data["current_state"] == "CLOSED"
def test_workflow_cannot_rerun_when_waiting_for_human_review():
    unique_id = str(uuid.uuid4())[:8]

    case_response = client.post(
        "/cases",
        json={
            "customer_id": f"CUST-WF-RERUN-{unique_id}",
            "transaction_id": f"TXN-WF-RERUN-{unique_id}",
            "case_type": "SUSPICIOUS_TRANSACTION",
            "description": "Customer reports an unknown card transaction after failed login attempts and a new device login.",
            "priority": "HIGH",
        },
        headers={"Idempotency-Key": f"workflow-test-rerun-{unique_id}"},
    )

    assert case_response.status_code in [200, 201]

    case_id = case_response.json()["case"]["id"]

    first_run_response = client.post(f"/workflows/cases/{case_id}/run")

    assert first_run_response.status_code == 200
    assert first_run_response.json()["current_state"] == "WAITING_FOR_HUMAN"

    second_run_response = client.post(f"/workflows/cases/{case_id}/run")

    assert second_run_response.status_code == 404
    assert "already waiting for human review" in second_run_response.json()["detail"].lower()