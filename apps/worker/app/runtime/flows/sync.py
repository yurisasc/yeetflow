"""Utilities for synchronizing flow manifests into the database."""

from __future__ import annotations

import logging
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Flow, FlowVisibility, User, UserRole

from .registry import FlowManifest, FlowRegistry

logger = logging.getLogger(__name__)


def _manifest_to_uuid(manifest: FlowManifest) -> UUID:
    """Resolve a deterministic UUID for a manifest.

    Prefers explicit UUID values in the manifest, otherwise derives one from the
    manifest id/key using UUID5 to maintain stability across deployments.
    """

    if manifest.id:
        try:
            return UUID(str(manifest.id))
        except (ValueError, TypeError):
            logger.debug("Manifest id %s is not a valid UUID", manifest.id)
    seed_value = manifest.id or manifest.key
    if not seed_value:
        error_msg = "Flow manifest must define at least one of 'id' or 'key'"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        seed = str(seed_value)
    except Exception as exc:
        error_msg = f"Failed to coerce manifest seed '{seed_value}' to string"
        logger.exception(error_msg)
        raise ValueError(error_msg) from exc

    return uuid5(NAMESPACE_URL, seed)


async def _pick_default_owner(session: AsyncSession) -> UUID | None:
    admin_row = await session.execute(
        select(User.id).where(User.role == UserRole.ADMIN).limit(1)
    )
    owner_id = admin_row.scalar_one_or_none()
    if owner_id is not None:
        return owner_id

    any_user_row = await session.execute(select(User.id).limit(1))
    return any_user_row.scalar_one_or_none()


def _prepare_manifests(registry: FlowRegistry) -> list[FlowManifest]:
    manifests = list(registry.list_flows())
    if not manifests:
        logger.info("No flow manifests discovered; skipping registry sync")
    return manifests


async def _resolve_owner(session: AsyncSession, owner_id: UUID | None) -> UUID | None:
    if owner_id is not None:
        return owner_id
    resolved = await _pick_default_owner(session)
    if resolved is None:
        logger.warning(
            "Unable to sync flows from registry: no users available to assign ownership"
        )
    return resolved


def _reconcile_flow(
    manifest: FlowManifest,
    flow: Flow | None,
    owner_id: UUID,
    session: AsyncSession,
) -> tuple[Flow | None, bool, bool]:
    """Create or update a flow record to match a manifest.

    Registry-managed manifests take precedence over existing records with the same
    key. Any matching flow is forced to `FlowVisibility.PUBLIC` so the catalog
    remains consistent with what the registry exposes.
    """

    manifest_uuid = _manifest_to_uuid(manifest)
    if flow is None:
        flow = Flow(
            id=manifest_uuid,
            key=manifest.key,
            name=manifest.name,
            description=manifest.description,
            config=manifest.config,
            visibility=FlowVisibility.PUBLIC,
            created_by=owner_id,
        )
        session.add(flow)
        return flow, True, False

    changed = False
    if flow.visibility != FlowVisibility.PUBLIC:
        flow.visibility = FlowVisibility.PUBLIC
        changed = True
    if flow.name != manifest.name:
        flow.name = manifest.name
        changed = True
    if flow.description != manifest.description:
        flow.description = manifest.description
        changed = True
    if flow.config != manifest.config:
        flow.config = manifest.config
        changed = True
    return flow, False, changed


async def sync_flows_from_registry(
    session: AsyncSession, registry: FlowRegistry, *, owner_id: UUID | None = None
) -> None:
    """Ensure flow manifests exist in the database.

    Creates or updates `Flow` rows based on the manifests discovered by the
    provided `FlowRegistry`. Newly created flows will be assigned to the
    supplied `owner_id` or the first available admin/user if omitted.
    """

    manifests = _prepare_manifests(registry)
    if not manifests:
        return

    resolved_owner = await _resolve_owner(session, owner_id)
    if resolved_owner is None:
        return

    existing_flows = await session.execute(select(Flow))
    flows_by_key = {flow.key: flow for flow in existing_flows.scalars()}

    created = 0
    updated = 0

    for manifest in manifests:
        flow = flows_by_key.get(manifest.key)
        flow, is_created, is_updated = _reconcile_flow(
            manifest, flow, resolved_owner, session
        )
        if is_created and flow is not None:
            flows_by_key[manifest.key] = flow
            created += 1
        elif is_updated:
            updated += 1

    if created or updated:
        await session.commit()
        logger.info(
            "Synchronized %s flow(s) from registry (%s created, %s updated)",
            created + updated,
            created,
            updated,
        )
    else:
        logger.info("Flow registry already in sync with database")
