"""Admin dashboard, user management, datasets and reports routes."""

from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import get_current_user, require_admin
from backend.app.core.logging_config import get_logger
from backend.app.schemas.admin import AdminStats, SystemReport
from backend.app.schemas.common import Message
from backend.app.schemas.document import DocumentListResponse
from backend.app.schemas.user import AdminUserUpdateRequest, UserListResponse, UserPublic
from backend.app.services.admin_service import AdminService
from backend.app.services.document_service import DocumentService
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = get_logger(__name__)


def admin_user(user: UserPublic = Depends(get_current_user)) -> UserPublic:
    """Dependency that requires the admin role."""

    return require_admin(user)


@router.get("/stats", response_model=AdminStats)
def stats(user: UserPublic = Depends(admin_user)) -> AdminStats:
    """Aggregate system statistics for the dashboard."""

    return AdminService().stats()


@router.get("/report", response_model=SystemReport)
def report(user: UserPublic = Depends(admin_user)) -> SystemReport:
    """Generate a system report with breakdowns."""

    return AdminService().report()


@router.get("/users", response_model=UserListResponse)
def list_users(user: UserPublic = Depends(admin_user)) -> UserListResponse:
    """List all registered users."""

    users = UserService().list_users()

    return UserListResponse(total=len(users), users=users)


@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(
    user_id: str,
    payload: AdminUserUpdateRequest,
    user: UserPublic = Depends(admin_user),
) -> UserPublic:
    """Update a user's role or activation status."""

    service = UserService()

    try:
        updated = service.admin_update(
            user_id,
            role=payload.role,
            is_active=payload.is_active,
            full_name=payload.full_name,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return updated


@router.delete("/users/{user_id}", response_model=Message)
def delete_user(
    user_id: str,
    user: UserPublic = Depends(admin_user),
) -> Message:
    """Delete a user account."""

    if user_id == user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )

    if not UserService().delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return Message(detail="User deleted.")


@router.get("/datasets", response_model=DocumentListResponse)
def list_datasets(user: UserPublic = Depends(admin_user)) -> DocumentListResponse:
    """List all ingested datasets (documents)."""

    documents = DocumentService().list_documents()

    return DocumentListResponse(total=len(documents), documents=documents)


@router.post("/datasets/rebuild")
def rebuild_datasets(user: UserPublic = Depends(admin_user)) -> dict:
    """Re-ingest every PDF found in the upload directory."""

    from ai.config.settings import settings

    service = DocumentService()
    upload_dir = Path(settings.UPLOAD_DIRECTORY)

    pdf_files = sorted(upload_dir.glob("*.pdf"))

    ingested: List[str] = []
    failed: List[dict] = []

    for pdf_path in pdf_files:

        try:
            result = service.ingest_upload(
                filename=pdf_path.name,
                content=pdf_path.read_bytes(),
                source_type="dataset_rebuild",
            )
            ingested.append(result["document_id"])
        except Exception as error:  # noqa: BLE001 - report per-file failures
            logger.warning("Rebuild failed for %s: %s", pdf_path.name, error)
            failed.append({"file": pdf_path.name, "error": str(error)})

    return {
        "detail": "Dataset rebuild complete.",
        "ingested": len(ingested),
        "failed": len(failed),
        "documents": ingested,
        "errors": failed,
    }
