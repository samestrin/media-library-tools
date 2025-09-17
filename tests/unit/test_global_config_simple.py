#!/usr/bin/env python3
"""
Simple Unit Tests for Global Configuration Feature

Tests the read_global_config_bool() function from a representative script
to verify proper environment variable reading with the defined hierarchy.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add the project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestGlobalConfigSimple(unittest.TestCase):
    """Simple test cases for global configuration functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for testing
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

        # Clear environment variables that might interfere
        for var in ["AUTO_EXECUTE", "AUTO_CONFIRM"]:
            os.environ.pop(var, None)

        # Load the function from a representative script
        self.read_func = self._load_read_global_config_bool()

    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment and directory
        os.environ.clear()
        os.environ.update(self.original_env)
        os.chdir(self.original_cwd)

        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _load_read_global_config_bool(self):
        """Load the read_global_config_bool function from plex_correct_dirs."""
        script_path = project_root / "plex" / "plex_correct_dirs"

        if not script_path.exists():
            self.fail(f"Script file does not exist: {script_path}")

        try:
            # Read the script and extract the function
            namespace = {"__file__": str(script_path)}

            # Add necessary imports that the script might need
            # Handle fcntl import with Windows compatibility
            try:
                import fcntl
            except ImportError:
                fcntl = None  # Windows compatibility

            namespace.update(
                {
                    "os": os,
                    "sys": sys,
                    "Path": Path,
                    "argparse": __import__("argparse"),
                    "shutil": __import__("shutil"),
                    "tempfile": __import__("tempfile"),
                    "fcntl": fcntl,
                    "re": __import__("re"),
                }
            )

            with open(script_path, encoding="utf-8") as f:
                script_content = f.read()

            # Find just the function definition
            lines = script_content.split("\n")
            func_start = None
            func_end = None

            for i, line in enumerate(lines):
                if line.startswith("def read_global_config_bool("):
                    func_start = i
                elif (
                    func_start is not None
                    and line
                    and not line.startswith(" ")
                    and not line.startswith("\t")
                ):
                    func_end = i
                    break

            if func_start is None:
                self.fail("Function read_global_config_bool not found")

            if func_end is None:
                func_end = len(lines)

            # Extract function code
            func_lines = lines[func_start:func_end]
            func_code = "\n".join(func_lines)

            # Execute just the function definition
            exec(func_code, namespace)

            if "read_global_config_bool" not in namespace:
                self.fail("Function read_global_config_bool not loaded properly")

            return namespace["read_global_config_bool"]

        except Exception as e:
            self.fail(f"Could not load read_global_config_bool: {e}")

    def test_environment_variable_priority(self):
        """Test that environment variables take precedence over .env files."""
        # Set environment variable
        os.environ["AUTO_EXECUTE"] = "true"

        # Create local .env with different value
        with open(self.working_dir / ".env", "w") as f:
            f.write("AUTO_EXECUTE=false\n")

        # Create global .env with different value
        with open(self.media_tools_dir / ".env", "w") as f:
            f.write("AUTO_EXECUTE=false\n")

        with patch("pathlib.Path.home", return_value=self.home_dir):
            result = self.read_func("AUTO_EXECUTE", False)
            self.assertTrue(result, "Environment variable should take precedence")

    def test_local_env_priority_over_global(self):
        """Test that local .env takes precedence over global .env."""
        # Create local .env
        with open(self.working_dir / ".env", "w") as f:
            f.write("AUTO_CONFIRM=true\n")

        # Create global .env with different value
        with open(self.media_tools_dir / ".env", "w") as f:
            f.write("AUTO_CONFIRM=false\n")

        with patch("pathlib.Path.home", return_value=self.home_dir):
            result = self.read_func("AUTO_CONFIRM", False)
            self.assertTrue(result, "Local .env should take precedence over global")

    def test_global_env_fallback(self):
        """Test that global .env is used when no local .env or environment variable."""
        # Create only global .env
        with open(self.media_tools_dir / ".env", "w") as f:
            f.write("AUTO_EXECUTE=true\nAUTO_CONFIRM=false\n")

        with patch("pathlib.Path.home", return_value=self.home_dir):
            # Test AUTO_EXECUTE=true
            result = self.read_func("AUTO_EXECUTE", False)
            self.assertTrue(result, "Global .env should be used for AUTO_EXECUTE")

            # Test AUTO_CONFIRM=false
            result = self.read_func(
                "AUTO_CONFIRM", True
            )  # default True to test override
            self.assertFalse(result, "Global .env should be used for AUTO_CONFIRM")

    def test_default_value_when_no_config(self):
        """Test that default value is returned when no configuration is found."""
        # Don't create any .env files or set environment variables

        with patch("pathlib.Path.home", return_value=self.home_dir):
            # Test with default False
            result = self.read_func("AUTO_EXECUTE", False)
            self.assertFalse(result, "Should return default False when no config")

            # Test with default True
            result = self.read_func("AUTO_CONFIRM", True)
            self.assertTrue(result, "Should return default True when no config")

    def test_boolean_value_parsing(self):
        """Test parsing of various boolean value formats."""
        test_cases = [
            # True values
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("YES", True),
            ("on", True),
            # False values
            ("false", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("invalid", False),  # Invalid values should be treated as false
            ("", False),  # Empty string should be treated as false
        ]

        for test_value, expected in test_cases:
            with self.subTest(value=test_value, expected=expected):
                os.environ["TEST_BOOL_VAR"] = test_value

                result = self.read_func("TEST_BOOL_VAR", False)
                self.assertEqual(
                    result, expected, f"Value '{test_value}' should parse to {expected}"
                )

                # Clean up
                del os.environ["TEST_BOOL_VAR"]

    def test_missing_env_files_handling(self):
        """Test graceful handling when .env files don't exist or can't be read."""
        with patch("pathlib.Path.home", return_value=self.home_dir):
            # Should not raise exception and return default
            result = self.read_func("NONEXISTENT_VAR", True)
            self.assertTrue(result, "Should return default when no .env files exist")

    def test_malformed_env_file_handling(self):
        """Test handling of malformed .env files."""
        # Create malformed .env file
        malformed_content = """
# This is a comment
VALID_VAR=true
INVALID_LINE_NO_EQUALS
=NO_VAR_NAME
AUTO_EXECUTE=true
TRAILING_SPACES=true
"""
        with open(self.working_dir / ".env", "w") as f:
            f.write(malformed_content)

        with patch("pathlib.Path.home", return_value=self.home_dir):
            # Should handle malformed file gracefully
            result = self.read_func("AUTO_EXECUTE", False)
            self.assertTrue(result, "Should parse valid line from malformed file")

            # Non-existent var should return default
            result = self.read_func("NONEXISTENT", True)
            self.assertTrue(result, "Should return default for non-existent var")

    def test_case_sensitivity(self):
        """Test that variable names are case-sensitive."""
        os.environ["AUTO_EXECUTE"] = "false"  # uppercase
        os.environ["auto_execute"] = "true"  # lowercase  # noqa: SIM112

        # Should match exact case
        result = self.read_func("AUTO_EXECUTE", True)
        self.assertFalse(result, "Should match exact case AUTO_EXECUTE")

        result = self.read_func("auto_execute", False)
        self.assertTrue(result, "Should match exact case auto_execute")


if __name__ == "__main__":
    unittest.main()
