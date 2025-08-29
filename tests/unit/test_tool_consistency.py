#!/usr/bin/env python3
"""
Tool Consistency Tests
Tests that plex_make_seasons and plex_make_all_seasons handle patterns consistently
"""

import unittest
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import both tools
try:
    import importlib.util
    
    # Import plex_make_seasons
    seasons_script_path = project_root / 'plex' / 'plex_make_seasons'
    spec1 = importlib.util.spec_from_file_location("plex_make_seasons", seasons_script_path)
    if spec1 and spec1.loader:
        seasons_module = importlib.util.module_from_spec(spec1)
        spec1.loader.exec_module(seasons_module)
        SeasonOrganizer = seasons_module.SeasonOrganizer
        SEASONS_AVAILABLE = True
    else:
        SeasonOrganizer = None
        SEASONS_AVAILABLE = False
    
    # Import plex_make_all_seasons 
    all_seasons_script_path = project_root / 'plex' / 'plex_make_all_seasons'
    spec2 = importlib.util.spec_from_file_location("plex_make_all_seasons", all_seasons_script_path)
    if spec2 and spec2.loader:
        all_seasons_module = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(all_seasons_module)
        AllSeasonsOrganizer = all_seasons_module.SeasonOrganizer
        ALL_SEASONS_AVAILABLE = True
    else:
        AllSeasonsOrganizer = None
        ALL_SEASONS_AVAILABLE = False
        
    BOTH_AVAILABLE = SEASONS_AVAILABLE and ALL_SEASONS_AVAILABLE
        
except Exception as e:
    print(f"Warning: Could not import tools: {e}")
    SeasonOrganizer = None
    AllSeasonsOrganizer = None
    BOTH_AVAILABLE = False


@unittest.skipIf(not BOTH_AVAILABLE, "Both tools not available for consistency testing")
class TestToolConsistency(unittest.TestCase):
    """Test that both tools handle patterns consistently."""
    
    def setUp(self):
        """Set up both organizers."""
        self.seasons_organizer = SeasonOrganizer(dry_run=True)
        self.all_seasons_organizer = AllSeasonsOrganizer(dry_run=True)
    
    def test_extended_season_patterns_consistency(self):
        """Test that both tools handle extended season patterns consistently."""
        test_cases = [
            "Show s2025e01.mkv",
            "Series.S2030E05.mp4", 
            "Title Season 100 Episode 1.avi",
            "Movie s150e01.avi",
        ]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                # Get results from both tools
                seasons_result = self.seasons_organizer.extract_season_info(filename)
                all_seasons_result = self.all_seasons_organizer.extract_season_episode(filename)
                
                # Both should detect the same season number
                seasons_season = seasons_result[0]  # (season, pattern, matched)
                all_seasons_season = all_seasons_result[0]  # (season, episode)
                
                self.assertEqual(seasons_season, all_seasons_season,
                               f"Season number mismatch for '{filename}': "
                               f"plex_make_seasons={seasons_season}, plex_make_all_seasons={all_seasons_season}")
                
                # Both should detect a valid season (not None)
                self.assertIsNotNone(seasons_season, f"plex_make_seasons should detect season in '{filename}'")
                self.assertIsNotNone(all_seasons_season, f"plex_make_all_seasons should detect season in '{filename}'")
    
    def test_numeric_only_patterns_consistency(self):
        """Test that both tools handle numeric-only patterns consistently."""
        test_cases = [
            "Show ep01.mkv",
            "Series - 02.mp4",
            "Title.03.avi",
            "Movie ep10.mkv",
        ]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                seasons_result = self.seasons_organizer.extract_season_info(filename)
                all_seasons_result = self.all_seasons_organizer.extract_season_episode(filename)
                
                seasons_season = seasons_result[0]
                all_seasons_season = all_seasons_result[0]
                
                self.assertEqual(seasons_season, all_seasons_season,
                               f"Numeric pattern season mismatch for '{filename}': "
                               f"plex_make_seasons={seasons_season}, plex_make_all_seasons={all_seasons_season}")
    
    def test_enhanced_alternative_patterns_consistency(self):
        """Test that both tools handle enhanced alternative patterns consistently."""
        test_cases = [
            "Show 100x01.mkv",
            "Series 2x05.mp4",
            "Movie 25x01.avi",
            "Title 500x02.mkv",
        ]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                seasons_result = self.seasons_organizer.extract_season_info(filename)
                all_seasons_result = self.all_seasons_organizer.extract_season_episode(filename)
                
                seasons_season = seasons_result[0]
                all_seasons_season = all_seasons_result[0]
                
                self.assertEqual(seasons_season, all_seasons_season,
                               f"Alternative pattern season mismatch for '{filename}': "
                               f"plex_make_seasons={seasons_season}, plex_make_all_seasons={all_seasons_season}")
    
    def test_false_positive_consistency(self):
        """Test that both tools reject false positives consistently."""
        false_positive_cases = [
            "Movie.720p.mkv",
            "Show.1080p.x264.mp4",
            "Series.480p.WEBRip.avi", 
            "Title.25fps.mkv",
            "Movie.5000kbps.mp4",
        ]
        
        for filename in false_positive_cases:
            with self.subTest(filename=filename):
                seasons_result = self.seasons_organizer.extract_season_info(filename)
                all_seasons_result = self.all_seasons_organizer.extract_season_episode(filename)
                
                seasons_season = seasons_result[0]
                all_seasons_season = all_seasons_result[0]
                
                # Both should reject false positives (return None)
                self.assertIsNone(seasons_season, f"plex_make_seasons should reject false positive '{filename}'")
                self.assertIsNone(all_seasons_season, f"plex_make_all_seasons should reject false positive '{filename}'")
    
    def test_range_validation_consistency(self):
        """Test that both tools handle range validation consistently."""
        edge_cases = [
            # Should be rejected
            ("Movie s99e01.mkv", None),      # Below extended range
            ("Series s2051e01.mp4", None),   # Above extended range  
            ("Show ep51.mkv", None),         # Above numeric range
            
            # Should be accepted
            ("Movie s100e01.mkv", 100),      # Valid extended range start
            ("Series s2050e01.mp4", 2050),  # Valid extended range end
            ("Show ep01.mkv", 1),            # Valid numeric range start
            ("Title ep50.mkv", 50),          # Valid numeric range end
        ]
        
        for filename, expected_season in edge_cases:
            with self.subTest(filename=filename):
                seasons_result = self.seasons_organizer.extract_season_info(filename)
                all_seasons_result = self.all_seasons_organizer.extract_season_episode(filename)
                
                seasons_season = seasons_result[0]
                all_seasons_season = all_seasons_result[0]
                
                # Both should return the same result
                self.assertEqual(seasons_season, expected_season,
                               f"plex_make_seasons range validation failed for '{filename}': "
                               f"expected {expected_season}, got {seasons_season}")
                self.assertEqual(all_seasons_season, expected_season, 
                               f"plex_make_all_seasons range validation failed for '{filename}': "
                               f"expected {expected_season}, got {all_seasons_season}")
                               
                # Both should give same result
                self.assertEqual(seasons_season, all_seasons_season,
                               f"Range validation inconsistency for '{filename}': "
                               f"plex_make_seasons={seasons_season}, plex_make_all_seasons={all_seasons_season}")
    
    def test_standard_pattern_consistency(self):
        """Test that both tools still handle standard patterns consistently."""
        standard_cases = [
            ("Show S01E01.mkv", 1),
            ("Series.S02E05.mp4", 2),
            ("Title 5x10.avi", 5),
            ("Movie Season 3 Episode 2.mkv", 3),
        ]
        
        for filename, expected_season in standard_cases:
            with self.subTest(filename=filename):
                seasons_result = self.seasons_organizer.extract_season_info(filename)
                all_seasons_result = self.all_seasons_organizer.extract_season_episode(filename)
                
                seasons_season = seasons_result[0]
                all_seasons_season = all_seasons_result[0]
                
                # Both should detect the expected season
                self.assertEqual(seasons_season, expected_season,
                               f"plex_make_seasons standard pattern failed for '{filename}'")
                self.assertEqual(all_seasons_season, expected_season,
                               f"plex_make_all_seasons standard pattern failed for '{filename}'")
                
                # Both should give same result
                self.assertEqual(seasons_season, all_seasons_season,
                               f"Standard pattern inconsistency for '{filename}': "
                               f"plex_make_seasons={seasons_season}, plex_make_all_seasons={all_seasons_season}")


if __name__ == '__main__':
    # Set up test environment
    print("Tool Consistency Tests")
    print("=" * 50)
    
    if BOTH_AVAILABLE:
        print("✅ Both plex_make_seasons and plex_make_all_seasons loaded successfully")
    else:
        print("⚠️  One or both tools not available - consistency tests will be skipped")
    
    # Run tests
    unittest.main(verbosity=2)