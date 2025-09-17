#!/usr/bin/env python3
"""
Input Validation Module for Media Library Tools
Version: 1.0

This module contains input validation and error handling functions including:
- Command-line argument validation
- Path and filename validation
- Configuration parameter validation
- Error handling and user feedback
- Data sanitization and security checks

This is part of the modular library structure that enables selective inclusion
in built tools while maintaining the self-contained principle.
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Optional, Tuple, Any


def validate_path_argument(path: str, must_exist: bool = True, must_be_dir: bool = True) -> Tuple[bool, str]:
    """
    Validate a path argument with various requirements.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must already exist
        must_be_dir: Whether the path must be a directory
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path cannot be empty"
    
    # Basic path validation
    try:
        path_obj = Path(path)
    except (ValueError, OSError) as e:
        return False, f"Invalid path format: {e}"
    
    if must_exist and not path_obj.exists():
        return False, f"Path does not exist: {path}"
    
    if must_exist and must_be_dir and not path_obj.is_dir():
        return False, f"Path must be a directory: {path}"
    
    if must_exist and not must_be_dir and not path_obj.is_file():
        return False, f"Path must be a file: {path}"
    
    return True, ""


def validate_filename(filename: str, allow_spaces: bool = True) -> Tuple[bool, str]:
    """
    Validate a filename for safety and compatibility.
    
    Args:
        filename: Filename to validate
        allow_spaces: Whether spaces are allowed in filename
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"
    
    # Check for dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        if char in filename:
            return False, f"Filename contains invalid character: {char}"
    
    # Check for spaces if not allowed
    if not allow_spaces and ' ' in filename:
        return False, "Filename cannot contain spaces"
    
    # Check for reserved names on Windows
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                     'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                     'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved_names:
        return False, f"Filename uses reserved name: {name_without_ext}"
    
    # Check filename length (255 is common filesystem limit)
    if len(filename) > 255:
        return False, "Filename too long (max 255 characters)"
    
    return True, ""


def validate_positive_integer(value: str, min_value: int = 1) -> Tuple[bool, Optional[int], str]:
    """
    Validate and convert a string to a positive integer.
    
    Args:
        value: String value to validate
        min_value: Minimum allowed value
        
    Returns:
        Tuple of (is_valid, converted_value, error_message)
    """
    try:
        int_value = int(value)
        if int_value < min_value:
            return False, None, f"Value must be at least {min_value}"
        return True, int_value, ""
    except ValueError:
        return False, None, f"Invalid integer: {value}"


def validate_regex_pattern(pattern: str) -> Tuple[bool, str]:
    """
    Validate a regular expression pattern.
    
    Args:
        pattern: Regex pattern to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern:
        return False, "Pattern cannot be empty"
    
    try:
        re.compile(pattern)
        return True, ""
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"


def validate_directory_writable(path: str) -> Tuple[bool, str]:
    """
    Validate that a directory is writable.
    
    Args:
        path: Directory path to check
        
    Returns:
        Tuple of (is_writable, error_message)
    """
    if not os.path.exists(path):
        return False, f"Directory does not exist: {path}"
    
    if not os.path.isdir(path):
        return False, f"Path is not a directory: {path}"
    
    if not os.access(path, os.W_OK):
        return False, f"Directory is not writable: {path}"
    
    return True, ""


def sanitize_filename(filename: str, replacement_char: str = "_") -> str:
    """
    Sanitize a filename by replacing invalid characters.
    
    Args:
        filename: Original filename
        replacement_char: Character to use as replacement
        
    Returns:
        Sanitized filename
    """
    # Replace dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, replacement_char)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    
    # Handle empty result
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Truncate if too long
    if len(sanitized) > 255:
        name_part = Path(sanitized).stem[:250]
        ext_part = Path(sanitized).suffix
        sanitized = f"{name_part}{ext_part}"
    
    return sanitized


def validate_cli_arguments(parser: argparse.ArgumentParser, args: argparse.Namespace) -> List[str]:
    """
    Validate common CLI arguments and return list of validation errors.
    
    Args:
        parser: ArgumentParser instance
        args: Parsed arguments namespace
        
    Returns:
        List of validation error messages (empty if all valid)
    """
    errors = []
    
    # Validate path argument if present
    if hasattr(args, 'path') and args.path:
        is_valid, error_msg = validate_path_argument(args.path)
        if not error_msg:
            errors.append(error_msg)
    
    # Validate mutually exclusive flags
    if hasattr(args, 'dry_run') and hasattr(args, 'yes'):
        if args.yes and args.dry_run:
            errors.append("Warning: -y/--yes flag has no effect in dry-run mode")
    
    # Validate positive integer arguments
    integer_args = ['depth', 'limit', 'threshold']
    for arg_name in integer_args:
        if hasattr(args, arg_name):
            arg_value = getattr(args, arg_name)
            if arg_value is not None:
                is_valid, _, error_msg = validate_positive_integer(str(arg_value))
                if not is_valid:
                    errors.append(f"Invalid {arg_name}: {error_msg}")
    
    return errors


def check_required_dependencies() -> List[str]:
    """
    Check for required system dependencies and return missing ones.
    
    Returns:
        List of missing dependencies
    """
    missing = []
    
    # Check for common system commands
    required_commands = ['du', 'find']  # Add more as needed
    
    for cmd in required_commands:
        if not _command_exists(cmd):
            missing.append(f"Missing system command: {cmd}")
    
    return missing


def _command_exists(command: str) -> bool:
    """
    Check if a system command exists.
    
    Args:
        command: Command name to check
        
    Returns:
        True if command exists, False otherwise
    """
    import shutil
    return shutil.which(command) is not None


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
    """
    Validate file extension against allowed list.
    
    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (with dots)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"
    
    file_ext = Path(filename).suffix.lower()
    allowed_lower = [ext.lower() for ext in allowed_extensions]
    
    if file_ext not in allowed_lower:
        return False, f"File extension '{file_ext}' not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    return True, ""