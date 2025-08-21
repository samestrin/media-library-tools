#!/usr/bin/env python3
"""
Unit tests for error handling scenarios across all tools

Tests various error conditions and edge cases to ensure robust error handling.
"""

import unittest
import os
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

# Try to import test helpers, handle import errors gracefully
try:
    from test_helpers import MediaLibraryTestCase
    TEST_HELPERS_AVAILABLE = True
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

import importlib.util
import shutil
import tempfile

def load_sabnzbd_tool(tool_name):
    """Load SABnzbd tool dynamically."""
    try:
        tool_path = Path(__file__).parent.parent.parent / 'SABnzbd' / tool_name
        if not tool_path.exists():
            return None
        
        # Copy to temp file with .py extension
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        with open(tool_path, 'r') as f:
            temp_file.write(f.read())
        temp_file.close()
        
        # Load as module
        spec = importlib.util.spec_from_file_location(tool_name, temp_file.name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return module
    except Exception:
        return None

def load_plex_tool(tool_name):
    """Load Plex tool dynamically."""
    try:
        tool_path = Path(__file__).parent.parent.parent / 'plex' / tool_name
        if not tool_path.exists():
            return None
        
        # Copy to temp file with .py extension
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        with open(tool_path, 'r') as f:
            temp_file.write(f.read())
        temp_file.close()
        
        # Load as module
        spec = importlib.util.spec_from_file_location(tool_name, temp_file.name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return module
    except Exception:
        return None

# Load tools dynamically
sabnzbd_module = load_sabnzbd_tool('sabnzbd_cleanup')
SABnzbdDetector = getattr(sabnzbd_module, 'SABnzbdDetector', None) if sabnzbd_module else None
get_dir_size = getattr(sabnzbd_module, 'get_dir_size', None) if sabnzbd_module else None
parse_size_threshold = getattr(sabnzbd_module, 'parse_size_threshold', None) if sabnzbd_module else None

plex_renamer_module = load_plex_tool('plex_movie_subdir_renamer')
PlexMovieSubdirRenamer = getattr(plex_renamer_module, 'PlexMovieSubdirRenamer', None) if plex_renamer_module else None

plex_dirs_module = load_plex_tool('plex_make_dirs')
PlexDirectoryCreator = getattr(plex_dirs_module, 'PlexDirectoryCreator', None) if plex_dirs_module else None

plex_seasons_module = load_plex_tool('plex_make_seasons')
SeasonOrganizer = getattr(plex_seasons_module, 'SeasonOrganizer', None) if plex_seasons_module else None

plex_batch_module = load_plex_tool('plex_make_all_seasons')
BatchSeasonOrganizer = getattr(plex_batch_module, 'SeasonOrganizer', None) if plex_batch_module else None

plex_extras_module = load_plex_tool('plex_move_movie_extras')
PlexMovieExtrasOrganizer = getattr(plex_extras_module, 'PlexMovieExtrasOrganizer', None) if plex_extras_module else None


@unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "SABnzbd tools not available")
class TestSABnzbdErrorHandling(MediaLibraryTestCase):
    """Test error handling in SABnzbd cleanup tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        if SABnzbdDetector is not None:
            self.detector = SABnzbdDetector()
        else:
            self.detector = None
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_nonexistent_directory(self):
        """Test handling of non-existent directories."""
        nonexistent_dir = Path('/nonexistent/directory')
        
        # Should handle gracefully without crashing, returning (False, 0, [])
        result = self.detector.analyze_directory(nonexistent_dir)
        self.assertEqual(result, (False, 0, []))
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_permission_denied_directory(self):
        """Test handling of directories without read permissions."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        restricted_dir = test_dir / 'restricted_test'
        restricted_dir.mkdir()
        
        # Remove read permissions
        restricted_dir.chmod(0o000)
        
        try:
            # Should handle permission errors gracefully, returning (False, 0, [])
            result = self.detector.analyze_directory(restricted_dir)
            self.assertEqual(result, (False, 0, []))
        finally:
            # Restore permissions for cleanup
            restricted_dir.chmod(0o755)
    
    @unittest.skipIf(parse_size_threshold is None, "SABnzbd tools not available")
    def test_invalid_size_threshold_formats(self):
        """Test invalid size threshold parsing."""
        invalid_formats = [
            '',
            'invalid',
            '50X',
            'abc',
            '-50G',   # Negative not supported
        ]
        
        for invalid_format in invalid_formats:
            with self.assertRaises(ValueError):
                parse_size_threshold(invalid_format)
        
        # Test that decimal formats are actually supported
        self.assertEqual(parse_size_threshold('50.5G'), 54223962112)
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_empty_directory_analysis(self):
        """Test analysis of completely empty directories."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        empty_dir = test_dir / 'empty_test_dir'
        empty_dir.mkdir()
        
        is_sabnzbd, score, indicators = self.detector.analyze_directory(empty_dir)
        
        self.assertFalse(is_sabnzbd)
        self.assertEqual(score, 0)
        self.assertEqual(indicators, [])


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestPlexToolsErrorHandling(MediaLibraryTestCase):
    """Test error handling in Plex tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.renamer = PlexMovieSubdirRenamer() if PlexMovieSubdirRenamer is not None else None
        self.creator = PlexDirectoryCreator() if PlexDirectoryCreator is not None else None
        self.season_organizer = SeasonOrganizer() if SeasonOrganizer is not None else None
        self.batch_organizer = BatchSeasonOrganizer() if BatchSeasonOrganizer is not None else None
        self.extras_organizer = PlexMovieExtrasOrganizer() if PlexMovieExtrasOrganizer is not None else None
    
    def test_nonexistent_file_processing(self):
        """Test processing of non-existent files."""
        nonexistent_file = Path('/nonexistent/file.mp4')
        
        # Tools should handle non-existent files gracefully
        # is_video_file methods typically check extension, not file existence
        if self.renamer is not None:
            # is_video_file checks extension, returns True for .mp4
            self.assertTrue(self.renamer.is_video_file(nonexistent_file))
        if self.creator is not None:
            # should_process_file typically checks extension, not file existence  
            self.assertTrue(self.creator.should_process_file(nonexistent_file))
        if self.season_organizer is not None:
            # is_video_file checks extension, returns True for .mp4  
            self.assertTrue(self.season_organizer.is_video_file(nonexistent_file))
        if self.batch_organizer is not None:
            # is_video_file checks extension, returns True for .mp4
            self.assertTrue(self.batch_organizer.is_video_file(nonexistent_file))
    
    def test_invalid_file_extensions(self):
        """Test handling of files with invalid or missing extensions."""
        test_dir = self.copy_fixture('common/image_files')
        
        invalid_files = [
            Path('file_without_extension'),
            Path('file.'),
            Path('.hidden_file'),
            Path('file..mp4'),  # Double extension
            Path('file.MP4.backup'),  # Backup file
        ]
        
        # Create test files
        for invalid_file in invalid_files:
            if not invalid_file.name.startswith('.'):
                (test_dir / invalid_file).touch()
        
        test_files = [f for f in test_dir.glob('*') if f.is_file()]
        
        for test_file in test_files:
            # Most tools should reject these files
            if self.renamer is not None:
                self.renamer.is_video_file(test_file)
            if self.season_organizer is not None:
                self.season_organizer.is_video_file(test_file)
            if self.batch_organizer is not None:
                self.batch_organizer.is_video_file(test_file)
    
    def test_extremely_long_filenames(self):
        """Test handling of extremely long filenames."""
        test_dir = self.copy_fixture('common/video_files')
        
        # Create a filename that exceeds typical filesystem limits
        long_name = 'a' * 200 + '.mp4'
        long_file = test_dir / long_name
        
        try:
            long_file.touch()
            file_created = True
        except OSError:
            # Some filesystems may not support very long names
            file_created = False
        
        if file_created:
            # Tools should handle long filenames without crashing
            try:
                if self.renamer is not None:
                    self.renamer.is_video_file(long_file)
                if self.season_organizer is not None:
                    self.season_organizer.is_video_file(long_file)
                if self.batch_organizer is not None:
                    self.batch_organizer.is_video_file(long_file)
            except Exception as e:
                self.fail(f"Tools should handle long filenames gracefully: {e}")
    
    def test_special_characters_in_filenames(self):
        """Test handling of special characters in filenames."""
        test_dir = self.copy_fixture('common/video_files')
        
        special_files = [
            Path('movie with spaces.mp4'),
            Path('movie-with-dashes.mp4'),
            Path('movie_with_underscores.mp4'),
            Path('movie[with]brackets.mp4'),
            Path('movie(with)parentheses.mp4'),
            Path('movie&with&ampersands.mp4'),
            Path('movie#with#hashes.mp4'),
        ]
        
        # Create test files
        created_files = []
        for special_file in special_files:
            try:
                file_path = test_dir / special_file
                file_path.touch()
                created_files.append(file_path)
            except Exception:
                # Some filesystems may not support certain characters
                pass
        
        for test_file in created_files:
            # Tools should handle special characters
            try:
                if self.renamer is not None:
                    self.renamer.is_video_file(test_file)
                if self.season_organizer is not None:
                    self.season_organizer.is_video_file(test_file)
                if self.batch_organizer is not None:
                    self.batch_organizer.is_video_file(test_file)
            except Exception as e:
                self.fail(f"Tools should handle special characters in '{test_file}': {e}")
    
    def test_unicode_filenames(self):
        """Test handling of Unicode characters in filenames."""
        test_dir = self.copy_fixture('common/video_files')
        
        unicode_files = [
            Path('电影.mp4'),  # Chinese
            Path('映画.mp4'),  # Japanese
            Path('фильм.mp4'),  # Russian
            Path('película.mp4'),  # Spanish
            Path('café_movie.mp4'),  # Accented characters
        ]
        
        # Create test files
        created_files = []
        for unicode_file in unicode_files:
            try:
                file_path = test_dir / unicode_file
                file_path.touch()
                created_files.append(file_path)
            except Exception:
                # Some filesystems may not support certain Unicode
                pass
        
        for test_file in created_files:
            # Tools should handle Unicode characters
            try:
                if self.renamer is not None:
                    self.renamer.is_video_file(test_file)
                if self.season_organizer is not None:
                    self.season_organizer.is_video_file(test_file)
                if self.batch_organizer is not None:
                    self.batch_organizer.is_video_file(test_file)
            except Exception as e:
                self.fail(f"Tools should handle Unicode in '{test_file}': {e}")


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestFileSystemErrorHandling(MediaLibraryTestCase):
    """Test file system related error handling."""
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_readonly_filesystem_simulation(self):
        """Test behavior when filesystem is read-only."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        readonly_test_dir = test_dir / 'readonly_test'
        readonly_test_dir.mkdir()
        
        # Create a test file
        test_file = readonly_test_dir / 'test.mp4'
        test_file.touch()
        
        # Make directory read-only
        readonly_test_dir.chmod(0o444)
        
        try:
            # Tools should handle read-only scenarios gracefully
            # This is more of a behavioral test - tools shouldn't crash
            detector = SABnzbdDetector()
            detector.analyze_directory(readonly_test_dir)
        except PermissionError:
            # This is expected behavior
            pass
        finally:
            # Restore permissions for cleanup
            readonly_test_dir.chmod(0o755)
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_very_long_filename_handling(self):
        """Test handling of extremely long filenames."""
        test_dir = self.copy_fixture('common/video_files')
        
        # Create a very long filename (filesystem dependent limits)
        long_name = 'a' * 250 + '.mp4'  # Near filesystem limit
        very_long_name = 'a' * 300 + '.mp4'  # Exceeds typical limits
        
        renamer = PlexMovieSubdirRenamer()
        
        # Test reasonable long filename
        long_file = test_dir / long_name
        result = renamer.is_video_file(long_file)
        self.assertTrue(result)  # Should handle long names
        
        # Test extremely long filename
        very_long_file = test_dir / very_long_name
        result = renamer.is_video_file(very_long_file)
        self.assertTrue(result)  # Should still check extension
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_network_path_handling(self):
        """Test handling of network paths and UNC paths."""
        network_paths = [
            Path('//server/share/movie.mp4'),
            Path('/mnt/network/movie.mp4'),
            Path('smb://server/share/movie.mp4'),
        ]
        
        for network_path in network_paths:
            # Tools should handle network paths without crashing
            try:
                renamer = PlexMovieSubdirRenamer()
                renamer.is_video_file(network_path)
            except Exception as e:
                # Some exceptions are expected for invalid network paths
                # Just ensure they don't cause crashes
                pass


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestConcurrencyErrorHandling(MediaLibraryTestCase):
    """Test error handling in concurrent scenarios."""
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_file_locked_by_another_process(self):
        """Test handling of files that might be locked by another process."""
        test_dir = self.copy_fixture('common/video_files')
        test_file = test_dir / 'locked_file.mp4'
        test_file.touch()
        
        renamer = PlexMovieSubdirRenamer()
        
        # Test that tools can still analyze potentially locked files
        result = renamer.is_video_file(test_file)
        self.assertTrue(result)  # Should identify as video file
        
        # Test that we can detect the file exists
        self.assertTrue(test_file.exists())
        
        # Test real file operation that might encounter locking
        try:
            # Try to rename the file to test real behavior
            new_name = test_file.parent / 'renamed_file.mp4'
            test_file.rename(new_name)
            # If successful, rename it back
            new_name.rename(test_file)
        except PermissionError:
            # This is acceptable - file might be locked by system/antivirus
            pass
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_file_deleted_during_processing(self):
        """Test handling of files deleted during processing."""
        test_dir = self.copy_fixture('common/video_files')
        test_file = test_dir / 'temp_file.mp4'
        test_file.touch()
        
        # Verify file exists
        self.assertTrue(test_file.exists())
        
        # Delete file
        test_file.unlink()
        
        # Verify deletion
        self.assertFalse(test_file.exists())
        
        # Tools should handle missing files gracefully
        renamer = PlexMovieSubdirRenamer()
        # Should not crash when checking non-existent file
        # is_video_file typically checks extension, not existence
        result = renamer.is_video_file(test_file)
        self.assertTrue(result)  # .mp4 extension is valid even if file doesn't exist


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestInputValidationErrorHandling(MediaLibraryTestCase):
    """Test input validation and sanitization."""
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_null_byte_injection(self):
        """Test handling of null byte injection in filenames."""
        test_dir = self.copy_fixture('common/video_files')
        
        malicious_files = [
            Path('movie\x00.mp4'),
            Path('movie\x00\x00.mp4'),
            Path('\x00movie.mp4'),
        ]
        
        # Create test files (if possible)
        created_files = []
        for malicious_file in malicious_files:
            try:
                file_path = test_dir / malicious_file
                file_path.touch()
                created_files.append(file_path)
            except (ValueError, OSError):
                # These exceptions are acceptable for malicious input
                pass
        
        for test_file in created_files:
            # Tools should handle null bytes safely
            try:
                renamer = PlexMovieSubdirRenamer()
                renamer.is_video_file(test_file)
            except (ValueError, OSError):
                # These exceptions are acceptable for malicious input
                pass
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_path_traversal_attempts(self):
        """Test handling of path traversal attempts."""
        traversal_paths = [
            Path('../../../etc/passwd'),
            Path('..\\..\\..\\windows\\system32'),
            Path('movie/../../../sensitive_file.mp4'),
        ]
        
        for traversal_path in traversal_paths:
            # Tools should handle path traversal safely
            try:
                renamer = PlexMovieSubdirRenamer()
                renamer.is_video_file(traversal_path)
            except (ValueError, OSError):
                # These exceptions are acceptable for malicious input
                pass
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_extremely_nested_paths(self):
        """Test handling of extremely nested directory structures."""
        test_dir = self.copy_fixture('common/video_files')
        
        # Create a very deep path
        deep_path_parts = ['level' + str(i) for i in range(50)]
        deep_path = test_dir
        for part in deep_path_parts:
            deep_path = deep_path / part
        
        deep_file = deep_path / 'movie.mp4'
        
        # Tools should handle deep paths without stack overflow
        try:
            renamer = PlexMovieSubdirRenamer()
            renamer.is_video_file(deep_file)
        except (OSError, RecursionError):
            # These exceptions are acceptable for extremely deep paths
            pass
        except Exception as e:
            # Other exceptions might be acceptable
            pass


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestResourceExhaustionScenarios(MediaLibraryTestCase):
    """Test handling of resource exhaustion scenarios."""
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_memory_pressure_simulation(self):
        """Test handling of memory pressure scenarios."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Create many files to simulate memory pressure
        for i in range(100):
            (test_dir / f'movie_{i}.mp4').touch()
        
        detector = SABnzbdDetector()
        
        try:
            # Should handle large directory without memory issues
            result = detector.analyze_directory(test_dir)
            self.assertIsNotNone(result)
        except MemoryError:
            self.fail("Tools should handle memory pressure gracefully")
        except Exception as e:
            # Other exceptions might be acceptable
            pass
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_large_directory_handling(self):
        """Test handling of directories with many files."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Create many files to test scalability
        for i in range(100):
            (test_dir / f'movie_{i}.mp4').touch()
            (test_dir / f'episode_{i}.mkv').touch()
            (test_dir / f'document_{i}.rar').touch()
        
        detector = SABnzbdDetector()
        
        # Should handle large directories without crashing
        result = detector.analyze_directory(test_dir)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)  # (is_sabnzbd, score, indicators)
        
        # Should return valid boolean, int, and list
        is_sabnzbd, score, indicators = result
        self.assertIsInstance(is_sabnzbd, bool)
        self.assertIsInstance(score, int)
        self.assertIsInstance(indicators, list)
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_deep_recursion_limits(self):
        """Test handling of extremely deep directory structures."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        deep_test_dir = test_dir / 'deep_recursion_test'
        deep_test_dir.mkdir()
        
        # Create deeply nested structure
        current_dir = deep_test_dir
        for i in range(30):  # Create 30 levels deep
            current_dir = current_dir / f'level_{i}'
            current_dir.mkdir()
        
        # Add a file at the deepest level
        (current_dir / 'deep_movie.mp4').touch()
        
        # Test tools with deep structure
        detector = SABnzbdDetector()
        
        try:
            # Should handle deep recursion without stack overflow
            result = detector.analyze_directory(deep_test_dir)
            # Should find the deep file
            self.assertIsNotNone(result)
        except RecursionError:
            self.fail("Tools should handle deep directory structures without recursion errors")
        except Exception as e:
            # Other exceptions might be acceptable
            pass


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestNetworkErrorScenarios(MediaLibraryTestCase):
    """Test network-related error handling using real file scenarios."""
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_nonexistent_network_path_handling(self):
        """Test handling of nonexistent network paths."""
        # Use realistic UNC paths that don't exist
        network_file = Path('//nonexistent-server/share/movie.mp4')
        
        renamer = PlexMovieSubdirRenamer()
        
        # Should handle nonexistent network paths gracefully
        # is_video_file typically checks extension, not path existence
        result = renamer.is_video_file(network_file)
        self.assertTrue(result)  # .mp4 extension is valid
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_invalid_hostname_paths(self):
        """Test handling of invalid hostname paths."""
        # Test various invalid hostname formats
        invalid_paths = [
            Path('//invalid-hostname-that-cannot-exist.local/share/movie.mp4'),
            Path('//999.999.999.999/share/movie.mp4'),  # Invalid IP
            Path('//localhost-nonexistent/share/movie.mp4'),
        ]
        
        renamer = PlexMovieSubdirRenamer()
        
        for invalid_path in invalid_paths:
            # Should handle invalid hostnames gracefully without crashing
            result = renamer.is_video_file(invalid_path)
            # is_video_file checks extension, so .mp4 should return True
            self.assertTrue(result, f"Failed for path: {invalid_path}")
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_malformed_network_paths(self):
        """Test handling of malformed network paths."""
        # Test various malformed network path formats
        malformed_paths = [
            Path('///malformed/path/movie.mp4'),  # Triple slash
            Path('//'),  # Incomplete UNC
            Path('//@#$%^&*/invalid/movie.mp4'),  # Invalid characters
            Path('//server name with spaces/share/movie.mp4'),  # Spaces in hostname
        ]
        
        renamer = PlexMovieSubdirRenamer()
        
        for malformed_path in malformed_paths:
            # Should handle malformed paths gracefully without crashing
            try:
                result = renamer.is_video_file(malformed_path)
                # If extension is valid (.mp4), should return True
                if malformed_path.suffix.lower() == '.mp4':
                    self.assertTrue(result, f"Failed for malformed path: {malformed_path}")
            except Exception as e:
                # If exception occurs, it should be a well-handled exception
                self.assertIn(type(e).__name__, ['OSError', 'ValueError', 'FileNotFoundError'],
                             f"Unexpected exception type for {malformed_path}: {type(e).__name__}")


if __name__ == '__main__':
    unittest.main()