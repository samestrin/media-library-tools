#!/usr/bin/env python3
"""
Filesystem Operations Module for Media Library Tools
Version: 1.0

This module contains filesystem utility functions including:
- Directory size calculation and analysis
- Path validation and normalization
- File and directory operations
- Permission handling and safety checks
- Media file detection and classification

This is part of the modular library structure that enables selective inclusion
in built tools while maintaining the self-contained principle.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Set


def get_directory_size(path: str) -> int:
    """
    Calculate total size of directory using system du command for accuracy.
    
    Args:
        path: Directory path to analyze
        
    Returns:
        Total size in bytes
    """
    try:
        # Use du command for accurate size calculation
        result = subprocess.run(['du', '-sb', path], 
                              capture_output=True, text=True, check=True)
        size_str = result.stdout.split()[0]
        return int(size_str)
    except (subprocess.CalledProcessError, ValueError, IndexError):
        # Fallback to Python calculation
        return _get_directory_size_python(path)


def _get_directory_size_python(path: str) -> int:
    """
    Python fallback for directory size calculation.
    
    Args:
        path: Directory path to analyze
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    continue  # Skip inaccessible files
    except (OSError, IOError):
        pass
    return total_size


def validate_directory_path(path: str) -> Tuple[bool, str]:
    """
    Validate that a path exists and is a directory.
    
    Args:
        path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path cannot be empty"
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        return False, f"Path does not exist: {path}"
    
    if not path_obj.is_dir():
        return False, f"Path is not a directory: {path}"
    
    # Check if we can read the directory
    try:
        list(path_obj.iterdir())
    except PermissionError:
        return False, f"Permission denied accessing directory: {path}"
    except OSError as e:
        return False, f"Error accessing directory: {path} ({e})"
    
    return True, ""


def safe_remove_directory(path: str, dry_run: bool = True) -> Tuple[bool, str]:
    """
    Safely remove a directory with validation and optional dry-run.
    
    Args:
        path: Directory path to remove
        dry_run: If True, only simulate the removal
        
    Returns:
        Tuple of (success, message)
    """
    if dry_run:
        return True, f"DRY RUN: Would remove directory {path}"
    
    try:
        shutil.rmtree(path)
        return True, f"Successfully removed directory: {path}"
    except PermissionError:
        return False, f"Permission denied removing directory: {path}"
    except OSError as e:
        return False, f"Error removing directory: {path} ({e})"


def get_subdirectories(path: str, max_depth: Optional[int] = None) -> List[str]:
    """
    Get list of subdirectories with optional depth limit.
    
    Args:
        path: Parent directory path
        max_depth: Maximum depth to traverse (None for unlimited)
        
    Returns:
        List of subdirectory paths
    """
    subdirs = []
    
    try:
        for root, dirs, files in os.walk(path):
            # Calculate current depth
            if max_depth is not None:
                current_depth = root[len(path):].count(os.sep)
                if current_depth >= max_depth:
                    dirs.clear()  # Don't recurse deeper
                    continue
            
            for dir_name in dirs:
                subdir_path = os.path.join(root, dir_name)
                subdirs.append(subdir_path)
                
    except (OSError, IOError):
        pass  # Skip inaccessible directories
    
    return sorted(subdirs)


def is_media_file(filename: str) -> bool:
    """
    Check if a file is a media file based on extension.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if file appears to be a media file
    """
    media_extensions = {
        # Video extensions
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v',
        '.mpg', '.mpeg', '.m2v', '.3gp', '.f4v', '.asf', '.rm', '.rmvb',
        '.vob', '.ts', '.mts', '.m2ts',
        
        # Audio extensions
        '.mp3', '.flac', '.wav', '.aac', '.ogg', '.wma', '.m4a', '.opus',
        '.ape', '.ac3', '.dts', '.aiff', '.au', '.ra'
    }
    
    return Path(filename).suffix.lower() in media_extensions


def count_files_by_type(directory: str) -> dict:
    """
    Count files by type in a directory.
    
    Args:
        directory: Directory to analyze
        
    Returns:
        Dictionary with counts by file type
    """
    counts = {
        'media_files': 0,
        'other_files': 0,
        'subdirectories': 0,
        'total_size': 0
    }
    
    try:
        for item in Path(directory).iterdir():
            if item.is_file():
                if is_media_file(item.name):
                    counts['media_files'] += 1
                else:
                    counts['other_files'] += 1
                try:
                    counts['total_size'] += item.stat().st_size
                except (OSError, IOError):
                    pass
            elif item.is_dir():
                counts['subdirectories'] += 1
                
    except (OSError, IOError):
        pass  # Skip inaccessible directories
    
    return counts


def normalize_path(path: str) -> str:
    """
    Normalize a path for consistent handling.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path string
    """
    return str(Path(path).resolve())


def has_write_permission(path: str) -> bool:
    """
    Check if we have write permission to a directory.
    
    Args:
        path: Directory path to check
        
    Returns:
        True if writable, False otherwise
    """
    try:
        return os.access(path, os.W_OK)
    except (OSError, IOError):
        return False