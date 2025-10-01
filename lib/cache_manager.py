#!/usr/bin/env python3
"""
Cache Manager Module for Media Library Tools
Version: 1.0

Provides generic caching functionality with JSON-based storage and TTL management.

Features:
- Generic key-value caching with TTL support
- XDG directory standards compliance
- Automatic expired entry removal
- Cache statistics and cleanup functionality
- Thread-safe operations
- Cross-platform support (Windows, macOS, Linux)

This module provides shared caching functionality for API clients and data management
across media library tools.
"""

import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any


class CacheManager:
    """Generic JSON-based cache manager with TTL support."""

    def __init__(self, cache_name: str, cache_dir: Optional[str] = None, ttl_days: int = 14):
        """
        Initialize cache with optional custom directory and TTL.

        Args:
            cache_name: Name for the cache file (e.g., 'plex_tv_shows')
            cache_dir: Custom cache directory, defaults to ~/.cache
            ttl_days: Time-to-live in days for cached entries (default: 14)
        """
        self.cache_name = cache_name
        self.ttl_days = ttl_days
        self.ttl_seconds = ttl_days * 24 * 3600

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use XDG cache directory standard
            self.cache_dir = Path.home() / '.cache'

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / f'{cache_name}.json'
        self._cache_data = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cache data from JSON file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            self._cache_data = {}

    def _save_cache(self) -> None:
        """Save cache data to JSON file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass  # Fail silently if we can't write cache

    def _generate_cache_key(self, key: str) -> str:
        """
        Generate normalized cache key from input string.

        Args:
            key: Input key to normalize

        Returns:
            Normalized cache key
        """
        # Clean key for consistent cache keys
        clean_key = re.sub(r'[^\w\s-]', '', key).strip().lower()
        return clean_key

    def _is_expired(self, timestamp: float) -> bool:
        """
        Check if cache entry is expired based on TTL.

        Args:
            timestamp: Unix timestamp of cache entry

        Returns:
            True if expired, False otherwise
        """
        return (time.time() - timestamp) > self.ttl_seconds

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached value for key.

        Args:
            key: Cache key to look up

        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._generate_cache_key(key)

        if cache_key in self._cache_data:
            entry = self._cache_data[cache_key]
            if not self._is_expired(entry['timestamp']):
                return entry['data']
            else:
                # Remove expired entry
                del self._cache_data[cache_key]
                self._save_cache()

        return None

    def set(self, key: str, data: Dict[str, Any]) -> None:
        """
        Cache data for key.

        Args:
            key: Cache key to set
            data: Data to cache
        """
        cache_key = self._generate_cache_key(key)

        self._cache_data[cache_key] = {
            'timestamp': time.time(),
            'data': data
        }

        self._save_cache()

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        expired_keys = []
        current_time = time.time()

        for key, entry in self._cache_data.items():
            if self._is_expired(entry['timestamp']):
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache_data[key]

        if expired_keys:
            self._save_cache()

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics including:
            - cache_file: Path to cache file
            - total_entries: Total number of cached entries
            - expired_entries: Number of expired entries
            - cache_size_bytes: Size of cache file in bytes
            - oldest_entry_age_days: Age of oldest entry in days
        """
        current_time = time.time()
        total_entries = len(self._cache_data)
        expired_count = 0
        oldest_timestamp = current_time

        for entry in self._cache_data.values():
            if self._is_expired(entry['timestamp']):
                expired_count += 1
            if entry['timestamp'] < oldest_timestamp:
                oldest_timestamp = entry['timestamp']

        cache_size = 0
        if self.cache_file.exists():
            cache_size = self.cache_file.stat().st_size

        return {
            'cache_file': str(self.cache_file),
            'total_entries': total_entries,
            'expired_entries': expired_count,
            'cache_size_bytes': cache_size,
            'oldest_entry_age_days': (current_time - oldest_timestamp) / 86400 if total_entries > 0 else 0
        }

    def clear(self) -> bool:
        """
        Clear all cache data.

        Returns:
            True if cache was cleared successfully, False otherwise
        """
        try:
            self._cache_data = {}
            if self.cache_file.exists():
                self.cache_file.unlink()
            return True
        except OSError:
            return False

    # Convenience methods for backward compatibility with TVDBCache
    def get_show_search(self, show_name: str) -> Optional[Dict[str, Any]]:
        """Get cached show search result (backward compatibility)."""
        return self.get(show_name)

    def set_show_search(self, show_name: str, data: Dict[str, Any]) -> None:
        """Cache show search result (backward compatibility)."""
        self.set(show_name, data)

    def clear_cache(self) -> bool:
        """Clear all cache data (backward compatibility)."""
        return self.clear()
