"""Legal procedure routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.deps import get_current_user
from backend.app.schemas.procedure import Procedure, ProcedureListResponse
from backend.app.schemas.user import UserPublic
from backend.app.services.procedure_service import ProcedureService

router = APIRouter(prefix="/procedures", tags=["Legal Procedures"])


@router.get("", response_model=ProcedureListResponse)
def list_procedures(
    category: Optional[str] = None,
    q: Optional[str] = Query(default=None, max_length=200),
    user: UserPublic = Depends(get_current_user),
) -> ProcedureListResponse:
    """List legal procedures, required documents and government forms."""

    procedures = ProcedureService().list_procedures(category=category, query=q)

    return ProcedureListResponse(total=len(procedures), procedures=procedures)


@router.get("/{document_id}", response_model=Procedure)
def get_procedure(
    document_id: str,
    user: UserPublic = Depends(get_current_user),
) -> Procedure:
    """Return a single legal procedure."""

    procedure = ProcedureService().get_procedure(document_id)

    if procedure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure not found.",
        )

    return procedure
