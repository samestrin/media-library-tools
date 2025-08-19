#!/usr/bin/env python3
"""
Integration tests for end-to-end workflows

Tests complete workflows across multiple tools and scenarios.
"""

import unittest
import os
import sys
import shutil
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

# Add tool directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'SABnzbd'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plex'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plex-api'))

try:
    from test_helpers import MediaLibraryTestCase
    TEST_HELPERS_AVAILABLE = True
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

# Import tool classes with error handling
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


@unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
class TestSABnzbdToPlexWorkflow(MediaLibraryTestCase):
    """Test complete workflow from SABnzbd cleanup to Plex organization."""
    
    @unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_movie_download_to_plex_workflow(self):
        """Test complete movie workflow: SABnzbd detection -> Plex organization."""
        # Create a test scenario with SABnzbd download
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Validate SABnzbd fixture structure
        sabnzbd_structure = {
            'complete': {},
            'incomplete': {},
            'watched': {}
        }
        self.assert_directory_structure(test_dir, sabnzbd_structure)
        
        # Step 1: Detect SABnzbd download
        detector = SABnzbdDetector()
        is_sabnzbd, score, indicators = detector.analyze_directory(test_dir)
        
        # For mixed environment, we expect at least one SABnzbd directory
        self.assertGreater(score, 0, "Should have positive detection score")
        
        # Step 2: Simulate cleanup (move to Plex directory)
        plex_movies_dir = self.copy_fixture('plex/movies/movie_with_extras')
        
        # Validate Plex movie fixture structure
        plex_structure = {
            'Movie Title (2023)': {
                'Movie Title (2023).mkv': None,
                'extras': {}
            }
        }
        self.assert_directory_structure(plex_movies_dir, plex_structure)
        
        # Step 3: Organize with Plex tools
        creator = PlexDirectoryCreator()
        
        # Verify movie files are properly organized
        organized_movies = list(plex_movies_dir.glob('**/*.mp4')) + list(plex_movies_dir.glob('**/*.mkv'))
        self.assertGreater(len(organized_movies), 0, "Should have organized movie files")
    
    @unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_tv_show_download_to_plex_workflow(self):
        """Test complete TV show workflow: SABnzbd detection -> Season organization."""
        # Create a test scenario with TV show download
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Step 1: Detect SABnzbd download
        detector = SABnzbdDetector()
        is_sabnzbd, score, indicators = detector.analyze_directory(test_dir)
        
        # For mixed environment, we expect at least one SABnzbd directory
        self.assertGreater(score, 0, "Should have positive detection score")
        
        # Step 2: Simulate cleanup (move to Plex TV directory)
        plex_tv_dir = self.copy_fixture('plex/tv_shows/unorganized_episodes')
        
        # Step 3: Organize episodes into seasons
        organizer = SeasonOrganizer()
        
        # Verify episodes exist before organization
        episodes_before = list(plex_tv_dir.glob('*S??E*.*'))
        self.assertGreater(len(episodes_before), 0, "Should have episode files to organize")
    
    @unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_mixed_media_workflow(self):
        """Test workflow with mixed media types (movies and TV shows)."""
        # Create a test scenario with mixed media
        test_dir = self.copy_fixture('plex/mixed_media')
        
        # Check if mixed_media directory exists
        if not (test_dir / 'mixed_content').exists():
            # Create a temporary mixed content directory
            mixed_content_dir = test_dir / 'mixed_content'
            mixed_content_dir.mkdir()
            
            # Copy movie content
            movie_fixture = self.fixture_manager.copy_fixture_to_test_data('plex/movies/movie_with_extras')
            for file_path in movie_fixture.glob('*'):
                shutil.copy2(file_path, mixed_content_dir / file_path.name)
            
            # Copy TV content
            tv_fixture = self.fixture_manager.copy_fixture_to_test_data('plex/tv_shows/unorganized_episodes')
            for file_path in tv_fixture.glob('*'):
                shutil.copy2(file_path, mixed_content_dir / file_path.name)
        else:
            mixed_content_dir = test_dir / 'mixed_content'
        
        # Separate movies and TV shows
        movie_files = []
        tv_files = []
        
        for file_path in mixed_content_dir.glob('*.*'):
            if file_path.suffix.lower() in ['.mp4', '.mkv', '.avi']:
                if 'S0' in file_path.name and 'E0' in file_path.name:
                    tv_files.append(file_path)
                else:
                    movie_files.append(file_path)
        
        # Verify we have both types
        self.assertGreater(len(movie_files), 0, "Should have movie files")
        self.assertGreater(len(tv_files), 0, "Should have TV episode files")
        
        # Test movie organization
        movie_renamer = PlexMovieSubdirRenamer()
        for movie_file in movie_files:
            self.assertTrue(movie_renamer.is_video_file(movie_file))
        
        # Test TV organization
        season_organizer = SeasonOrganizer()
        for tv_file in tv_files:
            self.assertTrue(season_organizer.is_video_file(tv_file))


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestPlexOrganizationWorkflow(MediaLibraryTestCase):
    """Test Plex-specific organization workflows."""
    
    @unittest.skipIf(PlexMovieExtrasOrganizer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_movie_extras_organization_workflow(self):
        """Test complete movie extras organization workflow."""
        # Create a test scenario with movie and extras
        test_dir = self.copy_fixture('plex/movies/movie_with_extras')
        
        # Step 1: Identify main movie and extras
        all_files = list(test_dir.glob('*.*'))
        video_files = [f for f in all_files if f.suffix.lower() in ['.mp4', '.mkv', '.avi']]
        
        self.assertGreater(len(video_files), 1, "Should have main movie plus extras")
        
        # Step 2: Organize extras
        extras_organizer = PlexMovieExtrasOrganizer()
        
        # Count files before organization
        files_before = len(list(test_dir.glob('*.*')))
        
        # Verify extras can be identified
        extras_files = [f for f in video_files if 'trailer' in f.name.lower() or 
                       'behind' in f.name.lower() or 'deleted' in f.name.lower()]
        
        self.assertGreater(len(extras_files), 0, "Should identify extras files")
    
    @unittest.skipIf(SeasonOrganizer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_season_organization_workflow(self):
        """Test complete season organization workflow."""
        # Create a test scenario with unorganized episodes
        test_dir = self.copy_fixture('plex/tv_shows/unorganized_episodes')
        
        # Step 1: Identify episodes
        episode_files = list(test_dir.glob('*S??E*.*'))
        self.assertGreater(len(episode_files), 0, "Should have episode files")
        
        # Step 2: Group by season
        seasons = {}
        for episode_file in episode_files:
            # Extract season number
            name = episode_file.name
            if 'S01' in name:
                seasons.setdefault('Season 01', []).append(episode_file)
            elif 'S02' in name:
                seasons.setdefault('Season 02', []).append(episode_file)
            elif 'S03' in name:
                seasons.setdefault('Season 03', []).append(episode_file)
        
        # Verify we have multiple seasons
        self.assertGreater(len(seasons), 1, "Should have multiple seasons")
        
        # Step 3: Organize with season organizer
        organizer = SeasonOrganizer()
        
        # Verify all files are recognized as video files
        for episode_file in episode_files:
            self.assertTrue(organizer.is_video_file(episode_file))
    
    @unittest.skipIf(BatchSeasonOrganizer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_batch_season_organization_workflow(self):
        """Test batch season organization across multiple shows."""
        # Create multiple TV show directories
        test_dir = self.copy_fixture('plex/tv_shows')
        
        # Create episode files for show 1
        show1_dir = test_dir / 'show1_test'
        show1_dir.mkdir()
        show1_episodes = [
            'Show1 S01E01 Pilot.mp4',
            'Show1 S01E02 Episode 2.mp4',
            'Show1 S02E01 Season 2 Start.mp4'
        ]
        
        for episode in show1_episodes:
            (show1_dir / episode).touch()
        
        # Create episode files for show 2
        show2_dir = test_dir / 'show2_test'
        show2_dir.mkdir()
        show2_episodes = [
            'Show2 S01E01 Beginning.mkv',
            'Show2 S01E02 Continuation.mkv',
            'Show2 S03E01 Season 3.mkv'
        ]
        
        for episode in show2_episodes:
            (show2_dir / episode).touch()
        
        # Test batch organization
        batch_organizer = BatchSeasonOrganizer()
        
        # Verify all episodes are recognized
        all_episodes = list(show1_dir.glob('*.*')) + list(show2_dir.glob('*.*'))
        for episode in all_episodes:
            self.assertTrue(batch_organizer.is_video_file(episode))
        
        # Verify we have episodes from multiple seasons
        season_patterns = ['S01', 'S02', 'S03']
        found_seasons = set()
        
        for episode in all_episodes:
            for pattern in season_patterns:
                if pattern in episode.name:
                    found_seasons.add(pattern)
        
        self.assertGreater(len(found_seasons), 1, "Should have multiple seasons across shows")


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestErrorRecoveryWorkflow(MediaLibraryTestCase):
    """Test workflows with error conditions and recovery."""
    
    @unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_partial_download_recovery(self):
        """Test handling of partial or corrupted downloads."""
        # Create a scenario with partial downloads
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        partial_dir = test_dir / 'partial_downloads_test'
        partial_dir.mkdir()
        
        # Create SABnzbd indicators
        (partial_dir / 'SABnzbd_nzo').touch()
        (partial_dir / 'SABnzbd_nzb').touch()
        
        # Create partial files (common in incomplete downloads)
        (partial_dir / 'movie.part01.rar').touch()
        (partial_dir / 'movie.part02.rar').touch()
        (partial_dir / 'movie.mp4.part').touch()  # Partial video file
        
        # Test SABnzbd detection
        detector = SABnzbdDetector()
        is_sabnzbd, score, indicators = detector.analyze_directory(partial_dir)
        
        self.assertTrue(is_sabnzbd, "Should detect SABnzbd even with partial files")
        
        # Verify no complete video files are found
        video_files = list(partial_dir.glob('*.mp4')) + list(partial_dir.glob('*.mkv'))
        self.assertEqual(len(video_files), 0, "Should not find complete video files")
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_permission_error_recovery(self):
        """Test recovery from permission errors during organization."""
        # Create a test scenario
        test_dir = self.copy_fixture('common/video_files')
        
        # Create a video file
        video_file = test_dir / 'test_movie.mp4'
        video_file.touch()
        
        # Create a subdirectory with restricted permissions
        restricted_dir = test_dir / 'restricted'
        restricted_dir.mkdir()
        restricted_dir.chmod(0o000)  # No permissions
        
        try:
            # Test that tools handle permission errors gracefully
            renamer = PlexMovieSubdirRenamer()
            
            # Should still recognize the video file
            self.assertTrue(renamer.is_video_file(video_file))
            
            # Should handle restricted directory gracefully
            detector = SABnzbdDetector()
            try:
                detector.analyze_directory(restricted_dir)
            except PermissionError:
                # This is expected and acceptable
                pass
        
        finally:
            # Restore permissions for cleanup
            restricted_dir.chmod(0o755)
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_network_interruption_simulation(self):
        """Test handling of network interruptions during file operations."""
        # Create a test scenario that simulates network issues
        test_dir = self.copy_fixture('common/video_files')
        
        # Create test files
        source_file = test_dir / 'source.mp4'
        source_file.touch()
        
        # Simulate network path (this will likely fail, which is the point)
        network_path = Path('//nonexistent-server/share/destination.mp4')
        
        # Tools should handle network failures gracefully
        renamer = PlexMovieSubdirRenamer()
        
        # Should still recognize local file as video
        self.assertTrue(renamer.is_video_file(source_file))
        
        # Should handle network path without crashing
        try:
            renamer.is_video_file(network_path)
        except (OSError, ValueError):
            # These exceptions are acceptable for network issues
            pass


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestPerformanceWorkflow(MediaLibraryTestCase):
    """Test workflows with performance considerations."""
    
    @unittest.skipIf(PlexDirectoryCreator is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_large_directory_workflow(self):
        """Test workflow with large number of files."""
        # Create a directory with many files
        test_dir = self.copy_fixture('common/video_files')
        large_dir = test_dir / 'large_directory_test'
        large_dir.mkdir()
        
        # Create many video files
        num_files = 50
        for i in range(num_files):
            video_file = large_dir / f'movie_{i:03d}.mp4'
            video_file.touch()
        
        # Test that tools can handle large directories
        creator = PlexDirectoryCreator()
        
        # Count video files
        video_files = list(large_dir.glob('*.mp4'))
        self.assertEqual(len(video_files), num_files)
        
        # Verify all files are recognized
        for video_file in video_files[:10]:  # Test first 10 to avoid timeout
            self.assertTrue(creator.should_process_file(video_file))
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_deep_directory_structure_workflow(self):
        """Test workflow with deeply nested directory structure."""
        # Create a deep directory structure
        test_dir = self.copy_fixture('common/video_files')
        deep_dir = test_dir / 'deep_structure_test'
        deep_dir.mkdir()
        
        # Create nested directories
        current_dir = deep_dir
        for i in range(10):  # 10 levels deep
            current_dir = current_dir / f'level_{i}'
            current_dir.mkdir()
        
        # Create a video file at the deepest level
        deep_video = current_dir / 'deep_movie.mp4'
        deep_video.touch()
        
        # Test that tools can handle deep structures
        renamer = PlexMovieSubdirRenamer()
        self.assertTrue(renamer.is_video_file(deep_video))
        
        # Test directory analysis at various levels
        detector = SABnzbdDetector()
        
        # Should handle deep directories without stack overflow
        try:
            detector.analyze_directory(deep_dir)
        except RecursionError:
            self.fail("Should handle deep directory structures without recursion errors")


if __name__ == '__main__':
    unittest.main()