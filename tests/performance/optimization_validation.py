#!/usr/bin/env python3
"""
Comprehensive performance validation for SABnzbd analysis optimization
Compares optimized version performance with different dataset sizes
"""

import os
import sys
import time
import tempfile
import shutil
import subprocess
from pathlib import Path

def create_comprehensive_test_structure(base_path, count):
    """Create more comprehensive test directories for performance validation"""
    sabnzbd_dirs = []
    
    for i in range(count):
        # Create more varied SABnzbd-like structures
        dir_path = Path(base_path) / f"test_download_{i}"
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Vary the complexity based on index
        complexity_factor = (i % 10) + 1
        
        # Create NZB files (60% chance)
        if i % 10 < 6:
            for j in range(min(3, complexity_factor)):
                (dir_path / f"download_{j}.nzb").touch()
        
        # Create PAR2 files with varying counts
        if i % 8 < 5:  # 62.5% chance
            par2_count = min(complexity_factor * 2, 15)
            for j in range(par2_count):
                (dir_path / f"archive.vol{j:03d}+01.par2").touch()
            (dir_path / "archive.par2").touch()
            
            # Some subdirectory PAR2 files
            if i % 5 == 0:
                subdir = dir_path / "subdir"
                subdir.mkdir(exist_ok=True)
                for j in range(3):
                    (subdir / f"sub_archive.vol{j:03d}+01.par2").touch()
        
        # Create RAR files with realistic patterns
        if i % 6 < 4:  # 66% chance
            rar_count = min(complexity_factor * 3, 25)
            for j in range(rar_count):
                if j == 0:
                    (dir_path / f"archive.rar").touch()
                else:
                    (dir_path / f"archive.r{j-1:02d}").touch()
        
        # Admin files (20% chance)
        if i % 5 == 0:
            (dir_path / "__admin__").touch()
            if i % 10 == 0:
                (dir_path / "SABnzbd_nzf").touch()
        
        # Unpack directories (30% chance)
        if i % 10 < 3:
            unpack_dir = dir_path / f"_UNPACK_{dir_path.name}"
            unpack_dir.mkdir(exist_ok=True)
            # Add some content to unpack dir
            for j in range(min(5, complexity_factor)):
                (unpack_dir / f"extracted_{j}.mkv").touch()
        
        # Add some regular files for realism
        for j in range(min(10, complexity_factor * 2)):
            extensions = ['.txt', '.log', '.nfo', '.sfv', '.jpg']
            ext = extensions[j % len(extensions)]
            (dir_path / f"file_{j}{ext}").touch()
            
        sabnzbd_dirs.append(dir_path)
    
    # Add some non-SABnzbd directories for realistic testing
    for i in range(count // 4):  # 25% non-SABnzbd directories
        dir_path = Path(base_path) / f"normal_dir_{i}"
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Just regular files
        for j in range(15):
            extensions = ['.txt', '.jpg', '.mp4', '.pdf', '.doc']
            ext = extensions[j % len(extensions)]
            (dir_path / f"normal_file_{j}{ext}").touch()
    
    # Add some BitTorrent directories
    for i in range(count // 8):  # 12.5% BitTorrent directories
        dir_path = Path(base_path) / f"torrent_dir_{i}"
        dir_path.mkdir(parents=True, exist_ok=True)
        
        (dir_path / "download.torrent").touch()
        (dir_path / "resume.dat").touch()
        (dir_path / "movie.mkv").touch()
        (dir_path / "subtitles.srt").touch()
    
    return sabnzbd_dirs

def run_performance_test(test_directory, test_name):
    """Run performance test and return detailed metrics"""
    script_path = Path(__file__).parent.parent.parent / "SABnzbd" / "sabnzbd_cleanup"
    
    # Run multiple times for consistent measurement
    times = []
    results = []
    
    for run in range(3):
        start_time = time.perf_counter()
        result = subprocess.run([
            str(script_path), 
            str(test_directory),
            "--verbose"
        ], capture_output=True, text=True)
        end_time = time.perf_counter()
        
        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        results.append((result.returncode, result.stdout, result.stderr))
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    # Count directories processed
    dir_count = len(list(Path(test_directory).iterdir()))
    
    # Extract found SABnzbd directories from stderr
    lines = results[0][2].split('\n')
    sabnzbd_found = 0
    for line in lines:
        if "SABnzbd directory detected" in line:
            sabnzbd_found += 1
    
    return {
        'test_name': test_name,
        'directory_count': dir_count,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'time_per_directory': avg_time / dir_count,
        'directories_per_second': dir_count / avg_time,
        'sabnzbd_found': sabnzbd_found,
        'return_code': results[0][0]
    }

def main():
    print("SABnzbd Analysis Optimization - Performance Validation")
    print("=" * 60)
    
    test_sizes = [100, 500, 1000, 2000]
    results = []
    
    for size in test_sizes:
        print(f"\n🧪 Testing with {size} directories...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"   📁 Creating {size} test directories...")
            create_comprehensive_test_structure(temp_dir, size)
            
            print(f"   ⚡ Running performance analysis...")
            result = run_performance_test(temp_dir, f"{size}_directories")
            results.append(result)
            
            print(f"   📊 Results:")
            print(f"      ⏱️  Average time: {result['avg_time']:.4f} seconds")
            print(f"      📈 Time per directory: {result['time_per_directory']:.6f} seconds")
            print(f"      🚀 Directories per second: {result['directories_per_second']:.1f}")
            print(f"      🎯 SABnzbd directories found: {result['sabnzbd_found']}")
    
    # Analyze scaling characteristics
    print(f"\n📈 Performance Scaling Analysis:")
    print("=" * 60)
    
    for i in range(1, len(results)):
        prev = results[i-1]
        curr = results[i]
        
        size_ratio = curr['directory_count'] / prev['directory_count']
        time_ratio = curr['avg_time'] / prev['avg_time']
        efficiency_factor = time_ratio / size_ratio
        
        print(f"\n🔍 {prev['directory_count']} → {curr['directory_count']} directories:")
        print(f"   📏 Size ratio: {size_ratio:.1f}x")
        print(f"   ⏱️  Time ratio: {time_ratio:.2f}x")
        print(f"   🎯 Efficiency factor: {efficiency_factor:.2f}")
        
        if efficiency_factor < 1.2:
            print(f"   ✅ Excellent linear scaling (factor {efficiency_factor:.2f})")
        elif efficiency_factor < 1.5:
            print(f"   ✅ Good scaling (factor {efficiency_factor:.2f})")
        else:
            print(f"   ⚠️  Non-linear scaling detected (factor {efficiency_factor:.2f})")
    
    # Calculate overall performance metrics
    print(f"\n🏆 Overall Performance Metrics:")
    print("=" * 60)
    
    total_dirs = sum(r['directory_count'] for r in results)
    total_time = sum(r['avg_time'] for r in results)
    overall_rate = total_dirs / total_time
    
    print(f"📊 Total directories processed: {total_dirs}")
    print(f"⏱️  Total processing time: {total_time:.4f} seconds")
    print(f"🚀 Overall processing rate: {overall_rate:.1f} directories/second")
    
    # Performance targets
    print(f"\n🎯 Performance Target Validation:")
    print("=" * 60)
    
    # Target: Process directories at > 1000 dirs/second for large datasets
    large_dataset_rate = results[-1]['directories_per_second']
    if large_dataset_rate > 1000:
        print(f"✅ Large dataset performance: {large_dataset_rate:.1f} dirs/sec (Target: >1000)")
    else:
        print(f"❌ Large dataset performance: {large_dataset_rate:.1f} dirs/sec (Target: >1000)")
    
    # Target: < 1ms average per directory for medium datasets
    medium_dataset_time = results[1]['time_per_directory']
    if medium_dataset_time < 0.001:
        print(f"✅ Medium dataset efficiency: {medium_dataset_time:.6f}s per dir (Target: <0.001s)")
    else:
        print(f"❌ Medium dataset efficiency: {medium_dataset_time:.6f}s per dir (Target: <0.001s)")
    
    # Check for consistent detection
    detection_rates = [r['sabnzbd_found'] / r['directory_count'] for r in results]
    detection_consistency = max(detection_rates) - min(detection_rates)
    
    if detection_consistency < 0.1:
        print(f"✅ Consistent detection across dataset sizes (variance: {detection_consistency:.3f})")
    else:
        print(f"⚠️  Detection variance across sizes: {detection_consistency:.3f}")
    
    print(f"\n🎉 Optimization validation completed!")

if __name__ == "__main__":
    main()