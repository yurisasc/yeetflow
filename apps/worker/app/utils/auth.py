import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.db import get_db_session
from app.models import User, UserRole

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token settings
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def _raise_unauthorized(detail: str) -> None:
    """Helper function to raise HTTP 401 Unauthorized exceptions."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


# OAuth2 scheme for token extraction with enhanced documentation
oauth2_scheme = HTTPBearer(
    scheme_name="JWT",
    description="""JWT Bearer token for authentication.
    Include your JWT token in the Authorization header as: Bearer {token}""",
    auto_error=False,
)

# Optional OAuth2 scheme for endpoints that might not require authentication
oauth2_scheme_optional = HTTPBearer(
    scheme_name="JWT",
    description="""Optional JWT Bearer token for authentication.
    Include your JWT token in the Authorization header as: Bearer {token}""",
    auto_error=False,
)

oauth2_scheme_optional_dep = Depends(oauth2_scheme_optional)
get_db_session_dep = Depends(get_db_session)
oauth2_scheme_dep = Depends(oauth2_scheme)


class Token(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 OAuth2 standard token type


class TokenData(BaseModel):
    """Token payload data."""

    user_id: UUID | None = None
    email: str | None = None
    role: UserRole | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire,
            "type": "access",
            "iat": datetime.now(UTC),  # Issued at time
            "jti": str(uuid4()),  # Unique token ID
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token with longer expiry."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
            "iat": datetime.now(UTC),  # Issued at time
            "jti": str(uuid4()),  # Unique token ID
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT access token."""

    def _raise_unauthorized(detail: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if this is actually an access token
        token_type = payload.get("type")
        if token_type != "access":  # noqa: S105
            logger.warning("Invalid token type for access: %s", token_type)
            _raise_unauthorized("Invalid token type")

        # Get and validate user_id as UUID
        sub = payload.get("sub")
        if sub is None:
            _raise_unauthorized("Token missing user ID")

        try:
            user_id = UUID(sub)
        except (ValueError, TypeError):
            logger.warning("Invalid UUID format in token sub claim: %s", sub)
            _raise_unauthorized("Invalid token format")

        email: str | None = payload.get("email")
        role: str | None = payload.get("role")

        # Convert role string back to enum
        user_role = None
        if role:
            try:
                user_role = UserRole(role)
            except ValueError:
                logger.warning("Invalid role in token: %s", role)
                user_role = UserRole.USER

        return TokenData(user_id=user_id, email=email, role=user_role)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except PyJWTError as e:
        logger.exception("JWT verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def verify_refresh_token(token: str) -> TokenData:
    """Verify and decode a refresh JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if this is actually a refresh token
        token_type = payload.get("type")
        if token_type != "refresh":  # noqa: S105 OAuth2 standard token type
            logger.warning("Invalid token type for refresh: %s", token_type)
            _raise_unauthorized("Invalid token type")

        # Get and validate user_id as UUID
        sub = payload.get("sub")
        if sub is None:
            _raise_unauthorized("Token missing user ID")

        try:
            user_id = UUID(sub)
        except (ValueError, TypeError):
            logger.warning("Invalid UUID format in refresh token sub claim: %s", sub)
            _raise_unauthorized("Invalid token format")

        email: str | None = payload.get("email")
        role: str | None = payload.get("role")

        # Convert role string back to enum
        user_role = None
        if role:
            try:
                user_role = UserRole(role)
            except ValueError:
                logger.warning("Invalid role in refresh token: %s", role)
                user_role = UserRole.USER

        return TokenData(user_id=user_id, email=email, role=user_role)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except PyJWTError as e:
        logger.exception("Refresh token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    token: HTTPAuthorizationCredentials | None = oauth2_scheme_dep,
    session: AsyncSession = get_db_session_dep,
) -> User:
    """Get the current authenticated user from JWT token."""
    # Check if Authorization header is present
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def _raise_credentials_exception() -> None:
        raise credentials_exception

    try:
        # Extract token from HTTPBearer
        token_data = verify_token(token.credentials)

        if token_data.user_id is None:
            _raise_credentials_exception()

        # Fetch user from database
        result = await session.execute(
            select(User).where(User.id == token_data.user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning("User %s not found in database", token_data.user_id)
            _raise_credentials_exception()

        logger.debug("Authenticated user: %s (%s)", user.email, user.role)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.exception("Database error in get_current_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during authentication",
        ) from e
    else:
        return user


get_current_user_dep = Depends(get_current_user)


def check_admin_role(current_user: User = get_current_user_dep) -> User:
    """Check if the current user has admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


async def get_current_user_or_first_admin(
    token_data: HTTPAuthorizationCredentials | None = oauth2_scheme_optional_dep,
    session: AsyncSession = get_db_session_dep,
) -> User:
    """Get current user, or allow first user registration without auth."""
    try:
        # First check if any users exist

        result = await session.execute(select(User).limit(1))
        existing_user = result.scalar_one_or_none()

        # If no users exist, allow registration without authentication
        if existing_user is None:
            # Return a dummy admin user for the first registration
            return User(
                id=uuid4(),
                email="system@yeetflow.local",
                name="System Admin",
                role=UserRole.ADMIN,
            )

        # If users exist, require normal authentication
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify the token
        token_data_obj = verify_token(token_data.credentials)

        if token_data_obj.user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch user from database
        result = await session.execute(
            select(User).where(User.id == token_data_obj.user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning("User %s not found in database", token_data_obj.user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except PyJWTError as e:
        logger.exception("JWT verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    else:
        logger.debug("Authenticated user: %s (%s)", user.email, user.role)
        return user


get_current_user_or_first_admin_dep = Depends(get_current_user_or_first_admin)


async def require_admin_or_first_user(
    current_user: User = get_current_user_or_first_admin_dep,
) -> User:
    """Require admin role, or allow first user registration."""
    # If this is the dummy admin user (first registration), allow it
    if current_user.email == "system@yeetflow.local":
        return current_user

    # Otherwise, check for admin role
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
