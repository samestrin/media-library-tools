#!/usr/bin/env python3
"""
Test script for PhaseProgressTracker component
Tests multi-phase operation tracking
"""

import sys
import time
import importlib.util
from pathlib import Path


def load_module_from_path(module_path: str, module_name: str):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase_tracker():
    """Test PhaseProgressTracker functionality."""
    print("\n" + "=" * 60)
    print("TESTING: PhaseProgressTracker Component")
    print("=" * 60)

    # Load ui module
    ui_path = Path(__file__).parent.parent.parent.parent.parent / 'lib' / 'ui.py'
    ui = load_module_from_path(str(ui_path), 'ui')

    # Test 1: Three-phase workflow (plex_make_seasons simulation)
    print("\nTest 1: Three-Phase Workflow (Consolidation → Organization → Archive)")
    print("-" * 60)
    
    tracker = ui.PhaseProgressTracker([
        "Phase 1: Consolidation",
        "Phase 2: Organization",
        "Phase 3: Archive"
    ])

    # Phase 1: Consolidation
    tracker.start_phase(0, total_items=150)
    for i in range(150):
        time.sleep(0.01)
        tracker.update_phase(0, increment=1)
    tracker.complete_phase(0)

    # Phase 2: Organization
    tracker.start_phase(1, total_items=150)
    for i in range(150):
        time.sleep(0.01)
        tracker.update_phase(1, increment=1)
    tracker.complete_phase(1)

    # Phase 3: Archive
    tracker.start_phase(2, total_items=5)
    for i in range(5):
        time.sleep(0.05)
        tracker.update_phase(2, increment=1)
    tracker.complete_phase(2)

    # Display summary
    tracker.display_summary()

    # Test 2: Phase failure handling
    print("\nTest 2: Phase Failure Handling")
    print("-" * 60)
    
    tracker2 = ui.PhaseProgressTracker([
        "Phase 1: Validation",
        "Phase 2: Processing",
        "Phase 3: Cleanup"
    ])

    # Phase 1: Success
    tracker2.start_phase(0, total_items=50)
    for i in range(50):
        time.sleep(0.005)
        tracker2.update_phase(0, increment=1)
    tracker2.complete_phase(0)

    # Phase 2: Failure
    tracker2.start_phase(1, total_items=100)
    for i in range(30):  # Only process 30 out of 100
        time.sleep(0.005)
        tracker2.update_phase(1, increment=1)
    tracker2.fail_phase(1, "Permission denied on file xyz.mkv")

    # Phase 3: Not started due to failure
    tracker2.display_summary()

    # Test 3: Overall progress calculation
    print("\nTest 3: Overall Progress Calculation")
    print("-" * 60)
    
    tracker3 = ui.PhaseProgressTracker([
        "Phase 1",
        "Phase 2",
        "Phase 3",
        "Phase 4"
    ])

    tracker3.start_phase(0, total_items=10)
    for i in range(10):
        tracker3.update_phase(0, increment=1)
    tracker3.complete_phase(0)
    print(f"  After Phase 1: {tracker3.get_overall_progress():.1f}% complete")

    tracker3.start_phase(1, total_items=10)
    for i in range(10):
        tracker3.update_phase(1, increment=1)
    tracker3.complete_phase(1)
    print(f"  After Phase 2: {tracker3.get_overall_progress():.1f}% complete")

    tracker3.start_phase(2, total_items=10)
    for i in range(10):
        tracker3.update_phase(2, increment=1)
    tracker3.complete_phase(2)
    print(f"  After Phase 3: {tracker3.get_overall_progress():.1f}% complete")

    tracker3.start_phase(3, total_items=10)
    for i in range(10):
        tracker3.update_phase(3, increment=1)
    tracker3.complete_phase(3)
    print(f"  After Phase 4: {tracker3.get_overall_progress():.1f}% complete")

    tracker3.display_summary()

    print("\n" + "=" * 60)
    print("PHASE TRACKER TESTS COMPLETE")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    test_phase_tracker()
