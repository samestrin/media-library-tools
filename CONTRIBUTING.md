# Contributing to Media Library Tools

Thank you for your interest in contributing to Media Library Tools! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)
- [Code Review Process](#code-review-process)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of media file organization
- Familiarity with command-line tools

### Initial Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/samestrin/media-library-tools.git
   cd media-library-tools
   ```

2. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```
   
This installs the project in editable mode with development dependencies (black, ruff, pre-commit, bandit, coverage).

### Security Scanning (Bandit)
- Bandit runs via pre-commit to scan first-party packages: `SABnzbd/`, `plex/`, and `plex-api/`.
- Run manually:
  ```bash
  bandit -r SABnzbd plex plex-api
  ```

### Test Coverage
- The custom test runner supports coverage reporting:
  ```bash
  python tests/run_tests.py --coverage --cov-term
  ```
- Reports are saved to `results/coverage_html/` (HTML) and `results/coverage.xml` (XML).

3. **Set Up Environment**
   ```bash
   # Copy the example environment file
   cp .env.example ~/.media-library-tools/.env
   
   # Edit with your credentials (optional for development)
   nano ~/.media-library-tools/.env
   ```

4. **Run Tests**
   ```bash
   python tests/run_tests.py
   ```

## Development Environment

### Environment Configuration

The project uses a hierarchical configuration system:

1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **Local .env file** (project directory)
4. **Global .env file** (`~/.media-library-tools/.env`)

### Key Environment Variables

```bash
# API Credentials
TVDB_API_KEY=your_tvdb_api_key
PLEX_TOKEN=your_plex_token
PLEX_SERVER=http://your-plex-server:32400

# Automation Settings
AUTO_EXECUTE=false
AUTO_CONFIRM=false
QUIET_MODE=false

# Testing Configuration
TEST_VERBOSE=false
TEST_DEBUG=false
TEST_CLEANUP=true
PRESERVE_FIXTURES=false
MAX_TEST_DIRS=50
TEST_TIMEOUT=300
LARGE_FILE_THRESHOLD=100
```

### Development Tools

- **Linting**: Follow PEP 8 standards
- **Testing**: Use unittest framework
- **Documentation**: Maintain inline comments and docstrings

## Build System

The project uses a modernized build system that consolidates shared utility functions while maintaining the principle of standalone, self-contained scripts for distribution.

### Overview

- **Development**: Work with modular source files that import from `utils.py`
- **Distribution**: Build script generates standalone scripts with injected utilities
- **Zero Dependencies**: Built tools remain completely self-contained

### Shared Utilities (`utils.py`)

Common functions are consolidated in `utils.py`:
- `display_banner()` - Standardized banner display
- `is_non_interactive()` - Non-interactive environment detection
- `read_global_config_bool()` - Global configuration support
- `format_size()` - Human-readable size formatting
- `confirm_action()` - User confirmation prompts
- `FileLock` class - File locking functionality

### Build Process

1. **Mark Integration Points**: Add `# {{include utils.py}}` marker in source files
2. **Build Tools**: Use `build.py` to generate standalone scripts
3. **Distribution**: Built scripts in `build/` directory are self-contained

### Build Commands

```bash
# Build all tools
python build.py --all

# Build specific tools
python build.py plex/plex_correct_dirs

# Build with verbose output
python build.py --all --verbose

# Build to custom directory
python build.py --all --output-dir dist

# Clean build directory first
python build.py --all --clean
```

### Development Workflow

1. **Development**: Modify source files (not built files)
2. **Testing**: Test both source and built versions
3. **Build**: Generate standalone scripts for distribution
4. **Distribution**: Share built scripts from `build/` directory

### Automated Build Validation

The project now includes automated build validation to ensure code quality:
- Pre-commit hooks automatically build and validate tools
- CI/CD pipeline tests both source and built versions
- Quality gates prevent merging broken code

To set up pre-commit hooks:
```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install
```

After installation, the pre-commit hooks will automatically run on every commit, ensuring that:
- All tools build successfully
- Built tools pass syntax validation
- Code meets quality standards

### Testing Built Tools

```bash
# Test against built tools
python tests/run_tests.py --built-tools

# Test specific categories against built tools
python tests/run_tests.py --built-tools --categories unit

# Test with custom build directory
python tests/run_tests.py --built-tools --build-dir ../dist

# Quick validation during development
python tests/run_tests.py --built-tools --categories unit --fast
```

### Best Practices

1. **Always test against built tools** before submitting pull requests
2. **Run the full test suite** to ensure no regressions
3. **Verify build output** works in your target environment
4. **Use pre-commit hooks** to catch issues early in development

## Project Structure

```
media-library-tools/
├── plex/                    # Plex media organization tools
├── plex-api/               # Plex API interaction tools
├── SABnzbd/                # SABnzbd cleanup utilities
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── performance/       # Performance tests
│   └── fixtures/          # Test data
├── planning/              # Sprint plans and documentation
└── docs/                  # Tool-specific documentation
```

## Coding Standards

### Python Style Guide

- **PEP 8 Compliance**: Follow Python's official style guide
- **Function Length**: Maximum 50-100 lines
- **File Length**: Maximum 500-650 lines
- **Line Length**: 88 characters (Black formatter standard)

### Naming Conventions

```python
# Functions
def process_media_files():     # Verb-based, snake_case
def get_season_info():         # CRUD: get, create, update, delete
def is_valid_episode():       # Boolean: is_, has_, can_, should_
def handle_file_error():       # Event handlers: handle_, on_

# Classes
class MediaOrganizer:          # PascalCase
class SeasonDetector:

# Constants
VIDEO_EXTENSIONS = ['.mp4', '.mkv']  # UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 300

# Variables
file_path = "/path/to/file"     # snake_case
episode_count = 0
```

### Documentation Standards

```python
def organize_episodes(source_dir: str, dry_run: bool = False) -> Dict[str, int]:
    """
    Organize TV episodes into season-specific directories.
    
    Args:
        source_dir: Path to directory containing episodes
        dry_run: If True, show what would be done without executing
        
    Returns:
        Dictionary with organization statistics
        
    Raises:
        FileNotFoundError: If source directory doesn't exist
        PermissionError: If insufficient permissions
    """
```

### Error Handling

```python
# Specific exception handling
try:
    result = process_file(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    return None
except PermissionError:
    logger.error(f"Permission denied: {file_path}")
    return None
except Exception as e:
    logger.error(f"Unexpected error processing {file_path}: {e}")
    return None
```

### CLI Argument Standards

All tools should support these standard arguments:

```python
# Required patterns
parser.add_argument('--execute', action='store_true', help='Execute changes (default: dry-run)')
parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
parser.add_argument('--debug', action='store_true', help='Show debug output')
parser.add_argument('--force', action='store_true', help='Force operation without prompts')
parser.add_argument('--yes', '-y', action='store_true', help='Answer yes to all prompts')
```

## Testing

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes
   - Fast execution (< 1 minute total)
   - No external dependencies

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - May use test fixtures
   - Moderate execution time (< 5 minutes)

3. **Performance Tests** (`tests/performance/`)
   - Benchmark critical operations
   - Large dataset testing
   - Longer execution time acceptable

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific category
python tests/run_tests.py --category unit
python tests/run_tests.py --category integration
python tests/run_tests.py --category performance

# Run with verbose output
python tests/run_tests.py --verbose

# Run specific test file
python -m unittest tests.unit.test_plex_tools
```

### Test Environment Variables

```bash
# Test configuration
TEST_VERBOSE=true          # Enable verbose test output
TEST_DEBUG=true            # Enable debug information
TEST_CLEANUP=true          # Clean up test files after success
PRESERVE_FIXTURES=false    # Keep test fixtures after tests
MAX_TEST_DIRS=50           # Limit test directory creation
TEST_TIMEOUT=300           # Test timeout in seconds
```

### Writing Tests

```python
import unittest
from pathlib import Path
from tests.utils.test_helpers import create_test_structure, cleanup_test_data

class TestMediaOrganizer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = create_test_structure({
            'Season 01': ['S01E01.mkv', 'S01E02.mkv'],
            'Season 02': ['S02E01.mkv']
        })
    
    def tearDown(self):
        """Clean up after each test method."""
        cleanup_test_data(self.test_dir)
    
    def test_season_detection(self):
        """Test season pattern detection."""
        organizer = MediaOrganizer()
        result = organizer.detect_season('S01E01.mkv')
        self.assertEqual(result, 1)
    
    def test_dry_run_mode(self):
        """Test that dry-run mode doesn't modify files."""
        organizer = MediaOrganizer(dry_run=True)
        original_files = list(self.test_dir.rglob('*.mkv'))
        organizer.organize(self.test_dir)
        current_files = list(self.test_dir.rglob('*.mkv'))
        self.assertEqual(len(original_files), len(current_files))
```

## Submitting Changes

### Branch Naming

```bash
# Feature branches
feature/season-detection-improvements
feature/plex-api-integration

# Bug fixes
bugfix/episode-parsing-error
bugfix/permission-handling

# Documentation
docs/contributing-guide
docs/api-documentation
```

### Commit Messages

```bash
# Format: type(scope): description

# Examples
feat(plex): add extended season detection patterns
fix(sabnzbd): handle permission errors gracefully
docs(readme): update installation instructions
test(unit): add tests for episode parsing
refactor(core): extract common file validation logic
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add/update tests
   - Update documentation

3. **Test Changes**
   ```bash
   python tests/run_tests.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description of changes"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Issue Reporting

### Bug Reports

Include the following information:

```markdown
**Environment:**
- OS: [e.g., macOS 12.0, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- Tool version: [e.g., latest commit hash]

**Command executed:**
```bash
./plex_make_seasons /path/to/shows --execute --verbose
```

**Expected behavior:**
Description of what should happen

**Actual behavior:**
Description of what actually happened

**Error output:**
```
Paste error messages here
```

**Additional context:**
- File structure
- Naming patterns
- Any relevant configuration
```

### Feature Requests

```markdown
**Problem description:**
What problem does this solve?

**Proposed solution:**
How should this work?

**Alternatives considered:**
Other approaches you've thought about

**Additional context:**
Any other relevant information
```

## Code Review Process

### Review Criteria

- **Functionality**: Does the code work as intended?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Style**: Does it follow project conventions?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security implications?

### Review Guidelines

- Be constructive and respectful
- Explain the reasoning behind suggestions
- Focus on the code, not the person
- Suggest specific improvements
- Acknowledge good practices

## Development Workflow

### Sprint Planning

The project uses sprint-based development:

- **Active sprints**: `planning/sprints/active/`
- **Completed sprints**: `planning/sprints/completed/`
- **Sprint duration**: Typically 1-2 weeks

### Common Development Tasks

```bash
# Add a new tool
1. Create script in appropriate directory (plex/, SABnzbd/, etc.)
2. Add documentation in docs/ subdirectory
3. Create unit tests in tests/unit/
4. Update README.md with tool description
5. Add integration tests if needed

# Fix a bug
1. Create test that reproduces the bug
2. Fix the issue
3. Verify test passes
4. Update documentation if needed

# Improve performance
1. Add performance test to establish baseline
2. Implement optimization
3. Verify performance improvement
4. Update documentation with performance notes
```

## Getting Help

- **Documentation**: Check tool-specific docs in each directory
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Code Examples**: Look at existing tools for patterns

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Media Library Tools!**
