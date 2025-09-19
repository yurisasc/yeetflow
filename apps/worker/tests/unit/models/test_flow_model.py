import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Flow, FlowCreate, FlowRead, User

# Test constants
FLOW_CREATOR_PASSWORD = "flowcreator_password_hash"
FLOW_CONSTRAINT_PASSWORD = "flowconstraint_password_hash"
FLOW_SERIALIZE_PASSWORD = "flowserialize_password_hash"


@pytest.mark.unit
class TestFlowModel:
    """Unit tests for Flow model operations."""

    async def test_create_flow_with_json_config(self, session):
        """Test creating Flow with JSON config."""
        # Create user first (required for created_by field)
        user = User(
            email="flowcreator@example.com", password_hash=FLOW_CREATOR_PASSWORD
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        flow_data = FlowCreate(
            key="test-flow",
            name="Test Flow",
            description="A test flow",
            config={
                "browser": "chrome",
                "timeout": 30,
                "steps": ["navigate", "click", "wait"],
            },
        )

        flow = Flow(**flow_data.model_dump())
        flow.created_by = user.id  # Set the required created_by field
        session.add(flow)
        await session.commit()
        await session.refresh(flow)

        # Verify JSON round-trip
        assert flow.config == flow_data.config
        assert flow.key == flow_data.key
        assert flow.name == flow_data.name
        assert flow.description == flow_data.description
        assert flow.created_by == user.id

    async def test_flow_key_unique_constraint(self, session):
        """Test that flow key field enforces uniqueness."""
        # Create user first
        user = User(
            email="flowconstraint@example.com", password_hash=FLOW_CONSTRAINT_PASSWORD
        )
        session.add(user)
        await session.commit()

        # Create first flow
        flow1 = Flow(key="unique-key", name="Flow 1", created_by=user.id)
        session.add(flow1)
        await session.commit()

        # Try to create flow with same key
        flow2 = Flow(key="unique-key", name="Flow 2", created_by=user.id)
        session.add(flow2)

        with pytest.raises(IntegrityError):
            await session.commit()

    async def test_flow_serialization(self, session):
        """Test Flow serialization to API models."""
        # Create user first
        user = User(
            email="flowserialize@example.com", password_hash=FLOW_SERIALIZE_PASSWORD
        )
        session.add(user)
        await session.commit()

        flow = Flow(
            key="serialize-flow",
            name="Serialize Flow",
            description="For serialization testing",
            config={"test": "config"},
            created_by=user.id,
        )
        session.add(flow)
        await session.commit()
        await session.refresh(flow)

        flow_read = FlowRead.model_validate(flow)

        assert flow_read.id == flow.id
        assert flow_read.key == flow.key
        assert flow_read.name == flow.name
        assert flow_read.description == flow.description
        assert flow_read.created_by == flow.created_by
        assert flow_read.created_at == flow.created_at
        assert flow_read.updated_at == flow.updated_at
