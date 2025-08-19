#!/usr/bin/env python3
"""
Unit tests for Plex tools
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

# Add the plex directory to the path so we can import the scripts
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'plex'))

# Try to import functions from plex tools, handle import errors gracefully
try:
    from plex_movie_subdir_renamer import PlexMovieSubdirRenamer, categorize_file, clean_title
except ImportError:
    PlexMovieSubdirRenamer = None
    categorize_file = None
    clean_title = None

try:
    from plex_make_dirs import PlexDirectoryCreator
except ImportError:
    PlexDirectoryCreator = None

try:
    from plex_make_seasons import SeasonOrganizer
except ImportError:
    SeasonOrganizer = None

try:
    from plex_make_years import YearOrganizer
except ImportError:
    YearOrganizer = None

try:
    from plex_make_all_seasons import SeasonOrganizer as BatchSeasonOrganizer
except ImportError:
    BatchSeasonOrganizer = None

try:
    from plex_move_movie_extras import PlexMovieExtrasOrganizer
except ImportError:
    PlexMovieExtrasOrganizer = None

@unittest.skipIf(categorize_file is None, "Plex tools not available")
class TestCategorizeFile(unittest.TestCase):
    """Test the categorize_file function."""
    
    def test_deleted_scene_categorization(self):
        """Test categorization of deleted scenes."""
        self.assertEqual(categorize_file("deleted_scene.mp4"), "deleted")
        self.assertEqual(categorize_file("cut_scene.mkv"), "deleted")
        self.assertEqual(categorize_file("alternate_ending.avi"), "deleted")
    
    def test_featurette_categorization(self):
        """Test categorization of featurettes."""
        self.assertEqual(categorize_file("featurette.mp4"), "featurette")
        self.assertEqual(categorize_file("behind_the_scenes.mkv"), "featurette")
        self.assertEqual(categorize_file("making_of.avi"), "featurette")
    
    def test_trailer_categorization(self):
        """Test categorization of trailers."""
        self.assertEqual(categorize_file("trailer.mp4"), "trailer")
        self.assertEqual(categorize_file("teaser.mkv"), "trailer")
        self.assertEqual(categorize_file("preview.avi"), "trailer")
    
    def test_other_categorization(self):
        """Test categorization of other extras."""
        self.assertEqual(categorize_file("extra.mp4"), "featurette")  # Default
        self.assertEqual(categorize_file("bonus_feature.mkv"), "featurette")  # Default

@unittest.skipIf(clean_title is None, "Plex tools not available")
class TestCleanTitle(unittest.TestCase):
    """Test the clean_title function."""
    
    def test_clean_title_basic(self):
        """Test basic title cleaning."""
        self.assertEqual(clean_title("01_featurette.mp4"), "featurette")
        self.assertEqual(clean_title("featurette_01.mkv"), "featurette")
        self.assertEqual(clean_title("01-featurette.avi"), "featurette")
        self.assertEqual(clean_title("featurette.01.mov"), "featurette")

@unittest.skipIf(PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Plex tools not available")
class TestPlexMovieSubdirRenamer(MediaLibraryTestCase):
    """Test the PlexMovieSubdirRenamer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.renamer = PlexMovieSubdirRenamer()
    
    def test_is_video_file(self):
        """Test is_video_file method."""
        # Use fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Validate video files fixture structure
        video_structure = {
            'sample.mp4': None,
            'sample.mkv': None,
            'sample.avi': None
        }
        self.assert_directory_structure(test_dir, video_structure)
        
        # Test with valid video extensions from fixtures
        self.assertTrue(self.renamer.is_video_file(test_dir / "sample.mp4"))
        self.assertTrue(self.renamer.is_video_file(test_dir / "sample.mkv"))
        self.assertTrue(self.renamer.is_video_file(test_dir / "sample.avi"))
        
        # Test with invalid extensions from fixtures
        image_dir = self.copy_fixture('common/image_files')
        
        # Validate image files fixture structure
        image_structure = {
            'poster.jpg': None,
            'fanart.png': None
        }
        self.assert_directory_structure(image_dir, image_structure)
        
        self.assertFalse(self.renamer.is_video_file(image_dir / "poster.jpg"))
        self.assertFalse(self.renamer.is_video_file(image_dir / "fanart.png"))

@unittest.skipIf(PlexDirectoryCreator is None or not TEST_HELPERS_AVAILABLE, "Plex tools not available")
class TestPlexDirectoryCreator(MediaLibraryTestCase):
    """Test the PlexDirectoryCreator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.creator = PlexDirectoryCreator()
    
    def test_should_process_file(self):
        """Test should_process_file method."""
        # Use fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test with valid media file from fixtures
        test_file = test_dir / "sample.mp4"
        self.assertTrue(self.creator.should_process_file(test_file))
        
        # Test with excluded file type from fixtures
        test_dir = self.copy_fixture('common/image_files')
        test_file = test_dir / "poster.jpg"
        self.assertFalse(self.creator.should_process_file(test_file))

@unittest.skipIf(SeasonOrganizer is None or not TEST_HELPERS_AVAILABLE, "Plex tools not available")
class TestSeasonOrganizer(MediaLibraryTestCase):
    """Test the SeasonOrganizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organizer = SeasonOrganizer()
    
    def test_is_video_file(self):
        """Test is_video_file method."""
        # Use fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test with valid video extensions from fixtures
        self.assertTrue(self.organizer.is_video_file(test_dir / "sample.mp4"))
        self.assertTrue(self.organizer.is_video_file(test_dir / "sample.mkv"))
        self.assertTrue(self.organizer.is_video_file(test_dir / "sample.avi"))
        
        # Test with invalid extensions from fixtures
        test_dir = self.copy_fixture('common/image_files')
        self.assertFalse(self.organizer.is_video_file(test_dir / "poster.jpg"))
        self.assertFalse(self.organizer.is_video_file(test_dir / "fanart.png"))

@unittest.skipIf(YearOrganizer is None or not TEST_HELPERS_AVAILABLE, "Plex tools not available")
class TestYearOrganizer(MediaLibraryTestCase):
    """Test the YearOrganizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organizer = YearOrganizer()
    
    def test_extract_year_info(self):
        """Test extract_year_info method."""
        year, pattern_desc, matched_text = self.organizer.extract_year_info("Movie.Title.(2023)")
        self.assertEqual(year, 2023)
        
        year, pattern_desc, matched_text = self.organizer.extract_year_info("Another.Movie.[2022]")
        self.assertEqual(year, 2022)

@unittest.skipIf(BatchSeasonOrganizer is None or not TEST_HELPERS_AVAILABLE, "Plex tools not available")
class TestBatchSeasonOrganizer(MediaLibraryTestCase):
    """Test the BatchSeasonOrganizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organizer = BatchSeasonOrganizer()
    
    def test_is_video_file(self):
        """Test is_video_file method."""
        # Use fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test with valid video extensions from fixtures
        self.assertTrue(self.organizer.is_video_file(test_dir / "sample.mp4"))
        self.assertTrue(self.organizer.is_video_file(test_dir / "sample.mkv"))
        self.assertTrue(self.organizer.is_video_file(test_dir / "sample.avi"))
        
        # Test with invalid extensions from fixtures
        test_dir = self.copy_fixture('common/image_files')
        self.assertFalse(self.organizer.is_video_file(test_dir / "poster.jpg"))
        self.assertFalse(self.organizer.is_video_file(test_dir / "fanart.png"))

@unittest.skipIf(PlexMovieExtrasOrganizer is None or not TEST_HELPERS_AVAILABLE, "Plex tools not available")
class TestPlexMovieExtrasOrganizer(MediaLibraryTestCase):
    """Test the PlexMovieExtrasOrganizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.organizer = PlexMovieExtrasOrganizer()
    
    def test_is_video_file(self):
        """Test is_video_file method."""
        # Use fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test with valid video extensions from fixtures
        self.assertTrue(self.organizer.is_video_file("sample.mp4"))
        self.assertTrue(self.organizer.is_video_file("sample.mkv"))
        self.assertTrue(self.organizer.is_video_file("sample.avi"))
        
        # Test with invalid extensions from fixtures
        test_dir = self.copy_fixture('common/image_files')
        self.assertFalse(self.organizer.is_video_file("poster.jpg"))
        self.assertFalse(self.organizer.is_video_file("fanart.png"))

if __name__ == '__main__':
    unittest.main()