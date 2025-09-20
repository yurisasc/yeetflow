"""Local file system storage backend."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import UUID

from app.config import settings
from app.services.artifact.errors import ArtifactAccessError
from app.services.artifact.storage import StorageBackend

logger = logging.getLogger(__name__)


class LocalFileStorage(StorageBackend):
    """Local file system storage backend for artifacts."""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path or settings.artifacts_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _validate_filename(self, filename: str) -> str:
        """Validate and sanitize filename to prevent path traversal."""
        # Extract just the basename to remove any path separators or
        # parent references
        safe_name = Path(filename).name

        # Ensure we got a valid filename after sanitization
        if not safe_name:
            error_msg = "Invalid filename provided"
            raise ArtifactAccessError(error_msg) from None

        return safe_name

    async def store(self, run_id: UUID, filename: str, content: bytes) -> str:
        """Store artifact in local file system."""
        try:
            # Create run-specific directory
            run_dir = self.base_path / str(run_id)
            run_dir.mkdir(parents=True, exist_ok=True)

            # Validate and sanitize filename
            safe_name = self._validate_filename(filename)

            # Construct target path within run directory
            target_path = run_dir / safe_name

            # Resolve both paths to absolute paths for security check
            resolved_run_dir = run_dir.resolve()
            resolved_target = target_path.resolve()

            # Security check: ensure target is within run directory
            # This prevents path traversal even if Path.name didn't catch everything
            try:
                resolved_target.relative_to(resolved_run_dir)
            except ValueError as err:
                logger.warning(
                    "Path traversal attempt blocked: %s -> %s",
                    filename,
                    str(resolved_target),
                )
                error_msg = "Invalid filename: path traversal not allowed"
                raise ArtifactAccessError(error_msg) from err

            # Only write the file after all security checks pass
            target_path.write_bytes(content)

            return str(resolved_target)

        except Exception as e:
            logger.exception("Failed to store artifact for run %s", run_id)
            error_msg = "Failed to store artifact"
            raise ArtifactAccessError(error_msg) from e

    async def retrieve(self, storage_uri: str) -> AsyncGenerator[bytes, None]:
        """Retrieve artifact from local file system."""

        def _validate_and_check_file():
            """Validate file path and check existence."""
            # Validate path is within base directory (security check)
            try:
                file_path.relative_to(base_path)
            except ValueError:
                logger.warning("Path traversal attempt: %s", storage_uri)
                error_msg = "Invalid file path"
                raise ArtifactAccessError(error_msg) from None

            if not file_path.exists():
                error_msg = "File not found"
                raise ArtifactAccessError(error_msg) from None

            if not file_path.is_file():
                error_msg = "Path is not a file"
                raise ArtifactAccessError(error_msg) from None

        chunk_size = 8192

        try:
            file_path = Path(storage_uri)

            # Resolve to absolute path
            file_path = file_path.resolve()
            base_path = self.base_path.resolve()

            _validate_and_check_file()

            # Use thread pool for async file I/O to avoid blocking
            loop = asyncio.get_running_loop()
            with file_path.open("rb") as f:
                while True:
                    chunk = await loop.run_in_executor(None, f.read, chunk_size)
                    if not chunk:
                        break
                    yield chunk

        except Exception as e:
            error_msg = "Failed to retrieve artifact"
            logger.exception(error_msg)
            raise ArtifactAccessError(error_msg) from e

    async def exists(self, storage_uri: str) -> bool:
        """Check if artifact exists."""
        try:
            file_path = Path(storage_uri)
            file_path = file_path.resolve()
            base_path = self.base_path.resolve()

            # Validate path is within base directory
            try:
                file_path.relative_to(base_path)
            except ValueError:
                return False

            return file_path.exists() and file_path.is_file()
        except (OSError, ValueError):
            return False

    async def delete(self, storage_uri: str) -> bool:
        """Delete artifact from local file system."""

        def _delete_file():
            """Delete the file if it exists."""
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False

        try:
            file_path = Path(storage_uri)
            file_path = file_path.resolve()
            base_path = self.base_path.resolve()

            # Validate path is within base directory
            try:
                file_path.relative_to(base_path)
            except ValueError:
                return False

            return _delete_file()
        except (OSError, ValueError):
            logger.exception("Failed to delete artifact")
            return False

    async def get_file_info(self, storage_uri: str) -> tuple[str, int]:
        """Get filename and file size."""
        error_msg = "Failed to get file info"

        def _validate_file():
            """Validate file existence and type."""
            if not file_path.exists():
                error_msg = "File not found"
                raise ArtifactAccessError(error_msg) from None

            if not file_path.is_file():
                error_msg = "Path is not a file"
                raise ArtifactAccessError(error_msg) from None

            return file_path.name, file_path.stat().st_size

        try:
            file_path = Path(storage_uri)
            file_path = file_path.resolve()
            base_path = self.base_path.resolve()

            # Validate path is within base directory
            try:
                file_path.relative_to(base_path)
            except ValueError:
                error_msg = "Invalid file path"
                raise ArtifactAccessError(error_msg) from None

            return _validate_file()
        except Exception as e:
            logger.exception(error_msg)
            raise ArtifactAccessError(error_msg) from e
