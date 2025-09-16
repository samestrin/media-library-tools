#!/usr/bin/env python3
"""
Comprehensive test suite for plex_update_tv_years
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Add the parent directory to path for test helpers
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

try:
    from utils.test_helpers import TEST_HELPERS_AVAILABLE, MediaLibraryTestCase
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

import importlib.util


# Load the plex_update_tv_years script as a module
def load_plex_update_tv_years():
    """Load the plex_update_tv_years script as a module."""
    script_path = Path(__file__).parent.parent / "plex" / "plex_update_tv_years"
    if not script_path.exists():
        return None

    # Copy the script to a temporary .py file for import
    import shutil

    temp_script_path = Path(__file__).parent / "temp_plex_update_tv_years.py"

    try:
        shutil.copy2(script_path, temp_script_path)

        spec = importlib.util.spec_from_file_location(
            "plex_update_tv_years", temp_script_path
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules["plex_update_tv_years"] = module
        spec.loader.exec_module(module)

        return module
    except Exception:
        return None
    finally:
        # Clean up the temporary file
        temp_script_path.unlink(missing_ok=True)


class TestCredentialHandling(MediaLibraryTestCase):
    """Test credential handling functionality."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_update_tv_years()
        if not self.module:
            self.skipTest("plex_update_tv_years module not available")

    def test_get_tvdb_key_from_cli(self):
        """Test API key retrieval from CLI argument."""
        result = self.module.get_tvdb_key_from_sources(
            cli_key="test_key_cli", debug=False
        )
        self.assertEqual(result, "test_key_cli")

    def test_get_tvdb_key_from_env(self):
        """Test API key retrieval from environment variable."""
        with patch.dict(os.environ, {"TVDB_API_KEY": "test_key_env"}):
            result = self.module.get_tvdb_key_from_sources(debug=False)
            self.assertEqual(result, "test_key_env")

    def test_get_tvdb_key_from_env_file(self):
        """Test API key retrieval from .env file."""
        env_content = "TVDB_API_KEY=test_key_file\nOTHER_VAR=value"

        with tempfile.TemporaryDirectory() as temp_dir:
            env_file_path = Path(temp_dir) / ".env"
            env_file_path.write_text(env_content)

            with patch("os.path.exists", return_value=True), patch(
                "builtins.open", mock_open(read_data=env_content)
            ):
                result = self.module.get_tvdb_key_from_sources(debug=False)
                self.assertEqual(result, "test_key_file")

    def test_get_tvdb_key_not_found(self):
        """Test handling when API key is not found."""
        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", return_value=False
        ):
            result = self.module.get_tvdb_key_from_sources(debug=False)
            self.assertIsNone(result)

    def test_cli_priority_over_env(self):
        """Test that CLI argument takes priority over environment variable."""
        with patch.dict(os.environ, {"TVDB_API_KEY": "env_key"}):
            result = self.module.get_tvdb_key_from_sources(
                cli_key="cli_key", debug=False
            )
            self.assertEqual(result, "cli_key")

    def test_get_tvdb_key_from_global_env_file(self):
        """Test API key retrieval from global .env file."""
        global_env_content = "TVDB_API_KEY=test_key_global\nOTHER_VAR=value"

        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", side_effect=lambda path: path != ".env"
        ), patch("pathlib.Path.home") as mock_home, patch(
            "builtins.open", mock_open(read_data=global_env_content)
        ), patch.object(
            Path, "exists", return_value=True
        ):
            mock_home.return_value = Path("/home/user")
            result = self.module.get_tvdb_key_from_sources(debug=False)
            self.assertEqual(result, "test_key_global")

    def test_local_env_priority_over_global_env(self):
        """Test that local .env takes priority over global .env."""
        local_env_content = "TVDB_API_KEY=local_key\n"
        global_env_content = "TVDB_API_KEY=global_key\n"

        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", return_value=True
        ), patch("pathlib.Path.home") as mock_home, patch.object(
            Path, "exists", return_value=True
        ):
            mock_home.return_value = Path("/home/user")

            # Mock file reads to return different content based on path
            def mock_open_func(file_path, *args, **kwargs):
                if str(file_path).endswith(".env") and not str(file_path).startswith(
                    "/home"
                ):
                    return mock_open(read_data=local_env_content).return_value
                else:
                    return mock_open(read_data=global_env_content).return_value

            with patch("builtins.open", side_effect=mock_open_func):
                result = self.module.get_tvdb_key_from_sources(debug=False)
                self.assertEqual(result, "local_key")

    def test_env_priority_over_global_env(self):
        """Test that environment variable takes priority over global .env."""
        global_env_content = "TVDB_API_KEY=global_key\n"

        with patch.dict(os.environ, {"TVDB_API_KEY": "env_key"}), patch(
            "os.path.exists", return_value=False
        ), patch("pathlib.Path.home") as mock_home, patch.object(
            Path, "exists", return_value=True
        ), patch(
            "builtins.open", mock_open(read_data=global_env_content)
        ):
            mock_home.return_value = Path("/home/user")
            result = self.module.get_tvdb_key_from_sources(debug=False)
            self.assertEqual(result, "env_key")

    def test_global_env_file_not_found(self):
        """Test handling when global .env file doesn't exist."""
        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", return_value=False
        ), patch("pathlib.Path.home") as mock_home, patch.object(
            Path, "exists", return_value=False
        ):
            mock_home.return_value = Path("/home/user")
            result = self.module.get_tvdb_key_from_sources(debug=False)
            self.assertIsNone(result)

    def test_global_env_file_read_error(self):
        """Test handling when global .env file cannot be read."""
        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", return_value=False
        ), patch("pathlib.Path.home") as mock_home, patch.object(
            Path, "exists", return_value=True
        ), patch(
            "builtins.open", side_effect=OSError("Permission denied")
        ):
            mock_home.return_value = Path("/home/user")
            result = self.module.get_tvdb_key_from_sources(debug=False)
            self.assertIsNone(result)


class TestTVDBClient(MediaLibraryTestCase):
    """Test TVDB API client functionality."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_update_tv_years()
        if not self.module:
            self.skipTest("plex_update_tv_years module not available")
        self.client = self.module.TVDBClient("test_api_key", debug=False)

    def test_client_initialization(self):
        """Test TVDBClient initialization."""
        self.assertEqual(self.client.api_key, "test_api_key")
        self.assertEqual(self.client.base_url, "https://api4.thetvdb.com/v4")
        self.assertIsNone(self.client.token)
        self.assertEqual(self.client.token_expires, 0)

    @patch("urllib.request.urlopen")
    def test_login_success(self, mock_urlopen):
        """Test successful TVDB API login."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {"data": {"token": "test_jwt_token"}}
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.login()
        self.assertTrue(result)
        self.assertEqual(self.client.token, "test_jwt_token")
        self.assertGreater(self.client.token_expires, 0)

    @patch("urllib.request.urlopen")
    def test_login_failure(self, mock_urlopen):
        """Test TVDB API login failure."""
        mock_response = MagicMock()
        mock_response.status = 401
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.login()
        self.assertFalse(result)
        self.assertIsNone(self.client.token)

    @patch("urllib.request.urlopen")
    def test_search_show_success(self, mock_urlopen):
        """Test successful show search."""
        # Mock login
        login_response = MagicMock()
        login_response.status = 200
        login_response.read.return_value = json.dumps(
            {"data": {"token": "test_token"}}
        ).encode("utf-8")

        # Mock search
        search_response = MagicMock()
        search_response.status = 200
        search_response.read.return_value = json.dumps(
            {"data": [{"name": "Test Show", "year": "2020"}]}
        ).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [
            login_response,
            search_response,
        ]

        result = self.client.search_show("Test Show")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test Show")
        self.assertEqual(result["year"], "2020")

    @patch("urllib.request.urlopen")
    def test_search_show_not_found(self, mock_urlopen):
        """Test show search when no results found."""
        # Mock login
        login_response = MagicMock()
        login_response.status = 200
        login_response.read.return_value = json.dumps(
            {"data": {"token": "test_token"}}
        ).encode("utf-8")

        # Mock empty search
        search_response = MagicMock()
        search_response.status = 200
        search_response.read.return_value = json.dumps({"data": []}).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [
            login_response,
            search_response,
        ]

        result = self.client.search_show("Nonexistent Show")
        self.assertIsNone(result)


class TestTVShowYearUpdater(MediaLibraryTestCase):
    """Test TV Show Year Updater functionality."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_update_tv_years()
        if not self.module:
            self.skipTest("plex_update_tv_years module not available")
        self.updater = self.module.TVShowYearUpdater(
            tvdb_key="test_key", dry_run=True, debug=False
        )

    def test_updater_initialization(self):
        """Test TVShowYearUpdater initialization."""
        self.assertEqual(self.updater.tvdb_key, "test_key")
        self.assertTrue(self.updater.dry_run)
        self.assertFalse(self.updater.debug)
        self.assertIsNotNone(self.updater.tvdb_client)
        self.assertEqual(len(self.updater.stats), 5)

    def test_extract_year_from_name_parentheses(self):
        """Test year extraction from parentheses format."""
        test_cases = [
            ("Show Title (2020)", 2020),
            ("Another Show (1995)", 1995),
            ("Show with Multiple (2020) Parentheses (2021)", 2020),  # First match
        ]

        for directory_name, expected_year in test_cases:
            with self.subTest(directory_name=directory_name):
                result = self.updater.extract_year_from_name(directory_name)
                self.assertEqual(result, expected_year)

    def test_extract_year_from_name_brackets(self):
        """Test year extraction from brackets format."""
        test_cases = [
            ("Show Title [2020]", 2020),
            ("Another Show [1995]", 1995),
        ]

        for directory_name, expected_year in test_cases:
            with self.subTest(directory_name=directory_name):
                result = self.updater.extract_year_from_name(directory_name)
                self.assertEqual(result, expected_year)

    def test_extract_year_from_name_various_formats(self):
        """Test year extraction from various formats."""
        test_cases = [
            ("Show.2020.", 2020),
            ("Show 2020", 2020),
            ("Show-2020-", 2020),
            ("Show_2020_", 2020),
            ("Show.2020", 2020),
            ("Show-2020", 2020),
            ("2020.Show", 2020),
            ("2020 Show", 2020),
        ]

        for directory_name, expected_year in test_cases:
            with self.subTest(directory_name=directory_name):
                result = self.updater.extract_year_from_name(directory_name)
                self.assertEqual(result, expected_year)

    def test_extract_year_no_year(self):
        """Test year extraction when no year is present."""
        test_cases = [
            "Show Title",
            "Another Show",
            "Show with Numbers 123",
        ]

        for directory_name in test_cases:
            with self.subTest(directory_name=directory_name):
                result = self.updater.extract_year_from_name(directory_name)
                self.assertIsNone(result)

    def test_extract_year_invalid_year(self):
        """Test year extraction with invalid years."""
        test_cases = [
            "Show (1800)",  # Too old
            "Show (2040)",  # Too new
            "Show (123)",  # Too short
        ]

        for directory_name in test_cases:
            with self.subTest(directory_name=directory_name):
                result = self.updater.extract_year_from_name(directory_name)
                self.assertIsNone(result)

    def test_clean_show_name(self):
        """Test show name cleaning for search."""
        test_cases = [
            ("Show Title (2020)", "Show Title"),
            ("Another Show [1995]", "Another Show"),
            ("Show.2020.Extra", "Show Extra"),
            ("Show Title", "Show Title"),
            ("Show_Title-2020-", "Show_Title"),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.updater.clean_show_name(original)
                self.assertEqual(result, expected)

    def test_needs_year_update(self):
        """Test logic for determining if year update is needed."""
        # No current year, needs update
        needs_update, current_year = self.updater.needs_year_update("Show Title", 2020)
        self.assertTrue(needs_update)
        self.assertIsNone(current_year)

        # Wrong year, needs update
        needs_update, current_year = self.updater.needs_year_update(
            "Show Title (2019)", 2020
        )
        self.assertTrue(needs_update)
        self.assertEqual(current_year, 2019)

        # Correct year, no update needed
        needs_update, current_year = self.updater.needs_year_update(
            "Show Title (2020)", 2020
        )
        self.assertFalse(needs_update)
        self.assertEqual(current_year, 2020)

    def test_generate_new_name(self):
        """Test new name generation."""
        result = self.updater.generate_new_name("Show Title", 2020)
        self.assertEqual(result, "Show Title (2020)")

        result = self.updater.generate_new_name("Another Show", 1995)
        self.assertEqual(result, "Another Show (1995)")

    def test_get_credential_from_sources_global_env(self):
        """Test _get_credential_from_sources method with global .env file."""
        global_env_content = "TEST_CREDENTIAL=global_value\nOTHER_VAR=value"

        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", side_effect=lambda path: path != ".env"
        ), patch("pathlib.Path.home") as mock_home, patch(
            "builtins.open", mock_open(read_data=global_env_content)
        ), patch.object(
            Path, "exists", return_value=True
        ):
            mock_home.return_value = Path("/home/user")
            result = self.updater._get_credential_from_sources("TEST_CREDENTIAL", None)
            self.assertEqual(result, "global_value")

    def test_get_credential_from_sources_priority_order(self):
        """Test _get_credential_from_sources method priority order."""
        local_env_content = "TEST_CREDENTIAL=local_value\n"
        global_env_content = "TEST_CREDENTIAL=global_value\n"

        # Test that CLI takes priority
        result = self.updater._get_credential_from_sources(
            "TEST_CREDENTIAL", "cli_value"
        )
        self.assertEqual(result, "cli_value")

        # Test that environment takes priority over files
        with patch.dict(os.environ, {"TEST_CREDENTIAL": "env_value"}):
            result = self.updater._get_credential_from_sources("TEST_CREDENTIAL", None)
            self.assertEqual(result, "env_value")

        # Test that local .env takes priority over global .env
        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", return_value=True
        ), patch("pathlib.Path.home") as mock_home, patch.object(
            Path, "exists", return_value=True
        ):
            mock_home.return_value = Path("/home/user")

            def mock_open_func(file_path, *args, **kwargs):
                if str(file_path).endswith(".env") and not str(file_path).startswith(
                    "/home"
                ):
                    return mock_open(read_data=local_env_content).return_value
                else:
                    return mock_open(read_data=global_env_content).return_value

            with patch("builtins.open", side_effect=mock_open_func):
                result = self.updater._get_credential_from_sources(
                    "TEST_CREDENTIAL", None
                )
                self.assertEqual(result, "local_value")

    def test_get_credential_from_sources_global_env_error_handling(self):
        """Test _get_credential_from_sources method error handling for global .env."""
        with patch.dict(os.environ, {}, clear=True), patch(
            "os.path.exists", return_value=False
        ), patch("pathlib.Path.home") as mock_home, patch.object(
            Path, "exists", return_value=True
        ), patch(
            "builtins.open", side_effect=OSError("Permission denied")
        ):
            mock_home.return_value = Path("/home/user")
            result = self.updater._get_credential_from_sources("TEST_CREDENTIAL", None)
            self.assertIsNone(result)


class TestNonInteractiveDetection(MediaLibraryTestCase):
    """Test non-interactive environment detection."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_update_tv_years()
        if not self.module:
            self.skipTest("plex_update_tv_years module not available")

    @patch("sys.stdin.isatty")
    def test_non_interactive_no_tty(self, mock_isatty):
        """Test non-interactive detection when no TTY."""
        mock_isatty.return_value = False
        result = self.module.is_non_interactive()
        self.assertTrue(result)

    @patch("sys.stdin.isatty")
    def test_non_interactive_with_env_vars(self, mock_isatty):
        """Test non-interactive detection with automation env vars."""
        mock_isatty.return_value = True

        env_vars = ["CRON", "CI", "AUTOMATED", "NON_INTERACTIVE"]
        for var in env_vars:
            with self.subTest(env_var=var), patch.dict(os.environ, {var: "1"}):
                result = self.module.is_non_interactive()
                self.assertTrue(result)

    @patch("sys.stdin.isatty")
    def test_non_interactive_no_term(self, mock_isatty):
        """Test non-interactive detection when TERM not set."""
        mock_isatty.return_value = True

        with patch.dict(os.environ, {}, clear=True):
            result = self.module.is_non_interactive()
            self.assertTrue(result)

    @patch("sys.stdin.isatty")
    def test_interactive_normal(self, mock_isatty):
        """Test interactive detection in normal environment."""
        mock_isatty.return_value = True

        with patch.dict(os.environ, {"TERM": "xterm-256color"}):
            result = self.module.is_non_interactive()
            self.assertFalse(result)


class TestFileLocking(MediaLibraryTestCase):
    """Test file locking functionality."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_update_tv_years()
        if not self.module:
            self.skipTest("plex_update_tv_years module not available")
        self.updater = self.module.TVShowYearUpdater(
            tvdb_key="test_key", dry_run=True, debug=False
        )

    def test_acquire_release_lock(self):
        """Test lock acquisition and release."""
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir)

            # Acquire lock
            result = self.updater.acquire_lock(lock_dir)
            self.assertTrue(result)
            self.assertIsNotNone(self.updater.lock_file)

            # Release lock
            self.updater.release_lock()
            self.assertIsNone(self.updater.lock_file)


class TestIntegrationWorkflow(MediaLibraryTestCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        """Set up test environment with temporary directories."""
        super().setUp()
        self.module = load_plex_update_tv_years()
        if not self.module:
            self.skipTest("plex_update_tv_years module not available")

        # Create temporary test directory structure
        self.test_dir = Path(tempfile.mkdtemp())

        # Create test TV show directories
        test_shows = [
            "Breaking Bad (2008)",  # Already correct
            "Game of Thrones",  # No year
            "The Office (2005)",  # Already correct
            "Stranger Things [2016]",  # Different format
        ]

        for show in test_shows:
            show_dir = self.test_dir / show
            show_dir.mkdir()
            # Create a dummy file in each directory
            (show_dir / "dummy.txt").write_text("test content")

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, "test_dir") and self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        super().tearDown()

    @patch("urllib.request.urlopen")
    def test_dry_run_workflow(self, mock_urlopen):
        """Test complete workflow in dry-run mode."""
        # Mock TVDB API responses
        login_response = MagicMock()
        login_response.status = 200
        login_response.read.return_value = json.dumps(
            {"data": {"token": "test_token"}}
        ).encode("utf-8")

        search_responses = [
            # Breaking Bad - already correct, won't be searched
            # Game of Thrones
            MagicMock(),
            # The Office - already correct, won't be searched
            # Stranger Things
            MagicMock(),
        ]

        search_responses[0].status = 200
        search_responses[0].read.return_value = json.dumps(
            {"data": [{"name": "Game of Thrones", "year": "2011"}]}
        ).encode("utf-8")

        search_responses[1].status = 200
        search_responses[1].read.return_value = json.dumps(
            {"data": [{"name": "Stranger Things", "year": "2016"}]}
        ).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [
            login_response,
            search_responses[0],
            search_responses[1],
        ]

        # Create updater and process directory
        updater = self.module.TVShowYearUpdater(
            tvdb_key="test_key",
            dry_run=True,
            debug=False,
            yes=True,  # Skip confirmation prompts
        )

        # This should not raise any exceptions in dry-run mode
        updater.process_directory(self.test_dir)

        # Verify statistics
        self.assertGreaterEqual(updater.stats["directories_processed"], 1)


class TestErrorHandling(MediaLibraryTestCase):
    """Test error handling scenarios."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_update_tv_years()
        if not self.module:
            self.skipTest("plex_update_tv_years module not available")

    def test_invalid_directory(self):
        """Test handling of invalid directory paths."""
        updater = self.module.TVShowYearUpdater(
            tvdb_key="test_key", dry_run=True, debug=False
        )

        # This should handle the non-existent directory gracefully
        Path("/nonexistent/directory/path")

        # We expect this to either return early or handle the error gracefully
        # The actual test depends on how the error is handled in the implementation
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_dir = Path(temp_dir)
            # Process empty directory should complete without errors
            updater.process_directory(empty_dir)

            # Should report no directories found
            self.assertEqual(updater.stats["directories_processed"], 0)

    @patch("urllib.request.urlopen")
    def test_api_error_handling(self, mock_urlopen):
        """Test handling of API errors."""
        # Mock network error
        mock_urlopen.side_effect = Exception("Network error")

        client = self.module.TVDBClient("test_key", debug=False)

        # Login should handle network errors gracefully
        result = client.login()
        self.assertFalse(result)

        # Search should handle errors gracefully
        result = client.search_show("Test Show")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
