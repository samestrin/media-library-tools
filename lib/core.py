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
    raw_value = None

    # 1. Check CLI arguments (highest priority)
    if cli_args is not None:
        # Try both exact key and lowercase version
        cli_attr = key.lower() if hasattr(cli_args, key.lower()) else key
        if hasattr(cli_args, cli_attr):
            cli_value = getattr(cli_args, cli_attr)
            if cli_value is not None:
                raw_value = str(cli_value)

    # 2. Check environment variable
    if raw_value is None:
        env_value = os.environ.get(key)
        if env_value is not None:
            raw_value = env_value

    # 3. Check local .env file
    if raw_value is None:
        local_env = read_local_env_file(local_env_path)
        if key in local_env:
            raw_value = local_env[key]

    # 4. Check global .env file
    if raw_value is None:
        global_env_path = str(Path.home() / ".media-library-tools" / ".env")
        global_env = read_local_env_file(global_env_path)
        if key in global_env:
            raw_value = global_env[key]

    # Use default if not found anywhere
    if raw_value is None:
        return default

    # Type conversion
    if value_type == 'bool':
        return raw_value.lower() in ('true', '1', 'yes', 'on')
    elif value_type == 'int':
        try:
            return int(raw_value)
        except (ValueError, TypeError):
            return default
    else:  # str
        return raw_value


def read_config_bool(
    key: str,
    cli_args: Optional[argparse.Namespace] = None,
    default: bool = False,
    local_env_path: Optional[str] = None
) -> bool:
    """
    Read boolean configuration value following CLI > ENV > Local .env > Global .env priority.

    Convenience wrapper around read_config_value for boolean values.
    Supports: true/false, yes/no, on/off, 1/0 (case-insensitive)

    Args:
        key: Configuration key to read
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
    result = read_config_value(
        key=key,
        cli_args=cli_args,
        default=default,
        value_type='bool',
        local_env_path=local_env_path
    )
    return bool(result)


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