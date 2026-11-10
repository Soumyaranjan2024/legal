"""Search routes: semantic and keyword retrieval."""

from fastapi import APIRouter, Depends

from backend.app.api.deps import enforce_rate_limit, get_current_user
from backend.app.core.rate_limit import search_limiter
from backend.app.schemas.search import (
    SearchFilterOptions,
    SearchRequest,
    SearchResponse,
)
from backend.app.schemas.user import UserPublic
from backend.app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    user: UserPublic = Depends(get_current_user),
) -> SearchResponse:
    """Run a semantic, keyword or hybrid search over the legal corpus."""

    enforce_rate_limit(search_limiter, f"search:{user.user_id}")

    service = SearchService()
    result = service.search(payload)

    return SearchResponse(
        query=result["query"],
        mode=result["mode"],
        total=result["total"],
        results=service.to_results(result["results"]),
    )


@router.get("/filters", response_model=SearchFilterOptions)
def filters(user: UserPublic = Depends(get_current_user)) -> SearchFilterOptions:
    """Return available court types, acts and categories for filtering."""

    return SearchService().filter_options()
