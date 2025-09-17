#!/usr/bin/env python3
"""
User Interface Module for Media Library Tools
Version: 1.0

This module contains user interface functions including:
- Banner display and application branding
- Size formatting for human-readable output  
- User confirmation prompts

This is part of the modular library structure that enables selective inclusion
in built tools while maintaining the self-contained principle.
"""

import sys


def display_banner(
    script_name: str,
    version: str,
    description: str,
    no_banner_flag: bool = False,
    quiet_mode: bool = False,
) -> None:
    """
    Display standardized banner for media library tools.

    Args:
        script_name: Name of the script
        version: Version string
        description: Brief description of the script
        no_banner_flag: If True, suppress banner display
        quiet_mode: If True, suppress banner display
    """
    # Import here to avoid circular dependency
    from .core import is_non_interactive
    
    # Check suppression conditions (highest to lowest priority)
    if no_banner_flag or quiet_mode or is_non_interactive():
        return

    try:
        # Display standardized ASCII art
        print("┏┳┓┏━╸╺┳┓╻┏━┓╻  ╻┏┓ ┏━┓┏━┓┏━┓╻ ╻╺┳╸┏━┓┏━┓╻  ┏━┓")
        print("┃┃┃┣╸  ┃┃┃┣━┫┃  ┃┣┻┓┣┳┛┣━┫┣┳┛┗┳┛ ┃ ┃ ┃┃ ┃┃  ┗━┓")
        print("╹ ╹┗━╸╺┻┛╹╹ ╹┗━╸╹┗━┛╹┗╸╹ ╹╹┗╸ ╹  ╹ ┗━┛┗━┛┗━╸┗━┛")
        print(f"{script_name} v{version}: {description}")
        print()  # Blank line for separation
    except Exception:
        # Banner display errors should not prevent script execution
        pass


def format_size(size_bytes: int) -> str:
    """
    Format size in bytes to human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human readable size string
    """
    for unit in ["B", "K", "M", "G", "T"]:
        if size_bytes < 1024.0:
            if unit == "B":
                return f"{size_bytes:.0f}{unit}"
            else:
                return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}P"


def confirm_action(message: str, skip_confirmation: bool = False) -> bool:
    """
    Ask for user confirmation unless skipped.

    Args:
        message: Confirmation message to display
        skip_confirmation: If True, automatically confirm

    Returns:
        True if confirmed, False otherwise
    """
    if skip_confirmation:
        return True

    try:
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ["y", "yes"]
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        return False