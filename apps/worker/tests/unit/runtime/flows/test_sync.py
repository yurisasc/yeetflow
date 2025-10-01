import pytest
from sqlalchemy import select

from app.models import Flow, FlowVisibility, User, UserRole
from app.runtime.flows.registry import FlowManifest
from app.runtime.flows.sync import _manifest_to_uuid, sync_flows_from_registry


class StubRegistry:
    """Simple registry stub returning provided manifests."""

    def __init__(self, manifests: list[FlowManifest]):
        self._manifests = manifests

    def list_flows(self) -> list[FlowManifest]:
        return list(self._manifests)


@pytest.mark.unit
class TestSyncFlowsFromRegistry:
    """Unit tests for registry synchronization logic."""

    async def test_creates_public_flow_for_new_manifest(self, session):
        """New manifests should create public flows owned by resolved owner."""

        admin = User(
            email="admin@example.com",
            password_hash="hashed",
            role=UserRole.ADMIN,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        manifest = FlowManifest(
            id="550e8400-e29b-41d4-a716-44665544aaaa",
            key="stub-flow",
            name="Stub Flow",
            description="Created from manifest",
            config={"foo": "bar"},
        )

        registry = StubRegistry([manifest])

        await sync_flows_from_registry(session, registry)

        result = await session.execute(select(Flow).where(Flow.key == manifest.key))
        flow = result.scalar_one()

        assert flow.visibility == FlowVisibility.PUBLIC
        assert flow.created_by == admin.id
        assert flow.name == manifest.name
        assert flow.description == manifest.description
        assert flow.config == manifest.config

    async def test_updates_existing_flow_to_public_visibility(self, session):
        """Existing flows should be forced to public visibility during sync."""

        admin = User(
            email="admin@example.com",
            password_hash="hashed",
            role=UserRole.ADMIN,
        )
        owner = User(
            email="owner@example.com",
            password_hash="hashed-owner",
            role=UserRole.USER,
        )
        session.add_all([admin, owner])
        await session.commit()
        await session.refresh(owner)

        manifest = FlowManifest(
            id="550e8400-e29b-41d4-a716-44665544bbbb",
            key="existing-flow",
            name="Updated Flow Name",
            description="Updated description",
            config={"step": "updated"},
        )

        existing_flow = Flow(
            id=_manifest_to_uuid(manifest),
            key="existing-flow",
            name="Existing Flow",
            description="Original description",
            created_by=owner.id,
            visibility=FlowVisibility.PRIVATE,
        )
        session.add(existing_flow)
        await session.commit()
        await session.refresh(existing_flow)

        registry = StubRegistry([manifest])

        await sync_flows_from_registry(session, registry)

        result = await session.execute(select(Flow).where(Flow.id == existing_flow.id))
        flow = result.scalar_one()

        assert flow.id == existing_flow.id
        assert flow.visibility == FlowVisibility.PUBLIC
        assert flow.created_by == owner.id
        assert flow.name == manifest.name
        assert flow.description == manifest.description
        assert flow.config == manifest.config
