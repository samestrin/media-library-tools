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

import contextlib
import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

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