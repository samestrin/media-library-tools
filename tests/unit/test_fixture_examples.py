#!/usr/bin/env python3
"""
Example Tests Using the Fixture System

Demonstrates how to use the fixture system for testing media library tools.
Provides examples of different testing patterns and fixture usage.
"""

import sys
import unittest
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

# Try to import test helpers, handle import errors gracefully
try:
    from test_helpers import (
        MediaLibraryTestCase,
        assert_plex_naming_convention,
        create_mock_args,
        create_plex_movie_fixture,
        create_plex_tv_fixture,
        create_sabnzbd_fixture,
    )
except ImportError:
    # Fallback if test_helpers is not available
    MediaLibraryTestCase = unittest.TestCase
    create_mock_args = None
    create_sabnzbd_fixture = None
    create_plex_movie_fixture = None
    create_plex_tv_fixture = None
    assert_plex_naming_convention = None


class TestFixtureExamples(MediaLibraryTestCase):
    """Example tests demonstrating fixture usage patterns."""

    @unittest.skipIf(
        MediaLibraryTestCase is unittest.TestCase, "Test helpers not available"
    )
    def test_sabnzbd_mixed_environment_fixture(self):
        """Test using a pre-built SABnzbd mixed environment fixture."""
        # Copy the mixed environment fixture
        test_dir = self.copy_fixture("sabnzbd/mixed_environment")

        # Verify the fixture structure
        self.assert_dir_exists(test_dir / "download1")
        self.assert_dir_exists(test_dir / "download2")

        # Check SABnzbd indicators
        self.assert_file_exists(test_dir / "download1" / "SABnzbd_nzo")
        self.assert_file_exists(test_dir / "download1" / "SABnzbd_nzb")

        # Check BitTorrent indicators
        self.assert_file_exists(test_dir / "download2" / ".torrent")

        # Check media files
        self.assert_file_exists(test_dir / "download1" / "sample.movie.2023.mkv")
        self.assert_file_exists(test_dir / "download2" / "Another.Movie.2023.mp4")

        # Verify video file detection
        self.assert_video_file(test_dir / "download1" / "sample.movie.2023.mkv")
        self.assert_video_file(test_dir / "download2" / "Another.Movie.2023.mp4")

    @unittest.skipIf(
        MediaLibraryTestCase is unittest.TestCase, "Test helpers not available"
    )
    def test_plex_movie_extras_fixture(self):
        """Test using a Plex movie with extras fixture."""
        # Copy the movie with extras fixture
        test_dir = self.copy_fixture("plex/movies/movie_with_extras")

        # Verify main movie file
        main_movie = test_dir / "Epic Movie (2023).mkv"
        self.assert_file_exists(main_movie)
        self.assert_video_file(main_movie)

        # Verify extras files that need renaming
        extras_files = [
            "behind_the_scenes.mp4",
            "deleted_scene_01.mkv",
            "trailer.mp4",
            "director_interview.avi",
        ]

        for extra_file in extras_files:
            self.assert_file_exists(test_dir / extra_file)
            self.assert_video_file(test_dir / extra_file)

        # Count total video files
        self.assert_file_count(
            test_dir, 2, "*.mp4"
        )  # behind_the_scenes.mp4, trailer.mp4
        self.assert_file_count(
            test_dir, 2, "*.mkv"
        )  # Epic Movie (2023).mkv, deleted_scene_01.mkv
        self.assert_file_count(test_dir, 1, "*.avi")  # director_interview.avi

    @unittest.skipIf(
        MediaLibraryTestCase is unittest.TestCase, "Test helpers not available"
    )
    def test_plex_tv_unorganized_episodes_fixture(self):
        """Test using unorganized TV episodes fixture."""
        # Copy the unorganized episodes fixture
        test_dir = self.copy_fixture("plex/tv_shows/unorganized_episodes")

        # Verify episode files exist in root directory
        episodes = [
            "Drama Series S01E01 Pilot.mkv",
            "Drama Series S01E02 The Beginning.mp4",
            "Drama Series S02E01 New Chapter.mkv",
            "Drama Series S02E05 Midpoint.avi",
            "Drama Series S03E01 Fresh Start.mp4",
        ]

        for episode in episodes:
            episode_path = test_dir / episode
            self.assert_file_exists(episode_path)
            self.assert_video_file(episode_path)

        # Verify no season directories exist yet
        season_dirs = ["Season 01", "Season 02", "Season 03"]
        for season_dir in season_dirs:
            self.assert_dir_not_exists(test_dir / season_dir)

        # Count episodes by season (for organization testing)
        s01_episodes = list(self.get_file_list(test_dir, "*S01E*"))
        s02_episodes = list(self.get_file_list(test_dir, "*S02E*"))
        s03_episodes = list(self.get_file_list(test_dir, "*S03E*"))

        self.assertEqual(len(s01_episodes), 2)
        self.assertEqual(len(s02_episodes), 2)
        self.assertEqual(len(s03_episodes), 1)

    @unittest.skipIf(create_sabnzbd_fixture is None, "Test helpers not available")
    def test_dynamic_sabnzbd_fixture_creation(self):
        """Test creating a dynamic SABnzbd fixture."""
        # Create a temporary directory for the fixture
        temp_dir = self.fixture_manager.test_data_dir / "dynamic_sabnzbd"
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.test_dirs.append(temp_dir)

        # Create a mixed SABnzbd scenario
        create_sabnzbd_fixture(temp_dir, "mixed")

        # Verify the created structure
        self.assert_dir_exists(temp_dir / "sabnzbd_download")
        self.assert_dir_exists(temp_dir / "bittorrent_download")

        # Check indicators were created
        self.assert_file_exists(temp_dir / "sabnzbd_download" / "SABnzbd_nzo")
        self.assert_file_exists(temp_dir / "bittorrent_download" / ".torrent")

    @unittest.skipIf(create_plex_movie_fixture is None, "Test helpers not available")
    def test_dynamic_plex_movie_fixture_creation(self):
        """Test creating a dynamic Plex movie fixture."""
        # Create a temporary directory for the fixture
        temp_dir = self.fixture_manager.test_data_dir / "dynamic_movie"
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.test_dirs.append(temp_dir)

        # Create a movie fixture with extras
        create_plex_movie_fixture(temp_dir, with_extras=True)

        # Verify the created structure
        movie_files = self.get_file_list(temp_dir, "*.mp4")
        self.assertGreater(len(movie_files), 0)

        # Check for extras directories
        self.assert_dir_exists(temp_dir / "Featurettes")
        self.assert_dir_exists(temp_dir / "Extras")

    @unittest.skipIf(create_plex_tv_fixture is None, "Test helpers not available")
    def test_dynamic_plex_tv_fixture_creation(self):
        """Test creating a dynamic Plex TV fixture."""
        # Create a temporary directory for the fixture
        temp_dir = self.fixture_manager.test_data_dir / "dynamic_tv"
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.test_dirs.append(temp_dir)

        # Create a TV show fixture
        create_plex_tv_fixture(temp_dir, num_seasons=2, episodes_per_season=3)

        # Verify the created episodes
        episode_files = self.get_file_list(temp_dir, "*.mp4")
        self.assertEqual(len(episode_files), 6)  # 2 seasons * 3 episodes

        # Check episode naming pattern
        for episode_file in episode_files:
            self.assertTrue(assert_plex_naming_convention(episode_file, "tv_episode"))

    @unittest.skipIf(
        MediaLibraryTestCase is unittest.TestCase, "Test helpers not available"
    )
    def test_common_media_files_fixture(self):
        """Test using common media files fixture."""
        # Copy common video files
        test_dir = self.copy_fixture("common/video_files")

        # Verify different video formats
        video_formats = ["sample.mp4", "sample.mkv", "sample.avi"]
        for video_file in video_formats:
            file_path = test_dir / video_file
            self.assert_file_exists(file_path)
            self.assert_video_file(file_path)

        # Test audio files
        audio_dir = self.copy_fixture("common/audio_files")
        audio_formats = ["sample.mp3", "sample.flac"]
        for audio_file in audio_formats:
            self.assert_file_exists(audio_dir / audio_file)

        # Test subtitle files
        subtitle_dir = self.copy_fixture("common/subtitle_files")
        subtitle_formats = ["sample.srt", "sample.vtt"]
        for subtitle_file in subtitle_formats:
            self.assert_file_exists(subtitle_dir / subtitle_file)

    @unittest.skipIf(
        MediaLibraryTestCase is unittest.TestCase, "Test helpers not available"
    )
    def test_fixture_structure_validation(self):
        """Test fixture structure validation."""
        # Define expected structure
        expected_structure = {
            "Movie (2023).mkv": "file",
            "extras": {"trailer.mp4": "file", "behind_scenes.mp4": "file"},
        }

        # Create temporary fixture
        test_dir = self.create_temp_fixture(expected_structure)

        # Validate the structure was created correctly
        self.fixture_manager.assert_directory_structure(test_dir, expected_structure)

        # Verify specific files
        self.assert_file_exists(test_dir / "Movie (2023).mkv")
        self.assert_dir_exists(test_dir / "extras")
        self.assert_file_exists(test_dir / "extras" / "trailer.mp4")
        self.assert_file_exists(test_dir / "extras" / "behind_scenes.mp4")

    @unittest.skipIf(create_mock_args is None, "Test helpers not available")
    def test_mock_args_creation(self):
        """Test creating mock command line arguments."""
        # Create mock args with defaults
        args = create_mock_args()
        self.assertFalse(args.verbose)
        self.assertFalse(args.debug)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.path, ".")

        # Create mock args with custom values
        custom_args = create_mock_args(
            verbose=True, debug=True, path="/custom/path", delete=True
        )
        self.assertTrue(custom_args.verbose)
        self.assertTrue(custom_args.debug)
        self.assertTrue(custom_args.delete)
        self.assertEqual(custom_args.path, "/custom/path")

    @unittest.skipIf(
        MediaLibraryTestCase is unittest.TestCase, "Test helpers not available"
    )
    def test_plex_api_fixtures(self):
        """Test using Plex API response fixtures."""
        # Test server response fixtures
        server_dir = self.copy_fixture("plex_api/server_responses")

        # Validate server response files
        self.assert_file_exists(server_dir / "server_info.json")
        self.assert_file_exists(server_dir / "library_sections.json")

        # Test episode metadata fixtures
        metadata_dir = self.copy_fixture("plex_api/episode_metadata")
        self.assert_file_exists(metadata_dir / "show_metadata.json")

        # Verify JSON structure validation
        import json

        with open(server_dir / "server_info.json") as f:
            server_data = json.load(f)
            self.assertIn("MediaContainer", server_data)

    @unittest.skipIf(
        MediaLibraryTestCase is unittest.TestCase, "Test helpers not available"
    )
    def test_edge_case_fixtures(self):
        """Test using edge case fixtures for error scenarios."""
        # Test SABnzbd edge cases
        edge_dir = self.copy_fixture("sabnzbd/edge_cases")

        # Verify edge case directory exists
        self.assert_dir_exists(edge_dir)

        # Test mixed downloads scenario
        mixed_dir = self.copy_fixture("sabnzbd/mixed_downloads")
        self.assert_dir_exists(mixed_dir)


class TestFixtureManagerDirectly(unittest.TestCase):
    """Test the FixtureManager class directly."""

    def setUp(self):
        """Set up test case."""
        try:
            from fixture_manager import FixtureManager
        except ImportError:
            # Skip if fixture_manager is not available
            self.skipTest("FixtureManager not available")

        self.fixture_manager = FixtureManager()
        self.test_dirs = []

    def tearDown(self):
        """Clean up test data."""
        for test_dir in self.test_dirs:
            self.fixture_manager.cleanup_test_data(test_dir)

    def test_fixture_manager_initialization(self):
        """Test FixtureManager initialization."""
        self.assertIsNotNone(self.fixture_manager.fixtures_dir)
        self.assertIsNotNone(self.fixture_manager.test_data_dir)
        self.assertTrue(self.fixture_manager.fixtures_dir.exists())

    def test_copy_fixture_to_test_data(self):
        """Test copying fixture to test data directory."""
        # Copy a fixture
        test_dir = self.fixture_manager.copy_fixture_to_test_data("common/video_files")
        self.test_dirs.append(test_dir)

        # Verify the copy was successful
        self.assertTrue(test_dir.exists())
        self.assertTrue((test_dir / "sample.mp4").exists())
        self.assertTrue((test_dir / "sample.mkv").exists())
        self.assertTrue((test_dir / "sample.avi").exists())

    def test_create_temp_fixture(self):
        """Test creating temporary fixture from structure."""
        structure = {"test_file.txt": "file", "test_dir": {"nested_file.txt": "file"}}

        test_dir = self.fixture_manager.create_temp_fixture(structure)
        self.test_dirs.append(test_dir)

        # Verify the structure was created
        self.assertTrue(test_dir.exists())
        self.assertTrue((test_dir / "test_file.txt").exists())
        self.assertTrue((test_dir / "test_dir").exists())
        self.assertTrue((test_dir / "test_dir" / "nested_file.txt").exists())

    def test_create_video_files(self):
        """Test creating video files with specific names."""
        test_dir = self.fixture_manager.test_data_dir / "video_test"
        test_dir.mkdir(parents=True, exist_ok=True)
        self.test_dirs.append(test_dir)

        video_files = ["movie1.mp4", "movie2.mkv", "episode.avi"]
        self.fixture_manager.create_video_files(test_dir, video_files)

        # Verify files were created
        for video_file in video_files:
            file_path = test_dir / video_file
            self.assertTrue(file_path.exists())
            self.assertTrue(file_path.is_file())


if __name__ == "__main__":
    unittest.main()
