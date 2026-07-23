"""Crystal Runtime Configuration: Centralized configuration management."""

from typing import Any, Dict, Optional, List
import json
import os
from pathlib import Path


class Config:
    """Centralized configuration management for the runtime."""

    # Allowlist of safe configuration keys that can be set via environment variables
    ALLOWED_ENV_KEYS = {
        "coordinator.default_timeout_seconds",
        "coordinator.retry_count",
        "coordinator.max_concurrent_tasks",
        "coordinator.log_level",
        "registry.heartbeat_timeout_seconds",
        "registry.status_check_interval_seconds",
        "registry.max_services",
        "registry.log_level",
        "api.host",
        "api.port",
        "api.rate_limit_per_minute",
        "api.log_level",
        "plugins.enabled",
        "plugins.directory",
        "plugins.auto_load",
        "plugins.log_level",
        "logging.log_level",
        "logging.audit_enabled",
    }

    def __init__(self, config_file: Optional[str] = None, env_prefix: str = "CRYSTAL_") -> None:
        """
        Initialize the Config manager.

        Args:
            config_file: Path to YAML/JSON config file (optional)
            env_prefix: Prefix for environment variables (default: CRYSTAL_)

        Raises:
            ValueError: If config file is invalid or required keys are missing
        """
        self.config_file = config_file
        self.env_prefix = env_prefix
        self._config: Dict[str, Any] = {}
        self._overrides: Dict[str, Any] = {}

        # Load configuration from file if provided
        if config_file:
            self._load_from_file(config_file)

        # Load configuration from environment variables
        self._load_from_environment()

        # Validate required keys
        self._validate_required_keys()

    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from a file (JSON or YAML)."""
        file_path = Path(config_file)

        if not file_path.exists():
            raise ValueError(f"Config file not found: {config_file}")

        try:
            if config_file.endswith(".json"):
                with open(config_file, "r") as f:
                    self._config = json.load(f)
            elif config_file.endswith(".yaml") or config_file.endswith(".yml"):
                # Try to import yaml, fall back to json if not available
                try:
                    import yaml
                    with open(config_file, "r") as f:
                        self._config = yaml.safe_load(f) or {}
                except ImportError:
                    raise ValueError("YAML support requires 'pyyaml' package")
            else:
                raise ValueError(f"Unsupported config file format: {config_file}")
        except Exception as e:
            raise ValueError(f"Failed to load config file {config_file}: {e}")

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Extract config key from env var name
                config_key = key[len(self.env_prefix):].lower()

                # Convert to nested key format (e.g., CRYSTAL_COORDINATOR__TIMEOUT -> coordinator.timeout)
                config_key = config_key.replace("__", ".")

                # SECURITY: Only allow allowlisted configuration keys
                if config_key not in self.ALLOWED_ENV_KEYS:
                    # Silently skip disallowed keys to prevent information disclosure
                    continue

                # Try to parse as JSON first (for complex types)
                try:
                    parsed_value = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    parsed_value = value

                # Set in config (environment overrides file)
                self._set_nested(config_key, parsed_value)

    def _set_nested(self, key: str, value: Any) -> None:
        """Set a nested config value using dot notation."""
        parts = key.split(".")
        current = self._config

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Can't traverse further
                return

            current = current[part]

        current[parts[-1]] = value

    def _validate_required_keys(self) -> None:
        """Validate that required configuration keys exist."""
        # Define required keys - these can be customized per application
        required_keys = []

        for key in required_keys:
            if not self.get(key):
                raise ValueError(f"Required configuration key missing: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # Check overrides first
        if key in self._overrides:
            return self._overrides[key]

        # Get from config
        parts = key.split(".")
        current = self._config

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get all configuration in a section.

        Args:
            section: Section name (e.g., "coordinator", "registry")

        Returns:
            Dictionary of all config in that section
        """
        return self.get(section, {})

    def override(self, key: str, value: Any) -> None:
        """
        Override a configuration value at runtime.

        Args:
            key: Configuration key
            value: Value to set
        """
        self._overrides[key] = value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value (alias for override).

        Args:
            key: Configuration key
            value: Value to set
        """
        self.override(key, value)

    def clear_overrides(self) -> None:
        """Clear all runtime overrides."""
        self._overrides.clear()

    def validate(self, schema: Dict[str, Any]) -> bool:
        """
        Validate configuration against a schema.

        Args:
            schema: Validation schema (custom format)

        Returns:
            True if valid, raises ValueError if invalid
        """
        # Simple schema validation - can be extended
        for key, constraints in schema.items():
            value = self.get(key)

            if constraints.get("required") and value is None:
                raise ValueError(f"Required key missing: {key}")

            if "type" in constraints:
                expected_type = constraints["type"]
                if value is not None and not isinstance(value, expected_type):
                    raise ValueError(f"Invalid type for {key}: expected {expected_type}, got {type(value)}")

            if "min" in constraints and value is not None:
                if value < constraints["min"]:
                    raise ValueError(f"Value too small for {key}: {value} < {constraints['min']}")

            if "max" in constraints and value is not None:
                if value > constraints["max"]:
                    raise ValueError(f"Value too large for {key}: {value} > {constraints['max']}")

        return True

    def reload(self) -> None:
        """Reload configuration from file and environment."""
        self._config.clear()
        self._overrides.clear()

        if self.config_file:
            self._load_from_file(self.config_file)

        self._load_from_environment()
        self._validate_required_keys()

    def to_dict(self) -> Dict[str, Any]:
        """
        Get all configuration as a dictionary.

        Returns:
            Configuration dictionary
        """
        # Merge config and overrides
        result = dict(self._config)
        result.update(self._overrides)
        return result

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration (alias for to_dict).

        Returns:
            Configuration dictionary
        """
        return self.to_dict()
