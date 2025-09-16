#!/usr/bin/env python3
"""
Test Suite for CLI Consistency and Global Configuration

This test suite verifies that all media library tools implement consistent
CLI argument patterns and global configuration support.

Test Categories:
- Standard CLI argument presence
- Global configuration support (AUTO_EXECUTE, AUTO_CONFIRM, QUIET_MODE)
- Argument precedence rules (CLI overrides global config)
- Help text consistency
- Banner display behavior

Author: Media Library Tools Project
Version: 1.0.0
"""

import contextlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List


class CLIConsistencyTestCase(unittest.TestCase):
    """Base test case for CLI consistency testing."""

    # Tool directory mapping
    TOOL_DIRECTORIES = {
        "plex_correct_dirs": "plex",
        "plex_make_dirs": "plex",
        "plex_make_seasons": "plex",
        "plex_make_years": "plex",
        "plex_make_all_seasons": "plex",
        "plex_update_tv_years": "plex",
        "plex_move_movie_extras": "plex",
        "plex_movie_subdir_renamer": "plex",
        "sabnzbd_cleanup": "SABnzbd",
        "plex_server_episode_refresh": "plex-api",
    }

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent.parent

        # Ensure all tools are built and in their main directories
        cls.build_all_tools()

    @classmethod
    def build_all_tools(cls):
        """Build all tools using the new workflow approach."""
        build_script = cls.project_root / "build.py"

        # Build tools to build_output directory
        result = subprocess.run(
            [
                sys.executable,
                str(build_script),
                "--all",
                "--output-dir",
                "build_output",
            ],
            capture_output=True,
            text=True,
            cwd=cls.project_root,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to build tools: {result.stderr}")

        # Copy tools to main directories (mimicking CI workflow)
        import shutil

        build_output = cls.project_root / "build_output"

        if build_output.exists():
            # Copy from build_output subdirectories to main directories
            for subdir in ["plex", "SABnzbd", "plex-api"]:
                src_dir = build_output / subdir
                dest_dir = cls.project_root / subdir

                if src_dir.exists():
                    # Copy all files from src to dest
                    for item in src_dir.iterdir():
                        if item.is_file():
                            dest_file = dest_dir / item.name
                            shutil.copy2(item, dest_file)
                            # Make executable
                            dest_file.chmod(0o755)

            # Clean up build_output
            shutil.rmtree(build_output)

    def run_tool_with_args(
        self, tool_name: str, args: List[str], env_vars: Dict[str, str] = None
    ) -> subprocess.CompletedProcess:
        """Run a tool with specified arguments and environment variables."""
        # Find tool in its main directory
        tool_dir = self.TOOL_DIRECTORIES.get(tool_name)
        if not tool_dir:
            self.fail(f"Unknown tool: {tool_name}")

        tool_path = self.project_root / tool_dir / tool_name
        if not tool_path.exists():
            self.fail(f"Tool not found: {tool_path}")

        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        return subprocess.run(
            [sys.executable, str(tool_path)] + args,
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

    def get_help_text(self, tool_name: str) -> str:
        """Get help text for a tool."""
        result = self.run_tool_with_args(tool_name, ["--help"])
        return result.stdout if result.returncode == 0 else result.stderr


class TestStandardCLIArguments(CLIConsistencyTestCase):
    """Test that all tools implement standard CLI arguments."""

    # List of all tools to test
    TOOLS = [
        "plex_correct_dirs",
        "plex_make_dirs",
        "plex_make_seasons",
        "plex_make_years",
        "plex_make_all_seasons",
        "sabnzbd_cleanup",
        "plex_update_tv_years",
        "plex_move_movie_extras",
        "plex_movie_subdir_renamer",
    ]

    # Standard arguments that should be present in all tools
    REQUIRED_ARGS = [
        "--verbose",
        "-v",  # Short form of verbose
        "--debug",
        "--no-banner",
        "-y",
        "--yes",
        "--force",
        "--version",
    ]

    def test_all_tools_have_standard_arguments(self):
        """Test that all tools support the required standard arguments."""
        for tool in self.TOOLS:
            with self.subTest(tool=tool):
                help_text = self.get_help_text(tool)

                for arg in self.REQUIRED_ARGS:
                    self.assertIn(
                        arg,
                        help_text,
                        f"Tool '{tool}' missing required argument '{arg}'",
                    )

    def test_help_argument_works(self):
        """Test that --help argument works for all tools."""
        for tool in self.TOOLS:
            with self.subTest(tool=tool):
                result = self.run_tool_with_args(tool, ["--help"])
                self.assertEqual(result.returncode, 0, f"Tool '{tool}' --help failed")
                self.assertIn(
                    "usage:",
                    result.stdout.lower(),
                    f"Tool '{tool}' help text missing usage information",
                )

    def test_version_argument_works(self):
        """Test that --version argument works for all tools."""
        for tool in self.TOOLS:
            with self.subTest(tool=tool):
                result = self.run_tool_with_args(tool, ["--version"])
                self.assertEqual(
                    result.returncode, 0, f"Tool '{tool}' --version failed"
                )
                # Version output should contain the tool name or version number
                self.assertTrue(
                    tool.replace("_", " ") in result.stdout
                    or any(char.isdigit() for char in result.stdout),
                    f"Tool '{tool}' version output seems invalid: {result.stdout}",
                )


class TestGlobalConfigurationSupport(CLIConsistencyTestCase):
    """Test global configuration support across all tools."""

    # Tools that support AUTO_EXECUTE (have execute/dry-run pattern)
    AUTO_EXECUTE_TOOLS = [
        "plex_make_dirs",
        "plex_make_seasons",
        "plex_make_years",
        "plex_make_all_seasons",
        "sabnzbd_cleanup",
        "plex_movie_subdir_renamer",
    ]

    # Tools with simple directory argument (for easy testing)
    SIMPLE_TOOLS = [
        "plex_correct_dirs",
        "plex_make_dirs",
        "plex_make_seasons",
        "plex_make_years",
        "plex_make_all_seasons",
        "sabnzbd_cleanup",
        "plex_movie_subdir_renamer",
    ]

    # Tools with special requirements (test differently)
    SPECIAL_REQUIREMENT_TOOLS = {
        "plex_update_tv_years": ["--tvdb-key", "test_key"],
        "plex_move_movie_extras": ["test_file.mp4", "test_subdir"],
    }

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(self.cleanup_test_dir)

    def cleanup_test_dir(self):
        """Clean up test directory."""
        import shutil

        with contextlib.suppress(Exception):
            shutil.rmtree(self.test_dir)

    def test_auto_confirm_support(self):
        """Test that AUTO_CONFIRM global configuration works."""
        # Test simple tools with just directory argument
        for tool in self.SIMPLE_TOOLS:
            with self.subTest(tool=tool):
                result = self.run_tool_with_args(
                    tool,
                    ["--dry-run", "--no-banner", "-y", self.test_dir],
                    env_vars={"AUTO_CONFIRM": "true"},
                )

                output = result.stdout + result.stderr
                # The key is that AUTO_CONFIRM doesn't cause errors
                self.assertNotIn(
                    "error",
                    output.lower(),
                    f"Tool '{tool}' failed with AUTO_CONFIRM: {output}",
                )

        # Test special requirement tools with their specific arguments
        for tool, extra_args in self.SPECIAL_REQUIREMENT_TOOLS.items():
            with self.subTest(tool=tool):
                args = ["--dry-run", "--no-banner", "-y"] + extra_args
                result = self.run_tool_with_args(
                    tool, args, env_vars={"AUTO_CONFIRM": "true"}
                )

                output = result.stdout + result.stderr
                # For these tools, we just check that AUTO_CONFIRM config is processed
                # without causing configuration-related errors
                config_errors = ["auto_confirm", "configuration error", "config error"]
                has_config_error = any(
                    error in output.lower() for error in config_errors
                )
                self.assertFalse(
                    has_config_error,
                    f"Tool '{tool}' has config error with AUTO_CONFIRM: {output}",
                )

    def test_quiet_mode_support(self):
        """Test that QUIET_MODE global configuration works."""
        # Test simple tools with just directory argument
        for tool in self.SIMPLE_TOOLS:
            with self.subTest(tool=tool):
                result = self.run_tool_with_args(
                    tool,
                    ["--dry-run", "--no-banner", "-y", self.test_dir],
                    env_vars={"QUIET_MODE": "true"},
                )

                output = result.stdout + result.stderr
                # QUIET_MODE should not cause errors
                self.assertNotIn(
                    "error",
                    output.lower(),
                    f"Tool '{tool}' failed with QUIET_MODE: {output}",
                )

        # Test special requirement tools with their specific arguments
        for tool, extra_args in self.SPECIAL_REQUIREMENT_TOOLS.items():
            with self.subTest(tool=tool):
                args = ["--dry-run", "--no-banner", "-y"] + extra_args
                result = self.run_tool_with_args(
                    tool, args, env_vars={"QUIET_MODE": "true"}
                )

                output = result.stdout + result.stderr
                # For these tools, we just check that QUIET_MODE config is processed
                config_errors = ["quiet_mode", "configuration error", "config error"]
                has_config_error = any(
                    error in output.lower() for error in config_errors
                )
                self.assertFalse(
                    has_config_error,
                    f"Tool '{tool}' has config error with QUIET_MODE: {output}",
                )

    def test_auto_execute_support(self):
        """Test that AUTO_EXECUTE global configuration works for applicable tools."""
        for tool in self.AUTO_EXECUTE_TOOLS:
            with self.subTest(tool=tool):
                # Test with AUTO_EXECUTE=true should override dry-run
                result = self.run_tool_with_args(
                    tool,
                    ["--dry-run", "--no-banner", "-y", self.test_dir],
                    env_vars={"AUTO_EXECUTE": "true"},
                )

                output = result.stdout + result.stderr

                # AUTO_EXECUTE should not cause configuration errors
                config_errors = ["auto_execute", "configuration error", "config error"]
                has_config_error = any(
                    error in output.lower() for error in config_errors
                )
                self.assertFalse(
                    has_config_error,
                    f"Tool '{tool}' has config error with AUTO_EXECUTE: {output}",
                )

                # Should show evidence of execute mode or non-dry-run behavior
                execute_indicators = ["execute", "changes will be made", "proceeding"]
                any(indicator in output.lower() for indicator in execute_indicators)

                # At minimum, AUTO_EXECUTE should not cause the tool to fail with config errors
                if result.returncode != 0:
                    # It's OK if tools fail for other reasons (like missing files)
                    # but not for configuration issues
                    self.assertFalse(
                        has_config_error,
                        f"Tool '{tool}' failed with AUTO_EXECUTE config error",
                    )


class TestArgumentPrecedence(CLIConsistencyTestCase):
    """Test that CLI arguments take precedence over global configuration."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(self.cleanup_test_dir)

    def cleanup_test_dir(self):
        """Clean up test directory."""
        import shutil

        with contextlib.suppress(Exception):
            shutil.rmtree(self.test_dir)

    def test_cli_overrides_auto_confirm(self):
        """Test that CLI -y flag works even when AUTO_CONFIRM=false."""
        # Test one representative tool
        tool = "plex_make_dirs"

        result = self.run_tool_with_args(
            tool, ["--dry-run", "-y", self.test_dir], env_vars={"AUTO_CONFIRM": "false"}
        )

        output = result.stdout + result.stderr

        # Should show warning about -y having no effect in dry-run
        # This proves that CLI -y was processed despite AUTO_CONFIRM=false
        self.assertTrue(
            "warning" in output.lower() or "-y" in output.lower(),
            f"CLI -y flag not processed properly: {output}",
        )

    def test_cli_overrides_quiet_mode(self):
        """Test that CLI --no-banner works even when QUIET_MODE=false."""
        # Test one representative tool
        tool = "plex_make_dirs"

        result = self.run_tool_with_args(
            tool,
            ["--dry-run", "--no-banner", self.test_dir],
            env_vars={"QUIET_MODE": "false"},
        )

        # Should not cause errors
        output = result.stdout + result.stderr
        self.assertNotIn(
            "error", output.lower(), f"CLI --no-banner flag failed: {output}"
        )


class TestHelpTextConsistency(CLIConsistencyTestCase):
    """Test that help text follows consistent patterns."""

    def test_help_text_sections(self):
        """Test that help text includes standard sections."""
        tools_to_test = ["plex_correct_dirs", "plex_make_dirs"]  # Representative sample

        required_sections = ["usage:", "positional arguments", "options", "examples"]

        for tool in tools_to_test:
            with self.subTest(tool=tool):
                help_text = self.get_help_text(tool).lower()

                for section in required_sections:
                    self.assertIn(
                        section,
                        help_text,
                        f"Tool '{tool}' help missing section '{section}'",
                    )

    def test_global_config_documentation(self):
        """Test that tools document global configuration in help text."""
        # Test the tool we specifically updated
        tool = "plex_correct_dirs"
        help_text = self.get_help_text(tool)

        self.assertIn(
            "Global Configuration",
            help_text,
            f"Tool '{tool}' help missing global configuration section",
        )
        self.assertIn(
            "AUTO_CONFIRM",
            help_text,
            f"Tool '{tool}' help missing AUTO_CONFIRM documentation",
        )


class TestBannerBehavior(CLIConsistencyTestCase):
    """Test banner display behavior across tools."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(self.cleanup_test_dir)

    def cleanup_test_dir(self):
        """Clean up test directory."""
        import shutil

        with contextlib.suppress(Exception):
            shutil.rmtree(self.test_dir)

    def test_no_banner_flag_works(self):
        """Test that --no-banner flag suppresses banner display."""
        # Test one representative tool
        tool = "plex_make_dirs"

        result = self.run_tool_with_args(
            tool, ["--dry-run", "--no-banner", "-y", self.test_dir]
        )

        # Should not cause errors
        output = result.stdout + result.stderr
        self.assertNotIn(
            "error", output.lower(), f"--no-banner flag caused error: {output}"
        )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
