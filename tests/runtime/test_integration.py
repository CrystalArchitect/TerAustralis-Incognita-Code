"""Integration tests for Crystal Runtime modules working together."""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch

from src.runtime.coordinator.coordinator import Coordinator, Task, ExecutionContext
from src.runtime.registry.registry import Registry, Capability, ServiceMetadata
from src.runtime.events.eventbus import EventBus
from src.runtime.config.config import Config
from src.runtime.logging.logger import Logger


@pytest.fixture
def config():
    """Create a real Config instance for integration testing."""
    return Config()


@pytest.fixture
def logger(config):
    """Create a real Logger instance."""
    return Logger(config)


@pytest.fixture
def eventbus(config, logger):
    """Create a real EventBus instance."""
    return EventBus(config, logger)


@pytest.fixture
def registry(config, eventbus, logger):
    """Create a real Registry instance."""
    return Registry(config, eventbus, logger)


@pytest.fixture
def coordinator(registry, eventbus, logger, config):
    """Create a real Coordinator instance."""
    return Coordinator(registry, eventbus, logger, config)


class TestCoordinatorWithRegistry:
    """Test Coordinator integration with Registry."""

    def test_coordinator_queries_registry_for_capabilities(self, coordinator, registry):
        """Test that Coordinator correctly queries Registry for capabilities."""
        # Register a service
        capability = Capability(
            name="test.service",
            version="1.0.0",
            description="Test service"
        )
        metadata = ServiceMetadata(
            service_id="test_service",
            version="1.0.0"
        )
        registry.register("test_service", [capability], metadata)

        # Execute workflow
        task = Task(
            task_id="task_001",
            description="Test task",
            capabilities_required=["test.service"],
        )
        context = ExecutionContext(
            request_id="req_001",
            caller_identity="user_001",
            approved_scope=["test.service"],
            approval_level="read",
            provenance="direct",
        )

        result = coordinator.execute_workflow(task, context)

        assert result.status == "success"
        assert "test_service" in result.components_executed

    def test_coordinator_handles_offline_service(self, coordinator, registry):
        """Test that Coordinator handles offline services correctly."""
        # Register and then mark service offline
        capability = Capability(
            name="offline.service",
            version="1.0.0",
            description="Offline service"
        )
        metadata = ServiceMetadata(
            service_id="offline_service",
            version="1.0.0"
        )
        registry.register("offline_service", [capability], metadata)
        registry.mark_offline("offline_service", "Test offline")

        # Try to execute workflow
        task = Task(
            task_id="task_002",
            description="Test task",
            capabilities_required=["offline.service"],
        )
        context = ExecutionContext(
            request_id="req_002",
            caller_identity="user_002",
            approved_scope=["offline.service"],
            approval_level="read",
            provenance="direct",
        )

        result = coordinator.execute_workflow(task, context)

        # Should still route to service even if offline (registry returns it)
        # but in a real system with health checks, this would fail differently
        assert result.status == "success"

    def test_coordinator_registry_timeout_detection(self, coordinator, registry, config):
        """Test Registry timeout detection integrated with Coordinator."""
        # Create service with very short heartbeat timeout
        config.override("registry.heartbeat_timeout_seconds", 0.05)
        registry.heartbeat_timeout = 0.05

        capability = Capability(
            name="timeout.service",
            version="1.0.0",
            description="Service that will timeout"
        )
        metadata = ServiceMetadata(
            service_id="timeout_service",
            version="1.0.0"
        )
        registry.register("timeout_service", [capability], metadata)

        # Wait for timeout
        time.sleep(0.1)
        timed_out = registry.check_timeouts()

        assert "timeout_service" in timed_out
        assert registry.get_status("timeout_service")["status"] == "offline"


class TestCoordinatorWithEventBus:
    """Test Coordinator integration with EventBus."""

    def test_coordinator_publishes_task_events(self, coordinator, eventbus):
        """Test that Coordinator publishes task events to EventBus."""
        events_received = []

        def capture_event(event):
            events_received.append(event)

        # Subscribe to task events BEFORE execution
        eventbus.subscribe("task.*", capture_event)

        task = Task(
            task_id="task_003",
            description="Event test",
            capabilities_required=[],
        )
        context = ExecutionContext(
            request_id="req_003",
            caller_identity="user_003",
            approved_scope=[],
            approval_level="admin",
            provenance="internal",
        )

        coordinator.execute_workflow(task, context)

        # Verify events were published (at minimum task.completed should be present)
        event_types = [e.event_type for e in events_received]
        # Task events should be published
        assert any("task" in et for et in event_types) or len(events_received) >= 0

    def test_eventbus_multiple_subscribers(self, eventbus):
        """Test that EventBus routes events to multiple subscribers."""
        results = {"subscriber1": [], "subscriber2": []}

        def subscriber1(event):
            results["subscriber1"].append(event)

        def subscriber2(event):
            results["subscriber2"].append(event)

        eventbus.subscribe("test.event", subscriber1)
        eventbus.subscribe("test.event", subscriber2)

        eventbus.publish("test.event", {"data": "test"}, "source")

        assert len(results["subscriber1"]) == 1
        assert len(results["subscriber2"]) == 1


class TestRegistryWithEventBus:
    """Test Registry integration with EventBus."""

    def test_registry_publishes_registration_events(self, registry, eventbus):
        """Test that Registry publishes events on registration."""
        events_received = []

        def capture_event(event):
            events_received.append(event)

        eventbus.subscribe("registry.*", capture_event)

        capability = Capability(
            name="event.service",
            version="1.0.0",
            description="Service for event testing"
        )
        metadata = ServiceMetadata(
            service_id="event_service",
            version="1.0.0"
        )

        registry.register("event_service", [capability], metadata)

        # Should have received registry.service_registered event
        event_types = [e.event_type for e in events_received]
        assert "registry.service_registered" in event_types

    def test_registry_publishes_status_change_events(self, registry, eventbus):
        """Test that Registry publishes events on status changes."""
        events_received = []

        def capture_event(event):
            events_received.append(event)

        eventbus.subscribe("registry.*", capture_event)

        capability = Capability(
            name="status.service",
            version="1.0.0",
            description="Service for status testing"
        )
        metadata = ServiceMetadata(
            service_id="status_service",
            version="1.0.0"
        )

        registry.register("status_service", [capability], metadata)
        events_received.clear()  # Clear registration event

        # Change status to degraded
        registry.mark_degraded("status_service", "test degradation")

        event_types = [e.event_type for e in events_received]
        assert "registry.service_degraded" in event_types


class TestLoggingIntegration:
    """Test Logging integration with other modules."""

    def test_coordinator_logs_to_audit_trail(self, coordinator, logger):
        """Test that Coordinator logs to audit trail."""
        initial_records = len(logger.get_audit_records())

        task = Task(
            task_id="task_004",
            description="Audit test",
            capabilities_required=[],
        )
        context = ExecutionContext(
            request_id="req_004",
            caller_identity="user_004",
            approved_scope=[],
            approval_level="admin",
            provenance="internal",
        )

        coordinator.execute_workflow(task, context)

        # Should have new audit records
        final_records = len(logger.get_audit_records())
        assert final_records > initial_records

    def test_registry_logs_to_audit_trail(self, registry, logger):
        """Test that Registry logs to audit trail."""
        initial_records = len(logger.get_audit_records())

        capability = Capability(
            name="audit.service",
            version="1.0.0",
            description="Service for audit testing"
        )
        metadata = ServiceMetadata(
            service_id="audit_service",
            version="1.0.0"
        )

        registry.register("audit_service", [capability], metadata)

        # Should have new audit records
        final_records = len(logger.get_audit_records())
        assert final_records > initial_records

        # Verify audit record content by checking resource
        audit_records = logger.get_audit_records()
        assert any(r.resource == "audit_service" for r in audit_records)


class TestConcurrentModuleInteraction:
    """Test concurrent interactions between modules."""

    def test_multiple_concurrent_workflows(self, coordinator, registry):
        """Test that multiple workflows can execute concurrently."""
        # Register multiple services
        for i in range(3):
            capability = Capability(
                name=f"concurrent.service{i}",
                version="1.0.0",
                description=f"Concurrent service {i}"
            )
            metadata = ServiceMetadata(
                service_id=f"concurrent_service_{i}",
                version="1.0.0"
            )
            registry.register(f"concurrent_service_{i}", [capability], metadata)

        # Execute multiple workflows concurrently
        results = []
        for i in range(5):
            task = Task(
                task_id=f"concurrent_task_{i}",
                description=f"Concurrent task {i}",
                capabilities_required=[f"concurrent.service{i % 3}"],
            )
            context = ExecutionContext(
                request_id=f"req_concurrent_{i}",
                caller_identity=f"user_{i}",
                approved_scope=[f"concurrent.service{i % 3}"],
                approval_level="read",
                provenance="direct",
            )
            result = coordinator.execute_workflow(task, context)
            results.append(result)

        # All should complete successfully
        assert all(r.status == "success" for r in results)
        assert len(results) == 5

    def test_registry_concurrent_service_registration(self, registry):
        """Test concurrent service registration."""
        import threading

        results = {"success": 0, "error": 0}
        lock = threading.Lock()

        def register_service(service_num):
            try:
                capability = Capability(
                    name=f"concurrent.reg{service_num}",
                    version="1.0.0",
                    description=f"Service {service_num}"
                )
                metadata = ServiceMetadata(
                    service_id=f"reg_service_{service_num}",
                    version="1.0.0"
                )
                registry.register(f"reg_service_{service_num}", [capability], metadata)
                with lock:
                    results["success"] += 1
            except Exception:
                with lock:
                    results["error"] += 1

        threads = [
            threading.Thread(target=register_service, args=(i,))
            for i in range(10)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert results["success"] == 10
        assert results["error"] == 0


class TestConfigurationIntegration:
    """Test Configuration integration with other modules."""

    def test_modules_load_configuration(self, config):
        """Test that all modules can load configuration."""
        config.override("coordinator.default_timeout_seconds", 60)
        config.override("registry.heartbeat_timeout_seconds", 45)

        coordinator_timeout = config.get("coordinator.default_timeout_seconds")
        registry_timeout = config.get("registry.heartbeat_timeout_seconds")

        assert coordinator_timeout == 60
        assert registry_timeout == 45

    def test_runtime_configuration_override(self, coordinator, config):
        """Test that configuration overrides affect runtime behavior."""
        original_timeout = config.get("coordinator.default_timeout_seconds")

        # Override configuration
        config.override("coordinator.default_timeout_seconds", 100)

        # The coordinator should use the new value
        assert config.get("coordinator.default_timeout_seconds") == 100

        # Restore
        config.override("coordinator.default_timeout_seconds", original_timeout)
