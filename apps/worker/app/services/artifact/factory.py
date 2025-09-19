"""Factory for creating storage backends."""

from app.config import settings
from app.services.artifact.local_storage import LocalFileStorage
from app.services.artifact.storage import StorageBackend


def get_storage_backend() -> StorageBackend:
    """Get configured storage backend."""
    backend_type = settings.storage_backend.lower()

    if backend_type == "local":
        return LocalFileStorage()
    if backend_type == "s3":
        # Future: S3Storage implementation
        error_msg = "S3 storage not implemented yet"
        raise NotImplementedError(error_msg)
    error_msg = f"Unsupported storage backend: {backend_type}"
    raise ValueError(error_msg)


# Global storage backend instance
storage_backend = get_storage_backend()
