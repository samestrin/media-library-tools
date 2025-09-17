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
from pathlib import Path

# Import dependencies from core module
try:
    from core import is_non_interactive, should_use_emojis
except ImportError:
    # Fallback for when core module is not available
    # This happens when modules are injected together during build
    def is_non_interactive():
        """Fallback implementation - will be overridden by injected core module"""
        return not sys.stdin.isatty()
    
    def should_use_emojis():
        """Fallback implementation - will be overridden by injected core module"""
        return sys.platform != "win32" and not is_non_interactive()


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


def format_status_message(
    message: str, emoji: str = "", fallback_prefix: str = ""
) -> str:
    """
    Format a status message with optional emoji or fallback prefix.

    Args:
        message: The message to format
        emoji: Emoji to use if emojis are supported
        fallback_prefix: Text prefix to use if emojis are not supported

    Returns:
        Formatted message string
    """
    if emoji and should_use_emojis():
        return f"{emoji} {message}"
    elif fallback_prefix:
        return f"{fallback_prefix}: {message}"
    else:
        return message


def display_item_list(items, title: str = None, numbered: bool = False, 
                     show_count: bool = True, indent: str = "  ") -> None:
    """
    Display a list of items with consistent formatting.
    
    Args:
        items: List of items to display (strings or objects with __str__)
        title: Optional title to display above the list
        numbered: Whether to number the items (default: False for bullet points)
        show_count: Whether to show total count in title (default: True)
        indent: Indentation string for list items (default: "  ")
    
    Example:
        display_item_list(['file1.mp4', 'file2.mkv'], 'Files to process', numbered=True)
        # Output:
        # Files to process (2):
        #   1. file1.mp4
        #   2. file2.mkv
    """
    if not items:
        if title:
            print(f"{title}: None found")
        return
    
    # Display title with optional count
    if title:
        count_text = f" ({len(items)})" if show_count else ""
        print(f"{title}{count_text}:")
    
    # Display items
    for i, item in enumerate(items, 1):
        if numbered:
            print(f"{indent}{i}. {item}")
        else:
            print(f"{indent}- {item}")


def display_summary_list(summary_data: dict, title: str = None) -> None:
    """
    Display a summary with categorized counts and totals.
    
    Args:
        summary_data: Dictionary with category names as keys and counts as values
        title: Optional title to display above the summary
    
    Example:
        display_summary_list({
            'Files processed': 15,
            'Files skipped': 3,
            'Errors encountered': 1
        }, 'Processing Summary')
        # Output:
        # Processing Summary:
        #   Files processed: 15
        #   Files skipped: 3
        #   Errors encountered: 1
    """
    if title:
        print(f"{title}:")
    
    # Find the longest key for alignment
    max_key_length = max(len(str(key)) for key in summary_data.keys()) if summary_data else 0
    
    for key, value in summary_data.items():
        print(f"  {str(key).ljust(max_key_length)}: {value}")


def display_progress_item(current: int, total: int, item_name: str, 
                         prefix: str = "Processing") -> None:
    """
    Display current progress for an item being processed.
    
    Args:
        current: Current item number (1-based)
        total: Total number of items
        item_name: Name of the current item being processed
        prefix: Prefix text (default: "Processing")
    
    Example:
        display_progress_item(3, 10, 'movie.mp4')
        # Output: [3/10] Processing: movie.mp4
    """
    print(f"[{current}/{total}] {prefix}: {item_name}")


def display_stats_table(stats: dict, title: str = None, 
                       value_formatter=None) -> None:
    """
    Display statistics in a formatted table with aligned columns.
    
    Args:
        stats: Dictionary with statistic names as keys and values
        title: Optional title to display above the table
        value_formatter: Optional function to format values (e.g., format_size for bytes)
    
    Example:
        display_stats_table({
            'Total files': 1250,
            'Total size': 15728640,
            'Average size': 12582
        }, 'File Statistics', format_size)
    """
    if not stats:
        return
    
    if title:
        print(f"\n{title}:")
    
    # Find the longest key for alignment
    max_key_length = max(len(str(key)) for key in stats.keys())
    
    for key, value in stats.items():
        formatted_value = value_formatter(value) if value_formatter else str(value)
        print(f"  {str(key).ljust(max_key_length)}: {formatted_value}")


def display_results_table(data: list, headers: list, title: str = None,
                         max_width: int = 80) -> None:
    """
    Display structured data in a formatted table with headers and proper alignment.
    
    Args:
        data: List of lists/tuples containing row data
        headers: List of column headers
        title: Optional title to display above the table
        max_width: Maximum width for the table (default: 80)
    
    Example:
        display_results_table([
            ['file1.mp4', '1.2 GB', 'Processed'],
            ['file2.mkv', '850 MB', 'Skipped']
        ], ['Filename', 'Size', 'Status'], 'Processing Results')
    """
    if not data or not headers:
        if title:
            print(f"{title}: No data to display")
        return
    
    if title:
        print(f"\n{title}:")
    
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        # Start with header width
        max_width_col = len(header)
        
        # Check data column widths
        for row in data:
            if i < len(row):
                max_width_col = max(max_width_col, len(str(row[i])))
        
        col_widths.append(min(max_width_col, max_width // len(headers)))
    
    # Print header
    header_row = "  " + " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
    print(header_row)
    print("  " + "-" * (len(header_row) - 2))
    
    # Print data rows
    for row in data:
        formatted_row = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell)
                if len(cell_str) > col_widths[i]:
                    cell_str = cell_str[:col_widths[i]-3] + "..."
                formatted_row.append(cell_str.ljust(col_widths[i]))
        
        print("  " + " | ".join(formatted_row))