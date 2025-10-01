#!/usr/bin/env python3
"""
TVDB Client Module for Media Library Tools
Version: 1.0

Provides TVDB v4 API client with JWT authentication and caching.

Features:
- JWT authentication with automatic token management
- 24-hour token caching for reduced API calls
- Search functionality for TV series
- Integration with cache_manager for response caching
- Integration with retry_utils for network resilience
- Statistics tracking for cache hits/misses and retries
- Debug logging support

This module provides shared TVDB API access functionality for tools that need
TV show metadata across media library tools.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Dict, Any

# Import will be handled by build system
# {{include retry_utils.py}}
# {{include cache_manager.py}}


class TVDBClient:
    """Client for interacting with TVDB v4 API with caching and retry support."""

    def __init__(self, api_key: str, debug: bool = False, cache: Optional['CacheManager'] = None):
        """
        Initialize TVDB client with API key and optional cache.

        Args:
            api_key: TVDB API key for authentication
            debug: Enable debug output for troubleshooting
            cache: Optional CacheManager instance for caching API responses
        """
        self.api_key = api_key
        self.debug = debug
        self.base_url = "https://api4.thetvdb.com/v4"
        self.token = None
        self.token_expires = 0
        self.cache = cache
        self.cache_hits = 0
        self.cache_misses = 0
        self.retry_attempts = 0
        self.retry_successes = 0

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def login(self) -> bool:
        """
        Login to TVDB API and obtain JWT token.

        Authenticates with TVDB v4 API using the provided API key and stores
        the resulting JWT token for subsequent API calls. Token is cached for
        24 hours to minimize authentication requests.

        Returns:
            True if login successful and token obtained, False otherwise
        """
        login_url = f"{self.base_url}/login"
        login_data = {"apikey": self.api_key}

        try:
            req = urllib.request.Request(
                login_url,
                data=json.dumps(login_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    self.token = data['data']['token']
                    # Token expires in 1 month, we'll cache for 24 hours to be safe
                    self.token_expires = time.time() + (24 * 60 * 60)
                    if self.debug:
                        print("Successfully logged in to TVDB API")
                    return True
                else:
                    if self.debug:
                        print(f"Login failed with status {response.status}")
                    return False

        except urllib.error.URLError as e:
            if self.debug:
                print(f"Login failed with network error: {e}")
            return False
        except (json.JSONDecodeError, KeyError) as e:
            if self.debug:
                print(f"Login failed with data error: {e}")
            return False

    def _ensure_authenticated(self) -> bool:
        """
        Ensure we have a valid authentication token.

        Checks if current token is valid and not expired. If token is missing
        or expired, attempts to login and obtain a new token.

        Returns:
            True if we have a valid token, False if authentication failed
        """
        if not self.token or time.time() >= self.token_expires:
            return self.login()
        return True

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def search_show(self, show_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a TV show by name with caching support.

        Searches TVDB API for a TV series matching the provided name. Results are
        cached if a cache manager is configured. Returns the best matching result
        with metadata including year information.

        Args:
            show_name: Name of the show to search for

        Returns:
            Dictionary with show data including 'name' and 'year' fields, or None if not found

        Example:
            >>> client = TVDBClient(api_key="your_key")
            >>> result = client.search_show("Breaking Bad")
            >>> print(f"{result['name']} ({result['year']})")
            Breaking Bad (2008)
        """
        # Check cache first if available
        if self.cache:
            cached_result = self.cache.get_show_search(show_name)
            if cached_result is not None:
                self.cache_hits += 1
                if self.debug:
                    print(f"Cache hit for '{show_name}': {cached_result.get('name')} ({cached_result.get('year')})")
                return cached_result
            else:
                self.cache_misses += 1

        if not self._ensure_authenticated():
            return None

        # Clean up show name for search
        clean_name = re.sub(r'[^\w\s-]', '', show_name).strip()
        search_url = f"{self.base_url}/search"
        params = {'query': clean_name, 'type': 'series'}

        try:
            url_with_params = f"{search_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url_with_params,
                headers={'Authorization': f'Bearer {self.token}'}
            )

            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    results = data.get('data', [])

                    if results:
                        # Return first result with year info
                        best_match = results[0]

                        # Cache the result if cache is available
                        if self.cache:
                            self.cache.set_show_search(show_name, best_match)

                        if self.debug:
                            print(f"Found show: {best_match.get('name')} ({best_match.get('year')})")
                        return best_match
                    else:
                        if self.debug:
                            print(f"No results found for '{show_name}'")
                        return None
                else:
                    if self.debug:
                        print(f"Search failed with status {response.status}")
                    return None

        except urllib.error.URLError as e:
            if self.debug:
                print(f"Search failed with network error: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            if self.debug:
                print(f"Search failed with data error: {e}")
            return None

    def get_statistics(self) -> Dict[str, int]:
        """
        Get client statistics for monitoring and debugging.

        Returns:
            Dictionary with statistics including:
            - cache_hits: Number of successful cache lookups
            - cache_misses: Number of cache misses requiring API calls
            - retry_attempts: Total number of retry attempts
            - retry_successes: Number of successful retries
        """
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'retry_attempts': self.retry_attempts,
            'retry_successes': self.retry_successes
        }
