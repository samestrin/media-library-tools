#!/usr/bin/env python3
"""
Performance tests for SABnzbd Cleanup Directory Analysis Optimization
Tests baseline performance and validates optimization effectiveness
"""

import os
import shutil
import statistics
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Add SABnzbd directory to path
sabnzbd_dir = os.path.join(project_root, "SABnzbd")
sys.path.insert(0, sabnzbd_dir)

# Import SABnzbdDetector
try:
    from sabnzbd_cleanup import SABnzbdDetector
except ImportError as e:
    SABnzbdDetector = None
    print(f"Warning: Could not import SABnzbdDetector: {e}")


@unittest.skipIf(SABnzbdDetector is None, "SABnzbdDetector not available")
class SABnzbdPerformanceTest(unittest.TestCase):
    """
    Performance tests for SABnzbd directory analysis optimization
    """

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.detector = SABnzbdDetector(verbose=False, debug=False)

    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_sabnzbd_directory(
        self,
        path: Path,
        include_nzb=True,
        include_par2=True,
        include_rar=True,
        include_admin=False,
    ) -> None:
        """Create a realistic SABnzbd directory structure"""
        path.mkdir(parents=True, exist_ok=True)

        if include_admin:
            # Create admin files
            (path / "__admin__").touch()
            (path / "SABnzbd_nzf").touch()

        if include_nzb:
            # Create NZB files
            (path / "download.nzb").touch()
            (path / "backup.nzb").touch()

        if include_par2:
            # Create PAR2 files
            for i in range(5):
                (path / f"archive.vol{i:03d}+01.par2").touch()
            (path / "archive.par2").touch()

        if include_rar:
            # Create RAR files
            for i in range(10):
                (path / f"archive.part{i:02d}.rar").touch()
            # Create split RAR files
            for i in range(5):
                (path / f"data.r{i:02d}").touch()

        # Create unpack directory
        unpack_dir = path / "_UNPACK_archive"
        unpack_dir.mkdir(exist_ok=True)
        (unpack_dir / "extracted_file.mkv").touch()

    def create_normal_directory(self, path: Path, file_count=10) -> None:
        """Create a normal directory with typical files"""
        path.mkdir(parents=True, exist_ok=True)

        # Create various file types
        extensions = [".txt", ".jpg", ".mp4", ".pdf", ".doc"]
        for i in range(file_count):
            ext = extensions[i % len(extensions)]
            (path / f"file_{i}{ext}").touch()

    def create_bittorrent_directory(self, path: Path) -> None:
        """Create a BitTorrent directory structure"""
        path.mkdir(parents=True, exist_ok=True)

        # Create torrent files
        (path / "download.torrent").touch()
        (path / "resume.dat").touch()
        (path / "fastresume.fastresume").touch()

        # Create typical BitTorrent files
        (path / "movie.mkv").touch()
        (path / "subtitles.srt").touch()

    def create_test_directories(self, count: int, sabnzbd_ratio=0.3) -> List[Path]:
        """
        Create a mix of directories for testing

        Args:
            count: Total number of directories to create
            sabnzbd_ratio: Proportion of directories that should be SABnzbd (0.0-1.0)

        Returns:
            List of created directory paths
        """
        directories = []
        sabnzbd_count = int(count * sabnzbd_ratio)
        bittorrent_count = int(count * 0.2)  # 20% BitTorrent
        normal_count = count - sabnzbd_count - bittorrent_count

        # Create SABnzbd directories
        for i in range(sabnzbd_count):
            dir_path = self.temp_dir / f"sabnzbd_dir_{i}"
            self.create_sabnzbd_directory(
                dir_path,
                include_admin=(i % 5 == 0),  # 20% with admin files
                include_nzb=(i % 3 != 0),  # 67% with NZB files
                include_par2=(i % 2 == 0),  # 50% with PAR2 files
                include_rar=(i % 3 == 0),  # 33% with RAR files
            )
            directories.append(dir_path)

        # Create BitTorrent directories
        for i in range(bittorrent_count):
            dir_path = self.temp_dir / f"bittorrent_dir_{i}"
            self.create_bittorrent_directory(dir_path)
            directories.append(dir_path)

        # Create normal directories
        for i in range(normal_count):
            dir_path = self.temp_dir / f"normal_dir_{i}"
            self.create_normal_directory(dir_path, file_count=10 + i % 20)
            directories.append(dir_path)

        return directories

    def measure_analysis_performance(
        self, directories: List[Path], runs=5
    ) -> Dict[str, Any]:
        """
        Measure performance of directory analysis

        Args:
            directories: List of directories to analyze
            runs: Number of test runs for averaging

        Returns:
            Dictionary with performance metrics
        """
        times = []
        results = []

        for _run in range(runs):
            start_time = time.perf_counter()

            run_results = []
            for directory in directories:
                is_sabnzbd, score, indicators = self.detector.analyze_directory(
                    directory
                )
                run_results.append((is_sabnzbd, score, len(indicators)))

            end_time = time.perf_counter()
            elapsed = end_time - start_time
            times.append(elapsed)
            results.append(run_results)

        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0

        # Verify consistent results across runs
        consistent_results = all(results[0] == result for result in results[1:])

        return {
            "directory_count": len(directories),
            "run_count": runs,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "time_per_directory": avg_time / len(directories),
            "directories_per_second": len(directories) / avg_time,
            "consistent_results": consistent_results,
            "total_results": len(results[0]),
        }

    def test_baseline_performance_small(self):
        """Test performance with 100 directories (small dataset)"""
        print("\n=== Baseline Performance Test: Small Dataset (100 directories) ===")
        directories = self.create_test_directories(100)

        metrics = self.measure_analysis_performance(directories)

        print(f"Directory count: {metrics['directory_count']}")
        print(f"Average time: {metrics['avg_time']:.4f}s")
        print(f"Time per directory: {metrics['time_per_directory']:.6f}s")
        print(f"Directories per second: {metrics['directories_per_second']:.1f}")
        print(f"Consistent results: {metrics['consistent_results']}")

        # Store baseline for comparison (would be saved to file in real implementation)
        self.baseline_small = metrics

        # Basic performance assertions
        self.assertTrue(
            metrics["consistent_results"], "Results should be consistent across runs"
        )
        self.assertLess(
            metrics["time_per_directory"], 0.1, "Should analyze each directory in <0.1s"
        )

    def test_baseline_performance_medium(self):
        """Test performance with 1000 directories (medium dataset)"""
        print("\n=== Baseline Performance Test: Medium Dataset (1000 directories) ===")
        directories = self.create_test_directories(1000)

        metrics = self.measure_analysis_performance(directories)

        print(f"Directory count: {metrics['directory_count']}")
        print(f"Average time: {metrics['avg_time']:.4f}s")
        print(f"Time per directory: {metrics['time_per_directory']:.6f}s")
        print(f"Directories per second: {metrics['directories_per_second']:.1f}")
        print(f"Consistent results: {metrics['consistent_results']}")

        # Store baseline for comparison
        self.baseline_medium = metrics

        # Performance assertions for medium dataset
        self.assertTrue(
            metrics["consistent_results"], "Results should be consistent across runs"
        )
        self.assertLess(
            metrics["time_per_directory"],
            0.05,
            "Should analyze each directory in <0.05s",
        )

    def test_baseline_performance_large(self):
        """Test performance with 2000 directories (large dataset)"""
        print("\n=== Baseline Performance Test: Large Dataset (2000 directories) ===")
        directories = self.create_test_directories(2000)

        metrics = self.measure_analysis_performance(
            directories, runs=3
        )  # Fewer runs for large dataset

        print(f"Directory count: {metrics['directory_count']}")
        print(f"Average time: {metrics['avg_time']:.4f}s")
        print(f"Time per directory: {metrics['time_per_directory']:.6f}s")
        print(f"Directories per second: {metrics['directories_per_second']:.1f}")
        print(f"Consistent results: {metrics['consistent_results']}")

        # Store baseline for comparison
        self.baseline_large = metrics

        # Performance assertions for large dataset
        self.assertTrue(
            metrics["consistent_results"], "Results should be consistent across runs"
        )
        self.assertLess(
            metrics["avg_time"], 300, "Should complete large dataset in <5 minutes"
        )

    def test_complexity_analysis(self):
        """Analyze time complexity by comparing different dataset sizes"""
        print("\n=== Time Complexity Analysis ===")

        sizes = [100, 500, 1000]
        results = {}

        for size in sizes:
            print(f"\nTesting {size} directories...")
            directories = self.create_test_directories(size)
            metrics = self.measure_analysis_performance(directories, runs=3)
            results[size] = metrics
            print(
                f"  {size} dirs: {metrics['avg_time']:.4f}s ({metrics['time_per_directory']:.6f}s per dir)"
            )

        # Calculate complexity ratios
        print("\nComplexity Analysis:")
        for i, size in enumerate(sizes[1:], 1):
            prev_size = sizes[i - 1]
            time_ratio = results[size]["avg_time"] / results[prev_size]["avg_time"]
            size_ratio = size / prev_size
            complexity_factor = time_ratio / size_ratio

            print(f"  {prev_size} → {size} directories:")
            print(f"    Size ratio: {size_ratio:.1f}x")
            print(f"    Time ratio: {time_ratio:.2f}x")
            print(f"    Complexity factor: {complexity_factor:.2f}")

            # If complexity factor > 1.5, likely indicates O(n²) or worse
            if complexity_factor > 1.5:
                print(
                    f"    ⚠️  Possible non-linear complexity (factor {complexity_factor:.2f})"
                )
            else:
                print(f"    ✅ Linear complexity (factor {complexity_factor:.2f})")

    def test_memory_usage_baseline(self):
        """Measure baseline memory usage during analysis"""
        import tracemalloc

        print("\n=== Memory Usage Baseline ===")

        # Create test directories
        directories = self.create_test_directories(1000)

        # Start memory tracking
        tracemalloc.start()

        # Run analysis
        for directory in directories:
            self.detector.analyze_directory(directory)

        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print("Memory usage for 1000 directories:")
        print(f"  Current: {current / 1024 / 1024:.2f} MB")
        print(f"  Peak: {peak / 1024 / 1024:.2f} MB")
        print(f"  Memory per directory: {peak / len(directories):.0f} bytes")

        # Store for comparison
        self.baseline_memory = {
            "directory_count": len(directories),
            "current_mb": current / 1024 / 1024,
            "peak_mb": peak / 1024 / 1024,
            "bytes_per_directory": peak / len(directories),
        }

        # Memory usage assertions
        self.assertLess(
            peak / 1024 / 1024, 100, "Peak memory should be <100MB for 1000 directories"
        )
        self.assertLess(
            peak / len(directories), 10000, "Should use <10KB per directory"
        )


if __name__ == "__main__":
    # Set up test environment
    print("SABnzbd Directory Analysis - Performance Baseline Tests")
    print("=" * 60)

    # Run specific tests in order
    suite = unittest.TestSuite()
    suite.addTest(SABnzbdPerformanceTest("test_baseline_performance_small"))
    suite.addTest(SABnzbdPerformanceTest("test_baseline_performance_medium"))
    suite.addTest(SABnzbdPerformanceTest("test_baseline_performance_large"))
    suite.addTest(SABnzbdPerformanceTest("test_complexity_analysis"))
    suite.addTest(SABnzbdPerformanceTest("test_memory_usage_baseline"))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("Performance Baseline Established")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, trace in result.failures:
            print(f"  {test}: {trace.split(chr(10))[-2]}")

    if result.errors:
        print("\nErrors:")
        for test, trace in result.errors:
            print(f"  {test}: {trace.split(chr(10))[-2]}")
