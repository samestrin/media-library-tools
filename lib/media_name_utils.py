#!/usr/bin/env python3
"""
Media Name Utilities Module for Media Library Tools
Version: 1.0

Provides utilities for parsing and cleaning media file/directory names.

Features:
- Year extraction from various naming patterns
- Show name cleaning for API searches
- Validation of extracted year values
- Support for multiple year format patterns
- Configurable year validation ranges

This module provides shared media name parsing functionality for tools that need
to extract metadata from file and directory names across media library tools.
"""

import re
from typing import Optional, Tuple, List


class MediaNameParser:
    """Parser for extracting metadata from media file and directory names."""

    # Standard year patterns used in media naming conventions
    DEFAULT_YEAR_PATTERNS = [
        (r'\((\d{4})\)', 'Parentheses format (YYYY)'),
        (r'\[(\d{4})\]', 'Brackets format [YYYY]'),
        (r'\.(\d{4})\.', 'Dot separated .YYYY.'),
        (r'\s(\d{4})\s', 'Space separated YYYY'),
        (r'-(\d{4})-', 'Dash separated -YYYY-'),
        (r'_(\d{4})_', 'Underscore separated _YYYY_'),
        (r'\.(\d{4})$', 'Dot ending .YYYY'),
        (r'\s(\d{4})$', 'Space ending YYYY'),
        (r'-(\d{4})$', 'Dash ending -YYYY'),
        (r'_(\d{4})$', 'Underscore ending _YYYY'),
        (r'^(\d{4})\.', 'Dot beginning YYYY.'),
        (r'^(\d{4})\s', 'Space beginning YYYY '),
        (r'^(\d{4})-', 'Dash beginning YYYY-'),
        (r'^(\d{4})_', 'Underscore beginning YYYY_'),
        (r'\b(\d{4})\b', 'Standalone year YYYY'),
    ]

    def __init__(self, year_patterns: Optional[List[Tuple[str, str]]] = None,
                 min_year: int = 1900, max_year: int = 2030, debug: bool = False):
        """
        Initialize media name parser with configurable patterns and validation.

        Args:
            year_patterns: List of (regex_pattern, description) tuples for year extraction
                         If None, uses DEFAULT_YEAR_PATTERNS
            min_year: Minimum valid year (default: 1900)
            max_year: Maximum valid year (default: 2030)
            debug: Enable debug output
        """
        self.year_patterns = year_patterns if year_patterns is not None else self.DEFAULT_YEAR_PATTERNS
        self.min_year = min_year
        self.max_year = max_year
        self.debug = debug

    def extract_year(self, name: str) -> Optional[int]:
        """
        Extract year from media name using configured regex patterns.

        Tries each pattern in order and returns the first valid year found.
        Validates that extracted year is within configured min/max range.

        Args:
            name: Media file or directory name

        Returns:
            Extracted year as integer, or None if no valid year found

        Example:
            >>> parser = MediaNameParser()
            >>> parser.extract_year("Breaking Bad (2008)")
            2008
            >>> parser.extract_year("The Wire [2002]")
            2002
            >>> parser.extract_year("Show Name")
            None
        """
        for pattern, description in self.year_patterns:
            match = re.search(pattern, name)
            if match:
                year = int(match.group(1))
                if self.min_year <= year <= self.max_year:
                    if self.debug:
                        print(f"DEBUG: Extracted year {year} using {description}")
                    return year
                elif self.debug:
                    print(f"DEBUG: Year {year} out of range ({self.min_year}-{self.max_year})")
        return None

    def clean_show_name(self, name: str) -> str:
        """
        Clean show name for API search by removing year and common patterns.

        Removes year information and cleans up punctuation to produce a name
        suitable for searching in media databases like TVDB.

        Args:
            name: Original directory or file name

        Returns:
            Cleaned show name suitable for API searching

        Example:
            >>> parser = MediaNameParser()
            >>> parser.clean_show_name("Breaking Bad (2008)")
            'Breaking Bad'
            >>> parser.clean_show_name("The.Wire.[2002]")
            'The Wire'
            >>> parser.clean_show_name("Show Name - 2010 - Season 1")
            'Show Name  Season 1'
        """
        # Remove year patterns
        cleaned = name
        for pattern, _ in self.year_patterns:
            cleaned = re.sub(pattern, '', cleaned)

        # Clean up extra spaces and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'[._-]+$', '', cleaned)  # Remove trailing punctuation
        cleaned = re.sub(r'^[._-]+', '', cleaned)  # Remove leading punctuation

        return cleaned

    def needs_year_update(self, current_name: str, correct_year: int) -> Tuple[bool, Optional[int]]:
        """
        Check if a media name needs year update.

        Compares the year in the current name (if any) with the correct year
        to determine if an update is needed.

        Args:
            current_name: Current directory or file name
            correct_year: The correct year from authoritative source (e.g., TVDB)

        Returns:
            Tuple of (needs_update, current_year):
            - needs_update: True if name should be updated with year
            - current_year: Year currently in the name, or None if no year present

        Example:
            >>> parser = MediaNameParser()
            >>> parser.needs_year_update("Breaking Bad", 2008)
            (True, None)
            >>> parser.needs_year_update("Breaking Bad (2007)", 2008)
            (True, 2007)
            >>> parser.needs_year_update("Breaking Bad (2008)", 2008)
            (False, 2008)
        """
        current_year = self.extract_year(current_name)

        if current_year is None:
            # No year in current name, needs update
            return True, None

        if current_year != correct_year:
            # Wrong year, needs update
            return True, current_year

        # Correct year already present
        return False, current_year

    def format_name_with_year(self, base_name: str, year: int,
                             format_style: str = 'parentheses') -> str:
        """
        Format a media name with year in the specified style.

        Args:
            base_name: Base name without year
            year: Year to add
            format_style: Style for year formatting:
                        'parentheses' -> "Name (YYYY)"
                        'brackets' -> "Name [YYYY]"
                        'space' -> "Name YYYY"
                        'dash' -> "Name - YYYY"

        Returns:
            Formatted name with year

        Example:
            >>> parser = MediaNameParser()
            >>> parser.format_name_with_year("Breaking Bad", 2008)
            'Breaking Bad (2008)'
            >>> parser.format_name_with_year("Breaking Bad", 2008, 'brackets')
            'Breaking Bad [2008]'
        """
        base_name = base_name.strip()

        if format_style == 'parentheses':
            return f"{base_name} ({year})"
        elif format_style == 'brackets':
            return f"{base_name} [{year}]"
        elif format_style == 'space':
            return f"{base_name} {year}"
        elif format_style == 'dash':
            return f"{base_name} - {year}"
        else:
            # Default to parentheses
            return f"{base_name} ({year})"
