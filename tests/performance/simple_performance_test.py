#!/usr/bin/env python3
"""
Simple performance test to establish baseline for SABnzbd directory analysis
"""

import subprocess
import tempfile
import time
from pathlib import Path


def create_test_directory_structure(base_path, count):
    """Create test directories with various structures"""
    sabnzbd_dirs = []

    for i in range(count):
        # Create SABnzbd-like directory
        dir_path = Path(base_path) / f"download_dir_{i}"
        dir_path.mkdir(parents=True, exist_ok=True)

        # Add typical SABnzbd files
        if i % 3 == 0:  # Some with NZB files
            (dir_path / "download.nzb").touch()
        if i % 2 == 0:  # Some with PAR2 files
            (dir_path / "archive.par2").touch()
            (dir_path / "archive.vol001+02.par2").touch()
        if i % 4 == 0:  # Some with admin files
            (dir_path / "__admin__").touch()
        if i % 5 == 0:  # Some with unpack dirs
            unpack_dir = dir_path / "_UNPACK_archive"
            unpack_dir.mkdir(exist_ok=True)

        # Add some RAR files
        for j in range(3):
            (dir_path / f"archive.part{j:02d}.rar").touch()

        sabnzbd_dirs.append(dir_path)

    return sabnzbd_dirs


def run_sabnzbd_script(test_directory):
    """Run the SABnzbd cleanup script on test directory"""
    script_path = Path(__file__).parent.parent.parent / "SABnzbd" / "sabnzbd_cleanup"

    start_time = time.perf_counter()
    result = subprocess.run(
        [str(script_path), str(test_directory), "--verbose"],
        capture_output=True,
        text=True,
    )
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    return elapsed_time, result.returncode, result.stdout, result.stderr


def main():
    print("SABnzbd Performance Baseline Test")
    print("=" * 50)

    # Test with different directory counts
    test_sizes = [50, 100, 200]

    for size in test_sizes:
        print(f"\nTesting with {size} directories...")

        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            print(f"  Creating {size} test directories...")
            create_test_directory_structure(temp_dir, size)

            # Run the script and measure time
            print("  Running SABnzbd cleanup script...")
            elapsed, returncode, stdout, stderr = run_sabnzbd_script(temp_dir)

            # Report results
            print("  Results:")
            print(f"    Elapsed time: {elapsed:.4f} seconds")
            print(f"    Time per directory: {elapsed/size:.6f} seconds")
            print(f"    Directories per second: {size/elapsed:.1f}")
            print(f"    Return code: {returncode}")

            # Extract found directories from output
            lines = stderr.split("\n")
            sabnzbd_count = 0
            for line in lines:
                if "SABnzbd directory detected" in line:
                    sabnzbd_count += 1
            print(f"    SABnzbd directories found: {sabnzbd_count}")


if __name__ == "__main__":
    main()
