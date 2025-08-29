# Test Suite - Media Library Tools

This directory contains the comprehensive test suite for the Media Library Tools project, implementing a fixture-based testing approach for reliable and maintainable tests.

## Directory Structure

```
tests/
├── README.md                   # This file
├── fixtures/                   # Test fixture data (see fixtures/README.md)
├── test_data/                  # Temporary test data (auto-generated)
├── utils/                      # Test utilities and helpers
│   ├── fixture_manager.py      # Fixture management system
│   └── test_helpers.py         # MediaLibraryTestCase and test utilities
├── unit/                       # Unit tests
│   ├── test_sabnzbd_cleanup.py
│   ├── test_plex_tools.py
│   ├── test_file_validation.py
│   ├── test_error_handling.py
│   └── test_fixture_examples.py
└── integration/                # Integration tests
    ├── test_workflow.py
    ├── test_batch_operations.py
    └── test_error_scenarios.py
```

## Testing Approach

### Fixture-Based Testing

All tests use the centralized fixture system to ensure:
- **Realistic Test Data**: Tests operate on actual media library structures
- **Test Isolation**: Each test gets its own copy of fixture data
- **Maintainability**: Fixture data can be updated independently of test code
- **Consistency**: Standardized testing patterns across all test files

### MediaLibraryTestCase

All test classes inherit from `MediaLibraryTestCase` which provides:
- Fixture management via `copy_fixture()` method
- Automatic cleanup of test data
- Structure validation utilities
- Common assertion methods

## Usage Patterns

### Basic Test Structure

```python
from tests.utils.test_helpers import MediaLibraryTestCase

class TestExample(MediaLibraryTestCase):
    def test_something(self):
        # Copy fixture to test_data for this test
        test_dir = self.copy_fixture('sabnzbd/mixed_environment')
        
        # Validate fixture structure
        self.assert_directory_structure(test_dir, {
            'download1': {'type': 'directory'},
            'download2': {'type': 'directory'}
        })
        
        # Run your test logic
        result = your_function(test_dir)
        
        # Assert results
        self.assertTrue(result)
        
        # Cleanup is automatic via tearDown()
```

### Available Fixtures

- **SABnzbd Fixtures**: `sabnzbd/mixed_environment`, `sabnzbd/sabnzbd_only`, `sabnzbd/bittorrent_only`
- **Plex Fixtures**: `plex/movies/*`, `plex/tv_shows/*`, `plex/mixed_media/*`
- **Common Fixtures**: `common/video_files`, `common/audio_files`, `common/subtitle_files`, `common/image_files`
- **Plex API Fixtures**: `plex_api/episode_metadata`, `plex_api/server_responses`

For complete fixture documentation, see `fixtures/README.md`.

## Running Tests

### All Tests
```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# Specific test file
python -m pytest tests/unit/test_sabnzbd_cleanup.py
```

### Test Coverage
```bash
# Option A: Built-in runner with coverage (HTML, XML, terminal)
python tests/run_tests.py --coverage --cov-term

# Generate only HTML report
python tests/run_tests.py --coverage --cov-html

# Generate only XML report
python tests/run_tests.py --coverage --cov-xml

# Quick subset with coverage
python tests/run_tests.py --categories unit --fast --coverage

# Reports are written to results/coverage_html (HTML) and results/coverage.xml (XML)
```

```bash
# Option B: Pytest (if used locally)
python -m pytest tests/ --cov=. --cov-report=html
```

## Test Development Guidelines

### Requirements
1. **Inherit from MediaLibraryTestCase**: All test classes must inherit from `MediaLibraryTestCase`
2. **Use Fixtures**: Replace manual test data creation with `copy_fixture()` calls
3. **Validate Structures**: Include `assert_directory_structure()` validation
4. **No Manual Cleanup**: Rely on automatic cleanup via `tearDown()`
5. **Realistic Scenarios**: Use fixtures that mirror actual usage patterns

### Best Practices
- Use appropriate fixture categories for your test scenarios
- Validate fixture structures before running test logic
- Test both success and error conditions
- Keep tests focused and independent
- Document any custom fixtures or test utilities

## Fixture Management

The `FixtureManager` class handles:
- Copying fixtures from `fixtures/` to `test_data/`
- Creating unique test directories for isolation
- Automatic cleanup after test completion
- Directory structure validation

For implementation details, see `utils/fixture_manager.py`.

## Contributing

When adding new tests:
1. Follow the fixture-based testing approach
2. Inherit from `MediaLibraryTestCase`
3. Use existing fixtures when possible
4. Create new fixtures only when necessary
5. Update this documentation if adding new test categories

For fixture creation guidelines, see `fixtures/README.md`.
