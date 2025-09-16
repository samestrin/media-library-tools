#!/usr/bin/env python3
"""
Fixture Manager for Media Library Tools Tests

Provides utilities for managing test fixtures including copying, cleanup,
and dynamic fixture creation for comprehensive testing.
"""

import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


class FixtureManager:
    """Manages test fixtures for media library tools testing."""

    def __init__(self):
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"
        self.test_data_dir = Path(__file__).parent.parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)

        # Track created test directories for cleanup
        self._created_dirs = set()

    def copy_fixture_to_test_data(self, fixture_path: str) -> Path:
        """Copy fixture to test_data directory with unique name.

        Args:
            fixture_path: Relative path to fixture (e.g., 'sabnzbd/mixed_downloads')

        Returns:
            Path to the copied test data directory

        Raises:
            FileNotFoundError: If fixture doesn't exist
        """
        source_path = self.fixtures_dir / fixture_path
        if not source_path.exists():
            raise FileNotFoundError(f"Fixture not found: {source_path}")

        # Create unique test directory name
        test_id = str(uuid.uuid4())[:8]
        fixture_name = fixture_path.replace("/", "_")
        dest_path = self.test_data_dir / f"{fixture_name}_{test_id}"

        # Copy fixture to test data
        if source_path.is_dir():
            shutil.copytree(source_path, dest_path)
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)

        # Track for cleanup
        self._created_dirs.add(dest_path)

        return dest_path

    def cleanup_test_data(self, test_data_path: Optional[Path] = None) -> None:
        """Remove test data directory and contents.

        Args:
            test_data_path: Specific path to clean up, or None for all tracked paths
        """
        if test_data_path:
            if test_data_path.exists():
                if test_data_path.is_dir():
                    shutil.rmtree(test_data_path)
                else:
                    test_data_path.unlink()
            self._created_dirs.discard(test_data_path)
        else:
            # Clean up all tracked directories
            for path in list(self._created_dirs):
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            self._created_dirs.clear()

    def create_temp_fixture(self, structure: Dict[str, Any]) -> Path:
        """Create temporary fixture from structure definition.

        Args:
            structure: Dictionary defining directory structure
                      Format: {
                          'files': ['file1.txt', 'file2.mp4'],
                          'directories': {
                              'subdir': {
                                  'files': ['subfile.txt']
                              }
                          }
                      }

        Returns:
            Path to created temporary fixture
        """
        test_id = str(uuid.uuid4())[:8]
        temp_path = self.test_data_dir / f"temp_fixture_{test_id}"
        temp_path.mkdir(parents=True, exist_ok=True)

        self._create_structure(temp_path, structure)
        self._created_dirs.add(temp_path)

        return temp_path

    def _create_structure(self, base_path: Path, structure: Dict[str, Any]) -> None:
        """Recursively create directory structure.

        Args:
            base_path: Base directory to create structure in
            structure: Structure definition dictionary
                     Supports two formats:
                     1. Legacy format: {'files': [...], 'directories': {...}}
                     2. Simple format: {'filename.ext': 'file', 'dirname': {...}}
        """
        # Handle legacy format
        if "files" in structure:
            for filename in structure["files"]:
                file_path = base_path / filename
                file_path.touch()

        if "directories" in structure:
            for dirname, substructure in structure["directories"].items():
                dir_path = base_path / dirname
                dir_path.mkdir(exist_ok=True)
                if substructure:
                    self._create_structure(dir_path, substructure)
        else:
            # Handle simple format
            for name, value in structure.items():
                if name in ["files", "directories"]:
                    continue  # Skip legacy keys

                if value == "file":
                    # Create file
                    file_path = base_path / name
                    file_path.touch()
                elif isinstance(value, dict):
                    # Create directory and recurse
                    dir_path = base_path / name
                    dir_path.mkdir(exist_ok=True)
                    self._create_structure(dir_path, value)

    def assert_directory_structure(self, path: Path, expected: Dict[str, Any]) -> None:
        """Assert directory matches expected structure.

        Args:
            path: Directory path to check
            expected: Expected structure dictionary

        Raises:
            AssertionError: If structure doesn't match
        """
        if not path.exists():
            raise AssertionError(f"Directory does not exist: {path}")

        if not path.is_dir():
            raise AssertionError(f"Path is not a directory: {path}")

        # Check files
        if "files" in expected:
            expected_files = set(expected["files"])
            actual_files = {f.name for f in path.iterdir() if f.is_file()}

            missing_files = expected_files - actual_files
            if missing_files:
                raise AssertionError(f"Missing files: {missing_files}")

            # Optional: Check for unexpected files
            # unexpected_files = actual_files - expected_files
            # if unexpected_files:
            #     raise AssertionError(f"Unexpected files: {unexpected_files}")

        # Check directories
        if "directories" in expected:
            for dirname, substructure in expected["directories"].items():
                subdir_path = path / dirname
                if not subdir_path.exists():
                    raise AssertionError(f"Missing directory: {subdir_path}")

                if substructure:
                    self.assert_directory_structure(subdir_path, substructure)

    def create_file_with_content(
        self, path: Path, content: str = "", size_bytes: Optional[int] = None
    ) -> None:
        """Create a file with specific content or size.

        Args:
            path: File path to create
            content: Content to write to file
            size_bytes: If specified, create file of this size (overrides content)
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        if size_bytes is not None:
            # Create file of specific size
            with open(path, "wb") as f:
                f.write(b"\0" * size_bytes)
        else:
            # Create file with content
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def create_sabnzbd_indicators(self, directory: Path) -> None:
        """Create SABnzbd-specific indicator files in directory.

        Args:
            directory: Directory to add SABnzbd indicators to
        """
        directory.mkdir(parents=True, exist_ok=True)

        # Common SABnzbd indicators (matching existing fixtures)
        indicators = [
            "SABnzbd_nzo",  # SABnzbd download indicator
            "SABnzbd_nzb",  # SABnzbd NZB file indicator
            ".nzb",  # NZB file
            "movie.nfo",  # NFO file
            "movie.r00",  # RAR part file
            "movie.r01",  # RAR part file
            "_UNPACK_movie/",  # Unpacking directory
            ".tmp",  # Temp file
        ]

        for indicator in indicators:
            if indicator.endswith("/"):
                # Directory
                (directory / indicator.rstrip("/")).mkdir(exist_ok=True)
            else:
                # File
                (directory / indicator).touch()

    def create_bittorrent_indicators(self, directory: Path) -> None:
        """Create BitTorrent-specific indicator files in directory.

        Args:
            directory: Directory to add BitTorrent indicators to
        """
        directory.mkdir(parents=True, exist_ok=True)

        # Common BitTorrent indicators
        indicators = [
            ".torrent",
            ".resume",
            "movie.mp4",  # Complete file
            ".fastresume",
            "torrent.state",
        ]

        for indicator in indicators:
            (directory / indicator).touch()

    def create_video_files(self, directory: Path, filenames: List[str]) -> None:
        """Create empty video files with proper extensions.

        Args:
            directory: Directory to create files in
            filenames: List of video filenames to create
        """
        directory.mkdir(parents=True, exist_ok=True)

        for filename in filenames:
            (directory / filename).touch()

    def get_fixture_path(self, fixture_path: str) -> Path:
        """Get absolute path to a fixture.

        Args:
            fixture_path: Relative path to fixture

        Returns:
            Absolute path to fixture
        """
        return self.fixtures_dir / fixture_path

    def list_fixtures(self, category: Optional[str] = None) -> List[str]:
        """List available fixtures.

        Args:
            category: Optional category filter (e.g., 'sabnzbd', 'plex')

        Returns:
            List of fixture paths
        """
        fixtures = []

        if category:
            search_dir = self.fixtures_dir / category
            if search_dir.exists():
                for item in search_dir.rglob("*"):
                    if item.is_dir():
                        rel_path = item.relative_to(self.fixtures_dir)
                        fixtures.append(str(rel_path))
        else:
            for item in self.fixtures_dir.rglob("*"):
                if item.is_dir() and item != self.fixtures_dir:
                    rel_path = item.relative_to(self.fixtures_dir)
                    fixtures.append(str(rel_path))

        return sorted(fixtures)


# Convenience functions for direct use
def copy_fixture_to_test_data(fixture_path: str) -> Path:
    """Copy fixture to test data directory.

    Args:
        fixture_path: Relative path to fixture

    Returns:
        Path to copied test data
    """
    manager = FixtureManager()
    return manager.copy_fixture_to_test_data(fixture_path)


def cleanup_test_data(test_data_path: Optional[Path] = None) -> None:
    """Clean up test data.

    Args:
        test_data_path: Specific path to clean up, or None for all
    """
    manager = FixtureManager()
    manager.cleanup_test_data(test_data_path)


def create_temp_fixture(structure: Dict[str, Any]) -> Path:
    """Create temporary fixture from structure.

    Args:
        structure: Structure definition dictionary

    Returns:
        Path to created fixture
    """
    manager = FixtureManager()
    return manager.create_temp_fixture(structure)


def assert_directory_structure(path: Path, expected: Dict[str, Any]) -> None:
    """Assert directory structure matches expected.

    Args:
        path: Directory to check
        expected: Expected structure
    """
    manager = FixtureManager()
    manager.assert_directory_structure(path, expected)
