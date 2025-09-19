"""Storage abstraction layer for artifact persistence."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Protocol
from uuid import UUID


class ArtifactStorage(Protocol):
    """Protocol defining the storage interface for artifacts."""

    async def store(self, run_id: UUID, filename: str, content: bytes) -> str:
        """Store artifact content and return the storage URI/path."""
        ...

    async def retrieve(self, storage_uri: str) -> AsyncGenerator[bytes, None]:
        """Retrieve artifact content as async generator."""
        ...

    async def exists(self, storage_uri: str) -> bool:
        """Check if artifact exists in storage."""
        ...

    async def delete(self, storage_uri: str) -> bool:
        """Delete artifact from storage."""
        ...

    async def get_file_info(self, storage_uri: str) -> tuple[str, int]:
        """Get filename and file size for artifact."""
        ...


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def store(self, run_id: UUID, filename: str, content: bytes) -> str:
        """Store artifact content and return storage URI."""

    @abstractmethod
    async def retrieve(self, storage_uri: str) -> AsyncGenerator[bytes, None]:
        """Retrieve artifact content."""

    @abstractmethod
    async def exists(self, storage_uri: str) -> bool:
        """Check if artifact exists."""

    @abstractmethod
    async def delete(self, storage_uri: str) -> bool:
        """Delete artifact."""

    @abstractmethod
    async def get_file_info(self, storage_uri: str) -> tuple[str, int]:
        """Get file info."""
