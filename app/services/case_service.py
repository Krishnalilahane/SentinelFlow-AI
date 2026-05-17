from sqlalchemy.orm import Session

from app.db.models import (
    Case,
    CaseEventType,
    CaseState,
    Customer,
    IdempotencyKey,
    Transaction,
)
from app.schemas.case_schema import CaseCreateRequest
from app.services.event_service import create_case_event


def build_idempotency_key(case_data: CaseCreateRequest) -> str:
    return f"{case_data.customer_id}:{case_data.transaction_id}:{case_data.case_type.value}"


def create_case(
    db: Session,
    case_data: CaseCreateRequest,
    idempotency_key: str | None = None,
) -> tuple[Case, bool, str]:
    final_idempotency_key = idempotency_key or build_idempotency_key(case_data)

    existing_key = (
        db.query(IdempotencyKey)
        .filter(IdempotencyKey.key == final_idempotency_key)
        .first()
    )

    if existing_key:
        existing_case = db.query(Case).filter(Case.id == existing_key.case_id).first()

        if existing_case:
            create_case_event(
                db=db,
                case_id=existing_case.id,
                event_type=CaseEventType.CASE_DUPLICATE_DETECTED,
                message="Duplicate case creation request detected. Existing case returned.",
            )
            db.commit()
            db.refresh(existing_case)

            return existing_case, True, "Duplicate request detected. Existing case returned safely."

    customer = db.query(Customer).filter(Customer.id == case_data.customer_id).first()
    if not customer:
        customer = Customer(id=case_data.customer_id)
        db.add(customer)
        db.flush()

    transaction = db.query(Transaction).filter(Transaction.id == case_data.transaction_id).first()
    if not transaction:
        transaction = Transaction(
            id=case_data.transaction_id,
            customer_id=case_data.customer_id,
        )
        db.add(transaction)
        db.flush()

    new_case = Case(
        customer_id=case_data.customer_id,
        transaction_id=case_data.transaction_id,
        case_type=case_data.case_type.value,
        description=case_data.description,
        priority=case_data.priority.value,
        state=CaseState.CREATED.value,
    )

    db.add(new_case)
    db.flush()

    idempotency_record = IdempotencyKey(
        key=final_idempotency_key,
        case_id=new_case.id,
    )
    db.add(idempotency_record)

    create_case_event(
        db=db,
        case_id=new_case.id,
        event_type=CaseEventType.CASE_CREATED,
        message="Case created successfully.",
    )

    db.commit()
    db.refresh(new_case)

    return new_case, False, "Case created successfully."


def get_case_by_id(db: Session, case_id: str) -> Case | None:
    case = db.query(Case).filter(Case.id == case_id).first()

    if case:
        create_case_event(
            db=db,
            case_id=case.id,
            event_type=CaseEventType.CASE_FETCHED,
            message="Case fetched by ID.",
        )
        db.commit()
        db.refresh(case)

    return case


def list_cases(db: Session) -> list[Case]:
    return db.query(Case).order_by(Case.created_at.desc()).all()


def list_case_events(db: Session, case_id: str):
    from app.db.models import CaseEvent

    return (
        db.query(CaseEvent)
        .filter(CaseEvent.case_id == case_id)
        .order_by(CaseEvent.created_at.asc())
        .all()
    )