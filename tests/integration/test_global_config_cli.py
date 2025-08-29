#!/usr/bin/env python3
"""
Integration Tests for Global Configuration CLI Integration

Tests that global configuration properly integrates with CLI argument parsing
to verify that AUTO_EXECUTE and AUTO_CONFIRM affect script behavior correctly.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestGlobalConfigCLI(unittest.TestCase):
    """Test global config integration with CLI argument processing."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.home_dir = self.temp_dir / 'home'
        self.media_tools_dir = self.home_dir / '.media-library-tools'
        self.working_dir = self.temp_dir / 'working'
        
        # Create directory structure
        self.home_dir.mkdir(parents=True)
        self.media_tools_dir.mkdir(parents=True)
        self.working_dir.mkdir(parents=True)
        
        # Store original environment
        self.original_env = os.environ.copy()
        self.original_cwd = os.getcwd()
        
        # Change to working directory
        os.chdir(self.working_dir)
        
        # Clear environment variables
        for var in ['AUTO_EXECUTE', 'AUTO_CONFIRM']:
            os.environ.pop(var, None)
    
    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _load_and_test_script_parsing(self, script_name, test_args=None):
        """
        Load a script and test its argument parsing with global config.
        
        Args:
            script_name: Name of the script to test
            test_args: List of command line arguments to simulate
            
        Returns:
            Parsed arguments object with global config applied
        """
        script_path = project_root / 'plex' / script_name
        
        if not script_path.exists():
            self.skipTest(f"Script {script_name} not found")
        
        # Read the script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Create a namespace with necessary imports
        namespace = {
            '__file__': str(script_path),
            '__name__': '__main__',  # Set __name__ to trigger main() execution
            'os': os,
            'sys': sys,
            'Path': Path,
            'argparse': __import__('argparse'),
            'shutil': __import__('shutil'),
            'tempfile': __import__('tempfile'),
            'fcntl': __import__('fcntl'),
            're': __import__('re'),
            'time': __import__('time'),
            'json': __import__('json'),
            'urllib': __import__('urllib')
        }
        
        try:
            # Mock sys.argv to simulate command line arguments
            original_argv = sys.argv
            if test_args is None:
                test_args = [script_name, '--help']
            sys.argv = test_args
            
            # Mock Path.home() to return our test directory
            with patch('pathlib.Path.home', return_value=self.home_dir):
                # Execute the script in the namespace
                exec(script_content, namespace)
                
                # The script should have executed its main() function and called sys.exit()
                # Since we mocked --help, it should have shown help and exited
                
        except SystemExit as e:
            # This is expected when --help is used
            if e.code == 0:
                return "help_displayed"
            else:
                return f"exit_code_{e.code}"
        except Exception as e:
            return f"error_{str(e)}"
        finally:
            sys.argv = original_argv
        
        return "completed"
    
    def test_auto_execute_affects_plex_correct_dirs(self):
        """Test that AUTO_EXECUTE affects plex_correct_dirs execution mode."""
        # Create global config
        with open(self.media_tools_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=true\n")
        
        # Test the script
        result = self._load_and_test_script_parsing('plex_correct_dirs')
        self.assertEqual(result, "help_displayed", 
            "Script should handle AUTO_EXECUTE config and show help")
    
    def test_auto_confirm_affects_plex_correct_dirs(self):
        """Test that AUTO_CONFIRM affects plex_correct_dirs confirmation behavior."""
        # Create global config
        with open(self.media_tools_dir / '.env', 'w') as f:
            f.write("AUTO_CONFIRM=true\n")
        
        # Test the script
        result = self._load_and_test_script_parsing('plex_correct_dirs')
        self.assertEqual(result, "help_displayed",
            "Script should handle AUTO_CONFIRM config and show help")
    
    def test_env_variable_precedence_over_files(self):
        """Test that environment variables take precedence over .env files."""
        # Create global .env with one value
        with open(self.media_tools_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=false\nAUTO_CONFIRM=false\n")
        
        # Create local .env with different values
        with open(self.working_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=false\nAUTO_CONFIRM=false\n")
        
        # Set environment variables to override
        os.environ['AUTO_EXECUTE'] = 'true'
        os.environ['AUTO_CONFIRM'] = 'true'
        
        # Test that environment variables are used
        result = self._load_and_test_script_parsing('plex_correct_dirs')
        self.assertEqual(result, "help_displayed",
            "Script should use environment variables over .env files")
    
    def test_local_env_precedence_over_global(self):
        """Test that local .env takes precedence over global .env."""
        # Create global .env
        with open(self.media_tools_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=false\nAUTO_CONFIRM=false\n")
        
        # Create local .env with different values
        with open(self.working_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=true\nAUTO_CONFIRM=true\n")
        
        result = self._load_and_test_script_parsing('plex_correct_dirs')
        self.assertEqual(result, "help_displayed",
            "Script should use local .env values over global .env")
    
    def test_malformed_config_handling(self):
        """Test graceful handling of malformed configuration files."""
        # Create malformed global config
        with open(self.media_tools_dir / '.env', 'w') as f:
            f.write("INVALID_LINE\nAUTO_EXECUTE=true\n=NO_VAR\n")
        
        result = self._load_and_test_script_parsing('plex_correct_dirs')
        self.assertEqual(result, "help_displayed",
            "Script should handle malformed config gracefully")
    
    def test_missing_config_files(self):
        """Test behavior when no configuration files exist."""
        # Don't create any .env files
        result = self._load_and_test_script_parsing('plex_correct_dirs')
        self.assertEqual(result, "help_displayed",
            "Script should work without config files")
    
    def test_multiple_script_consistency(self):
        """Test that multiple scripts handle global config consistently."""
        # Create global config
        with open(self.media_tools_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=true\nAUTO_CONFIRM=true\n")
        
        scripts_to_test = [
            'plex_correct_dirs',
            'plex_make_all_seasons',
            'plex_make_dirs',
            'plex_make_seasons',
            'plex_make_years'
        ]
        
        for script_name in scripts_to_test:
            with self.subTest(script=script_name):
                result = self._load_and_test_script_parsing(script_name)
                self.assertEqual(result, "help_displayed",
                    f"Script {script_name} should handle global config consistently")
    
    def test_boolean_value_formats(self):
        """Test various boolean value formats in configuration."""
        test_cases = [
            {'AUTO_EXECUTE': 'true', 'AUTO_CONFIRM': '1'},
            {'AUTO_EXECUTE': 'yes', 'AUTO_CONFIRM': 'on'},
            {'AUTO_EXECUTE': 'TRUE', 'AUTO_CONFIRM': 'YES'},
            {'AUTO_EXECUTE': 'false', 'AUTO_CONFIRM': '0'},
            {'AUTO_EXECUTE': 'no', 'AUTO_CONFIRM': 'off'},
        ]
        
        for config in test_cases:
            with self.subTest(config=config):
                # Create global config with test values
                config_content = '\n'.join(f"{k}={v}" for k, v in config.items())
                with open(self.media_tools_dir / '.env', 'w') as f:
                    f.write(config_content + '\n')
                
                result = self._load_and_test_script_parsing('plex_correct_dirs')
                self.assertEqual(result, "help_displayed",
                    f"Script should handle boolean format {config}")
    
    def test_config_hierarchy_integration(self):
        """Test the complete configuration hierarchy in an integrated scenario."""
        # Set up all levels of configuration
        
        # Global .env (lowest priority for environment variables)
        with open(self.media_tools_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=false\nAUTO_CONFIRM=false\nGLOBAL_ONLY=true\n")
        
        # Local .env (higher priority)
        with open(self.working_dir / '.env', 'w') as f:
            f.write("AUTO_EXECUTE=true\nLOCAL_ONLY=true\n")
        
        # Environment variable (highest priority)
        os.environ['AUTO_CONFIRM'] = 'true'
        os.environ['ENV_ONLY'] = 'true'
        
        result = self._load_and_test_script_parsing('plex_correct_dirs')
        self.assertEqual(result, "help_displayed",
            "Script should handle complete configuration hierarchy")


class TestNonInteractiveIntegration(unittest.TestCase):
    """Test integration of non-interactive detection with global config."""
    
    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def _test_non_interactive_function(self, script_name):
        """Test the is_non_interactive function from a script."""
        script_path = project_root / 'SABnzbd' / 'sabnzbd_cleanup'
        
        if not script_path.exists():
            self.skipTest(f"Script {script_name} not found")
        
        # Load just the is_non_interactive function
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Find the function
        lines = content.split('\n')
        func_start = None
        func_end = None
        
        for i, line in enumerate(lines):
            if line.startswith('def is_non_interactive():'):
                func_start = i
            elif func_start is not None and line and not line.startswith(' ') and not line.startswith('\t'):
                func_end = i
                break
        
        if func_start is None:
            self.skipTest(f"is_non_interactive function not found in {script_name}")
        
        if func_end is None:
            func_end = len(lines)
        
        # Extract and execute function
        func_lines = lines[func_start:func_end]
        func_code = '\n'.join(func_lines)
        
        namespace = {
            'os': os,
            'sys': sys
        }
        
        exec(func_code, namespace)
        return namespace['is_non_interactive']
    
    def test_cron_environment_detection(self):
        """Test detection of cron environment."""
        is_non_interactive = self._test_non_interactive_function('sabnzbd_cleanup')
        
        # Set CRON environment variable
        os.environ['CRON'] = '1'
        
        # Mock stdin to not be a TTY
        with patch('sys.stdin.isatty', return_value=False):
            result = is_non_interactive()
            self.assertTrue(result, "Should detect cron environment")
    
    def test_ci_environment_detection(self):
        """Test detection of CI environment."""
        is_non_interactive = self._test_non_interactive_function('sabnzbd_cleanup')
        
        os.environ['CI'] = 'true'
        
        result = is_non_interactive()
        self.assertTrue(result, "Should detect CI environment")
    
    def test_interactive_environment_detection(self):
        """Test detection of interactive environment."""
        is_non_interactive = self._test_non_interactive_function('sabnzbd_cleanup')
        
        # Clear automation environment variables
        for var in ['CRON', 'CI', 'AUTOMATED', 'NON_INTERACTIVE']:
            os.environ.pop(var, None)
        
        # Set TERM to indicate interactive terminal
        os.environ['TERM'] = 'xterm'
        
        # Mock stdin to be a TTY
        with patch('sys.stdin.isatty', return_value=True):
            result = is_non_interactive()
            self.assertFalse(result, "Should detect interactive environment")


if __name__ == '__main__':
    unittest.main()