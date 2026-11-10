"""Legal case / judgment routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.deps import get_current_user
from backend.app.schemas.case import (
    CaseDetail,
    CaseFilterOptions,
    CaseListResponse,
)
from backend.app.schemas.user import UserPublic
from backend.app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["Legal Cases"])


@router.get("/filters", response_model=CaseFilterOptions)
def filters(user: UserPublic = Depends(get_current_user)) -> CaseFilterOptions:
    """Available court types and categories."""

    return CaseService().filter_options()


@router.get("", response_model=CaseListResponse)
def list_cases(
    court_type: Optional[str] = None,
    category: Optional[str] = None,
    q: Optional[str] = Query(default=None, max_length=200),
    user: UserPublic = Depends(get_current_user),
) -> CaseListResponse:
    """List judgments with optional filters."""

    cases = CaseService().list_cases(
        court_type=court_type,
        category=category,
        query=q,
    )

    return CaseListResponse(total=len(cases), cases=cases)


@router.get("/{document_id}", response_model=CaseDetail)
def get_case(
    document_id: str,
    user: UserPublic = Depends(get_current_user),
) -> CaseDetail:
    """Return full details of a judgment."""

    case = CaseService().get_case(document_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return case
