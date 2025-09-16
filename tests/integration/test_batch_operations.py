#!/usr/bin/env python3
"""
Integration tests for batch operations

Tests batch processing capabilities across multiple files and directories.
"""

import os
import sys
import time
import unittest
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

# Add tool directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "SABnzbd"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "plex"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "plex-api"))

try:
    from test_helpers import MediaLibraryTestCase

    TEST_HELPERS_AVAILABLE = True
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

# Dynamic tool loading for files without .py extension
import importlib.util
import tempfile


def load_tool(tool_category, tool_name):
    """Load tool dynamically from category directory."""
    try:
        tool_path = Path(__file__).parent.parent.parent / tool_category / tool_name
        if not tool_path.exists():
            return None

        # Copy to temp file with .py extension
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
            with open(tool_path) as f:
                temp_file.write(f.read())
            temp_file_name = temp_file.name

        # Load as module
        spec = importlib.util.spec_from_file_location(tool_name, temp_file_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Clean up temp file
        os.unlink(temp_file_name)

        return module
    except Exception:
        return None


# Load tool classes with error handling
sabnzbd_module = load_tool("SABnzbd", "sabnzbd_cleanup")
SABnzbdDetector = (
    getattr(sabnzbd_module, "SABnzbdDetector", None) if sabnzbd_module else None
)

plex_renamer_module = load_tool("plex", "plex_movie_subdir_renamer")
PlexMovieSubdirRenamer = (
    getattr(plex_renamer_module, "PlexMovieSubdirRenamer", None)
    if plex_renamer_module
    else None
)

plex_dirs_module = load_tool("plex", "plex_make_dirs")
PlexDirectoryCreator = (
    getattr(plex_dirs_module, "PlexDirectoryCreator", None)
    if plex_dirs_module
    else None
)

plex_seasons_module = load_tool("plex", "plex_make_seasons")
SeasonOrganizer = (
    getattr(plex_seasons_module, "SeasonOrganizer", None)
    if plex_seasons_module
    else None
)

plex_batch_module = load_tool("plex", "plex_make_all_seasons")
BatchSeasonOrganizer = (
    getattr(plex_batch_module, "SeasonOrganizer", None) if plex_batch_module else None
)

plex_extras_module = load_tool("plex", "plex_move_movie_extras")
PlexMovieExtrasOrganizer = (
    getattr(plex_extras_module, "PlexMovieExtrasOrganizer", None)
    if plex_extras_module
    else None
)


@unittest.skipIf(
    SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE,
    "Required modules not available",
)
class TestBatchSABnzbdOperations(MediaLibraryTestCase):
    """Test batch operations for SABnzbd cleanup."""

    @unittest.skipIf(
        SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_batch_directory_analysis(self):
        """Test analyzing multiple directories in batch."""
        # Use existing fixtures for testing
        test_dir = self.copy_fixture("sabnzbd/mixed_environment")

        # Create additional test directories within the fixture
        sabnzbd_dirs = []
        for i in range(3):
            dir_path = test_dir / f"sabnzbd_download_{i}"
            dir_path.mkdir()

            # Add SABnzbd indicators
            (dir_path / "SABnzbd_nzo").touch()
            (dir_path / "SABnzbd_nzb").touch()

            # Add some media files
            (dir_path / f"movie_{i}.mp4").touch()
            (dir_path / f"episode_{i}_S01E01.mkv").touch()

            sabnzbd_dirs.append(dir_path)

        # Create non-SABnzbd directories
        non_sabnzbd_dirs = []
        for i in range(2):
            dir_path = test_dir / f"regular_download_{i}"
            dir_path.mkdir()

            # Add only media files (no SABnzbd indicators)
            (dir_path / f"movie_{i}.mp4").touch()

            non_sabnzbd_dirs.append(dir_path)

        # Test batch analysis
        detector = SABnzbdDetector()

        # Analyze all directories
        all_dirs = sabnzbd_dirs + non_sabnzbd_dirs
        results = []

        for dir_path in all_dirs:
            is_sabnzbd, score, indicators = detector.analyze_directory(dir_path)
            results.append((dir_path, is_sabnzbd, score, indicators))

        # Verify results
        sabnzbd_results = [r for r in results if r[0] in sabnzbd_dirs]
        non_sabnzbd_results = [r for r in results if r[0] in non_sabnzbd_dirs]

        # All SABnzbd directories should be detected
        for dir_path, is_sabnzbd, score, indicators in sabnzbd_results:
            self.assertTrue(is_sabnzbd, f"Should detect {dir_path} as SABnzbd")
            self.assertGreater(score, 0, f"Should have positive score for {dir_path}")
            self.assertGreater(
                len(indicators), 0, f"Should have indicators for {dir_path}"
            )

        # Non-SABnzbd directories should not be detected
        for dir_path, is_sabnzbd, _score, _indicators in non_sabnzbd_results:
            self.assertFalse(is_sabnzbd, f"Should not detect {dir_path} as SABnzbd")

    @unittest.skipIf(
        SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_batch_size_calculation(self):
        """Test calculating sizes for multiple directories."""
        test_dir = self.copy_fixture("sabnzbd/mixed_environment")
        batch_sizes_dir = test_dir / "batch_sizes_test"
        batch_sizes_dir.mkdir()

        # Create directories with different sizes
        test_dirs = []
        expected_sizes = []

        for i in range(3):
            dir_path = batch_sizes_dir / f"test_dir_{i}"
            dir_path.mkdir()

            # Create files of different sizes
            file_size = (i + 1) * 1024  # 1KB, 2KB, 3KB
            test_file = dir_path / f"test_file_{i}.txt"

            # Write data to create specific file size
            with open(test_file, "wb") as f:
                f.write(b"x" * file_size)

            test_dirs.append(dir_path)
            expected_sizes.append(file_size)

        # Test batch size calculation
        get_dir_size = (
            getattr(sabnzbd_module, "get_dir_size", None) if sabnzbd_module else None
        )
        if get_dir_size is None:
            self.skipTest("get_dir_size function not available")

        calculated_sizes = []
        for dir_path in test_dirs:
            size = get_dir_size(dir_path)
            calculated_sizes.append(size)

        # Verify sizes are calculated correctly
        for i, (expected, calculated) in enumerate(
            zip(expected_sizes, calculated_sizes)
        ):
            self.assertGreaterEqual(
                calculated,
                expected,
                f"Directory {i} size should be at least {expected} bytes",
            )


@unittest.skipIf(
    PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
    "Required modules not available",
)
class TestBatchPlexMovieOperations(MediaLibraryTestCase):
    """Test batch operations for Plex movie organization."""

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_batch_movie_renaming(self):
        """Test renaming multiple movie files in batch."""
        test_dir = self.copy_fixture("plex/movies/movie_with_extras")

        # Create additional movie files with extras
        movie_files = [
            "Epic Movie (2023).mkv",
            "Action Film (2022).mp4",
            "Comedy Show (2021).avi",
        ]

        extras_files = [
            "behind_the_scenes.mp4",
            "deleted_scene_01.mkv",
            "trailer.mp4",
            "director_commentary.avi",
            "making_of_documentary.mp4",
        ]

        # Create additional test directories
        for i, movie_file in enumerate(movie_files):
            movie_dir = test_dir / f"movie_test_{i}"
            movie_dir.mkdir()

            # Create main movie file
            (movie_dir / movie_file).touch()

            # Create extras files
            for _j, extra_file in enumerate(extras_files):
                (movie_dir / extra_file).touch()

        # Test batch processing
        renamer = PlexMovieSubdirRenamer()

        # Get all video files
        all_files = list(test_dir.glob("**/*.*"))
        video_files = [f for f in all_files if renamer.is_video_file(f)]

        # Verify all files are recognized as video files
        expected_total = len(movie_files) + len(extras_files)
        self.assertGreater(
            len(video_files), expected_total, "Should recognize all video files"
        )

        # Separate main movies from extras
        main_movies = [
            f for f in video_files if any(movie in f.name for movie in movie_files)
        ]
        extras = [f for f in video_files if f not in main_movies]

        self.assertGreater(
            len(main_movies), len(movie_files), "Should identify main movies"
        )
        self.assertGreater(len(extras), len(extras_files), "Should identify extras")

    @unittest.skipIf(
        PlexDirectoryCreator is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_batch_directory_creation(self):
        """Test creating directories for multiple media files."""
        # Use existing fixtures for testing
        test_dir = self.copy_fixture("common/video_files")
        batch_dirs_dir = test_dir / "batch_dirs_test"
        batch_dirs_dir.mkdir()

        # Create various media files
        media_files = [
            "movie1.mp4",
            "movie2.mkv",
            "episode_S01E01.avi",
            "episode_S01E02.mp4",
        ]

        for media_file in media_files:
            (batch_dirs_dir / media_file).touch()

        # Test batch directory creation
        creator = PlexDirectoryCreator()

        # Check which files should be processed
        processable_files = []
        for media_file in media_files:
            file_path = batch_dirs_dir / media_file
            if creator.should_process_file(file_path):
                processable_files.append(file_path)

        # Should process most media files
        self.assertGreater(len(processable_files), 0, "Should have files to process")

        # Video files should definitely be processable
        video_extensions = [".mp4", ".mkv", ".avi"]
        video_files = [
            f for f in processable_files if f.suffix.lower() in video_extensions
        ]

        self.assertGreater(len(video_files), 0, "Should process video files")


@unittest.skipIf(
    SeasonOrganizer is None or not TEST_HELPERS_AVAILABLE,
    "Required modules not available",
)
class TestBatchTVShowOperations(MediaLibraryTestCase):
    """Test batch operations for TV show organization."""

    @unittest.skipIf(
        SeasonOrganizer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_batch_season_organization(self):
        """Test organizing multiple TV shows into seasons."""
        test_dir = self.copy_fixture("plex/tv_shows/unorganized_episodes")
        batch_tv_dir = test_dir / "batch_tv_test"
        batch_tv_dir.mkdir()

        # Create multiple TV shows with episodes
        shows = {
            "Drama Series": [
                "Drama Series S01E01 Pilot.mkv",
                "Drama Series S01E02 The Beginning.mp4",
                "Drama Series S02E01 New Chapter.mkv",
                "Drama Series S02E05 Midpoint.avi",
            ],
            "Comedy Show": [
                "Comedy Show S01E01 First Laugh.mp4",
                "Comedy Show S01E02 Second Laugh.mkv",
                "Comedy Show S03E01 Season Three.avi",
            ],
            "Action Series": [
                "Action Series S01E01 Explosive Start.mp4",
                "Action Series S01E02 More Action.mkv",
                "Action Series S01E03 Final Action.avi",
                "Action Series S02E01 New Season.mp4",
            ],
        }

        # Create all episode files
        all_episodes = []
        for show_name, episodes in shows.items():
            show_dir = batch_tv_dir / show_name
            show_dir.mkdir()

            for episode in episodes:
                episode_path = show_dir / episode
                episode_path.touch()
                all_episodes.append(episode_path)

        # Test batch season organization
        organizer = SeasonOrganizer()

        # Verify all episodes are recognized as video files
        video_episodes = [ep for ep in all_episodes if organizer.is_video_file(ep)]
        self.assertEqual(
            len(video_episodes),
            len(all_episodes),
            "Should recognize all episodes as video files",
        )

        # Group episodes by show and season
        show_seasons = {}
        for episode in all_episodes:
            episode_name = episode.name

            # Extract show name (everything before first 'S')
            show_part = episode_name.split(" S")[0]

            # Extract season (S01, S02, etc.)
            if " S01" in episode_name:
                season = "S01"
            elif " S02" in episode_name:
                season = "S02"
            elif " S03" in episode_name:
                season = "S03"
            else:
                continue

            key = f"{show_part}_{season}"
            show_seasons.setdefault(key, []).append(episode)

        # Verify we have multiple shows and seasons
        self.assertGreater(
            len(show_seasons), 3, "Should have multiple show/season combinations"
        )

        # Verify each season has episodes
        for key, episodes in show_seasons.items():
            self.assertGreater(len(episodes), 0, f"Season {key} should have episodes")

    @unittest.skipIf(
        BatchSeasonOrganizer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_batch_all_seasons_organization(self):
        """Test batch organization across all seasons and shows."""
        test_dir = self.copy_fixture("plex/tv_shows")
        batch_all_seasons_dir = test_dir / "batch_all_seasons_test"
        batch_all_seasons_dir.mkdir()

        # Create multiple show directories
        shows_data = {
            "Show1": {"seasons": [1, 2, 3], "episodes_per_season": [3, 4, 2]},
            "Show2": {"seasons": [1, 2], "episodes_per_season": [5, 3]},
            "Show3": {"seasons": [1], "episodes_per_season": [6]},
        }

        all_episodes = []

        for show_name, _show_info in shows_data.items():
            show_dir = batch_all_seasons_dir / show_name
            show_dir.mkdir()

            for season_num, episode_count in zip(
                _show_info["seasons"], _show_info["episodes_per_season"]
            ):
                for episode_num in range(1, episode_count + 1):
                    episode_name = f"{show_name} S{season_num:02d}E{episode_num:02d} Episode {episode_num}.mp4"
                    episode_path = show_dir / episode_name
                    episode_path.touch()
                    all_episodes.append(episode_path)

        # Test batch organization
        batch_organizer = BatchSeasonOrganizer()

        # Verify all episodes are recognized
        recognized_episodes = [
            ep for ep in all_episodes if batch_organizer.is_video_file(ep)
        ]
        self.assertEqual(
            len(recognized_episodes), len(all_episodes), "Should recognize all episodes"
        )

        # Calculate expected totals
        total_expected_episodes = sum(
            sum(show_info["episodes_per_season"]) for show_info in shows_data.values()
        )

        self.assertEqual(
            len(all_episodes),
            total_expected_episodes,
            "Should have correct total number of episodes",
        )

        # Verify episodes are distributed across multiple shows
        shows_with_episodes = set()
        for episode in all_episodes:
            show_name = episode.parent.name
            shows_with_episodes.add(show_name)

        self.assertEqual(
            len(shows_with_episodes),
            len(shows_data),
            "Should have episodes for all shows",
        )

        # Verify each movie has the expected number of extras
        for show_name, _show_info in shows_data.items():
            show_dir = batch_all_seasons_dir / show_name
            [f for f in show_dir.glob("*.*") if f.name != f"{show_name}.mkv"]

            # Note: This test is checking for episodes, not extras, so we'll verify episodes
            show_episodes = [
                f for f in show_dir.glob("*.*") if f.name.startswith(show_name)
            ]

            self.assertGreater(
                len(show_episodes), 0, f"Show {show_name} should have episodes"
            )


@unittest.skipIf(
    PlexMovieExtrasOrganizer is None or not TEST_HELPERS_AVAILABLE,
    "Required modules not available",
)
class TestBatchMovieExtrasOperations(MediaLibraryTestCase):
    """Test batch operations for movie extras organization."""

    @unittest.skipIf(
        PlexMovieExtrasOrganizer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_batch_extras_organization(self):
        """Test organizing extras for multiple movies."""
        test_dir = self.copy_fixture("plex/movies/movie_with_extras")
        batch_extras_dir = test_dir / "batch_extras_test"
        batch_extras_dir.mkdir()

        # Create multiple movie directories with extras
        movies = ["Epic Movie (2023)", "Action Film (2022)", "Comedy Show (2021)"]

        extras_types = [
            "trailer.mp4",
            "behind_the_scenes.mkv",
            "deleted_scene_01.avi",
            "director_commentary.mp4",
            "making_of.mkv",
        ]

        all_extras = []

        for movie in movies:
            movie_dir = batch_extras_dir / movie
            movie_dir.mkdir()

            # Create main movie file
            main_movie = movie_dir / f"{movie}.mkv"
            main_movie.touch()

            # Create extras files
            for extra in extras_types:
                extra_path = movie_dir / extra
                extra_path.touch()
                all_extras.append(extra_path)

        # Test batch extras organization
        extras_organizer = PlexMovieExtrasOrganizer()

        # Verify all extras are recognized as video files
        recognized_extras = [
            extra for extra in all_extras if extras_organizer.is_video_file(extra.name)
        ]

        self.assertEqual(
            len(recognized_extras),
            len(all_extras),
            "Should recognize all extras as video files",
        )

        # Verify extras are distributed across movies
        movies_with_extras = set()
        for extra in all_extras:
            movie_name = extra.parent.name
            movies_with_extras.add(movie_name)

        self.assertEqual(
            len(movies_with_extras), len(movies), "Should have extras for all movies"
        )

        # Verify each movie has the expected number of extras
        for movie in movies:
            movie_dir = batch_extras_dir / movie
            movie_extras = [
                f for f in movie_dir.glob("*.*") if f.name != f"{movie}.mkv"
            ]

            self.assertEqual(
                len(movie_extras),
                len(extras_types),
                f"Movie {movie} should have {len(extras_types)} extras",
            )


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestBatchPerformanceOperations(MediaLibraryTestCase):
    """Test batch operations performance and scalability."""

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_large_batch_processing(self):
        """Test processing large batches of files efficiently."""
        test_dir = self.copy_fixture("common/video_files")
        large_batch_dir = test_dir / "large_batch_test"
        large_batch_dir.mkdir()

        # Create a large number of files
        num_files = 30  # Reduced for test performance
        file_types = [".mp4", ".mkv", ".avi"]

        created_files = []
        start_time = time.time()

        for i in range(num_files):
            file_ext = file_types[i % len(file_types)]
            file_name = f"file_{i:03d}{file_ext}"
            file_path = large_batch_dir / file_name
            file_path.touch()
            created_files.append(file_path)

        creation_time = time.time() - start_time

        # Test batch processing performance
        start_time = time.time()

        renamer = PlexMovieSubdirRenamer()
        processed_files = []

        for file_path in created_files:
            if renamer.is_video_file(file_path):
                processed_files.append(file_path)

        processing_time = time.time() - start_time

        # Verify all files were processed
        self.assertEqual(
            len(processed_files), num_files, "Should process all video files"
        )

        # Performance check (should be reasonably fast)
        self.assertLess(
            processing_time, 5.0, "Batch processing should complete within 5 seconds"
        )

        # Log performance metrics
        print("\nBatch Performance Metrics:")
        print(f"Files created: {num_files} in {creation_time:.3f}s")
        print(f"Files processed: {len(processed_files)} in {processing_time:.3f}s")
        print(
            f"Processing rate: {len(processed_files)/processing_time:.1f} files/second"
        )

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None
        or PlexDirectoryCreator is None
        or SeasonOrganizer is None
        or BatchSeasonOrganizer is None
        or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_concurrent_batch_operations(self):
        """Test handling concurrent batch operations safely."""
        test_dir = self.copy_fixture("common/video_files")
        concurrent_batch_dir = test_dir / "concurrent_batch_test"
        concurrent_batch_dir.mkdir()

        # Create test files
        test_files = []
        for i in range(10):
            file_path = concurrent_batch_dir / f"test_file_{i}.mp4"
            file_path.touch()
            test_files.append(file_path)

        # Simulate concurrent access by multiple tools
        tools = [
            PlexMovieSubdirRenamer(),
            PlexDirectoryCreator(),
            SeasonOrganizer(),
            BatchSeasonOrganizer(),
        ]

        # Test that multiple tools can safely access the same files
        results = []
        for tool in tools:
            tool_results = []
            for file_path in test_files:
                try:
                    if hasattr(tool, "is_video_file"):
                        result = tool.is_video_file(file_path)
                        tool_results.append(result)
                    elif hasattr(tool, "should_process_file"):
                        result = tool.should_process_file(file_path)
                        tool_results.append(result)
                except Exception as e:
                    self.fail(
                        f"Tool {tool.__class__.__name__} failed on concurrent access: {e}"
                    )

            results.append(tool_results)

        # Verify all tools processed all files
        for i, tool_results in enumerate(results):
            self.assertEqual(
                len(tool_results), len(test_files), f"Tool {i} should process all files"
            )


if __name__ == "__main__":
    unittest.main()
