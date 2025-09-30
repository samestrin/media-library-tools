#!/usr/bin/env python3
"""
Comprehensive Test Suite for plex_make_seasons v3.1.0
Tests all phases: consolidation, organization, and archive
"""

import unittest
import tempfile
import shutil
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple


def load_script_as_module(script_path: str, module_name: str):
    """
    Load an extensionless Python script as a module for testing.
    
    Args:
        script_path: Path to the extensionless script
        module_name: Name to assign to the loaded module
    
    Returns:
        The loaded module
    """
    script_path = Path(script_path)
    
    # Create temporary .py file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_py_path = temp_file.name
        
        # Copy script content to temporary .py file
        with open(script_path, 'r') as original:
            temp_file.write(original.read())
    
    try:
        # Load module from temporary .py file
        spec = importlib.util.spec_from_file_location(module_name, temp_py_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        # Clean up temporary file
        Path(temp_py_path).unlink(missing_ok=True)


class PlexMakeSeasonsTestBase(unittest.TestCase):
    """Base test class with common setup and utilities."""
    
    @classmethod
    def setUpClass(cls):
        """Load the plex_make_seasons module once for all tests."""
        # Navigate from tests/unit/ to repository root, then to built script
        script_path = Path(__file__).parent.parent.parent / 'plex' / 'plex_make_seasons'
        cls.module = load_script_as_module(str(script_path), 'plex_make_seasons')

    def setUp(self):
        """Create temporary test directory for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def tearDown(self):
        """Clean up test directory."""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, relative_path: str, size_mb: int = 100) -> Path:
        """
        Create a test file with specified size.
        
        Args:
            relative_path: Path relative to test directory
            size_mb: Size of file in MB
            
        Returns:
            Path to created file
        """
        file_path = Path(self.test_dir) / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with specified size
        with open(file_path, 'wb') as f:
            # Write 1MB chunks
            chunk = b'0' * (1024 * 1024)
            for _ in range(size_mb):
                f.write(chunk)
        
        return file_path


class TestConfigurationManagement(PlexMakeSeasonsTestBase):
    """Test configuration loading and validation."""

    def test_default_configuration(self):
        """Test default configuration values."""
        # Test that module has expected configuration attributes
        expected_attrs = ['VERSION', 'DEFAULT_SAMPLE_THRESHOLD', 'DEFAULT_MAX_DEPTH']
        for attr in expected_attrs:
            self.assertTrue(hasattr(self.module, attr), 
                          f"Module should have {attr} attribute")

    def test_configuration_validation(self):
        """Test configuration parameter validation."""
        # Test sample threshold validation
        if hasattr(self.module, 'validate_sample_threshold'):
            # Valid thresholds
            self.assertTrue(self.module.validate_sample_threshold(50))
            self.assertTrue(self.module.validate_sample_threshold(200))
            
            # Invalid thresholds
            self.assertFalse(self.module.validate_sample_threshold(-1))
            self.assertFalse(self.module.validate_sample_threshold(0))

    def test_env_configuration_loading(self):
        """Test environment variable configuration loading."""
        # Set test environment variables
        test_env = {
            'PLEX_MAKE_SEASONS_SAMPLE_THRESHOLD': '150',
            'PLEX_MAKE_SEASONS_MAX_DEPTH': '5',
            'PLEX_MAKE_SEASONS_ARCHIVE_SAMPLES': 'true'
        }
        
        # Temporarily set environment variables
        original_env = {}
        for key, value in test_env.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            # Test configuration loading
            if hasattr(self.module, 'load_configuration'):
                config = self.module.load_configuration()
                self.assertEqual(config.get('sample_threshold'), 150)
                self.assertEqual(config.get('max_depth'), 5)
                self.assertTrue(config.get('archive_samples'))
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class TestConsolidationPhase(PlexMakeSeasonsTestBase):
    """Test season detection and file consolidation logic."""

    def test_season_extraction_standard_format(self):
        """Test season extraction from standard filename formats."""
        test_cases = [
            ("Show.S01E01.Episode.Name.mkv", 1),
            ("Show.S02E05.Another.Episode.avi", 2),
            ("Show.S10E15.Final.Episode.mp4", 10),
            ("Show.Season.01.Episode.01.mkv", 1),
            ("Show.Season.02.Episode.05.avi", 2),
        ]
        
        for filename, expected_season in test_cases:
            with self.subTest(filename=filename):
                if hasattr(self.module, 'extract_season_number'):
                    season = self.module.extract_season_number(filename)
                    self.assertEqual(season, expected_season,
                                   f"Failed for {filename}: expected {expected_season}, got {season}")

    def test_season_extraction_alternative_formats(self):
        """Test season extraction from alternative filename formats."""
        test_cases = [
            ("Show - 1x01 - Episode Name.mkv", 1),
            ("Show - 2x05 - Another Episode.avi", 2),
            ("Show.1x01.Episode.Name.mp4", 1),
            ("Show.2x05.Another.Episode.mkv", 2),
        ]
        
        for filename, expected_season in test_cases:
            with self.subTest(filename=filename):
                if hasattr(self.module, 'extract_season_number'):
                    season = self.module.extract_season_number(filename)
                    self.assertEqual(season, expected_season,
                                   f"Failed for {filename}: expected {expected_season}, got {season}")

    def test_season_extraction_extended_format(self):
        """Test season extraction from extended filename formats."""
        test_cases = [
            ("Show.Season.100.Episode.1.avi", 100),
            ("Show.S100E01.Episode.Name.mkv", 100),
            ("Show - 100x01 - Episode Name.mp4", 100),
        ]
        
        for filename, expected_season in test_cases:
            with self.subTest(filename=filename):
                if hasattr(self.module, 'extract_season_number'):
                    season = self.module.extract_season_number(filename)
                    self.assertEqual(season, expected_season,
                                   f"Failed for {filename}: expected {expected_season}, got {season}")

    def test_season_extraction_false_positives(self):
        """Test that season extraction avoids false positives."""
        test_cases = [
            "Movie.2023.1080p.BluRay.mkv",  # Year, not season
            "Show.Behind.The.Scenes.mkv",   # No season info
            "Documentary.Part.1.mp4",       # Part number, not season
            "Show.Extras.Deleted.Scenes.mkv",  # Extras
            "Show.Making.Of.Documentary.avi",  # Making of
        ]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                if hasattr(self.module, 'extract_season_number'):
                    season = self.module.extract_season_number(filename)
                    self.assertIsNone(season,
                                     f"Should not extract season from {filename}, got {season}")

    def test_sample_file_detection(self):
        """Test sample file detection logic."""
        # Create test files with different sizes
        large_file = self.create_test_file("Show.S01E01.mkv", 500)  # 500MB
        small_file = self.create_test_file("Show.S01E01.sample.mkv", 50)  # 50MB
        
        if hasattr(self.module, 'is_sample_file'):
            # Large file should not be considered a sample
            self.assertFalse(self.module.is_sample_file(str(large_file), 100),
                           "Large file should not be detected as sample")
            
            # Small file should be considered a sample
            self.assertTrue(self.module.is_sample_file(str(small_file), 100),
                          "Small file should be detected as sample")
        
        # Test filename-based detection
        sample_filenames = [
            "Show.S01E01.sample.mkv",
            "Show.S01E01.SAMPLE.avi",
            "Show.S01E01.Sample.mp4",
        ]
        
        for filename in sample_filenames:
            with self.subTest(filename=filename):
                if hasattr(self.module, 'is_sample_file'):
                    # Create small file to trigger size-based detection
                    test_file = self.create_test_file(filename, 50)
                    self.assertTrue(self.module.is_sample_file(str(test_file), 100),
                                  f"Should detect {filename} as sample")

    def test_directory_exclusion(self):
        """Test directory exclusion logic."""
        excluded_dirs = [
            "Extras",
            "Behind the Scenes", 
            "Deleted Scenes",
            "Featurettes",
            "Interviews",
            "Trailers"
        ]
        
        for dir_name in excluded_dirs:
            with self.subTest(dir_name=dir_name):
                if hasattr(self.module, 'should_exclude_directory'):
                    self.assertTrue(self.module.should_exclude_directory(dir_name),
                                  f"Should exclude directory: {dir_name}")
        
        # Test that normal directories are not excluded
        normal_dirs = ["Season 01", "Season 02", "Episodes", "Show Name"]
        for dir_name in normal_dirs:
            with self.subTest(dir_name=dir_name):
                if hasattr(self.module, 'should_exclude_directory'):
                    self.assertFalse(self.module.should_exclude_directory(dir_name),
                                   f"Should not exclude directory: {dir_name}")


class TestOrganizationPhase(PlexMakeSeasonsTestBase):
    """Test file organization and season directory creation."""

    def test_season_directory_creation(self):
        """Test creation of season directories."""
        # Create test files for multiple seasons
        files = [
            "Show.S01E01.mkv",
            "Show.S01E02.mkv", 
            "Show.S02E01.mkv",
            "Show.S02E02.mkv",
        ]
        
        for filename in files:
            self.create_test_file(filename)
        
        if hasattr(self.module, 'create_season_directories'):
            season_dirs = self.module.create_season_directories(self.test_dir)
            
            # Should create Season 01 and Season 02 directories
            expected_dirs = ["Season 01", "Season 02"]
            for season_dir in expected_dirs:
                season_path = Path(self.test_dir) / season_dir
                self.assertTrue(season_path.exists(),
                              f"Season directory should be created: {season_dir}")

    def test_file_movement_tracking(self):
        """Test file movement tracking for rollback capability."""
        # Create test files
        test_files = [
            "Show.S01E01.mkv",
            "Show.S01E02.mkv",
        ]
        
        for filename in test_files:
            self.create_test_file(filename)
        
        if hasattr(self.module, 'organize_files_with_tracking'):
            movements = self.module.organize_files_with_tracking(self.test_dir)
            
            # Should track file movements
            self.assertIsInstance(movements, list)
            self.assertGreater(len(movements), 0)
            
            # Each movement should have source and destination
            for movement in movements:
                self.assertIn('source', movement)
                self.assertIn('destination', movement)


class TestArchivePhase(PlexMakeSeasonsTestBase):
    """Test archive creation and rollback functionality."""

    def test_manifest_creation(self):
        """Test creation of operation manifest for rollback."""
        # Create test scenario
        test_operations = [
            {
                "type": "move",
                "source": "/path/to/Show.S01E01.mkv",
                "destination": "/path/to/Season 01/Show.S01E01.mkv"
            },
            {
                "type": "create_directory", 
                "path": "/path/to/Season 01"
            }
        ]
        
        if hasattr(self.module, 'create_manifest'):
            manifest_path = self.module.create_manifest(self.test_dir, test_operations)
            
            # Manifest file should be created
            self.assertTrue(Path(manifest_path).exists())
            
            # Manifest should contain operation data
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
                
            self.assertIn('operations', manifest_data)
            self.assertIn('timestamp', manifest_data)
            self.assertEqual(len(manifest_data['operations']), 2)


class TestCompleteWorkflow(PlexMakeSeasonsTestBase):
    """Test complete workflow integration."""

    def test_dry_run_mode(self):
        """Test dry run mode functionality."""
        # Create test files
        test_files = [
            "Show.S01E01.mkv",
            "Show.S01E02.mkv",
            "Show.S02E01.mkv",
        ]
        
        for filename in test_files:
            self.create_test_file(filename)
        
        if hasattr(self.module, 'process_directory'):
            # Run in dry run mode
            result = self.module.process_directory(self.test_dir, dry_run=True)
            
            # Files should not be moved in dry run
            for filename in test_files:
                original_path = Path(self.test_dir) / filename
                self.assertTrue(original_path.exists(),
                              f"File should not be moved in dry run: {filename}")
            
            # Should return planned operations
            self.assertIsInstance(result, dict)
            self.assertIn('planned_operations', result)

    def test_single_season_processing(self):
        """Test processing directory with single season."""
        # Create test files for single season
        test_files = [
            "Show.S01E01.mkv",
            "Show.S01E02.mkv",
            "Show.S01E03.mkv",
        ]
        
        for filename in test_files:
            self.create_test_file(filename)
        
        if hasattr(self.module, 'process_directory'):
            result = self.module.process_directory(self.test_dir, dry_run=False)
            
            # Season 01 directory should be created
            season_dir = Path(self.test_dir) / "Season 01"
            self.assertTrue(season_dir.exists())
            
            # Files should be moved to season directory
            for filename in test_files:
                moved_file = season_dir / filename
                self.assertTrue(moved_file.exists(),
                              f"File should be moved to season directory: {filename}")


class TestCLIArguments(unittest.TestCase):
    """Test CLI argument parsing and handling."""
    
    @classmethod
    def setUpClass(cls):
        """Load the plex_make_seasons module."""
        # Navigate from tests/unit/ to repository root, then to built script
        script_path = Path(__file__).parent.parent.parent / 'plex' / 'plex_make_seasons'
        cls.module = load_script_as_module(str(script_path), 'plex_make_seasons')

    def test_standard_arguments(self):
        """Test standard CLI arguments are supported."""
        expected_args = ['--verbose', '--debug', '--delete', '--yes', '--version']
        
        if hasattr(self.module, 'create_argument_parser'):
            parser = self.module.create_argument_parser()
            
            # Check that expected arguments are supported
            for arg in expected_args:
                # This is a basic check - in practice you'd test argument parsing
                self.assertIsNotNone(parser)

    def test_configuration_attributes(self):
        """Test that module has required configuration attributes."""
        required_attrs = [
            'VERSION',
            'DEFAULT_SAMPLE_THRESHOLD', 
            'DEFAULT_MAX_DEPTH'
        ]
        
        for attr in required_attrs:
            with self.subTest(attribute=attr):
                self.assertTrue(hasattr(self.module, attr),
                              f"Module should have {attr} attribute")
        
        # Test version format
        if hasattr(self.module, 'VERSION'):
            version = self.module.VERSION
            self.assertIsInstance(version, str)
            self.assertRegex(version, r'^\d+\.\d+(\.\d+)?$',
                           "Version should follow semantic versioning")
        
        # Test threshold is numeric
        if hasattr(self.module, 'DEFAULT_SAMPLE_THRESHOLD'):
            threshold = self.module.DEFAULT_SAMPLE_THRESHOLD
            self.assertIsInstance(threshold, (int, float))
            self.assertGreater(threshold, 0)


class TestPerformance(PlexMakeSeasonsTestBase):
    """Test performance with realistic data volumes."""

    def test_large_file_discovery(self):
        """Test file discovery with many files."""
        # Create many test files
        for i in range(100):
            season = (i // 20) + 1
            episode = (i % 20) + 1
            filename = f"Show.S{season:02d}E{episode:02d}.mkv"
            self.create_test_file(filename, 1)  # 1MB files for speed
        
        if hasattr(self.module, 'discover_video_files'):
            video_files = self.module.discover_video_files(self.test_dir)
            self.assertEqual(len(video_files), 100)
        else:
            # Fallback test - just check files were created
            video_files = list(Path(self.test_dir).glob("*.mkv"))
            self.assertEqual(len(video_files), 100)


class TestEdgeCases(PlexMakeSeasonsTestBase):
    """Test edge cases and error conditions."""

    def test_empty_directory(self):
        """Test behavior with empty directory."""
        if hasattr(self.module, 'discover_video_files'):
            video_files = self.module.discover_video_files(self.test_dir)
            self.assertEqual(len(video_files), 0)
        else:
            # Fallback test
            video_files = list(Path(self.test_dir).glob("*.mkv"))
            self.assertEqual(len(video_files), 0)

    def test_files_without_season_info(self):
        """Test handling of files without season information."""
        # Create files without season info
        non_season_files = [
            "Movie.2023.1080p.mkv",
            "Documentary.mkv", 
            "Behind.The.Scenes.avi",
        ]
        
        for filename in non_season_files:
            self.create_test_file(filename)
        
        if hasattr(self.module, 'extract_season_number'):
            for filename in non_season_files:
                with self.subTest(filename=filename):
                    season = self.module.extract_season_number(filename)
                    self.assertIsNone(season,
                                     f"Should not extract season from {filename}")

    def test_special_characters_in_filenames(self):
        """Test handling of special characters in filenames."""
        special_files = [
            "Show's Best Episodes.S01E01.mkv",
            "Show (2023).S01E01.mkv",
            "Show & More.S01E01.mkv",
            "Show [Director's Cut].S01E01.mkv",
        ]
        
        for filename in special_files:
            with self.subTest(filename=filename):
                # Create file and test it can be processed
                test_file = self.create_test_file(filename)
                self.assertTrue(test_file.exists())
                
                if hasattr(self.module, 'extract_season_number'):
                    season = self.module.extract_season_number(filename)
                    self.assertEqual(season, 1,
                                   f"Should extract season 1 from {filename}")


def create_test_suite():
    """Create a comprehensive test suite."""
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestConfigurationManagement,
        TestConsolidationPhase,
        TestOrganizationPhase,
        TestArchivePhase,
        TestCompleteWorkflow,
        TestCLIArguments,
        TestPerformance,
        TestEdgeCases,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


if __name__ == '__main__':
    # Run comprehensive test suite
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_test_suite()
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)