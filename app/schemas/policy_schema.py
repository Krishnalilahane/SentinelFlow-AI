from pydantic import BaseModel, Field


class PolicySearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)


class PolicySearchResult(BaseModel):
    source_file: str
    policy_name: str
    chunk_text: str
    relevance_score: float


class PolicySearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[PolicySearchResult]