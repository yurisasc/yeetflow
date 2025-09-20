import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import User, UserCreate, UserRead

# Test constants
TEST_PASSWORD = "test_password_hash"
UNIQUE_PASSWORD_1 = "password1_hash"
UNIQUE_PASSWORD_2 = "password2_hash"
ADMIN_PASSWORD = "admin_password_hash"


@pytest.mark.unit
class TestUserModel:
    """Unit tests for User model operations."""

    async def test_create_and_fetch_user(self, session):
        """Test creating and fetching a User."""
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password=TEST_PASSWORD,
        )

        # Create user
        payload = user_data.model_dump(exclude={"password"})
        user = User(**payload, password_hash=user_data.password)  # Simulate hashing
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Fetch user
        stmt = select(User).where(User.email == user_data.email)
        result = await session.execute(stmt)
        fetched_user = result.scalar_one()

        assert fetched_user.email == user_data.email
        assert fetched_user.name == user_data.name
        assert fetched_user.password_hash == user_data.password
        assert fetched_user.role == "user"  # Default value
        assert fetched_user.id is not None

    async def test_user_email_unique_constraint(self, session):
        """Test that email field enforces uniqueness."""
        # Create first user
        user1 = User(email="unique@example.com", password_hash=UNIQUE_PASSWORD_1)
        session.add(user1)
        await session.commit()

        # Try to create user with same email - should fail
        user2 = User(email="unique@example.com", password_hash=UNIQUE_PASSWORD_2)
        session.add(user2)

        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()

    async def test_user_serialization(self, session):
        """Test User serialization to API models."""
        user = User(
            email="serialize@example.com",
            name="Serialize User",
            password_hash=ADMIN_PASSWORD,
            role="admin",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Test UserRead serialization
        user_read = UserRead.model_validate(user)

        assert user_read.email == user.email
        assert user_read.name == user.name
        assert user_read.role == user.role
        assert user_read.id == user.id
        assert user_read.created_at == user.created_at
        assert user_read.updated_at == user.updated_at
        # Sensitive field should not be included
        assert not hasattr(user_read, "password_hash")
