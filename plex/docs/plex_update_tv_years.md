# Plex TV Show Year Updater

A Python tool for updating TV show directory names with correct release years using the TVDB (The TV Database) API. This tool scans TV show directories, looks up accurate first air date information, and renames directories to follow the standardized "Show Title (YEAR)" format.

## Overview

The Plex TV Show Year Updater addresses a common issue in media library management where TV show directories may have incorrect years, missing years, or inconsistent naming formats. By leveraging the TVDB API, this tool ensures your TV show directories reflect accurate release year information, improving organization and media server recognition.

## Features

- **TVDB API Integration**: Uses TVDB v4 API for accurate show year information
- **Intelligent Caching**: JSON-based caching with 14-day TTL reduces API calls by 50%+
- **Retry Logic**: Exponential backoff for transient network errors and rate limiting
- **Cache Management**: Complete CLI for cache statistics, refresh, and clearing operations
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

The tool supports four methods for providing your TVDB API key (in order of precedence):

**Method 1: Command Line Argument (Highest Priority)**
```bash
./plex_update_tv_years /path/to/tv/shows --tvdb-key YOUR_API_KEY_HERE
```

**Method 2: Environment Variable**
```bash
export TVDB_API_KEY="YOUR_API_KEY_HERE"
./plex_update_tv_years /path/to/tv/shows
```

**Method 3: Local .env File**
Create a `.env` file in the same directory as the script:
```bash
echo "TVDB_API_KEY=YOUR_API_KEY_HERE" > .env
./plex_update_tv_years /path/to/tv/shows
```

**Method 4: Global .env File (Lowest Priority)**
Create a global configuration file in your home directory:
```bash
mkdir -p ~/.media-library-tool
echo "TVDB_API_KEY=YOUR_API_KEY_HERE" > ~/.media-library-tools/.env
./plex_update_tv_years /path/to/tv/shows
```

This global .env file can be shared across all media library tools that support credential handling.

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
  --tvdb-key KEY       TVDB API key (can also use TVDB_API_KEY env var, local .env, or global ~/.media-library-tools/.env)
  --dry-run            Show what would be renamed without making changes (default: true)
  --execute            Actually perform the renaming operations (overrides --dry-run)
  -y, --yes            Skip confirmation prompts (for non-interactive use)
  --force              Force execution even if another instance is running
  --verbose, -v        Show verbose output with detailed processing information
  --debug              Show detailed debug output including API calls
  
Cache Management:
  --cache-stats        Show cache statistics (hits, misses, size, entries)
  --cache-refresh      Force refresh of cached data during processing
  --cache-clear        Clear all cached data and exit
  --cache-dir DIR      Specify custom cache directory (default: ~/.cache)
  
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

**Cache Management Examples:**
```bash
# Show detailed cache statistics
./plex_update_tv_years --cache-stats

# Force refresh of all cached data during processing
./plex_update_tv_years /media/tv-shows --cache-refresh --execute

# Clear cache with confirmation prompt
./plex_update_tv_years --cache-clear

# Clear cache without confirmation (for automation)
./plex_update_tv_years --cache-clear -y

# Use custom cache directory
./plex_update_tv_years /media/tv-shows --cache-dir /custom/cache/path
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

## Caching System

The tool includes a sophisticated caching system that dramatically improves performance for repeated runs and large libraries.

### Cache Features

- **JSON-Based Storage**: Human-readable cache files in XDG-compliant directory structure
- **14-Day TTL**: Cached results expire after 14 days to ensure freshness
- **Automatic Cleanup**: Expired entries are automatically removed
- **Hit Rate Tracking**: Detailed statistics show cache effectiveness
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Cache Locations

**Default Cache Directory:**
- Linux/macOS: `~/.cache/plex_update_tv_years.json`
- Windows: `%LOCALAPPDATA%/plex_update_tv_years.json`

**Custom Cache Directory:**
Use `--cache-dir` to specify a custom location:
```bash
./plex_update_tv_years --cache-dir /path/to/custom/cache /media/tv-shows
```

### Cache Operations

**View Cache Statistics:**
```bash
./plex_update_tv_years --cache-stats
```

Example output:
```
Cache Statistics:
  Cache file: /home/user/.cache/plex_update_tv_years.json
  Total entries: 45
  Expired entries: 3
  Cache size: 128.5 KB
  Oldest entry: 7.2 days old
  Session hit rate: 78.5% (1,245 hits / 1,587 total requests)
```

**Force Cache Refresh:**
Bypass cache and fetch fresh data from TVDB:
```bash
./plex_update_tv_years --cache-refresh /media/tv-shows --execute
```

**Clear Cache:**
Remove all cached data:
```bash
# With confirmation prompt
./plex_update_tv_years --cache-clear

# Without confirmation (for automation)  
./plex_update_tv_years --cache-clear -y
```

### Performance Benefits

- **50%+ API Call Reduction**: Subsequent runs use cached data for previously looked up shows
- **Faster Processing**: Cached lookups are nearly instantaneous
- **Reduced TVDB Load**: Respectful API usage with intelligent caching
- **Large Library Support**: Efficient processing of libraries with hundreds of shows

### Cache Management Best Practices

1. **Regular Statistics Review**: Use `--cache-stats` to monitor cache effectiveness
2. **Periodic Cache Clearing**: Clear cache monthly or when changing libraries significantly  
3. **Custom Cache Directories**: Use dedicated cache locations for different libraries
4. **Automation-Friendly**: Cache operations work seamlessly with cron jobs

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

### Caching Performance
- **First Run**: Initial run builds cache, normal API call volume
- **Subsequent Runs**: 50%+ reduction in API calls through intelligent caching
- **Cache Hits**: Nearly instantaneous lookups for cached shows
- **Large Libraries**: Dramatic performance improvement for libraries with 100+ shows

### API Rate Limiting and Retry Logic
- **Built-in delays**: Automatic 0.5-second delays between API calls
- **Exponential backoff**: Automatic retry with increasing delays for transient errors
- **Intelligent retry**: Distinguishes between temporary and permanent failures
- **Rate limit handling**: Automatic handling of TVDB rate limiting (HTTP 429)
- **Respectful usage**: Designed to stay well within TVDB rate limits

### Large Libraries
- **Memory efficient**: Processes directories one at a time
- **Progress reporting**: Regular progress updates for long-running operations
- **Interrupt handling**: Graceful handling of Ctrl+C interruptions
- **Scalable caching**: Cache system handles libraries with hundreds of shows efficiently

### Network Resilience
- **Automatic retries**: Transient network errors are automatically retried
- **Jitter prevention**: Random delays prevent thundering herd problems
- **Graceful degradation**: Individual failures don't stop overall processing
- **Statistics tracking**: Detailed retry success rates and cache hit rates

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
Processing complete!
Statistics:
   Directories processed: 45
   Directories renamed: 12
   Directories skipped: 8
   API errors: 2
   File errors: 0
   Cache hits: 28
   Cache misses: 19
   Cache hit rate: 59.6%
   Retry attempts: 3
   Successful retries: 2
   Retry success rate: 66.7%
```

### Statistic Definitions

**Core Processing:**
- **Processed**: Total directories analyzed
- **Renamed**: Directories successfully renamed (or would be in dry-run)
- **Skipped**: Directories already correctly named
- **API errors**: TVDB lookup failures
- **File errors**: File system operation failures

**Caching Statistics:**
- **Cache hits**: Number of TVDB lookups served from cache
- **Cache misses**: Number of TVDB lookups requiring API calls
- **Cache hit rate**: Percentage of requests served from cache

**Retry Statistics:**
- **Retry attempts**: Total number of retry operations performed
- **Successful retries**: Number of retries that eventually succeeded
- **Retry success rate**: Percentage of retry attempts that were successful

### Performance Metrics

The statistics help you understand:
- **Cache effectiveness**: Higher hit rates indicate better performance
- **Network reliability**: Lower retry rates suggest stable network conditions  
- **Processing efficiency**: Balanced statistics indicate optimal operation

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
- **v1.0 Sprint 8.0 Enhancements**: Added comprehensive caching system with 14-day TTL, exponential backoff retry logic, cache management CLI options, and detailed statistics tracking. Provides 50%+ API call reduction and improved network resilience.

## License

This tool is part of the Media Library Tools project and is released under the MIT License.

## Contributing

Contributions are welcome! Please see the main repository for contribution guidelines:
https://github.com/samestrin/media-library-tools

## Support

For support, feature requests, or bug reports:
- GitHub Issues: https://github.com/samestrin/media-library-tools/issues
- Documentation: https://github.com/samestrin/media-library-tools/tree/main/plex/docs