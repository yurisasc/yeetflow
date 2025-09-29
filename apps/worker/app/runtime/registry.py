"""Flow registry for loading and managing flow manifests."""

import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger(__name__)


class FlowManifest(BaseModel):
    """Schema for flow manifest files."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

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
        self._by_key: dict[str, FlowManifest] = {}
        self._load_all_manifests()

    def _load_all_manifests(self) -> None:
        """Load all flow manifests from the flows directory."""
        if not self.flows_dir.exists():
            logger.warning("Flows directory %s does not exist", self.flows_dir)
            return

        patterns = ("*/manifest.yaml", "*/manifest.yml")
        for pattern in patterns:
            for manifest_file in sorted(self.flows_dir.glob(pattern)):
                try:
                    manifest = self._load_manifest(manifest_file)
                    if manifest is None:
                        continue
                    if manifest.id in self._manifests:
                        logger.warning(
                            "Duplicate flow id '%s' from %s ignored",
                            manifest.id,
                            manifest_file,
                        )
                        continue
                    if manifest.key in self._by_key:
                        logger.warning(
                            "Duplicate flow key '%s' from %s ignored",
                            manifest.key,
                            manifest_file,
                        )
                        continue
                    self._manifests[manifest.id] = manifest
                    self._by_key[manifest.key] = manifest
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
        return self._by_key.get(flow_key)

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
        self._by_key.clear()
        self._load_all_manifests()
