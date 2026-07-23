"""Crystal Runtime Logging: Audit and operational logging."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging
import json
import uuid
import threading

from ..config.config import Config


@dataclass
class AuditRecord:
    """An audit trail record."""
    audit_id: str
    event_type: str
    actor: str
    action: str
    resource: str
    result: str  # "success" | "failure:*" | "partial"
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)


class Logger:
    """Centralized logging for audit and operational events."""

    def __init__(self, config: Config) -> None:
        """
        Initialize the Logger.

        Args:
            config: Config instance with logging settings

        Raises:
            ValueError: If required configuration is missing
        """
        self.config = config

        # Load logging configuration
        try:
            self.log_level = config.get("logging.log_level", "info").upper()
            self.audit_enabled = config.get("logging.audit_enabled", True)
            self.audit_file = config.get("logging.audit_file", None)
            self.operational_enabled = config.get("logging.operational_enabled", True)
            self.operational_file = config.get("logging.operational_file", None)
        except Exception as e:
            raise ValueError(f"Failed to load logging configuration: {e}")

        # Set up Python logging
        self.python_logger = logging.getLogger("crystalcore.runtime")
        self.python_logger.setLevel(getattr(logging, self.log_level, logging.INFO))

        # Add console handler if not present
        if not self.python_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.python_logger.addHandler(handler)

        # Audit trail storage with thread safety
        self._audit_records: List[AuditRecord] = []
        self._audit_buffer: List[AuditRecord] = []
        self._max_audit_records = config.get("logging.max_audit_records", 10000)
        self._audit_lock = threading.Lock()
        self._file_lock = threading.Lock()

        self.operational("info", "Logger initialized", {
            "log_level": self.log_level,
            "audit_enabled": self.audit_enabled,
        })

    def operational(self, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an operational event.

        Args:
            level: Log level ("debug", "info", "warn", "error")
            message: Log message
            context: Optional context dictionary
        """
        if not self.operational_enabled:
            return

        log_level = getattr(logging, level.upper(), logging.INFO)
        context_str = f" | {json.dumps(context)}" if context else ""

        self.python_logger.log(log_level, f"{message}{context_str}")

        # Also write to operational file if configured (thread-safe)
        if self.operational_file:
            with self._file_lock:
                try:
                    with open(self.operational_file, "a") as f:
                        record = {
                            "timestamp": datetime.now().isoformat(),
                            "level": level,
                            "message": message,
                            "context": context,
                        }
                        f.write(json.dumps(record) + "\n")
                except Exception as e:
                    self.python_logger.error(f"Failed to write operational log: {e}")

    def diagnostic(self, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a diagnostic event (similar to operational but for deeper debugging).

        Args:
            level: Log level
            message: Log message
            context: Optional context dictionary
        """
        self.operational(level, f"[DIAGNOSTIC] {message}", context)

    def audit(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        result: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditRecord]:
        """
        Log an audit trail event.

        Args:
            event_type: Type of event (e.g., "service_registered", "task_executed")
            actor: Who performed the action (e.g., "user_001", "system")
            action: What action was performed
            resource: What resource was affected
            result: Result ("success" | "failure:*" | "partial")
            context: Optional context (without secrets)

        Returns:
            AuditRecord if audit is enabled, None otherwise
        """
        if not self.audit_enabled:
            return None

        import time
        record = AuditRecord(
            audit_id=str(uuid.uuid4()),
            event_type=event_type,
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            timestamp=time.time(),
            context=context or {},
        )

        with self._audit_lock:
            self._audit_records.append(record)
            self._audit_buffer.append(record)

            # Trim if exceeding max
            if len(self._audit_records) > self._max_audit_records:
                self._audit_records = self._audit_records[-self._max_audit_records:]

        # Log operational version
        self.operational("info", f"AUDIT: {event_type} | {action} on {resource} by {actor} -> {result}", {
            "audit_id": record.audit_id,
            "event_type": event_type,
        })

        # Write to audit file if configured (thread-safe)
        if self.audit_file:
            with self._file_lock:
                try:
                    with open(self.audit_file, "a") as f:
                        audit_dict = {
                            "audit_id": record.audit_id,
                            "event_type": record.event_type,
                            "actor": record.actor,
                            "action": record.action,
                            "resource": record.resource,
                            "result": record.result,
                            "timestamp": record.timestamp,
                            "context": record.context,
                        }
                        f.write(json.dumps(audit_dict) + "\n")
                except Exception as e:
                    self.python_logger.error(f"Failed to write audit log: {e}")

        return record

    def get_audit_records(self, limit: Optional[int] = None) -> List[AuditRecord]:
        """
        Get audit records (thread-safe).

        Args:
            limit: Maximum number of records to return

        Returns:
            List of AuditRecord objects
        """
        with self._audit_lock:
            if limit:
                return self._audit_records[-limit:]
            return list(self._audit_records)

    def get_audit_records_by_resource(self, resource: str) -> List[AuditRecord]:
        """Get audit records for a specific resource (thread-safe)."""
        with self._audit_lock:
            return [r for r in self._audit_records if r.resource == resource]

    def get_audit_records_by_actor(self, actor: str) -> List[AuditRecord]:
        """Get audit records by a specific actor (thread-safe)."""
        with self._audit_lock:
            return [r for r in self._audit_records if r.actor == actor]

    def get_audit_records_by_type(self, event_type: str) -> List[AuditRecord]:
        """Get audit records of a specific type (thread-safe)."""
        with self._audit_lock:
            return [r for r in self._audit_records if r.event_type == event_type]

    def flush_audit_buffer(self) -> None:
        """Flush the audit buffer (prepare for remote transmission, thread-safe)."""
        with self._audit_lock:
            self._audit_buffer.clear()

    def get_audit_buffer(self) -> List[AuditRecord]:
        """Get the current audit buffer (thread-safe)."""
        with self._audit_lock:
            return list(self._audit_buffer)

    def clear_audit_records(self) -> None:
        """Clear all audit records (testing only, thread-safe)."""
        with self._audit_lock:
            self._audit_records.clear()
            self._audit_buffer.clear()
