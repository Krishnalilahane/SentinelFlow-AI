# SentinelFlow AI

**Enterprise-style AI Engineering platform for FinTech risk operations, multi-agent workflow orchestration, policy-grounded decisioning, human review, and durable workflow recovery.**

SentinelFlow AI is not a chatbot. It is a backend-first AI Engineering portfolio project that simulates how financial institutions could manage suspicious transactions, chargeback disputes, KYC reviews, AML escalations, failed payment investigations, customer complaints, and human review workflows.

The project demonstrates practical AI Engineering skills across FastAPI, PostgreSQL, RAG, LangGraph-style multi-agent workflows, audit logging, idempotency, retry handling, failure recovery, compensation logic, and a Streamlit operations dashboard.

---

## Why This Project Matters

Most AI portfolio projects stop at a chatbot or a simple prediction model.

SentinelFlow AI focuses on a harder and more realistic problem: **how AI decisions move through enterprise workflows safely**.

The system shows how a risk case can be created, enriched with policy evidence, processed by multiple AI agents, scored for risk, routed for human review when needed, and tracked through an auditable workflow timeline.

It also demonstrates operational reliability concepts such as durable state, retry logic, failure simulation, and saga-style compensation without overloading the project with heavy infrastructure.

---

## Core Capabilities

- Case creation for financial risk operations
- PostgreSQL-backed persistent case state
- Idempotency protection for duplicate case creation
- Synthetic customer, transaction, and case data
- RAG-based policy search over banking policy documents
- LangGraph-style multi-agent workflow execution
- Agent output persistence
- Risk scoring and decision recommendation
- Human-in-the-loop review queue
- Workflow event logging and audit timeline
- Lightweight durable execution simulation
- Retry endpoint for failed workflows
- Failure simulation endpoint for demo recovery scenarios
- Saga-style compensation action logging
- Streamlit dashboard for operations visibility
- Automated test coverage for backend, workflow, policy search, and operations

---

## Architecture Overview

```mermaid
flowchart TD
    A[Analyst / Reviewer] --> B[Streamlit Dashboard]
    B --> C[FastAPI Backend]

    C --> D[PostgreSQL Database]
    C --> E[RAG Policy Search]
    C --> F[LangGraph Workflow]
    C --> G[Operations Layer]

    E --> H[ChromaDB Vector Store]
    E --> I[Banking Policy Documents]

    F --> J[Intake Agent]
    F --> K[Policy Retrieval Agent]
    F --> L[Risk Analysis Agent]
    F --> M[Decision Agent]
    F --> N[Human Review Agent]

    G --> O[Retry Workflow]
    G --> P[Simulate Failure]
    G --> Q[Compensation Action]
    G --> R[Operations Metrics]

    D --> S[Audit Events]
    S --> B
````

---

## Tech Stack

| Layer                  | Tools                                            |
| ---------------------- | ------------------------------------------------ |
| Backend API            | FastAPI, Pydantic                                |
| Database               | PostgreSQL 16, SQLAlchemy, Alembic               |
| Workflow Orchestration | LangGraph-style deterministic agent workflow     |
| RAG Layer              | ChromaDB, sentence-transformers/all-MiniLM-L6-v2 |
| Dashboard              | Streamlit                                        |
| Testing                | Pytest, FastAPI TestClient                       |
| Local Infrastructure   | Docker, Docker Compose                           |
| Language               | Python 3.10                                      |

---

## Project Stages

### Stage 1: Backend Foundation

Implemented:

* FastAPI backend
* PostgreSQL through Docker
* SQLAlchemy models
* Alembic migrations
* Customers table
* Transactions table
* Cases table
* Case events table
* Idempotency keys table
* Case creation API
* Health checks
* Database health endpoint
* Initial automated tests

Main endpoints:

```text
GET  /
GET  /health
GET  /health/db
POST /cases
GET  /cases
GET  /cases/{case_id}
GET  /cases/{case_id}/events
```

---

### Stage 2: RAG Policy Retrieval

Implemented:

* Synthetic fintech datasets
* Synthetic customers, transactions, and cases
* Banking policy documents
* ChromaDB vector store
* Sentence-transformer embeddings
* Policy search API
* Policy retrieval tests

Policy documents include:

* AML escalation policy
* Chargeback policy
* KYC review policy
* Fraud investigation policy
* Complaint SLA policy
* Vulnerable customer policy
* Account takeover policy
* Refund decision policy

Main endpoint:

```text
POST /policies/search
```

---

### Stage 3: Multi-Agent Workflow

Implemented:

* LangGraph workflow
* Intake Agent
* Policy Retrieval Agent
* Risk Analysis Agent
* Decision Agent
* Human Review Agent
* Agent run persistence
* Risk score persistence
* Decision persistence
* Human review persistence
* Case state updates
* Human-in-the-loop workflow pause
* Rerun protection
* Workflow tests

Main endpoints:

```text
POST /workflows/cases/{case_id}/run
GET  /workflows/cases/{case_id}/status
POST /workflows/cases/{case_id}/human-review
```

Example workflow result:

```text
Case State: WAITING_FOR_HUMAN
Risk Level: CRITICAL
Decision: FREEZE_ACCOUNT_RECOMMENDED
Human Review Status: PENDING
```

---

### Stage 4: Durable Operations and Dashboard

Implemented:

* Lightweight durable execution simulation using PostgreSQL
* Failure simulation endpoint
* Retry endpoint
* Saga-style compensation endpoint
* Operations metrics endpoint
* Streamlit dashboard
* Case timeline view
* Workflow status view
* Human review queue
* Audit events view
* Stage 4 operations tests

Main endpoints:

```text
GET  /operations/metrics
POST /operations/cases/{case_id}/simulate-failure
POST /operations/cases/{case_id}/retry
POST /operations/cases/{case_id}/compensate
```

Current test status:

```text
12 passed
```

---

## Dashboard Pages

The Streamlit dashboard provides a simple operational view of the system.

| Page               | Purpose                                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------------------- |
| Executive Overview | Shows total cases, pending reviews, closed cases, high-risk cases, agent runs, workflow events, and confidence |
| Case Timeline      | Shows case details and chronological event history                                                             |
| Workflow Status    | Shows AI risk score, AI decision, and agent outputs                                                            |
| Human Review       | Allows review of cases waiting for human decision                                                              |
| Audit Events       | Shows readable workflow event logs                                                                             |

Run command:

```bat
streamlit run frontend\streamlit_app.py
```

---

## Durable Execution Design

Real Temporal was intentionally not added in the local version because the project is designed to run on a lightweight Windows laptop with 8GB RAM.

Instead, SentinelFlow AI simulates durable execution using PostgreSQL-backed persistence:

| Durable Concept        | Project Implementation                         |
| ---------------------- | ---------------------------------------------- |
| Workflow state         | `cases.state`                                  |
| Workflow history       | `case_events`                                  |
| Agent activity outputs | `agent_runs`                                   |
| Risk results           | `risk_scores`                                  |
| Decision outputs       | `decisions`                                    |
| Human approval step    | `human_reviews`                                |
| Retry logic            | `/operations/cases/{case_id}/retry`            |
| Failure scenario       | `/operations/cases/{case_id}/simulate-failure` |
| Saga compensation      | `/operations/cases/{case_id}/compensate`       |

This keeps the project stable, understandable, and portfolio-ready while still showing enterprise workflow thinking.

---

## Folder Structure

```text
sentinelflow-ai/
│
├── agents/
│   ├── decision_agent.py
│   ├── graph.py
│   ├── human_review_agent.py
│   ├── intake_agent.py
│   ├── policy_agent.py
│   ├── risk_agent.py
│   └── state.py
│
├── app/
│   ├── core/
│   ├── db/
│   ├── routes/
│   │   ├── case_routes.py
│   │   ├── operations_routes.py
│   │   ├── policy_routes.py
│   │   └── workflow_routes.py
│   ├── schemas/
│   │   ├── case_schema.py
│   │   ├── operations_schema.py
│   │   ├── policy_schema.py
│   │   └── workflow_schema.py
│   ├── services/
│   │   ├── case_service.py
│   │   ├── event_service.py
│   │   ├── operations_service.py
│   │   ├── policy_service.py
│   │   └── workflow_service.py
│   └── main.py
│
├── data/
├── docs/
│   ├── architecture.md
│   └── durable_execution_design.md
│
├── frontend/
│   ├── streamlit_app.py
│   ├── ui_helpers.py
│   └── pages/
│       ├── 1_Case_Timeline.py
│       ├── 2_Workflow_Status.py
│       ├── 3_Human_Review.py
│       └── 4_Audit_Events.py
│
├── rag/
│   ├── ingest.py
│   ├── retriever.py
│   ├── policy_documents/
│   └── vector_store/
│
├── scripts/
├── tests/
│   ├── test_cases.py
│   ├── test_health.py
│   ├── test_operations.py
│   ├── test_policy_search.py
│   └── test_workflow.py
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## How to Run Locally

### 1. Clone the Repository

```bat
git clone <your-repository-url>
cd sentinelflow-ai
```

### 2. Create and Activate Virtual Environment

```bat
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bat
python -m pip install -r requirements.txt
```

### 4. Start PostgreSQL

```bat
docker compose up -d
docker compose ps
```

Expected PostgreSQL port:

```text
5433 -> 5432
```

### 5. Run Database Migrations

```bat
alembic upgrade head
```

### 6. Seed Data and Policies

Run the available project scripts for synthetic data and policy ingestion:

```bat
python scripts\seed_data.py
python rag\ingest.py
```

### 7. Start FastAPI Backend

Use this command for normal demo usage:

```bat
uvicorn app.main:app
```

For development only:

```bat
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### 8. Start Streamlit Dashboard

Open a second terminal:

```bat
cd /d D:\sentinelflow-ai
venv\Scripts\activate
streamlit run frontend\streamlit_app.py
```

Dashboard URL:

```text
http://localhost:8501
```

---

## API Endpoints

### Health

```text
GET /
GET /health
GET /health/db
```

### Cases

```text
POST /cases
GET  /cases
GET  /cases/{case_id}
GET  /cases/{case_id}/events
```

### Policy Search

```text
POST /policies/search
```

### Workflows

```text
POST /workflows/cases/{case_id}/run
GET  /workflows/cases/{case_id}/status
POST /workflows/cases/{case_id}/human-review
```

### Operations

```text
GET  /operations/metrics
POST /operations/cases/{case_id}/simulate-failure
POST /operations/cases/{case_id}/retry
POST /operations/cases/{case_id}/compensate
```

---

## Sample Workflow

### 1. Create a Case

```http
POST /cases
```

Example case:

```json
{
  "customer_id": "CUST-001",
  "transaction_id": "TXN-001",
  "case_type": "SUSPICIOUS_TRANSACTION",
  "description": "Customer reports an unknown card transaction after failed login attempts and a new device login.",
  "priority": "HIGH"
}
```

### 2. Run Workflow

```http
POST /workflows/cases/{case_id}/run
```

Expected result for high-risk suspicious transaction cases:

```json
{
  "current_state": "WAITING_FOR_HUMAN",
  "requires_human_review": true,
  "risk_summary": {
    "overall_risk_level": "CRITICAL",
    "confidence_score": 0.85
  },
  "decision_summary": {
    "decision_type": "FREEZE_ACCOUNT_RECOMMENDED",
    "requires_human_review": true
  }
}
```

### 3. Review Case

```http
POST /workflows/cases/{case_id}/human-review
```

Example review:

```json
{
  "review_status": "ESCALATED",
  "reviewer_notes": "Fraud indicators confirmed. Escalate to fraud operations.",
  "final_decision": "ESCALATE_TO_FRAUD_TEAM"
}
```

### 4. Simulate Failure and Retry

```http
POST /operations/cases/{case_id}/simulate-failure
POST /operations/cases/{case_id}/retry
```

This demonstrates failure recovery without adding Temporal locally.

---

## Testing

Run the full test suite:

```bat
python -m pytest
```

Current coverage includes:

* Health checks
* Case creation
* Idempotency behaviour
* Policy search
* Workflow execution
* Human review
* Rerun protection
* Operations metrics
* Failure simulation
* Retry blocking logic
* Compensation action logging

Current result:

```text
12 passed
```

---

## Screenshots Checklist

Add screenshots to GitHub after final demo capture:

```text
screenshots/
├── 01_swagger_overview.png
├── 02_create_case.png
├── 03_policy_search.png
├── 04_workflow_run.png
├── 05_workflow_status.png
├── 06_streamlit_overview.png
├── 07_case_timeline.png
├── 08_human_review_queue.png
├── 09_audit_events.png
└── 10_tests_passing.png
```

Recommended screenshots:

* Swagger endpoint list
* Operations metrics response
* Workflow run response
* Human review response
* Streamlit Executive Overview
* Streamlit Workflow Status
* Streamlit Human Review Queue
* Streamlit Audit Events
* Pytest result showing `12 passed`

---

## What This Project Demonstrates

SentinelFlow AI demonstrates:

* AI Engineering beyond chatbot development
* Backend API design using FastAPI
* Database-backed workflow state management
* RAG integration for policy-grounded decision support
* Multi-agent workflow orchestration
* Risk scoring and decision recommendation
* Human-in-the-loop AI design
* Idempotency and audit logging
* Durable execution thinking
* Retry and failure recovery design
* Saga-style compensation concepts
* Dashboarding for operational visibility
* Practical trade-off decisions under hardware constraints

---

## Limitations

This is a portfolio simulation, not a production banking system.

Current limitations:

* Uses synthetic data only
* No real customer data
* No real bank integrations
* No production authentication
* No role-based access control
* No real account freeze action
* No real fraud escalation API
* No real notification service
* No cloud deployment
* Compensation actions are simulated
* Durable execution is simulated through PostgreSQL rather than Temporal

---

## Future Improvements

Possible next improvements:

* Add role-based authentication
* Add richer dashboard filters
* Add JSON metadata to case events
* Add dedicated compensation event type
* Add CI workflow for automated tests
* Add deployment to Azure or AWS
* Add real Temporal or AWS Step Functions orchestration
* Add notification service integration
* Add model monitoring and evaluation dashboard
* Add Dockerized dashboard service

---

## Portfolio Positioning

SentinelFlow AI is designed to show practical AI Engineering judgment.

The project avoids unnecessary complexity such as Kafka, Kubernetes, Spark, heavy local LLMs, and paid APIs. Instead, it focuses on building a reliable, explainable, auditable, and demo-ready AI workflow system that can run locally on limited hardware.

The strongest part of this project is not the dashboard or the agents alone. It is the full workflow thinking: case intake, policy evidence, risk scoring, decisioning, human review, audit trail, failure handling, and recovery.

