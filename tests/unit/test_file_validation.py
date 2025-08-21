#!/usr/bin/env python3
"""
Unit tests for file type validation across all tools
"""

import unittest
import sys
import os
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

import importlib.util
import shutil
import tempfile

# Dynamic import functions
def load_sabnzbd_tool(tool_name):
    """Dynamically load SABnzbd tool by copying to temp .py file."""
    try:
        tool_path = Path(__file__).parent.parent.parent / 'SABnzbd' / tool_name
        if not tool_path.exists():
            return None
            
        # Create temporary .py file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            shutil.copy2(str(tool_path), temp_file.name)
            temp_path = temp_file.name
        
        # Load module from temporary file
        spec = importlib.util.spec_from_file_location(tool_name, temp_path)
        if spec is None or spec.loader is None:
            os.unlink(temp_path)
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Clean up temp file
        os.unlink(temp_path)
        return module
    except Exception:
        return None

def load_plex_tool(tool_name):
    """Dynamically load Plex tool by copying to temp .py file."""
    try:
        tool_path = Path(__file__).parent.parent.parent / 'plex' / tool_name
        if not tool_path.exists():
            return None
            
        # Create temporary .py file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            shutil.copy2(str(tool_path), temp_file.name)
            temp_path = temp_file.name
        
        # Load module from temporary file
        spec = importlib.util.spec_from_file_location(tool_name, temp_path)
        if spec is None or spec.loader is None:
            os.unlink(temp_path)
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Clean up temp file
        os.unlink(temp_path)
        return module
    except Exception:
        return None

# Load tools dynamically
sabnzbd_module = load_sabnzbd_tool('sabnzbd_cleanup')
SABnzbdDetector = getattr(sabnzbd_module, 'SABnzbdDetector', None) if sabnzbd_module else None

plex_renamer_module = load_plex_tool('plex_movie_subdir_renamer')
PlexMovieSubdirRenamer = getattr(plex_renamer_module, 'PlexMovieSubdirRenamer', None) if plex_renamer_module else None

plex_dirs_module = load_plex_tool('plex_make_dirs')
PlexDirectoryCreator = getattr(plex_dirs_module, 'PlexDirectoryCreator', None) if plex_dirs_module else None

plex_seasons_module = load_plex_tool('plex_make_seasons')
SeasonOrganizer = getattr(plex_seasons_module, 'SeasonOrganizer', None) if plex_seasons_module else None

plex_batch_module = load_plex_tool('plex_make_all_seasons')
BatchSeasonOrganizer = getattr(plex_batch_module, 'SeasonOrganizer', None) if plex_batch_module else None

plex_extras_module = load_plex_tool('plex_move_movie_extras')
PlexMovieExtrasOrganizer = getattr(plex_extras_module, 'PlexMovieExtrasOrganizer', None) if plex_extras_module else None

@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestFileTypeValidation(MediaLibraryTestCase):
    """Test file type validation across all tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.sabnzbd_detector = SABnzbdDetector() if SABnzbdDetector else None
        self.plex_renamer = PlexMovieSubdirRenamer() if PlexMovieSubdirRenamer else None
        # Configure PlexDirectoryCreator to exclude image files (consistent with other tests)
        if PlexDirectoryCreator:
            exclude_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg']
            self.plex_creator = PlexDirectoryCreator(exclude_types=exclude_types)
        else:
            self.plex_creator = None
        self.season_organizer = SeasonOrganizer() if SeasonOrganizer else None
        self.batch_season_organizer = BatchSeasonOrganizer() if BatchSeasonOrganizer else None
        self.extras_organizer = PlexMovieExtrasOrganizer() if PlexMovieExtrasOrganizer else None
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_sabnzbd_detector_directory_analysis(self):
        """Test SABnzbd detector with directory analysis."""
        if not self.sabnzbd_detector:
            self.skipTest("SABnzbdDetector not available")
            
        # Use actual fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test that SABnzbd detector can analyze directories containing video files
        is_sabnzbd, score, indicators = self.sabnzbd_detector.analyze_directory(test_dir)
        
        # This should not be detected as SABnzbd since it's just video files without SABnzbd indicators
        self.assertFalse(is_sabnzbd, f"Directory with only video files should not be detected as SABnzbd")
        self.assertIsInstance(score, int, "Score should be an integer")
        self.assertIsInstance(indicators, list, "Indicators should be a list")
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_plex_renamer_video_extensions(self):
        """Test Plex renamer with video file fixtures."""
        if not self.plex_renamer:
            self.skipTest("PlexMovieSubdirRenamer not available")
            
        # Use actual fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test that Plex renamer recognizes fixture video files
        video_files = list(test_dir.glob("*.mp4")) + list(test_dir.glob("*.mkv")) + list(test_dir.glob("*.avi"))
        for video_file in video_files:
            self.assertTrue(self.plex_renamer.is_video_file(video_file), 
                          f"Plex renamer should recognize {video_file} as video file")
    
    @unittest.skipIf(PlexDirectoryCreator is None, "Plex tools not available")
    def test_plex_creator_file_types(self):
        """Test Plex directory creator with various file type fixtures."""
        if not self.plex_creator:
            self.skipTest("PlexDirectoryCreator not available")
            
        # Test with video files
        test_dir = self.copy_fixture('common/video_files')
        video_files = list(test_dir.glob("*.mp4")) + list(test_dir.glob("*.mkv")) + list(test_dir.glob("*.avi"))
        for video_file in video_files:
            file_path = test_dir / video_file
            self.assertTrue(self.plex_creator.should_process_file(file_path), 
                          f"Should process {video_file} by default")
        
        # Test with audio files
        test_dir = self.copy_fixture('common/audio_files')
        audio_files = list(test_dir.glob("*.mp3")) + list(test_dir.glob("*.flac"))
        for audio_file in audio_files:
            file_path = test_dir / audio_file
            self.assertTrue(self.plex_creator.should_process_file(file_path), 
                          f"Should process {audio_file} by default")
        
        # Test with image files - these should NOT be processed if image types are excluded
        test_dir = self.copy_fixture('common/image_files')
        image_files = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
        for image_file in image_files:
            file_path = test_dir / image_file
            # Image files should not be processed by default in Plex directory creator
            self.assertFalse(self.plex_creator.should_process_file(file_path), 
                           f"Should not process {image_file} - image files typically excluded from Plex processing")
        
        # Test with subtitle files - these are NOT included in default media types
        test_dir = self.copy_fixture('common/subtitle_files')
        subtitle_files = list(test_dir.glob("*.srt")) + list(test_dir.glob("*.vtt"))
        for subtitle_file in subtitle_files:
            file_path = test_dir / subtitle_file
            # Subtitle files are not in default media types for PlexDirectoryCreator
            self.assertFalse(self.plex_creator.should_process_file(file_path), 
                           f"Should not process {subtitle_file} - subtitle files not in default media types")
    
    @unittest.skipIf(SeasonOrganizer is None, "Plex tools not available")
    def test_season_organizer_video_extensions(self):
        """Test season organizer with video file fixtures."""
        if not self.season_organizer:
            self.skipTest("SeasonOrganizer not available")
            
        # Use actual fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test that season organizer recognizes fixture video files
        video_files = list(test_dir.glob("*.mp4")) + list(test_dir.glob("*.mkv")) + list(test_dir.glob("*.avi"))
        for video_file in video_files:
            self.assertTrue(self.season_organizer.is_video_file(test_dir / video_file), 
                          f"Season organizer should recognize {video_file} as video file")
    
    @unittest.skipIf(BatchSeasonOrganizer is None, "Plex tools not available")
    def test_batch_season_organizer_video_extensions(self):
        """Test batch season organizer with video file fixtures."""
        if not self.batch_season_organizer:
            self.skipTest("BatchSeasonOrganizer not available")
            
        # Use actual fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test that batch season organizer recognizes fixture video files
        video_files = list(test_dir.glob("*.mp4")) + list(test_dir.glob("*.mkv")) + list(test_dir.glob("*.avi"))
        for video_file in video_files:
            self.assertTrue(self.batch_season_organizer.is_video_file(test_dir / video_file), 
                          f"Batch season organizer should recognize {video_file} as video file")
    
    @unittest.skipIf(PlexMovieExtrasOrganizer is None, "Plex tools not available")
    def test_extras_organizer_video_extensions(self):
        """Test extras organizer with video file fixtures."""
        if not self.extras_organizer:
            self.skipTest("PlexMovieExtrasOrganizer not available")
            
        # Use actual fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test that extras organizer recognizes fixture video files
        video_files = list(test_dir.glob("*.mp4")) + list(test_dir.glob("*.mkv")) + list(test_dir.glob("*.avi"))
        for video_file in video_files:
            self.assertTrue(self.extras_organizer.is_video_file(video_file.name), 
                          f"Extras organizer should recognize {video_file.name} as video file")

if __name__ == '__main__':
    unittest.main()