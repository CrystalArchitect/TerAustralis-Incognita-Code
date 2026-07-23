"""Crystal Runtime Coordinator: Orchestrates workflow execution across components."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Dict, List
import uuid
import time

from ..registry.registry import Registry, CapabilityNotFoundError
from ..events.eventbus import EventBus
from ..logging.logger import Logger
from ..config.config import Config


class TaskStatus(Enum):
    """Status of a task."""
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    FATAL_ERROR = "fatal_error"
    TIMEOUT = "timeout"


@dataclass
class Task:
    """A unit of work to be executed by the Coordinator."""
    task_id: str
    description: str
    capabilities_required: List[str]
    directives: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Context for task execution (from CrystalBridge)."""
    request_id: str
    caller_identity: str
    approved_scope: List[str]
    approval_level: str  # "read" | "write" | "admin"
    provenance: str


@dataclass
class ErrorDetails:
    """Details about an error during execution."""
    error_code: str
    message: str
    component: Optional[str] = None
    retryable: bool = False


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    task_id: str
    status: str
    outputs: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[ErrorDetails] = None
    components_executed: List[str] = field(default_factory=list)
    components_failed: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    audit_trail_ref: str = ""


class TaskExecutionError(Exception):
    """Base class for task execution errors."""

    def __init__(self, error_code: str, message: str, component: Optional[str] = None, retryable: bool = False):
        self.error_code = error_code
        self.message = message
        self.component = component
        self.retryable = retryable
        super().__init__(message)


class ScopeViolationError(TaskExecutionError):
    """Task exceeds caller's authorized scope."""

    def __init__(self, task_id: str, required: List[str], approved: List[str]):
        super().__init__(
            error_code="scope_violation",
            message=f"Task {task_id} requires capabilities {required} but caller only has {approved}",
            retryable=False
        )


class CapabilityNotAvailableError(TaskExecutionError):
    """Required capability is not registered."""

    def __init__(self, capability: str):
        super().__init__(
            error_code="capability_not_found",
            message=f"Capability '{capability}' is not registered",
            retryable=True
        )


class ComponentTimeoutError(TaskExecutionError):
    """Component exceeded timeout."""

    def __init__(self, component: str, timeout_seconds: float):
        super().__init__(
            error_code="component_timeout",
            message=f"Component '{component}' exceeded timeout of {timeout_seconds}s",
            component=component,
            retryable=False
        )


class ComponentFailureError(TaskExecutionError):
    """Component returned non-retriable error."""

    def __init__(self, component: str, reason: str):
        super().__init__(
            error_code="component_failure",
            message=f"Component '{component}' failed: {reason}",
            component=component,
            retryable=False
        )


class Coordinator:
    """Orchestrates workflow execution across runtime components."""

    def __init__(self, registry: Registry, events: EventBus, logging: Logger, config: Config) -> None:
        """
        Initialize the Coordinator.

        Args:
            registry: Registry instance for capability queries
            events: EventBus instance for component communication
            logging: Logger instance for audit/operational logging
            config: Config instance with coordinator settings

        Raises:
            ValueError: If required configuration is missing
        """
        self.registry = registry
        self.events = events
        self.logging = logging
        self.config = config

        # Load coordinator configuration
        try:
            self.default_timeout = config.get("coordinator.default_timeout_seconds", 30)
            self.retry_count = config.get("coordinator.retry_count", 3)
            self.retry_backoff_ms = config.get("coordinator.retry_backoff_ms", [100, 500, 2000])
            self.max_concurrent_tasks = config.get("coordinator.max_concurrent_tasks", 100)
            self.log_level = config.get("coordinator.log_level", "info")
        except Exception as e:
            raise ValueError(f"Failed to load coordinator configuration: {e}")

        self.logging.operational("info", "Coordinator initialized", {
            "default_timeout": self.default_timeout,
            "retry_count": self.retry_count
        })

    def execute_workflow(self, task: Task, context: ExecutionContext) -> WorkflowResult:
        """
        Execute a workflow for the given task.

        Args:
            task: Task object with description, required capabilities, directives
            context: ExecutionContext with request ID, caller identity, scope

        Returns:
            WorkflowResult: status, outputs, error details, audit trail reference

        Raises:
            TaskExecutionError: If workflow fails
            TimeoutError: If workflow exceeds configured timeout
        """
        start_time = time.time()
        result = WorkflowResult(
            task_id=task.task_id,
            status=TaskStatus.FATAL_ERROR.value,
            start_time=start_time
        )

        try:
            # Step 0: Validate inputs
            self._validate_task_inputs(task, context)

            # Step 1: Validate task against execution context scope
            self.logging.operational("debug", f"Validating task {task.task_id}", {
                "task_id": task.task_id,
                "request_id": context.request_id
            })

            self._validate_scope(task, context)

            # Step 2: Query Registry for required capabilities
            self.logging.operational("debug", f"Querying registry for capabilities", {
                "task_id": task.task_id,
                "capabilities_required": task.capabilities_required
            })

            # Check that all required capabilities have at least one service
            missing_capabilities = []
            for capability in task.capabilities_required:
                services = self.registry.query_capability(capability)
                if not services:
                    missing_capabilities.append(capability)

            if missing_capabilities:
                raise CapabilityNotAvailableError(missing_capabilities[0])

            service_references = self._get_services_for_capabilities(task.capabilities_required)

            # Step 3: Publish task started event
            self.events.publish(
                event_type="task.started",
                event_data={
                    "task_id": task.task_id,
                    "description": task.description,
                    "capabilities_required": task.capabilities_required
                },
                source="coordinator"
            )

            # Step 4: Execute components (simplified: route to first available service)
            result.status = TaskStatus.SUCCESS.value
            for capability in task.capabilities_required:
                service_ref = next((sr for sr in service_references if capability in sr.capabilities), None)
                if service_ref:
                    result.components_executed.append(service_ref.service_id)

                    # Publish component request event
                    self.events.publish(
                        event_type="component.invoked",
                        event_data={
                            "task_id": task.task_id,
                            "component": service_ref.service_id,
                            "capability": capability
                        },
                        source="coordinator"
                    )

            # Step 5: Publish task completed event
            self.events.publish(
                event_type="task.completed",
                event_data={
                    "task_id": task.task_id,
                    "status": result.status,
                    "components_executed": result.components_executed
                },
                source="coordinator"
            )

            # Step 6: Log to RDP via Logging
            audit_ref = self.logging.audit(
                event_type="task_executed",
                actor=context.caller_identity,
                action="execute_workflow",
                resource=task.task_id,
                result="success",
                context={
                    "request_id": context.request_id,
                    "components_executed": result.components_executed,
                    "capabilities_required": task.capabilities_required
                }
            )
            result.audit_trail_ref = audit_ref.audit_id if audit_ref else ""

        except ScopeViolationError as e:
            self.logging.operational("warn", f"Scope violation for task {task.task_id}", {
                "task_id": task.task_id,
                "error": str(e)
            })
            result.status = TaskStatus.FATAL_ERROR.value
            result.error_details = ErrorDetails(
                error_code=e.error_code,
                message=e.message,
                retryable=e.retryable
            )
            self._log_error(task, context, e)

        except CapabilityNotAvailableError as e:
            self.logging.operational("warn", f"Capability not found for task {task.task_id}", {
                "task_id": task.task_id,
                "error": str(e)
            })
            result.status = TaskStatus.FATAL_ERROR.value
            result.error_details = ErrorDetails(
                error_code=e.error_code,
                message=e.message,
                retryable=e.retryable
            )
            self._log_error(task, context, e)

        except Exception as e:
            self.logging.operational("error", f"Unexpected error in workflow execution", {
                "task_id": task.task_id,
                "error": str(e)
            })
            result.status = TaskStatus.FATAL_ERROR.value
            result.error_details = ErrorDetails(
                error_code="internal_error",
                message=f"Unexpected error: {str(e)}",
                retryable=False
            )
            self._log_error(task, context, e)

        finally:
            end_time = time.time()
            result.end_time = end_time
            result.duration_ms = (end_time - start_time) * 1000

            # Check if execution exceeded timeout
            if result.duration_ms > (self.default_timeout * 1000):
                result.status = TaskStatus.TIMEOUT.value
                result.error_details = ErrorDetails(
                    error_code="task_timeout",
                    message=f"Task exceeded timeout of {self.default_timeout}s",
                    retryable=False
                )

        return result

    def _validate_task_inputs(self, task: Task, context: ExecutionContext) -> None:
        """Validate task and context inputs."""
        # Validate task fields
        if not task.task_id or not isinstance(task.task_id, str):
            raise TaskExecutionError("invalid_input", "task_id must be a non-empty string")
        if len(task.task_id) > 255:
            raise TaskExecutionError("invalid_input", "task_id must be <= 255 characters")
        if not task.description or not isinstance(task.description, str):
            raise TaskExecutionError("invalid_input", "description must be a non-empty string")
        if len(task.description) > 1024:
            raise TaskExecutionError("invalid_input", "description must be <= 1024 characters")
        if not isinstance(task.capabilities_required, list):
            raise TaskExecutionError("invalid_input", "capabilities_required must be a list")
        if len(task.capabilities_required) > 100:
            raise TaskExecutionError("invalid_input", "capabilities_required limited to 100 items")
        if not all(isinstance(c, str) for c in task.capabilities_required):
            raise TaskExecutionError("invalid_input", "All capabilities must be strings")

        # Validate directives (must be dict with reasonable size)
        if not isinstance(task.directives, dict):
            raise TaskExecutionError("invalid_input", "directives must be a dict")
        import json
        directives_size = len(json.dumps(task.directives))
        if directives_size > 10_000:
            raise TaskExecutionError("invalid_input", "directives payload too large (>10KB)")

        # Validate metadata (must be dict with reasonable size)
        if not isinstance(task.metadata, dict):
            raise TaskExecutionError("invalid_input", "metadata must be a dict")
        metadata_size = len(json.dumps(task.metadata))
        if metadata_size > 10_000:
            raise TaskExecutionError("invalid_input", "metadata payload too large (>10KB)")

        # Validate context fields
        if not context.request_id or not isinstance(context.request_id, str):
            raise TaskExecutionError("invalid_input", "request_id must be a non-empty string")
        if len(context.request_id) > 255:
            raise TaskExecutionError("invalid_input", "request_id must be <= 255 characters")
        if not context.caller_identity or not isinstance(context.caller_identity, str):
            raise TaskExecutionError("invalid_input", "caller_identity must be a non-empty string")
        if len(context.caller_identity) > 255:
            raise TaskExecutionError("invalid_input", "caller_identity must be <= 255 characters")
        if not isinstance(context.approved_scope, list):
            raise TaskExecutionError("invalid_input", "approved_scope must be a list")
        if len(context.approved_scope) > 100:
            raise TaskExecutionError("invalid_input", "approved_scope limited to 100 items")
        if not all(isinstance(c, str) for c in context.approved_scope):
            raise TaskExecutionError("invalid_input", "All approved_scope items must be strings")
        if context.approval_level not in ["read", "write", "admin"]:
            raise TaskExecutionError("invalid_input", "approval_level must be 'read', 'write', or 'admin'")

    def _validate_scope(self, task: Task, context: ExecutionContext) -> None:
        """Validate that task is within caller's approved scope."""
        for capability in task.capabilities_required:
            if capability not in context.approved_scope:
                raise ScopeViolationError(
                    task.task_id,
                    task.capabilities_required,
                    context.approved_scope
                )

    def _get_services_for_capabilities(self, capabilities: List[str]):
        """Query Registry for services providing required capabilities."""
        service_references = []
        for capability in capabilities:
            try:
                services = self.registry.query_capability(capability)
                service_references.extend(services)
            except Exception as e:
                self.logging.operational("debug", f"Error querying capability {capability}", {
                    "capability": capability,
                    "error": str(e)
                })
        return service_references

    def _log_error(self, task: Task, context: ExecutionContext, error: Exception) -> None:
        """Log an error to the audit trail."""
        error_code = getattr(error, "error_code", "unknown_error")
        self.logging.audit(
            event_type="task_executed",
            actor=context.caller_identity,
            action="execute_workflow",
            resource=task.task_id,
            result=f"failure:{error_code}",
            context={
                "request_id": context.request_id,
                "error": str(error)
            }
        )
