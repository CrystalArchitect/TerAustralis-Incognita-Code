"""Contract tests for Crystal Runtime with external component mocks."""

import pytest
import json
from unittest.mock import Mock, MagicMock

from src.runtime.coordinator.coordinator import Coordinator, Task, ExecutionContext
from src.runtime.registry.registry import Registry, Capability, ServiceMetadata
from src.runtime.events.eventbus import EventBus
from src.runtime.config.config import Config
from src.runtime.logging.logger import Logger
from src.runtime.api.api import RuntimeAPI


@pytest.fixture
def full_runtime():
    """Create a complete runtime with all components."""
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


class TestLuminaComponentContract:
    """Test contract with mock Lumina component."""

    def test_lumina_request_format(self, full_runtime):
        """Test that Lumina receives requests in correct format."""
        coordinator = full_runtime["coordinator"]
        registry = full_runtime["registry"]

        # Register mock Lumina service
        capability = Capability(
            name="ai.lumina",
            version="1.0.0",
            description="Lumina AI companion"
        )
        metadata = ServiceMetadata(
            service_id="lumina",
            version="1.0.0",
            health_check_url="http://localhost:5000/health",
            tags=["ai", "companion"]
        )
        registry.register("lumina", [capability], metadata)

        # Execute task
        task = Task(
            task_id="lumina_task_001",
            description="Ask Lumina a question",
            capabilities_required=["ai.lumina"],
            directives={"prompt": "What is consciousness?"},
        )
        context = ExecutionContext(
            request_id="lumina_001",
            caller_identity="user_001",
            approved_scope=["ai.lumina"],
            approval_level="read",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        # Verify result format
        assert result.task_id == "lumina_task_001"
        assert result.status == "success"
        assert isinstance(result.components_executed, list)
        assert "lumina" in result.components_executed

    def test_lumina_error_response(self, full_runtime):
        """Test Coordinator handles Lumina errors gracefully."""
        coordinator = full_runtime["coordinator"]
        registry = full_runtime["registry"]
        logger = full_runtime["logger"]

        # Register Lumina
        capability = Capability(
            name="ai.lumina",
            version="1.0.0",
            description="Lumina AI companion"
        )
        metadata = ServiceMetadata(
            service_id="lumina",
            version="1.0.0"
        )
        registry.register("lumina", [capability], metadata)

        # Mark as degraded (simulating error state)
        registry.mark_degraded("lumina", "High latency detected")

        # Execute task
        task = Task(
            task_id="lumina_error_001",
            description="Task with degraded service",
            capabilities_required=["ai.lumina"],
        )
        context = ExecutionContext(
            request_id="error_001",
            caller_identity="user_001",
            approved_scope=["ai.lumina"],
            approval_level="read",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        # Should still succeed (coordinator doesn't fail on degraded)
        assert result.status == "success"

        # Verify error was logged
        audit_records = logger.get_audit_records()
        assert len(audit_records) > 0


class TestStarlineComponentContract:
    """Test contract with mock Starline component."""

    def test_starline_consent_denial(self, full_runtime):
        """Test Coordinator handles Starline consent denial."""
        coordinator = full_runtime["coordinator"]
        registry = full_runtime["registry"]

        # Register Starline service
        capability = Capability(
            name="consent.starline",
            version="1.0.0",
            description="Starline consent management"
        )
        metadata = ServiceMetadata(
            service_id="starline",
            version="1.0.0",
            health_check_url="http://localhost:6000/health",
            tags=["consent", "p2p"]
        )
        registry.register("starline", [capability], metadata)

        # Mark as offline to simulate consent denial
        registry.mark_offline("starline", "Consent denied for this request")

        # Execute task
        task = Task(
            task_id="starline_consent_001",
            description="Request denied due to consent",
            capabilities_required=["consent.starline"],
        )
        context = ExecutionContext(
            request_id="consent_001",
            caller_identity="user_001",
            approved_scope=["consent.starline"],
            approval_level="write",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        # Task should still complete (coordinator doesn't fail)
        assert result.task_id == "starline_consent_001"

    def test_starline_message_format(self, full_runtime):
        """Test Starline receives messages in correct format."""
        registry = full_runtime["registry"]

        capability = Capability(
            name="mesh.p2p.starline",
            version="2.0.0",
            description="Starline P2P mesh",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "recipient": {"type": "string"},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "delivery_time": {"type": "number"},
                },
            }
        )
        metadata = ServiceMetadata(
            service_id="starline",
            version="2.0.0"
        )
        registry.register("starline", [capability], metadata)

        # Verify capability schema
        cap_info = registry.get_capability_info("mesh.p2p.starline")
        assert cap_info is not None
        assert cap_info.input_schema is not None
        assert "message" in cap_info.input_schema["properties"]


class TestWeaverandMatrixContract:
    """Test contract with mock Weaver and Matrix components."""

    def test_weaver_matrix_response(self, full_runtime):
        """Test Coordinator correctly interprets Weaver matrix responses."""
        coordinator = full_runtime["coordinator"]
        registry = full_runtime["registry"]

        # Register Weaver service
        capability = Capability(
            name="analysis.weaver",
            version="1.0.0",
            description="Weaver cross-comparison analysis"
        )
        metadata = ServiceMetadata(
            service_id="weaver",
            version="1.0.0",
            health_check_url="http://localhost:7000/health",
            tags=["analysis", "consensus"]
        )
        registry.register("weaver", [capability], metadata)

        # Execute task
        task = Task(
            task_id="weaver_task_001",
            description="Ask Weaver for consensus",
            capabilities_required=["analysis.weaver"],
            directives={
                "question": "Is this data valid?",
                "threshold": 0.7,
            },
        )
        context = ExecutionContext(
            request_id="weaver_001",
            caller_identity="user_001",
            approved_scope=["analysis.weaver"],
            approval_level="read",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)

        # Should route to Weaver successfully
        assert "weaver" in result.components_executed
        # Should NOT interpret as direct verdict (it's consensus data)
        assert result.error_details is None


class TestRDPAuditContract:
    """Test contract with RDP (audit trail)."""

    def test_rdp_witness_write(self, full_runtime):
        """Test audit records are written with proper format."""
        logger = full_runtime["logger"]
        coordinator = full_runtime["coordinator"]

        initial_count = len(logger.get_audit_records())

        task = Task(
            task_id="rdp_audit_001",
            description="Task for RDP audit",
            capabilities_required=[],
        )
        context = ExecutionContext(
            request_id="rdp_001",
            caller_identity="system_admin",
            approved_scope=[],
            approval_level="admin",
            provenance="internal",
        )

        coordinator.execute_workflow(task, context)

        # Verify audit records were created
        final_count = len(logger.get_audit_records())
        assert final_count > initial_count

        # Verify audit record contains required fields
        records = logger.get_audit_records()
        assert all(hasattr(r, "audit_id") for r in records[-1:])
        assert all(hasattr(r, "timestamp") for r in records[-1:])
        assert all(hasattr(r, "actor") for r in records[-1:])


class TestAPIRequestFormat:
    """Test API request/response contracts."""

    def test_api_task_execute_request_format(self, full_runtime):
        """Test API accepts correct task execution request format."""
        api = full_runtime["api"]

        request_body = {
            "task": {
                "task_id": "api_task_001",
                "description": "API test task",
                "capabilities_required": [],
                "directives": {},
                "metadata": {},
            },
            "context": {
                "request_id": "api_001",
                "approved_scope": [],
                "approval_level": "read",
            },
        }

        response = api.handle_request(
            http_method="POST",
            path="/runtime/task/execute",
            body=request_body,
            caller_identity="api_user",
        )

        assert response.status_code == 200
        assert "task_id" in response.body
        assert response.body["task_id"] == "api_task_001"

    def test_api_health_check_format(self, full_runtime):
        """Test API health check returns correct format."""
        api = full_runtime["api"]

        response = api.handle_request(
            http_method="GET",
            path="/runtime/health",
            body=None,
            caller_identity="health_check",
        )

        assert response.status_code == 200
        assert "overall_status" in response.body
        assert "timestamp" in response.body
        assert "components" in response.body

    def test_api_malformed_request(self, full_runtime):
        """Test API handles malformed requests gracefully."""
        api = full_runtime["api"]

        response = api.handle_request(
            http_method="POST",
            path="/runtime/task/execute",
            body=None,
            caller_identity="api_user",
        )

        assert response.status_code == 400
        assert "error" in response.body

    def test_api_unknown_endpoint(self, full_runtime):
        """Test API handles unknown endpoints."""
        api = full_runtime["api"]

        response = api.handle_request(
            http_method="GET",
            path="/runtime/unknown/endpoint",
            body=None,
            caller_identity="api_user",
        )

        assert response.status_code == 404
        assert "error" in response.body


class TestComponentIsolation:
    """Test that component failures don't cascade."""

    def test_failed_component_isolation(self, full_runtime):
        """Test that one component failure doesn't affect others."""
        coordinator = full_runtime["coordinator"]
        registry = full_runtime["registry"]

        # Register two services
        cap1 = Capability(
            name="service1.capability",
            version="1.0.0",
            description="Service 1"
        )
        cap2 = Capability(
            name="service2.capability",
            version="1.0.0",
            description="Service 2"
        )

        registry.register("service1", [cap1], ServiceMetadata(
            service_id="service1",
            version="1.0.0"
        ))
        registry.register("service2", [cap2], ServiceMetadata(
            service_id="service2",
            version="1.0.0"
        ))

        # Mark service1 as offline
        registry.mark_offline("service1", "Test failure")

        # Service2 should still be accessible
        status = registry.get_status("service2")
        assert status["status"] == "online"

        # Execute task with service2
        task = Task(
            task_id="isolation_test",
            description="Test isolation",
            capabilities_required=["service2.capability"],
        )
        context = ExecutionContext(
            request_id="isolation_001",
            caller_identity="user_001",
            approved_scope=["service2.capability"],
            approval_level="read",
            provenance="api",
        )

        result = coordinator.execute_workflow(task, context)
        assert result.status == "success"
