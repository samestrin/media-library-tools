# Plex Movie Subdirectory Renamer

## Overview

Renames movie featurettes and extras in subdirectories according to Plex naming conventions. Automatically categorizes and renames video files within movie subdirectories to ensure proper recognition by Plex Media Server.

## Features

- **Intelligent categorization**: Automatically categorizes files based on filename patterns
- **Plex-compatible naming**: Renames files following Plex featurette conventions
- **Sequential numbering**: Handles multiple files with proper numbering (01, 02, etc.)
- **Pattern recognition**: Identifies trailers, behind-the-scenes, deleted scenes, and more
- **Safety features**: File locking, dry-run mode, and error handling
- **Self-contained**: Uses only Python standard library modules

## Installation

**Direct download**
```bash
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/plex/plex_movie_subdir_renamer
chmod +x plex_movie_subdir_renamer
```

**Clone repository**
```bash
git clone https://github.com/samestrin/media-library-tools.git
cd media-library-tools/plex
```

## Usage

**Basic usage**
```bash
# Preview changes (dry-run, default)
./plex_movie_subdir_renamer "/Movies/Avatar (2009)/Featurettes"

# Execute renaming with confirmation
./plex_movie_subdir_renamer "/Movies/Avatar (2009)/Featurettes" --execute
```

**Automation**
```bash
# Execute without confirmation (skip prompts)
./plex_movie_subdir_renamer "/Movies/Avatar (2009)/Featurettes" --execute -y

# Daily processing at 3 AM
0 3 * * * /path/to/plex_movie_subdir_renamer "/Movies/*/Featurettes" --execute -y
```

## Command-line options

| Option | Description |
|--------|-------------|
| `directory` | Directory containing movie extras to rename (required) |
| `--movie-name` | Override movie name (auto-detected from path if not provided) |
| `--execute` | Execute the renaming (default is dry-run) |
| `--dry-run` | Preview changes without making modifications (default) |
| `-y, --yes` | Skip confirmation prompts (useful for scripting) |
| `--force` | Force execution even if another instance is running |
| `--no-banner` | Suppress banner display |
| `--verbose` | Enable verbose output for debugging |
| `--debug` | Enable debug output (implies --verbose) |
| `--version` | Display version information |
| `--help` | Show help message and exit |

## Global Configuration Support

The tool respects environment variables for default behavior:

- `AUTO_EXECUTE=true` - Default to execute mode instead of dry-run
- `AUTO_CONFIRM=true` - Skip confirmation prompts automatically
- `QUIET_MODE=true` - Suppress banner display by default

Configuration hierarchy: CLI arguments > Environment variables > Local .env > Global ~/.media-library-tools/.env

## File categorization

**Supported categories**

| Pattern | Category | Example Output |
|---------|----------|----------------|
| trailer, preview | trailer | `Movie-trailer01.mkv` |
| behind.the.scenes, making.of, bts | behindthescenes | `Movie-behindthescenes01.mkv` |
| deleted.scene, cut.scene | deleted | `Movie-deleted01.mkv` |
| interview, cast, director | interview | `Movie-interview01.mkv` |
| featurette, extra, bonus | featurette | `Movie-featurette01.mkv` |
| commentary, audio.commentary | other | `Movie-other01.mkv` |
| gag.reel, blooper, outtake | other | `Movie-other01.mkv` |
| **Default** | featurette | `Movie-featurette01.mkv` |

**Supported file types**
- Video extensions: .mkv, .mp4, .avi, .mov, .m4v, .wmv, .flv, .webm

**Naming convention**
- Single file: `MovieName-category.ext`
- Multiple files: `MovieName-category01.ext`, `MovieName-category02.ext`, etc.
- Title cleaning: Removes special characters and normalizes spacing

## Examples

**Movie name detection**

The script automatically detects movie names from directory paths:
```
/Movies/Avatar (2009)/Featurettes/ → "Avatar (2009)"
/Media/Inception (2010) [1080p]/Extras/ → "Inception (2010) [1080p]"
```

**Manual override**
```bash
# Override auto-detected movie name
./plex_movie_subdir_renamer "/path/to/extras" --movie-name "Custom Movie Name (2023)"
```

**Directory structure transformation**
```
Before:
/Movies/Avatar (2009)/Featurettes/
├── Making of Avatar.mkv
├── Behind the Scenes.mp4
├── Deleted Scene - Extended Ending.mkv
└── Cast Interview.mkv

After:
/Movies/Avatar (2009)/Featurettes/
├── Avatar (2009)-behindthescenes01.mkv  # Making of Avatar
├── Avatar (2009)-behindthescenes02.mp4  # Behind the Scenes
├── Avatar (2009)-deleted01.mkv          # Deleted Scene - Extended Ending
└── Avatar (2009)-interview01.mkv        # Cast Interview
```

## Safety features

The tool implements comprehensive safety measures:

- **File locking**: Prevents concurrent executions with automatic cleanup
- **Dry-run mode**: Safe preview mode by default
- **Directory validation**: Ensures target directory exists and is accessible
- **Error handling**: Graceful handling of permission and file system errors
- **File type validation**: Only processes supported video file formats
- **Non-interactive detection**: Automatic detection for cron/automation environments

## Troubleshooting

**Common issues**

- "Another instance is already running": Use `--force` flag to override or check for stale lock files
- "Directory does not exist": Verify the directory path is correct
- "Not a directory": Ensure the provided path points to a directory, not a file
- "No video files found": Verify the directory contains supported video file formats
- "Permission denied": Ensure write permissions to target directory

## Technical details

**Implementation**
- Python 3.6+ with standard library only
- File locking for concurrent execution prevention
- Efficient regex-based pattern matching
- Safe operations (renames only, never deletes)
- Path validation prevents directory traversal

**Dependencies**
- Python standard library modules only
- Cross-platform compatibility (macOS, Linux, Windows)
- No external package requirements

**Performance**
- Memory efficient processing
- Direct file operations without content analysis
- Secure temporary file creation for locking