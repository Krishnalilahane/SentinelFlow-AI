from fastapi import APIRouter, HTTPException

from app.schemas.policy_schema import PolicySearchRequest, PolicySearchResponse
from app.services.policy_service import PolicyService


router = APIRouter(prefix="/policies", tags=["Policies"])

policy_service = PolicyService()


@router.post("/search", response_model=PolicySearchResponse)
def search_policies(request: PolicySearchRequest) -> PolicySearchResponse:
    try:
        results = policy_service.search_policies(
            query=request.query,
            top_k=request.top_k,
        )

        return PolicySearchResponse(
            query=request.query,
            top_k=request.top_k,
            results=results,
        )

    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Policy search failed: {str(error)}",
        )