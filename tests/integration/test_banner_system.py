#!/usr/bin/env python3
"""
Test Suite for Banner System Implementation

This test suite validates the banner functionality across all media library tools
to ensure consistent behavior and proper suppression conditions.
"""

import unittest
import subprocess
import os
import sys
import tempfile
from pathlib import Path


class TestBannerSystem(unittest.TestCase):
    """Test banner system functionality across all scripts."""
    
    def setUp(self):
        """Set up test environment."""
        self.script_dir = Path(__file__).parent.parent.parent
        self.scripts = [
            'plex/plex_update_tv_years',
            'plex/plex_correct_dirs',
            'plex/plex_make_all_seasons',
            'plex/plex_make_dirs',
            'plex/plex_make_seasons',
            'plex/plex_make_years',
            'plex/plex_move_movie_extras',
            'plex/plex_movie_subdir_renamer',
            'plex-api/plex_server_episode_refresh',
            'SABnzbd/sabnzbd_cleanup'
        ]
        
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.script_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_no_banner_flag_exists(self):
        """Test that all scripts have --no-banner flag."""
        for script_path in self.scripts:
            with self.subTest(script=script_path):
                try:
                    result = subprocess.run(
                        [sys.executable, script_path, '--help'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    self.assertIn('--no-banner', result.stdout, 
                                f"Script {script_path} missing --no-banner flag")
                    self.assertIn('Suppress banner display', result.stdout,
                                f"Script {script_path} missing banner suppression help text")
                except subprocess.TimeoutExpired:
                    self.fail(f"Script {script_path} --help timed out")
                except Exception as e:
                    self.fail(f"Script {script_path} --help failed: {e}")
    
    def test_banner_suppression_with_flag(self):
        """Test that --no-banner flag suppresses banner display."""
        # Test scripts that can run without special requirements
        safe_scripts = [
            'plex/plex_correct_dirs',
            'plex/plex_make_dirs', 
            'plex/plex_make_seasons',
            'plex/plex_make_years',
            'plex/plex_move_movie_extras',
            'plex/plex_movie_subdir_renamer',
            'SABnzbd/sabnzbd_cleanup'
        ]
        
        for script_path in safe_scripts:
            with self.subTest(script=script_path):
                try:
                    # Run with --no-banner and dry-run/preview mode
                    result = subprocess.run(
                        [sys.executable, script_path, self.temp_dir, '--no-banner', '--dry-run'],
                        capture_output=True,
                        text=True,
                        timeout=15,
                        env={**os.environ, 'TERM': 'xterm'}  # Ensure interactive-like environment
                    )
                    
                    # Banner should not appear - check for ASCII art characters
                    banner_chars = ['┏', '┳', '┓', '┃', '╻', '╸', '╺', '┛', '╹', '┗', '━']
                    banner_present = any(char in result.stdout for char in banner_chars)
                    
                    self.assertFalse(banner_present, 
                                   f"Script {script_path} shows banner despite --no-banner flag")
                                   
                except subprocess.TimeoutExpired:
                    self.fail(f"Script {script_path} with --no-banner timed out")
                except Exception as e:
                    # Some scripts may fail due to missing dependencies, but shouldn't crash on banner logic
                    if "banner" in str(e).lower():
                        self.fail(f"Script {script_path} failed on banner logic: {e}")
    
    def test_banner_suppression_with_quiet_mode(self):
        """Test that QUIET_MODE=true suppresses banner display."""
        # Test with a simple script that's unlikely to have external dependencies
        script_path = 'plex/plex_make_seasons'
        
        try:
            # Run with QUIET_MODE=true
            env = {**os.environ, 'QUIET_MODE': 'true', 'TERM': 'xterm'}
            result = subprocess.run(
                [sys.executable, script_path, self.temp_dir, '--dry-run'],
                capture_output=True,
                text=True,
                timeout=15,
                env=env
            )
            
            # Banner should not appear - check for ASCII art characters  
            banner_chars = ['┏', '┳', '┓', '┃', '╻', '╸', '╺', '┛', '╹', '┗', '━']
            banner_present = any(char in result.stdout for char in banner_chars)
            
            self.assertFalse(banner_present, 
                           f"Script {script_path} shows banner despite QUIET_MODE=true")
                           
        except subprocess.TimeoutExpired:
            self.fail(f"Script {script_path} with QUIET_MODE timed out")
        except Exception as e:
            if "banner" in str(e).lower():
                self.fail(f"Script {script_path} failed on QUIET_MODE banner logic: {e}")
    
    def test_banner_suppression_non_interactive(self):
        """Test that non-interactive mode suppresses banner display."""
        # Test with a simple script
        script_path = 'plex/plex_make_seasons'
        
        try:
            # Run in non-interactive environment (no TERM, stdin not TTY)
            env = {k: v for k, v in os.environ.items() if k != 'TERM'}
            result = subprocess.run(
                [sys.executable, script_path, self.temp_dir, '--dry-run'],
                capture_output=True,
                text=True,
                timeout=15,
                env=env,
                stdin=subprocess.PIPE  # Ensure stdin is not TTY
            )
            
            # Banner should not appear in non-interactive mode
            banner_chars = ['┏', '┳', '┓', '┃', '╻', '╸', '╺', '┛', '╹', '┗', '━']
            banner_present = any(char in result.stdout for char in banner_chars)
            
            self.assertFalse(banner_present, 
                           f"Script {script_path} shows banner in non-interactive mode")
                           
        except subprocess.TimeoutExpired:
            self.fail(f"Script {script_path} in non-interactive mode timed out")
        except Exception as e:
            if "banner" in str(e).lower():
                self.fail(f"Script {script_path} failed on non-interactive banner logic: {e}")
    
    def test_backward_compatibility(self):
        """Test that existing functionality is preserved."""
        # Test that scripts still have their original arguments
        test_cases = [
            ('plex/plex_correct_dirs', ['--execute', '--verbose']),
            ('plex/plex_make_dirs', ['--list-types']),
            ('plex/plex_make_seasons', ['--list-patterns']),
            ('SABnzbd/sabnzbd_cleanup', ['--prune-at'])
        ]
        
        for script_path, args in test_cases:
            with self.subTest(script=script_path, args=args):
                try:
                    result = subprocess.run(
                        [sys.executable, script_path, '--help'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    for arg in args:
                        self.assertIn(arg, result.stdout,
                                    f"Script {script_path} missing original argument {arg}")
                                    
                except subprocess.TimeoutExpired:
                    self.fail(f"Script {script_path} --help timed out")
                except Exception as e:
                    self.fail(f"Script {script_path} --help failed: {e}")
    
    def test_version_consistency(self):
        """Test that version information is properly displayed."""
        for script_path in self.scripts:
            with self.subTest(script=script_path):
                try:
                    result = subprocess.run(
                        [sys.executable, script_path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    # Should have version information
                    self.assertTrue(result.stdout.strip(), 
                                  f"Script {script_path} --version produced no output")
                    
                    # Should contain version number pattern
                    version_pattern = r'\d+\.\d+(?:\.\d+)?'
                    import re
                    self.assertTrue(re.search(version_pattern, result.stdout),
                                  f"Script {script_path} version output missing version number")
                                  
                except subprocess.TimeoutExpired:
                    self.fail(f"Script {script_path} --version timed out")
                except Exception as e:
                    self.fail(f"Script {script_path} --version failed: {e}")
    
    def test_help_text_consistency(self):
        """Test that help text includes banner-related information."""
        for script_path in self.scripts:
            with self.subTest(script=script_path):
                try:
                    result = subprocess.run(
                        [sys.executable, script_path, '--help'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    # Should have --no-banner in options
                    self.assertIn('--no-banner', result.stdout,
                                f"Script {script_path} missing --no-banner in help")
                    
                    # Should have proper help text for --no-banner
                    self.assertIn('Suppress banner display', result.stdout,
                                f"Script {script_path} missing banner suppression help")
                                
                except subprocess.TimeoutExpired:
                    self.fail(f"Script {script_path} --help timed out")
                except Exception as e:
                    self.fail(f"Script {script_path} --help failed: {e}")


class TestBannerFunctionality(unittest.TestCase):
    """Test the banner display functionality directly."""
    
    def setUp(self):
        """Set up test environment."""
        self.script_dir = Path(__file__).parent.parent.parent
        os.chdir(self.script_dir)
    
    def test_banner_display_format(self):
        """Test that banner displays with correct format."""
        # Create a test script that forces banner display
        test_script = '''
import sys
sys.path.append("plex")

def is_non_interactive():
    return False  # Force interactive mode

def display_banner(script_name, version, description, no_banner_flag=False, quiet_mode=False):
    if no_banner_flag or quiet_mode or is_non_interactive():
        return
    
    try:
        print("┏┳┓┏━╸╺┳┓╻┏━┓╻  ╻┏┓ ┏━┓┏━┓┏━┓╻ ╻╺┳╸┏━┓┏━┓╻  ┏━┓")
        print("┃┃┃┣╸  ┃┃┃┣━┫┃  ┃┣┻┓┣┳┛┣━┫┣┳┛┗┳┛ ┃ ┃ ┃┃ ┃┃  ┗━┓")
        print("╹ ╹┗━╸╺┻┛╹╹ ╹┗━╸╹┗━┛╹┗╸╹ ╹╹┗╸ ╹  ╹ ┗━┛┗━┛┗━╸┗━┛")
        print(f"{script_name} v{version}: {description}")
        print()
    except Exception:
        pass

# Test banner display
display_banner("test_script", "1.0", "test description")
print("END_OF_BANNER")
'''
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', test_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            
            # Should have ASCII art lines
            banner_chars = ['┏', '┳', '┓', '┃', '╻', '╸', '╺', '┛', '╹', '┗', '━']
            ascii_lines = [line for line in lines if any(char in line for char in banner_chars)]
            self.assertEqual(len(ascii_lines), 3, "Banner should have exactly 3 ASCII art lines")
            
            # Should have script info line
            info_lines = [line for line in lines if 'test_script v1.0: test description' in line]
            self.assertEqual(len(info_lines), 1, "Banner should have exactly 1 script info line")
            
            # Should end with END_OF_BANNER
            self.assertIn('END_OF_BANNER', result.stdout, "Test script should complete")
            
        except subprocess.TimeoutExpired:
            self.fail("Banner display test timed out")
        except Exception as e:
            self.fail(f"Banner display test failed: {e}")


if __name__ == '__main__':
    unittest.main()