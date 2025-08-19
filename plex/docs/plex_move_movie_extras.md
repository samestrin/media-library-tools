# Plex Movie Extras Organizer

Self-contained Python tool for organizing movie extras (featurettes, deleted scenes, etc.) according to Plex naming conventions. This script moves and renames extra files from subdirectories into the main movie directory with proper Plex-compatible naming.

## Overview

This tool automates the organization of movie extras to match Plex Media Server's naming conventions. It processes video files in subdirectories and moves them to the main movie directory with proper featurette naming.

## Features

- **Self-contained**: Single Python script using only standard library modules
- **Zero installation**: Download, make executable, and run immediately
- **Automatic extra detection**: Identifies and processes video files in subdirectories
- **Plex-compatible naming**: Renames files following Plex featurette conventions
- **Safe operations**: Dry-run mode, file locking, and comprehensive error handling
- **Directory cleanup**: Removes empty subdirectories after moving files

## Installation

No installation required. Download the script and make it executable:

```bash
# Download and make executable
curl -O https://raw.githubusercontent.com/your-repo/media-library-tools/main/plex/plex_move_movie_extras.py
chmod +x plex_move_movie_extras.py

# Run immediately
./plex_move_movie_extras.py --help
```

## Usage

### Basic usage
```bash
# Preview changes (dry-run)
./plex_move_movie_extras "Movie (2023).mkv" "Featurettes" --dry-run

# Move extras with confirmation
./plex_move_movie_extras "Movie (2023).mkv" "Deleted Scenes"

# Move extras without confirmation (automation)
./plex_move_movie_extras "Movie (2023).mkv" "Behind the Scenes" -y
```

## Command-line options

| Option | Description |
|--------|-------------|
| `main_file` | Main movie file path (required) |
| `sub_dir` | Subdirectory name containing extras (required) |
| `--dry-run` | Preview changes without making modifications |
| `-y, --yes` | Skip confirmation prompts (useful for automation) |
| `--force` | Force execution even if another instance is running |
| `--verbose` | Enable verbose output for debugging |
| `--debug` | Enable debug output (implies --verbose) |
| `--version` | Display version information |
| `--help` | Show help message and exit |

## Examples

**Basic organization**
```bash
# Featurettes organization
./plex_move_movie_extras "Avatar (2009).mkv" "Featurettes"

# Deleted scenes organization
./plex_move_movie_extras "Inception (2010).mkv" "Deleted Scenes"
```

**Directory structure transformation**

Before:
```
/Movies/Movie (2023)/
├── Movie (2023).mkv
└── Featurettes/
    ├── Behind the Scenes.mkv
    └── Making Of.mp4
```

After:
```
/Movies/Movie (2023)/
├── Movie (2023).mkv
├── Movie (2023)-featurette01.mkv
└── Movie (2023)-featurette02.mp4
```

**Automation examples**
```bash
# Skip confirmation prompts
./plex_move_movie_extras "Movie.mkv" "Extras" -y

# Verbose output for debugging
./plex_move_movie_extras "Movie.mkv" "Extras" --verbose
```

**Naming conventions**
- Single file: `MovieName-featurette.ext`
- Multiple files: `MovieName-featurette01.ext`, `MovieName-featurette02.ext`, etc.
- Supported formats: .mkv, .mp4, .avi, .mov, .m4v (and all other file types)

## Safety features

The tool implements comprehensive safety measures:

- **File locking**: Prevents concurrent executions with automatic cleanup
- **Dry-run mode**: Preview all changes before execution
- **File validation**: Ensures main file and subdirectory exist before processing
- **Error handling**: Graceful handling of permission and file system errors
- **Directory cleanup**: Only removes subdirectories if completely empty

## Troubleshooting

**Common issues**

- "Another instance is already running": Use `--force` flag to override or check for stale lock files
- "Main file does not exist": Verify the main movie file path is correct
- "Subdirectory does not exist": Check subdirectory name and permissions
- "Permission denied": Ensure write permissions to target directory

**Debug information**

```bash
# Check what would be processed
./plex_move_movie_extras "Movie.mkv" "Extras" --dry-run --verbose

# Check file and directory permissions
ls -la "/path/to/Movie.mkv"
```

## Technical details

**Implementation**
- Python 3.6+ with standard library only
- File locking for concurrent execution prevention
- Safe operations (moves/renames only, never deletes)
- Path validation prevents directory traversal

**Dependencies**
- Python standard library modules only
- Cross-platform compatibility (macOS, Linux, Windows)
- No external package requirements

**Performance**
- Memory efficient processing
- Direct file operations without content analysis
- Minimal I/O overhead