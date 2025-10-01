#!/usr/bin/env python3
"""
Performance Tests for Configuration Priority System
Validates performance benchmarks and security of configuration reading
"""

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.core import read_config_bool, read_config_value, ConfigCache, _config_cache


class TestConfigurationPerformance(unittest.TestCase):
    """Test configuration reading performance"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        _config_cache.clear_cache()

        # Create test .env file
        with open('.env', 'w') as f:
            for i in range(100):
                f.write(f'KEY_{i}=value_{i}\n')

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_single_read_performance(self):
        """Test that single configuration read is < 1ms"""
        start = time.time()
        value = read_config_value('KEY_50', default='')
        elapsed = (time.time() - start) * 1000  # Convert to milliseconds

        self.assertLess(elapsed, 1.0, f"Read took {elapsed:.3f}ms (should be < 1ms)")
        self.assertEqual(value, 'value_50')

    def test_cached_read_performance(self):
        """Test that cached reads are significantly faster"""
        # First read (uncached)
        start = time.time()
        value1 = read_config_value('KEY_10', default='')
        first_read_time = time.time() - start

        # Second read (cached)
        start = time.time()
        value2 = read_config_value('KEY_10', default='')
        cached_read_time = time.time() - start

        self.assertEqual(value1, value2)
        # Cached read should be at least 2x faster
        self.assertLess(cached_read_time, first_read_time / 2,
                        f"Cached read ({cached_read_time:.6f}s) not faster than "
                        f"first read ({first_read_time:.6f}s)")

    def test_bulk_read_performance(self):
        """Test that multiple reads complete quickly"""
        start = time.time()
        for i in range(100):
            value = read_config_value(f'KEY_{i}', default='')
            self.assertEqual(value, f'value_{i}')
        elapsed = time.time() - start

        # 100 reads should complete in under 100ms with caching
        self.assertLess(elapsed, 0.1, f"100 reads took {elapsed:.3f}s (should be < 0.1s)")

    def test_boolean_conversion_performance(self):
        """Test boolean conversion performance"""
        with open('.env', 'w') as f:
            f.write('BOOL_KEY=true\n')

        _config_cache.clear_cache()

        start = time.time()
        for _ in range(1000):
            value = read_config_bool('BOOL_KEY', default=False)
            self.assertTrue(value)
        elapsed = (time.time() - start) * 1000

        # 1000 cached boolean reads should be < 10ms
        avg_time = elapsed / 1000
        self.assertLess(avg_time, 0.01, f"Average read time {avg_time:.6f}ms (should be < 0.01ms)")


class TestCacheMemoryUsage(unittest.TestCase):
    """Test cache memory usage"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_memory_reasonable(self):
        """Test that cache memory usage is reasonable"""
        cache = ConfigCache()

        # Create multiple env files
        for i in range(10):
            filename = f'.env_{i}'
            with open(filename, 'w') as f:
                for j in range(100):
                    f.write(f'KEY_{j}=value_{j}\n')

            # Load into cache
            cache.get_env_file(filename)

        # Check cache size (rough estimate)
        import sys
        cache_size = sys.getsizeof(cache._cache)

        # Cache should be < 1MB for this test data
        self.assertLess(cache_size, 1024 * 1024,
                        f"Cache size {cache_size / 1024:.1f}KB exceeds 1MB limit")


class TestConcurrentAccess(unittest.TestCase):
    """Test concurrent configuration access"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create test .env file
        with open('.env', 'w') as f:
            for i in range(50):
                f.write(f'KEY_{i}=value_{i}\n')

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_concurrent_reads_thread_safe(self):
        """Test that concurrent reads are thread-safe"""
        import threading

        results = []
        errors = []

        def read_config():
            try:
                for i in range(50):
                    value = read_config_value(f'KEY_{i}', default='')
                    results.append(value == f'value_{i}')
            except Exception as e:
                errors.append(e)

        # Create 10 threads
        threads = [threading.Thread(target=read_config) for _ in range(10)]

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.time() - start

        # No errors should occur
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")

        # All reads should be correct
        self.assertEqual(len(results), 500)  # 10 threads * 50 reads
        self.assertTrue(all(results), "Some reads returned incorrect values")

        # Should complete in reasonable time (< 1 second)
        self.assertLess(elapsed, 1.0, f"Concurrent reads took {elapsed:.3f}s")


class TestConfigurationSecurity(unittest.TestCase):
    """Test security aspects of configuration system"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_no_code_injection_in_values(self):
        """Test that configuration values don't execute code"""
        # Create .env with potentially dangerous values
        with open('.env', 'w') as f:
            f.write('DANGER="; rm -rf /"\n')
            f.write('EVAL="$(malicious_command)"\n')

        # Read values - should be treated as plain strings
        danger = read_config_value('DANGER', default='')
        eval_val = read_config_value('EVAL', default='')

        # Values should be returned as-is, not executed
        self.assertEqual(danger, '"; rm -rf /"')
        self.assertEqual(eval_val, '"$(malicious_command)"')

    def test_path_traversal_protection(self):
        """Test that path traversal in env paths doesn't expose files"""
        # Try to read file outside of expected locations
        result = read_config_value('KEY', local_env_path='../../etc/passwd', default='safe')

        # Should safely fall back to default (file won't be found/read)
        # This tests that the system handles invalid paths gracefully
        self.assertEqual(result, 'safe')

    def test_permission_denied_graceful(self):
        """Test graceful handling of permission denied errors"""
        # Create unreadable .env file
        with open('.env', 'w') as f:
            f.write('KEY=value\n')

        os.chmod('.env', 0o000)

        try:
            # Should not crash, should use default
            value = read_config_value('KEY', default='default')
            self.assertEqual(value, 'default')
        finally:
            # Restore permissions for cleanup
            os.chmod('.env', 0o644)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Comprehensive performance benchmark tests"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        _config_cache.clear_cache()

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_benchmark_summary(self):
        """Run comprehensive benchmark and report results"""
        # Create test file
        with open('.env', 'w') as f:
            for i in range(100):
                f.write(f'KEY_{i}=value_{i}\n')

        benchmarks = {}

        # Benchmark 1: First read (uncached)
        _config_cache.clear_cache()
        start = time.time()
        value = read_config_value('KEY_0', default='')
        benchmarks['first_read_ms'] = (time.time() - start) * 1000

        # Benchmark 2: Cached read
        start = time.time()
        value = read_config_value('KEY_0', default='')
        benchmarks['cached_read_ms'] = (time.time() - start) * 1000

        # Benchmark 3: Boolean conversion
        with open('.env', 'w') as f:
            f.write('BOOL=true\n')
        _config_cache.clear_cache()
        start = time.time()
        for _ in range(100):
            value = read_config_bool('BOOL', default=False)
        benchmarks['100_bool_reads_ms'] = (time.time() - start) * 1000

        # Report results
        print("\n" + "=" * 60)
        print("Configuration System Performance Benchmarks")
        print("=" * 60)
        for name, value in benchmarks.items():
            print(f"  {name:30s}: {value:8.3f}ms")
        print("=" * 60)

        # Verify benchmarks meet requirements
        self.assertLess(benchmarks['first_read_ms'], 1.0,
                        "First read should be < 1ms")
        self.assertLess(benchmarks['cached_read_ms'], 0.1,
                        "Cached read should be < 0.1ms")


if __name__ == '__main__':
    unittest.main(verbosity=2)
