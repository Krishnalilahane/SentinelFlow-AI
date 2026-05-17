from sqlalchemy.orm import Session

from app.db.models import CaseEvent, CaseEventType


def create_case_event(
    db: Session,
    case_id: str,
    event_type: CaseEventType,
    message: str,
) -> CaseEvent:
    event = CaseEvent(
        case_id=case_id,
        event_type=event_type.value,
        message=message,
    )

    db.add(event)
    db.flush()

    return event