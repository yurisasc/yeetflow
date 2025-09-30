"""Integration tests for flow execution with FlowRunner."""

import uuid
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from app.models import Run, RunStatus
from app.runtime.agents.noop import NoopAgent
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
        service.update_run = AsyncMock()
        return service

    @pytest.fixture
    def mock_steel_adapter(self):
        """Mock SteelBrowserAdapter for testing."""
        adapter = MagicMock()
        adapter.attach_to_session = AsyncMock()
        adapter.get_session_info = MagicMock(return_value={"websocket_url": None})
        adapter.close_session = AsyncMock()
        return adapter

    @pytest.fixture
    async def flow_runner(self, mock_run_service, mock_steel_adapter):
        """Create FlowRunner with mocked dependencies."""
        # Mock session
        mock_session = MagicMock()

        # Mock event emitter
        mock_event_emitter = MagicMock()
        mock_event_emitter.emit_run_started = AsyncMock()
        mock_event_emitter.emit_run_completed = AsyncMock()
        mock_event_emitter.emit_step_started = AsyncMock()
        mock_event_emitter.emit_step_completed = AsyncMock()
        mock_event_emitter.emit_step_failed = AsyncMock()
        mock_event_emitter.emit_checkpoint_reached = AsyncMock()
        mock_event_emitter.emit_run_failed = AsyncMock()

        return FlowRunner(
            run_service=mock_run_service,
            steel_adapter=mock_steel_adapter,
            session=mock_session,
            event_emitter=mock_event_emitter,
        )

    async def test_flow_executes_actions_and_stops_at_checkpoint(
        self, flow_runner, sample_flow_manifest, mock_run_service, mock_steel_adapter
    ):
        """Test that flow executes actions and pauses at checkpoint without teardown."""
        # Create a test run
        run = Run(
            id=uuid.uuid4(),
            flow_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            status=RunStatus.PENDING,
        )

        input_payload = {}

        # Execute the flow
        with patch("app.runtime.runner.create_browser_use_agent", return_value=None):
            await flow_runner.execute_flow(run, sample_flow_manifest, input_payload)

        # Verify Steel session was attached
        mock_steel_adapter.attach_to_session.assert_called_once_with(run.id)

        # Verify run status was updated to running
        mock_run_service.update_run.assert_any_call(run.id, {"status": "running"}, ANY)

        # Verify run status was updated to awaiting_input (not completed!)
        mock_run_service.update_run.assert_any_call(
            run.id, {"status": "awaiting_input"}, ANY
        )

        # Verify run was NOT marked as completed (should not be in call list)
        completed_calls = [
            call
            for call in mock_run_service.update_run.call_args_list
            if call[0][1].get("status") == "completed"
        ]
        assert len(completed_calls) == 0, (
            "Flow should not be marked as completed when paused at checkpoint"
        )

        # Verify session was NOT closed (resources preserved for resume)
        mock_steel_adapter.close_session.assert_not_called()

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
            id=uuid.uuid4(),
            flow_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            status=RunStatus.PENDING,
        )

        with patch("app.runtime.runner.create_browser_use_agent", return_value=None):
            await flow_runner.execute_flow(run, simple_flow, {})

        # Verify run was marked as completed
        mock_run_service.update_run.assert_any_call(
            run.id, {"status": "completed"}, ANY
        )

    async def test_flow_handles_action_execution_errors(
        self, flow_runner, sample_flow_manifest, mock_run_service
    ):
        """Test that flow properly handles errors during action execution."""
        # Create run
        run = Run(
            id=uuid.uuid4(),
            flow_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
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
        mock_run_service.update_run.assert_any_call(
            run.id, {"status": "failed", "error": "Test error"}, ANY
        )

    async def test_checkpoint_emits_proper_event_data(
        self, flow_runner, sample_flow_manifest
    ):
        """Test that checkpoint emits event with correct data structure."""
        run = Run(
            id=uuid.uuid4(),
            flow_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
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

    async def test_agent_lifecycle_management(self, flow_runner):
        """Test that browser agent is properly started and stopped on completion."""
        run = Run(
            id=uuid.uuid4(),
            flow_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            status=RunStatus.PENDING,
        )

        # Track agent lifecycle by mocking the async methods
        start_mock = AsyncMock()
        stop_mock = AsyncMock()

        # Use a simple flow without a checkpoint so the run completes
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

        with (
            patch("app.runtime.runner.create_browser_use_agent", return_value=None),
            patch.object(NoopAgent, "start", new=start_mock),
            patch.object(NoopAgent, "stop", new=stop_mock),
        ):
            await flow_runner.execute_flow(run, simple_flow, {})

        # Verify agent lifecycle methods were called
        start_mock.assert_awaited_once()
        stop_mock.assert_awaited_once()
