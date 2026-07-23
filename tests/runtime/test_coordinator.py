"""Unit tests for Crystal Runtime Coordinator module."""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

from src.runtime.coordinator.coordinator import (
    Coordinator,
    Task,
    ExecutionContext,
    WorkflowResult,
    ErrorDetails,
    TaskStatus,
    ScopeViolationError,
    CapabilityNotAvailableError,
    ComponentTimeoutError,
)


@pytest.fixture
def mock_registry():
    """Create a mock Registry."""
    registry = Mock()
    registry.query_capability = Mock(return_value=[])
    return registry


@pytest.fixture
def mock_eventbus():
    """Create a mock EventBus."""
    eventbus = Mock()
    eventbus.publish = Mock()
    return eventbus


@pytest.fixture
def mock_logger():
    """Create a mock Logger."""
    logger = Mock()
    logger.operational = Mock()
    logger.audit = Mock(return_value=Mock(audit_id="audit_123"))
    return logger


@pytest.fixture
def mock_config():
    """Create a mock Config."""
    config = Mock()
    config.get = Mock(side_effect=lambda key, default: {
        "coordinator.default_timeout_seconds": 30,
        "coordinator.retry_count": 3,
        "coordinator.retry_backoff_ms": [100, 500, 2000],
        "coordinator.max_concurrent_tasks": 100,
        "coordinator.log_level": "info",
    }.get(key, default))
    return config


@pytest.fixture
def coordinator(mock_registry, mock_eventbus, mock_logger, mock_config):
    """Create a Coordinator instance with mocked dependencies."""
    return Coordinator(mock_registry, mock_eventbus, mock_logger, mock_config)


class TestCoordinatorInitialization:
    """Test Coordinator initialization."""

    def test_coordinator_initializes_with_config(self, mock_registry, mock_eventbus, mock_logger, mock_config):
        """Test that Coordinator loads configuration during initialization."""
        coordinator = Coordinator(mock_registry, mock_eventbus, mock_logger, mock_config)

        assert coordinator.registry is mock_registry
        assert coordinator.events is mock_eventbus
        assert coordinator.logging is mock_logger
        assert coordinator.config is mock_config
        assert coordinator.default_timeout == 30
        assert coordinator.retry_count == 3
        assert coordinator.max_concurrent_tasks == 100

    def test_coordinator_initialization_logs_info(self, mock_registry, mock_eventbus, mock_logger, mock_config):
        """Test that Coordinator logs initialization."""
        coordinator = Coordinator(mock_registry, mock_eventbus, mock_logger, mock_config)

        mock_logger.operational.assert_called()
        call_args = mock_logger.operational.call_args
        assert "Coordinator initialized" in str(call_args)

    def test_coordinator_initialization_fails_with_missing_config(self, mock_registry, mock_eventbus, mock_logger):
        """Test that Coordinator raises error when configuration is unavailable."""
        bad_config = Mock()
        bad_config.get = Mock(side_effect=Exception("Config unavailable"))

        with pytest.raises(ValueError, match="Failed to load coordinator configuration"):
            Coordinator(mock_registry, mock_eventbus, mock_logger, bad_config)


class TestExecuteWorkflowSuccess:
    """Test successful workflow execution."""

    def test_execute_workflow_success(self, coordinator, mock_registry, mock_eventbus, mock_logger):
        """Test successful workflow execution with all capabilities available."""
        # Create a mock service reference
        service_ref = Mock()
        service_ref.service_id = "lumina_service"
        service_ref.capabilities = ["ai.lumina"]

        mock_registry.query_capability.return_value = [service_ref]

        task = Task(
            task_id="task_001",
            description="Execute AI task",
            capabilities_required=["ai.lumina"],
        )
        context = ExecutionContext(
            request_id="req_001",
            caller_identity="user_001",
            approved_scope=["ai.lumina"],
            approval_level="read",
            provenance="direct",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == TaskStatus.SUCCESS.value
        assert result.task_id == "task_001"
        assert "lumina_service" in result.components_executed
        assert result.error_details is None
        assert result.audit_trail_ref == "audit_123"
        assert result.duration_ms > 0

    def test_execute_workflow_publishes_events(self, coordinator, mock_registry, mock_eventbus):
        """Test that workflow execution publishes events."""
        service_ref = Mock()
        service_ref.service_id = "test_service"
        service_ref.capabilities = ["test.capability"]

        mock_registry.query_capability.return_value = [service_ref]

        task = Task(
            task_id="task_002",
            description="Test task",
            capabilities_required=["test.capability"],
        )
        context = ExecutionContext(
            request_id="req_002",
            caller_identity="user_002",
            approved_scope=["test.capability"],
            approval_level="write",
            provenance="api",
        )

        coordinator.execute_workflow(task, context)

        # Verify events were published
        published_events = [call[1]["event_type"] for call in mock_eventbus.publish.call_args_list]
        assert "task.started" in published_events
        assert "task.completed" in published_events
        assert "component.invoked" in published_events

    def test_execute_workflow_logs_to_audit_trail(self, coordinator, mock_logger):
        """Test that workflow execution logs to audit trail."""
        service_ref = Mock()
        service_ref.service_id = "audit_service"
        service_ref.capabilities = ["audit.test"]

        from unittest.mock import Mock as MockType
        coordinator.registry.query_capability = MockType(return_value=[service_ref])

        task = Task(
            task_id="task_003",
            description="Audit test",
            capabilities_required=["audit.test"],
        )
        context = ExecutionContext(
            request_id="req_003",
            caller_identity="user_003",
            approved_scope=["audit.test"],
            approval_level="admin",
            provenance="internal",
        )

        coordinator.execute_workflow(task, context)

        # Verify audit logging
        mock_logger.audit.assert_called()
        audit_call = mock_logger.audit.call_args
        assert audit_call[1]["result"] == "success"
        assert audit_call[1]["resource"] == "task_003"


class TestExecuteWorkflowScopeValidation:
    """Test scope validation during workflow execution."""

    def test_execute_workflow_scope_violation(self, coordinator):
        """Test that workflow execution rejects out-of-scope tasks."""
        task = Task(
            task_id="task_004",
            description="Out of scope task",
            capabilities_required=["mesh.p2p"],
        )
        context = ExecutionContext(
            request_id="req_004",
            caller_identity="user_004",
            approved_scope=["ai.lumina"],
            approval_level="read",
            provenance="direct",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == TaskStatus.FATAL_ERROR.value
        assert result.error_details is not None
        assert result.error_details.error_code == "scope_violation"
        assert not result.error_details.retryable

    def test_scope_validation_rejects_out_of_bounds(self, coordinator):
        """Test explicit scope validation against out-of-bounds capabilities."""
        task = Task(
            task_id="task_005",
            description="Out of bounds",
            capabilities_required=["mesh.p2p", "storage.rdp"],
        )
        context = ExecutionContext(
            request_id="req_005",
            caller_identity="user_005",
            approved_scope=["ai.lumina"],
            approval_level="write",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == TaskStatus.FATAL_ERROR.value
        assert "scope_violation" in result.error_details.error_code

    def test_scope_validation_allows_partial_overlap(self, coordinator, mock_registry):
        """Test that scope validation passes when all required capabilities are approved."""
        service_ref = Mock()
        service_ref.service_id = "service_1"
        service_ref.capabilities = ["ai.lumina"]

        mock_registry.query_capability.return_value = [service_ref]

        task = Task(
            task_id="task_006",
            description="Partial overlap",
            capabilities_required=["ai.lumina"],
        )
        context = ExecutionContext(
            request_id="req_006",
            caller_identity="user_006",
            approved_scope=["ai.lumina", "mesh.p2p"],
            approval_level="admin",
            provenance="internal",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == TaskStatus.SUCCESS.value


class TestExecuteWorkflowCapabilityHandling:
    """Test capability handling during workflow execution."""

    def test_execute_workflow_capability_not_found(self, coordinator, mock_registry):
        """Test that missing capabilities are handled correctly."""
        mock_registry.query_capability.return_value = []

        task = Task(
            task_id="task_007",
            description="Missing capability",
            capabilities_required=["nonexistent.capability"],
        )
        context = ExecutionContext(
            request_id="req_007",
            caller_identity="user_007",
            approved_scope=["nonexistent.capability"],
            approval_level="read",
            provenance="direct",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == TaskStatus.FATAL_ERROR.value
        assert result.error_details is not None
        assert result.error_details.error_code == "capability_not_found"
        assert result.error_details.retryable is True

    def test_execute_workflow_multiple_capabilities(self, coordinator, mock_registry):
        """Test workflow with multiple required capabilities."""
        service_ref_1 = Mock()
        service_ref_1.service_id = "service_1"
        service_ref_1.capabilities = ["ai.lumina"]

        service_ref_2 = Mock()
        service_ref_2.service_id = "service_2"
        service_ref_2.capabilities = ["storage.rdp"]

        mock_registry.query_capability.side_effect = lambda cap: {
            "ai.lumina": [service_ref_1],
            "storage.rdp": [service_ref_2],
        }.get(cap, [])

        task = Task(
            task_id="task_008",
            description="Multi-capability task",
            capabilities_required=["ai.lumina", "storage.rdp"],
        )
        context = ExecutionContext(
            request_id="req_008",
            caller_identity="user_008",
            approved_scope=["ai.lumina", "storage.rdp"],
            approval_level="write",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == TaskStatus.SUCCESS.value
        assert len(result.components_executed) >= 1


class TestExecuteWorkflowErrorHandling:
    """Test error handling during workflow execution."""

    def test_execute_workflow_with_no_services_found(self, coordinator, mock_registry):
        """Test handling when no services match required capabilities."""
        mock_registry.query_capability.return_value = []

        task = Task(
            task_id="task_009",
            description="No services test",
            capabilities_required=["missing.capability"],
        )
        context = ExecutionContext(
            request_id="req_009",
            caller_identity="user_009",
            approved_scope=["missing.capability"],
            approval_level="read",
            provenance="direct",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == TaskStatus.FATAL_ERROR.value
        assert result.error_details is not None
        assert result.error_details.error_code == "capability_not_found"

    def test_execute_workflow_error_logged_to_audit(self, coordinator, mock_registry, mock_logger):
        """Test that errors are logged to audit trail."""
        mock_registry.query_capability.side_effect = Exception("Test error")

        task = Task(
            task_id="task_010",
            description="Error audit logging",
            capabilities_required=["test.capability"],
        )
        context = ExecutionContext(
            request_id="req_010",
            caller_identity="user_010",
            approved_scope=["test.capability"],
            approval_level="write",
            provenance="api",
        )

        coordinator.execute_workflow(task, context)

        # Verify error was logged
        audit_calls = [call for call in mock_logger.audit.call_args_list]
        assert len(audit_calls) > 0
        last_call = audit_calls[-1]
        assert "failure" in last_call[1]["result"]


class TestWorkflowResultTiming:
    """Test timing and duration calculations."""

    def test_workflow_result_duration_calculated(self, coordinator):
        """Test that workflow duration is correctly calculated."""
        task = Task(
            task_id="task_011",
            description="Timing test",
            capabilities_required=[],
        )
        context = ExecutionContext(
            request_id="req_011",
            caller_identity="user_011",
            approved_scope=[],
            approval_level="admin",
            provenance="internal",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.duration_ms >= 0
        assert result.start_time > 0
        assert result.end_time >= result.start_time

    def test_workflow_result_end_time_set(self, coordinator):
        """Test that workflow result has end_time set."""
        task = Task(
            task_id="task_012",
            description="End time test",
            capabilities_required=[],
        )
        context = ExecutionContext(
            request_id="req_012",
            caller_identity="user_012",
            approved_scope=[],
            approval_level="admin",
            provenance="internal",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.end_time > result.start_time
        assert (result.end_time - result.start_time) == pytest.approx(result.duration_ms / 1000, abs=0.1)


class TestConcurrentTaskExecution:
    """Test concurrent task execution."""

    def test_execute_workflow_concurrent_tasks(self, coordinator, mock_registry):
        """Test that concurrent tasks execute independently."""
        service_ref = Mock()
        service_ref.service_id = "concurrent_service"
        service_ref.capabilities = ["concurrent.test"]

        mock_registry.query_capability.return_value = [service_ref]

        results = []
        for i in range(5):
            task = Task(
                task_id=f"concurrent_task_{i}",
                description=f"Concurrent task {i}",
                capabilities_required=["concurrent.test"],
            )
            context = ExecutionContext(
                request_id=f"req_concurrent_{i}",
                caller_identity=f"user_{i}",
                approved_scope=["concurrent.test"],
                approval_level="read",
                provenance="direct",
            )
            result = coordinator.execute_workflow(task, context)
            results.append(result)

        # All tasks should complete successfully
        assert all(r.status == TaskStatus.SUCCESS.value for r in results)
        # Each should have its own task_id
        assert len({r.task_id for r in results}) == 5


class TestCoordinatorLogging:
    """Test logging behavior during workflow execution."""

    def test_coordinator_logs_validation_step(self, coordinator, mock_logger):
        """Test that validation step is logged."""
        task = Task(
            task_id="task_013",
            description="Logging test",
            capabilities_required=[],
        )
        context = ExecutionContext(
            request_id="req_013",
            caller_identity="user_013",
            approved_scope=[],
            approval_level="admin",
            provenance="internal",
        )

        coordinator.execute_workflow(task, context)

        # Check that operational logging occurred
        operational_calls = [call for call in mock_logger.operational.call_args_list if "Validating" in str(call)]
        assert len(operational_calls) > 0

    def test_coordinator_logs_registry_query(self, coordinator, mock_logger):
        """Test that registry query is logged."""
        task = Task(
            task_id="task_014",
            description="Registry logging test",
            capabilities_required=["test.capability"],
        )
        context = ExecutionContext(
            request_id="req_014",
            caller_identity="user_014",
            approved_scope=["test.capability"],
            approval_level="read",
            provenance="direct",
        )

        coordinator.execute_workflow(task, context)

        # Check for registry query logging
        operational_calls = [call for call in mock_logger.operational.call_args_list if "registry" in str(call).lower()]
        assert len(operational_calls) > 0
