"""Integration tests for flow execution with FlowRunner."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.agents.noop import NoopAgent
from app.models import Run, RunStatus
from app.runtime.runner import FlowRunner


@pytest.mark.asyncio
class TestFlowExecution:
    """Integration tests for flow execution behavior."""

    @pytest.fixture
    def sample_flow_manifest(self):
        """Sample flow manifest with actions and checkpoint."""
        return {
            "id": "test-flow-001",
            "name": "Test Flow",
            "key": "test-flow",
            "description": "A test flow with actions and checkpoint",
            "config": {
                "steps": [
                    {
                        "type": "action",
                        "name": "Navigate to website",
                        "action": {"type": "navigate", "url": "https://example.com"},
                    },
                    {
                        "type": "action",
                        "name": "Click button",
                        "action": {"type": "click", "selector": "#submit-button"},
                    },
                    {
                        "type": "checkpoint",
                        "name": "Human verification",
                        "reason": "Please verify the form was filled correctly",
                        "expected_action": "confirm",
                        "timeout": 300,
                    },
                    {
                        "type": "action",
                        "name": "Submit form",
                        "action": {"type": "click", "selector": "[type='submit']"},
                    },
                ]
            },
        }

    @pytest.fixture
    def mock_run_service(self):
        """Mock RunService for testing."""
        service = MagicMock()
        service.update_run_status = AsyncMock()
        return service

    @pytest.fixture
    def mock_steel_adapter(self):
        """Mock SteelBrowserAdapter for testing."""
        adapter = MagicMock()
        adapter.create_session = AsyncMock(return_value="https://test-session-url.com")
        adapter.get_session_info = MagicMock(return_value={"websocket_url": None})
        adapter.close_session = AsyncMock()
        return adapter

    @pytest.fixture
    async def flow_runner(self, mock_run_service, mock_steel_adapter):
        """Create FlowRunner with mocked dependencies."""
        return FlowRunner(mock_run_service, mock_steel_adapter)

    async def test_flow_executes_actions_and_stops_at_checkpoint(
        self, flow_runner, sample_flow_manifest, mock_run_service, mock_steel_adapter
    ):
        """Test that flow executes actions and properly stops at checkpoint."""
        # Create a test run
        run = Run(
            id="test-run-123",
            flow_id=sample_flow_manifest["id"],
            user_id="test-user-123",
            status=RunStatus.PENDING,
        )

        input_payload = {}

        # Execute the flow
        with patch("app.runtime.runner.create_browser_use_agent", return_value=None):
            await flow_runner.execute_flow(run, sample_flow_manifest, input_payload)

        # Verify Steel session was created
        mock_steel_adapter.create_session.assert_called_once_with(run.id)

        # Verify run status was updated to running
        mock_run_service.update_run_status.assert_any_call(run.id, "running")

        # Verify run status was updated to awaiting_input (not completed!)
        mock_run_service.update_run_status.assert_any_call(run.id, "awaiting_input")

        # Verify run was NOT marked as completed (should not be in call list)
        completed_calls = [
            call
            for call in mock_run_service.update_run_status.call_args_list
            if call[0][1] == "completed"
        ]
        assert len(completed_calls) == 0, (
            "Flow should not be marked as completed when paused at checkpoint"
        )

        # Verify session was closed
        mock_steel_adapter.close_session.assert_called_once_with(run.id)

    async def test_flow_completes_when_no_checkpoint(
        self, flow_runner, mock_run_service
    ):
        """Test that flow completes fully when there are no checkpoints."""
        # Flow manifest with only actions, no checkpoint
        simple_flow = {
            "id": "simple-flow-001",
            "name": "Simple Flow",
            "key": "simple-flow",
            "config": {
                "steps": [
                    {
                        "type": "action",
                        "name": "Navigate",
                        "action": {"type": "navigate", "url": "https://example.com"},
                    },
                    {
                        "type": "action",
                        "name": "Click",
                        "action": {"type": "click", "selector": "#button"},
                    },
                ]
            },
        }

        run = Run(
            id="simple-run-123",
            flow_id=simple_flow["id"],
            user_id="test-user-123",
            status=RunStatus.PENDING,
        )

        with patch("app.runtime.runner.create_browser_use_agent", return_value=None):
            await flow_runner.execute_flow(run, simple_flow, {})

        # Verify run was marked as completed
        mock_run_service.update_run_status.assert_any_call(run.id, "completed")

    async def test_flow_handles_action_execution_errors(
        self, flow_runner, sample_flow_manifest, mock_run_service
    ):
        """Test that flow properly handles errors during action execution."""
        # Create run
        run = Run(
            id="error-run-123",
            flow_id=sample_flow_manifest["id"],
            user_id="test-user-123",
            status=RunStatus.PENDING,
        )

        with (
            patch("app.runtime.runner.create_browser_use_agent", return_value=None),
            patch.object(
                NoopAgent, "click", new=AsyncMock(side_effect=Exception("Test error"))
            ),
        ):
            await flow_runner.execute_flow(run, sample_flow_manifest, {})

        # Verify run was marked as failed
        mock_run_service.update_run_status.assert_any_call(
            run.id, "failed", error="Test error"
        )

    async def test_checkpoint_emits_proper_event_data(
        self, flow_runner, sample_flow_manifest
    ):
        """Test that checkpoint emits event with correct data structure."""
        run = Run(
            id="checkpoint-run-123",
            flow_id=sample_flow_manifest["id"],
            user_id="test-user-123",
            status=RunStatus.PENDING,
        )

        # Mock the event emitter to capture emitted events
        mock_event_emitter = MagicMock()
        for method_name in [
            "emit_run_started",
            "emit_step_started",
            "emit_step_completed",
            "emit_step_failed",
            "emit_checkpoint_reached",
            "emit_run_failed",
        ]:
            setattr(mock_event_emitter, method_name, AsyncMock())
        flow_runner.event_emitter = mock_event_emitter

        with patch("app.runtime.runner.create_browser_use_agent", return_value=None):
            await flow_runner.execute_flow(run, sample_flow_manifest, {})

        # Verify checkpoint event was emitted with correct data
        mock_event_emitter.emit_checkpoint_reached.assert_called_once()
        call_args = mock_event_emitter.emit_checkpoint_reached.call_args

        checkpoint_id = call_args[0][1]  # Second positional argument
        reason = call_args[0][2]
        expected_action = call_args[0][3]

        assert checkpoint_id == "Human verification"
        assert reason == "Please verify the form was filled correctly"
        assert expected_action == "confirm"

    async def test_agent_lifecycle_management(self, flow_runner, sample_flow_manifest):
        """Test that browser agent is properly started and stopped."""
        run = Run(
            id="lifecycle-run-123",
            flow_id=sample_flow_manifest["id"],
            user_id="test-user-123",
            status=RunStatus.PENDING,
        )

        # Track agent lifecycle by mocking the async methods
        start_mock = AsyncMock()
        stop_mock = AsyncMock()

        with (
            patch("app.runtime.runner.create_browser_use_agent", return_value=None),
            patch.object(NoopAgent, "start", new=start_mock),
            patch.object(NoopAgent, "stop", new=stop_mock),
        ):
            await flow_runner.execute_flow(run, sample_flow_manifest, {})

        # Verify agent lifecycle methods were called
        start_mock.assert_awaited_once()
        stop_mock.assert_awaited_once()
