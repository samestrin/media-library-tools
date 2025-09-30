# UI Library Documentation - lib/ui.py

**Version**: 2.0 (Sprint 10.0 enhancements)  
**Last Updated**: September 30, 2025  
**Status**: Complete

## Overview

The `lib/ui.py` module provides a comprehensive set of user interface components for Media Library Tools. All components follow the project's zero-dependency principle, using only Python standard library modules.

## Component Catalog

### 1. ProgressBar Class

**Purpose**: Real-time progress indication with ETA calculation and rate display.

**Features**:
- Configurable width and display style
- ETA calculation based on processing rate
- Dynamic updates without line spam (0.1s update interval)
- Rate display (items/sec, bytes/sec, etc.)
- TTY detection with non-interactive fallback
- Memory-efficient for large operations
- Context manager support

**Constructor**:
```python
ProgressBar(total: int, desc: str = "", width: int = 50,
           unit: str = "items", show_rate: bool = True)
```

**Parameters**:
- `total`: Total number of items to process
- `desc`: Description displayed before progress bar
- `width`: Width of progress bar in characters (default: 50)
- `unit`: Unit name for rate display (default: "items")
- `show_rate`: Whether to display processing rate (default: True)

**Usage Example**:
```python
from lib.ui import ProgressBar

# Using context manager (recommended)
with ProgressBar(total=1000, desc="Processing files", unit="files") as pb:
    for item in items:
        process_item(item)
        pb.update(1)

# Manual usage
pb = ProgressBar(total=500, desc="Scanning")
for i in range(500):
    pb.update(1)
pb.__exit__()  # Cleanup
```

**Output Example** (TTY mode):
```
Processing files: [████████████████████] 1000/1000 (100.0%) - 45.2 files/sec - Complete
```

**Output Example** (Non-TTY mode):
```
Processing files: Progress: 0/1000 (0.0%)
Processing files: Progress: 250/1000 (25.0%)
Processing files: Progress: 500/1000 (50.0%)
Processing files: Progress: 750/1000 (75.0%)
Processing files: Progress: 1000/1000 (100.0%)
```

**Methods**:
- `update(increment: int = 1)`: Update progress by specified increment
- `__enter__()` / `__exit__()`: Context manager support

---

### 2. PhaseProgressTracker Class

**Purpose**: Multi-phase operation tracking with individual progress bars and timing.

**Features**:
- Track multiple named phases (e.g., Consolidation, Organization, Archive)
- Per-phase progress bars
- Overall completion percentage
- Phase timing and duration display
- Phase status tracking (pending, in-progress, completed, failed)
- Phase failure handling with error messages
- Summary report generation

**Constructor**:
```python
PhaseProgressTracker(phase_names: List[str])
```

**Parameters**:
- `phase_names`: List of phase names in order

**Usage Example**:
```python
from lib.ui import PhaseProgressTracker

# Initialize tracker with phase names
tracker = PhaseProgressTracker([
    "Phase 1: Consolidation",
    "Phase 2: Organization",
    "Phase 3: Archive"
])

# Phase 1
tracker.start_phase(0, total_items=150)
for item in items:
    process_item(item)
    tracker.update_phase(0, increment=1)
tracker.complete_phase(0)

# Phase 2
tracker.start_phase(1, total_items=150)
for item in items:
    organize_item(item)
    tracker.update_phase(1, increment=1)
tracker.complete_phase(1)

# Phase 3 with failure handling
tracker.start_phase(2, total_items=5)
try:
    archive_samples()
    tracker.complete_phase(2)
except Exception as e:
    tracker.fail_phase(2, str(e))

# Display summary
tracker.display_summary()
```

**Output Example**:
```
Phase 1: Consolidation
  Progress: [████████████████████] 150/150 (100.0%) - 2.3 items/sec - Complete
  Complete - Duration: 1m 5s

Phase 2: Organization
  Progress: [████████████████████] 150/150 (100.0%) - 3.3 items/sec - Complete
  Complete - Duration: 45s

Phase 3: Archive
  Progress: [████████████████████] 5/5 (100.0%) - 0.25 items/sec - Complete
  Complete - Duration: 20s

============================================================
PHASE SUMMARY
============================================================
[x] Phase 1: Consolidation (150/150 items) - 1m 5s
[x] Phase 2: Organization (150/150 items) - 45s
[x] Phase 3: Archive (5/5 items) - 20s

Total Duration: 2m 10s
============================================================
```

**Methods**:
- `start_phase(phase_index: int, total_items: int = 0)`: Start a phase
- `update_phase(phase_index: int, increment: int = 1)`: Update phase progress
- `complete_phase(phase_index: int, status: str = 'completed')`: Mark phase complete
- `fail_phase(phase_index: int, error_message: str = "")`: Mark phase failed
- `display_summary()`: Display summary of all phases
- `get_overall_progress() -> float`: Get overall progress percentage (0-100)

---

### 3. display_directory_tree()

**Purpose**: Visual representation of directory structures with size information.

**Features**:
- Configurable depth limit
- File size display
- Path highlighting for specific patterns
- Unicode or ASCII symbols (auto-detected)
- Efficient traversal
- Permission error handling
- Statistics summary

**Function Signature**:
```python
def display_directory_tree(root_path: str, max_depth: int = 3,
                          show_sizes: bool = True,
                          highlight_patterns: Optional[List[str]] = None,
                          use_unicode: Optional[bool] = None) -> None
```

**Parameters**:
- `root_path`: Root directory to visualize
- `max_depth`: Maximum depth to traverse (default: 3)
- `show_sizes`: Show file/directory sizes (default: True)
- `highlight_patterns`: List of patterns to highlight (e.g., ["Season *"])
- `use_unicode`: Use Unicode symbols (default: auto-detect)

**Usage Example**:
```python
from lib.ui import display_directory_tree

# Basic usage
display_directory_tree("/media/TV Shows/Show Name", max_depth=3)

# With highlighting
display_directory_tree("/media/TV Shows/Show Name",
                       max_depth=3,
                       highlight_patterns=["Season", "samples"])

# ASCII mode (Windows compatibility)
display_directory_tree("/media/TV Shows/Show Name",
                       max_depth=2,
                       use_unicode=False)
```

**Output Example** (Unicode):
```
/media/TV Shows/Show Name/
├── Season 01/ (14.5G)
│   ├── Episode.S01E01.mkv (1.2G)
│   ├── Episode.S01E02.mkv (1.1G)
│   └── Episode.S01E03.mkv (1.3G)
├── Season 02/ (18.7G)
│   ├── Episode.S02E01.mkv (1.4G)
│   └── Episode.S02E02.mkv (1.2G)
└── samples/ (50M)
    └── sample.mkv (25M)

Total: 33.2G across 6 files in 3 directories
```

**Output Example** (ASCII):
```
/media/TV Shows/Show Name/
|-- Season 01/ (14.5G)
|   |-- Episode.S01E01.mkv (1.2G)
|   |-- Episode.S01E02.mkv (1.1G)
|   `-- Episode.S01E03.mkv (1.3G)
|-- Season 02/ (18.7G)
|   |-- Episode.S02E01.mkv (1.4G)
|   `-- Episode.S02E02.mkv (1.2G)
`-- samples/ (50M)
    `-- sample.mkv (25M)

Total: 33.2G across 6 files in 3 directories
```

---

### 4. Enhanced display_results_table()

**Purpose**: Advanced table rendering with column configuration, sorting, and formatting.

**Features**:
- Column alignment control (left, right, center)
- Automatic width calculation
- Row sorting by column
- Column-specific formatters
- Footer rows for totals
- Maximum width enforcement with truncation
- Border style options (ASCII, Unicode, minimal)
- Backward compatible with simple usage

**Function Signature**:
```python
def display_results_table(data: list, headers: list, title: str = None,
                         max_width: int = 80,
                         column_config: Optional[List[ColumnConfig]] = None,
                         sort_by: Optional[int] = None,
                         reverse: bool = False,
                         show_totals: bool = False,
                         border_style: str = 'ascii') -> None
```

**Parameters**:
- `data`: List of lists/tuples containing row data
- `headers`: List of column headers
- `title`: Optional title above table
- `max_width`: Maximum table width (default: 80)
- `column_config`: List of ColumnConfig objects
- `sort_by`: Column index to sort by
- `reverse`: Reverse sort order (default: False)
- `show_totals`: Show totals row for numeric columns (default: False)
- `border_style`: 'ascii', 'unicode', or 'minimal'

**ColumnConfig Class**:
```python
@dataclass
class ColumnConfig:
    align: str = 'left'  # 'left', 'right', 'center'
    formatter: Optional[Callable[[Any], str]] = None
    max_width: Optional[int] = None
```

**Usage Examples**:

**Basic Usage** (backward compatible):
```python
from lib.ui import display_results_table

display_results_table(
    data=[
        ['file1.mkv', '1.2G', 'processed'],
        ['file2.mp4', '850M', 'skipped']
    ],
    headers=['Filename', 'Size', 'Status'],
    title='Processing Results'
)
```

**Advanced Usage** with formatting:
```python
from lib.ui import display_results_table, ColumnConfig, format_size

display_results_table(
    data=[
        ['file1.mkv', 1234567890, 'processed', 95],
        ['file2.mp4', 987654321, 'skipped', 0],
        ['file3.avi', 2345678901, 'processed', 100]
    ],
    headers=['Filename', 'Size', 'Status', 'Progress %'],
    title='File Processing Results',
    column_config=[
        ColumnConfig(align='left'),
        ColumnConfig(align='right', formatter=format_size),
        ColumnConfig(align='center'),
        ColumnConfig(align='right', formatter=lambda x: f"{x}%")
    ],
    sort_by=1,  # Sort by Size column
    reverse=True,  # Largest first
    show_totals=True,
    border_style='unicode'
)
```

**Output Example** (Unicode with totals):
```
File Processing Results:
  Filename        │       Size │  Status   │ Progress %
  ────────────────┼────────────┼───────────┼───────────
  file3.avi       │      2.2G  │ processed │      100%
  file1.mkv       │      1.1G  │ processed │       95%
  file2.mp4       │    941.9M  │  skipped  │        0%
  ────────────────┼────────────┼───────────┼───────────
  TOTAL           │      4.3G  │           │      195%
```

---

### 5. Existing Components (Pre-Sprint 10.0)

These components were already available in lib/ui.py:

#### display_banner()
Display standardized banner for Media Library Tools scripts.

#### format_size()
Convert bytes to human-readable format (B, K, M, G, T).

#### confirm_action()
Ask for user confirmation with skip option.

#### format_status_message()
Format messages with optional emoji or text prefix.

#### display_item_list()
Display list of items with optional numbering.

#### display_summary_list()
Display categorized counts and summaries.

#### display_progress_item()
Display current progress for individual items (legacy, use ProgressBar instead).

#### display_stats_table()
Display statistics with value formatting.

---

## Integration Patterns

### Pattern 1: Simple Progress Tracking

For single-phase operations with known item counts:

```python
from lib.ui import ProgressBar

items = get_items_to_process()

with ProgressBar(total=len(items), desc="Processing items") as pb:
    for item in items:
        process_item(item)
        pb.update(1)
```

### Pattern 2: Multi-Phase Workflow

For complex operations with multiple distinct phases:

```python
from lib.ui import PhaseProgressTracker

tracker = PhaseProgressTracker([
    "Phase 1: Discovery",
    "Phase 2: Processing",
    "Phase 3: Cleanup"
])

# Phase 1
tracker.start_phase(0, total_items=file_count)
files = discover_files()
tracker.complete_phase(0)

# Phase 2
tracker.start_phase(1, total_items=len(files))
for file in files:
    process_file(file)
    tracker.update_phase(1, increment=1)
tracker.complete_phase(1)

# Phase 3
tracker.start_phase(2)
cleanup()
tracker.complete_phase(2)

tracker.display_summary()
```

### Pattern 3: Combined Progress and Tables

For operations that need both progress tracking and result display:

```python
from lib.ui import ProgressBar, display_results_table, ColumnConfig, format_size

# Process with progress bar
results = []
with ProgressBar(total=len(files), desc="Processing files") as pb:
    for file in files:
        result = process_file(file)
        results.append([file.name, file.size, result.status])
        pb.update(1)

# Display results in table
display_results_table(
    data=results,
    headers=['Filename', 'Size', 'Status'],
    title='Processing Results',
    column_config=[
        ColumnConfig(align='left'),
        ColumnConfig(align='right', formatter=format_size),
        ColumnConfig(align='center')
    ],
    border_style='unicode'
)
```

---

## TTY vs Non-TTY Behavior

All UI components automatically detect TTY environments and adapt their output:

### TTY (Interactive Terminal)
- Progress bars use ANSI escape codes for dynamic updates
- Unicode box-drawing characters for tables (if supported)
- Real-time progress updates every 0.1 seconds
- Colorful and visually appealing output

### Non-TTY (Cron, CI, Piped Output)
- Progress bars show milestone updates (0%, 25%, 50%, 75%, 100%)
- ASCII characters only
- No ANSI escape codes
- Line-based output suitable for log files

**Detection**:
```python
is_tty = sys.stdout.isatty() and not is_non_interactive()
```

---

## Performance Considerations

### ProgressBar
- Update interval: 0.1 seconds minimum between display updates
- Memory: O(1) - only current state tracked
- Best for: Operations with 10+ items

### PhaseProgressTracker
- Wraps ProgressBar for each phase
- Memory: O(number of phases)
- Best for: 2-5 distinct phases

### display_directory_tree()
- Recursive traversal with depth limiting
- Memory: O(max_depth * avg_files_per_directory)
- File size calculation can be slow for large directories
- Best for: Preview and validation, not real-time monitoring

### display_results_table()
- Sorts data if requested: O(n log n)
- Memory: O(number of rows)
- Width calculation: O(rows * columns)
- Best for: Result summaries (< 1000 rows)

---

## Error Handling

All UI components gracefully handle errors:

**ProgressBar**:
- Zero total: No-op, no errors
- Negative values: Clamped to valid range

**PhaseProgressTracker**:
- Invalid phase index: Silent no-op
- Phase already completed: No-op

**display_directory_tree()**:
- Non-existent path: Error message, returns immediately
- Permission denied: Shows "[Permission Denied]" for inaccessible directories
- Symbolic link loops: Limited by max_depth

**display_results_table()**:
- Empty data: Shows "No data to display"
- Mismatched columns: Pads with empty cells
- Formatter errors: Falls back to str()

---

## Testing

Component tests are available in:
- `planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_progress_bar.py`
- `planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_phase_tracker.py`
- `planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_directory_tree.py`
- `planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_table.py`

Run tests:
```bash
python3 planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_progress_bar.py
python3 planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_phase_tracker.py
python3 planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_directory_tree.py
python3 planning/sprints/active/10.0_ui_improvements_lib_ui/artifacts/test_table.py
```

---

## Migration Guide

### Migrating from display_progress_item()

**Before**:
```python
for i, item in enumerate(items, 1):
    display_progress_item(i, len(items), item.name, "Processing")
    process(item)
```

**After**:
```python
with ProgressBar(total=len(items), desc="Processing") as pb:
    for item in items:
        process(item)
        pb.update(1)
```

### Migrating from print() statements for phases

**Before**:
```python
print("Phase 1: Starting consolidation...")
consolidate()
print("Phase 1: Complete")

print("Phase 2: Starting organization...")
organize()
print("Phase 2: Complete")
```

**After**:
```python
tracker = PhaseProgressTracker(["Phase 1: Consolidation", "Phase 2: Organization"])

tracker.start_phase(0)
consolidate()
tracker.complete_phase(0)

tracker.start_phase(1)
organize()
tracker.complete_phase(1)

tracker.display_summary()
```

---

## Future Enhancements (Sprint 11.0+)

Planned components not yet implemented:

- **TieredOutput**: Manage different verbosity levels
- **OperationTimer**: Track and display operation timing
- **display_conflicts()**: Visualize file conflicts and duplicates
- **Spinner**: Indicate activity for indeterminate operations
- **Interactive menus**: Allow selection with arrow keys

---

## Compatibility

- **Python Version**: 3.8+
- **Platforms**: macOS, Linux, Windows
- **Dependencies**: Python standard library only
- **Terminal Requirements**: Any terminal (ASCII fallback for limited terminals)

---

## Support

For issues, questions, or contributions related to the UI library:

1. Check this documentation first
2. Review test scripts for usage examples
3. Consult `CLAUDE.md` for coding standards
4. Create an issue in the repository

---

**Document Version**: 2.0  
**Last Updated**: September 30, 2025  
**Sprint**: 10.0 - UI Component Library Enhancement
