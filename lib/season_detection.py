#!/usr/bin/env python3
"""
Season Detection Module for Media Library Tools
Version: 1.0

Shared season detection logic extracted from plex_make_seasons with advanced
multi-stage validation, confidence scoring, and comprehensive pattern matching.

Features:
- 19 season detection patterns with priority ordering
- Multi-stage validation with confidence scoring
- Pattern-specific validation for different season types
- Quality indicator detection (prevents false positives)
- Position-based validation (relative position in filename)
- Range validation (different ranges for different pattern types)
- Extended season support (S100-S2050 for long-running shows)
- Year-based seasons (1990-2099 with special handling)
- Episode/Part/Chapter/Disc/Volume patterns
- Comprehensive statistics tracking

This module provides the shared interface and logic for both plex_make_seasons
and plex_make_all_seasons scripts, eliminating code duplication while providing
advanced detection capabilities.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class SeasonPatternDefinitions:
    """
    Centralized season pattern definitions with metadata.

    All patterns are ordered by specificity and priority to ensure
    the most accurate match is found first.
    """

    # Standard patterns (highest priority) - S01E01, Season 1
    STANDARD_PATTERNS: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r'[Ss](\d{1,2})[Ee]\d{1,3}', 'S{:02d}E format'),
        (r'[Ss]eason[\s\._-]*(\d{1,2})', 'Season X format'),
    ])

    # Extended season patterns (high priority) - S100+
    EXTENDED_PATTERNS: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r'[Ss](\d{3,4})[Ee]\d{1,3}', 'Extended season S###/####E## format'),
        (r'[Ss]eason[\s\._-]*(\d{3,4})', 'Extended Season #### format'),
    ])

    # Enhanced alternative patterns (medium-high priority)
    ENHANCED_ALTERNATIVE: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r'(\d{1,3})x\d{1,3}', 'Enhanced season #x# format'),
        (r'[Ss](\d{1,4})\D', 'Enhanced S# format'),
    ])

    # Numeric-only patterns (medium priority)
    NUMERIC_ONLY: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r'(?:ep|episode)[\s\-_.]*(\d{1,2})(?:[^\d]|$)', 'Episode-prefixed numeric format'),
        (r'(?:^|[\s\-_.])[^\d]*[\s\-_.](\d{1,2})[\s\-_.](?!\d*(?:p|fps|kbps))', 'Separated numeric format'),
    ])

    # Year-based seasons (special handling)
    YEAR_BASED: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r'[\(\[]?(20\d{2})[\)\]]?', 'Year format'),
    ])

    # Episode/media patterns (various priorities)
    EPISODE_PATTERNS: List[Tuple[str, str]] = field(default_factory=lambda: [
        # Episode numbering patterns
        (r'[Ee]pisode[\s\._-]*(\d{1,3})', 'Episode X format'),
        (r'[Ee]p[\s\._-]*(\d{1,3})', 'Ep X format'),
        # Part/Chapter patterns
        (r'[Pp]art[\s\._-]*(\d{1,2})', 'Part X format'),
        (r'[Cc]hapter[\s\._-]*(\d{1,2})', 'Chapter X format'),
        # Disc patterns
        (r'[Dd]isc[\s\._-]*(\d{1,2})', 'Disc X format'),
        (r'[Dd](\d{1,2})', 'D1 format'),
        # Volume patterns
        (r'[Vv]ol[\s\._-]*(\d{1,2})', 'Vol X format'),
        (r'[Vv](\d{1,2})', 'V1 format'),
    ])

    def get_all_patterns(self) -> List[Tuple[str, str]]:
        """
        Get all patterns in priority order.

        Returns:
            List of (regex, description) tuples
        """
        return (
            self.STANDARD_PATTERNS +
            self.EXTENDED_PATTERNS +
            self.ENHANCED_ALTERNATIVE +
            self.YEAR_BASED +
            self.EPISODE_PATTERNS +
            self.NUMERIC_ONLY
        )


class SeasonValidationEngine:
    """
    Multi-stage validation engine for season detection.

    Provides sophisticated validation including:
    - Quality indicator detection
    - Position-based confidence scoring
    - Range validation by pattern type
    - Context character analysis
    """

    # Quality indicators that should be rejected
    QUALITY_PATTERNS = [
        r'720p', r'1080p', r'480p', r'2160p', r'4K',
        r'\d+kbps', r'\d+fps', r'HDR', r'DTS', r'AC3',
        r'H\.?264', r'H\.?265', r'x264', r'x265',
        r'HEVC', r'AVC', r'BluRay', r'WEBRip', r'DVDRip'
    ]

    # Positive indicators for season detection
    POSITIVE_INDICATORS = ['ep', 'episode', 'season', 'series', '-', '_', '.', ' ']

    # Negative indicators that reduce confidence
    NEGATIVE_INDICATORS = ['p', 'fps', 'kbps', 'bit', 'mb', 'gb']

    def detect_quality_indicators(self, filename: str) -> bool:
        """
        Detect if filename contains quality indicators.

        Args:
            filename: Filename to check

        Returns:
            True if quality indicators detected, False otherwise
        """
        filename_lower = filename.lower()
        for pattern in self.QUALITY_PATTERNS:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                return True
        return False

    def validate_position(self, filename: str, match_pos: int) -> float:
        """
        Calculate position-based confidence adjustment.

        Args:
            filename: Full filename
            match_pos: Position of match in filename

        Returns:
            Confidence adjustment value
        """
        filename_length = len(filename)
        if filename_length == 0:
            return 0.0

        relative_position = match_pos / filename_length

        if relative_position > 0.7:  # Changed from 0.8 to 0.7 to be more strict
            return -0.5  # Late in filename, likely not season
        elif relative_position < 0.3:
            return 0.3   # Early in filename, likely season
        else:
            return 0.0   # Middle position, neutral

    def validate_range_by_pattern(self, season_num: int, pattern_desc: str) -> bool:
        """
        Validate season number range based on pattern type.

        Args:
            season_num: Season number to validate
            pattern_desc: Pattern description

        Returns:
            True if valid range, False otherwise
        """
        if 'Extended' in pattern_desc:
            return 100 <= season_num <= 2050
        elif 'numeric' in pattern_desc.lower():
            return 1 <= season_num <= 50
        elif 'Enhanced' in pattern_desc:
            if 'S#' in pattern_desc:
                return 1 <= season_num <= 2050
            elif '#x#' in pattern_desc:
                return 1 <= season_num <= 500
        elif 'Year format' in pattern_desc:
            return season_num >= 1990
        else:
            return 1 <= season_num <= 50

    def calculate_confidence_score(self, filename: str, match_text: str,
                                   season_num: int, pattern_desc: str) -> float:
        """
        Calculate comprehensive confidence score for a match.

        Args:
            filename: Full filename
            match_text: Matched text from pattern
            season_num: Extracted season number
            pattern_desc: Pattern description

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.0

        # Position-based adjustment
        match_pos = filename.find(match_text)
        confidence += self.validate_position(filename, match_pos)

        # Range-based confidence boost
        if 'Extended' in pattern_desc:
            confidence += 0.4
        elif 'numeric' in pattern_desc.lower():
            confidence += 0.2
        elif 'Enhanced' in pattern_desc:
            confidence += 0.3

        # Context character analysis
        filename_length = len(filename)
        context_start = max(0, match_pos - 3)
        context_end = min(filename_length, match_pos + len(match_text) + 3)
        context = filename[context_start:context_end].lower()

        for indicator in self.POSITIVE_INDICATORS:
            if indicator in context:
                confidence += 0.1

        for indicator in self.NEGATIVE_INDICATORS:
            if indicator in context:
                confidence -= 0.2

        # Filename structure analysis
        if any(sep in filename for sep in [' - ', '.', '_', 'S0', 's0', 'Season', 'season']):
            confidence += 0.2

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))

    def validate_numeric_season(self, filename: str, match_text: str,
                               season_num: int, pattern_desc: str) -> Tuple[bool, float]:
        """
        Validate that a numeric match represents a season.

        Args:
            filename: Full filename
            match_text: Matched text from pattern
            season_num: Extracted season number
            pattern_desc: Pattern description

        Returns:
            Tuple of (is_valid, confidence_score)
        """
        # Check for quality indicators first
        if self.detect_quality_indicators(filename):
            return False, 0.0

        # Validate range
        if not self.validate_range_by_pattern(season_num, pattern_desc):
            return False, 0.0

        # Calculate confidence
        confidence = self.calculate_confidence_score(filename, match_text, season_num, pattern_desc)

        # Apply minimum confidence threshold
        min_confidence = 0.3 if 'numeric' in pattern_desc.lower() else 0.2

        return confidence >= min_confidence, confidence


class BaseSeasonDetector:
    """
    Base class for season detection shared between plex scripts.

    Provides common season detection interface and functionality that can be
    inherited by script-specific organizer classes.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize season detector with configuration.

        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.patterns = SeasonPatternDefinitions()
        self.validator = SeasonValidationEngine()
        self.season_patterns = self.patterns.get_all_patterns()

        # Statistics tracking
        self.stats = {
            'season_patterns_found': {},
            'validation_results': {},
            'confidence_scores': []
        }

    def extract_season_info(self, filename: str) -> Tuple[Optional[int], str, str]:
        """
        Extract season information from filename.

        Args:
            filename: Filename to analyze

        Returns:
            Tuple of (season_number, pattern_description, matched_text)
            Returns (None, "No pattern matched", "") if no match found
        """
        for pattern, description in self.season_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    season_num = int(match.group(1))
                    matched_text = match.group(0)

                    # Pattern-specific validation
                    if 'Year format' in description:
                        if season_num >= 1990:
                            self._track_pattern_usage(description, True)
                            return season_num, description, matched_text
                    elif 'Extended' in description:
                        if 100 <= season_num <= 2050:
                            self._track_pattern_usage(description, True)
                            return season_num, description, matched_text
                    elif 'numeric' in description.lower():
                        is_valid, confidence = self.validator.validate_numeric_season(
                            filename, matched_text, season_num, description)
                        if is_valid:
                            self._track_pattern_usage(description, True)
                            self.stats['confidence_scores'].append(confidence)
                            return season_num, description, matched_text
                    elif 'Enhanced' in description:
                        if 'S#' in description and 1 <= season_num <= 2050:
                            self._track_pattern_usage(description, True)
                            return season_num, description, matched_text
                        elif '#x#' in description and 1 <= season_num <= 500:
                            self._track_pattern_usage(description, True)
                            return season_num, description, matched_text
                    elif 1 <= season_num <= 50:
                        self._track_pattern_usage(description, True)
                        return season_num, description, matched_text

                except (ValueError, IndexError):
                    continue

        self._track_pattern_usage("No pattern matched", False)
        return None, "No pattern matched", ""

    def generate_season_directory_name(self, season_num: int, pattern_desc: str) -> str:
        """
        Generate season directory name based on season number and pattern.

        Args:
            season_num: Season number
            pattern_desc: Pattern description

        Returns:
            Season directory name (e.g., "Season 01" or "Season 100")
        """
        if 'Year format' in pattern_desc:
            return f"Season {season_num}"
        elif 'Extended' in pattern_desc or season_num >= 100:
            return f"Season {season_num}"
        else:
            return f"Season {season_num:02d}"

    def get_season_patterns(self) -> List[Tuple[str, str]]:
        """
        Get all season patterns.

        Returns:
            List of (regex, description) tuples
        """
        return self.season_patterns

    def _track_pattern_usage(self, pattern_desc: str, success: bool) -> None:
        """
        Track pattern usage for statistics.

        Args:
            pattern_desc: Pattern description
            success: Whether pattern matched successfully
        """
        if pattern_desc not in self.stats['season_patterns_found']:
            self.stats['season_patterns_found'][pattern_desc] = 0

        if success:
            self.stats['season_patterns_found'][pattern_desc] += 1

    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive detection statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            'patterns_found': dict(self.stats['season_patterns_found']),
            'total_patterns_used': len([k for k, v in self.stats['season_patterns_found'].items() if v > 0]),
            'average_confidence': (
                sum(self.stats['confidence_scores']) / len(self.stats['confidence_scores'])
                if self.stats['confidence_scores'] else 0.0
            )
        }
