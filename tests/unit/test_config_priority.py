#!/usr/bin/env python3
"""
Unit Tests for Configuration Priority System
Tests the CLI > ENV > Local .env > Global .env priority chain
"""

import argparse
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import configuration functions
from lib.core import (
    ConfigCache,
    read_config_value,
    read_config_bool,
    read_local_env_file,
    get_config_source,
    debug_config_resolution,
    validate_config_setup,
    _config_cache,
)


class TestConfigPriorityChain(unittest.TestCase):
    """Test configuration priority: CLI > ENV > Local .env > Global .env"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Clear environment variables
        self.env_backup = {}
        for key in ['TEST_KEY', 'DEBUG', 'AUTO_EXECUTE']:
            if key in os.environ:
                self.env_backup[key] = os.environ[key]
                del os.environ[key]

        # Clear cache
        _config_cache.clear_cache()

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)

        # Restore environment
        for key, value in self.env_backup.items():
            os.environ[key] = value

        # Remove test files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_priority_highest(self):
        """Test that CLI arguments have highest priority"""
        # Create .env files
        with open('.env', 'w') as f:
            f.write('TEST_KEY=local\n')

        global_env = Path.home() / '.media-library-tools' / '.env'
        global_env.parent.mkdir(parents=True, exist_ok=True)
        with open(global_env, 'w') as f:
            f.write('TEST_KEY=global\n')

        # Set environment variable
        os.environ['TEST_KEY'] = 'env'

        # Create CLI args with TEST_KEY
        args = argparse.Namespace(test_key='cli')

        value = read_config_value('TEST_KEY', cli_args=args)
        self.assertEqual(value, 'cli')

        source = get_config_source('TEST_KEY', cli_args=args)
        self.assertEqual(source, 'cli')

    def test_env_priority_second(self):
        """Test that ENV variables have second priority"""
        # Create .env files
        with open('.env', 'w') as f:
            f.write('TEST_KEY=local\n')

        global_env = Path.home() / '.media-library-tools' / '.env'
        global_env.parent.mkdir(parents=True, exist_ok=True)
        with open(global_env, 'w') as f:
            f.write('TEST_KEY=global\n')

        # Set environment variable (no CLI args)
        os.environ['TEST_KEY'] = 'env'

        value = read_config_value('TEST_KEY')
        self.assertEqual(value, 'env')

        source = get_config_source('TEST_KEY')
        self.assertEqual(source, 'env')

    def test_local_env_priority_third(self):
        """Test that local .env has third priority"""
        # Create local .env
        with open('.env', 'w') as f:
            f.write('TEST_KEY=local\n')

        # Create global .env
        global_env = Path.home() / '.media-library-tools' / '.env'
        global_env.parent.mkdir(parents=True, exist_ok=True)
        with open(global_env, 'w') as f:
            f.write('TEST_KEY=global\n')

        # No CLI args, no environment variable
        value = read_config_value('TEST_KEY')
        self.assertEqual(value, 'local')

        source = get_config_source('TEST_KEY')
        self.assertEqual(source, 'local_env')

    def test_global_env_priority_fourth(self):
        """Test that global .env has lowest priority"""
        # Create global .env only
        global_env = Path.home() / '.media-library-tools' / '.env'
        global_env.parent.mkdir(parents=True, exist_ok=True)
        with open(global_env, 'w') as f:
            f.write('TEST_KEY=global\n')

        # No CLI args, no environment variable, no local .env
        value = read_config_value('TEST_KEY')
        self.assertEqual(value, 'global')

        source = get_config_source('TEST_KEY')
        self.assertEqual(source, 'global_env')

    def test_default_value_when_not_found(self):
        """Test that default value is returned when key not found anywhere"""
        value = read_config_value('NONEXISTENT_KEY', default='default_value')
        self.assertEqual(value, 'default_value')

        source = get_config_source('NONEXISTENT_KEY')
        self.assertEqual(source, 'not_found')


class TestBooleanConversion(unittest.TestCase):
    """Test boolean value conversion"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        _config_cache.clear_cache()

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_boolean_true_values(self):
        """Test that various true values are recognized"""
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']

        for value in true_values:
            with open('.env', 'w') as f:
                f.write(f'TEST_BOOL={value}\n')

            _config_cache.clear_cache()
            result = read_config_bool('TEST_BOOL', default=False)
            self.assertTrue(result, f"Failed for value: {value}")

    def test_boolean_false_values(self):
        """Test that non-true values are considered false"""
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', 'random']

        for value in false_values:
            with open('.env', 'w') as f:
                f.write(f'TEST_BOOL={value}\n')

            _config_cache.clear_cache()
            result = read_config_bool('TEST_BOOL', default=False)
            self.assertFalse(result, f"Failed for value: {value}")


class TestConfigCache(unittest.TestCase):
    """Test configuration caching functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.cache = ConfigCache(ttl_seconds=1)

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_stores_and_retrieves(self):
        """Test that cache stores and retrieves values"""
        with open('.env', 'w') as f:
            f.write('KEY1=value1\nKEY2=value2\n')

        result1 = self.cache.get_env_file('.env')
        self.assertIsNotNone(result1)
        self.assertEqual(result1['KEY1'], 'value1')
        self.assertEqual(result1['KEY2'], 'value2')

        # Should retrieve from cache (not disk)
        result2 = self.cache.get_env_file('.env')
        self.assertEqual(result1, result2)

    def test_cache_ttl_expiration(self):
        """Test that cache expires after TTL"""
        with open('.env', 'w') as f:
            f.write('KEY=value1\n')

        result1 = self.cache.get_env_file('.env')
        self.assertEqual(result1['KEY'], 'value1')

        # Wait for TTL to expire
        time.sleep(1.1)

        # Update file
        with open('.env', 'w') as f:
            f.write('KEY=value2\n')

        result2 = self.cache.get_env_file('.env')
        self.assertEqual(result2['KEY'], 'value2')

    def test_cache_thread_safety(self):
        """Test that cache is thread-safe"""
        with open('.env', 'w') as f:
            f.write('KEY=value\n')

        results = []
        errors = []

        def read_cache():
            try:
                for _ in range(10):
                    result = self.cache.get_env_file('.env')
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_cache) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 50)

    def test_cache_clear(self):
        """Test that cache can be cleared"""
        with open('.env', 'w') as f:
            f.write('KEY=value1\n')

        result1 = self.cache.get_env_file('.env')
        self.assertIsNotNone(result1)

        self.cache.clear_cache()

        # Update file
        with open('.env', 'w') as f:
            f.write('KEY=value2\n')

        result2 = self.cache.get_env_file('.env')
        self.assertEqual(result2['KEY'], 'value2')


class TestEnvFileReading(unittest.TestCase):
    """Test .env file reading and parsing"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        _config_cache.clear_cache()

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_read_simple_env_file(self):
        """Test reading simple key=value pairs"""
        with open('.env', 'w') as f:
            f.write('KEY1=value1\n')
            f.write('KEY2=value2\n')

        result = read_local_env_file('.env', use_cache=False)
        self.assertEqual(result['KEY1'], 'value1')
        self.assertEqual(result['KEY2'], 'value2')

    def test_skip_comments(self):
        """Test that comments are skipped"""
        with open('.env', 'w') as f:
            f.write('# This is a comment\n')
            f.write('KEY=value\n')
            f.write('# Another comment\n')

        result = read_local_env_file('.env', use_cache=False)
        self.assertEqual(result['KEY'], 'value')
        self.assertEqual(len(result), 1)

    def test_skip_empty_lines(self):
        """Test that empty lines are skipped"""
        with open('.env', 'w') as f:
            f.write('KEY1=value1\n')
            f.write('\n')
            f.write('KEY2=value2\n')

        result = read_local_env_file('.env', use_cache=False)
        self.assertEqual(len(result), 2)

    def test_remove_quotes_from_values(self):
        """Test that quotes are removed from values"""
        with open('.env', 'w') as f:
            f.write('KEY1="value with spaces"\n')
            f.write("KEY2='single quotes'\n")
            f.write('KEY3=no quotes\n')

        result = read_local_env_file('.env', use_cache=False)
        self.assertEqual(result['KEY1'], 'value with spaces')
        self.assertEqual(result['KEY2'], 'single quotes')
        self.assertEqual(result['KEY3'], 'no quotes')

    def test_handle_missing_file(self):
        """Test handling of missing .env file"""
        result = read_local_env_file('nonexistent.env', use_cache=False)
        self.assertEqual(result, {})


class TestValidateConfigSetup(unittest.TestCase):
    """Test configuration validation"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_no_env_files(self):
        """Test validation when no .env files exist"""
        result = validate_config_setup()

        self.assertTrue(result['valid'])
        self.assertEqual(result['files']['local_env'], 'not_found')
        # Note: global_env may exist if created by other tests or user setup
        self.assertIn(result['files']['global_env'], ['exists', 'not_found'])

    def test_validate_with_local_env(self):
        """Test validation with local .env"""
        with open('.env', 'w') as f:
            f.write('KEY=value\n')

        result = validate_config_setup()

        self.assertTrue(result['valid'])
        self.assertEqual(result['files']['local_env'], 'exists')

    def test_validate_unreadable_env(self):
        """Test validation with unreadable .env"""
        with open('.env', 'w') as f:
            f.write('KEY=value\n')

        # Make file unreadable
        os.chmod('.env', 0o000)

        try:
            result = validate_config_setup()
            # Should report issue
            self.assertFalse(result['valid'])
            self.assertGreater(len(result['warnings']), 0)
        finally:
            # Restore permissions for cleanup
            os.chmod('.env', 0o644)


if __name__ == '__main__':
    unittest.main()
