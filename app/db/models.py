import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CaseState(str, Enum):
    NEW = "NEW"
    VALIDATING = "VALIDATING"
    CREATED = "CREATED"
    CLASSIFYING = "CLASSIFYING"
    RETRIEVING_POLICY = "RETRIEVING_POLICY"
    ANALYSING_RISK = "ANALYSING_RISK"
    DECISION_READY = "DECISION_READY"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    CLOSED = "CLOSED"
    FAILED = "FAILED"


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseType(str, Enum):
    SUSPICIOUS_TRANSACTION = "SUSPICIOUS_TRANSACTION"
    CHARGEBACK_DISPUTE = "CHARGEBACK_DISPUTE"
    KYC_REVIEW = "KYC_REVIEW"
    AML_ESCALATION = "AML_ESCALATION"
    FAILED_PAYMENT = "FAILED_PAYMENT"
    CUSTOMER_COMPLAINT = "CUSTOMER_COMPLAINT"


class CaseEventType(str, Enum):
    CASE_CREATED = "CASE_CREATED"
    CASE_DUPLICATE_DETECTED = "CASE_DUPLICATE_DETECTED"
    CASE_VALIDATION_FAILED = "CASE_VALIDATION_FAILED"
    CASE_FETCHED = "CASE_FETCHED"

    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    INTAKE_COMPLETED = "INTAKE_COMPLETED"
    POLICY_RETRIEVED = "POLICY_RETRIEVED"
    RISK_ANALYSIS_COMPLETED = "RISK_ANALYSIS_COMPLETED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    DECISION_GENERATED = "DECISION_GENERATED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    HUMAN_REVIEW_COMPLETED = "HUMAN_REVIEW_COMPLETED"


class HumanReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(50), ForeignKey("customers.id"), nullable=False)
    amount: Mapped[str | None] = mapped_column(String(50), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(String(50), ForeignKey("customers.id"), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(50), ForeignKey("transactions.id"), nullable=False)
    case_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    state: Mapped[str] = mapped_column(String(30), default=CaseState.NEW.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("CaseEvent", back_populates="case")


class CaseEvent(Base):
    __tablename__ = "case_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="events")


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("key", name="uq_idempotency_keys_key"),
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), nullable=False)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    fraud_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    customer_harm_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_risk_level: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    decision_type: Mapped[str] = mapped_column(String(80), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    review_status: Mapped[str] = mapped_column(String(30), nullable=False, default=HumanReviewStatus.PENDING.value)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_decision: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)