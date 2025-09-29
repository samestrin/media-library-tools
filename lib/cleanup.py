#!/usr/bin/env python3
"""
System Trash File Cleanup Module

Centralized cleanup utilities for removing system-generated trash files
that commonly cause issues with media library tools, especially files
transferred via rsync or network shares.

Common Issues Solved:
- .DS_Store files from macOS causing directory conflicts
- Thumbs.db files from Windows
- ._ AppleDouble files from macOS resource forks
- Desktop.ini files from Windows
- Other hidden system files

Author: Media Library Tools Project
Version: 1.0.0
"""

import os
from pathlib import Path
from typing import List, Optional, Set


class SystemTrashCleaner:
    """
    Handles detection and removal of system-generated trash files.

    These files are commonly created by operating systems and can cause
    conflicts during media library operations, especially after rsync
    transfers or network share access.
    """

    # System trash file patterns
    TRASH_FILES = {
        '.DS_Store',        # macOS Finder metadata
        'Thumbs.db',        # Windows thumbnail cache
        'Desktop.ini',      # Windows folder settings
        '.Spotlight-V100',  # macOS Spotlight index
        '.Trashes',         # macOS trash folder
        '.fseventsd',       # macOS file system events
        '.TemporaryItems',  # macOS temporary items
        '.localized',       # macOS localization
        'desktop.ini',      # Windows (lowercase variant)
        'thumbs.db',        # Windows (lowercase variant)
    }

    # Patterns for prefixed trash files
    TRASH_PREFIXES = {
        '._',               # macOS AppleDouble resource fork files
        '.~',               # Temporary/backup files
    }

    # Patterns for suffixed trash files
    TRASH_SUFFIXES = {
        '.tmp',             # Temporary files
        '.temp',            # Temporary files (variant)
        '~',                # Backup files
    }

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        """
        Initialize the trash cleaner.

        Args:
            verbose: Enable verbose output
            dry_run: Preview mode - don't actually delete files
        """
        self.verbose = verbose
        self.dry_run = dry_run
        self.removed_files: List[Path] = []
        self.failed_removals: List[tuple] = []

    def is_trash_file(self, file_path: Path) -> bool:
        """
        Determine if a file is system trash.

        Args:
            file_path: Path to check

        Returns:
            True if file matches trash patterns
        """
        filename = file_path.name

        # Check exact matches
        if filename in self.TRASH_FILES:
            return True

        # Check prefixes
        for prefix in self.TRASH_PREFIXES:
            if filename.startswith(prefix):
                return True

        # Check suffixes
        for suffix in self.TRASH_SUFFIXES:
            if filename.endswith(suffix):
                return True

        return False

    def clean_directory(self, directory: Path, recursive: bool = False) -> int:
        """
        Clean trash files from a directory.

        Args:
            directory: Directory to clean
            recursive: Also clean subdirectories

        Returns:
            Number of files removed
        """
        if not directory.exists() or not directory.is_dir():
            if self.verbose:
                print(f"Directory does not exist or is not a directory: {directory}")
            return 0

        removed_count = 0

        try:
            if recursive:
                # Walk entire directory tree
                for root, dirs, files in os.walk(directory):
                    root_path = Path(root)

                    # Clean files in this directory
                    for filename in files:
                        file_path = root_path / filename
                        if self.is_trash_file(file_path):
                            if self._remove_file(file_path):
                                removed_count += 1

                    # Clean trash directories
                    for dirname in dirs[:]:  # Copy list to allow modification
                        dir_path = root_path / dirname
                        if dirname in self.TRASH_FILES:
                            if self._remove_directory(dir_path):
                                removed_count += 1
                                dirs.remove(dirname)  # Don't descend into removed dir
            else:
                # Only clean current directory
                for item in directory.iterdir():
                    if item.is_file() and self.is_trash_file(item):
                        if self._remove_file(item):
                            removed_count += 1
                    elif item.is_dir() and item.name in self.TRASH_FILES:
                        if self._remove_directory(item):
                            removed_count += 1

        except PermissionError as e:
            if self.verbose:
                print(f"Permission denied accessing {directory}: {e}")
        except Exception as e:
            if self.verbose:
                print(f"Error cleaning {directory}: {e}")

        return removed_count

    def _remove_file(self, file_path: Path) -> bool:
        """
        Remove a single trash file.

        Args:
            file_path: File to remove

        Returns:
            True if removed successfully
        """
        if self.dry_run:
            if self.verbose:
                print(f"[DRY RUN] Would remove: {file_path}")
            self.removed_files.append(file_path)
            return True

        try:
            os.remove(file_path)
            self.removed_files.append(file_path)
            if self.verbose:
                print(f"Removed: {file_path}")
            return True
        except OSError as e:
            self.failed_removals.append((file_path, str(e)))
            if self.verbose:
                print(f"Error removing {file_path}: {e}")
            return False

    def _remove_directory(self, dir_path: Path) -> bool:
        """
        Remove a trash directory.

        Args:
            dir_path: Directory to remove

        Returns:
            True if removed successfully
        """
        if self.dry_run:
            if self.verbose:
                print(f"[DRY RUN] Would remove directory: {dir_path}")
            self.removed_files.append(dir_path)
            return True

        try:
            import shutil
            shutil.rmtree(dir_path)
            self.removed_files.append(dir_path)
            if self.verbose:
                print(f"Removed directory: {dir_path}")
            return True
        except OSError as e:
            self.failed_removals.append((dir_path, str(e)))
            if self.verbose:
                print(f"Error removing directory {dir_path}: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get cleanup statistics.

        Returns:
            Dictionary with cleanup stats
        """
        return {
            'files_removed': len(self.removed_files),
            'failed_removals': len(self.failed_removals),
            'removed_list': [str(p) for p in self.removed_files],
            'failed_list': [(str(p), e) for p, e in self.failed_removals]
        }

    def print_summary(self) -> None:
        """Print cleanup summary."""
        stats = self.get_stats()

        if self.dry_run:
            print(f"\n[DRY RUN] Would remove {stats['files_removed']} trash files")
        else:
            print(f"\nRemoved {stats['files_removed']} trash files")

        if stats['failed_removals'] > 0:
            print(f"Failed to remove {stats['failed_removals']} files")
            if self.verbose:
                print("\nFailed removals:")
                for path, error in stats['failed_list']:
                    print(f"  {path}: {error}")


def quick_clean(directory: Path, recursive: bool = False,
                verbose: bool = False, dry_run: bool = False) -> int:
    """
    Quick cleanup function for simple use cases.

    Args:
        directory: Directory to clean
        recursive: Clean subdirectories
        verbose: Show detailed output
        dry_run: Preview mode

    Returns:
        Number of files removed

    Example:
        >>> from pathlib import Path
        >>> import lib.cleanup as cleanup
        >>> removed = cleanup.quick_clean(Path('.'), recursive=True, verbose=True)
    """
    cleaner = SystemTrashCleaner(verbose=verbose, dry_run=dry_run)
    count = cleaner.clean_directory(directory, recursive=recursive)

    if verbose:
        cleaner.print_summary()

    return count

