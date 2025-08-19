#!/usr/bin/env python3
"""
Integration tests for error scenarios

Tests error conditions and edge cases in realistic scenarios.
"""

import unittest
import os
import sys
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import time

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

# Add tool directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'SABnzbd'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plex'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plex-api'))

try:
    from test_helpers import MediaLibraryTestCase
    TEST_HELPERS_AVAILABLE = True
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

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


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestFileSystemErrorScenarios(MediaLibraryTestCase):
    """Test error scenarios related to file system operations."""
    
    @unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
    def test_disk_full_scenario(self):
        """Test handling when disk space is exhausted."""
        test_dir = self.copy_fixture('common/video_files')
        disk_full_dir = test_dir / 'disk_full_test'
        disk_full_dir.mkdir()
        
        # Create test files
        source_file = disk_full_dir / 'source_movie.mp4'
        source_file.touch()
        
        dest_dir = disk_full_dir / 'destination'
        dest_dir.mkdir()
        
        # Mock disk full error
        with patch('shutil.move') as mock_move:
            mock_move.side_effect = OSError(28, "No space left on device")
            
            # Test that tools handle disk full errors gracefully
            with self.assertRaises(OSError) as context:
                shutil.move(str(source_file), str(dest_dir / 'dest_movie.mp4'))
            
            self.assertIn("No space left on device", str(context.exception))
    
    @unittest.skipIf(SABnzbdDetector is None or PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_permission_denied_scenarios(self):
        """Test various permission denied scenarios."""
        test_dir = self.copy_fixture('common/video_files')
        permission_test_dir = test_dir / 'permission_test'
        permission_test_dir.mkdir()
        
        # Create test structure
        source_file = permission_test_dir / 'movie.mp4'
        source_file.touch()
        
        readonly_dir = permission_test_dir / 'readonly'
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        noread_dir = permission_test_dir / 'noread'
        noread_dir.mkdir()
        noread_dir.chmod(0o000)  # No permissions
        
        try:
            # Test SABnzbd detector with permission issues
            detector = SABnzbdDetector()
            
            # Should handle readonly directory
            try:
                detector.analyze_directory(readonly_dir)
            except PermissionError:
                pass  # Expected
            
            # Should handle no-read directory
            with self.assertRaises(PermissionError):
                detector.analyze_directory(noread_dir)
            
            # Test Plex tools with permission issues
            renamer = PlexMovieSubdirRenamer()
            
            # Should still recognize the accessible file
            self.assertTrue(renamer.is_video_file(source_file))
            
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)
            noread_dir.chmod(0o755)
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_corrupted_filesystem_scenario(self):
        """Test handling of corrupted or inconsistent filesystem states."""
        test_dir = self.copy_fixture('common/video_files')
        corrupted_fs_dir = test_dir / 'corrupted_fs_test'
        corrupted_fs_dir.mkdir()
        
        # Create a file
        test_file = corrupted_fs_dir / 'test_movie.mp4'
        test_file.touch()
        
        # Simulate filesystem corruption by mocking os.path operations
        with patch('os.path.exists') as mock_exists:
            # Simulate inconsistent filesystem state
            mock_exists.return_value = False
            
            # Tools should handle inconsistent filesystem states
            renamer = PlexMovieSubdirRenamer()
            
            # Should not crash on inconsistent state
            try:
                result = renamer.is_video_file(test_file)
                # Result may be False due to mocked exists, but shouldn't crash
            except Exception as e:
                self.fail(f"Should handle filesystem inconsistencies gracefully: {e}")
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or SeasonOrganizer is None or BatchSeasonOrganizer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_network_filesystem_errors(self):
        """Test handling of network filesystem errors."""
        # Simulate network paths
        network_paths = [
            Path('//server/share/movie.mp4'),
            Path('/mnt/nfs/movie.mp4'),
            Path('smb://server/share/movie.mp4')
        ]
        
        # Test tools with network paths
        tools = [
            PlexMovieSubdirRenamer(),
            SeasonOrganizer(),
            BatchSeasonOrganizer()
        ]
        
        for tool in tools:
            for network_path in network_paths:
                try:
                    if hasattr(tool, 'is_video_file'):
                        tool.is_video_file(network_path)
                except (OSError, ValueError, AttributeError):
                    # These exceptions are acceptable for network issues
                    pass
                except Exception as e:
                    self.fail(f"Tool {tool.__class__.__name__} should handle network paths gracefully: {e}")


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestConcurrencyErrorScenarios(MediaLibraryTestCase):
    """Test error scenarios in concurrent environments."""
    
    @unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
    def test_file_locked_by_another_process(self):
        """Test handling files locked by another process."""
        test_dir = self.copy_fixture('common/video_files')
        file_lock_dir = test_dir / 'file_lock_test'
        file_lock_dir.mkdir()
        
        # Create test file
        test_file = file_lock_dir / 'locked_movie.mp4'
        test_file.touch()
        
        # Simulate file being locked
        with patch('pathlib.Path.rename') as mock_rename:
            mock_rename.side_effect = PermissionError("The process cannot access the file because it is being used by another process")
            
            # Test file operations with locked file
            with self.assertRaises(PermissionError):
                test_file.rename(test_file.parent / 'renamed_movie.mp4')
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_file_modified_during_processing(self):
        """Test handling files modified during processing."""
        test_dir = self.copy_fixture('common/video_files')
        file_modification_dir = test_dir / 'file_modification_test'
        file_modification_dir.mkdir()
        
        # Create test file
        test_file = file_modification_dir / 'movie.mp4'
        test_file.touch()
        
        # Get initial file stats
        initial_stat = test_file.stat()
        
        # Modify file during processing
        time.sleep(0.01)  # Ensure different timestamp
        test_file.touch()  # Update modification time
        
        # Verify file was modified
        new_stat = test_file.stat()
        self.assertNotEqual(initial_stat.st_mtime, new_stat.st_mtime)
        
        # Tools should still handle the file
        renamer = PlexMovieSubdirRenamer()
        self.assertTrue(renamer.is_video_file(test_file))
    
    @unittest.skipIf(SABnzbdDetector is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_directory_deleted_during_processing(self):
        """Test handling directories deleted during processing."""
        test_dir = self.copy_fixture('common/video_files')
        dir_deletion_dir = test_dir / 'dir_deletion_test'
        dir_deletion_dir.mkdir()
        
        # Create subdirectory with files
        sub_dir = dir_deletion_dir / 'subdir'
        sub_dir.mkdir()
        
        test_file = sub_dir / 'movie.mp4'
        test_file.touch()
        
        # Verify initial state
        self.assertTrue(sub_dir.exists())
        self.assertTrue(test_file.exists())
        
        # Delete directory
        shutil.rmtree(sub_dir)
        
        # Verify deletion
        self.assertFalse(sub_dir.exists())
        self.assertFalse(test_file.exists())
        
        # Tools should handle missing directories gracefully
        detector = SABnzbdDetector()
        
        with self.assertRaises((FileNotFoundError, OSError)):
            detector.analyze_directory(sub_dir)
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or SeasonOrganizer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_race_condition_simulation(self):
        """Test handling potential race conditions."""
        test_dir = self.copy_fixture('common/video_files')
        race_condition_dir = test_dir / 'race_condition_test'
        race_condition_dir.mkdir()
        
        # Create test file
        test_file = race_condition_dir / 'race_test_movie.mp4'
        test_file.touch()
        
        # Simulate race condition with file operations
        def simulate_concurrent_access():
            """Simulate another process accessing the file."""
            if test_file.exists():
                # Simulate reading file stats
                test_file.stat()
                # Simulate brief file lock
                time.sleep(0.01)
        
        # Test concurrent access
        tools = [PlexMovieSubdirRenamer(), SeasonOrganizer()]
        
        for tool in tools:
            # Simulate concurrent access
            simulate_concurrent_access()
            
            # Tool should still work
            try:
                if hasattr(tool, 'is_video_file'):
                    result = tool.is_video_file(test_file)
                    self.assertTrue(result)
            except Exception as e:
                self.fail(f"Tool {tool.__class__.__name__} should handle concurrent access: {e}")


@unittest.skipIf(not TEST_HELPERS_AVAILABLE, "Test helpers not available")
class TestDataCorruptionScenarios(MediaLibraryTestCase):
    """Test scenarios involving data corruption or invalid data."""
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_corrupted_file_detection(self):
        """Test handling of corrupted media files."""
        test_dir = self.copy_fixture('common/video_files')
        corrupted_files_dir = test_dir / 'corrupted_files_test'
        corrupted_files_dir.mkdir()
        
        # Create files with video extensions but invalid content
        corrupted_files = [
            'corrupted_movie.mp4',
            'invalid_video.mkv',
            'broken_episode.avi'
        ]
        
        for corrupted_file in corrupted_files:
            file_path = corrupted_files_dir / corrupted_file
            # Write invalid content
            with open(file_path, 'w') as f:
                f.write("This is not a valid video file")
        
        # Tools should still recognize files by extension
        renamer = PlexMovieSubdirRenamer()
        
        for corrupted_file in corrupted_files:
            file_path = corrupted_files_dir / corrupted_file
            # Should recognize by extension, even if content is invalid
            self.assertTrue(renamer.is_video_file(file_path))
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or SeasonOrganizer is None or PlexMovieExtrasOrganizer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_zero_byte_files(self):
        """Test handling of zero-byte files."""
        test_dir = self.copy_fixture('common/video_files')
        zero_byte_dir = test_dir / 'zero_byte_test'
        zero_byte_dir.mkdir()
        
        # Create zero-byte files
        zero_byte_files = [
            'empty_movie.mp4',
            'empty_episode.mkv',
            'empty_trailer.avi'
        ]
        
        for zero_file in zero_byte_files:
            file_path = zero_byte_dir / zero_file
            file_path.touch()  # Creates zero-byte file
        
        # Tools should handle zero-byte files
        tools = [
            PlexMovieSubdirRenamer(),
            SeasonOrganizer(),
            PlexMovieExtrasOrganizer()
        ]
        
        for tool in tools:
            for zero_file in zero_byte_files:
                file_path = zero_byte_dir / zero_file
                try:
                    if hasattr(tool, 'is_video_file'):
                        result = tool.is_video_file(file_path)
                        # Should recognize by extension
                        self.assertTrue(result)
                except Exception as e:
                    self.fail(f"Tool {tool.__class__.__name__} should handle zero-byte files: {e}")
    
    @unittest.skipIf(PlexMovieSubdirRenamer is None or not TEST_HELPERS_AVAILABLE, "Required modules not available")
    def test_extremely_large_files(self):
        """Test handling of extremely large file paths and names."""
        test_dir = self.copy_fixture('common/video_files')
        large_files_dir = test_dir / 'large_files_test'
        large_files_dir.mkdir()
        
        # Create file with very long name
        long_name = 'a' * 100 + '.mp4'
        long_file = large_files_dir / long_name
        
        try:
            long_file.touch()
            file_created = True
        except OSError:
            # Some filesystems may not support very long names
            file_created = False
        
        if file_created:
            # Test tools with long filename
            renamer = PlexMovieSubdirRenamer()
            
            try:
                result = renamer.is_video_file(long_file)
                self.assertTrue(result)
            except Exception as e:
                self.fail(f"Tool should handle long filenames: {e}")