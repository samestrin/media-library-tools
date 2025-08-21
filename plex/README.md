# Plex Media Organization Tools

Utilities for organizing and maintaining media libraries optimized for Plex Media Server.

## Overview

This directory contains self-contained Python tools designed to help you organize your media files according to Plex's naming conventions and directory structures. The tools ensure optimal recognition and metadata matching for your Plex Media Server.

## Features

- **Plex-compatible naming**: Enforces Plex naming conventions for movies and TV shows
- **Safe preview modes**: Dry-run capabilities to test operations before making changes
- **Batch processing**: Handle multiple files and directories efficiently
- **Directory organization**: Create proper folder hierarchies for media libraries
- **Movie extras handling**: Organize trailers, behind-the-scenes, and other extras
- **TV show organization**: Automatic season directory creation and episode organization
- **Self-contained**: Python tools use only standard library modules

## Installation

These tools require Python 3.6+ and use only standard library modules.

```bash
# Make scripts executable
chmod +x plex_*

# Run tools directly
./plex_move_movie_extras --help
./plex_make_seasons --help
./plex_correct_dirs --help
```

## Available Tools

### Directory Organization Tools

#### `plex_make_dirs` (Python)
Creates proper directory structures for media libraries.
- Organizes media files into appropriate folder hierarchies
- Ensures Plex-compatible directory naming
- Safe preview mode with comprehensive validation
- Automation-friendly with `-y` flag support

**Documentation**: [docs/plex_make_dirs.md](docs/plex_make_dirs.md)

#### `plex_correct_dirs` (Python)
Sanitizes and corrects directory names for Plex compatibility.
- Removes unwanted release group tags (YTS, RARBG, YIFY, etc.)
- Properly formats resolutions (1080p, 2160p) in brackets
- Encloses years in parentheses (2023)
- Converts [4K] tags to [2160p]
- Removes video source tags (BluRay, WEBRip, etc.)
- Cleans up audio format tags (5.1, DTS, AC3, etc.)

**Documentation**: [docs/plex_correct_dirs.md](docs/plex_correct_dirs.md)

### TV Show Organization

#### `plex_make_seasons` (Python)
Organizes TV show episodes into proper season directories.
- Detects episode patterns (S01E01, etc.)
- Creates season folders automatically
- Moves episodes to appropriate season directories
- Comprehensive safety features and dry-run mode
- Automation support with file locking

**Documentation**: [docs/plex_make_seasons.md](docs/plex_make_seasons.md)

#### `plex_make_all_seasons` (Python)
Batch processes multiple TV shows for season organization.
- Processes entire directories of TV shows
- Applies season organization across multiple series
- Progress indicators and concurrent processing
- Built-in error recovery and reporting

**Documentation**: [docs/plex_make_all_seasons.md](docs/plex_make_all_seasons.md)

### Year-Based Organization

#### `plex_make_years` (Python)
Organizes movies into year-based directory structures.
- Creates year folders (2020, 2021, etc.)
- Moves movies to appropriate year directories
- Extracts year information from filenames
- Safe preview mode and automation support

**Documentation**: [docs/plex_make_years.md](docs/plex_make_years.md)

### Movie Organization

#### `plex_move_movie_extras` (Python)

Moves and renames movie extras (featurettes, deleted scenes, etc.) from subdirectories into the main movie directory following Plex naming conventions.
- **Automatic extra detection**: Identifies and processes video files in subdirectories
- **Plex-compatible naming**: Renames files following Plex featurette conventions
- **Sequential numbering**: Handles multiple files with proper numbering (01, 02, etc.)
- **Directory cleanup**: Removes empty subdirectories after moving files
- **Automation-friendly**: Designed for automated scheduling with `-y` flag
- **File locking**: Prevents multiple instances from running simultaneously

**Documentation**: [docs/plex_move_movie_extras.md](docs/plex_move_movie_extras.md)

#### `plex_movie_subdir_renamer` (Python)

Renames movie featurettes and extras within subdirectories according to Plex naming conventions with intelligent categorization.
- **Intelligent categorization**: Automatically categorizes files based on filename patterns
- **Plex-compatible naming**: Renames files following Plex featurette conventions
- **Pattern recognition**: Identifies trailers, behind-the-scenes, deleted scenes, and more
- **Movie name detection**: Auto-detects movie names from directory paths
- **Automation-friendly**: Designed for automated scheduling with `-y` flag
- **File locking**: Prevents multiple instances from running simultaneously

**Documentation**: [docs/plex_movie_subdir_renamer.md](docs/plex_movie_subdir_renamer.md)

## Usage

### Movie extras organization
```bash
# Preview changes (dry-run)
./plex_move_movie_extras "Movie (2023).mkv" "Featurettes" --dry-run

# Move extras with confirmation
./plex_move_movie_extras "Movie (2023).mkv" "Deleted Scenes"

# Automation mode (no confirmation)
./plex_move_movie_extras "Movie (2023).mkv" "Behind the Scenes" -y
```

### Movie subdirectory renaming
```bash
# Preview changes (dry-run, default)
./plex_movie_subdir_renamer "/Movies/Avatar (2009)/Featurettes"

# Execute renaming with confirmation
./plex_movie_subdir_renamer "/Movies/Avatar (2009)/Featurettes" --execute

# Automation mode (no confirmation)
./plex_movie_subdir_renamer "/Movies/Avatar (2009)/Featurettes" --execute -y
```

### TV show organization
```bash
# Create season directories
./plex_make_seasons /path/to/tv/show --dry-run

# Process multiple shows
./plex_make_all_seasons /path/to/tv/library
```

### Directory organization
```bash
# Fix naming issues
./plex_correct_dirs /path/to/downloads

# Organize into proper structure
./plex_make_dirs /path/to/downloads
```

### Complete movie library setup
```bash
# 1. Correct directory names
./plex_correct_dirs /path/to/movies

# 2. Organize by year (optional)
./plex_make_years /path/to/movies

# 3. Organize movie extras
./plex_move_movie_extras "Movie (2023).mkv" "Featurettes" --dry-run
./plex_movie_subdir_renamer "/Movies/Movie (2023)/Extras" --dry-run

# 4. Execute after reviewing dry-run results
./plex_move_movie_extras "Movie (2023).mkv" "Featurettes" -y
./plex_movie_subdir_renamer "/Movies/Movie (2023)/Extras" --execute -y
```

## Output format

These tools help enforce Plex's recommended naming conventions:

### Movies
```
Movies/
├── Movie Name (2023)/
│   ├── Movie Name (2023) [1080p].mkv
│   ├── Movie Name (2023) - Trailer-trailer.mkv
│   └── Movie Name (2023) - Behind the Scenes-behindthescenes.mkv
```

### TV Shows
```
TV Shows/
├── Show Name (2020)/
│   ├── Season 01/
│   │   ├── Show Name - S01E01 - Episode Title.mkv
│   │   └── Show Name - S01E02 - Episode Title.mkv
│   └── Season 02/
│       └── Show Name - S02E01 - Episode Title.mkv
```

## Safety features

- **Dry-run modes**: Test operations before making changes
- **Lock files**: Prevent multiple instances from running simultaneously
- **Backup recommendations**: Always backup your media before bulk operations
- **Permission handling**: Graceful handling of permission issues

## Technical Details

### Self-Contained Python Tools
All Plex tools are complete Python implementations using only standard library modules:

- **Zero dependencies**: No external libraries required
- **Portable execution**: Download and run anywhere with Python 3.6+
- **Consistent interface**: Standardized CLI arguments across all tools
- **Enhanced safety**: Comprehensive dry-run modes and validation
- **Automation ready**: Built-in support for cron jobs and scripting

### Standard Features
All tools include these standard features:

- **Safe defaults**: Preview mode by default, require explicit execution
- **Comprehensive options**: `--verbose`, `--debug`, `--dry-run`/`--execute` flags
- **Progress indicators**: Visual feedback for large operations
- **Error recovery**: Graceful handling of permission and file system errors
- **File locking**: Prevents concurrent execution conflicts
- **Automation support**: `-y` flag for non-interactive operation
- **Non-interactive detection**: Automatic cron-friendly behavior

## Troubleshooting

### Permission issues
```bash
# Check file permissions
ls -la /path/to/media

# Run with appropriate user
sudo -u plex ./script_name
```

### Special characters
- Tools handle most special characters automatically
- Some characters may need manual review
- Use dry-run mode to preview changes

### Large libraries
- Process in smaller batches for very large libraries
- Monitor disk space during reorganization
- Consider using screen/tmux for long-running operations

## Documentation

### Tool-Specific Documentation
- [docs/plex_correct_dirs.md](docs/plex_correct_dirs.md) - Directory name sanitization
- [docs/plex_make_dirs.md](docs/plex_make_dirs.md) - Directory structure creation  
- [docs/plex_make_seasons.md](docs/plex_make_seasons.md) - TV show season organization
- [docs/plex_make_all_seasons.md](docs/plex_make_all_seasons.md) - Batch season processing
- [docs/plex_make_years.md](docs/plex_make_years.md) - Year-based movie organization
- [docs/plex_move_movie_extras.md](docs/plex_move_movie_extras.md) - Movie extras organization
- [docs/plex_movie_subdir_renamer.md](docs/plex_movie_subdir_renamer.md) - Movie subdirectory renaming

## Resources

- [Plex Naming Conventions](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/)
- [Plex TV Show Naming](https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/)
- [Plex Movie Extras](https://support.plex.tv/articles/local-files-for-trailers-and-extras/)