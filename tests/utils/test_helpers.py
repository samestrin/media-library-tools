#!/usr/bin/env python3
"""
Test Helpers for Media Library Tools

Common utilities and helper functions for testing media library tools.
Provides standardized testing patterns and assertion helpers.
"""

import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from unittest.mock import patch

# Add tool directories to path for imports
TOOLS_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TOOLS_ROOT / "SABnzbd"))
sys.path.insert(0, str(TOOLS_ROOT / "plex"))
sys.path.insert(0, str(TOOLS_ROOT / "plex-api"))


class MediaLibraryTestCase(unittest.TestCase):
    """Base test case class for media library tools.

    Provides common setup, teardown, and assertion methods.
    """

    def setUp(self):
        """Set up test case with fixture manager."""
        try:
            from fixture_manager import FixtureManager
        except ImportError:
            # Fallback for when relative imports don't work
            import sys
            from pathlib import Path

            utils_dir = Path(__file__).parent
            sys.path.insert(0, str(utils_dir))
            from fixture_manager import FixtureManager

        self.fixture_manager = FixtureManager()
        self.test_dirs = []

    def tearDown(self):
        """Clean up test data."""
        for test_dir in self.test_dirs:
            self.fixture_manager.cleanup_test_data(test_dir)
        self.fixture_manager.cleanup_test_data()

    def copy_fixture(self, fixture_path: str) -> Path:
        """Copy fixture and track for cleanup.

        Args:
            fixture_path: Relative path to fixture

        Returns:
            Path to copied test data
        """
        test_dir = self.fixture_manager.copy_fixture_to_test_data(fixture_path)
        self.test_dirs.append(test_dir)
        return test_dir

    def create_temp_fixture(self, structure: Dict[str, Any]) -> Path:
        """Create temporary fixture and track for cleanup.

        Args:
            structure: Structure definition

        Returns:
            Path to created fixture
        """
        test_dir = self.fixture_manager.create_temp_fixture(structure)
        self.test_dirs.append(test_dir)
        return test_dir

    def assert_file_exists(self, path: Union[str, Path], msg: Optional[str] = None):
        """Assert that a file exists.

        Args:
            path: File path to check
            msg: Optional custom message
        """
        path = Path(path)
        if not path.exists():
            self.fail(msg or f"File does not exist: {path}")
        if not path.is_file():
            self.fail(msg or f"Path is not a file: {path}")

    def assert_file_not_exists(self, path: Union[str, Path], msg: Optional[str] = None):
        """Assert that a file does not exist.

        Args:
            path: File path to check
            msg: Optional custom message
        """
        path = Path(path)
        if path.exists():
            self.fail(msg or f"File should not exist: {path}")

    def assert_dir_exists(self, path: Union[str, Path], msg: Optional[str] = None):
        """Assert that a directory exists.

        Args:
            path: Directory path to check
            msg: Optional custom message
        """
        path = Path(path)
        if not path.exists():
            self.fail(msg or f"Directory does not exist: {path}")
        if not path.is_dir():
            self.fail(msg or f"Path is not a directory: {path}")

    def assert_dir_not_exists(self, path: Union[str, Path], msg: Optional[str] = None):
        """Assert that a directory does not exist.

        Args:
            path: Directory path to check
            msg: Optional custom message
        """
        path = Path(path)
        if path.exists():
            self.fail(msg or f"Directory should not exist: {path}")

    def assert_file_count(
        self,
        directory: Union[str, Path],
        expected_count: int,
        pattern: str = "*",
        msg: Optional[str] = None,
    ):
        """Assert number of files in directory.

        Args:
            directory: Directory to check
            expected_count: Expected number of files
            pattern: File pattern to match (default: all files)
            msg: Optional custom message
        """
        directory = Path(directory)
        if not directory.exists():
            self.fail(f"Directory does not exist: {directory}")

        files = list(directory.glob(pattern))
        actual_count = len([f for f in files if f.is_file()])

        if actual_count != expected_count:
            self.fail(
                msg
                or f"Expected {expected_count} files matching '{pattern}', "
                f"found {actual_count} in {directory}"
            )

    def assert_video_file(self, path: Union[str, Path], msg: Optional[str] = None):
        """Assert that a file is a video file based on extension.

        Args:
            path: File path to check
            msg: Optional custom message
        """
        path = Path(path)
        video_extensions = {
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
            ".mpg",
            ".mpeg",
            ".3gp",
            ".ogv",
            ".ts",
            ".m2ts",
            ".vob",
            ".divx",
            ".xvid",
            ".rm",
            ".rmvb",
            ".asf",
            ".f4v",
            ".m4p",
        }

        if path.suffix.lower() not in video_extensions:
            self.fail(msg or f"File is not a video file: {path}")

    def get_file_list(
        self, directory: Union[str, Path], pattern: str = "*"
    ) -> List[Path]:
        """Get list of files in directory matching pattern.

        Args:
            directory: Directory to search
            pattern: File pattern to match

        Returns:
            List of file paths
        """
        directory = Path(directory)
        return [f for f in directory.glob(pattern) if f.is_file()]

    def get_dir_list(
        self, directory: Union[str, Path], pattern: str = "*"
    ) -> List[Path]:
        """Get list of directories matching pattern.

        Args:
            directory: Directory to search
            pattern: Directory pattern to match

        Returns:
            List of directory paths
        """
        directory = Path(directory)
        return [d for d in directory.glob(pattern) if d.is_dir()]


class MockArgumentParser:
    """Mock argument parser for testing CLI tools."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def create_mock_args(**kwargs) -> MockArgumentParser:
    """Create mock command line arguments.

    Args:
        **kwargs: Argument values

    Returns:
        Mock args object
    """
    defaults = {
        "verbose": False,
        "debug": False,
        "dry_run": False,
        "delete": False,
        "yes": False,
        "force": False,
        "path": ".",
    }
    defaults.update(kwargs)
    return MockArgumentParser(**defaults)


def mock_non_interactive(return_value: bool = True):
    """Decorator to mock non-interactive detection.

    Args:
        return_value: Value to return for is_non_interactive()

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch("builtins.input", return_value="y"), patch(
                "sys.stdin.isatty", return_value=not return_value
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def capture_output(func, *args, **kwargs) -> tuple:
    """Capture stdout and stderr from function execution.

    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Tuple of (stdout, stderr, return_value)
    """
    import io
    from contextlib import redirect_stderr, redirect_stdout

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            result = func(*args, **kwargs)
        return stdout_capture.getvalue(), stderr_capture.getvalue(), result
    except Exception as e:
        return stdout_capture.getvalue(), stderr_capture.getvalue(), e


def create_sabnzbd_fixture(base_dir: Path, scenario: str = "mixed") -> Path:
    """Create SABnzbd test fixture.

    Args:
        base_dir: Base directory to create fixture in
        scenario: Type of scenario ('mixed', 'sabnzbd_only', 'bittorrent_only')

    Returns:
        Path to created fixture
    """
    from fixture_manager import FixtureManager

    manager = FixtureManager()

    if scenario == "mixed":
        # Create mixed SABnzbd and BitTorrent directories
        sabnzbd_dir = base_dir / "sabnzbd_download"
        bittorrent_dir = base_dir / "bittorrent_download"

        manager.create_sabnzbd_indicators(sabnzbd_dir)
        manager.create_bittorrent_indicators(bittorrent_dir)

    elif scenario == "sabnzbd_only":
        # Create only SABnzbd directories
        for i in range(3):
            sabnzbd_dir = base_dir / f"sabnzbd_download_{i}"
            manager.create_sabnzbd_indicators(sabnzbd_dir)

    elif scenario == "bittorrent_only":
        # Create only BitTorrent directories
        for i in range(2):
            bittorrent_dir = base_dir / f"bittorrent_download_{i}"
            manager.create_bittorrent_indicators(bittorrent_dir)

    return base_dir


def create_plex_movie_fixture(base_dir: Path, with_extras: bool = True) -> Path:
    """Create Plex movie test fixture.

    Args:
        base_dir: Base directory to create fixture in
        with_extras: Whether to include extras subdirectories

    Returns:
        Path to created fixture
    """
    from fixture_manager import FixtureManager

    manager = FixtureManager()

    # Main movie file
    manager.create_video_files(base_dir, ["Movie (2023).mp4"])

    if with_extras:
        # Featurettes subdirectory
        featurettes_dir = base_dir / "Featurettes"
        manager.create_video_files(
            featurettes_dir,
            [
                "behind_the_scenes.mp4",
                "deleted_scene_01.mkv",
                "making_of.avi",
                "interview_director.mp4",
            ],
        )

        # Extras subdirectory
        extras_dir = base_dir / "Extras"
        manager.create_video_files(extras_dir, ["trailer.mp4", "teaser.mkv"])

    return base_dir


def create_plex_tv_fixture(
    base_dir: Path, num_seasons: int = 2, episodes_per_season: int = 5
) -> Path:
    """Create Plex TV show test fixture.

    Args:
        base_dir: Base directory to create fixture in
        num_seasons: Number of seasons to create
        episodes_per_season: Number of episodes per season

    Returns:
        Path to created fixture
    """
    from fixture_manager import FixtureManager

    manager = FixtureManager()

    # Create episode files in root directory (unorganized)
    episode_files = []
    for season in range(1, num_seasons + 1):
        for episode in range(1, episodes_per_season + 1):
            filename = f"Show.S{season:02d}E{episode:02d}.Episode.Title.mp4"
            episode_files.append(filename)

    manager.create_video_files(base_dir, episode_files)

    return base_dir


def assert_plex_naming_convention(file_path: Path, expected_pattern: str) -> bool:
    """Assert file follows Plex naming convention.

    Args:
        file_path: File to check
        expected_pattern: Expected naming pattern

    Returns:
        True if naming convention is correct
    """
    import re

    filename = file_path.name

    # Common Plex patterns
    patterns = {
        "movie_extra": r"^.+-(?:featurette|deleted|trailer|behindthescenes|interview|scene|short|other)(?:\d+)?\.\w+$",
        "tv_episode": r"^.+[Ss]\d{2}[Ee]\d{2}.*\.\w+$",
        "season_dir": r"^Season \d{2}$",
    }

    if expected_pattern in patterns:
        pattern = patterns[expected_pattern]
        return bool(re.match(pattern, filename))

    return False


def get_tool_version(tool_name: str) -> str:
    """Get version of a tool.

    Args:
        tool_name: Name of the tool

    Returns:
        Version string
    """
    try:
        if tool_name == "sabnzbd_cleanup":
            from sabnzbd_cleanup import VERSION

            return VERSION
        elif tool_name.startswith("plex_"):
            # Import the specific tool and get its version
            module = __import__(tool_name)
            return getattr(module, "VERSION", "unknown")
        else:
            return "unknown"
    except ImportError:
        return "unknown"


def run_tool_with_args(tool_name: str, args: List[str]) -> tuple:
    """Run a tool with command line arguments.

    Args:
        tool_name: Name of the tool to run
        args: Command line arguments

    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    import subprocess
    import sys

    tool_path = TOOLS_ROOT / tool_name.split("_")[0] / tool_name
    if not tool_path.exists():
        # Try with .py extension
        tool_path = tool_path.with_suffix(".py")

    if not tool_path.exists():
        raise FileNotFoundError(f"Tool not found: {tool_name}")

    cmd = [sys.executable, str(tool_path)] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Tool execution timed out", 1
    except Exception as e:
        return "", str(e), 1


# Indicate that test helpers are available
TEST_HELPERS_AVAILABLE = True
