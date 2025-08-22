# Plex Directory Name Corrector

## Overview

A comprehensive Python tool for sanitizing and organizing Plex media directory names. This script processes directory names to ensure they follow Plex naming conventions by removing unwanted tags, standardizing formats, and organizing files into proper directory structures.

## Features

- **Comprehensive tag removal** - Advanced regex patterns for removing release groups, quality tags, codec information, and streaming service identifiers
- **Smart format standardization** - Automatically converts resolutions (4K → [2160p]) and ensures proper year formatting
- **Extensible pattern system** - Organized regex patterns that can be easily extended for new tag types
- **Automatic directory creation** - Converts loose media files into proper directory structures
- **Collision detection** - Handles existing directories with sanitized names gracefully
- **Plex-optimized naming** - Ensures directory names follow Plex Media Server conventions
- **File locking** - Prevents multiple instances from running simultaneously
- **Dry-run mode** - Preview changes before execution with configurable item limits
- **Cron-friendly** - Designed for automated scheduling with proper error handling
- **Force override** - Bypass locking mechanism when needed
- **Self-contained** - Uses only Python standard library modules
- **Zero installation** - Download and run immediately

## Installation

```bash
# Download and make executable
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/Plex/plex_correct_dirs.py
chmod +x plex_correct_dirs.py
```

## Usage

### Basic usage
```bash
# Preview changes (dry-run)
./plex_correct_dirs.py /path/to/media --dry-run

# Process directory
./plex_correct_dirs.py /path/to/media
```

### Automation
```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/plex_correct_dirs.py /path/to/media

# Force run (bypass lock)
./plex_correct_dirs.py /path/to/media --force
```

## Command-line options

| Option | Description |
|--------|-------------|
| `directory` | Target directory to process (required) |
| `--dry-run` | Preview changes without making modifications (limited to 5 items) |
| `--force` | Force execution even if another instance is running |
| `--max-items N` | Maximum items to process in dry-run mode (default: 5) |
| `--version` | Display version information |
| `--help` | Show help message and exit |

## Tag removal patterns

The script uses comprehensive regex patterns to identify and remove:

- **Release groups** - YTS, RARBG, YIFY, FGT, ION10, ETRG, TGx, and many more
- **Video quality** - BluRay, WEBRip, DVDRip, BRRip, HDRip, HDCAM, etc.
- **Audio formats** - 5.1, 7.1, AC3, AAC, DTS, Dolby Atmos, TrueHD, etc.
- **Codecs** - H.264, H.265, x264, x265, HEVC, AVC, VP9, AV1, etc.
- **Enhancements** - HDR, HDR10+, Dolby Vision, IMAX, Director's Cut, etc.
- **Streaming services** - AMZN, NFLX, HULU, DSNP, ATVP, HBO, etc.
- **Technical tags** - 10bit, INTERNAL, PROPER, REPACK, REMUX, etc.

## Format standardization

- **Resolution formatting** - Encloses resolutions in brackets `[1080p]`, `[2160p]`
- **Year formatting** - Encloses 4-digit years in parentheses `(2023)`
- **4K conversion** - Automatically converts `[4K]` to `[2160p]`
- **Dot replacement** - Converts dots to spaces for readability
- **Cleanup** - Removes empty brackets, extra spaces, and trailing punctuation

## File organization

- **File to directory** - Converts loose media files into directories named after the file (without extension)
- **Directory sanitization** - Applies naming rules to existing directories
- **Collision handling** - Skips processing if sanitized name already exists

## Safety features

- **Automatic lock** - Creates temporary lock file to prevent concurrent execution
- **PID tracking** - Stores process ID in lock file for debugging
- **Clean cleanup** - Automatically removes lock file on exit
- **Force override** - Use `--force` flag to bypass locking (use with caution)
- **Cron-safe** - Prevents overlapping cron jobs from conflicting
- **Non-interactive** - Runs without user prompts in automated environments
- **Proper exit codes** - Returns appropriate exit codes for monitoring
- **Error handling** - Graceful handling of missing directories and permissions
- **Dry-run mode** - Test changes safely before execution
- **Collision detection** - Prevents overwriting existing directories
- **Lock file protection** - Prevents concurrent execution conflicts
- **Reversible operations** - Directory renames can be manually reversed if needed

## Examples

### Directory name sanitization
```
Before: The.Matrix.1999.2160p.UHD.BluRay.x265.HDR.Atmos-SPARKS
After:  The Matrix (1999) [2160p]

Before: Inception.2010.1080p.BluRay.x264.DTS-HD.MA.5.1-FGT
After:  Inception (2010) [1080p]

Before: Dune.Part.One.2021.4K.WEB-DL.DV.HDR10.Atmos-HMAX
After:  Dune Part One (2021) [2160p]
```

### File organization
```
Before: /Movies/Avatar.2009.1080p.BluRay.x264.mkv
After:  /Movies/Avatar.2009.1080p.BluRay.x264/Avatar.2009.1080p.BluRay.x264.mkv
        → /Movies/Avatar (2009) [1080p]/Avatar.2009.1080p.BluRay.x264.mkv
```

## Troubleshooting

### "Another instance is already running"
- Another copy of the script is running
- Use `--force` flag to override (ensure no other instance is actually running)
- Check for stale lock files in system temp directory

### "Directory does not exist"
- Verify the path is correct and accessible
- Check directory permissions
- Ensure the path is absolute or relative to current directory

### "Permission denied"
- Ensure write permissions to target directory
- Check if files are in use by other applications
- Run with appropriate user permissions

### Debug information

```bash
# Check what would be processed
./plex_correct_dirs.py /path/to/media --dry-run --max-items 20

# Verify script permissions
ls -la plex_correct_dirs.py

# Check directory permissions
ls -la /path/to/media
```

## Technical details

- **Python 3.6+** - Uses f-strings and pathlib
- **Standard library only** - No external dependencies required
- **Cross-platform** - Works on macOS, Linux, and Windows
- **Memory efficient** - Processes entries one at a time
- **Fast regex** - Compiled patterns for optimal performance
- **Minimal I/O** - Only reads directory structure, no file content
- **Safe operations** - Only renames/moves, never deletes
- **Path validation** - Prevents directory traversal attacks
- **Lock file security** - Uses secure temporary file creation

### Implementation

- **Safe operations** - Only renames/moves, never deletes
- **Path validation** - Prevents directory traversal attacks
- **Lock file security** - Uses secure temporary file creation

---

*Part of the Media Library Tools project - A collection of utilities for organizing and maintaining Plex media libraries.*