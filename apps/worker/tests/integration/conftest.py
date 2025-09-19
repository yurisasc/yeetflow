import os

import pytest


def pytest_configure(config):
    """Configure pytest for integration tests."""
    # Mark CI environment
    config.ci_mode = os.getenv("CI", "").lower() in ("true", "1", "yes")


def pytest_collection_modifyitems(config, items):  # noqa: ARG001
    """Modify test collection to skip xfail tests to save time."""
    # Skip tests marked as xfail to save time (they test unimplemented features)
    for item in items:
        if item.get_closest_marker("xfail"):
            item.add_marker(
                pytest.mark.skip(reason="Skipping xfail test (unimplemented feature)")
            )


@pytest.fixture(scope="session")
def is_ci_mode():
    """Fixture to check if running in CI mode."""
    return os.getenv("CI", "").lower() in ("true", "1", "yes")
