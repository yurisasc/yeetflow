import asyncio

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Flow, User, UserRole


async def seed_e2e_flows() -> None:
    """Seed sample flows for E2E testing."""
    async with AsyncSessionLocal() as session:
        # Ensure there is at least one admin (created by first signup)
        admin_id = None
        max_attempts = 10
        delay_seconds = 0.5

        for attempt in range(max_attempts):
            admin_row = await session.execute(
                select(User.id).where(User.role == UserRole.ADMIN).limit(1)
            )
            admin_id = admin_row.scalar_one_or_none()
            if admin_id:
                break
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay_seconds)

        if not admin_id:
            # No admin yet; flows will be created after the first signup
            return

        # Only seed if there are no flows yet
        any_flow = await session.execute(select(Flow.id).limit(1))
        if any_flow.scalar_one_or_none():
            return

        session.add_all(
            [
                Flow(
                    key="test-flow",
                    name="Test Flow",
                    description="A test flow for E2E validation",
                    created_by=admin_id,
                ),
                Flow(
                    key="hitl-flow",
                    name="HITL Flow",
                    description="Human-in-the-loop demo flow",
                    created_by=admin_id,
                ),
            ]
        )
        await session.commit()
