```plain
┏┳┓┏━╸╺┳┓╻┏━┓╻  ╻┏┓ ┏━┓┏━┓┏━┓╻ ╻          
┃┃┃┣╸  ┃┃┃┣━┫┃  ┃┣┻┓┣┳┛┣━┫┣┳┛┗┳┛          
╹ ╹┗━╸╺┻┛╹╹ ╹┗━╸╹┗━┛╹┗╸╹ ╹╹┗╸ ╹           
┏┳┓┏━┓┏┓╻┏━┓┏━╸┏┳┓┏━╸┏┓╻╺┳╸╺┳╸┏━┓┏━┓╻  ┏━┓
┃┃┃┣━┫┃┗┫┣━┫┃╺┓┃┃┃┣╸ ┃┗┫ ┃  ┃ ┃ ┃┃ ┃┃  ┗━┓
╹ ╹╹ ╹╹ ╹╹ ╹┗━┛╹ ╹┗━╸╹ ╹ ╹  ╹ ┗━┛┗━┛┗━╸┗━┛                         
```                                             
# Media Library Management Tools

A comprehensive collection of self-contained Python CLI tools for managing and organizing media libraries across Plex, SABnzbd, and other media applications. Each tool is designed as a standalone script requiring no external dependencies, focusing on safety, automation, and consistent user experience.

## Overview

This project provides a unified suite of tools that help you maintain clean, well-organized media libraries. Each tool follows consistent design principles with standardized CLI interfaces, comprehensive safety features, and detailed logging capabilities. All tools are self-contained Python scripts that you can download and run immediately without any installation or setup.

## Features

- **Self-contained design**: Each tool is a standalone Python script using only standard library modules
- **Zero dependencies**: No external libraries required - download, `chmod +x`, and run immediately
- **Safety first**: All tools include dry-run modes and comprehensive validation before making changes
- **Consistent interface**: Standardized CLI arguments and output formatting across all tools
- **Comprehensive logging**: Detailed verbose and debug modes for troubleshooting and monitoring
- **Cross-platform compatibility**: Python-based tools that work across different operating systems
- **Automation-friendly**: Built-in support for cron jobs with non-interactive modes
- **Well-documented**: Extensive documentation and practical usage examples for every tool

## Project Structure

```
media-library-tools/
├── plex/                                     # Plex media organization tools
│   ├── docs/                                 # Documentation for Plex tools
│   │   ├── plex_correct_dirs.md              # Directory name sanitization documentation
│   │   ├── plex_make_all_seasons.md          # Batch season processing documentation
│   │   ├── plex_make_dirs.md                 # Directory structure creation documentation
│   │   ├── plex_make_seasons.md              # TV show season organization documentation
│   │   ├── plex_make_years.md                # Year-based organization documentation
│   │   ├── plex_move_movie_extras.md         # Movie extras organization documentation
│   │   └── plex_movie_subdir_renamer.md      # Movie subdirectory renaming documentation
│   ├── plex_correct_dirs                     # Directory name sanitization tool
│   ├── plex_make_all_seasons                 # Batch season processing tool
│   ├── plex_make_dirs                        # Directory structure creation tool
│   ├── plex_make_seasons                     # TV show season organization tool
│   ├── plex_make_years                       # Year-based organization tool
│   ├── plex_move_movie_extras                # Movie extras organization tool
│   ├── plex_movie_subdir_renamer             # Movie subdirectory renaming tool
│   └── README.md                             # Plex tools overview
├── plex-api/                                 # Plex server management tools
│   ├── docs/                                 # Documentation for Plex API tools
│   │   └── plex_server_episode_refresh.md    # Episode refresh tool documentation
│   ├── plex_server_episode_refresh           # Episode thumbnail regeneration tool
│   └── README.md                             # Plex API tools overview
├── QWEN.md                                   # Agent configuration file (private)
├── README.md                                 # Project overview and main documentation
└── SABnzbd/                                  # SABnzbd cleanup and management tools
    ├── docs/                                 # Documentation for SABnzbd tools
    │   └── sabnzbd_cleanup.md                # SABnzbd cleanup documentation
    ├── README.md                             # SABnzbd tools overview
    └── sabnzbd_cleanup                       # SABnzbd directory cleanup tool
```

## Available Tools

### SABnzbd Tools

#### `sabnzbd_cleanup` - Self-Contained Python
Intelligent cleanup tool for SABnzbd download directories.

**Self-Contained Features:**
- **Zero dependencies**: Uses only Python standard library
- **Single file**: Complete functionality in one script
- **Portable**: Download and run anywhere with Python
- Detects SABnzbd-specific directory patterns
- Avoids BitTorrent directories to prevent data loss
- Calculates disk space savings before cleanup
- Interactive confirmation with detailed file listings (or `-y` for automation)
- Comprehensive logging and safety checks
- Cron-friendly with automatic non-interactive detection

**Quick Start:**
```bash
# Download and run immediately
wget [raw-url]/sabnzbd_cleanup && chmod +x sabnzbd_cleanup

# Scan for SABnzbd directories (safe mode)
./sabnzbd_cleanup /path/to/downloads

# Actually delete identified directories
./sabnzbd_cleanup /path/to/downloads --delete

# Non-interactive mode for cron jobs
./sabnzbd_cleanup /path/to/downloads --delete -y
```

### Plex Tools

#### Media Organization Suite
Comprehensive tools for organizing media libraries according to Plex naming conventions.

**Current Status:**
- `plex_move_movie_extras` - Python (Complete)
- `plex_movie_subdir_renamer` - Python (Complete)
- `plex_server_episode_refresh` - Python (Complete)
- Directory and TV show tools - Bash scripts being migrated to Python

**Capabilities:**
- Directory name sanitization and cleanup
- TV show season organization
- Movie extras management
- Year-based movie organization
- Batch processing for large libraries

**Migration Benefits:**
- **Self-contained design**: No external dependencies
- **Portable execution**: Download and run anywhere
- Standardized CLI interfaces with `-y` flag for automation
- Better error handling and recovery
- Progress indicators for large operations
- Comprehensive dry-run modes
- Improved safety features
- Cron-friendly with automatic non-interactive detection

## Quick Start Guide

### Installation

### Individual tool download (Recommended)
```bash
# Download any single tool and run immediately
wget https://raw.githubusercontent.com/[repo]/media-library-tools/main/SABnzbd/sabnzbd_cleanup
chmod +x sabnzbd_cleanup
./sabnzbd_cleanup --help

# All tools support standard arguments:
# --verbose, --debug, --dry-run, --force, --version, -y/--yes
```

### Full repository
```bash
# Clone entire repository
git clone <repository-url>
cd media-library-tools
chmod +x SABnzbd/sabnzbd_cleanup plex/plex_* plex-api/plex_*
```

### No dependencies required
- **Zero installation**: All tools use Python standard library only
- **No pip install**: No external packages needed
- **Portable**: Works on any system with Python 3.6+

## Usage

### Common workflows

#### Clean up downloads
```bash
# Clean up SABnzbd leftovers (preview mode)
./SABnzbd/sabnzbd_cleanup /path/to/downloads --verbose

# Clean up SABnzbd leftovers (execute)
./SABnzbd/sabnzbd_cleanup /path/to/downloads --delete -y

# Organize Plex media (preview mode)
./plex/plex_correct_dirs /path/to/media

# Organize Plex media (execute)
./plex/plex_correct_dirs /path/to/media -y
```

#### Organize TV shows
```bash
# Create season directories (preview mode)
./plex/plex_make_seasons /path/to/tv/show --dry-run

# Create season directories (execute)
./plex/plex_make_seasons /path/to/tv/show -y
```

#### Process movie extras
```bash
# Move and rename movie extras from subdirectories (preview mode)
./plex/plex_move_movie_extras "Movie (2023).mkv" "Featurettes" --dry-run

# Move and rename movie extras from subdirectories (execute)
./plex/plex_move_movie_extras "Movie (2023).mkv" "Featurettes" -y

# Rename movie extras within subdirectories (preview mode)
./plex/plex_movie_subdir_renamer "/Movies/Movie (2023)/Extras" --dry-run

# Rename movie extras within subdirectories (execute)
./plex/plex_movie_subdir_renamer "/Movies/Movie (2023)/Extras" --execute -y
```

## Automation support

All tools support automation-friendly operation with built-in non-interactive detection.

### Automatic non-interactive detection
Tools automatically detect non-interactive environments:
- Cron jobs
- CI/CD pipelines
- SSH sessions without TTY
- Scripts with redirected input

### Manual non-interactive mode
Use the `-y` or `--yes` flag to skip confirmation prompts:

```bash
# SABnzbd cleanup in cron
./sabnzbd_cleanup /downloads --delete -y

# Plex organization in automation
./plex/plex_make_seasons /media/tv -y
./plex/plex_make_years /media/movies -y
```

### Cron examples
```bash
# Daily SABnzbd cleanup at 3 AM
0 3 * * * /path/to/sabnzbd_cleanup /downloads --delete -y >> /var/log/sabnzbd_cleanup.log 2>&1

# Weekly Plex organization on Sundays at 2 AM
0 2 * * 0 /path/to/plex_make_all_seasons /media/tv -y >> /var/log/plex_organize.log 2>&1

# Monthly year-based organization
0 1 1 * * /path/to/plex_make_years /media/movies -y >> /var/log/plex_years.log 2>&1
```

### Safety in automation
- File locking prevents concurrent executions
- Comprehensive logging for troubleshooting
- Graceful handling of permission errors
- Exit codes for monitoring systems

## Safety features

### Built-in protections
- **Dry-run modes**: Preview operations before execution
- **Interactive confirmations**: User approval for destructive operations (or `-y` for automation)
- **Lock files**: Prevent multiple instances of the same tool
- **Path validation**: Ensure target directories exist and are accessible
- **BitTorrent detection**: Avoid interfering with active torrents
- **Non-interactive detection**: Automatic cron-friendly behavior

### Best practices
- Always test with `--dry-run` first
- Backup important media before bulk operations
- Use `--verbose` mode to understand what tools are doing
- Start with small test directories before processing entire libraries

## Technical details

### Python requirements
- **Python version**: 3.6 or higher
- **Dependencies**: Standard library only
- **Platform**: Cross-platform (Linux, macOS, Windows)

### Design principles
1. **Self-contained design**: Each tool is a complete, standalone script
2. **Zero dependencies**: Use only Python standard library modules
3. **Maintain functionality**: Preserve all existing features
4. **Improve safety**: Add better validation and error handling
5. **Standardize interface**: Consistent CLI arguments and output
6. **Add features**: Progress indicators, better logging, built-in help
7. **Portable execution**: Download, `chmod +x`, and run immediately

### Debugging
```bash
# Enable debug mode for detailed logging
./tool_name --debug --verbose

# Use dry-run to see what would happen
./tool_name --dry-run --verbose
```

## Documentation

### Tool-specific documentation
- **SABnzbd**: See `SABnzbd/README.md` and `SABnzbd/docs/sabnzbd_cleanup.md`
- **Plex**: See `plex/README.md` for detailed tool descriptions
- **Plex API**: See `plex-api/README.md` for server management tools

### Safe operation workflow
1. **Always start with dry-run**: `--dry-run` flag available on most tools
2. **Use verbose mode**: `--verbose` for detailed operation logs
3. **Check results**: Review what will be changed before proceeding
4. **Backup important data**: Especially before bulk operations



## Project status

| Component | Status | Language | Features |
|-----------|--------|----------|----------|
| SABnzbd Tools | Complete | Python | Full feature set |
| Plex Media Tools | Complete | Python | Full feature set |
| Plex Directory Tools | Complete | Python | Full feature set |
| Project Documentation | Complete | Markdown | Comprehensive |
| Coding Standards | Complete | Guidelines | Established |

### Future enhancements
- **Built-in configuration**: Embedded config options (no external files)
- **Batch processing**: Process multiple directories efficiently
- **Self-testing**: Built-in `--test` modes for validation
- **Enhanced portability**: Even better cross-platform compatibility

## Support

### Getting help
- Check tool-specific README files in each directory
- Use `--help` flag on any tool for usage information
- Review the documentation in the `docs/` subdirectories

### Reporting issues
When reporting issues, please include:
- Tool name and version (`./tool_name --version`)
- Operating system and Python version
- Complete command line used
- Error messages or unexpected behavior
- Sample directory structure (if relevant)
- Output from `--debug --verbose` mode

---

**Note**: This project prioritizes safety and data integrity. All tools are designed to be conservative and require explicit user confirmation for destructive operations. Always backup your media libraries before running bulk operations.