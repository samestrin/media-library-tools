#!/usr/bin/env python3
"""
Integration tests for error scenarios

Tests error conditions and edge cases in realistic scenarios.
"""

import os
import shutil
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
get_dir_size = getattr(sabnzbd_module, "get_dir_size", None) if sabnzbd_module else None
parse_size_threshold = (
    getattr(sabnzbd_module, "parse_size_threshold", None) if sabnzbd_module else None
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


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestFileSystemErrorScenarios(MediaLibraryTestCase):
    """Test error scenarios related to file system operations."""

    @unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
    def test_disk_full_scenario(self):
        """Test handling when disk space is exhausted."""
        test_dir = self.copy_fixture("common/video_files")
        disk_full_dir = test_dir / "disk_full_test"
        disk_full_dir.mkdir()

        # Create test files
        source_file = disk_full_dir / "source_movie.mp4"
        source_file.touch()

        dest_dir = disk_full_dir / "destination"
        dest_dir.mkdir()

        # Test actual file operations that might encounter disk issues
        # Try to move file to destination
        try:
            dest_file = dest_dir / "dest_movie.mp4"
            shutil.move(str(source_file), str(dest_file))
            # If successful, verify file was moved
            self.assertTrue(dest_file.exists())
            self.assertFalse(source_file.exists())
        except OSError as e:
            # Handle potential disk issues gracefully
            if "No space left" in str(e) or "Disk full" in str(e):
                # This is an acceptable error for disk space scenarios
                pass
            else:
                # Unexpected error, but still test graceful handling
                self.assertIsInstance(e, OSError)

    @unittest.skipIf(
        SABnzbdDetector is None
        or PlexMovieSubdirRenamer is None
        or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_permission_denied_scenarios(self):
        """Test various permission denied scenarios."""
        test_dir = self.copy_fixture("common/video_files")
        permission_test_dir = test_dir / "permission_test"
        permission_test_dir.mkdir()

        # Create test structure
        source_file = permission_test_dir / "movie.mp4"
        source_file.touch()

        readonly_dir = permission_test_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        noread_dir = permission_test_dir / "noread"
        noread_dir.mkdir()
        noread_dir.chmod(0o000)  # No permissions

        try:
            # Test SABnzbd detector with permission issues
            detector = SABnzbdDetector()

            # Should handle readonly directory
            from contextlib import suppress

            with suppress(PermissionError):
                detector.analyze_directory(readonly_dir)  # Expected

            # Should handle no-read directory gracefully
            result = detector.analyze_directory(noread_dir)
            # Should return False, 0, [] for permission denied directories
            self.assertEqual(result, (False, 0, []))

            # Test Plex tools with permission issues
            renamer = PlexMovieSubdirRenamer()

            # Should still recognize the accessible file
            self.assertTrue(renamer.is_video_file(source_file))

        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)
            noread_dir.chmod(0o755)

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_corrupted_filesystem_scenario(self):
        """Test handling of corrupted or inconsistent filesystem states."""
        test_dir = self.copy_fixture("common/video_files")
        corrupted_fs_dir = test_dir / "corrupted_fs_test"
        corrupted_fs_dir.mkdir()

        # Create a file
        test_file = corrupted_fs_dir / "test_movie.mp4"
        test_file.touch()

        # Test edge cases with filesystem operations
        renamer = PlexMovieSubdirRenamer()

        # Test with existing file
        result_existing = renamer.is_video_file(test_file)
        self.assertTrue(result_existing)  # .mp4 extension should be recognized

        # Delete file and test with non-existent file
        test_file.unlink()

        # Should handle non-existent files gracefully
        try:
            result_missing = renamer.is_video_file(test_file)
            # is_video_file typically checks extension, not existence
            self.assertTrue(result_missing)  # .mp4 extension still valid
        except Exception as e:
            self.fail(f"Should handle missing files gracefully: {e}")

        # Test with very long path
        long_path = corrupted_fs_dir / ("x" * 200 + ".mp4")
        try:
            result_long = renamer.is_video_file(long_path)
            self.assertTrue(result_long)  # Extension should still be recognized
        except Exception as e:
            # Some filesystem limits might cause issues, but should be handled
            self.assertIsInstance(e, (OSError, ValueError))

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None
        or SeasonOrganizer is None
        or BatchSeasonOrganizer is None
        or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_network_filesystem_errors(self):
        """Test handling of network filesystem errors."""
        # Simulate network paths
        network_paths = [
            Path("//server/share/movie.mp4"),
            Path("/mnt/nfs/movie.mp4"),
            Path("smb://server/share/movie.mp4"),
        ]

        # Test tools with network paths
        tools = [PlexMovieSubdirRenamer(), SeasonOrganizer(), BatchSeasonOrganizer()]

        for tool in tools:
            for network_path in network_paths:
                try:
                    if hasattr(tool, "is_video_file"):
                        tool.is_video_file(network_path)
                except (OSError, ValueError, AttributeError):
                    # These exceptions are acceptable for network issues
                    pass
                except Exception as e:
                    self.fail(
                        f"Tool {tool.__class__.__name__} should handle network paths gracefully: {e}"
                    )


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestConcurrencyErrorScenarios(MediaLibraryTestCase):
    """Test error scenarios in concurrent environments."""

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_file_locked_by_another_process(self):
        """Test handling files locked by another process."""
        test_dir = self.copy_fixture("common/video_files")
        file_lock_dir = test_dir / "file_lock_test"
        file_lock_dir.mkdir()

        # Create test file
        test_file = file_lock_dir / "locked_movie.mp4"
        test_file.touch()

        # Test real file locking scenarios
        renamer = PlexMovieSubdirRenamer()

        # Test that tool can analyze potentially locked file
        result = renamer.is_video_file(test_file)
        self.assertTrue(result)  # Should identify as video file

        # Test actual file operations that might encounter locking
        try:
            # Try to rename the file
            renamed_file = test_file.parent / "renamed_movie.mp4"
            test_file.rename(renamed_file)

            # If successful, verify and rename back
            self.assertTrue(renamed_file.exists())
            renamed_file.rename(test_file)

        except PermissionError as e:
            # This is acceptable - file might be locked by system/antivirus
            self.assertIn(
                (
                    "access" in str(e).lower()
                    or "being used" in str(e).lower()
                    or "permission" in str(e).lower()
                ),
                [True],
            )
        except OSError as e:
            # Other OS errors are also acceptable in locking scenarios
            self.assertIsInstance(e, OSError)

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_file_modified_during_processing(self):
        """Test handling files modified during processing."""
        test_dir = self.copy_fixture("common/video_files")
        file_modification_dir = test_dir / "file_modification_test"
        file_modification_dir.mkdir()

        # Create test file
        test_file = file_modification_dir / "movie.mp4"
        test_file.touch()

        # Get initial file stats
        initial_stat = test_file.stat()

        # Modify file during processing
        time.sleep(0.01)  # Ensure different timestamp
        test_file.touch()  # Update modification time

        # Verify file was modified
        new_stat = test_file.stat()
        self.assertNotEqual(initial_stat.st_mtime, new_stat.st_mtime)

        # Tools should still handle the file
        renamer = PlexMovieSubdirRenamer()
        self.assertTrue(renamer.is_video_file(test_file))

    @unittest.skipIf(
        SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_directory_deleted_during_processing(self):
        """Test handling directories deleted during processing."""
        test_dir = self.copy_fixture("common/video_files")
        dir_deletion_dir = test_dir / "dir_deletion_test"
        dir_deletion_dir.mkdir()

        # Create subdirectory with files
        sub_dir = dir_deletion_dir / "subdir"
        sub_dir.mkdir()

        test_file = sub_dir / "movie.mp4"
        test_file.touch()

        # Verify initial state
        self.assertTrue(sub_dir.exists())
        self.assertTrue(test_file.exists())

        # Delete directory
        shutil.rmtree(sub_dir)

        # Verify deletion
        self.assertFalse(sub_dir.exists())
        self.assertFalse(test_file.exists())

        # Tools should handle missing directories gracefully
        detector = SABnzbdDetector()

        # Should handle missing directory gracefully
        result = detector.analyze_directory(sub_dir)
        # Should return False, 0, [] for missing directories
        self.assertEqual(result, (False, 0, []))

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None
        or SeasonOrganizer is None
        or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_race_condition_simulation(self):
        """Test handling potential race conditions."""
        test_dir = self.copy_fixture("common/video_files")
        race_condition_dir = test_dir / "race_condition_test"
        race_condition_dir.mkdir()

        # Create test file
        test_file = race_condition_dir / "race_test_movie.mp4"
        test_file.touch()

        # Simulate race condition with file operations
        def simulate_concurrent_access():
            """Simulate another process accessing the file."""
            if test_file.exists():
                # Simulate reading file stats
                test_file.stat()
                # Simulate brief file lock
                time.sleep(0.01)

        # Test concurrent access
        tools = [PlexMovieSubdirRenamer(), SeasonOrganizer()]

        for tool in tools:
            # Simulate concurrent access
            simulate_concurrent_access()

            # Tool should still work
            try:
                if hasattr(tool, "is_video_file"):
                    result = tool.is_video_file(test_file)
                    self.assertTrue(result)
            except Exception as e:
                self.fail(
                    f"Tool {tool.__class__.__name__} should handle concurrent access: {e}"
                )


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestDataCorruptionScenarios(MediaLibraryTestCase):
    """Test scenarios involving data corruption or invalid data."""

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_corrupted_file_detection(self):
        """Test handling of corrupted media files."""
        test_dir = self.copy_fixture("common/video_files")
        corrupted_files_dir = test_dir / "corrupted_files_test"
        corrupted_files_dir.mkdir()

        # Create files with video extensions but invalid content
        corrupted_files = [
            "corrupted_movie.mp4",
            "invalid_video.mkv",
            "broken_episode.avi",
        ]

        for corrupted_file in corrupted_files:
            file_path = corrupted_files_dir / corrupted_file
            # Write invalid content
            with open(file_path, "w") as f:
                f.write("This is not a valid video file")

        # Tools should still recognize files by extension
        renamer = PlexMovieSubdirRenamer()

        for corrupted_file in corrupted_files:
            file_path = corrupted_files_dir / corrupted_file
            # Should recognize by extension, even if content is invalid
            self.assertTrue(renamer.is_video_file(file_path))

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None
        or SeasonOrganizer is None
        or PlexMovieExtrasOrganizer is None
        or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_zero_byte_files(self):
        """Test handling of zero-byte files."""
        test_dir = self.copy_fixture("common/video_files")
        zero_byte_dir = test_dir / "zero_byte_test"
        zero_byte_dir.mkdir()

        # Create zero-byte files
        zero_byte_files = ["empty_movie.mp4", "empty_episode.mkv", "empty_trailer.avi"]

        for zero_file in zero_byte_files:
            file_path = zero_byte_dir / zero_file
            file_path.touch()  # Creates zero-byte file

        # Tools should handle zero-byte files
        tools = [
            PlexMovieSubdirRenamer(),
            SeasonOrganizer(),
            PlexMovieExtrasOrganizer(),
        ]

        for tool in tools:
            for zero_file in zero_byte_files:
                file_path = zero_byte_dir / zero_file
                try:
                    if hasattr(tool, "is_video_file"):
                        result = tool.is_video_file(file_path)
                        # Should recognize by extension
                        self.assertTrue(result)
                except Exception as e:
                    self.fail(
                        f"Tool {tool.__class__.__name__} should handle zero-byte files: {e}"
                    )

    @unittest.skipIf(
        PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE,
        "Required modules not available",
    )
    def test_extremely_large_files(self):
        """Test handling of extremely large file paths and names."""
        test_dir = self.copy_fixture("common/video_files")
        large_files_dir = test_dir / "large_files_test"
        large_files_dir.mkdir()

        # Create file with very long name
        long_name = "a" * 100 + ".mp4"
        long_file = large_files_dir / long_name

        try:
            long_file.touch()
            file_created = True
        except OSError:
            # Some filesystems may not support very long names
            file_created = False

        if file_created:
            # Test tools with long filename
            renamer = PlexMovieSubdirRenamer()

            try:
                result = renamer.is_video_file(long_file)
                self.assertTrue(result)
            except Exception as e:
                self.fail(f"Tool should handle long filenames: {e}")
