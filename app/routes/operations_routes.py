from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.operations_schema import (
    CompensationRequest,
    CompensationResponse,
    OperationsMetricsResponse,
    RetryWorkflowResponse,
    SimulateFailureRequest,
    SimulateFailureResponse,
)
from app.services.operations_service import (
    compensate_case_workflow,
    get_operations_metrics,
    retry_failed_workflow,
    simulate_workflow_failure,
)


router = APIRouter(prefix="/operations", tags=["Operations"])


@router.post(
    "/cases/{case_id}/simulate-failure",
    response_model=SimulateFailureResponse,
)
def simulate_failure(
    case_id: str,
    request: SimulateFailureRequest,
    db: Session = Depends(get_db),
):
    try:
        return simulate_workflow_failure(
            db=db,
            case_id=case_id,
            failure_reason=request.failure_reason,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/cases/{case_id}/retry",
    response_model=RetryWorkflowResponse,
)
def retry_workflow(
    case_id: str,
    db: Session = Depends(get_db),
):
    try:
        return retry_failed_workflow(db=db, case_id=case_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retry failed: {str(error)}",
        )


@router.post(
    "/cases/{case_id}/compensate",
    response_model=CompensationResponse,
)
def compensate_workflow(
    case_id: str,
    request: CompensationRequest,
    db: Session = Depends(get_db),
):
    try:
        return compensate_case_workflow(
            db=db,
            case_id=case_id,
            compensation_action=request.compensation_action,
            reason=request.reason,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get("/metrics", response_model=OperationsMetricsResponse)
def operations_metrics(db: Session = Depends(get_db)):
    return get_operations_metrics(db=db)