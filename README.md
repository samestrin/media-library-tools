```plain
┏┳┓┏━╸╺┳┓╻┏━┓╻  ╻┏┓ ┏━┓┏━┓┏━┓╻ ╻╺┳╸┏━┓┏━┓╻  ┏━┓         
┃┃┃┣╸  ┃┃┃┣━┫┃  ┃┣┻┓┣┳┛┣━┫┣┳┛┗┳┛ ┃ ┃ ┃┃ ┃┃  ┗━┓        
╹ ╹┗━╸╺┻┛╹╹ ╹┗━╸╹┗━┛╹┗╸╹ ╹╹┗╸ ╹  ╹ ┗━┛┗━┛┗━╸┗━┛                              
```                                             
# Media Library Tools
[![Star on GitHub](https://img.shields.io/github/stars/samestrin/media-library-tools?style=social)](https://github.com/samestrin/media-library-tools/stargazers) [![Fork on GitHub](https://img.shields.io/github/forks/samestrin/media-library-tools?style=social)](https://github.com/samestrin/media-library-tools/network/members) [![Watch on GitHub](https://img.shields.io/github/watchers/samestrin/media-library-tools?style=social)](https://github.com/samestrin/media-library-tools/watchers)
![Version 1.2.0-beta](https://img.shields.io/badge/Version-1.2.0--beta-orange) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Built with Python](https://img.shields.io/badge/Built%20with-Python-green)](https://python.org/)

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

## CLI Standardization (v1.2.0)

All tools now follow a completely standardized command-line interface with consistent behavior across the entire suite:

### Standard Arguments (Available on All Tools)
- `--dry-run` - **Default behavior**: Preview changes without making modifications
- `--execute` - Override dry-run mode to actually perform operations  
- `--no-banner` - Suppress banner display
- `--verbose` - Show detailed operation information
- `--debug` - Show comprehensive debug output (includes verbose)
- `-y` / `--yes` - Skip confirmation prompts for automation
- `--force` - Bypass lock files and force execution
- `--version` - Display tool version information

### Consistent Mode Indicators
Every tool clearly displays its current mode:
- **DRY-RUN MODE**: No changes will be made (default)
- **EXECUTE MODE**: Changes will be made to files/directories

### Global Configuration Support
Tools respect environment variables for default behavior:
- `AUTO_EXECUTE=true` - Default to execute mode instead of dry-run
- `AUTO_CONFIRM=true` - Skip confirmation prompts automatically
- `QUIET_MODE=true` - Suppress banner display by default

### Cron-Friendly Operation
All tools include comprehensive automation support with:
- Non-interactive environment detection
- Proper exit codes for monitoring
- Detailed logging for unattended operation
- Example cron configurations in help text

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
│   │   ├── plex_movie_subdir_renamer.md      # Movie subdirectory renaming documentation
│   │   └── plex_update_tv_years.md           # TV show year updater documentation
│   ├── plex_correct_dirs                     # Directory name sanitization tool
│   ├── plex_make_all_seasons                 # Batch season processing tool
│   ├── plex_make_dirs                        # Directory structure creation tool
│   ├── plex_make_seasons                     # TV show season organization tool
│   ├── plex_make_years                       # Year-based organization tool
│   ├── plex_move_movie_extras                # Movie extras organization tool
│   ├── plex_movie_subdir_renamer             # Movie subdirectory renaming tool
│   ├── plex_update_tv_years                  # TV show year updater tool
│   └── README.md                             # Plex tools overview
├── plex-api/                                 # Plex server management tools
│   ├── docs/                                 # Documentation for Plex API tools
│   │   └── plex_server_episode_refresh.md    # Episode refresh tool documentation
│   ├── plex_server_episode_refresh           # Episode thumbnail regeneration tool
│   └── README.md                             # Plex API tools overview
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

**All Tools Complete:**
- `plex_correct_dirs` - Directory name sanitization and cleanup
- `plex_make_all_seasons` - Batch season processing for TV shows
- `plex_make_dirs` - Directory structure creation
- `plex_make_seasons` - TV show season organization
- `plex_make_years` - Year-based movie organization
- `plex_move_movie_extras` - Movie extras management and relocation
- `plex_movie_subdir_renamer` - Movie subdirectory renaming
- `plex_update_tv_years` - Update TV show year metadata

**Key Capabilities:**
- Directory name sanitization and cleanup
- TV show season organization and batch processing
- Movie extras management and Plex-compliant naming
- Year-based movie organization
- Comprehensive safety features and dry-run modes

**Self-Contained Design Benefits:**
- **Zero dependencies**: Uses only Python standard library
- **Portable execution**: Download and run anywhere with Python
- **Standardized interface**: Consistent CLI arguments with `-y` flag for automation
- **Enhanced safety**: Comprehensive dry-run modes and confirmation prompts
- **Better reliability**: Improved error handling and recovery mechanisms
- **Progress tracking**: Visual indicators for large operations
- **Automation-ready**: Cron-friendly with automatic non-interactive detection

## Quick Start Guide

### Installation

### Individual tool download (Recommended)
```bash
# Download any single tool and run immediately
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/SABnzbd/sabnzbd_cleanup
chmod +x sabnzbd_cleanup
./sabnzbd_cleanup --help

# All tools support standard arguments:
# --verbose, --debug, --dry-run, --force, --version, -y/--yes
```

### Full repository
```bash
# Clone entire repository
git clone https://github.com/samestrin/media-library-tools.git
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

## Global Configuration

All tools support global configuration via environment variables and `.env` files, allowing you to set default behavior without specifying command-line flags every time.

### Environment Variables

#### `AUTO_EXECUTE`
Sets the default execution mode for tools that support `--execute`/`--dry-run` flags.

**Supported values**: `true`, `1`, `yes`, `on` (case-insensitive) enable execution mode; any other value keeps dry-run as default.

#### `AUTO_CONFIRM`
Sets the default confirmation behavior, equivalent to the `-y`/`--yes` flag.

**Supported values**: `true`, `1`, `yes`, `on` (case-insensitive) skip confirmation prompts; any other value keeps interactive confirmations.

### Configuration Hierarchy

Configuration is applied in the following order (highest to lowest precedence):
1. **CLI arguments**: Explicit command-line flags (e.g., `--execute`, `-y`)
2. **Environment variables**: `AUTO_EXECUTE`, `AUTO_CONFIRM`
3. **Local .env**: File in current working directory
4. **Global .env**: File in `~/.media-library-tools/.env`

### Setup Global Configuration

#### Method 1: Environment Variables
```bash
# Set globally for current session
export AUTO_EXECUTE=true
export AUTO_CONFIRM=true

# Add to shell profile for persistence
echo 'export AUTO_EXECUTE=true' >> ~/.bashrc
echo 'export AUTO_CONFIRM=true' >> ~/.bashrc
```

#### Method 2: Global Configuration File
```bash
# Create global config directory
mkdir -p ~/.media-library-tools

# Create global configuration file
cat > ~/.media-library-tools/.env << EOF
# Global configuration for media library tools
AUTO_EXECUTE=true
AUTO_CONFIRM=true
EOF
```

#### Method 3: Project-Specific Configuration
```bash
# Create local .env in your media directory
cd /path/to/your/media
cat > .env << EOF
# Project-specific configuration
AUTO_EXECUTE=false
AUTO_CONFIRM=true
EOF
```

### Usage Examples with Global Config

#### Traditional Usage (Still Supported)
```bash
# Explicit flags (always works)
./plex/plex_correct_dirs /media --execute -y
./SABnzbd/sabnzbd_cleanup /downloads --delete -y
```

#### With Global Configuration
```bash
# After setting AUTO_EXECUTE=true, AUTO_CONFIRM=true
./plex/plex_correct_dirs /media              # Runs in execute mode with no prompts
./SABnzbd/sabnzbd_cleanup /downloads --delete  # Deletes with no prompts

# CLI flags still override global config
./plex/plex_correct_dirs /media --dry-run    # Forces dry-run despite AUTO_EXECUTE=true
./SABnzbd/sabnzbd_cleanup /downloads --delete  # Will prompt despite AUTO_CONFIRM=true
```

#### Automation-Friendly Workflows
```bash
# Set up once for interactive workflows
echo "AUTO_EXECUTE=true" > ~/.media-library-tools/.env

# Now scripts run in execute mode by default
./plex/plex_make_seasons /media/tv/ShowName
./plex/plex_move_movie_extras "Movie (2023).mkv" "Extras"

# Override when you want to preview
./plex/plex_make_years /media/movies --dry-run
```

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
| SABnzbd Tools | ✅ Complete | Python | Full feature set with automation support |
| Plex Media Tools | ✅ Complete | Python | Comprehensive organization suite |
| Plex API Tools | ✅ Complete | Python | Server management capabilities |
| Project Documentation | ✅ Complete | Markdown | Comprehensive and specification-compliant |
| Test Coverage | ✅ Complete | Python | Comprehensive fixture-based testing |

### Configuration Management

This project follows a **self-contained, dependency-free** approach to configuration:

- **Command-line arguments**: Primary configuration method for all tools
- **Environment variables**: Used only for sensitive credentials (API keys, tokens)
- **No configuration files**: Maintains portability and zero-dependency principle
- **Embedded defaults**: All configuration options built into each script

**Sensitive Data Handling:**
```bash
# Use .env file for API credentials only (not tracked in git)
export PLEX_TOKEN="your-token-here"
export PLEX_URL="http://your-server:32400"

# All other configuration via command-line arguments
./plex_server_episode_refresh --library "TV Shows" --verbose
```

### Future enhancements
- **Batch processing**: Process multiple directories efficiently
- **Self-testing**: Built-in `--test` modes for validation
- **Enhanced portability**: Even better cross-platform compatibility
- **Extended automation**: More cron-friendly features and scheduling options

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

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Share

[![Twitter](https://img.shields.io/badge/X-Tweet-blue)](https://twitter.com/intent/tweet?text=Check%20out%20this%20awesome%20project!&url=https://github.com/samestrin/media-library-tools) [![Facebook](https://img.shields.io/badge/Facebook-Share-blue)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/samestrin/media-library-tools) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Share-blue)](https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/samestrin/media-library-tools)

---

**Note**: This project prioritizes **safety and data integrity**. All tools are designed to be conservative and require explicit user confirmation for destructive operations. _Always **backup** your media libraries before running bulk operations._
