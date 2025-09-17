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

import os
import sys
import fcntl
import tempfile
from pathlib import Path
from typing import Optional


def is_non_interactive() -> bool:
    """
    Detect if we're running in a non-interactive environment (e.g., cron job).
    
    Returns:
        bool: True if running non-interactively, False otherwise
    """
    # Check if stdin is not a TTY (common in cron jobs)
    if not sys.stdin.isatty():
        return True
    
    # Check common environment variables that indicate automation
    automation_vars = ['CRON', 'CI', 'AUTOMATED', 'NON_INTERACTIVE']
    for var in automation_vars:
        if os.environ.get(var):
            return True
    
    # Check if TERM is not set (common in cron)
    if not os.environ.get('TERM'):
        return True
    
    return False


def read_global_config_bool(var_name: str, default: bool = False) -> bool:
    """Read a boolean environment variable with support for .env files.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if not found
        
    Returns:
        Boolean value of the environment variable
    """
    # Check environment variable directly
    value = os.environ.get(var_name)
    if value is not None:
        return value.lower() in ('true', '1', 'yes', 'on')
    
    # Check local .env file
    env_file = '.env'
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f'{var_name}='):
                        value = line.split('=', 1)[1].strip()
                        return value.lower() in ('true', '1', 'yes', 'on')
        except (IOError, OSError):
            pass
    
    # Check global .env file
    global_env_path = Path.home() / '.media-library-tools' / '.env'
    if global_env_path.exists():
        try:
            with open(global_env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f'{var_name}='):
                        value = line.split('=', 1)[1].strip()
                        return value.lower() in ('true', '1', 'yes', 'on')
        except (IOError, OSError):
            pass
    
    return default


def acquire_lock(script_name: str) -> Optional[int]:
    """
    Acquire a file lock to prevent multiple instances of the same script.
    
    Args:
        script_name: Name of the script for lock file naming
        
    Returns:
        File descriptor if lock acquired, None if lock failed
    """
    try:
        lock_file = Path(tempfile.gettempdir()) / f"{script_name}.lock"
        fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Write PID to lock file for debugging
        os.write(fd, str(os.getpid()).encode())
        return fd
    except (OSError, IOError):
        return None


def release_lock(fd: Optional[int]) -> None:
    """
    Release a file lock.
    
    Args:
        fd: File descriptor of the lock to release
    """
    if fd is not None:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        except (OSError, IOError):
            pass


def is_windows() -> bool:
    """
    Check if running on Windows platform.
    
    Returns:
        bool: True if running on Windows, False otherwise
    """
    return os.name == 'nt'


def should_use_emojis() -> bool:
    """
    Determine if emoji output should be used based on environment.
    
    Returns:
        bool: True if emojis should be used, False otherwise
    """
    # Disable emojis in non-interactive environments
    if is_non_interactive():
        return False
    
    # Disable emojis on Windows (potential terminal compatibility issues)
    if is_windows():
        return False
    
    # Check for explicit environment variable
    emoji_setting = os.environ.get('USE_EMOJIS', '').lower()
    if emoji_setting in ('false', '0', 'no', 'off'):
        return False
    
    return True