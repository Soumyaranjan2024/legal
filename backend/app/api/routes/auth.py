"""Authentication and account routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.app.api.deps import client_ip, enforce_rate_limit, get_current_user
from backend.app.core.logging_config import get_logger
from backend.app.core.rate_limit import login_limiter
from backend.app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from backend.app.schemas.common import Message
from backend.app.schemas.user import UserPublic
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest) -> TokenResponse:
    """Create a new account and return an access token."""

    service = UserService()

    try:
        record = service.register(payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    return TokenResponse(**service.issue_token(record))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request) -> TokenResponse:
    """Authenticate with email and password."""

    enforce_rate_limit(login_limiter, f"login:{client_ip(request)}")

    service = UserService()

    try:
        record = service.authenticate(payload.email, payload.password)
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    return TokenResponse(**service.issue_token(record))


@router.get("/me", response_model=UserPublic)
def me(user: UserPublic = Depends(get_current_user)) -> UserPublic:
    """Return the currently authenticated user."""

    return user


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """Issue a password-reset token.

    In production this token would be emailed. For this academic project it is
    returned so the reset flow is fully functional in the UI.
    """

    service = UserService()
    token = service.create_reset_token(payload.email)

    if token is None:
        # Do not reveal whether the email exists.
        return ForgotPasswordResponse(
            detail="If an account exists for this email, a reset link has been sent."
        )

    return ForgotPasswordResponse(
        detail="Reset token generated. Use it to set a new password.",
        reset_token=token,
    )


@router.post("/reset-password", response_model=Message)
def reset_password(payload: ResetPasswordRequest) -> Message:
    """Set a new password using a valid reset token."""

    service = UserService()

    if not service.reset_password(payload.token, payload.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    return Message(detail="Password updated successfully.")


@router.post("/change-password", response_model=Message)
def change_password(
    payload: ChangePasswordRequest,
    user: UserPublic = Depends(get_current_user),
) -> Message:
    """Change the password of the authenticated user."""

    service = UserService()

    if not service.change_password(
        user.user_id, payload.current_password, payload.new_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    return Message(detail="Password changed successfully.")
