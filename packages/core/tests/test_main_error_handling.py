"""
Test for error handling in main.py execute endpoint.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from monkey_coder.app.main import app
from monkey_coder.models import ExecuteRequest, TaskType, ExecutionContext, PersonaConfig, PersonaType
from monkey_coder.monitoring import MetricsCollector


class TestMainErrorHandling:
    """Test error handling in main.py execute endpoint."""

    @pytest.fixture
    def mock_metrics_collector(self):
        """Create a mock MetricsCollector."""
        collector = MagicMock(spec=MetricsCollector)
        collector.start_execution = MagicMock(return_value="test_execution_id")
        collector.record_error = MagicMock()
        return collector

    @pytest.fixture
    def mock_app_state(self, mock_metrics_collector):
        """Create mock app state with required components."""
        state = MagicMock()
        state.metrics_collector = mock_metrics_collector
        state.orchestrator = AsyncMock()
        state.persona_router = AsyncMock()
        state.quantum_executor = AsyncMock()
        state.billing_tracker = AsyncMock()
        state.quantum_router = AsyncMock()
        return state

    @pytest.mark.asyncio
    async def test_execute_task_error_handling(self, mock_app_state):
        """Test that execute_task properly calls record_error with all required parameters."""

        # Override app state for testing
        with patch.object(app, 'state', mock_app_state):

            # Create a proper mock quantum routing result
            from monkey_coder.quantum.router_integration import QuantumRoutingResult
            from monkey_coder.models import ProviderType

            mock_quantum_result = MagicMock(spec=QuantumRoutingResult)
            mock_quantum_result.provider = ProviderType.OPENAI
            mock_quantum_result.model = "gpt-4.1"
            mock_quantum_result.confidence = 0.95
            mock_quantum_result.strategy = "test_strategy"
            mock_quantum_result.execution_time = 0.1
            mock_quantum_result.fallback_used = False

            # Mock quantum router to return proper result
            mock_app_state.quantum_router.route_request.return_value = mock_quantum_result

            # Mock the dependencies to raise an exception
            mock_app_state.persona_router.route_request.side_effect = Exception("Test error")

            # Create test request
            request = ExecuteRequest(
                task_id="test_task",
                task_type=TaskType.CODE_GENERATION,
                prompt="test prompt",
                files=None,
                context=ExecutionContext(user_id="test_user", session_id="test_session", workspace_id="test_workspace"),
                persona_config=PersonaConfig(persona=PersonaType.DEVELOPER, custom_instructions=None)
            )

            # Mock the API key dependency
            with patch('monkey_coder.app.main.get_api_key', return_value="test_key"):
                with patch('monkey_coder.app.main.verify_permissions', new_callable=AsyncMock):

                    # Execute the request and expect it to raise an exception
                    with pytest.raises(HTTPException):
                        from monkey_coder.app.main import execute_task
                        await execute_task(request, AsyncMock(), "test_key")

                    # Verify that record_error was called with the correct parameters
                    mock_app_state.metrics_collector.record_error.assert_called_once()
                    call_args = mock_app_state.metrics_collector.record_error.call_args

                    # Check that the correct parameters were passed (as keyword arguments)
                    assert call_args.kwargs['execution_id'] == "test_execution_id"
                    assert call_args.kwargs['error'] == "Test error"

    @pytest.mark.asyncio
    async def test_record_error_signature_compatibility(self, mock_metrics_collector):
        """Test that record_error is called with parameters compatible with the expected signature."""

        # Test the actual MetricsCollector record_error method signature
        from monkey_coder.monitoring import MetricsCollector

        # Create a real MetricsCollector instance to test the method signature
        collector = MetricsCollector()

        # This should not raise a TypeError if the signature is correct
        try:
            collector.record_error(
                execution_id="test_id",
                error="test error"
            )
            # If we get here, the signature is correct
            assert True
        except TypeError as e:
            pytest.fail(f"record_error method signature is incompatible: {e}")
