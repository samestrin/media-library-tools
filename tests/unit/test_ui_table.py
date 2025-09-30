#!/usr/bin/env python3
"""
Test script for enhanced display_results_table() function
Tests column configuration, sorting, alignment, and formatting
"""

import sys
import importlib.util
from pathlib import Path


def load_module_from_path(module_path: str, module_name: str):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_table_rendering():
    """Test enhanced table rendering functionality."""
    print("\n" + "=" * 80)
    print("TESTING: Enhanced display_results_table() Function")
    print("=" * 80)

    # Load ui module
    ui_path = Path(__file__).parent.parent.parent.parent.parent / 'lib' / 'ui.py'
    ui = load_module_from_path(str(ui_path), 'ui')

    # Sample data
    file_data = [
        ['movie1.mkv', 1234567890, 'processed', 95],
        ['movie2.mp4', 987654321, 'skipped', 0],
        ['show.s01e01.mkv', 2345678901, 'processed', 100],
        ['show.s01e02.mkv', 1456789012, 'processed', 100],
        ['documentary.avi', 567890123, 'failed', 45]
    ]

    # Test 1: Basic table (backward compatibility)
    print("\nTest 1: Basic Table (Backward Compatibility)")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress'],
        title='File Processing Results'
    )

    # Test 2: Column alignment
    print("\nTest 2: Column Alignment (left, right, center, center)")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress'],
        title='Aligned Columns',
        column_config=[
            ui.ColumnConfig(align='left'),
            ui.ColumnConfig(align='right'),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='center')
        ]
    )

    # Test 3: Column formatting
    print("\nTest 3: Column Formatting (Size as human-readable)")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress %'],
        title='Formatted Table',
        column_config=[
            ui.ColumnConfig(align='left'),
            ui.ColumnConfig(align='right', formatter=ui.format_size),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='right', formatter=lambda x: f"{x}%")
        ]
    )

    # Test 4: Sorting
    print("\nTest 4: Sorting by Size (descending)")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress %'],
        title='Sorted by Size',
        column_config=[
            ui.ColumnConfig(align='left'),
            ui.ColumnConfig(align='right', formatter=ui.format_size),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='right', formatter=lambda x: f"{x}%")
        ],
        sort_by=1,
        reverse=True
    )

    # Test 5: Unicode border style
    print("\nTest 5: Unicode Border Style")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress %'],
        title='Unicode Table',
        column_config=[
            ui.ColumnConfig(align='left'),
            ui.ColumnConfig(align='right', formatter=ui.format_size),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='right', formatter=lambda x: f"{x}%")
        ],
        border_style='unicode'
    )

    # Test 6: Minimal border style
    print("\nTest 6: Minimal Border Style")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress'],
        title='Minimal Table',
        column_config=[
            ui.ColumnConfig(align='left'),
            ui.ColumnConfig(align='right', formatter=ui.format_size),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='right')
        ],
        border_style='minimal'
    )

    # Test 7: Show totals
    print("\nTest 7: Show Totals Row")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress %'],
        title='Table with Totals',
        column_config=[
            ui.ColumnConfig(align='left'),
            ui.ColumnConfig(align='right', formatter=ui.format_size),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='right', formatter=lambda x: f"{x}%")
        ],
        show_totals=True,
        border_style='unicode'
    )

    # Test 8: Column width limiting
    print("\nTest 8: Column Width Limiting")
    print("-" * 80)
    ui.display_results_table(
        data=file_data,
        headers=['Filename', 'Size', 'Status', 'Progress'],
        title='Limited Column Width',
        column_config=[
            ui.ColumnConfig(align='left', max_width=15),
            ui.ColumnConfig(align='right', formatter=ui.format_size),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='right')
        ]
    )

    # Test 9: Empty data
    print("\nTest 9: Empty Data Handling")
    print("-" * 80)
    ui.display_results_table(
        data=[],
        headers=['Column1', 'Column2'],
        title='Empty Table'
    )

    # Test 10: Complex data with all features
    print("\nTest 10: All Features Combined")
    print("-" * 80)
    season_data = [
        ['Season 01', 15, 18234567890, 'complete'],
        ['Season 02', 18, 21345678901, 'complete'],
        ['Season 03', 12, 14567890123, 'in-progress'],
        ['Season 04', 10, 11234567890, 'pending']
    ]
    
    ui.display_results_table(
        data=season_data,
        headers=['Season', 'Episodes', 'Total Size', 'Status'],
        title='Season Organization Summary',
        column_config=[
            ui.ColumnConfig(align='left'),
            ui.ColumnConfig(align='center'),
            ui.ColumnConfig(align='right', formatter=ui.format_size),
            ui.ColumnConfig(align='center')
        ],
        sort_by=2,
        reverse=True,
        show_totals=True,
        border_style='unicode'
    )

    print("\n" + "=" * 80)
    print("TABLE RENDERING TESTS COMPLETE")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    test_table_rendering()
