\# SentinelFlow AI Architecture



\## 1. Project Overview



SentinelFlow AI is an enterprise-style FinTech RiskOps orchestration platform designed to handle financial risk cases such as suspicious transactions, chargeback disputes, KYC reviews, AML escalations, failed payment investigations, customer complaints, and human review workflows.



The project is not a chatbot. It is built to demonstrate AI Engineering capability through backend APIs, stateful workflow orchestration, RAG-based policy retrieval, risk scoring, human-in-the-loop review, durable workflow simulation, retry handling, compensation logic, and audit visibility.



\## 2. What the System Does



SentinelFlow AI receives a risk case, stores it in PostgreSQL, retrieves relevant policy context using RAG, runs a multi-agent workflow, calculates risk scores, generates a decision recommendation, pauses for human review when required, and records every major workflow step as an auditable event.



The system also includes lightweight operations endpoints for retrying failed workflows, simulating workflow failures, recording compensation actions, and exposing operational metrics for the dashboard.



\## 3. High-Level Architecture



```mermaid

flowchart TD

&#x20;   A\[Analyst or Reviewer] --> B\[Streamlit Dashboard]

&#x20;   B --> C\[FastAPI Backend]



&#x20;   C --> D\[PostgreSQL Database]

&#x20;   C --> E\[RAG Policy Search]

&#x20;   C --> F\[LangGraph Workflow]



&#x20;   E --> G\[ChromaDB Vector Store]

&#x20;   E --> H\[Banking Policy Documents]



&#x20;   F --> I\[Intake Agent]

&#x20;   F --> J\[Policy Retrieval Agent]

&#x20;   F --> K\[Risk Analysis Agent]

&#x20;   F --> L\[Decision Agent]

&#x20;   F --> M\[Human Review Agent]



&#x20;   M --> N\[Human Review Queue]


&#x20;   C --> O\[Operations Layer]

&#x20;   O --> P\[Retry Workflow]

&#x20;   O --> Q\[Simulate Failure]

&#x20;   O --> R\[Compensation Action]

&#x20;   O --> S\[Operations Metrics]



&#x20;   D --> T\[Audit Events]

&#x20;   T --> B


4. Backend API Layer

The backend is built with FastAPI. It exposes endpoints for case creation, case retrieval, policy search, workflow execution, human review, and operations management.

Main backend capabilities include:

Create and retrieve risk cases
Store idempotency keys to prevent duplicate case creation
Retrieve case event history
Search banking policy documents through RAG
Run a multi-agent workflow for a case
Retrieve workflow status and agent outputs
Submit human review decisions
Simulate workflow failure
Retry failed workflows
Record saga-style compensation actions
Expose operational metrics for the dashboard
5. Database Layer

PostgreSQL is used as the durable system of record. It stores cases, customers, transactions, case events, idempotency keys, agent runs, risk scores, decisions, and human review records.

Important tables include:

Table	Purpose
customers	Stores customer records
transactions	Stores transaction records
cases	Stores financial risk cases and current case state
case_events	Stores chronological audit events
idempotency_keys	Prevents duplicate case creation
agent_runs	Stores persisted agent inputs and outputs
risk_scores	Stores risk scoring outputs
decisions	Stores AI decision recommendations
human_reviews	Stores human review decisions

PostgreSQL also supports the durable workflow simulation by persisting case state, event history, agent outputs, risk results, and review status.

6. RAG Policy Retrieval Layer

The RAG layer retrieves relevant policy context from synthetic banking policy documents. It uses ChromaDB as the vector store and sentence-transformer embeddings for semantic search.

Policy documents include:

AML escalation policy
Chargeback policy
KYC review policy
Fraud investigation policy
Complaint SLA policy
Vulnerable customer policy
Account takeover policy
Refund decision policy

The retrieved policies are used by the workflow to support risk analysis and decision recommendations.

7. Multi-Agent Workflow Layer

The workflow is implemented using a deterministic LangGraph-style orchestration pattern.

Main agents:

Agent	Role
Intake Agent	Classifies the case and extracts urgency signals
Policy Retrieval Agent	Retrieves relevant policy evidence
Risk Analysis Agent	Scores fraud, compliance, and customer harm risk
Decision Agent	Generates a decision recommendation
Human Review Agent	Routes high-risk cases to manual review

The workflow updates case state as it progresses through classification, policy retrieval, risk analysis, decision generation, human review, or closure.

8. Human-in-the-Loop Review

High-risk or sensitive cases are not automatically closed. They are moved into a human review queue.

A reviewer can inspect:

Case description
Case priority
Risk score
AI reasoning
AI recommendation
Decision explanation
Audit history

The reviewer then submits a final decision such as escalation, approval, rejection, request for more information, or closure with no action.

9. Durable Execution Simulation

Real Temporal was not added in Stage 4 because the project is being developed on an 8GB RAM laptop. A clean PostgreSQL-backed durable workflow simulation is more reliable than forcing a heavy orchestration system into a constrained local setup.

The project simulates durable execution through:

Persistent case state
Persistent agent run records
Persistent risk scores
Persistent decision records
Persistent human review records
Persistent event logs
Retry endpoint for failed workflows
Failure simulation endpoint for demo scenarios
Compensation endpoint for saga-style recovery examples

This design maps naturally to Temporal, Cadence, Inngest, or AWS Step Functions in a future production version.

10. Operations Layer

The operations layer adds enterprise-readiness features without adding heavy infrastructure.

Operations endpoints include:

Endpoint	Purpose
POST /operations/cases/{case_id}/simulate-failure	Marks a case as failed for local recovery testing
POST /operations/cases/{case_id}/retry	Retries failed workflows safely
POST /operations/cases/{case_id}/compensate	Records simulated compensation actions
GET /operations/metrics	Returns dashboard metrics

These endpoints make the project easier to demonstrate because they show failure handling, recovery, and operational visibility.

11. Dashboard Layer

The dashboard is built with Streamlit. It provides a lightweight UI for demonstrating the system without adding a heavy frontend framework.

Dashboard pages include:

Page	Purpose
Executive Overview	Shows total cases, pending reviews, closed cases, high-risk cases, agent runs, workflow events, and confidence
Case Timeline	Shows case details and chronological event history
Workflow Status	Shows risk score, AI decision, and agent outputs
Human Review	Allows manual review of cases waiting for human input
Audit Events	Shows readable event logs and event summaries

The dashboard communicates the project clearly to recruiters, hiring managers, and technical reviewers.

12. Event-Driven Architecture Thinking

The system records key workflow actions as events. This gives the project an event-driven structure even though it does not use Kafka or a real message broker.

Examples of recorded events:

Case created
Workflow started
Intake completed
Policy retrieved
Risk analysis completed
Decision generated
Human review required
Human review completed
Workflow failed
Compensation action recorded

This event trail supports auditability, debugging, compliance-style review, and dashboard visibility.

13. Why This Architecture Is Portfolio-Ready

SentinelFlow AI demonstrates more than basic API development. It shows understanding of enterprise AI workflow design, operational reliability, stateful orchestration, policy-grounded reasoning, human oversight, and system observability.

The project is intentionally lightweight but structured like a real enterprise platform. It avoids unnecessary tools such as Kafka, Kubernetes, Spark, and paid LLM APIs because the goal is to demonstrate clean engineering judgment rather than tool overload.

14. Current Limitations

This is a portfolio simulation, not a production banking system.

Current limitations:

Uses synthetic data only
No real customer data
No real banking integrations
No production authentication
No real notification service
No real account freeze or fraud escalation action
No cloud deployment
Compensation actions are simulated and recorded, not executed
Durable execution is simulated through PostgreSQL rather than Temporal
15. Future Improvements

Possible future improvements include:

Add production authentication and role-based access control
Add real workflow orchestration using Temporal or AWS Step Functions
Add notification integrations
Add richer dashboard filtering
Add model monitoring and drift tracking
Add deployment to Azure or AWS
Add CI pipeline for automated tests
Add better event metadata storage using JSON fields
Add a dedicated compensation event type
