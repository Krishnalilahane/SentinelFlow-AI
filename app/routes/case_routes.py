from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.case_schema import (
    CaseCreateApiResponse,
    CaseCreateRequest,
    CaseEventResponse,
    CaseResponse,
)
from app.services.case_service import (
    create_case,
    get_case_by_id,
    list_case_events,
    list_cases,
)

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseCreateApiResponse, status_code=status.HTTP_201_CREATED)
def create_risk_case(
    case_data: CaseCreateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    case, duplicate, message = create_case(
        db=db,
        case_data=case_data,
        idempotency_key=idempotency_key,
    )

    return {
        "duplicate": duplicate,
        "message": message,
        "case": case,
    }


@router.get("", response_model=list[CaseResponse])
def get_cases(db: Session = Depends(get_db)):
    return list_cases(db)


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = get_case_by_id(db=db, case_id=case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return case


@router.get("/{case_id}/events", response_model=list[CaseEventResponse])
def get_case_events(case_id: str, db: Session = Depends(get_db)):
    case = get_case_by_id(db=db, case_id=case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return list_case_events(db=db, case_id=case_id)