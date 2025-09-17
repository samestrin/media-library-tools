#!/usr/bin/env python3
"""
User Interface Module for Media Library Tools
Version: 1.0

This module contains user interface functions including:
- Banner display and application branding
- Status message formatting and output
- User confirmation prompts
- Size formatting for human-readable output
- Progress indicators and visual feedback

This is part of the modular library structure that enables selective inclusion
in built tools while maintaining the self-contained principle.
"""

import sys
from typing import Optional


def display_banner(tool_name: str, version: str, description: str) -> None:
    """
    Display a standardized banner for media library tools.
    
    Args:
        tool_name: Name of the tool
        version: Version string
        description: Brief description of tool purpose
    """
    print(f"\n{tool_name} v{version}")
    print("=" * 50)
    print(f"Purpose: {description}")
    print("Part of: Media Library Tools")
    print("=" * 50)


def format_status_message(status: str, message: str, details: Optional[str] = None) -> str:
    """
    Format a status message with consistent styling.
    
    Args:
        status: Status type (SUCCESS, ERROR, WARNING, INFO)
        message: Main message text
        details: Optional additional details
        
    Returns:
        Formatted status message string
    """
    formatted_msg = f"{status}: {message}"
    if details:
        formatted_msg += f" ({details})"
    return formatted_msg


def confirm_action(prompt: str, default_yes: bool = False) -> bool:
    """
    Prompt user for confirmation with consistent behavior.
    
    Args:
        prompt: Question to ask the user
        default_yes: Whether to default to yes if user just presses enter
        
    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]: " if default_yes else " [y/N]: "
    
    try:
        response = input(f"{prompt}{suffix}").strip().lower()
        
        if not response:  # Empty response uses default
            return default_yes
            
        return response in ['y', 'yes']
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled by user.")
        return False


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:  # Bytes
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def show_progress(current: int, total: int, prefix: str = "Progress") -> None:
    """
    Display a simple progress indicator.
    
    Args:
        current: Current progress count
        total: Total items to process
        prefix: Prefix text for progress display
    """
    if total == 0:
        percentage = 100
    else:
        percentage = int((current / total) * 100)
    
    # Simple text-based progress indicator
    bar_length = 30
    filled_length = int((percentage / 100) * bar_length)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"\r{prefix}: [{bar}] {percentage}% ({current}/{total})", end='', flush=True)
    
    if current == total:
        print()  # New line when complete


def print_error(message: str, exit_code: Optional[int] = None) -> None:
    """
    Print error message to stderr with consistent formatting.
    
    Args:
        message: Error message to display
        exit_code: Optional exit code to exit with
    """
    print(f"ERROR: {message}", file=sys.stderr)
    if exit_code is not None:
        sys.exit(exit_code)


def print_warning(message: str) -> None:
    """
    Print warning message with consistent formatting.
    
    Args:
        message: Warning message to display
    """
    print(f"WARNING: {message}")


def print_success(message: str) -> None:
    """
    Print success message with consistent formatting.
    
    Args:
        message: Success message to display
    """
    print(f"SUCCESS: {message}")


def print_info(message: str) -> None:
    """
    Print informational message with consistent formatting.
    
    Args:
        message: Information message to display
    """
    print(f"INFO: {message}")