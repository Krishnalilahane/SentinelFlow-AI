from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CaseType(str, Enum):
    SUSPICIOUS_TRANSACTION = "SUSPICIOUS_TRANSACTION"
    CHARGEBACK_DISPUTE = "CHARGEBACK_DISPUTE"
    KYC_REVIEW = "KYC_REVIEW"
    AML_ESCALATION = "AML_ESCALATION"
    FAILED_PAYMENT = "FAILED_PAYMENT"
    CUSTOMER_COMPLAINT = "CUSTOMER_COMPLAINT"


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CaseState(str, Enum):
    NEW = "NEW"
    VALIDATING = "VALIDATING"
    CREATED = "CREATED"
    FAILED = "FAILED"


class CaseCreateRequest(BaseModel):
    customer_id: str = Field(..., min_length=3, max_length=50)
    transaction_id: str = Field(..., min_length=3, max_length=50)
    case_type: CaseType
    description: str = Field(..., min_length=10, max_length=2000)
    priority: CasePriority


class CaseResponse(BaseModel):
    id: str
    customer_id: str
    transaction_id: str
    case_type: str
    description: str
    priority: str
    state: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class CaseEventResponse(BaseModel):
    id: str
    case_id: str
    event_type: str
    message: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class CaseCreateApiResponse(BaseModel):
    duplicate: bool
    message: str
    case: CaseResponse