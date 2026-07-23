"""Crystal Runtime API: Accept inbound requests and route to Coordinator."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time
import json
import threading

from ..coordinator.coordinator import Coordinator, Task, ExecutionContext
from ..logging.logger import Logger
from ..config.config import Config
from ..registry.registry import Registry


@dataclass
class APIResponse:
    """Response to an API request."""
    status_code: int
    headers: Dict[str, str] = field(default_factory=lambda: {"Content-Type": "application/json"})
    body: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Runtime health status."""
    overall_status: str  # "online" | "degraded" | "offline"
    timestamp: float
    components: Dict[str, Any] = field(default_factory=dict)
    event_queue_depth: int = 0
    recent_error_rate: float = 0.0
    uptime_seconds: float = 0.0


class RuntimeAPI:
    """HTTP/REST interface to the runtime."""

    # Allowlist of configuration keys that can be overridden at runtime
    OVERRIDEABLE_CONFIG_KEYS = {
        "api.rate_limit_per_minute": int,
        "coordinator.default_timeout_seconds": (int, float),
        "coordinator.retry_count": int,
        "eventbus.handler_timeout_seconds": (int, float),
        "eventbus.max_queue_size": int,
        "logging.log_level": str,
    }

    def __init__(
        self,
        coordinator: Coordinator,
        registry: Registry,
        logging: Logger,
        config: Config
    ) -> None:
        """
        Initialize the API.

        Args:
            coordinator: Coordinator instance
            registry: Registry instance
            logging: Logger instance
            config: Config instance
        """
        self.coordinator = coordinator
        self.registry = registry
        self.logging = logging
        self.config = config

        # Load API configuration
        try:
            self.host = config.get("api.host", "0.0.0.0")
            self.port = config.get("api.port", 8000)
            self.rate_limit_per_minute = config.get("api.rate_limit_per_minute", 1000)
            self.log_level = config.get("api.log_level", "info")
        except Exception as e:
            raise ValueError(f"Failed to load API configuration: {e}")

        # Rate limiting with thread safety
        self._request_times: Dict[str, List[float]] = {}
        self._rate_limit_lock = threading.Lock()
        self._start_time = time.time()
        self._request_count = 0
        self._error_count = 0

        self.logging.operational("info", "RuntimeAPI initialized", {
            "host": self.host,
            "port": self.port,
        })

    def handle_request(
        self,
        http_method: str,
        path: str,
        body: Optional[Dict[str, Any]],
        caller_identity: str,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Handle an inbound HTTP request.

        Args:
            http_method: "GET" | "POST" | "PUT" | "DELETE"
            path: Request path
            body: Request body (parsed JSON)
            caller_identity: Caller identity
            headers: HTTP headers

        Returns:
            APIResponse with status, headers, body
        """
        headers = headers or {}
        self._request_count += 1

        try:
            # Log request
            self.logging.operational("debug", f"API request: {http_method} {path}", {
                "caller": caller_identity,
                "method": http_method,
                "path": path,
            })

            # Check rate limit
            if not self._check_rate_limit(caller_identity):
                return APIResponse(
                    status_code=429,
                    body={"error": "Rate limit exceeded"}
                )

            # Route request
            if path == "/runtime/task/execute" and http_method == "POST":
                return self._handle_task_execute(body, caller_identity)
            elif path == "/runtime/health" and http_method == "GET":
                return self._handle_health_check()
            elif path == "/runtime/registry/services" and http_method == "GET":
                return self._handle_list_services()
            elif path == "/runtime/registry/capabilities" and http_method == "GET":
                return self._handle_list_capabilities()
            elif path == "/runtime/config/override" and http_method == "POST":
                return self._handle_config_override(body, caller_identity)
            elif path == "/runtime/logs/audit" and http_method == "GET":
                return self._handle_get_audit_logs(caller_identity)
            else:
                return APIResponse(
                    status_code=404,
                    body={"error": f"Unknown endpoint: {path}"}
                )

        except Exception as e:
            self._error_count += 1
            self.logging.operational("error", f"API error handling {path}", {
                "error": str(e),
            })
            return APIResponse(
                status_code=500,
                body={"error": "Internal server error"}
            )

    def health_check(self) -> HealthStatus:
        """
        Get runtime health status.

        Returns:
            HealthStatus: Overall status and component statuses
        """
        # Get event queue depth
        event_queue_depth = 0
        if hasattr(self.coordinator.events, "get_event_count"):
            event_queue_depth = self.coordinator.events.get_event_count()

        # Calculate recent error rate
        uptime = time.time() - self._start_time
        error_rate = (self._error_count / max(self._request_count, 1)) * 100

        # Get component statuses
        services = self.registry.list_services()
        components = {
            s["service_id"]: {
                "status": s["status"],
                "capabilities": s["capabilities"],
            }
            for s in services
        }

        # Determine overall status
        if not services:
            overall_status = "degraded"
        elif any(s["status"] == "offline" for s in services):
            overall_status = "degraded"
        else:
            overall_status = "online"

        return HealthStatus(
            overall_status=overall_status,
            timestamp=time.time(),
            components=components,
            event_queue_depth=event_queue_depth,
            recent_error_rate=error_rate,
            uptime_seconds=uptime,
        )

    def _handle_task_execute(self, body: Optional[Dict[str, Any]], caller_identity: str) -> APIResponse:
        """Handle task execution request."""
        if not body:
            return APIResponse(
                status_code=400,
                body={"error": "Request body required"}
            )

        try:
            # Parse request
            task_data = body.get("task", {})
            context_data = body.get("context", {})

            # Create objects
            task = Task(
                task_id=task_data.get("task_id", ""),
                description=task_data.get("description", ""),
                capabilities_required=task_data.get("capabilities_required", []),
                directives=task_data.get("directives", {}),
                metadata=task_data.get("metadata", {}),
            )

            # Use caller identity and provided context
            context = ExecutionContext(
                request_id=context_data.get("request_id", ""),
                caller_identity=caller_identity,
                approved_scope=context_data.get("approved_scope", []),
                approval_level=context_data.get("approval_level", "read"),
                provenance="api",
            )

            # Execute workflow
            result = self.coordinator.execute_workflow(task, context)

            return APIResponse(
                status_code=200,
                body={
                    "task_id": result.task_id,
                    "status": result.status,
                    "outputs": result.outputs,
                    "error_details": {
                        "error_code": result.error_details.error_code,
                        "message": result.error_details.message,
                    } if result.error_details else None,
                    "components_executed": result.components_executed,
                    "duration_ms": result.duration_ms,
                }
            )

        except Exception as e:
            self.logging.operational("error", f"Task execution error", {
                "error": str(e),
            })
            return APIResponse(
                status_code=500,
                body={"error": str(e)}
            )

    def _handle_health_check(self) -> APIResponse:
        """Handle health check request."""
        health = self.health_check()
        return APIResponse(
            status_code=200,
            body={
                "overall_status": health.overall_status,
                "timestamp": health.timestamp,
                "components": health.components,
                "event_queue_depth": health.event_queue_depth,
                "recent_error_rate": health.recent_error_rate,
                "uptime_seconds": health.uptime_seconds,
            }
        )

    def _handle_list_services(self) -> APIResponse:
        """Handle list services request."""
        services = self.registry.list_services()
        return APIResponse(
            status_code=200,
            body={
                "services": [
                    {
                        "service_id": s["service_id"],
                        "status": s["status"],
                        "capabilities": s["capabilities"],
                        "version": s["version"],
                    }
                    for s in services
                ]
            }
        )

    def _handle_list_capabilities(self) -> APIResponse:
        """Handle list capabilities request."""
        # Get all unique capabilities from services
        capabilities = set()
        for service in self.registry.list_services():
            capabilities.update(service["capabilities"])

        return APIResponse(
            status_code=200,
            body={
                "capabilities": sorted(list(capabilities))
            }
        )

    def _handle_config_override(self, body: Optional[Dict[str, Any]], caller_identity: str) -> APIResponse:
        """Handle config override request."""
        if not body or "key" not in body or "value" not in body:
            return APIResponse(
                status_code=400,
                body={"error": "key and value required"}
            )

        try:
            key = body["key"]
            value = body["value"]

            # SECURITY: Only admins can override configuration
            if caller_identity not in ["system_admin", "admin", "internal"]:
                self.logging.audit(
                    event_type="config_override_denied",
                    actor=caller_identity,
                    action="override_config",
                    resource=key,
                    result="failure:unauthorized",
                    context={"reason": "non-admin user"},
                )
                return APIResponse(
                    status_code=403,
                    body={"error": "Only administrators can override configuration"}
                )

            # SECURITY: Only allow overriding whitelisted keys
            if key not in self.OVERRIDEABLE_CONFIG_KEYS:
                self.logging.audit(
                    event_type="config_override_denied",
                    actor=caller_identity,
                    action="override_config",
                    resource=key,
                    result="failure:not_allowed",
                    context={"reason": "key not in allowlist"},
                )
                return APIResponse(
                    status_code=400,
                    body={"error": f"Configuration key '{key}' cannot be overridden"}
                )

            # Validate value type
            allowed_types = self.OVERRIDEABLE_CONFIG_KEYS[key]
            if not isinstance(value, allowed_types):
                expected = allowed_types if isinstance(allowed_types, tuple) else (allowed_types,)
                return APIResponse(
                    status_code=400,
                    body={"error": f"Invalid type for '{key}': expected {[t.__name__ for t in expected]}"}
                )

            # Log override
            self.logging.audit(
                event_type="config_override",
                actor=caller_identity,
                action="override_config",
                resource=key,
                result="success",
                context={"value": str(value)},
            )

            # Apply override
            self.config.override(key, value)

            return APIResponse(
                status_code=200,
                body={"status": "success", "key": key}
            )

        except Exception as e:
            self.logging.operational("error", f"Config override error", {
                "error": str(e),
            })
            return APIResponse(
                status_code=400,
                body={"error": str(e)}
            )

    def _handle_get_audit_logs(self, caller_identity: str) -> APIResponse:
        """Handle get audit logs request."""
        try:
            # SECURITY: Only allow system_admin or internal callers to see audit logs
            # Other users can only see logs related to their own activities
            is_admin = caller_identity in ["system_admin", "admin", "internal"]

            # Get audit records
            records = self.logging.get_audit_records(limit=100)

            if not is_admin:
                # Filter to only show logs where caller is the actor or resource is related
                records = [
                    r for r in records
                    if r.actor == caller_identity
                ]

            return APIResponse(
                status_code=200,
                body={
                    "records": [
                        {
                            "audit_id": r.audit_id,
                            "event_type": r.event_type,
                            "actor": r.actor,
                            "action": r.action,
                            "resource": r.resource,
                            "result": r.result,
                            "timestamp": r.timestamp,
                        }
                        for r in records
                    ]
                }
            )

        except Exception as e:
            return APIResponse(
                status_code=500,
                body={"error": str(e)}
            )

    def _check_rate_limit(self, caller_identity: str) -> bool:
        """Check if caller is within rate limit (thread-safe)."""
        with self._rate_limit_lock:
            now = time.time()

            # Initialize if needed
            if caller_identity not in self._request_times:
                self._request_times[caller_identity] = []

            # Remove old entries (older than 1 minute)
            self._request_times[caller_identity] = [
                t for t in self._request_times[caller_identity]
                if now - t < 60
            ]

            # Check limit
            if len(self._request_times[caller_identity]) >= self.rate_limit_per_minute:
                return False

            # Add current request (atomic with check)
            self._request_times[caller_identity].append(now)
            return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get API metrics."""
        uptime = time.time() - self._start_time
        error_rate = (self._error_count / max(self._request_count, 1)) * 100

        return {
            "uptime_seconds": uptime,
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "error_rate": error_rate,
        }
