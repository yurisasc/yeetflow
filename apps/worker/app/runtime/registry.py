"""Flow registry for loading and managing flow manifests."""

import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class FlowManifest(BaseModel):
    """Schema for flow manifest files."""

    id: str
    name: str
    key: str
    description: str | None = None
    config: dict = Field(default_factory=dict)


class FlowRegistry:
    """Registry for loading and managing flows."""

    def __init__(self, flows_dir: Path):
        self.flows_dir = flows_dir
        self._manifests: dict[str, FlowManifest] = {}
        self._load_all_manifests()

    def _load_all_manifests(self) -> None:
        """Load all flow manifests from the flows directory."""
        if not self.flows_dir.exists():
            logger.warning("Flows directory %s does not exist", self.flows_dir)
            return

        for manifest_file in self.flows_dir.glob("*/manifest.yaml"):
            try:
                manifest = self._load_manifest(manifest_file)
                if manifest:
                    self._manifests[manifest.id] = manifest
                    logger.info("Loaded flow manifest: %s", manifest.id)
            except Exception:
                logger.exception("Failed to load manifest %s", manifest_file)

    def _load_manifest(self, manifest_path: Path) -> FlowManifest | None:
        """Load a single manifest file."""
        try:
            with Path.open(manifest_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            return FlowManifest(**data)
        except (FileNotFoundError, yaml.YAMLError, ValidationError):
            logger.exception("Error loading manifest %s", manifest_path)
            return None

    def get_manifest(self, flow_id: str) -> FlowManifest | None:
        """Get a flow manifest by ID."""
        return self._manifests.get(flow_id)

    def get_manifest_by_key(self, flow_key: str) -> FlowManifest | None:
        """Get a flow manifest by key."""
        for manifest in self._manifests.values():
            if manifest.key == flow_key:
                return manifest
        return None

    def list_flows(self) -> list[FlowManifest]:
        """List all available flows."""
        return list(self._manifests.values())

    def validate_manifest(self, manifest_data: dict) -> FlowManifest:
        """Validate manifest data and return a FlowManifest instance."""
        try:
            return FlowManifest(**manifest_data)
        except ValidationError:
            logger.exception("Invalid manifest data")
            raise

    def reload_manifests(self) -> None:
        """Reload all manifests from disk."""
        self._manifests.clear()
        self._load_all_manifests()
