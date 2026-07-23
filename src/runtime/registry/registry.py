"""Crystal Runtime Registry: Manages component registration, discovery, and status tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Dict, List
import threading
import time
import uuid

from ..config.config import Config
from ..events.eventbus import EventBus
from ..logging.logger import Logger


class ComponentStatus(Enum):
    """Status of a registered component."""
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"


@dataclass
class Capability:
    """A capability provided by a service."""
    name: str
    version: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceMetadata:
    """Metadata about a registered service."""
    service_id: str
    version: str
    health_check_url: Optional[str] = None
    health_check_interval_seconds: int = 30
    tags: List[str] = field(default_factory=list)


@dataclass
class ServiceReference:
    """Reference to a registered service."""
    service_id: str
    capabilities: List[str]
    status: str
    last_heartbeat: float
    registered_at: float


@dataclass
class RegistrationToken:
    """Token returned when a service is registered."""
    token_id: str
    service_id: str
    issued_at: float


class CapabilityNotFoundError(Exception):
    """Capability is not available in the registry."""

    def __init__(self, capability: str):
        super().__init__(f"Capability '{capability}' not found in registry")


class DuplicateServiceError(Exception):
    """Service with this ID is already registered."""

    def __init__(self, service_id: str):
        super().__init__(f"Service '{service_id}' is already registered")


class ServiceNotFoundError(Exception):
    """Service is not registered."""

    def __init__(self, service_id: str):
        super().__init__(f"Service '{service_id}' not found in registry")


class Registry:
    """Manages component registration, discovery, and status tracking."""

    def __init__(self, config: Config, events: EventBus, logging: Logger) -> None:
        """
        Initialize the Registry.

        Args:
            config: Config instance with registry settings
            events: EventBus for broadcasting status changes
            logging: Logger for audit logging

        Raises:
            ValueError: If required configuration is missing
        """
        self.config = config
        self.events = events
        self.logging = logging

        # Load registry configuration
        try:
            self.heartbeat_timeout = config.get("registry.heartbeat_timeout_seconds", 30)
            self.status_check_interval = config.get("registry.status_check_interval_seconds", 5)
            self.max_services = config.get("registry.max_services", 1000)
            self.log_level = config.get("registry.log_level", "info")
        except Exception as e:
            raise ValueError(f"Failed to load registry configuration: {e}")

        # Registry storage
        self._services: Dict[str, Dict[str, Any]] = {}
        self._capabilities: Dict[str, List[str]] = {}  # capability_name -> [service_ids]
        self._lock = threading.RLock()

        # Status tracking
        self._last_heartbeat: Dict[str, float] = {}
        self._registered_at: Dict[str, float] = {}
        self._status: Dict[str, str] = {}
        self._degraded_reason: Dict[str, str] = {}

        self.logging.operational("info", "Registry initialized", {
            "heartbeat_timeout": self.heartbeat_timeout,
            "max_services": self.max_services
        })

    def register(
        self,
        service_id: str,
        capabilities: List[Capability],
        metadata: ServiceMetadata
    ) -> RegistrationToken:
        """
        Register a new service and its capabilities.

        Args:
            service_id: Unique identifier for the service
            capabilities: List of Capability objects this service provides
            metadata: ServiceMetadata with version, health_check_url, etc.

        Returns:
            RegistrationToken: Token for later unregistration

        Raises:
            ValueError: If service_id is invalid or already registered
            DuplicateServiceError: If service_id already exists
        """
        with self._lock:
            # Validate inputs
            if not service_id or not isinstance(service_id, str):
                raise ValueError(f"Invalid service_id: {service_id}")

            if service_id in self._services:
                raise DuplicateServiceError(service_id)

            if len(self._services) >= self.max_services:
                raise ValueError(f"Registry at capacity: {self.max_services} services")

            if not capabilities:
                raise ValueError("Service must provide at least one capability")

            # Register service
            now = time.time()
            capability_names = [cap.name for cap in capabilities]

            self._services[service_id] = {
                "metadata": metadata,
                "capabilities": capability_names,
                "capability_objects": capabilities,
            }

            # Index capabilities
            for capability in capabilities:
                if capability.name not in self._capabilities:
                    self._capabilities[capability.name] = []
                self._capabilities[capability.name].append(service_id)

            # Initialize status tracking
            self._status[service_id] = ComponentStatus.ONLINE.value
            self._last_heartbeat[service_id] = now
            self._registered_at[service_id] = now

            # Publish event
            self.events.publish(
                event_type="registry.service_registered",
                event_data={
                    "service_id": service_id,
                    "capabilities": capability_names,
                    "version": metadata.version,
                },
                source="registry"
            )

            # Log to audit trail
            self.logging.audit(
                event_type="service_registered",
                actor="system",
                action="register_service",
                resource=service_id,
                result="success",
                context={
                    "capabilities": capability_names,
                    "version": metadata.version,
                }
            )

            token = RegistrationToken(
                token_id=str(uuid.uuid4()),
                service_id=service_id,
                issued_at=now
            )

            self.logging.operational("info", f"Service '{service_id}' registered", {
                "service_id": service_id,
                "capabilities": capability_names,
            })

            return token

    def unregister(self, service_id: str) -> bool:
        """
        Unregister a service.

        Args:
            service_id: Service to remove

        Returns:
            True if service was registered and removed, False if not found
        """
        with self._lock:
            if service_id not in self._services:
                return False

            service_info = self._services.pop(service_id)
            capabilities = service_info["capabilities"]

            # Remove from capability index
            for capability in capabilities:
                if capability in self._capabilities:
                    if service_id in self._capabilities[capability]:
                        self._capabilities[capability].remove(service_id)
                    if not self._capabilities[capability]:
                        del self._capabilities[capability]

            # Clean up status tracking
            self._status.pop(service_id, None)
            self._last_heartbeat.pop(service_id, None)
            self._registered_at.pop(service_id, None)
            self._degraded_reason.pop(service_id, None)

            # Publish event
            self.events.publish(
                event_type="registry.service_unregistered",
                event_data={
                    "service_id": service_id,
                    "capabilities": capabilities,
                },
                source="registry"
            )

            # Log to audit trail
            self.logging.audit(
                event_type="service_unregistered",
                actor="system",
                action="unregister_service",
                resource=service_id,
                result="success",
                context={
                    "capabilities": capabilities,
                }
            )

            self.logging.operational("info", f"Service '{service_id}' unregistered", {
                "service_id": service_id,
                "capabilities": capabilities,
            })

            return True

    def query_capability(self, capability_name: str) -> List[ServiceReference]:
        """
        Find all services providing a capability.

        Args:
            capability_name: Capability to search for

        Returns:
            List of ServiceReference objects (sorted by status, then registration time)
        """
        with self._lock:
            if capability_name not in self._capabilities:
                return []

            service_ids = self._capabilities[capability_name]
            references = []

            for service_id in service_ids:
                if service_id not in self._services:
                    continue

                service_info = self._services[service_id]
                ref = ServiceReference(
                    service_id=service_id,
                    capabilities=service_info["capabilities"],
                    status=self._status.get(service_id, ComponentStatus.OFFLINE.value),
                    last_heartbeat=self._last_heartbeat.get(service_id, 0),
                    registered_at=self._registered_at.get(service_id, 0),
                )
                references.append(ref)

            # Sort: online first, then degraded, then offline
            status_priority = {
                ComponentStatus.ONLINE.value: 0,
                ComponentStatus.DEGRADED.value: 1,
                ComponentStatus.OFFLINE.value: 2,
            }
            references.sort(key=lambda r: (
                status_priority.get(r.status, 3),
                r.registered_at
            ))

            return references

    def get_status(self, service_id: str) -> Dict[str, Any]:
        """
        Get current status of a service.

        Args:
            service_id: Service to check

        Returns:
            ComponentStatus dict with status, reason, last_heartbeat, capabilities_online/degraded

        Raises:
            ServiceNotFoundError: If service is not registered
        """
        with self._lock:
            if service_id not in self._services:
                raise ServiceNotFoundError(service_id)

            service_info = self._services[service_id]
            status = self._status.get(service_id, ComponentStatus.OFFLINE.value)
            reason = self._degraded_reason.get(service_id)

            return {
                "service_id": service_id,
                "status": status,
                "reason": reason,
                "last_heartbeat": self._last_heartbeat.get(service_id, 0),
                "capabilities_online": service_info["capabilities"] if status == ComponentStatus.ONLINE.value else [],
                "capabilities_degraded": service_info["capabilities"] if status == ComponentStatus.DEGRADED.value else [],
            }

    def heartbeat(self, service_id: str) -> bool:
        """
        Record a heartbeat from a service (liveness signal).

        Args:
            service_id: Service sending heartbeat

        Returns:
            True if heartbeat was recorded, False if service not found
        """
        with self._lock:
            if service_id not in self._services:
                return False

            now = time.time()
            old_status = self._status.get(service_id, ComponentStatus.OFFLINE.value)

            # Update heartbeat timestamp
            self._last_heartbeat[service_id] = now

            # If service was offline, mark as online
            if old_status == ComponentStatus.OFFLINE.value:
                self._status[service_id] = ComponentStatus.ONLINE.value
                self._degraded_reason.pop(service_id, None)

                # Publish event
                self.events.publish(
                    event_type="registry.service_recovered",
                    event_data={
                        "service_id": service_id,
                        "previous_status": old_status,
                    },
                    source="registry"
                )

                self.logging.operational("info", f"Service '{service_id}' recovered", {
                    "service_id": service_id,
                    "previous_status": old_status,
                })

            return True

    def mark_degraded(self, service_id: str, reason: str) -> bool:
        """
        Mark a service as degraded (partial failure).

        Args:
            service_id: Service to mark
            reason: Human-readable reason

        Returns:
            True if marked, False if service not found
        """
        with self._lock:
            if service_id not in self._services:
                return False

            old_status = self._status.get(service_id, ComponentStatus.OFFLINE.value)
            self._status[service_id] = ComponentStatus.DEGRADED.value
            self._degraded_reason[service_id] = reason

            # Publish event if status changed
            if old_status != ComponentStatus.DEGRADED.value:
                self.events.publish(
                    event_type="registry.service_degraded",
                    event_data={
                        "service_id": service_id,
                        "reason": reason,
                        "previous_status": old_status,
                    },
                    source="registry"
                )

                self.logging.operational("warn", f"Service '{service_id}' degraded: {reason}", {
                    "service_id": service_id,
                    "reason": reason,
                })

            return True

    def mark_offline(self, service_id: str, reason: Optional[str] = None) -> bool:
        """
        Mark a service as offline.

        Args:
            service_id: Service to mark
            reason: Optional reason for being offline

        Returns:
            True if marked, False if service not found
        """
        with self._lock:
            if service_id not in self._services:
                return False

            old_status = self._status.get(service_id, ComponentStatus.OFFLINE.value)
            self._status[service_id] = ComponentStatus.OFFLINE.value

            if reason:
                self._degraded_reason[service_id] = reason

            # Publish event if status changed
            if old_status != ComponentStatus.OFFLINE.value:
                self.events.publish(
                    event_type="registry.service_offline",
                    event_data={
                        "service_id": service_id,
                        "reason": reason,
                        "previous_status": old_status,
                    },
                    source="registry"
                )

                self.logging.operational("warn", f"Service '{service_id}' marked offline", {
                    "service_id": service_id,
                    "reason": reason,
                })

            return True

    def check_timeouts(self) -> List[str]:
        """
        Check for services that have timed out (no heartbeat).

        Returns:
            List of service IDs that were marked offline due to timeout
        """
        with self._lock:
            now = time.time()
            timed_out = []

            for service_id, last_heartbeat in self._last_heartbeat.items():
                if now - last_heartbeat > self.heartbeat_timeout:
                    status = self._status.get(service_id, ComponentStatus.OFFLINE.value)
                    if status != ComponentStatus.OFFLINE.value:
                        self.mark_offline(service_id, f"Heartbeat timeout after {self.heartbeat_timeout}s")
                        timed_out.append(service_id)

            return timed_out

    def list_services(self) -> List[Dict[str, Any]]:
        """
        List all registered services.

        Returns:
            List of service information dictionaries
        """
        with self._lock:
            services = []
            for service_id, service_info in self._services.items():
                services.append({
                    "service_id": service_id,
                    "status": self._status.get(service_id, ComponentStatus.OFFLINE.value),
                    "capabilities": service_info["capabilities"],
                    "version": service_info["metadata"].version,
                    "registered_at": self._registered_at.get(service_id, 0),
                    "last_heartbeat": self._last_heartbeat.get(service_id, 0),
                })
            return services

    def get_capability_info(self, capability_name: str) -> Optional[Capability]:
        """
        Get detailed information about a capability.

        Args:
            capability_name: Capability to look up

        Returns:
            Capability object if found, None otherwise
        """
        with self._lock:
            service_ids = self._capabilities.get(capability_name, [])
            if not service_ids:
                return None

            for service_id in service_ids:
                if service_id in self._services:
                    for cap in self._services[service_id]["capability_objects"]:
                        if cap.name == capability_name:
                            return cap
            return None
