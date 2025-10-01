#!/usr/bin/env python3
"""
Retry Utilities Module for Media Library Tools
Version: 1.0

Provides retry logic with exponential backoff for network operations.

Features:
- Exponential backoff with jitter
- Intelligent error classification (retriable vs non-retriable)
- Statistics tracking for retry attempts and successes
- Configurable retry parameters
- Debug logging support

This module provides shared retry functionality for API clients and network operations
across media library tools.
"""

import time
import random
import urllib.error
from typing import Callable, Any


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, multiplier: float = 2.0, max_delay: float = 30.0):
    """
    Decorator to retry function calls with exponential backoff.

    Implements exponential backoff with jitter to handle transient network failures
    and rate limiting. Intelligently classifies errors to determine retriability.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds before first retry (default: 1.0)
        multiplier: Multiplier for exponential backoff (default: 2.0)
        max_delay: Maximum delay between retries (default: 30.0)

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_retries=5, base_delay=2.0)
        def fetch_data(self, url):
            response = urllib.request.urlopen(url)
            return response.read()
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)

                    # Track successful retry if this wasn't the first attempt
                    if attempt > 0 and args and hasattr(args[0], 'retry_successes'):
                        args[0].retry_successes += 1

                    return result

                except (urllib.error.HTTPError, urllib.error.URLError, ConnectionError, OSError) as e:
                    last_exception = e

                    # Don't retry on final attempt
                    if attempt == max_retries:
                        break

                    # Determine if error is retriable
                    if isinstance(e, urllib.error.HTTPError):
                        # Retry on server errors and rate limiting
                        if e.code in [429, 500, 502, 503, 504]:
                            is_retriable = True
                        else:
                            # Don't retry on client errors (4xx except 429)
                            is_retriable = False
                    else:
                        # Retry on network errors (URLError, ConnectionError, OSError)
                        is_retriable = True

                    if not is_retriable:
                        break

                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (multiplier ** attempt), max_delay)
                    jitter = random.uniform(0.1, 0.5)  # Add jitter to prevent thundering herd
                    delay += jitter

                    # Update retry statistics if available in args/self
                    if args and hasattr(args[0], 'retry_attempts'):
                        args[0].retry_attempts += 1

                    # Log retry attempt if debug is available in args/self
                    debug = False
                    if args and hasattr(args[0], 'debug'):
                        debug = args[0].debug

                    if debug:
                        print(f"Retry attempt {attempt + 1}/{max_retries} after {delay:.1f}s delay. Error: {e}")

                    time.sleep(delay)

                except Exception as e:
                    # Don't retry on non-network exceptions
                    last_exception = e
                    break

            # Re-raise the last exception if all retries failed
            raise last_exception

        return wrapper
    return decorator
