# SABnzbd Tools

Python utilities for managing SABnzbd downloads and maintaining clean download directories.

## Overview

This directory contains self-contained Python tools designed to help you manage SABnzbd downloads safely and efficiently. The tools focus on cleaning up temporary and incomplete download directories while avoiding interference with BitTorrent downloads in shared directories.

## Tools

### sabnzbd_cleanup

A sophisticated Python script that safely identifies and removes temporary/incomplete download directories created by SABnzbd in shared directories that may also contain BitTorrent downloads.

## Features

- **Smart detection**: Uses scoring algorithms to distinguish SABnzbd from BitTorrent downloads
- **Safe preview mode**: List-only mode by default to prevent accidental deletions
- **Comprehensive error handling**: Graceful permission management and error recovery
- **Progress indicators**: Visual feedback for large directory scans
- **Human-readable reporting**: Clear size calculations and status messages
- **Detailed logging**: Verbose and debug modes for troubleshooting
- **Automation-friendly**: Cron-compatible with automatic non-interactive detection
- **Self-contained**: Uses only Python standard library modules

## Banner System

All SABnzbd tools display a consistent ASCII art banner by default that identifies them as part of the media-library-tools project. Banner display can be controlled via:

- `--no-banner` flag for one-time suppression
- `QUIET_MODE=true` global configuration for permanent suppression
- Automatic suppression in non-interactive environments (cron, CI/CD)

## Installation

These tools require Python 3.6+ and use only standard library modules.

```bash
# Make scripts executable
chmod +x sabnzbd_cleanup

# Run directly
./sabnzbd_cleanup --help
```

## Usage

### Basic usage
```bash
# Preview what would be cleaned (safe)
./sabnzbd_cleanup /path/to/downloads

# Show detailed detection information
./sabnzbd_cleanup /path/to/downloads --verbose

# Actually delete identified directories (requires confirmation)
./sabnzbd_cleanup /path/to/downloads --delete

# Non-interactive mode for automation/cron
./sabnzbd_cleanup /path/to/downloads --delete -y
```

### Command line options

```bash
./sabnzbd_cleanup [path] [options]

Positional Arguments:
  path                  Directory to search (default: current directory)

Options:
  --delete              Actually delete found directories (default: list only)
  --prune-at SIZE       Auto-delete when total size exceeds threshold (e.g., 50G, 2T)
  -y, --yes             Skip confirmation prompt (for non-interactive use)
  --verbose, -v         Show verbose output
  --debug               Show detailed debug output for all directories
  --force               Force execution even if another instance is running
  --version             Show version information
  --help, -h            Show help message
```

### Examples

#### Clean up failed downloads
SABnzbd often leaves behind temporary directories when downloads fail or are cancelled:
```bash
./sabnzbd_cleanup /downloads --verbose
```

#### Mixed download directories
If you use the same directory for both SABnzbd and BitTorrent downloads:
```bash
./sabnzbd_cleanup /shared/downloads --debug
```

#### Automated cleanup
For scheduled cleanup (after stopping SABnzbd):
```bash
# Interactive mode (requires confirmation)
./sabnzbd_cleanup /downloads --delete

# Non-interactive mode for cron jobs
./sabnzbd_cleanup /downloads --delete -y
```

## Automation support

The script automatically detects cron environments and operates in non-interactive mode:
```bash
# Daily cleanup at 3 AM
0 3 * * * /path/to/sabnzbd_cleanup /downloads --delete -y >> /var/log/sabnzbd_cleanup.log 2>&1

# Weekly cleanup with size threshold
0 2 * * 0 /path/to/sabnzbd_cleanup /downloads --delete --prune-at 50G -y >> /var/log/sabnzbd_cleanup.log 2>&1
```

## Technical details

### Detection algorithm

The cleanup script uses a sophisticated scoring system to identify SABnzbd directories:

**High confidence indicators:**
- SABnzbd administrative files (`__admin__`, `SABnzbd_nzf`, `SABnzbd_nzo`)
- NZB download files
- Unpack/extract directories (`_UNPACK_*`, `EXTRACT_*`)

**Medium confidence indicators:**
- PAR2 verification files
- RAR archives with PAR2/NZB files
- Usenet naming patterns (par2, yEnc, nzb in directory names)
- Retry suffixes (.1, .2, etc.)

**BitTorrent exclusion:**
- Automatically detects and skips .torrent files
- Recognizes BitTorrent client files (.resume, .fastresume, .!ut)
- Identifies BitTorrent naming patterns

### Safety features

- Never deletes without explicit user confirmation (unless `-y` flag used)
- Skips BitTorrent downloads automatically
- Handles permission errors gracefully
- Shows exactly what will be deleted before taking action
- File locking prevents concurrent executions
- Automatic detection of non-interactive environments

## Safety guidelines

1. **Always test first**: Run without `--delete` to see what would be removed
2. **Stop SABnzbd**: Ensure SABnzbd is not actively downloading before cleanup
3. **Check permissions**: Ensure you have appropriate permissions for the target directory
4. **Backup important data**: While the script is designed to be safe, always backup critical data

## Troubleshooting

### Permission denied errors
```bash
# Check directory permissions
ls -la /path/to/downloads

# Run with appropriate user permissions
sudo -u sabnzbd ./sabnzbd_cleanup /downloads
```

### No directories found
- Verify the path is correct
- Use `--debug` to see detailed analysis of all directories
- Check if SABnzbd is using a different temporary directory structure

### False positives/negatives
- Use `--debug` to see scoring details
- Report issues with specific directory examples
- The scoring system can be adjusted if needed

## Documentation

- [`docs/sabnzbd_cleanup.md`](docs/sabnzbd_cleanup.md) - Detailed documentation for the cleanup script

## Version history

- **v2.2**: Added cron-friendly features, `-y` flag, and `--prune-at` threshold
- **v2.1**: Python implementation with scoring system
- **v2.0**: Python rewrite from original bash script
- **v1.x**: Original bash implementation