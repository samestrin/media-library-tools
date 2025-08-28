# Plex Directory Creator

## Overview

A Python tool for converting loose media files into proper directory structures. This script creates a directory for each file (named after the file without extension) and moves the file into its corresponding directory, which is ideal for Plex media organization where each movie should be in its own directory.

## Features

- **Automatic directory creation** - Creates a directory for each file using the filename (without extension)
- **File movement** - Moves each file into its corresponding directory
- **Multiple file type support** - Supports video, audio, image, document, and archive files
- **Custom file type filtering** - Process only specific file types or exclude certain types
- **Collision detection** - Handles naming conflicts intelligently
- **File-based locking** - Prevents multiple instances from running simultaneously
- **Dry-run mode** - Preview changes before execution
- **Collision handling** - Manages conflicts when directories or files already exist
- **Error recovery** - Continues processing even if individual files fail
- **Progress tracking** - Real-time feedback on processing status
- **Non-interactive operation** - Runs without user input for automation
- **Comprehensive logging** - Detailed output for monitoring
- **Exit codes** - Proper exit codes for script monitoring
- **Lock override** - `--force` flag for emergency situations
- **Self-contained** - Uses only Python standard library modules
- **Zero installation** - Download and run immediately

## Installation

```bash
# Download and make executable
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/plex/plex_make_dirs
chmod +x plex_make_dirs
```

## Usage

### Basic usage
```bash
# Process all supported files
./plex_make_dirs.py /path/to/media/files

# Preview changes first
./plex_make_dirs.py /path/to/media/files --dry-run

# Process only video files
./plex_make_dirs.py /path/to/media/files --types mp4 mkv avi
```

### Automation
```bash
# Daily processing at 4 AM
0 4 * * * /usr/local/bin/plex_make_dirs.py /path/to/downloads

# Force execution (bypass lock)
./plex_make_dirs.py /path/to/media --force
```

## Command-line Options

| Option | Description |
|--------|-------------|
| `directory` | Directory containing files to process (required) |
| `--dry-run` | Show what would be done without making changes |
| `--force` | Force execution even if another instance is running |
| `--types EXT [EXT ...]` | File extensions to process (e.g., mp4 mkv avi) |
| `--exclude EXT [EXT ...]` | File extensions to exclude from processing |
| `--list-types` | List all supported file types and exit |
| `--version` | Show version information |
| `--help` | Show help message |

## Supported file types

### Video files
- **Common**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`
- **MPEG**: `.mpg`, `.mpeg`, `.3gp`, `.ts`, `.m2ts`, `.vob`
- **Codecs**: `.divx`, `.xvid`, `.rm`, `.rmvb`, `.asf`, `.f4v`

### Audio files
- **Lossless**: `.flac`, `.wav`, `.aiff`, `.au`
- **Compressed**: `.mp3`, `.aac`, `.ogg`, `.wma`, `.m4a`, `.opus`
- **Surround**: `.ac3`, `.dts`, `.ra`

### Image files
- **Web**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`
- **Print**: `.bmp`, `.tiff`, `.tif`, `.ico`
- **Professional**: `.psd`, `.raw`, `.cr2`, `.nef`, `.arw`

### Document files
- `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.pages`

### Archive files
- `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.xz`

## Processing logic

### Directory creation
1. **File analysis** - Scans the target directory for files matching specified types
2. **Name generation** - Creates directory name from filename (without extension)
3. **Collision detection** - Checks for existing directories or files with the same name
4. **Directory creation** - Creates the directory if it doesn't exist
5. **File movement** - Moves the file into the newly created directory

### Collision handling
- **Empty directory** - Reuses existing empty directories
- **File conflict** - Renames conflicting files with `_backup` suffix
- **Directory conflict** - Creates numbered variants (e.g., `Movie_1`, `Movie_2`)
- **Same file** - Skips if the file is already in the correct directory

## Safety features

- **Automatic lock** - Creates temporary lock file to prevent concurrent runs
- **PID tracking** - Stores process ID in lock file for monitoring
- **Clean cleanup** - Automatically removes lock file on exit
- **Force override** - `--force` flag bypasses lock for emergency situations
- **Graceful failures** - Continues processing other files if one fails
- **Detailed logging** - Reports specific errors for troubleshooting
- **Rollback safety** - Original files remain intact if directory creation fails
- **Permission checks** - Validates write permissions before processing
- **Safe preview** - Shows exactly what would be done without making changes
- **Collision preview** - Displays how naming conflicts would be resolved
- **Statistics** - Provides counts of files that would be processed
- **Validation** - Helps identify potential issues before execution

## Troubleshooting

### "Another instance is already running"
```
ERROR: Another instance is already running (PID: 12345)
```
**Solution:**
- Wait for the current process to finish
- Use `--force` flag to override if the process is stuck
- Check if the PID is still active: `ps -p 12345`

### "Permission denied"
```
ERROR: Permission denied: /path/to/directory
```
**Solution:**
- Check directory permissions: `ls -la /path/to/directory`
- Ensure write access to the target directory
- Run with appropriate user permissions

### "No files found to process"
```
INFO: No supported files found in directory
```
**Solution:**
- Verify the directory contains supported file types
- Use `--list-types` to see supported extensions
- Check if files are already organized

### "Files not being processed"
**Possible causes:**
- Files are already in subdirectories
- File extensions not in supported list
- Files are hidden (start with '.')
- Insufficient permissions

**Debug steps:**
```bash
# Enable debug output
./plex_make_dirs.py /path/to/media --debug

# List all files in directory
find /path/to/media -type f -name "*" | head -20

# Check supported types
./plex_make_dirs.py --list-types
```

## Technical details

- **Python 3.6+** - Uses only standard library modules
- **Cross-platform** - Works on Linux, macOS, and Windows
- **Memory efficient** - Processes files individually, not in bulk
- **Fast processing** - Uses efficient file operations
- **Atomic moves** - Files are moved atomically to prevent corruption
- **Unicode support** - Handles international characters in filenames
- **Path validation** - Validates all paths before processing
- **Symlink handling** - Follows symbolic links appropriately
- **Temporary directory** - Uses system temp directory for lock files
- **PID tracking** - Stores process ID for monitoring and cleanup
- **Automatic cleanup** - Removes lock files on normal and abnormal exit
- **Permission checks** - Respects file system permissions
- **Temporary files** - Uses secure temporary file creation
- **Error isolation** - Errors in one file don't affect others

### Implementation

- **Path validation** - Prevents directory traversal attacks
- **Permission checks** - Respects file system permissions
- **Temporary files** - Uses secure temporary file creation
- **Error isolation** - Errors in one file don't affect others

---

*Part of the Media Library Tools project - A collection of utilities for managing and organizing media libraries.*