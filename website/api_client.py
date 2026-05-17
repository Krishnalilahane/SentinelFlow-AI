import requests
from typing import Any, Dict, List, Optional


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_SECONDS = 20


class APIError(Exception):
    """Readable API error for Streamlit pages."""
    pass


def _handle_response(response: requests.Response) -> Any:
    try:
        data = response.json()
    except ValueError:
        data = response.text

    if response.status_code >= 400:
        raise APIError(f"API error {response.status_code}: {data}")

    return data


def _get(path: str) -> Any:
    try:
        response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT_SECONDS)
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        raise APIError("Backend is not running. Start FastAPI on http://127.0.0.1:8000")
    except requests.exceptions.Timeout:
        raise APIError("Backend request timed out.")
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Backend request failed: {exc}")


def _post(path: str, payload: Optional[Dict[str, Any]] = None) -> Any:
    try:
        response = requests.post(
            f"{BASE_URL}{path}",
            json=payload or {},
            timeout=TIMEOUT_SECONDS,
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        raise APIError("Backend is not running. Start FastAPI on http://127.0.0.1:8000")
    except requests.exceptions.Timeout:
        raise APIError("Backend request timed out.")
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Backend request failed: {exc}")


def check_health() -> Dict[str, Any]:
    return _get("/health")


def check_db_health() -> Dict[str, Any]:
    return _get("/health/db")


def create_case(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post("/cases", payload)


def list_cases() -> List[Dict[str, Any]]:
    data = _get("/cases")
    return data if isinstance(data, list) else []


def get_case(case_id: str) -> Dict[str, Any]:
    return _get(f"/cases/{case_id}")


def get_case_events(case_id: str) -> List[Dict[str, Any]]:
    data = _get(f"/cases/{case_id}/events")
    return data if isinstance(data, list) else []


def search_policies(query: str, top_k: int = 3) -> Dict[str, Any]:
    payload = {
        "query": query,
        "top_k": top_k,
    }
    return _post("/policies/search", payload)


def run_workflow(case_id: str) -> Dict[str, Any]:
    return _post(f"/workflows/cases/{case_id}/run")


def get_workflow_status(case_id: str) -> Dict[str, Any]:
    return _get(f"/workflows/cases/{case_id}/status")


def submit_human_review(case_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post(f"/workflows/cases/{case_id}/human-review", payload)


def get_operations_metrics() -> Dict[str, Any]:
    """
    Optional endpoint. If unavailable or incompatible, pages can fall back
    to deriving metrics from /cases and workflow status.
    """
    return _get("/operations/metrics")