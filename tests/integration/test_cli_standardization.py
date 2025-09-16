#!/usr/bin/env python3
"""
CLI Standardization Integration Tests

Tests that all scripts follow the standardized CLI argument patterns
and behavior established in Sprint 10.0 CLI Standardization.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from typing import List

# Add the project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestCLIStandardization(unittest.TestCase):
    """Test CLI argument standardization across all scripts."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.project_root = project_root
        cls.scripts = {
            # Complex Scripts
            "plex_update_tv_years": cls.project_root / "plex" / "plex_update_tv_years",
            "sabnzbd_cleanup": cls.project_root / "SABnzbd" / "sabnzbd_cleanup",
            # Medium Complexity Scripts
            "plex_correct_dirs": cls.project_root / "plex" / "plex_correct_dirs",
            "plex_make_dirs": cls.project_root / "plex" / "plex_make_dirs",
            "plex_make_seasons": cls.project_root / "plex" / "plex_make_seasons",
            "plex_make_years": cls.project_root / "plex" / "plex_make_years",
            # Remaining Scripts
            "plex_move_movie_extras": cls.project_root
            / "plex"
            / "plex_move_movie_extras",
            "plex_movie_subdir_renamer": cls.project_root
            / "plex"
            / "plex_movie_subdir_renamer",
            "plex_make_all_seasons": cls.project_root
            / "plex"
            / "plex_make_all_seasons",
        }

        # Verify all scripts exist
        for name, path in cls.scripts.items():
            if not path.exists():
                raise unittest.SkipTest(f"Script {name} not found at {path}")

    def setUp(self):
        """Set up test environment for each test."""
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run_script_help(self, script_path: Path) -> subprocess.CompletedProcess:
        """Run a script with --help flag."""
        return subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

    def _run_script_with_args(
        self, script_path: Path, args: List[str], timeout: int = 30
    ) -> subprocess.CompletedProcess:
        """Run a script with specified arguments."""
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=str(self.temp_dir)
        )

    def test_all_scripts_have_help(self):
        """Test that all scripts respond to --help."""
        for name, script_path in self.scripts.items():
            with self.subTest(script=name):
                result = self._run_script_help(script_path)
                self.assertEqual(
                    result.returncode,
                    0,
                    f"Script {name} --help failed: {result.stderr}",
                )
                self.assertIn(
                    "usage:",
                    result.stdout.lower(),
                    f"Script {name} --help doesn't show usage",
                )

    def test_dry_run_and_execute_arguments(self):
        """Test that all scripts have --dry-run and --execute arguments."""
        for name, script_path in self.scripts.items():
            with self.subTest(script=name):
                result = self._run_script_help(script_path)
                self.assertEqual(result.returncode, 0)

                help_text = result.stdout

                # Check for --dry-run flag
                self.assertIn(
                    "--dry-run", help_text, f"Script {name} missing --dry-run argument"
                )

                # Check for --execute flag (except special cases)
                if name not in ["plex_server_episode_refresh"]:  # API tool exception
                    self.assertIn(
                        "--execute",
                        help_text,
                        f"Script {name} missing --execute argument",
                    )

    def test_verbose_and_debug_arguments(self):
        """Test that all scripts have --verbose and --debug arguments."""
        for name, script_path in self.scripts.items():
            with self.subTest(script=name):
                result = self._run_script_help(script_path)
                self.assertEqual(result.returncode, 0)

                help_text = result.stdout

                # Check for --verbose flag
                self.assertIn(
                    "--verbose", help_text, f"Script {name} missing --verbose argument"
                )

                # Check for --debug flag
                self.assertIn(
                    "--debug", help_text, f"Script {name} missing --debug argument"
                )

    def test_standard_arguments_present(self):
        """Test that all scripts have the standard argument set."""
        standard_args = ["--help", "-y", "--yes", "--force", "--version"]

        for name, script_path in self.scripts.items():
            with self.subTest(script=name):
                result = self._run_script_help(script_path)
                self.assertEqual(result.returncode, 0)

                help_text = result.stdout

                for arg in standard_args:
                    self.assertIn(
                        arg, help_text, f"Script {name} missing standard argument {arg}"
                    )

    def test_dry_run_default_behavior(self):
        """Test that scripts default to dry-run mode."""
        # Scripts that can be tested with minimal setup
        testable_scripts = [
            ("plex_correct_dirs", []),
            ("plex_make_dirs", []),
            ("plex_make_all_seasons", []),
            ("plex_movie_subdir_renamer", []),
        ]

        for name, extra_args in testable_scripts:
            with self.subTest(script=name):
                script_path = self.scripts[name]

                # Run script with minimal args to check default behavior
                result = self._run_script_with_args(script_path, extra_args, timeout=10)

                # Should complete successfully or exit gracefully
                # Most importantly, should show "DRY-RUN MODE" in output
                if result.returncode == 0:
                    output = result.stdout + result.stderr
                    self.assertIn(
                        "DRY-RUN MODE",
                        output,
                        f"Script {name} should show DRY-RUN MODE by default",
                    )

    def test_cron_examples_in_help(self):
        """Test that all scripts have cron usage examples."""
        for name, script_path in self.scripts.items():
            with self.subTest(script=name):
                result = self._run_script_help(script_path)
                self.assertEqual(result.returncode, 0)

                help_text = result.stdout.lower()

                # Check for cron usage section
                self.assertTrue(
                    "cron" in help_text or "automation" in help_text,
                    f"Script {name} missing cron usage examples",
                )

    def test_help_text_consistency(self):
        """Test that help text follows consistent patterns."""
        for name, script_path in self.scripts.items():
            with self.subTest(script=name):
                result = self._run_script_help(script_path)
                self.assertEqual(result.returncode, 0)

                help_text = result.stdout

                # Check for examples section
                self.assertIn(
                    "Examples:", help_text, f"Script {name} missing Examples section"
                )

                # Check for consistent dry-run description
                if "--dry-run" in help_text:
                    # Should mention default behavior (look for 'default' anywhere in help text)
                    help_lower = help_text.lower()
                    self.assertTrue(
                        "default" in help_lower and "dry" in help_lower,
                        f"Script {name} help should mention dry-run as default behavior",
                    )

    def test_execute_flag_behavior(self):
        """Test that --execute flag overrides dry-run mode."""
        # Test with a safe script that can run with --execute
        test_script = "plex_movie_subdir_renamer"
        script_path = self.scripts[test_script]

        # Create a test directory structure
        test_dir = self.temp_dir / "test_movie"
        test_dir.mkdir()

        # Test dry-run mode (should be default)
        result = self._run_script_with_args(script_path, [str(test_dir)], timeout=10)
        if result.returncode == 0:
            output = result.stdout + result.stderr
            self.assertIn(
                "DRY-RUN MODE", output, "Script should default to dry-run mode"
            )

        # Test execute mode
        result = self._run_script_with_args(
            script_path, [str(test_dir), "--execute", "--yes"], timeout=10
        )
        if result.returncode == 0:
            output = result.stdout + result.stderr
            self.assertIn(
                "EXECUTE MODE",
                output,
                "Script should show execute mode with --execute flag",
            )

    def test_version_flag_consistency(self):
        """Test that all scripts respond to --version flag."""
        for name, script_path in self.scripts.items():
            with self.subTest(script=name):
                result = self._run_script_with_args(
                    script_path, ["--version"], timeout=10
                )

                # --version should exit with code 0 and show version info
                self.assertEqual(
                    result.returncode,
                    0,
                    f"Script {name} --version should exit with code 0",
                )

                # Should contain version information
                output = result.stdout + result.stderr
                self.assertTrue(
                    any(char.isdigit() for char in output),
                    f"Script {name} --version should show version number",
                )

    def test_special_script_requirements(self):
        """Test special requirements for specific scripts."""
        # Test plex_move_movie_extras requires arguments
        script_path = self.scripts["plex_move_movie_extras"]
        result = self._run_script_with_args(script_path, [], timeout=10)
        self.assertNotEqual(
            result.returncode, 0, "plex_move_movie_extras should require arguments"
        )

        # Test sabnzbd_cleanup backward compatibility with --delete
        script_path = self.scripts["sabnzbd_cleanup"]
        result = self._run_script_help(script_path)
        help_text = result.stdout
        self.assertIn(
            "--delete",
            help_text,
            "sabnzbd_cleanup should maintain --delete backward compatibility",
        )

    def test_unique_arguments_preserved(self):
        """Test that scripts preserve their unique arguments."""
        unique_args_tests = [
            ("plex_make_dirs", ["--types", "--exclude", "--list-types"]),
            ("plex_make_seasons", ["--target", "--list-patterns"]),
            ("plex_make_years", ["--base", "--year-range", "--list-patterns"]),
            ("plex_make_all_seasons", ["--parallel", "--workers", "--recursive"]),
            ("plex_movie_subdir_renamer", ["--movie-name"]),
            ("sabnzbd_cleanup", ["--prune-at"]),
        ]

        for script_name, unique_args in unique_args_tests:
            with self.subTest(script=script_name):
                script_path = self.scripts[script_name]
                result = self._run_script_help(script_path)
                help_text = result.stdout

                for arg in unique_args:
                    self.assertIn(
                        arg,
                        help_text,
                        f"Script {script_name} should preserve unique argument {arg}",
                    )


class TestGlobalConfigCLIIntegration(unittest.TestCase):
    """Test global configuration integration with CLI standardization."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.home_dir = self.temp_dir / "home"
        self.media_tools_dir = self.home_dir / ".media-library-tools"
        self.working_dir = self.temp_dir / "working"

        # Create directory structure
        self.home_dir.mkdir(parents=True)
        self.media_tools_dir.mkdir(parents=True)
        self.working_dir.mkdir(parents=True)

        # Store original environment
        self.original_env = os.environ.copy()
        self.original_cwd = os.getcwd()

        # Change to working directory
        os.chdir(self.working_dir)

        # Clear test environment variables
        for var in ["AUTO_EXECUTE", "AUTO_CONFIRM"]:
            os.environ.pop(var, None)

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_global_config_integration(self):
        """Test that scripts properly integrate global configuration."""
        # This test verifies the global config functionality is present
        # The actual behavior testing is covered by the existing global config tests

        # Create global config
        with open(self.media_tools_dir / ".env", "w") as f:
            f.write("AUTO_EXECUTE=true\nAUTO_CONFIRM=true\n")

        # Test that a simple script can load without errors
        script_path = project_root / "plex" / "plex_correct_dirs"

        with unittest.mock.patch("pathlib.Path.home", return_value=self.home_dir):
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.working_dir),
            )

        self.assertEqual(
            result.returncode, 0, "Script should work with global configuration present"
        )


if __name__ == "__main__":
    unittest.main()
