# Test Fixtures for Media Library Tools

This directory contains test fixtures for comprehensive testing of the Media Library Tools project. The fixtures are organized by tool category and provide realistic test scenarios for various media library management operations.

## Directory Structure

```
tests/fixtures/
├── README.md                    # This file
├── sabnzbd/                     # SABnzbd tool fixtures
│   ├── mixed_environment/       # Mixed SABnzbd and BitTorrent downloads
│   ├── sabnzbd_only/           # Pure SABnzbd download scenarios
│   └── bittorrent_only/        # Pure BitTorrent download scenarios
├── plex/                       # Plex tool fixtures
│   ├── movies/                 # Movie organization scenarios
│   ├── tv_shows/               # TV show organization scenarios
│   └── mixed_media/            # Mixed content scenarios
├── plex_api/                   # Plex API tool fixtures
│   ├── episode_metadata/       # Episode metadata responses
│   └── server_responses/       # Server API responses
└── common/                     # Common media file types
    ├── video_files/            # Sample video files
    ├── audio_files/            # Sample audio files
    ├── subtitle_files/         # Sample subtitle files
    └── image_files/            # Sample image files
```

## Fixture Categories

### SABnzbd Fixtures

#### Mixed Environment (`sabnzbd/mixed_environment/`)
Tests scenarios where both SABnzbd and BitTorrent downloads coexist:
- `download1/` - SABnzbd download with `.nzo` and `.nzb` indicators
- `download2/` - BitTorrent download with `.torrent` indicator

#### SABnzbd Only (`sabnzbd/sabnzbd_only/`)
Tests pure SABnzbd environments:
- `completed1/` - TV episode download with SABnzbd indicators
- `completed2/` - Documentary download with SABnzbd indicators

#### BitTorrent Only (`sabnzbd/bittorrent_only/`)
Tests pure BitTorrent environments:
- `torrent1/` - Movie download with `.torrent` indicator
- `torrent2/` - TV episode download with `.torrent` indicator

### Plex Fixtures

#### Movies (`plex/movies/`)
Tests movie organization scenarios:
- `movie_with_extras/` - Movie with unorganized extras files
- `movie_with_subdirs/` - Movie with incorrectly named subdirectories

#### TV Shows (`plex/tv_shows/`)
Tests TV show organization scenarios:
- `unorganized_episodes/` - Episodes that need season directory organization

#### Mixed Media (`plex/mixed_media/`)
Tests scenarios with mixed content types:
- `mixed_content/` - Movies and TV episodes in the same directory

### Plex API Fixtures

#### Episode Metadata (`plex_api/episode_metadata/`)
Tests episode refresh functionality:
- `show_metadata.json` - Sample episode metadata response

#### Server Responses (`plex_api/server_responses/`)
Tests server connectivity and discovery:
- `server_info.json` - Server information response
- `library_sections.json` - Library sections response

### Common Media Files (`common/`)

Provides sample files for testing file type detection:
- **Video Files**: MP4, MKV, AVI formats
- **Audio Files**: MP3, FLAC formats
- **Subtitle Files**: SRT, VTT formats
- **Image Files**: JPG, PNG formats

## Usage with FixtureManager

The `FixtureManager` class in `tests/utils/fixture_manager.py` provides methods to work with these fixtures:

```python
from tests.utils.fixture_manager import FixtureManager

# Copy a fixture to test data directory
fixture_manager = FixtureManager()
test_dir = fixture_manager.copy_fixture_to_test_data('sabnzbd/mixed_environment')

# Create temporary fixture from structure
structure = {
    'movie.mp4': 'file',
    'extras/': {
        'trailer.mp4': 'file',
        'behind_scenes.mp4': 'file'
    }
}
temp_dir = fixture_manager.create_temp_fixture(structure)
```

## Usage with Test Helpers

The `MediaLibraryTestCase` class in `tests/utils/test_helpers.py` provides convenient methods:

```python
from tests.utils.test_helpers import MediaLibraryTestCase

class TestMyTool(MediaLibraryTestCase):
    def test_sabnzbd_detection(self):
        # Copy fixture and automatically track for cleanup
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Run your test logic
        # ...
        
        # Cleanup happens automatically in tearDown()
```

## File Indicators

### SABnzbd Indicators
- `SABnzbd_nzo` - Indicates active SABnzbd download
- `SABnzbd_nzb` - Contains NZB metadata

### BitTorrent Indicators
- `.torrent` - Indicates BitTorrent download

## Content Guidelines

### Placeholder Files
All media files are text placeholders containing metadata about what they represent. This approach:
- Keeps the repository size small
- Provides clear documentation of file types
- Allows easy modification for specific test scenarios
- Avoids copyright issues with actual media content

### Realistic Scenarios
Fixtures are designed to represent real-world scenarios:
- Mixed download environments
- Various file naming conventions
- Different media formats and qualities
- Typical directory structures

### Extensibility
The fixture structure is designed to be easily extended:
- Add new scenarios by creating new directories
- Modify existing fixtures for specific test cases
- Use the `FixtureManager` to create dynamic fixtures

## Best Practices

1. **Use FixtureManager**: Always use the `FixtureManager` class for fixture operations
2. **Clean Up**: Ensure test data is cleaned up after tests (automatic with `MediaLibraryTestCase`)
3. **Isolation**: Each test should use its own copy of fixture data
4. **Documentation**: Document any new fixtures or modifications
5. **Realistic Data**: Keep fixtures representative of real-world scenarios

## Contributing

When adding new fixtures:
1. Follow the existing directory structure
2. Use descriptive names for scenarios
3. Include placeholder content that documents the file type
4. Update this README with new fixture descriptions
5. Add corresponding tests that use the new fixtures

For questions or suggestions about the fixture strategy, refer to `/planning/specifications/fixtures.md`.