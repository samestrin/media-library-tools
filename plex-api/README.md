# Plex API Tools

Self-contained Python tools for interacting with the Plex Media Server API to manage and maintain your media library.

## Overview

This collection provides API-based tools for Plex Media Server management, focusing on maintenance operations that require server interaction. Each tool is a standalone Python script using only standard library modules.

## Features

- **API-based operations**: Direct interaction with Plex Media Server API
- **Flexible authentication**: Support for tokens, environment variables, and .env files
- **Remote server support**: Works with both local and remote Plex servers
- **Safe operations**: Read-only and refresh operations without file manipulation
- **Self-contained**: No external dependencies, uses only Python standard library
- **Zero installation**: Download, make executable, and run immediately

## Tools

### `plex_server_episode_refresh`
Force regeneration of episode thumbnails in Plex Media Server.

- Refreshes episode thumbnails using Plex API
- Handles authentication via token, environment variables, or .env file
- Works with local or remote Plex servers
- Safe operation without moving or deleting video files

**Documentation:** [docs/plex_server_episode_refresh.md](docs/plex_server_episode_refresh.md)

## Installation

All tools are self-contained Python scripts requiring no external dependencies:

```bash
# Download and make executable
chmod +x plex_server_episode_refresh

# Run directly
./plex_server_episode_refresh --help
```

## Usage

### Basic usage
```bash
# Refresh episode thumbnails using episode ID
./plex_server_episode_refresh 12345 --server http://localhost:32400 --token YOUR_TOKEN

# Use environment variable for token
PLEX_TOKEN=YOUR_TOKEN ./plex_server_episode_refresh 12345 --server http://localhost:32400

# Show verbose output
./plex_server_episode_refresh 12345 --verbose

# Show debug information
./plex_server_episode_refresh 12345 --debug
```

### Authentication

Tools require a Plex authentication token, provided via:

1. Command line argument: `--token YOUR_TOKEN`
2. Environment variable: `PLEX_TOKEN=YOUR_TOKEN`
3. .env file: `PLEX_TOKEN=YOUR_TOKEN`

## Safety features

- **Read-only operations**: Tools only read from or refresh the Plex server
- **Authentication validation**: Checks for valid tokens before processing
- **Error handling**: Graceful handling of API errors and network issues
- **Non-destructive**: No file system modifications, only API calls

## Technical Details

- **Python version**: 3.6 or higher
- **Dependencies**: Standard library only
- **Platform**: Cross-platform (Linux, macOS, Windows)
- **Network**: Requires HTTP(S) access to Plex Media Server

## Troubleshooting

### Authentication issues
- Verify your Plex token is valid and has appropriate permissions
- Check that the server URL is accessible from your machine
- Ensure the Plex Media Server is running and responsive

### Network connectivity
- Test server accessibility: `curl http://your-plex-server:32400/identity`
- Check firewall settings if using remote server
- Verify port forwarding configuration for external access

### API errors
- Use `--debug` flag to see detailed API communication
- Check Plex server logs for additional error information
- Verify episode ID exists and is accessible

## Documentation

- [docs/plex_server_episode_refresh.md](docs/plex_server_episode_refresh.md) - Episode thumbnail refresh tool

## Version History

- **v1.0**: Initial release with episode thumbnail refresh functionality