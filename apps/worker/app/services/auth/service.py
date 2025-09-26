import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import User, UserCreate, UserRead, UserRole
from app.utils.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    Token,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling user authentication and authorization."""

    def __init__(self):
        """Initialize the auth service."""

    async def create_user(
        self,
        user_data: UserCreate,
        session: AsyncSession,
        creator_role: UserRole | None = None,
    ) -> User:
        """Create a new user with role-based permissions."""
        # Check if this is truly the first user within the transaction
        result = await session.execute(select(func.count(User.id)))
        user_count = result.scalar()

        # Handle first user scenario
        if user_count == 0:
            # This is truly the first user, they automatically become admin
            # creator_role should be None for first user (validated by caller)
            if creator_role is not None:
                error_msg = "First user registration must not have a creator"
                logger.error(error_msg)
                raise ValueError(error_msg)
            role = UserRole.ADMIN
            logger.info("Creating first user as admin")
        else:
            # Subsequent users require a creator with proper permissions
            if creator_role is None:
                error_msg = "Creator role required for non-first user registration"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Only admins can create users with ADMIN role
            if (
                user_data.role
                and user_data.role == UserRole.ADMIN
                and creator_role != UserRole.ADMIN
            ):
                error_msg = "Only administrators can create admin users"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Default role if not specified
            role = user_data.role or UserRole.USER

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create user instance
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=hashed_password,
            role=role,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        logger.info("Created user: %s with role: %s", user.email, user.role)
        return user

    async def authenticate_user(
        self, email: str, password: str, session: AsyncSession
    ) -> User | None:
        """Authenticate a user with email and password."""
        # Find user by email
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Verify password
        if not verify_password(password, user.password_hash):
            return None

        return user

    def create_user_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for a user."""
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Calculate expiry times
        now = datetime.now(UTC)
        access_expires_at = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert minutes to seconds
        refresh_expires_in = (
            REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )  # Convert days to seconds

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            refresh_expires_in=refresh_expires_in,
            access_token_expires_at=access_expires_at,
            refresh_token_expires_at=refresh_expires_at,
        )

    async def refresh_user_tokens(
        self, refresh_token: str, session: AsyncSession
    ) -> Token:
        """Refresh user tokens using a valid refresh token."""
        # Verify the refresh token
        token_data = verify_refresh_token(refresh_token)

        if token_data.user_id is None:
            error_msg = "Invalid refresh token: missing user ID"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get the user from the database to ensure they still exist
        user = await self.get_user_by_id(token_data.user_id, session)
        if not user:
            error_msg = "User not found"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Create new tokens for the user
        logger.info("Refreshing tokens for user: %s", user.email)
        return self.create_user_tokens(user)

    async def get_user_by_id(self, user_id: UUID, session: AsyncSession) -> User | None:
        """Get a user by ID."""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_all_users(self, session: AsyncSession) -> list[UserRead]:
        """Get all users (admin only)."""
        # Select only the columns needed for UserRead to avoid loading password_hash
        result = await session.execute(
            select(
                User.id,
                User.email,
                User.name,
                User.role,
                User.created_at,
                User.updated_at,
            )
        )
        rows = result.all()

        return [
            UserRead(
                id=row.id,
                email=row.email,
                name=row.name,
                role=row.role,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    async def update_user_role(
        self,
        user_id: UUID,
        new_role: UserRole,
        session: AsyncSession,
        updater_role: UserRole,
    ) -> User | None:
        """Update a user's role (admin only)."""
        # Only admins can update roles
        if updater_role != UserRole.ADMIN:
            error_msg = "Only administrators can update user roles"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get the user
        user = await self.get_user_by_id(user_id, session)
        if not user:
            return None

        # Update the role
        user.role = new_role
        session.add(user)
        await session.commit()
        await session.refresh(user)

        logger.info("Updated user %s role to %s", user.email, new_role)
        return user
