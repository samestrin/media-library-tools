# Plex Server Episode Refresh Tool

## Overview

Forces Plex Media Server to regenerate thumbnails for specific episodes. This server management tool uses the Plex API to refresh episode metadata and thumbnails, useful when episode thumbnails are corrupted, missing, or need updating after metadata changes.

## Features

- **Force thumbnail regeneration**: Refresh specific episodes using their rating key (ID)
- **Multiple token sources**: CLI argument, environment variables, local `.env`, or global `~/.media-library-tool/.env` file
- **Flexible server configuration**: Supports custom Plex server URLs and hostnames
- **Comprehensive logging**: Verbose and debug modes for troubleshooting
- **Interactive design**: Confirmation prompts with `-y` flag for automation
- **Self-contained**: Uses only Python standard library modules

## Installation

**Direct download**
```bash
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/plex-api/plex_server_episode_refresh
chmod +x plex_server_episode_refresh
```

**Clone repository**
```bash
git clone https://github.com/samestrin/media-library-tools.git
cd media-library-tools/plex-api
chmod +x plex_server_episode_refresh
```

## Configuration

**Plex token setup**

The tool requires a Plex authentication token (in order of priority):

1. Command line argument: `--token YOUR_PLEX_TOKEN`
2. Environment variable: `export PLEX_TOKEN="YOUR_PLEX_TOKEN"`
3. Local `.env` file: `echo "PLEX_TOKEN=YOUR_PLEX_TOKEN" > .env`
4. Global `.env` file: `mkdir -p ~/.media-library-tool && echo "PLEX_TOKEN=YOUR_PLEX_TOKEN" > ~/.media-library-tool/.env`

**Plex server setup**

The tool requires a Plex server URL (in order of priority):

1. Command line argument: `--server http://plex.local:32400`
2. Environment variable: `export PLEX_SERVER="http://plex.local:32400"`
3. Local `.env` file: `echo "PLEX_SERVER=http://plex.local:32400" >> .env`
4. Global `.env` file: `echo "PLEX_SERVER=http://plex.local:32400" >> ~/.media-library-tool/.env`
5. Default fallback: `http://localhost:32400`

The global `.env` file at `~/.media-library-tool/.env` can be shared across all media library tools that support credential handling.

**Finding your Plex token**

1. Log into your Plex Web App
2. Open browser developer tools (F12)
3. Go to Network tab and refresh the page
4. Look for requests containing `X-Plex-Token` in the headers
5. Copy the token value

Alternatively, visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

**Finding episode rating keys**

To find an episode's rating key (ID):

1. **Via Plex Web Interface**: Navigate to the episode and look at the URL for the number after `/metadata/`
2. **Via Plex API**: Use `curl -X GET "http://localhost:32400/library/sections/1/all?X-Plex-Token=YOUR_TOKEN" | grep -o 'ratingKey="[0-9]*"'`

## Usage

**Basic usage**

```bash
# Refresh episode with ID 12345 (uses localhost:32400 by default)
./plex_server_episode_refresh 12345

# Refresh with verbose output
./plex_server_episode_refresh 12345 --verbose

# Use specific token and server
./plex_server_episode_refresh 12345 --token YOUR_TOKEN --server http://plex.local:32400

# Debug mode for troubleshooting
./plex_server_episode_refresh 12345 --debug
```

## Command-line options

| Option | Description |
|--------|-------------|
| `episode_hash` | Episode rating key (ID) from Plex (required) |
| `--token TOKEN, -t` | Plex authentication token (overrides environment/file) |
| `--server SERVER, -s` | Plex server URL (overrides environment/file, default: localhost:32400) |
| `--verbose, -v` | Show verbose output |
| `--debug` | Show detailed debug output |
| `--version` | Show program's version number and exit |
| `--help, -h` | Show help message and exit |

## Examples

**Basic episode refresh**
```bash
$ ./plex_server_episode_refresh 12345
Plex Server Episode Refresh Tool v2.0
==================================================
✓ Successfully refreshed episode image for rating key: 12345
```

**Verbose output with custom server**
```bash
$ ./plex_server_episode_refresh 12345 --server http://plex.local:32400 --verbose
Plex Server Episode Refresh Tool v2.0
==================================================
Refreshing episode image for rating key: 12345
Show: Breaking Bad
Season: 1, Episode: 1
Title: Pilot
✓ Successfully refreshed episode image for rating key: 12345
```

**Batch processing script**
```bash
#!/bin/bash
# refresh_episodes.sh

EPISODES=("12345" "67890" "11111" "22222")
SERVER="http://plex.local:32400"  # Optional: set custom server

for episode in "${EPISODES[@]}"; do
    echo "Refreshing episode: $episode"
    /usr/local/bin/plex_server_episode_refresh "$episode" --server "$SERVER" --verbose -y
    sleep 2  # Brief pause between requests
done
```

## Troubleshooting

**Common issues**

- "Configuration Error: No Plex token found": Provide a Plex token via `--token`, `PLEX_TOKEN` environment variable, or `.env` file
- "HTTP Error 401: Unauthorized": Invalid or expired Plex token - verify token is correct and has proper permissions
- "HTTP Error 404: Not Found": Invalid episode rating key or server URL - verify the episode exists in your Plex library
- "Connection refused": Plex server is not running or unreachable - verify server is running and network connectivity

**Debug mode**

Use `--debug` flag for detailed troubleshooting:

```bash
./plex_episode_image_refresh 12345 --debug
```

This shows token source, server URL, request URLs, HTTP response codes, and detailed error information.

## Technical details

**Implementation**
- Pure Python using only standard library modules
- HTTP requests via urllib for Plex API communication
- Environment variable and .env file support
- Cross-platform compatibility (Windows, macOS, Linux)

**Dependencies**
- Python 3.6+ (uses f-strings and pathlib)
- No external packages required
- Self-contained single-file script

**Performance**
- Lightweight refresh operations with minimal server impact
- Rate limiting recommended for batch operations
- Local network operations preferred for best performance

**Security considerations**
- Never commit tokens to version control
- Use environment variables or secure config files
- Rotate tokens regularly and limit scope to necessary permissions
- Run with minimal required privileges

**Integration examples**

Cron job for automated refreshes:
```bash
# Refresh specific episodes daily at 3 AM
0 3 * * * /usr/local/bin/plex_server_episode_refresh 12345 -y >> /var/log/plex_refresh.log 2>&1
```

Python integration:
```python
import subprocess

def refresh_episode(rating_key, server=None, token=None):
    cmd = ['/usr/local/bin/plex_server_episode_refresh', str(rating_key), '-y']
    if server:
        cmd.extend(['--server', server])
    if token:
        cmd.extend(['--token', token])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
```

## Version History

- **v1.1:** Enhanced CLI with standard arguments, multiple token sources, improved logging
- **v1.0:** Initial release with basic episode refresh functionality

## Related Tools

- [`plex_move_movie_extras`](plex_move_movie_extras.md) - Organize movie extras and bonus content
- [`plex_movie_subdir_renamer`](plex_movie_subdir_renamer.md) - Rename movie extras within subdirectories
- [Main Project README](../README.md) - Complete media library tools overview

## Support

For issues, feature requests, or contributions:
- GitHub Issues: [Project Issues](https://github.com/samestrin/media-library-tools/issues)
- Documentation: [Project Wiki](https://github.com/samestrin/media-library-tools/wiki)
- Discussions: [GitHub Discussions](https://github.com/samestrin/media-library-tools/discussions)

## License

This tool is part of the Media Library Tools project and is released under the MIT License. See the main project LICENSE file for details.