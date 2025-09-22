"""Run-related utility functions."""

import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Run, User, UserRole
from app.services.run.errors import RunNotFoundError
from app.services.run.service import RunService

logger = logging.getLogger(__name__)


async def ensure_run_access(
    run_id: UUID,
    user: User,
    session: AsyncSession,
    run_service: RunService,
) -> Run:  # Run type
    """Ensure user has access to the specified run.

    Args:
        run_id: The run ID to check access for
        user: The current user
        session: Database session
        run_service: Run service instance

    Returns:
        The run object if access is granted

    Raises:
        HTTPException: If user doesn't have access to the run
        (404 Not Found to prevent enumeration)
    """
    try:
        run = await run_service.get_run(run_id, session)
        if run.user_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Run not found",
            )
    except RunNotFoundError as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Run not found",
        ) from e
    else:
        return run
