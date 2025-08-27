# Plex TV Show Year Updater

A Python tool for updating TV show directory names with correct release years using the TVDB (The TV Database) API. This tool scans TV show directories, looks up accurate first air date information, and renames directories to follow the standardized "Show Title (YEAR)" format.

## Overview

The Plex TV Show Year Updater addresses a common issue in media library management where TV show directories may have incorrect years, missing years, or inconsistent naming formats. By leveraging the TVDB API, this tool ensures your TV show directories reflect accurate release year information, improving organization and media server recognition.

## Features

- **TVDB API Integration**: Uses TVDB v4 API for accurate show year information
- **Intelligent Year Detection**: Recognizes existing years in various formats (parentheses, brackets, separators)
- **Safe Operation**: Defaults to dry-run mode with comprehensive preview functionality
- **Flexible Authentication**: Supports API key via CLI argument, environment variable, or .env file
- **File Locking**: Prevents concurrent executions with automatic lock management
- **Non-Interactive Support**: Cron-friendly with automatic environment detection
- **Progress Tracking**: Shows detailed progress and statistics during processing
- **Error Handling**: Robust error handling for API failures and file system issues
- **Comprehensive Logging**: Verbose and debug modes for detailed operation insight

## Prerequisites

- Python 3.7 or higher
- TVDB API key (free registration at thetvdb.com)
- No external dependencies (uses only Python standard library)

## Installation

1. Download the script:
```bash
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/plex/plex_update_tv_years
chmod +x plex_update_tv_years
```

2. Or clone the entire repository:
```bash
git clone https://github.com/samestrin/media-library-tools.git
cd media-library-tools/plex
chmod +x plex_update_tv_years
```

## TVDB API Key Setup

### Getting Your API Key

1. Visit [thetvdb.com](https://thetvdb.com) and create a free account
2. Navigate to your account dashboard
3. Generate an API key under the API section
4. Copy the API key for use with this tool

### Providing the API Key

The tool supports three methods for providing your TVDB API key (in order of precedence):

**Method 1: Command Line Argument (Highest Priority)**
```bash
./plex_update_tv_years /path/to/tv/shows --tvdb-key YOUR_API_KEY_HERE
```

**Method 2: Environment Variable**
```bash
export TVDB_API_KEY="YOUR_API_KEY_HERE"
./plex_update_tv_years /path/to/tv/shows
```

**Method 3: .env File (Lowest Priority)**
Create a `.env` file in the same directory as the script:
```bash
echo "TVDB_API_KEY=YOUR_API_KEY_HERE" > .env
./plex_update_tv_years /path/to/tv/shows
```

## Usage

### Basic Usage

**Dry Run (Default - Safe Mode)**
```bash
./plex_update_tv_years /path/to/tv/shows
```

**Execute Mode (Make Actual Changes)**
```bash
./plex_update_tv_years /path/to/tv/shows --execute
```

### Command Line Options

```
Usage: plex_update_tv_years [OPTIONS] [PATH]

Arguments:
  PATH                  Directory containing TV show subdirectories (default: current directory)

Options:
  --tvdb-key KEY       TVDB API key (can also use TVDB_API_KEY env var or .env file)
  --dry-run            Show what would be renamed without making changes (default: true)
  --execute            Actually perform the renaming operations (overrides --dry-run)
  -y, --yes            Skip confirmation prompts (for non-interactive use)
  --force              Force execution even if another instance is running
  --verbose, -v        Show verbose output with detailed processing information
  --debug              Show detailed debug output including API calls
  --version            Show version number and exit
  -h, --help           Show help message and exit
```

### Examples

**Basic dry run to preview changes:**
```bash
./plex_update_tv_years /media/tv-shows
```

**Execute changes with verbose output:**
```bash
./plex_update_tv_years /media/tv-shows --execute --verbose
```

**Non-interactive execution for automation:**
```bash
./plex_update_tv_years /media/tv-shows --execute -y
```

**Debug API interactions:**
```bash
./plex_update_tv_years /media/tv-shows --debug --tvdb-key YOUR_KEY
```

## Supported Directory Name Formats

The tool recognizes and processes various year formats in directory names:

### Input Formats (Recognized)
- `Show Title (2020)` - Parentheses format
- `Show Title [2020]` - Brackets format  
- `Show Title.2020.` - Dot separated
- `Show Title 2020` - Space separated
- `Show Title-2020-` - Dash separated
- `Show Title_2020_` - Underscore separated
- `Show Title.2020` - Dot ending
- `Show Title-2020` - Dash ending
- `2020.Show Title` - Year prefix formats
- `Show Title` - No year (will add year)

### Output Format (Standardized)
All directories are renamed to the standardized format:
```
Show Title (YEAR)
```

## Operation Modes

### Dry-Run Mode (Default)
- **Default behavior**: All operations run in preview mode
- **No changes made**: Directory structure remains unchanged
- **Full preview**: Shows exactly what changes would be made
- **Statistics**: Provides complete statistics as if changes were made
- **Safety**: Perfect for testing and validation

### Execute Mode
- **Actual changes**: Renames directories according to TVDB data
- **Confirmation**: Interactive confirmation unless `-y` flag is used
- **Progress tracking**: Shows real-time progress during operations
- **Error handling**: Continues processing other directories if individual failures occur

## Automation and Cron Usage

The tool includes comprehensive support for automated execution:

### Non-Interactive Detection
Automatically detects non-interactive environments:
- Cron jobs (no TTY)
- CI/CD pipelines (CI environment variables)
- Automated scripts (AUTOMATED, NON_INTERACTIVE variables)

### Cron Examples

**Daily execution at 3 AM:**
```bash
0 3 * * * /usr/local/bin/plex_update_tv_years /media/tv-shows --execute -y
```

**Weekly execution on Sundays at 2 AM:**
```bash
0 2 * * 0 /usr/local/bin/plex_update_tv_years /media/tv-shows --execute -y
```

**With environment variable API key:**
```bash
0 3 * * * TVDB_API_KEY="your_key" /usr/local/bin/plex_update_tv_years /media/tv-shows --execute -y
```

### Logging for Automation

For automated runs, consider redirecting output:
```bash
0 3 * * * /usr/local/bin/plex_update_tv_years /media/tv-shows --execute -y >> /var/log/plex_update_tv_years.log 2>&1
```

## File Locking and Concurrent Execution

### Automatic Locking
- **Prevents overlaps**: Multiple instances cannot run simultaneously
- **Process tracking**: Lock files include process ID and timestamp
- **Automatic cleanup**: Locks are automatically released on completion
- **Force override**: Use `--force` to bypass lock protection (use carefully)

### Lock File Location
Lock files are created in the system temporary directory:
```bash
/tmp/plex_update_tv_years_<PID>.lock
```

## Error Handling

### API Errors
- **Authentication failures**: Clear messages for invalid API keys
- **Rate limiting**: Automatic handling with respectful delays
- **Network issues**: Graceful degradation and retry logic
- **Show not found**: Continues processing other directories

### File System Errors
- **Permission issues**: Clear error messages and suggestions
- **Directory conflicts**: Detection and prevention of naming conflicts  
- **Path validation**: Comprehensive path existence and access checking

### Recovery Strategies
- **Individual failures**: Single directory failures don't stop overall processing
- **Partial completion**: Statistics show exactly what was accomplished
- **Resume capability**: Safe to re-run on partially processed libraries

## Performance Considerations

### API Rate Limiting
- **Built-in delays**: Automatic 0.5-second delays between API calls
- **Respectful usage**: Designed to stay well within TVDB rate limits
- **Batch processing**: Efficient processing of large libraries

### Large Libraries
- **Memory efficient**: Processes directories one at a time
- **Progress reporting**: Regular progress updates for long-running operations
- **Interrupt handling**: Graceful handling of Ctrl+C interruptions

## Troubleshooting

### Common Issues

**ERROR: TVDB_API_KEY not found**
- Ensure your API key is provided via CLI, environment, or .env file
- Verify the API key is correct and active
- Check for extra spaces or quotes in the key

**ERROR: No TVDB results found**
- Some shows may not be in TVDB database
- Try different variations of the show name
- Check the show exists on thetvdb.com website

**ERROR: Another instance is running**
- Wait for the previous instance to complete
- Check for stale lock files in /tmp/
- Use `--force` flag if necessary (be cautious)

**ERROR: Permission denied**
- Ensure you have write access to the TV shows directory
- Check file system permissions
- Verify the script has execute permissions

### Debug Mode

For detailed troubleshooting, use debug mode:
```bash
./plex_update_tv_years /path/to/tv/shows --debug --verbose
```

This provides:
- Detailed API request/response information
- File system operation details
- Lock acquisition and release logging
- Credential source detection details

### Getting Help

If you encounter issues:
1. Run with `--debug --verbose` flags for detailed output
2. Check the [GitHub Issues](https://github.com/samestrin/media-library-tools/issues) page
3. Create a new issue with debug output and system information

## Statistics and Reporting

The tool provides comprehensive statistics after each run:

```
✨ Processing complete!
📊 Statistics:
   📁 Directories processed: 45
   🔄 Directories renamed: 12
   ⏭️ Directories skipped: 8
   🌐 API errors: 2
   💾 File errors: 0
```

### Statistic Definitions
- **Processed**: Total directories analyzed
- **Renamed**: Directories successfully renamed (or would be in dry-run)
- **Skipped**: Directories already correctly named
- **API errors**: TVDB lookup failures
- **File errors**: File system operation failures

## Security Considerations

### API Key Protection
- **Never logged**: API keys are never written to logs or output
- **Memory only**: Keys are only stored in memory during execution
- **Process isolation**: Each execution uses independent credential handling

### File System Safety
- **Preview first**: Dry-run mode prevents accidental changes
- **Confirmation prompts**: Interactive confirmation for destructive operations
- **Atomic operations**: Directory renames are atomic operations
- **Rollback**: Operations can be manually reversed if needed

## Integration with Plex Media Server

### Best Practices
1. **Stop Plex**: Stop Plex Media Server before running the tool
2. **Backup**: Always backup your media library configuration
3. **Scan after**: Force a library scan after renaming directories
4. **Monitor**: Check Plex logs for any recognition issues

### Plex Library Refresh
After running the tool, refresh your TV Shows library in Plex:
1. Go to Settings > Manage Libraries
2. Select your TV Shows library
3. Click "Scan Library Files"

## Version History

- **v1.0**: Initial release with core TVDB integration and directory renaming functionality

## License

This tool is part of the Media Library Tools project and is released under the MIT License.

## Contributing

Contributions are welcome! Please see the main repository for contribution guidelines:
https://github.com/samestrin/media-library-tools

## Support

For support, feature requests, or bug reports:
- GitHub Issues: https://github.com/samestrin/media-library-tools/issues
- Documentation: https://github.com/samestrin/media-library-tools/tree/main/plex/docs