#!/usr/bin/env python3
"""
Unit tests for shared season detection module (lib/season_detection.py)

Tests all 17 season patterns, multi-stage validation, confidence scoring,
and comprehensive detection functionality.
"""

import unittest
import sys
import importlib.util
from pathlib import Path


def load_module_from_path(module_path: str, module_name: str):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSeasonPatternDefinitions(unittest.TestCase):
    """Test SeasonPatternDefinitions class."""

    @classmethod
    def setUpClass(cls):
        """Load season_detection module."""
        module_path = Path(__file__).parent.parent.parent / 'lib' / 'season_detection.py'
        cls.module = load_module_from_path(str(module_path), 'season_detection')
        cls.patterns = cls.module.SeasonPatternDefinitions()

    def test_all_patterns_count(self):
        """Verify we have all 17 patterns."""
        all_patterns = self.patterns.get_all_patterns()
        self.assertEqual(len(all_patterns), 17, "Should have exactly 17 patterns")

    def test_standard_patterns(self):
        """Test standard patterns (S01E01, Season 1)."""
        self.assertEqual(len(self.patterns.STANDARD_PATTERNS), 2)
        self.assertIn('S{:02d}E format', [p[1] for p in self.patterns.STANDARD_PATTERNS])
        self.assertIn('Season X format', [p[1] for p in self.patterns.STANDARD_PATTERNS])

    def test_extended_patterns(self):
        """Test extended patterns (S100+)."""
        self.assertEqual(len(self.patterns.EXTENDED_PATTERNS), 2)
        self.assertTrue(any('Extended' in p[1] for p in self.patterns.EXTENDED_PATTERNS))

    def test_numeric_only_patterns(self):
        """Test numeric-only patterns."""
        self.assertEqual(len(self.patterns.NUMERIC_ONLY), 2)

    def test_year_based_patterns(self):
        """Test year-based patterns."""
        self.assertEqual(len(self.patterns.YEAR_BASED), 1)
        self.assertIn('Year format', self.patterns.YEAR_BASED[0][1])

    def test_episode_patterns(self):
        """Test episode/media patterns."""
        self.assertEqual(len(self.patterns.EPISODE_PATTERNS), 8)


class TestSeasonValidationEngine(unittest.TestCase):
    """Test SeasonValidationEngine class."""

    @classmethod
    def setUpClass(cls):
        """Load season_detection module."""
        module_path = Path(__file__).parent.parent.parent / 'lib' / 'season_detection.py'
        cls.module = load_module_from_path(str(module_path), 'season_detection')
        cls.validator = cls.module.SeasonValidationEngine()

    def test_quality_indicator_detection(self):
        """Test quality indicator detection."""
        # Should detect quality indicators
        self.assertTrue(self.validator.detect_quality_indicators("Show.S01E01.720p.mkv"))
        self.assertTrue(self.validator.detect_quality_indicators("Show.S01E01.1080p.x264.mkv"))
        self.assertTrue(self.validator.detect_quality_indicators("Show.S01E01.HEVC.mkv"))

        # Should not detect quality indicators
        self.assertFalse(self.validator.detect_quality_indicators("Show.S01E01.mkv"))
        self.assertFalse(self.validator.detect_quality_indicators("Show.Season.01.Episode.01.mkv"))

    def test_position_validation(self):
        """Test position-based validation."""
        filename = "Show.S01E01.Episode.Name.mkv"

        # Early position should have positive adjustment
        early_pos = filename.find("S01")
        adjustment = self.validator.validate_position(filename, early_pos)
        self.assertGreater(adjustment, 0, "Early position should have positive adjustment")

        # Late position should have negative adjustment
        late_filename = "Some.Show.Name.Information.S01E01.mkv"
        late_pos = late_filename.find("S01")
        late_adjustment = self.validator.validate_position(late_filename, late_pos)
        self.assertLess(late_adjustment, 0, "Late position should have negative adjustment")

    def test_range_validation(self):
        """Test range validation by pattern type."""
        # Standard patterns: 1-50
        self.assertTrue(self.validator.validate_range_by_pattern(1, "S{:02d}E format"))
        self.assertTrue(self.validator.validate_range_by_pattern(50, "Season X format"))
        self.assertFalse(self.validator.validate_range_by_pattern(0, "S{:02d}E format"))
        self.assertFalse(self.validator.validate_range_by_pattern(51, "S{:02d}E format"))

        # Extended patterns: 100-2050
        self.assertTrue(self.validator.validate_range_by_pattern(100, "Extended season S###E## format"))
        self.assertTrue(self.validator.validate_range_by_pattern(2050, "Extended Season #### format"))
        self.assertFalse(self.validator.validate_range_by_pattern(99, "Extended season S###E## format"))
        self.assertFalse(self.validator.validate_range_by_pattern(2051, "Extended Season #### format"))

        # Year-based: 1990+
        self.assertTrue(self.validator.validate_range_by_pattern(1990, "Year format"))
        self.assertTrue(self.validator.validate_range_by_pattern(2099, "Year format"))
        self.assertFalse(self.validator.validate_range_by_pattern(1989, "Year format"))

    def test_confidence_scoring(self):
        """Test confidence score calculation."""
        filename = "Show.S01E01.Episode.Name.mkv"
        match_text = "S01E01"
        season_num = 1
        pattern_desc = "S{:02d}E format"

        confidence = self.validator.calculate_confidence_score(
            filename, match_text, season_num, pattern_desc
        )

        # Confidence should be in valid range
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_numeric_season_validation(self):
        """Test validate_numeric_season method."""
        # Valid numeric season
        is_valid, confidence = self.validator.validate_numeric_season(
            "Show.Episode.01.mkv", "01", 1, "Episode-prefixed numeric format"
        )
        self.assertTrue(is_valid)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

        # Invalid due to quality indicator
        is_valid, confidence = self.validator.validate_numeric_season(
            "Show.Episode.01.720p.mkv", "01", 1, "Episode-prefixed numeric format"
        )
        self.assertFalse(is_valid)
        self.assertEqual(confidence, 0.0)


class TestBaseSeasonDetector(unittest.TestCase):
    """Test BaseSeasonDetector class."""

    @classmethod
    def setUpClass(cls):
        """Load season_detection module."""
        module_path = Path(__file__).parent.parent.parent / 'lib' / 'season_detection.py'
        cls.module = load_module_from_path(str(module_path), 'season_detection')

    def setUp(self):
        """Create fresh detector for each test."""
        self.detector = self.module.BaseSeasonDetector()

    def test_standard_s01e01_format(self):
        """Test S01E01 format detection."""
        season, desc, match = self.detector.extract_season_info("Show.S01E01.mkv")
        self.assertEqual(season, 1)
        self.assertIn("S{:02d}E format", desc)
        self.assertEqual(match, "S01E01")

    def test_season_format(self):
        """Test Season X format detection."""
        season, desc, match = self.detector.extract_season_info("Show.Season.01.mkv")
        self.assertEqual(season, 1)
        self.assertIn("Season X format", desc)

    def test_extended_season_format(self):
        """Test extended season format (S100+)."""
        season, desc, match = self.detector.extract_season_info("Show.S100E01.mkv")
        self.assertEqual(season, 100)
        self.assertIn("Extended", desc)

    def test_year_based_format(self):
        """Test year-based season format."""
        season, desc, match = self.detector.extract_season_info("Show.2023.Episode.01.mkv")
        self.assertEqual(season, 2023)
        self.assertIn("Year format", desc)

    def test_episode_format(self):
        """Test episode format detection."""
        season, desc, match = self.detector.extract_season_info("Show.Episode.05.mkv")
        self.assertEqual(season, 5)
        self.assertIn("Episode", desc)

    def test_part_format(self):
        """Test part format detection."""
        season, desc, match = self.detector.extract_season_info("Show.Part.03.mkv")
        self.assertEqual(season, 3)
        self.assertIn("Part", desc)

    def test_disc_format(self):
        """Test disc format detection."""
        season, desc, match = self.detector.extract_season_info("Show.Disc.02.mkv")
        self.assertEqual(season, 2)
        self.assertIn("Disc", desc)

    def test_volume_format(self):
        """Test volume format detection."""
        season, desc, match = self.detector.extract_season_info("Show.Vol.04.mkv")
        self.assertEqual(season, 4)
        self.assertIn("Vol", desc)

    def test_quality_indicator_rejection(self):
        """Test that quality indicators are properly rejected."""
        season, desc, match = self.detector.extract_season_info("Show.720p.x264.mkv")
        self.assertIsNone(season)
        self.assertEqual(desc, "No pattern matched")

    def test_case_insensitivity(self):
        """Test that patterns are case-insensitive."""
        season1, _, _ = self.detector.extract_season_info("Show.S01E01.mkv")
        season2, _, _ = self.detector.extract_season_info("Show.s01e01.mkv")
        self.assertEqual(season1, season2)

    def test_no_match(self):
        """Test behavior when no pattern matches."""
        season, desc, match = self.detector.extract_season_info("Random.File.Name.mkv")
        self.assertIsNone(season)
        self.assertEqual(desc, "No pattern matched")
        self.assertEqual(match, "")

    def test_season_directory_name_generation(self):
        """Test season directory name generation."""
        # Standard season
        name1 = self.detector.generate_season_directory_name(1, "S{:02d}E format")
        self.assertEqual(name1, "Season 01")

        # Extended season
        name2 = self.detector.generate_season_directory_name(100, "Extended season format")
        self.assertEqual(name2, "Season 100")

        # Year-based season
        name3 = self.detector.generate_season_directory_name(2023, "Year format")
        self.assertEqual(name3, "Season 2023")

    def test_pattern_usage_tracking(self):
        """Test that pattern usage is tracked."""
        self.detector.extract_season_info("Show.S01E01.mkv")
        self.detector.extract_season_info("Show.S02E01.mkv")
        self.detector.extract_season_info("Show.Season.03.mkv")

        stats = self.detector.get_detection_stats()
        self.assertIn('patterns_found', stats)
        self.assertGreater(stats['total_patterns_used'], 0)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Maximum standard season
        season, _, _ = self.detector.extract_season_info("Show.S50E01.mkv")
        self.assertEqual(season, 50)

        # Minimum extended season
        season, _, _ = self.detector.extract_season_info("Show.S100E01.mkv")
        self.assertEqual(season, 100)

        # Maximum extended season
        season, _, _ = self.detector.extract_season_info("Show.S2050E01.mkv")
        self.assertEqual(season, 2050)


class TestRealWorldScenarios(unittest.TestCase):
    """Test with real-world filename scenarios."""

    @classmethod
    def setUpClass(cls):
        """Load season_detection module."""
        module_path = Path(__file__).parent.parent.parent / 'lib' / 'season_detection.py'
        cls.module = load_module_from_path(str(module_path), 'season_detection')

    def setUp(self):
        """Create fresh detector for each test."""
        self.detector = self.module.BaseSeasonDetector()

    def test_common_tv_show_patterns(self):
        """Test common TV show naming patterns."""
        test_cases = [
            ("The.Show.S01E01.Episode.Name.mkv", 1),
            ("Show Name - S02E05 - Episode Title.mp4", 2),
            ("Show.Name.s03e12.720p.WEB-DL.mkv", 3),
            ("Show_Name_Season_04_Episode_03.avi", 4),
            ("ShowName.1x05.Episode.Title.mkv", 1),
        ]

        for filename, expected_season in test_cases:
            season, _, _ = self.detector.extract_season_info(filename)
            self.assertEqual(season, expected_season,
                           f"Failed for filename: {filename}")

    def test_anime_patterns(self):
        """Test anime-style naming patterns."""
        test_cases = [
            ("Anime.Title.Episode.01.mkv", 1),
            ("Anime.Title.Part.05.mp4", 5),
            ("Anime.Title.Vol.03.mkv", 3),
        ]

        for filename, expected_season in test_cases:
            season, _, _ = self.detector.extract_season_info(filename)
            self.assertEqual(season, expected_season,
                           f"Failed for filename: {filename}")

    def test_documentary_patterns(self):
        """Test documentary-style naming patterns."""
        test_cases = [
            ("Documentary.Series.2023.Episode.1.mkv", 2023),
            ("Nature.Documentary.Disc.2.mp4", 2),
        ]

        for filename, expected_season in test_cases:
            season, _, _ = self.detector.extract_season_info(filename)
            self.assertEqual(season, expected_season,
                           f"Failed for filename: {filename}")


if __name__ == '__main__':
    unittest.main()
