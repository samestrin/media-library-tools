#!/usr/bin/env python3
"""
Test script for display_directory_tree() function
Tests directory visualization with various options
"""

import sys
import os
import tempfile
import importlib.util
from pathlib import Path


def load_module_from_path(module_path: str, module_name: str):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_test_structure(base_path: Path):
    """Create a test directory structure."""
    # Create TV show structure
    show_dir = base_path / "TV Shows" / "Example Show"
    show_dir.mkdir(parents=True, exist_ok=True)

    # Season 01
    season1 = show_dir / "Season 01"
    season1.mkdir(exist_ok=True)
    for i in range(1, 6):
        (season1 / f"Episode.S01E{i:02d}.mkv").write_text("video content")

    # Season 02
    season2 = show_dir / "Season 02"
    season2.mkdir(exist_ok=True)
    for i in range(1, 8):
        (season2 / f"Episode.S02E{i:02d}.mkv").write_text("video content")

    # Samples directory
    samples = show_dir / "samples"
    samples.mkdir(exist_ok=True)
    (samples / "sample1.mkv").write_text("sample")
    (samples / "sample2.avi").write_text("sample")

    # Extra files
    (show_dir / "show.nfo").write_text("metadata")
    (show_dir / "poster.jpg").write_text("image")

    return show_dir


def test_directory_tree():
    """Test display_directory_tree functionality."""
    print("\n" + "=" * 60)
    print("TESTING: display_directory_tree() Function")
    print("=" * 60)

    # Load ui module
    ui_path = Path(__file__).parent.parent.parent.parent.parent / 'lib' / 'ui.py'
    ui = load_module_from_path(str(ui_path), 'ui')

    # Create test structure
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = create_test_structure(Path(tmpdir))

        # Test 1: Basic tree display with Unicode
        print("\nTest 1: Basic Tree Display (Unicode)")
        print("-" * 60)
        ui.display_directory_tree(str(test_dir), max_depth=2, use_unicode=True)

        # Test 2: Tree display with ASCII
        print("\nTest 2: Tree Display (ASCII)")
        print("-" * 60)
        ui.display_directory_tree(str(test_dir), max_depth=2, use_unicode=False)

        # Test 3: Deep traversal
        print("\nTest 3: Deep Traversal (max_depth=5)")
        print("-" * 60)
        ui.display_directory_tree(str(test_dir), max_depth=5, use_unicode=True)

        # Test 4: Without sizes
        print("\nTest 4: Without Size Information")
        print("-" * 60)
        ui.display_directory_tree(str(test_dir), max_depth=2, show_sizes=False, use_unicode=True)

        # Test 5: With highlighting
        print("\nTest 5: With Pattern Highlighting (Season *)")
        print("-" * 60)
        ui.display_directory_tree(str(test_dir), max_depth=2, 
                                  highlight_patterns=["Season", "samples"],
                                  use_unicode=True)

        # Test 6: Shallow depth
        print("\nTest 6: Shallow Depth (max_depth=1)")
        print("-" * 60)
        ui.display_directory_tree(str(test_dir), max_depth=1, use_unicode=True)

    # Test 7: Non-existent path
    print("\nTest 7: Non-Existent Path Handling")
    print("-" * 60)
    ui.display_directory_tree("/non/existent/path", max_depth=2)

    # Test 8: Real directory (if available)
    print("\nTest 8: Real Directory (current project root)")
    print("-" * 60)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    if project_root.exists():
        ui.display_directory_tree(str(project_root / "lib"), max_depth=1, use_unicode=True)

    print("\n" + "=" * 60)
    print("DIRECTORY TREE TESTS COMPLETE")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    test_directory_tree()
