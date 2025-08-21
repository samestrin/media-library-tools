#!/usr/bin/env python3
"""
Unit tests for Plex tools
"""

import unittest
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import test helpers
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import test helpers, handle import errors gracefully
try:
    from utils.test_helpers import MediaLibraryTestCase, TEST_HELPERS_AVAILABLE
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

import importlib.util
import shutil

# Try to import functions from plex tools, handle import errors gracefully
def load_plex_tool(tool_name):
    """Load a Plex tool as a module by copying it to a temporary .py file."""
    try:
        script_path = Path(__file__).parent.parent.parent / 'Plex' / tool_name
        if not script_path.exists():
            print(f"DEBUG: Tool {tool_name} not found at {script_path}")
            return None
        
        temp_script_path = Path(__file__).parent / f'temp_{tool_name}.py'
        shutil.copy2(script_path, temp_script_path)
        print(f"DEBUG: Copied {tool_name} to {temp_script_path}")
        
        spec = importlib.util.spec_from_file_location(tool_name, temp_script_path)
        if spec is None or spec.loader is None:
            print(f"DEBUG: Could not create spec for {tool_name}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[tool_name] = module
        spec.loader.exec_module(module)
        
        # Debug: Print available attributes
        attrs = [attr for attr in dir(module) if not attr.startswith('_')]
        print(f"DEBUG: {tool_name} available attributes: {attrs}")
        
        temp_script_path.unlink(missing_ok=True)
        return module
    except Exception as e:
        print(f"DEBUG: Error loading {tool_name}: {e}")
        import traceback
        traceback.print_exc()
        temp_script_path = Path(__file__).parent / f'temp_{tool_name}.py'
        temp_script_path.unlink(missing_ok=True)
        return None

# Load Plex tools
plex_movie_subdir_renamer = load_plex_tool('plex_movie_subdir_renamer')
PlexMovieSubdirRenamer = getattr(plex_movie_subdir_renamer, 'PlexMovieSubdirRenamer', None) if plex_movie_subdir_renamer else None
categorize_file = getattr(plex_movie_subdir_renamer, 'categorize_file', None) if plex_movie_subdir_renamer else None
clean_title = getattr(plex_movie_subdir_renamer, 'clean_title', None) if plex_movie_subdir_renamer else None

plex_make_dirs = load_plex_tool('plex_make_dirs')
PlexDirectoryCreator = getattr(plex_make_dirs, 'PlexDirectoryCreator', None) if plex_make_dirs else None

plex_make_seasons = load_plex_tool('plex_make_seasons')
SeasonOrganizer = getattr(plex_make_seasons, 'SeasonOrganizer', None) if plex_make_seasons else None

plex_make_years = load_plex_tool('plex_make_years')
YearOrganizer = getattr(plex_make_years, 'YearOrganizer', None) if plex_make_years else None

plex_make_all_seasons = load_plex_tool('plex_make_all_seasons')
BatchSeasonOrganizer = getattr(plex_make_all_seasons, 'SeasonOrganizer', None) if plex_make_all_seasons else None

plex_move_movie_extras = load_plex_tool('plex_move_movie_extras')
PlexMovieExtrasOrganizer = getattr(plex_move_movie_extras, 'PlexMovieExtrasOrganizer', None) if plex_move_movie_extras else None

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
        self.assertEqual(categorize_file("extra.mp4"), "other")
        self.assertEqual(categorize_file("bonus_feature.mkv"), "other")
        self.assertEqual(categorize_file("special_edition.mkv"), "other")
        # Test default fallback to featurette
        self.assertEqual(categorize_file("unknown_content.mp4"), "featurette")

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
        self.fixture_manager.assert_directory_structure(test_dir, video_structure)
        
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
        self.fixture_manager.assert_directory_structure(image_dir, image_structure)
        
        self.assertFalse(self.renamer.is_video_file(image_dir / "poster.jpg"))
        self.assertFalse(self.renamer.is_video_file(image_dir / "fanart.png"))

@unittest.skipIf(PlexDirectoryCreator is None or not TEST_HELPERS_AVAILABLE, "Plex tools not available")
class TestPlexDirectoryCreator(MediaLibraryTestCase):
    """Test the PlexDirectoryCreator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        # Configure to exclude image files for proper Plex media organization
        image_types = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico', '.psd', '.raw', '.cr2', '.nef', '.arw'}
        self.creator = PlexDirectoryCreator(exclude_types=image_types)
    
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