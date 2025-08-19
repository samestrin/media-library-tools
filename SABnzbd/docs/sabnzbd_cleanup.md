# SABnzbd Directory Cleanup Script

## Overview

A Python script that safely identifies and removes temporary/incomplete download directories created by SABnzbd (a Usenet downloader) in shared directories that may also contain BitTorrent downloads.

## Features

- **Smart detection**: Uses scoring algorithms to distinguish SABnzbd from BitTorrent downloads
- **Safe preview mode**: List-only mode by default to prevent accidental deletions
- **Mixed environment support**: Handles directories with both Usenet and BitTorrent downloads
- **Permission handling**: Gracefully skips inaccessible directories
- **Progress indicators**: Visual feedback for large directory scans
- **Automation-friendly**: Cron-compatible with file locking and non-interactive mode
- **Self-contained**: Uses only Python standard library modules

## Installation

This tool requires Python 3.6+ and uses only standard library modules.

```bash
# Make script executable
chmod +x sabnzbd_cleanup

# Run directly
./sabnzbd_cleanup --help
```

## Usage

### Basic commands
```bash
# List SABnzbd directories (safe preview)
./sabnzbd_cleanup /downloads

# Show verbose details about detection
./sabnzbd_cleanup /downloads --verbose

# Show debug info for ALL directories
./sabnzbd_cleanup /downloads --debug

# Actually delete directories (with confirmation)
./sabnzbd_cleanup /downloads --delete

# Force execution even if another instance is running
./sabnzbd_cleanup /downloads --delete --force

# Show version
./sabnzbd_cleanup --version
```

### Automation support

The script is designed to work seamlessly with cron for automated cleanup:

```bash
# Add to crontab for hourly cleanup
0 * * * * /path/to/sabnzbd_cleanup /downloads --delete

# Daily cleanup at 3 AM
0 3 * * * /path/to/sabnzbd_cleanup /downloads --delete

# Weekly cleanup on Sundays at 2 AM
0 2 * * 0 /path/to/sabnzbd_cleanup /downloads --delete
```

**Cron features:**
- Automatically proceeds with deletion in non-interactive mode
- Uses file locking to prevent overlapping executions
- Minimal output unless errors occur
- Proper exit codes for monitoring

## Output format
```
SABnzbd Directory Cleanup v2.1
==================================================
Searching in: /mnt/in_progress
Mode: LIST ONLY

Found 15 SABnzbd directories:
==================================================

   2.3G  Prisoners of S02 1080p WEB-DL AAC2.0 AVC-TrollHD
   856M  Monster.S01E03.WEB.NOR.HC.Eng.Sub-TVC
   1.1G  Easy.Money.E01.BBC.SE.HC.Eng.Sub.HDTV.x264-TVC.1
   423M  Fantasy__LitRPG__Science_Fiction__Michael_Chatfield.par2__yEnc.1
   ...

==================================================
Total: 8.7G across 15 directories

Skipped 45 directories identified as BitTorrent downloads
```

## Safety features

- **List-first approach**: Shows what would be deleted before any action
- **Permission handling**: Gracefully skips inaccessible directories
- **Size calculation**: Displays individual and total sizes
- **Confirmation prompt**: Requires explicit approval before deletion
- **Progress indicators**: Shows scanning progress and statistics
- **Debug mode**: Detailed analysis of each directory's scoring
- **File locking**: Prevents multiple instances from running simultaneously
## Technical details

### Detection algorithm

The script uses a scoring system to identify SABnzbd directories:

**SABnzbd-specific indicators (high confidence):**
- Administrative files (`__admin__`, `SABnzbd_nzf`, `SABnzbd_nzo`) → +15 points
- NZB download files → +10 points
- Unpack/extract directories (`_UNPACK_*`, `EXTRACT_*`) → +12 points

**Usenet-specific patterns (medium confidence):**
- PAR2 verification files → +6 points (+3 bonus for multiple files)
- RAR archives with PAR2/NZB files → +6 points
- Directory names containing par2, yEnc, nzb → +6 points
- Retry suffixes (.1, .2, etc.) → +5 points
- TV show patterns with retry suffix → +5 points

**BitTorrent exclusion (active filtering):**
- Detects and skips .torrent files
- Recognizes BitTorrent client files (.resume, .fastresume, .!ut)
- Identifies BitTorrent naming patterns

**Threshold system:**
- Default threshold: 10 points
- Lowered to 5 with NZB files present
- Lowered to 8 with PAR2 files present
- Override: NZB + PAR2 = automatic detection

### Implementation details

- Written in Python 3.6+
- Uses pathlib for robust file operations
- Handles permission errors gracefully
- Configurable detection thresholds
- File locking mechanism prevents concurrent executions
- Supports both interactive and non-interactive modes
- Proper exit codes for automation monitoring

## Use cases

- SABnzbd has filled up your download drive
- You want to clean up failed/incomplete Usenet downloads
- Your download directory contains both Usenet and BitTorrent files
- You need to free up space but want to preserve legitimate downloads