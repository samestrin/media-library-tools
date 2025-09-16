#!/usr/bin/env python3
"""
Unit tests for SABnzbd Directory Cleanup Script
"""

import importlib.util
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path to import test helpers
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import test helpers, handle import errors gracefully
try:
    from utils.test_helpers import TEST_HELPERS_AVAILABLE, MediaLibraryTestCase
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

# Try to import functions from sabnzbd_cleanup script, handle import errors gracefully
try:
    # Load the sabnzbd_cleanup script as a module by copying it to a .py file temporarily
    script_path = Path(__file__).parent.parent.parent / "SABnzbd" / "sabnzbd_cleanup"
    temp_script_path = Path(__file__).parent / "temp_sabnzbd_cleanup.py"

    # Copy the script content to a temporary .py file
    import shutil

    shutil.copy2(script_path, temp_script_path)

    # Now import it as a regular Python module
    spec = importlib.util.spec_from_file_location("sabnzbd_cleanup", temp_script_path)
    sabnzbd_module = importlib.util.module_from_spec(spec)
    sys.modules["sabnzbd_cleanup"] = sabnzbd_module
    spec.loader.exec_module(sabnzbd_module)

    # Extract the classes and functions we need
    SABnzbdDetector = getattr(sabnzbd_module, "SABnzbdDetector", None)
    get_dir_size = getattr(sabnzbd_module, "get_dir_size", None)
    bytes_to_human = getattr(sabnzbd_module, "bytes_to_human", None)
    is_non_interactive = getattr(sabnzbd_module, "is_non_interactive", None)
    parse_size_threshold = getattr(sabnzbd_module, "parse_size_threshold", None)

    # Clean up the temporary file
    temp_script_path.unlink(missing_ok=True)

except Exception as e:
    print(f"Import failed: {e}")
    import traceback

    traceback.print_exc()
    SABnzbdDetector = None
    get_dir_size = None
    bytes_to_human = None
    is_non_interactive = None
    parse_size_threshold = None
    # Clean up the temporary file in case of error
    temp_script_path = Path(__file__).parent / "temp_sabnzbd_cleanup.py"
    temp_script_path.unlink(missing_ok=True)

# Debug: Print what we imported
print(f"DEBUG: SABnzbdDetector = {SABnzbdDetector}")
print(f"DEBUG: bytes_to_human = {bytes_to_human}")
print(f"DEBUG: TEST_HELPERS_AVAILABLE = {TEST_HELPERS_AVAILABLE}")


@unittest.skipIf(bytes_to_human is None, "SABnzbd tools not available")
class TestBytesToHuman(MediaLibraryTestCase):
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
class TestParseSizeThreshold(MediaLibraryTestCase):
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


@unittest.skipIf(
    SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE,
    "SABnzbd tools or test helpers not available",
)
class TestSABnzbdDetector(MediaLibraryTestCase):
    """Test the SABnzbdDetector class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.detector = SABnzbdDetector()

    def test_is_bittorrent_directory_no_files(self):
        """Test is_bittorrent_directory with no torrent files."""
        test_dir = self.copy_fixture("sabnzbd/mixed_environment")

        # Validate fixture structure
        expected_structure = {"complete": {}, "incomplete": {}, "watched": {}}
        self.fixture_manager.assert_directory_structure(test_dir, expected_structure)

        empty_dir = test_dir / "empty_test_dir"
        empty_dir.mkdir()

        result = self.detector.is_bittorrent_directory(empty_dir)
        self.assertFalse(result)

    def test_analyze_directory_no_indicators(self):
        """Test analyze_directory with no SABnzbd indicators."""
        test_dir = self.copy_fixture("sabnzbd/mixed_environment")

        # Validate fixture structure
        expected_structure = {"complete": {}, "incomplete": {}, "watched": {}}
        self.fixture_manager.assert_directory_structure(test_dir, expected_structure)

        empty_dir = test_dir / "empty_test_dir"
        empty_dir.mkdir()

        is_sabnzbd, score, indicators = self.detector.analyze_directory(empty_dir)
        self.assertFalse(is_sabnzbd)
        self.assertEqual(score, 0)
        self.assertEqual(indicators, [])


if __name__ == "__main__":
    unittest.main()
