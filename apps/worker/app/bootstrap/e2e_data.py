import asyncio
import logging

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Flow, User, UserRole

logger = logging.getLogger(__name__)
_seed_tasks: set[asyncio.Task[None]] = set()


async def seed_e2e_flows() -> None:
    """Seed sample flows for E2E testing without blocking startup."""

    async def _wait_for_admin_and_seed() -> None:
        async with AsyncSessionLocal() as session:
            # Bail early if flows already exist
            existing_flow = await session.execute(select(Flow.id).limit(1))
            if existing_flow.scalar_one_or_none():
                logger.debug("E2E flows already seeded; skipping")
                return

            admin_id = None
            max_attempts = 120
            delay_seconds = 1.0

            for attempt in range(max_attempts):
                admin_row = await session.execute(
                    select(User.id).where(User.role == UserRole.ADMIN).limit(1)
                )
                admin_id = admin_row.scalar_one_or_none()
                if admin_id:
                    break
                logger.debug(
                    "Waiting for admin user before seeding flows (attempt %s/%s)",
                    attempt + 1,
                    max_attempts,
                )
                await asyncio.sleep(delay_seconds)

            if not admin_id:
                logger.warning(
                    "E2E flow seeding skipped - admin user not found after waiting"
                )
                return

            # Double-check no flows were added while we were waiting
            any_flow = await session.execute(select(Flow.id).limit(1))
            if any_flow.scalar_one_or_none():
                logger.debug("E2E flows seeded by another process; skipping")
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
            logger.info("Seeded default E2E flows")

    task = asyncio.create_task(_wait_for_admin_and_seed())
    _seed_tasks.add(task)
    task.add_done_callback(_seed_tasks.discard)
