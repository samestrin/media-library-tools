#!/usr/bin/env python3
"""
Integration Tests for Configuration Priority System
Tests real-world configuration scenarios across different environments
"""

import argparse
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.core import read_config_bool, read_config_value, get_config_source, _config_cache


class TestDevelopmentEnvironment(unittest.TestCase):
    """Test configuration in development environment with local .env"""

    def setUp(self):
        """Set up development environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Clear cache
        _config_cache.clear_cache()

        # Clear test environment variables
        for key in ['DEBUG', 'VERBOSE', 'AUTO_EXECUTE']:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_development_with_local_env(self):
        """Test typical development scenario with local .env file"""
        # Create local .env with development settings
        with open('.env', 'w') as f:
            f.write('DEBUG=true\n')
            f.write('VERBOSE=true\n')
            f.write('AUTO_EXECUTE=false\n')

        # Read configuration (no CLI args, no environment vars)
        debug = read_config_bool('DEBUG', default=False)
        verbose = read_config_bool('VERBOSE', default=False)
        auto_exec = read_config_bool('AUTO_EXECUTE', default=False)

        self.assertTrue(debug)
        self.assertTrue(verbose)
        self.assertFalse(auto_exec)

        # Verify source is local_env
        self.assertEqual(get_config_source('DEBUG'), 'local_env')

    def test_cli_overrides_local_env(self):
        """Test that CLI args override local .env in development"""
        with open('.env', 'w') as f:
            f.write('DEBUG=false\n')

        args = argparse.Namespace(debug=True)
        debug = read_config_bool('DEBUG', cli_args=args, default=False)

        self.assertTrue(debug)
        self.assertEqual(get_config_source('DEBUG', cli_args=args), 'cli')


class TestProductionEnvironment(unittest.TestCase):
    """Test configuration in production with environment variables"""

    def setUp(self):
        """Set up production environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Clear cache
        _config_cache.clear_cache()

        # Backup and clear environment
        self.env_backup = {}
        for key in ['DEBUG', 'VERBOSE', 'AUTO_EXECUTE', 'API_KEY']:
            if key in os.environ:
                self.env_backup[key] = os.environ[key]
                del os.environ[key]

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)

        # Restore environment
        for key, value in self.env_backup.items():
            os.environ[key] = value

        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_production_with_env_vars(self):
        """Test typical production scenario with environment variables"""
        # Set environment variables (no .env files)
        os.environ['DEBUG'] = 'false'
        os.environ['VERBOSE'] = 'false'
        os.environ['AUTO_EXECUTE'] = 'true'
        os.environ['API_KEY'] = 'prod-key-123'

        debug = read_config_bool('DEBUG', default=False)
        auto_exec = read_config_bool('AUTO_EXECUTE', default=False)
        api_key = read_config_value('API_KEY', default='')

        self.assertFalse(debug)
        self.assertTrue(auto_exec)
        self.assertEqual(api_key, 'prod-key-123')

        # Verify source is env
        self.assertEqual(get_config_source('DEBUG'), 'env')
        self.assertEqual(get_config_source('API_KEY'), 'env')

    def test_env_vars_override_local_env(self):
        """Test that environment variables override local .env"""
        with open('.env', 'w') as f:
            f.write('DEBUG=true\n')

        os.environ['DEBUG'] = 'false'

        debug = read_config_bool('DEBUG', default=False)
        self.assertFalse(debug)
        self.assertEqual(get_config_source('DEBUG'), 'env')


class TestCICDEnvironment(unittest.TestCase):
    """Test configuration in CI/CD with CLI arguments"""

    def setUp(self):
        """Set up CI/CD environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Clear cache
        _config_cache.clear_cache()

        # Clear environment
        for key in ['DEBUG', 'VERBOSE', 'CI']:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cicd_with_cli_args(self):
        """Test typical CI/CD scenario with explicit CLI arguments"""
        # Simulate CI environment
        os.environ['CI'] = 'true'

        # Create .env files that should be overridden
        with open('.env', 'w') as f:
            f.write('DEBUG=false\n')
            f.write('VERBOSE=false\n')

        # CLI args take precedence
        args = argparse.Namespace(debug=True, verbose=True)

        debug = read_config_bool('DEBUG', cli_args=args, default=False)
        verbose = read_config_bool('VERBOSE', cli_args=args, default=False)

        self.assertTrue(debug)
        self.assertTrue(verbose)

        # Verify source is CLI
        self.assertEqual(get_config_source('DEBUG', cli_args=args), 'cli')


class TestDockerContainerEnvironment(unittest.TestCase):
    """Test configuration in Docker containers"""

    def setUp(self):
        """Set up Docker environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Clear cache
        _config_cache.clear_cache()

        # Backup environment
        self.env_backup = {}
        for key in ['DATABASE_URL', 'API_KEY', 'DEBUG', 'TIMEOUT']:
            if key in os.environ:
                self.env_backup[key] = os.environ[key]
                del os.environ[key]

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)

        # Restore environment
        for key, value in self.env_backup.items():
            os.environ[key] = value

        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_docker_with_env_and_global_fallback(self):
        """Test Docker with environment variables and global .env fallback"""
        # Create global .env for defaults
        global_env = Path.home() / '.media-library-tools' / '.env'
        global_env.parent.mkdir(parents=True, exist_ok=True)
        with open(global_env, 'w') as f:
            f.write('DEBUG=false\n')
            f.write('TIMEOUT=30\n')

        # Set container environment (overrides global)
        os.environ['DEBUG'] = 'true'
        os.environ['API_KEY'] = 'container-key'

        debug = read_config_bool('DEBUG', default=False)
        api_key = read_config_value('API_KEY', default='')
        timeout = read_config_value('TIMEOUT', default='60', value_type='int')

        self.assertTrue(debug)  # From environment
        self.assertEqual(api_key, 'container-key')  # From environment
        self.assertEqual(timeout, 30)  # From global .env

        self.assertEqual(get_config_source('DEBUG'), 'env')
        self.assertEqual(get_config_source('TIMEOUT'), 'global_env')


class TestMultiToolConsistency(unittest.TestCase):
    """Test consistency across multiple tools"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Clear cache
        _config_cache.clear_cache()

        # Clear environment
        for key in ['AUTO_EXECUTE', 'AUTO_CONFIRM', 'QUIET_MODE']:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_consistent_config_across_tools(self):
        """Test that configuration is consistent when used by multiple tools"""
        # Create local .env with common settings
        with open('.env', 'w') as f:
            f.write('AUTO_EXECUTE=true\n')
            f.write('AUTO_CONFIRM=true\n')
            f.write('QUIET_MODE=false\n')

        # Simulate reading from multiple tools
        tool1_auto_exec = read_config_bool('AUTO_EXECUTE', default=False)
        tool1_auto_confirm = read_config_bool('AUTO_CONFIRM', default=False)

        tool2_auto_exec = read_config_bool('AUTO_EXECUTE', default=False)
        tool2_auto_confirm = read_config_bool('AUTO_CONFIRM', default=False)

        # Should be consistent
        self.assertEqual(tool1_auto_exec, tool2_auto_exec)
        self.assertEqual(tool1_auto_confirm, tool2_auto_confirm)
        self.assertTrue(tool1_auto_exec)
        self.assertTrue(tool1_auto_confirm)


class TestConfigurationMigration(unittest.TestCase):
    """Test migration scenarios from old to new configuration system"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Clear cache
        _config_cache.clear_cache()

        # Clear environment
        for key in ['AUTO_EXECUTE', 'AUTO_CONFIRM']:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backward_compatibility(self):
        """Test that existing configurations still work"""
        # Simulate existing global .env
        global_env = Path.home() / '.media-library-tools' / '.env'
        global_env.parent.mkdir(parents=True, exist_ok=True)
        with open(global_env, 'w') as f:
            f.write('AUTO_EXECUTE=true\n')
            f.write('AUTO_CONFIRM=true\n')

        # Should read correctly
        auto_exec = read_config_bool('AUTO_EXECUTE', default=False)
        auto_confirm = read_config_bool('AUTO_CONFIRM', default=False)

        self.assertTrue(auto_exec)
        self.assertTrue(auto_confirm)

    def test_gradual_migration_local_overrides_global(self):
        """Test gradual migration where local .env overrides global"""
        # Old global configuration
        global_env = Path.home() / '.media-library-tools' / '.env'
        global_env.parent.mkdir(parents=True, exist_ok=True)
        with open(global_env, 'w') as f:
            f.write('AUTO_EXECUTE=false\n')

        # New local configuration (project-specific)
        with open('.env', 'w') as f:
            f.write('AUTO_EXECUTE=true\n')

        # Local should override global
        auto_exec = read_config_bool('AUTO_EXECUTE', default=False)
        self.assertTrue(auto_exec)
        self.assertEqual(get_config_source('AUTO_EXECUTE'), 'local_env')


if __name__ == '__main__':
    unittest.main()
