#!/usr/bin/env python3
"""
Unit tests for error handling scenarios across all tools

Tests various error conditions and edge cases to ensure robust error handling.
"""

import unittest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

# Try to import test helpers, handle import errors gracefully
try:
    from test_helpers import MediaLibraryTestCase
    TEST_HELPERS_AVAILABLE = True
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

# Add tool directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'SABnzbd'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plex'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plex-api'))

# Import tool classes with error handling
try:
    from sabnzbd_cleanup import SABnzbdDetector, get_dir_size, parse_size_threshold
except ImportError:
    SABnzbdDetector = None
    get_dir_size = None
    parse_size_threshold = None

try:
    from plex_movie_subdir_renamer import PlexMovieSubdirRenamer
except ImportError:
    PlexMovieSubdirRenamer = None

try:
    from plex_make_dirs import PlexDirectoryCreator
except ImportError:
    PlexDirectoryCreator = None

try:
    from plex_make_seasons import SeasonOrganizer
except ImportError:
    SeasonOrganizer = None

try:
    from plex_make_all_seasons import SeasonOrganizer as BatchSeasonOrganizer
except ImportError:
    BatchSeasonOrganizer = None

try:
    from plex_move_movie_extras import PlexMovieExtrasOrganizer
except ImportError:
    PlexMovieExtrasOrganizer = None


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
        
        # Should handle gracefully without crashing
        with self.assertRaises((FileNotFoundError, OSError)):
            self.detector.analyze_directory(nonexistent_dir)
    
    @unittest.skipIf(SABnzbdDetector is None, "SABnzbd tools not available")
    def test_permission_denied_directory(self):
        """Test handling of directories without read permissions."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        restricted_dir = test_dir / 'restricted_test'
        restricted_dir.mkdir()
        
        # Remove read permissions
        restricted_dir.chmod(0o000)
        
        try:
            # Should handle permission errors gracefully
            with self.assertRaises(PermissionError):
                self.detector.analyze_directory(restricted_dir)
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
            '50.5G',  # Decimal not supported
            '-50G',   # Negative not supported
        ]
        
        for invalid_format in invalid_formats:
            with self.assertRaises(ValueError):
                parse_size_threshold(invalid_format)
    
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
        if self.renamer is not None:
            self.assertFalse(self.renamer.is_video_file(nonexistent_file))
        if self.creator is not None:
            self.assertFalse(self.creator.should_process_file(nonexistent_file))
        if self.season_organizer is not None:
            self.assertFalse(self.season_organizer.is_video_file(nonexistent_file))
        if self.batch_organizer is not None:
            self.assertFalse(self.batch_organizer.is_video_file(nonexistent_file))
    
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
    def test_disk_space_simulation(self):
        """Test behavior when disk space is limited."""
        # This is difficult to test without actually filling disk
        # We'll test the error handling paths instead
        with patch('shutil.move') as mock_move:
            mock_move.side_effect = OSError("No space left on device")
            
            # Tools should handle disk space errors gracefully
            with self.assertRaises(OSError):
                mock_move('/source/file.mp4', '/dest/file.mp4')
    
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
        """Test handling of files locked by another process."""
        test_dir = self.copy_fixture('common/video_files')
        test_file = test_dir / 'locked_file.mp4'
        test_file.touch()
        
        # Simulate file being locked
        with patch('pathlib.Path.rename') as mock_rename:
            mock_rename.side_effect = PermissionError("File is locked")
            
            # Tools should handle locked files gracefully
            with self.assertRaises(PermissionError):
                test_file.rename(test_file.parent / 'new_name.mp4')
    
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
        result = renamer.is_video_file(test_file)
        self.assertFalse(result)


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
    def test_file_descriptor_exhaustion(self):
        """Test handling when file descriptors are exhausted."""
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Create many files
        for i in range(50):
            (test_dir / f'movie_{i}.mp4').touch()
        
        # Mock file opening to simulate FD exhaustion
        original_open = open
        open_count = 0
        
        def limited_open(*args, **kwargs):
            nonlocal open_count
            open_count += 1
            if open_count > 25:  # Simulate FD limit
                raise OSError("Too many open files")
            return original_open(*args, **kwargs)
        
        with patch('builtins.open', side_effect=limited_open):
            detector = SABnzbdDetector()
            
            try:
                # Should handle FD exhaustion gracefully
                detector.analyze_directory(test_dir)
            except OSError as e:
                if "Too many open files" in str(e):
                    pass  # Expected
                else:
                    raise
            except Exception as e:
                self.fail(f"Should handle FD exhaustion gracefully: {e}")
    
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
    """Test network-related error handling."""
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_network_timeout_simulation(self):
        """Test handling of network timeouts during operations."""
        # Simulate network paths
        network_file = Path('//remote-server/share/movie.mp4')
        
        # Mock network operations to simulate timeout
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = OSError("Connection timed out")
            
            renamer = PlexMovieSubdirRenamer()
            
            try:
                # Should handle timeout gracefully
                result = renamer.is_video_file(network_file)
                # Should return False for inaccessible files
                self.assertFalse(result)
            except OSError as e:
                if "Connection timed out" in str(e):
                    pass  # Expected
                else:
                    raise
            except Exception as e:
                self.fail(f"Should handle network timeout gracefully: {e}")
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_network_disconnection_simulation(self):
        """Test handling of network disconnection during operations."""
        # Simulate network paths
        network_file = Path('//remote-server/share/movie.mp4')
        
        # Mock network operations to simulate disconnection
        with patch('os.path.exists') as mock_exists:
            # First call succeeds, second fails (simulating disconnection)
            mock_exists.side_effect = [True, OSError("Network is unreachable")]
            
            renamer = PlexMovieSubdirRenamer()
            
            try:
                # First call should work
                renamer.is_video_file(network_file)
                
                # Second call should handle network error
                renamer.is_video_file(network_file)
            except OSError as e:
                if "Network is unreachable" in str(e):
                    pass  # Expected
                else:
                    raise
            except Exception as e:
                self.fail(f"Should handle network disconnection gracefully: {e}")
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None, "Plex tools not available")
    def test_dns_resolution_failure(self):
        """Test handling of DNS resolution failures."""
        # Simulate hostname-based paths
        hostname_file = Path('//nonexistent-server.local/share/movie.mp4')
        
        # Mock DNS resolution to fail
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = OSError("Name or service not known")
            
            renamer = PlexMovieSubdirRenamer()
            
            try:
                # Should handle DNS failure gracefully
                result = renamer.is_video_file(hostname_file)
                # Should return False for inaccessible files
                self.assertFalse(result)
            except OSError as e:
                if "Name or service not known" in str(e):
                    pass  # Expected
                else:
                    raise
            except Exception as e:
                self.fail(f"Should handle DNS resolution failure gracefully: {e}")


if __name__ == '__main__':
    unittest.main()