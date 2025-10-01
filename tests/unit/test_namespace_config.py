#!/usr/bin/env python3
"""
Unit Tests for MLT_ Namespace Configuration System

Tests the namespace-aware configuration functions in lib/core.py including:
- MIGRATION_MAP constant correctness
- Configuration priority order (CLI > ENV > .env)
- Deprecation warnings
- Support for both legacy and MLT_ prefixed variables
- Type conversions (str, bool, int)
- Warning suppression functionality

Author: Media Library Tools Project
Version: 1.0.0
"""

import os
import sys
import unittest
import tempfile
import argparse
from pathlib import Path
from unittest.mock import patch
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))

import core


class TestMigrationMap(unittest.TestCase):
    """Test MIGRATION_MAP constant correctness."""

    def test_migration_map_exists(self):
        """Verify MIGRATION_MAP constant exists and is a dict."""
        self.assertIsInstance(core.MIGRATION_MAP, dict)

    def test_migration_map_count(self):
        """Verify MIGRATION_MAP has all 23 legacy variables."""
        # Note: The count is 23, not 24. MLT_SUPPRESS_DEPRECATION_WARNINGS is MLT-only
        # and doesn't have a legacy equivalent, so it's not in the migration map.
        self.assertEqual(len(core.MIGRATION_MAP), 23)

    def test_migration_map_api_credentials(self):
        """Test API credential variable mappings."""
        expected = {
            'TVDB_API_KEY': 'MLT_TVDB_API_KEY',
            'PLEX_TOKEN': 'MLT_PLEX_TOKEN',
            'PLEX_SERVER': 'MLT_PLEX_SERVER',
            'OPENAI_API_KEY': 'MLT_OPENAI_API_KEY',
            'OPENAI_API_BASE_URL': 'MLT_OPENAI_API_BASE_URL',
            'OPENAI_API_MODEL': 'MLT_OPENAI_API_MODEL',
        }
        for legacy, mlt in expected.items():
            self.assertEqual(core.MIGRATION_MAP.get(legacy), mlt)

    def test_migration_map_automation_settings(self):
        """Test automation settings variable mappings."""
        expected = {
            'AUTO_EXECUTE': 'MLT_AUTO_EXECUTE',
            'AUTO_CONFIRM': 'MLT_AUTO_CONFIRM',
            'QUIET_MODE': 'MLT_QUIET_MODE',
            'AUTO_CLEANUP': 'MLT_AUTO_CLEANUP',
        }
        for legacy, mlt in expected.items():
            self.assertEqual(core.MIGRATION_MAP.get(legacy), mlt)

    def test_migration_map_debug_logging(self):
        """Test debug and logging variable mappings."""
        expected = {
            'DEBUG': 'MLT_DEBUG',
            'VERBOSE': 'MLT_VERBOSE',
            'PLEX_DEBUG': 'MLT_PLEX_DEBUG',
            'NO_EMOJIS': 'MLT_NO_EMOJIS',
        }
        for legacy, mlt in expected.items():
            self.assertEqual(core.MIGRATION_MAP.get(legacy), mlt)

    def test_reverse_migration_map(self):
        """Test REVERSE_MIGRATION_MAP is correct inverse."""
        self.assertIsInstance(core.REVERSE_MIGRATION_MAP, dict)
        self.assertEqual(len(core.REVERSE_MIGRATION_MAP), 23)

        # Verify bidirectional mapping
        for legacy, mlt in core.MIGRATION_MAP.items():
            self.assertEqual(core.REVERSE_MIGRATION_MAP.get(mlt), legacy)


class TestDeprecationWarnings(unittest.TestCase):
    """Test deprecation warning system."""

    def setUp(self):
        """Reset warning state before each test."""
        core._shown_deprecation_warnings.clear()
        core._deprecation_warnings_suppressed = None

    @patch('sys.stderr', new_callable=StringIO)
    @patch('core.is_non_interactive', return_value=False)
    def test_deprecation_warning_shown(self, mock_interactive, mock_stderr):
        """Test deprecation warning is displayed for legacy variables."""
        core._show_deprecation_warning('AUTO_EXECUTE', 'MLT_AUTO_EXECUTE', 'env_legacy')

        output = mock_stderr.getvalue()
        self.assertIn("Warning: Using legacy environment variable 'AUTO_EXECUTE'", output)
        self.assertIn("Please migrate to 'MLT_AUTO_EXECUTE'", output)
        self.assertIn("Legacy support will be removed", output)

    @patch('sys.stderr', new_callable=StringIO)
    @patch('core.is_non_interactive', return_value=False)
    def test_deprecation_warning_shown_once(self, mock_interactive, mock_stderr):
        """Test deprecation warning is shown only once per session."""
        # First call should show warning
        core._show_deprecation_warning('AUTO_EXECUTE', 'MLT_AUTO_EXECUTE', 'env_legacy')
        first_output = mock_stderr.getvalue()
        self.assertIn("Warning:", first_output)

        # Reset stderr
        mock_stderr.truncate(0)
        mock_stderr.seek(0)

        # Second call should not show warning
        core._show_deprecation_warning('AUTO_EXECUTE', 'MLT_AUTO_EXECUTE', 'env_legacy')
        second_output = mock_stderr.getvalue()
        self.assertEqual(second_output, "")

    @patch('sys.stderr', new_callable=StringIO)
    @patch('core.is_non_interactive', return_value=True)
    def test_deprecation_warning_suppressed_non_interactive(self, mock_interactive, mock_stderr):
        """Test deprecation warnings are suppressed in non-interactive mode."""
        core._show_deprecation_warning('AUTO_EXECUTE', 'MLT_AUTO_EXECUTE', 'env_legacy')

        output = mock_stderr.getvalue()
        self.assertEqual(output, "")

    @patch('sys.stderr', new_callable=StringIO)
    @patch('core.is_non_interactive', return_value=False)
    def test_deprecation_warning_suppressed_by_env_var(self, mock_interactive, mock_stderr):
        """Test MLT_SUPPRESS_DEPRECATION_WARNINGS environment variable."""
        with patch.dict(os.environ, {'MLT_SUPPRESS_DEPRECATION_WARNINGS': 'true'}):
            # Reset cache
            core._deprecation_warnings_suppressed = None

            core._show_deprecation_warning('AUTO_EXECUTE', 'MLT_AUTO_EXECUTE', 'env_legacy')

            output = mock_stderr.getvalue()
            self.assertEqual(output, "")


class TestConfigurationResolution(unittest.TestCase):
    """Test configuration resolution with namespace support."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary .env files
        self.temp_dir = tempfile.mkdtemp()
        self.local_env_path = os.path.join(self.temp_dir, '.env.local')
        self.global_env_path = os.path.join(self.temp_dir, '.env.global')

        # Clear deprecation warnings
        core._shown_deprecation_warnings.clear()
        core._deprecation_warnings_suppressed = None

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temp files
        if os.path.exists(self.local_env_path):
            os.remove(self.local_env_path)
        if os.path.exists(self.global_env_path):
            os.remove(self.global_env_path)
        os.rmdir(self.temp_dir)

    def test_priority_cli_over_env(self):
        """Test CLI arguments have highest priority."""
        with patch.dict(os.environ, {'MLT_DEBUG': 'false', 'DEBUG': 'false'}):
            args = argparse.Namespace(debug=True)
            result = core.read_config_value_with_namespace('DEBUG', cli_args=args, value_type='bool')
            self.assertTrue(result)

    def test_priority_mlt_env_over_legacy_env(self):
        """Test MLT_ environment variables take precedence over legacy."""
        with patch.dict(os.environ, {'MLT_DEBUG': 'true', 'DEBUG': 'false'}, clear=True):
            result = core.read_config_value_with_namespace('DEBUG', value_type='bool')
            self.assertTrue(result)

    def test_legacy_env_fallback(self):
        """Test legacy environment variables work as fallback."""
        with patch.dict(os.environ, {'DEBUG': 'true'}, clear=True):
            with patch('core.is_non_interactive', return_value=True):
                result = core.read_config_value_with_namespace('DEBUG', value_type='bool')
                self.assertTrue(result)

    def test_default_when_not_found(self):
        """Test default value is returned when variable not found."""
        with patch.dict(os.environ, {}, clear=True):
            result = core.read_config_value_with_namespace('DEBUG', default=False, value_type='bool')
            self.assertFalse(result)


class TestTypeConversions(unittest.TestCase):
    """Test type conversion functionality."""

    def test_bool_true_values(self):
        """Test boolean true value conversions."""
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'YES', 'on', 'ON']
        for value in true_values:
            with patch.dict(os.environ, {'MLT_TEST': value}, clear=True):
                result = core.read_config_value_with_namespace('TEST', value_type='bool')
                self.assertTrue(result, f"Failed for value: {value}")

    def test_bool_false_values(self):
        """Test boolean false value conversions."""
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'NO', 'off', 'OFF']
        for value in false_values:
            with patch.dict(os.environ, {'MLT_TEST': value}, clear=True):
                result = core.read_config_value_with_namespace('TEST', value_type='bool')
                self.assertFalse(result, f"Failed for value: {value}")

    def test_int_conversion(self):
        """Test integer type conversion."""
        with patch.dict(os.environ, {'MLT_TEST': '42'}, clear=True):
            result = core.read_config_value_with_namespace('TEST', value_type='int')
            self.assertEqual(result, 42)
            self.assertIsInstance(result, int)

    def test_int_conversion_invalid(self):
        """Test integer conversion with invalid value returns default."""
        with patch.dict(os.environ, {'MLT_TEST': 'not_a_number'}, clear=True):
            result = core.read_config_value_with_namespace('TEST', default=99, value_type='int')
            self.assertEqual(result, 99)

    def test_str_conversion(self):
        """Test string type conversion (default)."""
        with patch.dict(os.environ, {'MLT_TEST': 'hello world'}, clear=True):
            result = core.read_config_value_with_namespace('TEST', value_type='str')
            self.assertEqual(result, 'hello world')
            self.assertIsInstance(result, str)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing code."""

    def test_read_config_value_delegates(self):
        """Test read_config_value() delegates to namespace version."""
        with patch.dict(os.environ, {'MLT_DEBUG': 'true'}, clear=True):
            result = core.read_config_value('DEBUG', value_type='bool')
            self.assertTrue(result)

    def test_read_config_bool_delegates(self):
        """Test read_config_bool() delegates to namespace version."""
        with patch.dict(os.environ, {'MLT_DEBUG': 'true'}, clear=True):
            result = core.read_config_bool('DEBUG')
            self.assertTrue(result)

    def test_legacy_variables_still_work(self):
        """Test legacy variables work without MLT_ prefix."""
        with patch.dict(os.environ, {'DEBUG': 'true'}, clear=True):
            with patch('core.is_non_interactive', return_value=True):
                result = core.read_config_bool('DEBUG')
                self.assertTrue(result)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience wrapper functions."""

    def test_read_config_bool_with_namespace(self):
        """Test read_config_bool_with_namespace() convenience function."""
        with patch.dict(os.environ, {'MLT_VERBOSE': 'yes'}, clear=True):
            result = core.read_config_bool_with_namespace('VERBOSE')
            self.assertTrue(result)
            self.assertIsInstance(result, bool)

    def test_read_config_bool_with_namespace_default(self):
        """Test read_config_bool_with_namespace() with default value."""
        with patch.dict(os.environ, {}, clear=True):
            result = core.read_config_bool_with_namespace('NONEXISTENT', default=True)
            self.assertTrue(result)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMigrationMap))
    suite.addTests(loader.loadTestsFromTestCase(TestDeprecationWarnings))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationResolution))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeConversions))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
