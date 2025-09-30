#!/usr/bin/env python3
"""
Test script for ProgressBar component
Tests various progress bar scenarios including TTY and non-TTY modes
"""

import sys
import time
import tempfile
import importlib.util
from pathlib import Path


def load_module_from_path(module_path: str, module_name: str):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_progress_bar():
    """Test ProgressBar functionality."""
    print("\n" + "=" * 60)
    print("TESTING: ProgressBar Component")
    print("=" * 60)

    # Load ui module
    ui_path = Path(__file__).parent.parent.parent.parent.parent / 'lib' / 'ui.py'
    ui = load_module_from_path(str(ui_path), 'ui')

    # Test 1: Basic progress bar with context manager
    print("\nTest 1: Basic Progress Bar")
    print("-" * 40)
    with ui.ProgressBar(total=100, desc="Processing items") as pb:
        for i in range(100):
            time.sleep(0.01)  # Simulate work
            pb.update(1)

    # Test 2: Progress bar with custom unit
    print("\nTest 2: Progress Bar with Custom Unit (files)")
    print("-" * 40)
    with ui.ProgressBar(total=50, desc="Scanning files", unit="files") as pb:
        for i in range(50):
            time.sleep(0.02)
            pb.update(1)

    # Test 3: Fast progress (rate display test)
    print("\nTest 3: Fast Progress Rate Display")
    print("-" * 40)
    with ui.ProgressBar(total=1000, desc="Fast processing", unit="items") as pb:
        for i in range(1000):
            pb.update(1)

    # Test 4: Zero total handling
    print("\nTest 4: Zero Total Handling")
    print("-" * 40)
    with ui.ProgressBar(total=0, desc="Empty operation") as pb:
        pass
    print("  Zero total handled gracefully")

    # Test 5: Manual updates without context manager
    print("\nTest 5: Manual Updates")
    print("-" * 40)
    pb = ui.ProgressBar(total=25, desc="Manual progress")
    for i in range(25):
        time.sleep(0.02)
        pb.update(1)
    pb.__exit__()

    # Test 6: Large numbers
    print("\nTest 6: Large Numbers (10000 items)")
    print("-" * 40)
    with ui.ProgressBar(total=10000, desc="Large dataset", unit="records") as pb:
        for i in range(0, 10000, 100):
            pb.update(100)
            time.sleep(0.001)

    print("\n" + "=" * 60)
    print("PROGRESS BAR TESTS COMPLETE")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    test_progress_bar()
