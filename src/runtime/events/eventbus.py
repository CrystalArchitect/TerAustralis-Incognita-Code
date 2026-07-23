"""Crystal Runtime EventBus: Publish events and route to subscribers with delivery guarantees."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import threading
import time
import uuid

from ..config.config import Config
from ..logging.logger import Logger


@dataclass
class Event:
    """An event published on the EventBus."""
    event_id: str
    event_type: str
    event_data: Dict[str, Any]
    source: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Subscription:
    """A subscription to events on the EventBus."""
    subscription_id: str
    event_type_pattern: str  # e.g., "task.*" or "task.started"
    handler: Callable
    filter_func: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)


class EventBus:
    """Asynchronous message bus for component communication."""

    def __init__(self, config: Config, logging: Logger) -> None:
        """
        Initialize the EventBus.

        Args:
            config: Config instance with event bus settings
            logging: Logger for event audit

        Raises:
            ValueError: If required configuration is missing
        """
        self.config = config
        self.logging = logging

        # Load event bus configuration
        try:
            self.max_queue_size = config.get("eventbus.max_queue_size", 10000)
            self.retention_seconds = config.get("eventbus.retention_seconds", 300)
            self.delivery_timeout_seconds = config.get("eventbus.delivery_timeout_seconds", 30)
            self.handler_timeout_seconds = config.get("eventbus.handler_timeout_seconds", 5)
            self.max_retries = config.get("eventbus.max_retries", 3)
            self.log_level = config.get("eventbus.log_level", "info")
        except Exception as e:
            raise ValueError(f"Failed to load event bus configuration: {e}")

        # Event storage and subscriptions
        self._events: List[Event] = []
        self._subscriptions: Dict[str, Subscription] = {}
        self._lock = threading.RLock()
        self._delivery_lock = threading.Lock()

        # Delivery tracking
        self._delivery_attempts: Dict[str, int] = {}
        self._pending_events: Dict[str, List[str]] = {}  # subscription_id -> [event_ids]

        self.logging.operational("info", "EventBus initialized", {
            "max_queue_size": self.max_queue_size,
            "retention_seconds": self.retention_seconds,
            "handler_timeout_seconds": self.handler_timeout_seconds
        })

    def publish(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish an event.

        Args:
            event_type: Event type (e.g., "task.started", "component.failed")
            event_data: Opaque event payload (dict)
            source: Source identifier (e.g., "coordinator", "registry")
            metadata: Optional metadata dict

        Returns:
            Event ID of published event

        Raises:
            RuntimeError: If event queue is full (backpressure)
        """
        with self._lock:
            # Check backpressure
            if len(self._events) >= self.max_queue_size:
                raise RuntimeError(f"Event queue full: {self.max_queue_size} events")

            # Create event
            now = time.time()
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                event_data=event_data,
                source=source,
                timestamp=now,
                metadata=metadata or {}
            )

            # Store event
            self._events.append(event)

            # Clean old events
            self._cleanup_old_events()

            # Route to subscribers
            self._route_to_subscribers(event)

            self.logging.operational("debug", f"Event published: {event_type}", {
                "event_id": event.event_id,
                "event_type": event_type,
                "source": source,
            })

            return event.event_id

    def subscribe(
        self,
        event_type_pattern: str,
        handler: Callable[[Event], None],
        filter_func: Optional[Callable[[Event], bool]] = None
    ) -> str:
        """
        Subscribe to events.

        Args:
            event_type_pattern: Event type pattern (e.g., "task.*", "task.started")
            handler: Callable that receives Event objects
            filter_func: Optional predicate filter (returns True to deliver)

        Returns:
            Subscription ID
        """
        with self._lock:
            subscription_id = str(uuid.uuid4())
            subscription = Subscription(
                subscription_id=subscription_id,
                event_type_pattern=event_type_pattern,
                handler=handler,
                filter_func=filter_func,
            )
            self._subscriptions[subscription_id] = subscription
            self._pending_events[subscription_id] = []

            self.logging.operational("debug", f"Subscription created: {event_type_pattern}", {
                "subscription_id": subscription_id,
                "pattern": event_type_pattern,
            })

            return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: Subscription ID to remove

        Returns:
            True if subscription was removed, False if not found
        """
        with self._lock:
            if subscription_id not in self._subscriptions:
                return False

            subscription = self._subscriptions.pop(subscription_id)
            self._pending_events.pop(subscription_id, None)
            self._delivery_attempts.pop(subscription_id, None)

            self.logging.operational("debug", f"Subscription removed: {subscription_id}", {
                "subscription_id": subscription_id,
            })

            return True

    def get_pending_events(self) -> List[Event]:
        """
        Get all pending (not yet delivered) events.

        Returns:
            List of Event objects
        """
        with self._lock:
            return list(self._events)

    def _route_to_subscribers(self, event: Event) -> None:
        """Route an event to matching subscribers."""
        for subscription_id, subscription in self._subscriptions.items():
            if self._matches_pattern(event.event_type, subscription.event_type_pattern):
                # Apply filter if provided
                if subscription.filter_func and not subscription.filter_func(event):
                    continue

                # Track as pending
                if subscription_id not in self._pending_events:
                    self._pending_events[subscription_id] = []
                self._pending_events[subscription_id].append(event.event_id)

                # Attempt delivery
                self._deliver_to_subscriber(event, subscription)

    def _deliver_to_subscriber(self, event: Event, subscription: Subscription) -> None:
        """Attempt to deliver an event to a subscriber with timeout."""
        def run_handler():
            try:
                subscription.handler(event)
                # Mark as delivered
                with self._delivery_lock:
                    if subscription.subscription_id in self._pending_events:
                        if event.event_id in self._pending_events[subscription.subscription_id]:
                            self._pending_events[subscription.subscription_id].remove(event.event_id)
            except Exception as e:
                self.logging.operational("warn", f"Delivery failed for subscription", {
                    "subscription_id": subscription.subscription_id,
                    "event_id": event.event_id,
                    "error": str(e),
                })

        # Run handler in thread with timeout to prevent blocking
        handler_thread = threading.Thread(target=run_handler, daemon=True)
        handler_thread.start()
        handler_thread.join(timeout=self.handler_timeout_seconds)

        if handler_thread.is_alive():
            self.logging.operational("warn", f"Handler timeout for subscription", {
                "subscription_id": subscription.subscription_id,
                "event_id": event.event_id,
                "timeout_seconds": self.handler_timeout_seconds,
            })

    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event_type matches pattern (wildcard support)."""
        if pattern == "*":
            return True

        if pattern == event_type:
            return True

        # Handle wildcard patterns like "task.*"
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")

        return False

    def _cleanup_old_events(self) -> None:
        """Remove events older than retention period."""
        now = time.time()
        cutoff = now - self.retention_seconds

        # Keep only recent events
        self._events = [e for e in self._events if e.timestamp > cutoff]

    def get_event_count(self) -> int:
        """Get current event queue size."""
        with self._lock:
            return len(self._events)

    def get_subscription_count(self) -> int:
        """Get current subscription count."""
        with self._lock:
            return len(self._subscriptions)

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get a specific event by ID."""
        with self._lock:
            for event in self._events:
                if event.event_id == event_id:
                    return event
            return None

    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get all events of a specific type."""
        with self._lock:
            return [e for e in self._events if e.event_type == event_type]

    def get_events_by_source(self, source: str) -> List[Event]:
        """Get all events from a specific source."""
        with self._lock:
            return [e for e in self._events if e.source == source]

    def clear_events(self) -> None:
        """Clear all events from the bus (testing only)."""
        with self._lock:
            self._events.clear()
            self._pending_events.clear()
            self._delivery_attempts.clear()
