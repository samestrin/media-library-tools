#!/usr/bin/env python3
"""
Test Configuration and Settings

Centralized configuration for the media library tools test suite.
Provides test settings, paths, and common test utilities.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Test suite configuration
TEST_CONFIG = {
    # Test execution settings
    'verbose': os.environ.get('TEST_VERBOSE', 'false').lower() == 'true',
    'debug': os.environ.get('TEST_DEBUG', 'false').lower() == 'true',
    'cleanup_on_success': os.environ.get('TEST_CLEANUP', 'true').lower() == 'true',
    'preserve_fixtures': os.environ.get('PRESERVE_FIXTURES', 'false').lower() == 'true',
    
    # Test data settings
    'max_test_dirs': int(os.environ.get('MAX_TEST_DIRS', '50')),
    'test_timeout': int(os.environ.get('TEST_TIMEOUT', '300')),  # 5 minutes
    'large_file_threshold': int(os.environ.get('LARGE_FILE_THRESHOLD', '100')),  # MB
    
    # Fixture settings
    'default_video_size': '1MB',
    'default_audio_size': '5MB',
    'default_subtitle_size': '50KB',
    'default_image_size': '500KB',
    
    # SABnzbd test settings
    'sabnzbd_indicators': ['SABnzbd_nzo', 'SABnzbd_nzb', '__UNPACK__'],
    'bittorrent_indicators': ['.torrent', '.magnet'],
    
    # Plex test settings
    'plex_video_extensions': ['.mp4', '.mkv', '.avi', '.mov', '.wmv'],
    'plex_audio_extensions': ['.mp3', '.flac', '.aac', '.ogg', '.wav'],
    'plex_subtitle_extensions': ['.srt', '.vtt', '.ass', '.ssa', '.sub'],
    'plex_image_extensions': ['.jpg', '.jpeg', '.png', '.bmp', '.gif'],
    
    # Test patterns
    'movie_patterns': [
        'Movie.Title.{year}.{quality}.{format}',
        '{title} ({year}).{format}',
        '{title}.{year}.{quality}.{codec}.{format}'
    ],
    'tv_patterns': [
        '{show}.S{season:02d}E{episode:02d}.{title}.{format}',
        '{show} S{season:02d}E{episode:02d} {title}.{format}',
        '{show}.{season}x{episode:02d}.{title}.{format}'
    ],
    
    # Quality indicators
    'video_qualities': ['480p', '720p', '1080p', '2160p', '4K'],
    'audio_qualities': ['128k', '192k', '256k', '320k', 'FLAC'],
    
    # Test data sizes (for performance testing)
    'test_sizes': {
        'small': {'files': 10, 'dirs': 3, 'size': '10MB'},
        'medium': {'files': 100, 'dirs': 10, 'size': '100MB'},
        'large': {'files': 1000, 'dirs': 50, 'size': '1GB'}
    }
}

# Test environment paths
TEST_PATHS = {
    'project_root': Path(__file__).parent.parent,
    'tests_dir': Path(__file__).parent,
    'fixtures_dir': Path(__file__).parent / 'fixtures',
    'utils_dir': Path(__file__).parent / 'utils',
    'temp_dir': Path(__file__).parent / 'temp',
    'output_dir': Path(__file__).parent / 'output'
}

# Ensure test directories exist
for path_name, path_obj in TEST_PATHS.items():
    if path_name in ['temp_dir', 'output_dir']:
        path_obj.mkdir(parents=True, exist_ok=True)

# Test suite categories
TEST_CATEGORIES = {
    'unit': {
        'pattern': 'test_*.py',
        'timeout': 60,
        'description': 'Fast unit tests for individual components',
        'subdir': 'unit'
    },
    'integration': {
        'pattern': 'test_*.py',
        'timeout': 300,
        'description': 'Integration tests for component interactions',
        'subdir': 'integration'
    },
    'performance': {
        'pattern': 'test_*.py',
        'timeout': 600,
        'description': 'Performance and benchmark tests',
        'subdir': 'performance'
    },
    'fixture': {
        'pattern': 'test_fixture_*.py',
        'timeout': 120,
        'description': 'Tests for fixture system and test data'
    },
    'examples': {
        'pattern': 'test_*.py',
        'timeout': 180,
        'description': 'Example tests and demonstrations',
        'subdir': 'examples'
    }
}

# Common test data
TEST_DATA = {
    'sample_movies': [
        'Action Movie (2023).mkv',
        'Comedy Film (2022).mp4',
        'Drama Picture (2021).avi',
        'Sci-Fi Flick (2024).mov'
    ],
    'sample_tv_shows': [
        'Drama Series S01E01 Pilot.mkv',
        'Comedy Show S02E05 Funny Episode.mp4',
        'Action Series S03E10 Finale.avi',
        'Mystery Show S01E03 The Clue.mov'
    ],
    'sample_extras': [
        'behind_the_scenes.mp4',
        'deleted_scenes.mkv',
        'director_commentary.mp4',
        'making_of.avi',
        'trailer.mp4',
        'interview.mov'
    ],
    'sample_audio': [
        'soundtrack.mp3',
        'theme_song.flac',
        'background_music.aac',
        'dialogue.wav'
    ],
    'sample_subtitles': [
        'english.srt',
        'spanish.vtt',
        'french.ass',
        'german.ssa'
    ],
    'sample_images': [
        'poster.jpg',
        'fanart.png',
        'banner.jpeg',
        'thumb.gif'
    ]
}

# Test validation rules
VALIDATION_RULES = {
    'file_size_limits': {
        'min_size': 1,  # bytes
        'max_size': 1024 * 1024 * 1024,  # 1GB
        'warn_size': 100 * 1024 * 1024   # 100MB
    },
    'filename_rules': {
        'max_length': 255,
        'forbidden_chars': ['<', '>', ':', '"', '|', '?', '*'],
        'reserved_names': ['CON', 'PRN', 'AUX', 'NUL']
    },
    'directory_rules': {
        'max_depth': 10,
        'max_files_per_dir': 1000,
        'max_total_files': 10000
    }
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    'file_operations': {
        'copy_1mb_file': 0.1,      # seconds
        'scan_1000_files': 1.0,    # seconds
        'delete_100_files': 0.5    # seconds
    },
    'directory_operations': {
        'create_deep_structure': 2.0,  # seconds
        'traverse_large_tree': 5.0,   # seconds
        'cleanup_test_data': 3.0      # seconds
    },
    'media_operations': {
        'detect_video_format': 0.01,   # seconds
        'calculate_directory_size': 1.0,  # seconds
        'organize_100_files': 10.0     # seconds
    }
}

# Error handling test cases
ERROR_TEST_CASES = {
    'permission_errors': [
        'readonly_file',
        'readonly_directory',
        'no_write_permission',
        'no_read_permission'
    ],
    'filesystem_errors': [
        'nonexistent_path',
        'invalid_filename',
        'disk_full_simulation',
        'network_path_unavailable'
    ],
    'format_errors': [
        'corrupted_video_file',
        'unsupported_format',
        'empty_file',
        'binary_data_as_text'
    ]
}

# Test reporting configuration
REPORTING_CONFIG = {
    'output_formats': ['console', 'junit', 'html'],
    'coverage_threshold': 80,  # percentage
    'performance_regression_threshold': 20,  # percentage
    'log_levels': {
        'console': 'INFO',
        'file': 'DEBUG',
        'performance': 'WARNING'
    }
}


def get_test_config(key: str = None) -> Any:
    """
    Get test configuration value.
    
    Args:
        key: Configuration key to retrieve. If None, returns entire config.
        
    Returns:
        Configuration value or entire config dict.
    """
    if key is None:
        return TEST_CONFIG
    return TEST_CONFIG.get(key)


def get_test_path(path_name: str) -> Path:
    """
    Get test path by name.
    
    Args:
        path_name: Name of the path to retrieve.
        
    Returns:
        Path object for the requested path.
        
    Raises:
        KeyError: If path_name is not found.
    """
    if path_name not in TEST_PATHS:
        raise KeyError(f"Unknown test path: {path_name}")
    return TEST_PATHS[path_name]


def get_test_data(category: str) -> List[str]:
    """
    Get test data by category.
    
    Args:
        category: Category of test data to retrieve.
        
    Returns:
        List of test data items.
        
    Raises:
        KeyError: If category is not found.
    """
    if category not in TEST_DATA:
        raise KeyError(f"Unknown test data category: {category}")
    return TEST_DATA[category].copy()


def validate_test_environment() -> Dict[str, bool]:
    """
    Validate the test environment setup.
    
    Returns:
        Dictionary with validation results.
    """
    results = {}
    
    # Check required directories
    for path_name, path_obj in TEST_PATHS.items():
        results[f"path_{path_name}_exists"] = path_obj.exists()
        if path_name in ['temp_dir', 'output_dir']:
            results[f"path_{path_name}_writable"] = os.access(path_obj, os.W_OK)
    
    # Check Python version
    results['python_version_ok'] = sys.version_info >= (3, 7)
    
    # Check available disk space
    try:
        import shutil
        free_space = shutil.disk_usage(TEST_PATHS['temp_dir']).free
        results['sufficient_disk_space'] = free_space > (1024 * 1024 * 1024)  # 1GB
    except Exception:
        results['sufficient_disk_space'] = False
    
    return results


def setup_test_environment() -> bool:
    """
    Set up the test environment.
    
    Returns:
        True if setup was successful, False otherwise.
    """
    try:
        # Create required directories
        for path_name, path_obj in TEST_PATHS.items():
            if path_name in ['temp_dir', 'output_dir']:
                path_obj.mkdir(parents=True, exist_ok=True)
        
        # Validate environment
        validation_results = validate_test_environment()
        failed_checks = [k for k, v in validation_results.items() if not v]
        
        if failed_checks:
            print(f"Test environment validation failed: {failed_checks}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Failed to set up test environment: {e}")
        return False


def cleanup_test_environment() -> bool:
    """
    Clean up the test environment.
    
    Returns:
        True if cleanup was successful, False otherwise.
    """
    try:
        import shutil
        
        # Clean up temporary directories
        for path_name in ['temp_dir', 'output_dir']:
            path_obj = TEST_PATHS[path_name]
            if path_obj.exists():
                shutil.rmtree(path_obj)
                path_obj.mkdir(parents=True, exist_ok=True)
        
        return True
        
    except Exception as e:
        print(f"Failed to clean up test environment: {e}")
        return False


if __name__ == '__main__':
    # Validate and display test environment information
    print("Media Library Tools - Test Configuration")
    print("=" * 50)
    
    print("\nTest Paths:")
    for name, path in TEST_PATHS.items():
        status = "✅" if path.exists() else "❌"
        print(f"  {name}: {path} {status}")
    
    print("\nTest Configuration:")
    for key, value in TEST_CONFIG.items():
        print(f"  {key}: {value}")
    
    print("\nValidation Results:")
    validation_results = validate_test_environment()
    for check, result in validation_results.items():
        status = "✅" if result else "❌"
        print(f"  {check}: {status}")
    
    # Set up environment if needed
    if not all(validation_results.values()):
        print("\nSetting up test environment...")
        if setup_test_environment():
            print("✅ Test environment setup complete")
        else:
            print("❌ Test environment setup failed")
    else:
        print("\n✅ Test environment is ready")