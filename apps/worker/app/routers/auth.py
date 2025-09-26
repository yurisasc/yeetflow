import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants import BOOTSTRAP_USER_EMAIL
from app.db import get_db_session
from app.models import User, UserCreate, UserRead, UserRole
from app.services.auth import AuthService
from app.utils.auth import (
    Token,
    WebLoginResponse,
    WebLoginUser,
    check_admin_role,
    get_current_user,
    require_admin_or_first_user,
)

# Module-level dependencies
get_db_session_dep = Depends(get_db_session)
require_admin_or_first_user_dep = Depends(require_admin_or_first_user)
oauth2_form_dep = Depends(OAuth2PasswordRequestForm)
get_current_user_dep = Depends(get_current_user)
check_admin_role_dep = Depends(check_admin_role)

logger = logging.getLogger(__name__)

router = APIRouter()


class UpdateUserRole(BaseModel):
    new_role: UserRole


@router.post(
    "/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = get_db_session_dep,
    current_user: User = require_admin_or_first_user_dep,
):
    """Register a new user. First user becomes admin automatically."""
    auth_service = AuthService()

    try:
        # For first user registration, pass None as creator_role
        # The service will validate this is truly the first user
        creator_role = (
            None if current_user.email == BOOTSTRAP_USER_EMAIL else current_user.role
        )

        # Create the user with role-based permissions
        user = await auth_service.create_user(user_data, session, creator_role)

        return UserRead.model_validate(user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception("Error registering user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        ) from e


@router.post(
    "/auth/login",
    response_model=Token | WebLoginResponse,
    openapi_extra={
        "parameters": [
            {
                "name": "X-Client-Type",
                "in": "header",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["web", "mobile"],
                    "default": "web",
                    "description": (
                        "Client type for hybrid authentication. 'web' returns cookies,"
                        "'mobile' returns tokens in response body."
                    ),
                },
            }
        ]
    },
)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = oauth2_form_dep,
    session: AsyncSession = get_db_session_dep,
):
    """Authenticate user and return JWT tokens (OAuth2 compatible)."""
    auth_service = AuthService()
    user = await auth_service.authenticate_user(
        form_data.username, form_data.password, session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = auth_service.create_user_tokens(user)

    # Check client type for hybrid authentication
    client_type = request.headers.get("X-Client-Type", "web").lower()

    if client_type == "mobile":
        # Mobile clients get full token response with expiry details
        logger.info("User %s logged in successfully (mobile client)", user.email)
        return tokens

    # Web clients get HttpOnly cookies (default behavior)
    # Set HttpOnly cookies for tokens using configurable settings
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.cookie_max_age or tokens.expires_in,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.cookie_max_age or tokens.refresh_expires_in,
    )

    logger.info("User %s logged in successfully (web client)", user.email)
    return WebLoginResponse(
        message="Login successful",
        user=WebLoginUser(email=user.email, role=user.role.value),
    )


@router.post("/auth/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True),
    session: AsyncSession = get_db_session_dep,
):
    """Refresh access token using a valid refresh token."""
    auth_service = AuthService()
    try:
        return await auth_service.refresh_user_tokens(refresh_token, session)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except (ExpiredSignatureError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        logger.exception("Error refreshing token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token",
        ) from e


@router.get("/auth/me", response_model=UserRead)
async def get_current_user_info(current_user: User = get_current_user_dep):
    """Get current authenticated user information."""
    return UserRead.model_validate(current_user)


@router.get("/auth/users", response_model=list[UserRead])
async def get_all_users(
    session: AsyncSession = get_db_session_dep,
    _: User = check_admin_role_dep,  # Only admins can access
):
    """Get all users (admin only)."""
    auth_service = AuthService()
    return await auth_service.get_all_users(session)


@router.patch("/auth/users/{user_id}/role", response_model=UserRead)
async def update_user_role(
    user_id: UUID,
    payload: UpdateUserRole,
    session: AsyncSession = get_db_session_dep,
    current_user: User = check_admin_role_dep,  # Only admins can update roles
):
    """Update a user role (admin only)."""
    auth_service = AuthService()

    try:
        updated_user = await auth_service.update_user_role(
            user_id, payload.new_role, session, current_user.role
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            ) from None

        return UserRead.model_validate(updated_user)

    except ValueError as e:
        # Handle permission errors (non-admin trying to update)
        if "Only administrators" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
            ) from e
        # Handle other validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
