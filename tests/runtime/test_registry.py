"""Unit tests for Crystal Runtime Registry module."""

import pytest
import time
from unittest.mock import Mock, MagicMock

from src.runtime.registry.registry import (
    Registry,
    Capability,
    ServiceMetadata,
    ServiceReference,
    ComponentStatus,
    DuplicateServiceError,
    ServiceNotFoundError,
)


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
    logger.audit = Mock()
    return logger


@pytest.fixture
def mock_config():
    """Create a mock Config."""
    config = Mock()
    config.get = Mock(side_effect=lambda key, default: {
        "registry.heartbeat_timeout_seconds": 30,
        "registry.status_check_interval_seconds": 5,
        "registry.max_services": 1000,
        "registry.log_level": "info",
    }.get(key, default))
    return config


@pytest.fixture
def registry(mock_config, mock_eventbus, mock_logger):
    """Create a Registry instance with mocked dependencies."""
    return Registry(mock_config, mock_eventbus, mock_logger)


@pytest.fixture
def sample_capability():
    """Create a sample Capability."""
    return Capability(
        name="ai.lumina",
        version="1.0.0",
        description="AI companion service",
        input_schema={"type": "object"},
        output_schema={"type": "object"}
    )


@pytest.fixture
def sample_metadata():
    """Create a sample ServiceMetadata."""
    return ServiceMetadata(
        service_id="lumina_service",
        version="1.0.0",
        health_check_url="http://localhost:8000/health",
        health_check_interval_seconds=30,
        tags=["ai", "companion"]
    )


class TestRegistryInitialization:
    """Test Registry initialization."""

    def test_registry_initializes_with_config(self, mock_config, mock_eventbus, mock_logger):
        """Test that Registry loads configuration during initialization."""
        registry = Registry(mock_config, mock_eventbus, mock_logger)

        assert registry.config is mock_config
        assert registry.events is mock_eventbus
        assert registry.logging is mock_logger
        assert registry.heartbeat_timeout == 30
        assert registry.max_services == 1000

    def test_registry_initialization_logs_info(self, registry, mock_logger):
        """Test that Registry logs initialization."""
        mock_logger.operational.assert_called()
        call_args = mock_logger.operational.call_args
        assert "Registry initialized" in str(call_args)


class TestServiceRegistration:
    """Test service registration."""

    def test_register_service(self, registry, sample_capability, sample_metadata):
        """Test registering a service."""
        token = registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        assert token.service_id == "lumina_service"
        assert token.token_id is not None
        assert token.issued_at > 0

    def test_register_service_publishes_event(self, registry, sample_capability, sample_metadata, mock_eventbus):
        """Test that service registration publishes an event."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        mock_eventbus.publish.assert_called()
        call_args = mock_eventbus.publish.call_args
        assert call_args[1]["event_type"] == "registry.service_registered"
        assert call_args[1]["event_data"]["service_id"] == "lumina_service"

    def test_register_duplicate_service_rejected(self, registry, sample_capability, sample_metadata):
        """Test that duplicate service IDs are rejected."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        with pytest.raises(DuplicateServiceError):
            registry.register(
                service_id="lumina_service",
                capabilities=[sample_capability],
                metadata=sample_metadata
            )

    def test_register_service_with_invalid_service_id(self, registry, sample_capability, sample_metadata):
        """Test that invalid service IDs are rejected."""
        with pytest.raises(ValueError):
            registry.register(
                service_id="",
                capabilities=[sample_capability],
                metadata=sample_metadata
            )

    def test_register_service_with_no_capabilities(self, registry, sample_metadata):
        """Test that services must have at least one capability."""
        with pytest.raises(ValueError):
            registry.register(
                service_id="empty_service",
                capabilities=[],
                metadata=sample_metadata
            )


class TestQueryCapability:
    """Test capability querying."""

    def test_query_capability_found(self, registry, sample_capability, sample_metadata):
        """Test querying an available capability."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        results = registry.query_capability("ai.lumina")

        assert len(results) == 1
        assert results[0].service_id == "lumina_service"
        assert "ai.lumina" in results[0].capabilities

    def test_query_capability_not_found(self, registry):
        """Test querying an unavailable capability."""
        results = registry.query_capability("nonexistent.capability")

        assert len(results) == 0

    def test_query_capability_multiple_services(self, registry, sample_metadata):
        """Test querying a capability provided by multiple services."""
        cap = Capability(
            name="shared.capability",
            version="1.0.0",
            description="Shared capability"
        )

        registry.register("service_1", [cap], sample_metadata)
        registry.register("service_2", [cap], ServiceMetadata(
            service_id="service_2",
            version="1.0.0"
        ))

        results = registry.query_capability("shared.capability")

        assert len(results) == 2
        service_ids = {r.service_id for r in results}
        assert "service_1" in service_ids
        assert "service_2" in service_ids

    def test_query_capability_sorting_by_status(self, registry, sample_capability, sample_metadata):
        """Test that query results are sorted by status (online first)."""
        registry.register("service_1", [sample_capability], sample_metadata)
        registry.register("service_2", [sample_capability], ServiceMetadata(
            service_id="service_2",
            version="1.0.0"
        ))

        # Mark one as offline
        registry.mark_offline("service_2", "test offline")

        results = registry.query_capability("ai.lumina")

        # Online service should come first
        assert results[0].service_id == "service_1"
        assert results[0].status == ComponentStatus.ONLINE.value
        assert results[1].service_id == "service_2"
        assert results[1].status == ComponentStatus.OFFLINE.value


class TestServiceStatus:
    """Test service status tracking."""

    def test_get_status_online(self, registry, sample_capability, sample_metadata):
        """Test getting status of an online service."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        status = registry.get_status("lumina_service")

        assert status["status"] == ComponentStatus.ONLINE.value
        assert status["service_id"] == "lumina_service"
        assert len(status["capabilities_online"]) > 0

    def test_get_status_offline(self, registry, sample_capability, sample_metadata):
        """Test getting status of an offline service."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        registry.mark_offline("lumina_service", "test offline")

        status = registry.get_status("lumina_service")

        assert status["status"] == ComponentStatus.OFFLINE.value
        assert status["reason"] == "test offline"

    def test_get_status_not_found(self, registry):
        """Test getting status of non-existent service."""
        with pytest.raises(ServiceNotFoundError):
            registry.get_status("nonexistent_service")

    def test_mark_degraded(self, registry, sample_capability, sample_metadata):
        """Test marking a service as degraded."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        result = registry.mark_degraded("lumina_service", "high latency")

        assert result is True
        status = registry.get_status("lumina_service")
        assert status["status"] == ComponentStatus.DEGRADED.value
        assert status["reason"] == "high latency"

    def test_mark_degraded_publishes_event(self, registry, sample_capability, sample_metadata, mock_eventbus):
        """Test that marking degraded publishes an event."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        # Clear previous event calls
        mock_eventbus.publish.reset_mock()

        registry.mark_degraded("lumina_service", "high latency")

        mock_eventbus.publish.assert_called()
        call_args = mock_eventbus.publish.call_args
        assert call_args[1]["event_type"] == "registry.service_degraded"


class TestHeartbeat:
    """Test heartbeat handling."""

    def test_heartbeat_recorded(self, registry, sample_capability, sample_metadata):
        """Test that heartbeats are recorded."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        old_heartbeat = registry._last_heartbeat["lumina_service"]
        time.sleep(0.01)  # Slight delay

        result = registry.heartbeat("lumina_service")

        assert result is True
        new_heartbeat = registry._last_heartbeat["lumina_service"]
        assert new_heartbeat > old_heartbeat

    def test_heartbeat_transitions_offline_to_online(self, registry, sample_capability, sample_metadata):
        """Test that heartbeat transitions offline service to online."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        registry.mark_offline("lumina_service", "test offline")
        assert registry.get_status("lumina_service")["status"] == ComponentStatus.OFFLINE.value

        registry.heartbeat("lumina_service")

        assert registry.get_status("lumina_service")["status"] == ComponentStatus.ONLINE.value

    def test_heartbeat_for_nonexistent_service(self, registry):
        """Test heartbeat for non-existent service."""
        result = registry.heartbeat("nonexistent_service")

        assert result is False


class TestServiceUnregistration:
    """Test service unregistration."""

    def test_unregister_service(self, registry, sample_capability, sample_metadata):
        """Test unregistering a service."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        result = registry.unregister("lumina_service")

        assert result is True
        # Service should no longer be queryable
        assert len(registry.query_capability("ai.lumina")) == 0

    def test_unregister_nonexistent_service(self, registry):
        """Test unregistering a non-existent service."""
        result = registry.unregister("nonexistent_service")

        assert result is False

    def test_unregister_publishes_event(self, registry, sample_capability, sample_metadata, mock_eventbus):
        """Test that unregistration publishes an event."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        mock_eventbus.publish.reset_mock()

        registry.unregister("lumina_service")

        mock_eventbus.publish.assert_called()
        call_args = mock_eventbus.publish.call_args
        assert call_args[1]["event_type"] == "registry.service_unregistered"


class TestTimeoutChecking:
    """Test timeout checking."""

    def test_check_timeouts_marks_offline(self, registry, sample_capability, sample_metadata, mock_config):
        """Test that check_timeouts marks services as offline."""
        # Create a registry with very short timeout
        mock_config.get.side_effect = lambda key, default: {
            "registry.heartbeat_timeout_seconds": 0.01,  # Very short timeout
            "registry.status_check_interval_seconds": 5,
            "registry.max_services": 1000,
            "registry.log_level": "info",
        }.get(key, default)

        registry = Registry(mock_config, registry.events, registry.logging)

        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        # Wait for timeout to occur
        time.sleep(0.02)

        timed_out = registry.check_timeouts()

        assert "lumina_service" in timed_out
        assert registry.get_status("lumina_service")["status"] == ComponentStatus.OFFLINE.value


class TestListServices:
    """Test listing services."""

    def test_list_services(self, registry, sample_capability, sample_metadata):
        """Test listing all registered services."""
        registry.register(
            service_id="service_1",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        cap2 = Capability(
            name="storage.rdp",
            version="1.0.0",
            description="Storage service"
        )
        registry.register(
            service_id="service_2",
            capabilities=[cap2],
            metadata=ServiceMetadata(service_id="service_2", version="1.0.0")
        )

        services = registry.list_services()

        assert len(services) == 2
        service_ids = {s["service_id"] for s in services}
        assert "service_1" in service_ids
        assert "service_2" in service_ids


class TestGetCapabilityInfo:
    """Test getting capability details."""

    def test_get_capability_info(self, registry, sample_capability, sample_metadata):
        """Test retrieving detailed capability information."""
        registry.register(
            service_id="lumina_service",
            capabilities=[sample_capability],
            metadata=sample_metadata
        )

        cap_info = registry.get_capability_info("ai.lumina")

        assert cap_info is not None
        assert cap_info.name == "ai.lumina"
        assert cap_info.version == "1.0.0"
        assert cap_info.description == "AI companion service"

    def test_get_capability_info_not_found(self, registry):
        """Test getting info for non-existent capability."""
        cap_info = registry.get_capability_info("nonexistent.capability")

        assert cap_info is None
