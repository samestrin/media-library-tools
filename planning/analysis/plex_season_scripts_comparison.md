# Plex Season Scripts Comparison Analysis

## Overview
This document analyzes the differences and similarities between `plex_make_seasons` and `plex_make_all_seasons` to identify the best implementation method for synchronization.

## Key Differences

### 1. Scope and Functionality
**plex_make_seasons:**
- Processes video files in a single directory
- Designed for organizing one TV show at a time
- Interactive confirmation by default
- No parallel processing capabilities

**plex_make_all_seasons:**
- Processes multiple TV show directories
- Batch processing of multiple shows
- Parallel processing capabilities with threading
- Recursive directory processing option

### 2. Season Detection Patterns
**plex_make_seasons:**
- More comprehensive pattern matching (13 patterns)
- Supports various naming conventions including year-based seasons
- Handles part/chapter/disc/volume patterns
- More flexible pattern matching with descriptive labels

**plex_make_all_seasons:**
- More limited pattern matching (4 patterns)
- Focuses on standard S##E## formats
- Less flexible but more focused approach

### 3. Class Structure
**plex_make_seasons:**
- Single `SeasonOrganizer` class
- Handles all functionality in one class

**plex_make_all_seasons:**
- Two main classes: `SeasonOrganizer` and `PlexSeasonBatchOrganizer`
- Separation of single directory logic and batch processing logic
- More modular design

### 4. Parallel Processing
**plex_make_seasons:**
- No parallel processing
- Sequential file processing only

**plex_make_all_seasons:**
- Uses `concurrent.futures.ThreadPoolExecutor` for parallel processing
- Configurable number of worker threads
- Sequential processing option (1 worker)

### 5. Command Line Interface
**plex_make_seasons:**
- `--target` option to specify different target directory
- `--list-patterns` option to display supported patterns
- More detailed help examples

**plex_make_all_seasons:**
- `--parallel`/`--workers` option for thread count
- `--recursive` option for deep directory processing
- Different default behavior (processes subdirectories)

### 6. Error Handling and Reporting
**plex_make_seasons:**
- Detailed per-file error reporting
- Pattern usage statistics
- Individual file collision handling

**plex_make_all_seasons:**
- Batch-level error reporting
- Overall statistics summary
- Directory-level error tracking

## Key Similarities

### 1. Core Functionality
- Both organize video files into season directories
- Both use season number extraction from filenames
- Both create "Season ##" directory names
- Both handle file collisions with unique naming
- Both support dry-run mode

### 2. Non-Interactive Detection
- Both implement `is_non_interactive()` function for cron/automation detection
- Both support `-y`/`--yes` flag for skipping confirmation

### 3. File Locking
- Both implement file-based locking with `fcntl`
- Both support `--force` flag to bypass locking

### 4. Video File Detection
- Both use extension-based video file detection
- Similar sets of supported video extensions (with some differences)

### 5. Season Directory Naming
- Both create "Season ##" directories
- Both handle season number formatting

## Complexity Assessment

### Files/Components Affected
- 2 existing scripts to refactor
- Potential shared utility module creation
- Test files to update

### Integration Complexity
- Low to moderate - both scripts are standalone
- Need to maintain backward compatibility
- Shared logic should be extracted to common module

### New Dependencies
- No new external dependencies required
- Only standard library modules used

### Testing Complexity
- Moderate - need to test both individual and batch functionality
- Need to verify pattern matching works correctly
- Edge cases around file collisions and error handling

## Recommendation

The best approach would be to:
1. Extract common functionality into a shared module
2. Enhance `plex_make_all_seasons` with the better pattern matching from `plex_make_seasons`
3. Maintain the batch processing and parallel capabilities of `plex_make_all_seasons`
4. Keep the single directory focus of `plex_make_seasons` but improve its pattern matching

This approach leverages the strengths of both scripts while providing consistency in their core logic.