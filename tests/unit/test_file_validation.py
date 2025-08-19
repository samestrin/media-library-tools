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

# Add directories to path so we can import the scripts
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'SABnzbd'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'plex'))

# Import validation functions from all tools with error handling
try:
    from sabnzbd_cleanup import SABnzbdDetector
except ImportError:
    SABnzbdDetector = None

try:
    from plex_movie_subdir_renamer import PlexMovieSubdirRenamer
except ImportError:
    PlexMovieSubdirRenamer = None

try:
    from plex_make_dirs import PlexDirectoryCreator
except ImportError:
    PlexDirectoryCreator = None

try:
    from plex_make_seasons import SeasonOrganizer
except ImportError:
    SeasonOrganizer = None

try:
    from plex_make_all_seasons import SeasonOrganizer as BatchSeasonOrganizer
except ImportError:
    BatchSeasonOrganizer = None

try:
    from plex_move_movie_extras import PlexMovieExtrasOrganizer
except ImportError:
    PlexMovieExtrasOrganizer = None

@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestFileTypeValidation(MediaLibraryTestCase):
    """Test file type validation across all tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.sabnzbd_detector = SABnzbdDetector() if SABnzbdDetector else None
        self.plex_renamer = PlexMovieSubdirRenamer() if PlexMovieSubdirRenamer else None
        self.plex_creator = PlexDirectoryCreator() if PlexDirectoryCreator else None
        self.season_organizer = SeasonOrganizer() if SeasonOrganizer else None
        self.batch_season_organizer = BatchSeasonOrganizer() if BatchSeasonOrganizer else None
        self.extras_organizer = PlexMovieExtrasOrganizer() if PlexMovieExtrasOrganizer else None
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_sabnzbd_detector_video_extensions(self):
        """Test SABnzbd detector with video file fixtures."""
        if not self.sabnzbd_detector:
            self.skipTest("SABnzbdDetector not available")
            
        # Use actual fixture files for testing
        test_dir = self.copy_fixture('common/video_files')
        
        # Test that SABnzbd detector recognizes fixture video files
        video_files = list(test_dir.glob("*.mp4")) + list(test_dir.glob("*.mkv")) + list(test_dir.glob("*.avi"))
        for video_file in video_files:
            # Most SABnzbd detectors should recognize video files by extension
            self.assertTrue(self.sabnzbd_detector.is_video_file(video_file), 
                          f"SABnzbd detector should recognize {video_file} as video file")
    
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
        
        # Test with image files
        test_dir = self.copy_fixture('common/image_files')
        image_files = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
        for image_file in image_files:
            file_path = test_dir / image_file
            self.assertTrue(self.plex_creator.should_process_file(file_path), 
                          f"Should process {image_file} by default")
        
        # Test with subtitle files
        test_dir = self.copy_fixture('common/subtitle_files')
        subtitle_files = list(test_dir.glob("*.srt")) + list(test_dir.glob("*.vtt"))
        for subtitle_file in subtitle_files:
            file_path = test_dir / subtitle_file
            self.assertTrue(self.plex_creator.should_process_file(file_path), 
                          f"Should process {subtitle_file} by default")
    
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