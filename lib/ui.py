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
import time
import shutil
import os
from pathlib import Path
from typing import Optional, List, Dict, Set, Callable, Any
from dataclasses import dataclass

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


@dataclass
class ColumnConfig:
    """
    Configuration for table column rendering.

    Attributes:
        align: Column alignment ('left', 'right', 'center')
        formatter: Optional function to format cell values
        max_width: Maximum width for this column (None for auto)
    """
    align: str = 'left'
    formatter: Optional[Callable[[Any], str]] = None
    max_width: Optional[int] = None


def display_results_table(data: list, headers: list, title: str = None,
                         max_width: int = 80, column_config: Optional[List[ColumnConfig]] = None,
                         sort_by: Optional[int] = None, reverse: bool = False,
                         show_totals: bool = False, border_style: str = 'ascii') -> None:
    """
    Display structured data in a formatted table with advanced configuration.

    Features:
    - Column alignment control (left, right, center)
    - Automatic width calculation based on content
    - Row sorting by column
    - Column-specific formatters (size, date, percentage)
    - Footer rows for totals/summaries
    - Maximum width enforcement with truncation
    - Border style options (ASCII, Unicode, minimal)

    Args:
        data: List of lists/tuples containing row data
        headers: List of column headers
        title: Optional title to display above the table
        max_width: Maximum width for the table (default: 80)
        column_config: Optional list of ColumnConfig objects for each column
        sort_by: Optional column index to sort by
        reverse: Reverse sort order (default: False)
        show_totals: Show totals row for numeric columns (default: False)
        border_style: Border style ('ascii', 'unicode', 'minimal')

    Example:
        from lib.ui import display_results_table, ColumnConfig

        display_results_table([
            ['file1.mp4', 1234567890, 'Processed'],
            ['file2.mkv', 987654321, 'Skipped']
        ], ['Filename', 'Size', 'Status'],
        column_config=[
            ColumnConfig(align='left'),
            ColumnConfig(align='right', formatter=format_size),
            ColumnConfig(align='center')
        ],
        sort_by=1, reverse=True, border_style='unicode')
    """
    if not data or not headers:
        if title:
            print(f"{title}: No data to display")
        return

    # Default column config if not provided
    if column_config is None:
        column_config = [ColumnConfig() for _ in headers]
    elif len(column_config) < len(headers):
        # Extend with defaults if needed
        column_config = list(column_config) + [ColumnConfig() for _ in range(len(headers) - len(column_config))]

    # Sort data if requested
    if sort_by is not None and 0 <= sort_by < len(headers):
        data = sorted(data, key=lambda row: row[sort_by] if sort_by < len(row) else '', reverse=reverse)

    # Apply formatters to data
    formatted_data = []
    for row in data:
        formatted_row = []
        for i, cell in enumerate(row):
            if i < len(column_config) and column_config[i].formatter:
                formatted_row.append(column_config[i].formatter(cell))
            else:
                formatted_row.append(str(cell))
        formatted_data.append(formatted_row)

    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        # Start with header width
        max_col_width = len(header)

        # Check data column widths
        for row in formatted_data:
            if i < len(row):
                max_col_width = max(max_col_width, len(row[i]))

        # Apply column-specific max width if set
        if i < len(column_config) and column_config[i].max_width:
            max_col_width = min(max_col_width, column_config[i].max_width)
        else:
            # Apply global max width
            max_col_width = min(max_col_width, max_width // len(headers))

        col_widths.append(max_col_width)

    # Choose border characters
    if border_style == 'unicode':
        sep = " │ "
        top_left, top_mid, top_right = "┌", "┬", "┐"
        mid_left, mid_mid, mid_right = "├", "┼", "┤"
        bot_left, bot_mid, bot_right = "└", "┴", "┘"
        horiz = "─"
    elif border_style == 'minimal':
        sep = "  "
        top_left = top_mid = top_right = ""
        mid_left = mid_mid = mid_right = ""
        bot_left = bot_mid = bot_right = ""
        horiz = " "
    else:  # ascii
        sep = " | "
        top_left = top_mid = top_right = ""
        mid_left = mid_mid = mid_right = ""
        bot_left = bot_mid = bot_right = ""
        horiz = "-"

    def align_cell(cell: str, width: int, alignment: str) -> str:
        """Align cell content according to specified alignment."""
        if len(cell) > width:
            cell = cell[:width-3] + "..."
        if alignment == 'right':
            return cell.rjust(width)
        elif alignment == 'center':
            return cell.center(width)
        else:  # left
            return cell.ljust(width)

    # Display title
    if title:
        print(f"\n{title}:")

    # Build and print header
    header_cells = []
    for i, header in enumerate(headers):
        alignment = column_config[i].align if i < len(column_config) else 'left'
        header_cells.append(align_cell(header, col_widths[i], alignment))

    header_row = "  " + sep.join(header_cells)
    print(header_row)

    # Print separator
    if border_style == 'unicode':
        separator = "  " + mid_left + horiz * col_widths[0]
        for i in range(1, len(col_widths)):
            separator += mid_mid + horiz * col_widths[i]
        separator += mid_right
        print(separator)
    else:
        print("  " + horiz * (len(header_row) - 2))

    # Print data rows
    for row in formatted_data:
        row_cells = []
        for i in range(len(headers)):
            cell = row[i] if i < len(row) else ""
            alignment = column_config[i].align if i < len(column_config) else 'left'
            row_cells.append(align_cell(cell, col_widths[i], alignment))

        print("  " + sep.join(row_cells))

    # Show totals if requested
    if show_totals and data:
        # Calculate totals for numeric columns
        totals = []
        has_total = False
        for i in range(len(headers)):
            try:
                # Try to sum numeric values from original data (before formatting)
                col_values = [row[i] for row in data if i < len(row) and isinstance(row[i], (int, float))]
                if col_values:
                    total = sum(col_values)
                    # Apply formatter if available
                    if i < len(column_config) and column_config[i].formatter:
                        totals.append(column_config[i].formatter(total))
                    else:
                        totals.append(str(total))
                    has_total = True
                else:
                    totals.append("")
            except (TypeError, ValueError):
                totals.append("")

        if has_total:
            # Print separator before totals
            if border_style != 'minimal':
                print("  " + horiz * (len(header_row) - 2))

            # Print totals row
            total_cells = []
            for i in range(len(headers)):
                if i == 0 and not totals[0]:
                    cell = "TOTAL"
                else:
                    cell = totals[i] if i < len(totals) else ""
                alignment = column_config[i].align if i < len(column_config) else 'left'
                total_cells.append(align_cell(cell, col_widths[i], alignment))

            print("  " + sep.join(total_cells))

    print()  # Blank line after table


class ProgressBar:
    """
    Real-time progress bar with ETA calculation and rate display.

    Features:
    - Configurable width and style
    - ETA calculation based on current rate
    - Dynamic updates without line spam
    - Rate display (items/sec, MB/sec)
    - Memory-efficient for large operations
    - TTY detection with fallback for non-interactive environments

    Usage:
        with ProgressBar(total=1000, desc="Processing files") as pb:
            for item in items:
                process_item(item)
                pb.update(1)
    """

    def __init__(self, total: int, desc: str = "", width: int = 50,
                 unit: str = "items", show_rate: bool = True):
        """
        Initialize progress bar.

        Args:
            total: Total number of items to process
            desc: Description to display before progress bar
            width: Width of progress bar in characters (default: 50)
            unit: Unit name for rate display (default: "items")
            show_rate: Whether to show processing rate (default: True)
        """
        self.total = total
        self.desc = desc
        self.width = width
        self.unit = unit
        self.show_rate = show_rate
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_print_length = 0
        self.is_tty = sys.stdout.isatty() and not is_non_interactive()
        self.update_interval = 0.1  # Update display every 0.1 seconds minimum
        self.completed = False

    def update(self, increment: int = 1) -> None:
        """
        Update progress by specified increment.

        Args:
            increment: Number of items to add to progress (default: 1)
        """
        self.current = min(self.current + increment, self.total)
        current_time = time.time()

        # Only update display if enough time has passed or we're complete
        if (current_time - self.last_update_time >= self.update_interval or
            self.current >= self.total):
            self._display()
            self.last_update_time = current_time

    def _display(self) -> None:
        """Display current progress state."""
        if self.total == 0:
            return

        # Calculate metrics
        elapsed = time.time() - self.start_time
        percentage = (self.current / self.total) * 100

        # Build progress bar
        if self.is_tty:
            filled = int(self.width * self.current / self.total)
            bar = "█" * filled + "░" * (self.width - filled)

            # Calculate ETA
            if self.current > 0 and elapsed > 0:
                rate = self.current / elapsed
                remaining = self.total - self.current
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_str = self._format_time(eta_seconds)

                # Build status line
                status_parts = [
                    f"{self.desc}: " if self.desc else "",
                    f"[{bar}] ",
                    f"{self.current}/{self.total} ",
                    f"({percentage:.1f}%)"
                ]

                if self.show_rate and rate > 0:
                    status_parts.append(f" - {rate:.1f} {self.unit}/sec")

                if self.current < self.total:
                    status_parts.append(f" - ETA: {eta_str}")
                else:
                    status_parts.append(" - Complete")

                status = "".join(status_parts)
            else:
                status = f"{self.desc}: [{bar}] {self.current}/{self.total} ({percentage:.1f}%)"

            # Clear previous line and print new status
            print(f"\r{' ' * self.last_print_length}\r{status}", end="", flush=True)
            self.last_print_length = len(status)

            # Print newline when complete
            if self.current >= self.total and not self.completed:
                print()
                self.completed = True
        else:
            # Non-TTY mode: only print at milestones (0%, 25%, 50%, 75%, 100%)
            milestones = [0, 25, 50, 75, 100]
            current_milestone = int(percentage / 25) * 25

            if not hasattr(self, '_last_milestone'):
                self._last_milestone = -1

            if current_milestone > self._last_milestone and current_milestone in milestones:
                prefix = f"{self.desc}: " if self.desc else ""
                print(f"{prefix}Progress: {self.current}/{self.total} ({percentage:.1f}%)")
                self._last_milestone = current_milestone

    def _format_time(self, seconds: float) -> str:
        """
        Format seconds into human-readable time string.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string (e.g., "2m 30s")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit - ensure final display."""
        if not self.completed:
            self.current = self.total
            self._display()
            if self.is_tty:
                print()


class PhaseProgressTracker:
    """
    Multi-phase operation tracking with individual progress bars.

    Features:
    - Track multiple named phases (e.g., Consolidation, Organization, Archive)
    - Per-phase progress with individual progress bars
    - Overall completion percentage
    - Phase timing and duration display
    - Phase status tracking (pending, in-progress, completed, failed)

    Usage:
        tracker = PhaseProgressTracker([
            "Phase 1: Consolidation",
            "Phase 2: Organization",
            "Phase 3: Archive"
        ])

        tracker.start_phase(0, total_items=500)
        # ... process items ...
        tracker.update_phase(0, increment=1)
        tracker.complete_phase(0)

        tracker.display_summary()
    """

    def __init__(self, phase_names: List[str]):
        """
        Initialize phase progress tracker.

        Args:
            phase_names: List of phase names in order
        """
        self.phase_names = phase_names
        self.phases: Dict[int, Dict] = {}
        self.current_phase_index: Optional[int] = None
        self.is_tty = sys.stdout.isatty() and not is_non_interactive()

        # Initialize phase data
        for i in range(len(phase_names)):
            self.phases[i] = {
                'name': phase_names[i],
                'status': 'pending',  # pending, in-progress, completed, failed
                'total': 0,
                'current': 0,
                'start_time': None,
                'end_time': None,
                'progress_bar': None
            }

    def start_phase(self, phase_index: int, total_items: int = 0) -> None:
        """
        Start a specific phase.

        Args:
            phase_index: Index of the phase to start (0-based)
            total_items: Total number of items for this phase
        """
        if phase_index not in self.phases:
            return

        self.current_phase_index = phase_index
        phase = self.phases[phase_index]
        phase['status'] = 'in-progress'
        phase['total'] = total_items
        phase['current'] = 0
        phase['start_time'] = time.time()

        # Display phase start
        print(f"\n{phase['name']}")
        if total_items > 0:
            phase['progress_bar'] = ProgressBar(
                total=total_items,
                desc="  Progress",
                width=40,
                unit="items"
            )

    def update_phase(self, phase_index: int, increment: int = 1) -> None:
        """
        Update progress for a specific phase.

        Args:
            phase_index: Index of the phase to update
            increment: Number of items to add to progress
        """
        if phase_index not in self.phases:
            return

        phase = self.phases[phase_index]
        if phase['status'] != 'in-progress':
            return

        phase['current'] = min(phase['current'] + increment, phase['total'])

        if phase['progress_bar']:
            phase['progress_bar'].update(increment)

    def complete_phase(self, phase_index: int, status: str = 'completed') -> None:
        """
        Mark a phase as complete.

        Args:
            phase_index: Index of the phase to complete
            status: Final status ('completed' or 'failed')
        """
        if phase_index not in self.phases:
            return

        phase = self.phases[phase_index]
        phase['status'] = status
        phase['end_time'] = time.time()

        # Ensure progress bar is complete
        if phase['progress_bar'] and phase['current'] < phase['total']:
            phase['progress_bar'].current = phase['total']
            phase['progress_bar']._display()
            if phase['progress_bar'].is_tty:
                print()

        # Display phase completion
        if phase['start_time']:
            duration = phase['end_time'] - phase['start_time']
            duration_str = self._format_duration(duration)
            status_text = "Complete" if status == 'completed' else "FAILED"
            print(f"  {status_text} - Duration: {duration_str}\n")

    def fail_phase(self, phase_index: int, error_message: str = "") -> None:
        """
        Mark a phase as failed.

        Args:
            phase_index: Index of the phase that failed
            error_message: Optional error message to display
        """
        if error_message:
            print(f"  Error: {error_message}")
        self.complete_phase(phase_index, status='failed')

    def display_summary(self) -> None:
        """Display summary of all phases."""
        print("\n" + "=" * 60)
        print("PHASE SUMMARY")
        print("=" * 60)

        total_duration = 0
        for i in range(len(self.phase_names)):
            phase = self.phases[i]
            status_symbol = {
                'pending': '[ ]',
                'in-progress': '[~]',
                'completed': '[✓]' if not is_non_interactive() else '[x]',
                'failed': '[✗]' if not is_non_interactive() else '[!]'
            }.get(phase['status'], '[ ]')

            duration_str = ""
            if phase['start_time'] and phase['end_time']:
                duration = phase['end_time'] - phase['start_time']
                duration_str = f" - {self._format_duration(duration)}"
                total_duration += duration

            progress_str = ""
            if phase['total'] > 0:
                progress_str = f" ({phase['current']}/{phase['total']} items)"

            print(f"{status_symbol} {phase['name']}{progress_str}{duration_str}")

        if total_duration > 0:
            print(f"\nTotal Duration: {self._format_duration(total_duration)}")
        print("=" * 60 + "\n")

    def get_overall_progress(self) -> float:
        """
        Get overall progress percentage across all phases.

        Returns:
            Overall progress percentage (0-100)
        """
        completed_phases = sum(1 for p in self.phases.values() if p['status'] == 'completed')
        return (completed_phases / len(self.phase_names)) * 100 if self.phase_names else 0

    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable string.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if seconds < 1:
            return f"{int(seconds * 1000)}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"


def display_directory_tree(root_path: str, max_depth: int = 3,
                          show_sizes: bool = True,
                          highlight_patterns: Optional[List[str]] = None,
                          use_unicode: Optional[bool] = None) -> None:
    """
    Display directory structure as a tree with optional size information.

    Features:
    - Configurable depth limit
    - File size display
    - Path highlighting for specific patterns
    - Unicode or ASCII symbols
    - Efficient traversal with depth limiting

    Args:
        root_path: Root directory to visualize
        max_depth: Maximum depth to traverse (default: 3)
        show_sizes: Whether to show file/directory sizes (default: True)
        highlight_patterns: List of patterns to highlight (e.g., ["Season *"])
        use_unicode: Use Unicode symbols (default: auto-detect based on platform)

    Example:
        display_directory_tree("/media/TV Shows/Show Name", max_depth=3,
                             highlight_patterns=["Season *"])
    """
    root = Path(root_path)
    if not root.exists():
        print(f"Error: Path does not exist: {root_path}")
        return

    # Auto-detect unicode support
    if use_unicode is None:
        use_unicode = sys.platform != "win32" and not is_non_interactive()

    # Tree symbols
    if use_unicode:
        PIPE = "│   "
        TEE = "├── "
        ELBOW = "└── "
        BLANK = "    "
    else:
        PIPE = "|   "
        TEE = "|-- "
        ELBOW = "`-- "
        BLANK = "    "

    # Compile highlight patterns if provided
    highlight_set: Set[str] = set()
    if highlight_patterns:
        for pattern in highlight_patterns:
            highlight_set.add(pattern.lower())

    # Track statistics
    total_size = 0
    file_count = 0
    dir_count = 0

    def should_highlight(path: Path) -> bool:
        """Check if path matches any highlight patterns."""
        if not highlight_patterns:
            return False
        path_str = path.name.lower()
        for pattern in highlight_patterns:
            pattern_lower = pattern.lower().replace("*", "")
            if pattern_lower in path_str:
                return True
        return False

    def get_size(path: Path) -> int:
        """Get size of file or directory."""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                # For directories, sum all file sizes
                total = 0
                try:
                    for item in path.rglob('*'):
                        if item.is_file():
                            try:
                                total += item.stat().st_size
                            except (OSError, PermissionError):
                                pass
                except (OSError, PermissionError):
                    pass
                return total
        except (OSError, PermissionError):
            return 0
        return 0

    def format_entry(path: Path, is_last: bool, prefix: str, depth: int) -> str:
        """Format a single tree entry."""
        nonlocal total_size, file_count, dir_count

        # Choose connector
        connector = ELBOW if is_last else TEE

        # Get name and size
        name = path.name
        if path.is_dir():
            name += "/"
            dir_count += 1
        else:
            file_count += 1

        # Check for highlighting
        highlighted = should_highlight(path)
        if highlighted and use_unicode:
            name = f"→ {name}"

        # Add size if requested
        size_str = ""
        if show_sizes:
            size = get_size(path)
            total_size += size
            if size > 0:
                size_str = f" ({format_size(size)})"

        return f"{prefix}{connector}{name}{size_str}"

    def walk_tree(path: Path, prefix: str = "", depth: int = 0):
        """Recursively walk directory tree."""
        if depth > max_depth:
            return

        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            print(f"{prefix}{TEE}[Permission Denied]")
            return
        except OSError as e:
            print(f"{prefix}{TEE}[Error: {e}]")
            return

        # Filter out hidden files for cleaner display
        entries = [e for e in entries if not e.name.startswith('.')]

        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)

            # Print entry
            print(format_entry(entry, is_last, prefix, depth))

            # Recurse into directories
            if entry.is_dir() and depth < max_depth:
                extension = BLANK if is_last else PIPE
                walk_tree(entry, prefix + extension, depth + 1)

    # Display root
    print(f"\n{root}/")

    # Walk tree
    walk_tree(root, "", 0)

    # Display summary
    if show_sizes and (file_count > 0 or dir_count > 0):
        print(f"\nTotal: {format_size(total_size)} across {file_count} files in {dir_count} directories")
    print()