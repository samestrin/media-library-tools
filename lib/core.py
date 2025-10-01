#!/usr/bin/env python3
"""
Core Utilities Module for Media Library Tools
Version: 1.0

This module contains essential utility functions including:
- Platform detection and environment handling
- Configuration management and global settings
- File locking mechanisms for concurrent execution
- Interactive mode detection for automation support

This is part of the modular library structure that enables selective inclusion
in built tools while maintaining the self-contained principle.
"""

import argparse
import contextlib
import os
import platform
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

# Platform-specific imports
try:
    import fcntl  # Unix/Linux/macOS
except ImportError:
    fcntl = None  # Windows

try:
    import msvcrt  # Windows
except ImportError:
    msvcrt = None  # Unix/Linux/macOS


# =============================================================================
# Environment Variable Namespace Migration
# =============================================================================

# Migration map for environment variable namespace (Legacy → MLT_)
MIGRATION_MAP = {
    # API Credentials (6 variables)
    'TVDB_API_KEY': 'MLT_TVDB_API_KEY',
    'PLEX_TOKEN': 'MLT_PLEX_TOKEN',
    'PLEX_SERVER': 'MLT_PLEX_SERVER',
    'OPENAI_API_KEY': 'MLT_OPENAI_API_KEY',
    'OPENAI_API_BASE_URL': 'MLT_OPENAI_API_BASE_URL',
    'OPENAI_API_MODEL': 'MLT_OPENAI_API_MODEL',

    # Automation Settings (4 variables)
    'AUTO_EXECUTE': 'MLT_AUTO_EXECUTE',
    'AUTO_CONFIRM': 'MLT_AUTO_CONFIRM',
    'QUIET_MODE': 'MLT_QUIET_MODE',
    'AUTO_CLEANUP': 'MLT_AUTO_CLEANUP',

    # Debug and Logging (4 variables)
    'DEBUG': 'MLT_DEBUG',
    'VERBOSE': 'MLT_VERBOSE',
    'PLEX_DEBUG': 'MLT_PLEX_DEBUG',
    'NO_EMOJIS': 'MLT_NO_EMOJIS',

    # Testing Configuration (7 variables)
    'TEST_VERBOSE': 'MLT_TEST_VERBOSE',
    'TEST_DEBUG': 'MLT_TEST_DEBUG',
    'TEST_CLEANUP': 'MLT_TEST_CLEANUP',
    'PRESERVE_FIXTURES': 'MLT_PRESERVE_FIXTURES',
    'MAX_TEST_DIRS': 'MLT_MAX_TEST_DIRS',
    'TEST_TIMEOUT': 'MLT_TEST_TIMEOUT',
    'LARGE_FILE_THRESHOLD': 'MLT_LARGE_FILE_THRESHOLD',

    # Legacy Variables (2 variables)
    'MAX_FILES': 'MLT_MAX_FILES',
    'LOG_LEVEL': 'MLT_LOG_LEVEL'
}

# Reverse map for efficient lookup (MLT_ → Legacy)
REVERSE_MIGRATION_MAP = {v: k for k, v in MIGRATION_MAP.items()}

# Module-level tracking of shown warnings (one per session)
_shown_deprecation_warnings = set()
_deprecation_warnings_suppressed = None  # Cache the suppression setting


# =============================================================================
# Deprecation Warning System
# =============================================================================

def _should_show_deprecation_warnings() -> bool:
    """
    Determine if deprecation warnings should be displayed.

    Warnings are suppressed in non-interactive environments and when
    MLT_SUPPRESS_DEPRECATION_WARNINGS is set.

    Returns:
        bool: True if warnings should be shown, False otherwise
    """
    global _deprecation_warnings_suppressed

    # Cache the result to avoid repeated environment variable lookups
    if _deprecation_warnings_suppressed is None:
        # Check suppression environment variable
        suppress = os.environ.get('MLT_SUPPRESS_DEPRECATION_WARNINGS', '').lower()
        _deprecation_warnings_suppressed = suppress in ('true', '1', 'yes', 'on')

    # Don't show in non-interactive environments (defined later in this file)
    # We'll check this on every call since is_non_interactive() is cheap
    if is_non_interactive():
        return False

    return not _deprecation_warnings_suppressed


def _show_deprecation_warning(legacy_var: str, mlt_var: str, source: str = 'environment') -> None:
    """
    Display deprecation warning for legacy variable usage.

    Warnings are shown only once per variable per session and respect
    the suppression flag and non-interactive environment detection.

    Args:
        legacy_var: Legacy variable name (e.g., 'AUTO_EXECUTE')
        mlt_var: New MLT_ prefixed variable name (e.g., 'MLT_AUTO_EXECUTE')
        source: Source of the variable (e.g., 'environment', 'file_mlt', 'env_legacy')
    """
    # Only show each warning once per session
    warning_key = f"{legacy_var}:{source}"
    if warning_key in _shown_deprecation_warnings:
        return

    _shown_deprecation_warnings.add(warning_key)

    # Don't show if suppressed or in non-interactive mode
    if not _should_show_deprecation_warnings():
        return

    # Format source for user-friendly display
    source_display = source.replace('_', ' ')

    # Display warning to stderr with clear guidance
    print(f"Warning: Using legacy environment variable '{legacy_var}' from {source_display}.",
          file=sys.stderr)
    print(f"         Please migrate to '{mlt_var}' for future compatibility.",
          file=sys.stderr)
    print(f"         Legacy support will be removed in a future version.",
          file=sys.stderr)
    print(f"         Set MLT_SUPPRESS_DEPRECATION_WARNINGS=true to hide these warnings.",
          file=sys.stderr)


# =============================================================================
# Configuration Resolution Core
# =============================================================================

def _resolve_config_with_namespace(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    local_env_path: Optional[str] = None
) -> Tuple[Any, str]:
    """
    Resolve configuration value with namespace support.

    Priority Order:
    1. CLI Arguments (MLT_ then legacy)
    2. MLT_ Environment Variables
    3. Legacy Environment Variables (with deprecation)
    4. MLT_ Local .env File Variables
    5. Legacy Local .env File Variables (with deprecation)
    6. MLT_ Global .env File Variables
    7. Legacy Global .env File Variables (with deprecation)
    8. Not Found

    Args:
        key: Base key without MLT_ prefix (e.g., 'AUTO_EXECUTE')
        cli_args: Parsed CLI arguments
        local_env_path: Path to local .env file

    Returns:
        Tuple of (value, source) where source indicates where value was found:
        - 'cli_mlt': CLI argument with MLT_ prefix
        - 'cli_legacy': CLI argument with legacy name
        - 'env_mlt': Environment variable with MLT_ prefix
        - 'env_legacy': Environment variable with legacy name
        - 'file_mlt': Local .env file with MLT_ prefix
        - 'file_legacy': Local .env file with legacy name
        - 'global_mlt': Global .env file with MLT_ prefix
        - 'global_legacy': Global .env file with legacy name
        - 'not_found': Value not found in any source
    """
    mlt_key = f"MLT_{key}"
    legacy_key = key

    # 1. Check CLI arguments (highest priority)
    if cli_args is not None:
        # Try MLT_ attribute first
        cli_attr_mlt = mlt_key.lower()
        if hasattr(cli_args, cli_attr_mlt):
            value = getattr(cli_args, cli_attr_mlt)
            if value is not None:
                return (value, 'cli_mlt')

        # Try legacy attribute
        cli_attr_legacy = legacy_key.lower()
        if hasattr(cli_args, cli_attr_legacy):
            value = getattr(cli_args, cli_attr_legacy)
            if value is not None:
                return (value, 'cli_legacy')

    # 2. Check MLT_ environment variable
    value = os.environ.get(mlt_key)
    if value is not None:
        return (value, 'env_mlt')

    # 3. Check legacy environment variable
    value = os.environ.get(legacy_key)
    if value is not None:
        return (value, 'env_legacy')

    # 4. Check local .env file (both MLT_ and legacy)
    local_env = read_local_env_file(local_env_path, use_cache=True)
    if mlt_key in local_env:
        return (local_env[mlt_key], 'file_mlt')

    if legacy_key in local_env:
        return (local_env[legacy_key], 'file_legacy')

    # 5. Check global .env file (both MLT_ and legacy)
    global_env_path = str(Path.home() / ".media-library-tools" / ".env")
    global_env = read_local_env_file(global_env_path, use_cache=True)
    if mlt_key in global_env:
        return (global_env[mlt_key], 'global_mlt')

    if legacy_key in global_env:
        return (global_env[legacy_key], 'global_legacy')

    # 6. Not found in any source
    return (None, 'not_found')


def read_config_value_with_namespace(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    default: Optional[Union[str, bool, int]] = None,
    value_type: str = 'str',
    local_env_path: Optional[str] = None,
    show_deprecation: bool = True
) -> Union[str, bool, int, None]:
    """
    Read configuration value with MLT_ namespace support and backward compatibility.

    This is the primary configuration reading function that should be used by all tools.
    It supports both new MLT_ prefixed variables and legacy variables with deprecation warnings.

    Priority Order:
    1. CLI Arguments (highest priority)
    2. MLT_ Environment Variables
    3. Legacy Environment Variables (with deprecation)
    4. MLT_ .env File Variables
    5. Legacy .env File Variables (with deprecation)
    6. Default Value (if provided)

    Args:
        key: Configuration key WITHOUT MLT_ prefix (e.g., 'AUTO_EXECUTE', not 'MLT_AUTO_EXECUTE')
        cli_args: Parsed CLI arguments namespace
        default: Default value if not found in any source
        value_type: Type conversion ('str', 'bool', 'int')
        local_env_path: Path to local .env file (defaults to current directory)
        show_deprecation: Show deprecation warning for legacy variable usage

    Returns:
        Configuration value with proper type conversion, or default if not found

    Examples:
        >>> # Read boolean with CLI priority
        >>> debug = read_config_value_with_namespace('DEBUG', cli_args=args, default=False, value_type='bool')

        >>> # Read API key
        >>> api_key = read_config_value_with_namespace('OPENAI_API_KEY', default='')

        >>> # Read with custom .env path
        >>> verbose = read_config_value_with_namespace('VERBOSE', local_env_path='/path/to/.env', value_type='bool')
    """
    # Resolve value with namespace support
    raw_value, source = _resolve_config_with_namespace(key, cli_args, local_env_path)

    # Show deprecation warning if using legacy variable
    if raw_value is not None and 'legacy' in source and show_deprecation:
        mlt_key = f"MLT_{key}"
        _show_deprecation_warning(key, mlt_key, source)

    # Use default if not found
    if raw_value is None:
        return default

    # Type conversion
    if value_type == 'bool':
        return str(raw_value).lower() in ('true', '1', 'yes', 'on')
    elif value_type == 'int':
        try:
            return int(raw_value)
        except (ValueError, TypeError):
            return default
    else:  # str
        return str(raw_value)


def read_config_bool_with_namespace(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    default: bool = False,
    local_env_path: Optional[str] = None,
    show_deprecation: bool = True
) -> bool:
    """
    Convenience function for reading boolean configuration values with namespace support.

    This is a wrapper around read_config_value_with_namespace() optimized for boolean values.

    Args:
        key: Configuration key WITHOUT MLT_ prefix (e.g., 'AUTO_EXECUTE')
        cli_args: Parsed CLI arguments namespace
        default: Default boolean value
        local_env_path: Path to local .env file
        show_deprecation: Show deprecation warning for legacy variables

    Returns:
        Boolean configuration value

    Examples:
        >>> # Read debug flag
        >>> debug = read_config_bool_with_namespace('DEBUG', cli_args=args)

        >>> # Read with default True
        >>> auto_exec = read_config_bool_with_namespace('AUTO_EXECUTE', default=True)

        >>> # Suppress deprecation warnings
        >>> quiet = read_config_bool_with_namespace('QUIET_MODE', show_deprecation=False)
    """
    result = read_config_value_with_namespace(
        key, cli_args, default, 'bool', local_env_path, show_deprecation
    )
    return bool(result)


# =============================================================================
# Core Utility Functions
# =============================================================================

def is_non_interactive() -> bool:
    """
    Detect if running in non-interactive environment (cron, etc.).

    Returns:
        True if non-interactive, False otherwise
    """
    # Check if stdin is not a TTY (common in cron jobs)
    if not sys.stdin.isatty():
        return True

    # Check for common non-interactive environment variables
    non_interactive_vars = ["CRON", "CI", "AUTOMATED", "NON_INTERACTIVE"]
    for var in non_interactive_vars:
        if os.environ.get(var):
            return True

    # Check if TERM is not set or is 'dumb' (common in automated environments)
    term = os.environ.get("TERM", "")
    return bool(not term or term == "dumb")


def read_global_config_bool(var_name: str, default: bool = False) -> bool:
    """
    Read a boolean environment variable with support for .env files.

    DEPRECATED: This function is maintained for backward compatibility.
    New code should use read_config_bool() which supports CLI argument priority.

    Args:
        var_name: Name of the environment variable
        default: Default value if not found

    Returns:
        Boolean value of the environment variable
    """
    # Check environment variable directly
    value = os.environ.get(var_name)
    if value is not None:
        return value.lower() in ("true", "1", "yes", "on")

    # Check local .env file
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{var_name}="):
                        value = line.split("=", 1)[1].strip()
                        return value.lower() in ("true", "1", "yes", "on")
        except OSError:
            pass

    # Check global .env file
    global_env_path = Path.home() / ".media-library-tools" / ".env"
    if global_env_path.exists():
        try:
            with open(global_env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{var_name}="):
                        value = line.split("=", 1)[1].strip()
                        return value.lower() in ("true", "1", "yes", "on")
        except OSError:
            pass

    return default


class ConfigCache:
    """
    Thread-safe configuration cache with TTL support.

    Caches configuration values from .env files to avoid repeated file system
    operations. Uses threading locks for thread safety.
    """

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize configuration cache.

        Args:
            ttl_seconds: Time-to-live for cached values in seconds (default: 300 = 5 minutes)
        """
        self._cache: Dict[str, Dict[str, str]] = {}
        self._cache_times: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def get_env_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        Get cached .env file contents or read from disk.

        Args:
            file_path: Path to .env file

        Returns:
            Dictionary of key-value pairs from .env file, or None if file doesn't exist
        """
        with self._lock:
            # Check if cached and not expired
            if file_path in self._cache:
                cache_time = self._cache_times.get(file_path, 0)
                if time.time() - cache_time < self._ttl:
                    return self._cache[file_path].copy()

            # Read from disk
            env_dict = self._read_env_file(file_path)
            if env_dict is not None:
                self._cache[file_path] = env_dict
                self._cache_times[file_path] = time.time()

            return env_dict.copy() if env_dict else None

    def _read_env_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        Read .env file from disk.

        Args:
            file_path: Path to .env file

        Returns:
            Dictionary of key-value pairs, or None if file doesn't exist
        """
        if not os.path.exists(file_path):
            return None

        env_dict = {}
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes from values
                        if value and value[0] in ('"', "'") and value[-1] == value[0]:
                            value = value[1:-1]
                        env_dict[key] = value
        except OSError:
            return None

        return env_dict

    def clear_cache(self) -> None:
        """Clear all cached configuration values."""
        with self._lock:
            self._cache.clear()
            self._cache_times.clear()


# Global cache instance
_config_cache = ConfigCache()


def read_local_env_file(
    env_path: Optional[str] = None,
    use_cache: bool = True
) -> Dict[str, str]:
    """
    Read local .env file with optional caching.

    Args:
        env_path: Path to .env file (defaults to current directory .env)
        use_cache: Whether to use cache (default: True)

    Returns:
        Dictionary of key-value pairs from .env file
    """
    if env_path is None:
        env_path = ".env"

    if use_cache:
        result = _config_cache.get_env_file(env_path)
        return result if result is not None else {}
    else:
        # Direct read without cache
        result = _config_cache._read_env_file(env_path)
        return result if result is not None else {}


def read_config_value(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    default: Optional[Union[str, bool, int]] = None,
    value_type: str = 'str',
    local_env_path: Optional[str] = None
) -> Union[str, bool, int, None]:
    """
    Read configuration value following CLI > ENV > Local .env > Global .env priority.

    Priority order (highest to lowest):
    1. CLI arguments (if cli_args provided and attribute exists)
    2. Environment variables
    3. Local .env file (current directory or specified path)
    4. Global .env file (~/.media-library-tools/.env)

    Args:
        key: Configuration key to read
        cli_args: Parsed CLI arguments namespace
        default: Default value if not found in any source
        value_type: Type conversion ('str', 'bool', 'int')
        local_env_path: Path to local .env file (defaults to current directory)

    Returns:
        Configuration value with proper type conversion, or default if not found

    Examples:
        >>> # Read boolean config with CLI priority
        >>> debug_mode = read_config_value('DEBUG', cli_args=args, default=False, value_type='bool')

        >>> # Read string config without CLI args
        >>> api_key = read_config_value('API_KEY', default='', value_type='str')
    """
    # Delegate to namespace-aware function for backward compatibility
    # This maintains the same behavior but adds MLT_ namespace support
    return read_config_value_with_namespace(
        key=key,
        cli_args=cli_args,
        default=default,
        value_type=value_type,
        local_env_path=local_env_path,
        show_deprecation=True
    )


def read_config_bool(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    default: bool = False,
    local_env_path: Optional[str] = None
) -> bool:
    """
    Read boolean configuration value following CLI > ENV > Local .env > Global .env priority.

    UPDATED: This function now delegates to read_config_bool_with_namespace() which
    supports both MLT_ prefixed and legacy environment variables with backward compatibility.

    Convenience wrapper for boolean values.
    Supports: true/false, yes/no, on/off, 1/0 (case-insensitive)

    Args:
        key: Configuration key to read (WITHOUT MLT_ prefix)
        cli_args: Parsed CLI arguments namespace
        default: Default value if not found (default: False)
        local_env_path: Path to local .env file (defaults to current directory)

    Returns:
        Boolean value

    Examples:
        >>> # Read debug flag with CLI priority
        >>> debug = read_config_bool('DEBUG', cli_args=args, default=False)

        >>> # Read auto-confirm setting
        >>> auto_confirm = read_config_bool('AUTO_CONFIRM', default=False)
    """
    # Delegate to namespace-aware function for backward compatibility
    return read_config_bool_with_namespace(
        key=key,
        cli_args=cli_args,
        default=default,
        local_env_path=local_env_path,
        show_deprecation=True
    )


def get_config_source(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    local_env_path: Optional[str] = None
) -> str:
    """
    Determine which source provides a configuration value.

    Args:
        key: Configuration key to check
        cli_args: Parsed CLI arguments namespace
        local_env_path: Path to local .env file

    Returns:
        Source name: 'cli', 'env', 'local_env', 'global_env', or 'not_found'
    """
    # Check CLI arguments
    if cli_args is not None:
        cli_attr = key.lower() if hasattr(cli_args, key.lower()) else key
        if hasattr(cli_args, cli_attr):
            cli_value = getattr(cli_args, cli_attr)
            if cli_value is not None:
                return 'cli'

    # Check environment variable
    if os.environ.get(key) is not None:
        return 'env'

    # Check local .env
    local_env = read_local_env_file(local_env_path)
    if key in local_env:
        return 'local_env'

    # Check global .env
    global_env_path = str(Path.home() / ".media-library-tools" / ".env")
    global_env = read_local_env_file(global_env_path)
    if key in global_env:
        return 'global_env'

    return 'not_found'


def debug_config_resolution(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    local_env_path: Optional[str] = None,
    show_value: bool = False
) -> None:
    """
    Print detailed configuration resolution information for debugging.

    Shows which sources contain the key and which source is being used.

    Args:
        key: Configuration key to debug
        cli_args: Parsed CLI arguments namespace
        local_env_path: Path to local .env file
        show_value: Whether to show actual value (default: False for security)
    """
    print(f"\nConfiguration Debug: {key}")
    print("=" * 60)

    # Check each source
    sources_found = []

    # CLI
    if cli_args is not None:
        cli_attr = key.lower() if hasattr(cli_args, key.lower()) else key
        if hasattr(cli_args, cli_attr):
            cli_value = getattr(cli_args, cli_attr)
            if cli_value is not None:
                sources_found.append('CLI')
                if show_value:
                    print(f"  CLI: {cli_value}")
                else:
                    print(f"  CLI: <set>")

    # ENV
    env_value = os.environ.get(key)
    if env_value is not None:
        sources_found.append('ENV')
        if show_value:
            print(f"  ENV: {env_value}")
        else:
            print(f"  ENV: <set>")

    # Local .env
    local_env = read_local_env_file(local_env_path)
    if key in local_env:
        sources_found.append('Local .env')
        if show_value:
            print(f"  Local .env: {local_env[key]}")
        else:
            print(f"  Local .env: <set>")

    # Global .env
    global_env_path = str(Path.home() / ".media-library-tools" / ".env")
    global_env = read_local_env_file(global_env_path)
    if key in global_env:
        sources_found.append('Global .env')
        if show_value:
            print(f"  Global .env: {global_env[key]}")
        else:
            print(f"  Global .env: <set>")

    # Show resolution
    print(f"\nResolution:")
    if sources_found:
        print(f"  Found in: {', '.join(sources_found)}")
        print(f"  Using: {sources_found[0]} (highest priority)")
    else:
        print(f"  Not found in any source")

    print("=" * 60)


def validate_config_setup() -> Dict[str, Any]:
    """
    Validate configuration setup and check for potential issues.

    Returns:
        Dictionary with validation results including:
        - 'valid': bool indicating overall validity
        - 'warnings': list of warning messages
        - 'info': list of informational messages
        - 'files': dict of file status (local_env, global_env)
    """
    results = {
        'valid': True,
        'warnings': [],
        'info': [],
        'files': {}
    }

    # Check local .env
    local_env_path = ".env"
    if os.path.exists(local_env_path):
        results['files']['local_env'] = 'exists'
        results['info'].append(f"Local .env file found: {os.path.abspath(local_env_path)}")

        # Check readability
        try:
            with open(local_env_path, 'r') as f:
                f.read()
        except OSError as e:
            results['warnings'].append(f"Local .env exists but cannot be read: {e}")
            results['valid'] = False
    else:
        results['files']['local_env'] = 'not_found'
        results['info'].append("No local .env file found")

    # Check global .env
    global_env_path = Path.home() / ".media-library-tools" / ".env"
    if global_env_path.exists():
        results['files']['global_env'] = 'exists'
        results['info'].append(f"Global .env file found: {global_env_path}")

        # Check readability
        try:
            with open(global_env_path, 'r') as f:
                f.read()
        except OSError as e:
            results['warnings'].append(f"Global .env exists but cannot be read: {e}")
            results['valid'] = False
    else:
        results['files']['global_env'] = 'not_found'
        results['info'].append(f"No global .env file found (expected at: {global_env_path})")

    # Check for conflicts (same key in multiple places with different values)
    if results['files']['local_env'] == 'exists' and results['files']['global_env'] == 'exists':
        local_env = read_local_env_file(local_env_path)
        global_env = read_local_env_file(str(global_env_path))

        # Find keys that exist in both
        common_keys = set(local_env.keys()) & set(global_env.keys())
        if common_keys:
            results['info'].append(f"Keys defined in both files: {', '.join(sorted(common_keys))}")
            results['info'].append("(Local .env values will take priority)")

    return results


def is_windows() -> bool:
    """
    Detect if running on Windows platform.

    Returns:
        True if running on Windows, False otherwise
    """
    return platform.system().lower() == "windows"


def should_use_emojis() -> bool:
    """
    Determine if emojis should be used based on platform and environment.

    Returns:
        True if emojis should be used, False otherwise
    """
    # Don't use emojis on Windows to avoid encoding issues
    if is_windows():
        return False

    # Don't use emojis in non-interactive environments
    if is_non_interactive():
        return False

    # Check for explicit emoji suppression
    return not read_global_config_bool("NO_EMOJIS", False)


class FileLock:
    """
    File locking utility class for preventing concurrent executions.
    """

    def __init__(self, lock_prefix: str = "media_library_tool"):
        """
        Initialize file lock.

        Args:
            lock_prefix: Prefix for lock file name
        """
        self.lock_prefix = lock_prefix
        self.lock_file = None

    def acquire_lock(self, force: bool = False) -> bool:
        """
        Acquire file lock to prevent multiple instances.

        Args:
            force: If True, skip locking mechanism

        Returns:
            True if lock acquired successfully, False otherwise
        """
        if force:
            return True

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", prefix=f"{self.lock_prefix}_", suffix=".lock", delete=False
            ) as temp_file:
                self.lock_file = temp_file
                
                # Platform-specific file locking
                if fcntl is not None:  # Unix/Linux/macOS
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                elif msvcrt is not None:  # Windows
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    # Fallback: no locking available, just proceed
                    pass
                    
                self.lock_file.write(str(os.getpid()))
                self.lock_file.flush()
            return True
        except (OSError, IOError) as e:
            if self.lock_file:
                self.lock_file.close()
                with contextlib.suppress(OSError):
                    os.unlink(self.lock_file.name)
                self.lock_file = None
            print(
                "Error: Another instance is already running. Use --force to override."
            )
            print(f"Lock error: {e}")
            return False

    def release_lock(self) -> None:
        """
        Release the file lock.
        """
        if self.lock_file:
            try:
                # Only unlock if file is still open
                if not self.lock_file.closed:
                    # Platform-specific file unlocking
                    if fcntl is not None:  # Unix/Linux/macOS
                        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    elif msvcrt is not None:  # Windows
                        msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    # No explicit unlock needed for fallback case
                    
                    self.lock_file.close()
            except (OSError, ValueError, IOError):
                # Handle both file system errors and closed file errors
                pass

            # Always try to remove lock file if it exists
            try:
                if os.path.exists(self.lock_file.name):
                    os.unlink(self.lock_file.name)
            except OSError:
                pass
            finally:
                self.lock_file = None


# Legacy standalone functions for backward compatibility
def acquire_lock(
    lock_prefix: str = "media_library_tool", force: bool = False
) -> Tuple[bool, Optional[FileLock]]:
    """
    Legacy function for acquiring file locks.

    Args:
        lock_prefix: Prefix for lock file name
        force: If True, skip locking mechanism

    Returns:
        Tuple of (success: bool, lock_instance: FileLock or None)
    """
    lock = FileLock(lock_prefix)
    success = lock.acquire_lock(force)
    return success, lock if success else None


def release_lock(lock_instance: FileLock) -> None:
    """
    Legacy function for releasing file locks.

    Args:
        lock_instance: FileLock instance to release
    """
    if lock_instance:
        lock_instance.release_lock()