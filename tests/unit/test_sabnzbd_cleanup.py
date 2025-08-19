#!/usr/bin/env python3
"""
Unit tests for SABnzbd Directory Cleanup Script
"""

import unittest
import os
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

# Try to import test helpers, handle import errors gracefully
try:
    from test_helpers import MediaLibraryTestCase
    TEST_HELPERS_AVAILABLE = True
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

# Add the SABnzbd directory to the path so we can import the script
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'SABnzbd'))

# Try to import functions from sabnzbd_cleanup, handle import errors gracefully
try:
    from sabnzbd_cleanup import (
        SABnzbdDetector,
        get_dir_size,
        bytes_to_human,
        is_non_interactive,
        parse_size_threshold
    )
except ImportError:
    SABnzbdDetector = None
    get_dir_size = None
    bytes_to_human = None
    is_non_interactive = None
    parse_size_threshold = None

@unittest.skipIf(bytes_to_human is None, "SABnzbd tools not available")
class TestBytesToHuman(unittest.TestCase):
    """Test the bytes_to_human function."""
    
    def test_bytes_conversion(self):
        """Test conversion of bytes to human readable format."""
        self.assertEqual(bytes_to_human(0), "0B")
        self.assertEqual(bytes_to_human(1023), "1023B")
        self.assertEqual(bytes_to_human(1024), "1K")
        self.assertEqual(bytes_to_human(1024**2), "1M")
        self.assertEqual(bytes_to_human(1024**3), "1G")
        self.assertEqual(bytes_to_human(1024**4), "1T")
    
    def test_boundary_values(self):
        """Test boundary values for unit conversions."""
        self.assertEqual(bytes_to_human(1024), "1K")
        self.assertEqual(bytes_to_human(1025), "1K")
        self.assertEqual(bytes_to_human(2048), "2K")

@unittest.skipIf(parse_size_threshold is None, "SABnzbd tools not available")
class TestParseSizeThreshold(unittest.TestCase):
    """Test the parse_size_threshold function."""
    
    def test_valid_formats(self):
        """Test valid size threshold formats."""
        self.assertEqual(parse_size_threshold("50G"), 50 * 1024**3)
        self.assertEqual(parse_size_threshold("2T"), 2 * 1024**4)
        self.assertEqual(parse_size_threshold("500M"), 500 * 1024**2)
        self.assertEqual(parse_size_threshold("1024K"), 1024 * 1024)
        self.assertEqual(parse_size_threshold("500B"), 500)
    
    def test_case_insensitive(self):
        """Test that size threshold parsing is case insensitive."""
        self.assertEqual(parse_size_threshold("50g"), 50 * 1024**3)
        self.assertEqual(parse_size_threshold("2t"), 2 * 1024**4)
    
    def test_invalid_formats(self):
        """Test invalid size threshold formats."""
        with self.assertRaises(ValueError):
            parse_size_threshold("")
        
        with self.assertRaises(ValueError):
            parse_size_threshold("invalid")
        
        with self.assertRaises(ValueError):
            parse_size_threshold("50X")

@unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "SABnzbd tools not available")
class TestSABnzbdDetector(MediaLibraryTestCase):
    """Test the SABnzbdDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.detector = SABnzbdDetector()
    
    def test_is_bittorrent_directory_no_files(self):
        """Test is_bittorrent_directory with no torrent files."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Validate fixture structure
        expected_structure = {
            'complete': {},
            'incomplete': {},
            'watched': {}
        }
        self.assert_directory_structure(test_dir, expected_structure)
        
        empty_dir = test_dir / "empty_test_dir"
        empty_dir.mkdir()
        
        result = self.detector.is_bittorrent_directory(empty_dir)
        self.assertFalse(result)
    
    def test_analyze_directory_no_indicators(self):
        """Test analyze_directory with no SABnzbd indicators."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Validate fixture structure
        expected_structure = {
            'complete': {},
            'incomplete': {},
            'watched': {}
        }
        self.assert_directory_structure(test_dir, expected_structure)
        
        empty_dir = test_dir / "empty_test_dir"
        empty_dir.mkdir()
        
        is_sabnzbd, score, indicators = self.detector.analyze_directory(empty_dir)
        self.assertFalse(is_sabnzbd)
        self.assertEqual(score, 0)
        self.assertEqual(indicators, [])

if __name__ == '__main__':
    unittest.main()