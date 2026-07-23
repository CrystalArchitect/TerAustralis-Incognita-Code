"""Crystal Runtime Plugins: Load, validate, and manage plugin lifecycle."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import importlib
import inspect
import sys
import time
import uuid
import os

from ..config.config import Config
from ..logging.logger import Logger


@dataclass
class PluginMetadata:
    """Metadata about a plugin."""
    name: str
    version: str
    description: str
    author: str
    required_hooks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    min_runtime_version: str = "0.1.0"
    max_runtime_version: Optional[str] = None


@dataclass
class HookResult:
    """Result of hook invocation."""
    hook_name: str
    succeeded: int = 0
    failed: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""
    plugin_id: str
    name: str
    version: str
    status: str  # "loaded" | "failed" | "disabled"
    hooks_registered: List[str] = field(default_factory=list)
    load_time: float = field(default_factory=time.time)


class PluginLoadError(Exception):
    """Plugin cannot be loaded."""

    def __init__(self, error_code: str, plugin_name: str, reason: str):
        self.error_code = error_code
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"Failed to load plugin '{plugin_name}': {reason}")


class PluginManager:
    """Manages plugin loading, initialization, and execution."""

    def __init__(self, config: Config, logging: Logger) -> None:
        """
        Initialize the PluginManager.

        Args:
            config: Config instance
            logging: Logger instance

        Raises:
            ValueError: If required configuration is missing
        """
        self.config = config
        self.logging = logging

        # Load plugin manager configuration
        try:
            self.enabled = config.get("plugins.enabled", True)
            self.plugin_directory = config.get("plugins.directory", "./plugins")
            self.auto_load = config.get("plugins.auto_load", False)
            self.log_level = config.get("plugins.log_level", "info")
        except Exception as e:
            raise ValueError(f"Failed to load plugin manager configuration: {e}")

        # Plugin storage
        self._plugins: Dict[str, Dict[str, Any]] = {}
        self._hooks: Dict[str, List[tuple]] = {}  # hook_name -> [(plugin_id, handler_func)]
        self._plugin_modules: Dict[str, Any] = {}

        self.logging.operational("info", "PluginManager initialized", {
            "plugin_directory": self.plugin_directory,
            "auto_load": self.auto_load,
        })

    def load(
        self,
        plugin_path: str,
        metadata: Optional[PluginMetadata] = None
    ) -> str:
        """
        Load a plugin from disk or package.

        Args:
            plugin_path: File path or module name
            metadata: PluginMetadata with version, hooks, etc.

        Returns:
            plugin_id: Unique identifier for loaded plugin

        Raises:
            PluginLoadError: If plugin cannot be loaded or is incompatible
        """
        if not self.enabled:
            raise PluginLoadError("disabled", plugin_path, "Plugin manager is disabled")

        plugin_id = str(uuid.uuid4())

        try:
            # Validate path
            if not self._validate_plugin_path(plugin_path):
                raise PluginLoadError("not_found", plugin_path, f"Plugin path not found: {plugin_path}")

            # Load module
            module = self._load_plugin_module(plugin_path)

            # Get metadata if not provided
            if metadata is None:
                metadata = self._extract_metadata(module)

            # Validate compatibility
            if not self._check_compatibility(metadata):
                raise PluginLoadError(
                    "incompatible",
                    metadata.name,
                    f"Incompatible with runtime version"
                )

            # Check dependencies
            for dep in metadata.dependencies:
                if dep not in self._plugins:
                    raise PluginLoadError(
                        "incompatible",
                        metadata.name,
                        f"Required dependency not loaded: {dep}"
                    )

            # Call plugin's init function if available
            if hasattr(module, "init"):
                try:
                    module.init(self)
                except Exception as e:
                    raise PluginLoadError("init_failed", metadata.name, str(e))

            # Register hooks
            hooks_registered = self._register_hooks(plugin_id, module, metadata)

            # Store plugin info
            self._plugins[plugin_id] = {
                "metadata": metadata,
                "module": module,
                "status": "loaded",
                "hooks_registered": hooks_registered,
            }

            self._plugin_modules[plugin_id] = module

            # Log
            self.logging.audit(
                event_type="plugin_loaded",
                actor="system",
                action="load_plugin",
                resource=metadata.name,
                result="success",
                context={
                    "plugin_id": plugin_id,
                    "version": metadata.version,
                    "hooks": hooks_registered,
                }
            )

            self.logging.operational("info", f"Plugin '{metadata.name}' loaded", {
                "plugin_id": plugin_id,
                "version": metadata.version,
            })

            return plugin_id

        except PluginLoadError:
            raise
        except Exception as e:
            raise PluginLoadError("syntax_error", plugin_path, str(e))

    def unload(self, plugin_id: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_id: Plugin to unload

        Returns:
            True if unloaded, False if not found
        """
        if plugin_id not in self._plugins:
            return False

        plugin_info = self._plugins[plugin_id]
        module = plugin_info["module"]
        metadata = plugin_info["metadata"]

        try:
            # Call plugin's shutdown function if available
            if hasattr(module, "shutdown"):
                try:
                    module.shutdown(self)
                except Exception as e:
                    self.logging.operational("warn", f"Plugin shutdown error for {metadata.name}", {
                        "error": str(e),
                    })

            # Unregister hooks
            for hook_name in plugin_info["hooks_registered"]:
                if hook_name in self._hooks:
                    self._hooks[hook_name] = [
                        (pid, handler) for pid, handler in self._hooks[hook_name]
                        if pid != plugin_id
                    ]

            # Remove from storage
            del self._plugins[plugin_id]
            self._plugin_modules.pop(plugin_id, None)

            # Log
            self.logging.audit(
                event_type="plugin_unloaded",
                actor="system",
                action="unload_plugin",
                resource=metadata.name,
                result="success",
                context={"plugin_id": plugin_id}
            )

            self.logging.operational("info", f"Plugin '{metadata.name}' unloaded", {
                "plugin_id": plugin_id,
            })

            return True

        except Exception as e:
            self.logging.operational("error", f"Error unloading plugin {plugin_id}", {
                "error": str(e),
            })
            return False

    def invoke_hook(self, hook_name: str, event: Any) -> HookResult:
        """
        Invoke all plugins' implementations of a hook.

        Args:
            hook_name: Hook name
            event: Event to pass to hook handlers

        Returns:
            HookResult aggregating results from all plugins
        """
        result = HookResult(hook_name=hook_name)

        if hook_name not in self._hooks:
            return result

        for plugin_id, handler_func in self._hooks[hook_name]:
            try:
                handler_result = handler_func(event)
                result.results.append({
                    "plugin_id": plugin_id,
                    "result": handler_result,
                })
                result.succeeded += 1
            except Exception as e:
                result.errors[plugin_id] = str(e)
                result.failed += 1

                self.logging.operational("warn", f"Hook '{hook_name}' failed for plugin {plugin_id}", {
                    "error": str(e),
                })

        return result

    def list_plugins(self) -> List[PluginInfo]:
        """
        Get information about all loaded plugins.

        Returns:
            List of PluginInfo objects
        """
        plugins_info = []
        for plugin_id, plugin_data in self._plugins.items():
            info = PluginInfo(
                plugin_id=plugin_id,
                name=plugin_data["metadata"].name,
                version=plugin_data["metadata"].version,
                status=plugin_data["status"],
                hooks_registered=plugin_data["hooks_registered"],
            )
            plugins_info.append(info)
        return plugins_info

    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get info for a specific plugin."""
        if plugin_id not in self._plugins:
            return None

        plugin_data = self._plugins[plugin_id]
        return PluginInfo(
            plugin_id=plugin_id,
            name=plugin_data["metadata"].name,
            version=plugin_data["metadata"].version,
            status=plugin_data["status"],
            hooks_registered=plugin_data["hooks_registered"],
        )

    def _validate_plugin_path(self, plugin_path: str) -> bool:
        """Check if plugin path exists."""
        # Check if it's a file path
        if os.path.exists(plugin_path):
            return True

        # Check if it's a module in the plugin directory
        full_path = os.path.join(self.plugin_directory, plugin_path)
        if os.path.exists(full_path):
            return True

        # Could be an importable module
        try:
            importlib.util.find_spec(plugin_path)
            return True
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def _is_safe_path(self, path: str) -> bool:
        """Check if path is safe (no directory traversal attacks)."""
        try:
            # Resolve to absolute path
            abs_path = os.path.abspath(path)
            plugin_dir = os.path.abspath(self.plugin_directory)

            # Check if resolved path stays within plugin directory (if using relative path)
            if not abs_path.startswith(plugin_dir) and not os.path.isabs(path):
                return False

            # Reject paths with .. sequences
            if ".." in path:
                return False

            return True
        except Exception:
            return False

    def _load_plugin_module(self, plugin_path: str) -> Any:
        """Load a Python module for a plugin."""
        plugin_id = str(uuid.uuid4())

        # Try as file path
        if os.path.exists(plugin_path):
            # Validate path doesn't traverse directories
            if not self._is_safe_path(plugin_path):
                raise PluginLoadError("invalid_path", plugin_path, "Path traversal detected")

            import importlib.util
            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_id}", plugin_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"plugin_{plugin_id}"] = module
                spec.loader.exec_module(module)
                return module

        # Try as full path in plugin directory
        full_path = os.path.join(self.plugin_directory, plugin_path)
        if os.path.exists(full_path):
            # Validate path doesn't traverse directories
            if not self._is_safe_path(full_path):
                raise PluginLoadError("invalid_path", plugin_path, "Path traversal detected")

            import importlib.util
            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_id}", full_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"plugin_{plugin_id}"] = module
                spec.loader.exec_module(module)
                return module

        # Try as importable module
        try:
            return importlib.import_module(plugin_path)
        except ImportError as e:
            raise PluginLoadError("not_found", plugin_path, str(e))

    def _extract_metadata(self, module: Any) -> PluginMetadata:
        """Extract metadata from a plugin module."""
        if hasattr(module, "PLUGIN_METADATA"):
            metadata = module.PLUGIN_METADATA
            # Validate metadata structure
            if not isinstance(metadata, PluginMetadata):
                raise PluginLoadError("invalid_metadata", getattr(module, "__name__", "unknown"),
                                    "PLUGIN_METADATA must be PluginMetadata instance")
            return metadata

        # Create default metadata
        name = getattr(module, "__name__", "unknown")
        version = getattr(module, "__version__", "0.0.1")
        description = getattr(module, "__doc__", "No description")
        author = getattr(module, "__author__", "Unknown")

        # Validate metadata fields
        if not isinstance(name, str) or not name:
            raise PluginLoadError("invalid_metadata", name, "Plugin name must be non-empty string")
        if not isinstance(version, str) or not version:
            raise PluginLoadError("invalid_metadata", name, "Plugin version must be non-empty string")

        return PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
        )

    def _check_compatibility(self, metadata: PluginMetadata) -> bool:
        """Check if plugin is compatible with runtime version."""
        # Version comparison (simplified)
        runtime_version = "0.3.0"

        # Check minimum version
        if metadata.min_runtime_version:
            if self._compare_versions(runtime_version, metadata.min_runtime_version) < 0:
                return False

        # Check maximum version
        if metadata.max_runtime_version:
            if self._compare_versions(runtime_version, metadata.max_runtime_version) > 0:
                return False

        return True

    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two semantic versions. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2."""
        try:
            # Extract numeric parts only (e.g., "1.0.0-beta" -> "1.0.0")
            def get_numeric_parts(v: str):
                # Get the base version before any pre-release identifiers
                base = v.split("-")[0].split("+")[0]
                parts = []
                for part in base.split("."):
                    try:
                        parts.append(int(part))
                    except ValueError:
                        # Skip non-numeric parts
                        pass
                return parts

            parts1 = get_numeric_parts(v1)
            parts2 = get_numeric_parts(v2)

            # Pad with zeros if needed
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))

            for p1, p2 in zip(parts1, parts2):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1

            return 0
        except Exception:
            # Fallback to string comparison if version parsing fails
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            return 0

    def _register_hooks(self, plugin_id: str, module: Any, metadata: PluginMetadata) -> List[str]:
        """Register hooks from a plugin."""
        hooks_registered = []

        for hook_name in metadata.required_hooks:
            handler_name = f"on_{hook_name}"
            if hasattr(module, handler_name):
                handler = getattr(module, handler_name)
                if callable(handler):
                    if hook_name not in self._hooks:
                        self._hooks[hook_name] = []
                    self._hooks[hook_name].append((plugin_id, handler))
                    hooks_registered.append(hook_name)

        return hooks_registered
