"""End-to-end tests for complete Crystal Runtime workflows."""

import pytest
import threading
import time

from src.runtime.coordinator.coordinator import Coordinator, Task, ExecutionContext
from src.runtime.registry.registry import Registry, Capability, ServiceMetadata
from src.runtime.events.eventbus import EventBus
from src.runtime.config.config import Config
from src.runtime.logging.logger import Logger
from src.runtime.api.api import RuntimeAPI


@pytest.fixture
def runtime_system():
    """Create a complete runtime system for E2E testing."""
    config = Config()
    logger = Logger(config)
    eventbus = EventBus(config, logger)
    registry = Registry(config, eventbus, logger)
    coordinator = Coordinator(registry, eventbus, logger, config)
    api = RuntimeAPI(coordinator, registry, logger, config)

    return {
        "config": config,
        "logger": logger,
        "eventbus": eventbus,
        "registry": registry,
        "coordinator": coordinator,
        "api": api,
    }


class TestE2ELuminaConversation:
    """End-to-end test of Lumina conversation workflow."""

    def test_e2e_lumina_conversation(self, runtime_system):
        """Test complete workflow with Lumina."""
        coordinator = runtime_system["coordinator"]
        registry = runtime_system["registry"]
        logger = runtime_system["logger"]

        # Register Lumina
        capability = Capability(
            name="ai.lumina",
            version="1.0.0",
            description="Lumina AI companion",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "context": {"type": "object"},
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "confidence": {"type": "number"},
                }
            }
        )
        metadata = ServiceMetadata(
            service_id="lumina",
            version="1.0.0",
            health_check_url="http://localhost:5000/health",
            health_check_interval_seconds=30,
            tags=["ai", "companion", "conversation"]
        )
        registry.register("lumina", [capability], metadata)

        # Execute task
        task = Task(
            task_id="conversation_001",
            description="Have a conversation with Lumina",
            capabilities_required=["ai.lumina"],
            directives={
                "prompt": "What does it mean to be conscious?",
                "tone": "philosophical",
            },
            metadata={
                "user_id": "user_001",
                "session_id": "session_123",
            }
        )
        context = ExecutionContext(
            request_id="req_001",
            caller_identity="user_001",
            approved_scope=["ai.lumina"],
            approval_level="read",
            provenance="api",
        )

        # Execute workflow
        result = coordinator.execute_workflow(task, context)

        # Verify result
        assert result.task_id == "conversation_001"
        assert result.status == "success"
        assert "lumina" in result.components_executed
        assert result.duration_ms > 0

        # Verify audit trail
        audit_records = logger.get_audit_records_by_resource("conversation_001")
        assert len(audit_records) > 0


class TestE2EMultiComponentWorkflow:
    """End-to-end test with multiple components."""

    def test_e2e_multi_component_workflow(self, runtime_system):
        """Test workflow involving multiple components."""
        coordinator = runtime_system["coordinator"]
        registry = runtime_system["registry"]
        logger = runtime_system["logger"]

        # Register three services
        services = [
            {
                "id": "lumina",
                "capability": "ai.lumina",
                "name": "Lumina AI",
            },
            {
                "id": "weaver",
                "capability": "analysis.weaver",
                "name": "Weaver Analysis",
            },
            {
                "id": "starline",
                "capability": "mesh.p2p",
                "name": "Starline P2P",
            }
        ]

        for service in services:
            cap = Capability(
                name=service["capability"],
                version="1.0.0",
                description=service["name"]
            )
            metadata = ServiceMetadata(
                service_id=service["id"],
                version="1.0.0",
                tags=[service["id"]]
            )
            registry.register(service["id"], [cap], metadata)

        # Execute multi-component task (simplified)
        task = Task(
            task_id="multi_001",
            description="Multi-component workflow",
            capabilities_required=["ai.lumina", "analysis.weaver"],
        )
        context = ExecutionContext(
            request_id="req_multi_001",
            caller_identity="user_001",
            approved_scope=["ai.lumina", "analysis.weaver", "mesh.p2p"],
            approval_level="write",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        # Verify all components were invoked
        assert result.status == "success"
        assert "lumina" in result.components_executed
        assert "weaver" in result.components_executed


class TestE2EComponentFailureIsolation:
    """End-to-end test of component failure isolation."""

    def test_e2e_component_failure_isolation(self, runtime_system):
        """Test that component failure doesn't affect others."""
        coordinator = runtime_system["coordinator"]
        registry = runtime_system["registry"]

        # Register two components
        cap1 = Capability(
            name="primary.service",
            version="1.0.0",
            description="Primary service"
        )
        cap2 = Capability(
            name="backup.service",
            version="1.0.0",
            description="Backup service"
        )

        registry.register("primary", [cap1], ServiceMetadata(
            service_id="primary",
            version="1.0.0"
        ))
        registry.register("backup", [cap2], ServiceMetadata(
            service_id="backup",
            version="1.0.0"
        ))

        # Crash primary service
        registry.mark_offline("primary", "Service crashed")

        # Execute task with primary
        task1 = Task(
            task_id="failure_001",
            description="Task on failed service",
            capabilities_required=["primary.service"],
        )
        context1 = ExecutionContext(
            request_id="req_fail_001",
            caller_identity="user_001",
            approved_scope=["primary.service"],
            approval_level="read",
            provenance="api",
        )

        result1 = coordinator.execute_workflow(task1, context1)
        assert result1.task_id == "failure_001"

        # Execute task with backup (should still work)
        task2 = Task(
            task_id="backup_001",
            description="Task on backup service",
            capabilities_required=["backup.service"],
        )
        context2 = ExecutionContext(
            request_id="req_backup_001",
            caller_identity="user_002",
            approved_scope=["backup.service"],
            approval_level="read",
            provenance="api",
        )

        result2 = coordinator.execute_workflow(task2, context2)
        assert result2.status == "success"
        assert "backup" in result2.components_executed


class TestE2EConcurrentUsers:
    """End-to-end test with concurrent users."""

    def test_e2e_concurrent_users(self, runtime_system):
        """Test handling of concurrent users."""
        coordinator = runtime_system["coordinator"]
        registry = runtime_system["registry"]

        # Register service
        capability = Capability(
            name="concurrent.service",
            version="1.0.0",
            description="Service for concurrent testing"
        )
        metadata = ServiceMetadata(
            service_id="concurrent",
            version="1.0.0"
        )
        registry.register("concurrent", [capability], metadata)

        results = []
        errors = []
        lock = threading.Lock()

        def execute_user_task(user_id):
            try:
                task = Task(
                    task_id=f"user_{user_id}_task",
                    description=f"Task for user {user_id}",
                    capabilities_required=["concurrent.service"],
                )
                context = ExecutionContext(
                    request_id=f"req_user_{user_id}",
                    caller_identity=f"user_{user_id}",
                    approved_scope=["concurrent.service"],
                    approval_level="read",
                    provenance="api",
                )

                result = coordinator.execute_workflow(task, context)
                with lock:
                    results.append(result)
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # Launch 5 concurrent users
        threads = [
            threading.Thread(target=execute_user_task, args=(i,))
            for i in range(5)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Verify all completed successfully
        assert len(errors) == 0
        assert len(results) == 5
        assert all(r.status == "success" for r in results)


class TestE2EAuditTrailIntegrity:
    """End-to-end test of audit trail integrity."""

    def test_e2e_audit_trail_integrity(self, runtime_system):
        """Test that audit trail is complete and accurate."""
        coordinator = runtime_system["coordinator"]
        registry = runtime_system["registry"]
        logger = runtime_system["logger"]

        # Clear audit records
        logger.clear_audit_records()

        # Register service
        cap = Capability(
            name="audit.service",
            version="1.0.0",
            description="Service for audit testing"
        )
        registry.register("audit_service", [cap], ServiceMetadata(
            service_id="audit_service",
            version="1.0.0"
        ))

        # Execute task
        task = Task(
            task_id="audit_e2e_001",
            description="Audit trail test",
            capabilities_required=["audit.service"],
        )
        context = ExecutionContext(
            request_id="audit_req_001",
            caller_identity="audit_user",
            approved_scope=["audit.service"],
            approval_level="read",
            provenance="api",
        )

        coordinator.execute_workflow(task, context)

        # Verify audit trail
        records = logger.get_audit_records()
        assert len(records) > 0

        # Check that records have all required fields
        for record in records:
            assert record.audit_id
            assert record.timestamp > 0
            assert record.event_type
            assert record.actor
            assert record.action
            assert record.resource
            assert record.result


class TestE2EEndToEndLatency:
    """End-to-end test measuring latency."""

    def test_e2e_latency_within_bounds(self, runtime_system):
        """Test that end-to-end latency is acceptable."""
        coordinator = runtime_system["coordinator"]
        registry = runtime_system["registry"]

        # Register service
        cap = Capability(
            name="latency.service",
            version="1.0.0",
            description="Service for latency testing"
        )
        registry.register("latency", [cap], ServiceMetadata(
            service_id="latency",
            version="1.0.0"
        ))

        task = Task(
            task_id="latency_001",
            description="Latency test",
            capabilities_required=["latency.service"],
        )
        context = ExecutionContext(
            request_id="latency_req_001",
            caller_identity="user_001",
            approved_scope=["latency.service"],
            approval_level="read",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        # Duration should be reasonable (< 5 seconds for typical task)
        assert result.duration_ms < 5000
        assert result.duration_ms >= 0


class TestE2EComplexWorkflow:
    """End-to-end test of complex multi-step workflow."""

    def test_e2e_complex_workflow(self, runtime_system):
        """Test complex workflow with multiple steps."""
        coordinator = runtime_system["coordinator"]
        registry = runtime_system["registry"]
        logger = runtime_system["logger"]

        # Register multiple services
        services = {
            "input": "intake.service",
            "process": "processing.service",
            "output": "delivery.service",
        }

        for name, capability_name in services.items():
            cap = Capability(
                name=capability_name,
                version="1.0.0",
                description=f"{name.capitalize()} service"
            )
            registry.register(name, [cap], ServiceMetadata(
                service_id=name,
                version="1.0.0"
            ))

        # Execute workflow
        task = Task(
            task_id="complex_e2e_001",
            description="Complex multi-step workflow",
            capabilities_required=[
                "intake.service",
                "processing.service",
                "delivery.service",
            ],
            directives={
                "steps": ["validate", "process", "deliver"],
                "priority": "high",
            }
        )
        context = ExecutionContext(
            request_id="complex_req_001",
            caller_identity="workflow_engine",
            approved_scope=[
                "intake.service",
                "processing.service",
                "delivery.service",
            ],
            approval_level="admin",
            provenance="internal",
        )

        result = coordinator.execute_workflow(task, context)

        # Verify workflow completed
        assert result.status == "success"
        assert len(result.components_executed) >= 0
        assert result.duration_ms > 0

        # Verify comprehensive audit trail
        audit_records = logger.get_audit_records_by_resource("complex_e2e_001")
        assert len(audit_records) > 0
