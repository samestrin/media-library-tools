# Media Library Tools - Claude Coding Standards

**Repository**: https://github.com/samestrin/media-library-tools/

This document defines the coding standards and best practices for Claude when assisting with the Media Library Tools project. These rules ensure consistency, safety, and maintainability across all tools developed for this project.

## Project Requirements

**Self-Contained** Each tool is a standalone Python script using only standard library modules. **No External Dependencies** Each tool should have no external dependencies, requiring no installation or setup. **No overly complex scripts**: Maximum around 900 lines.

## Claude and Commits

Do not include any reference to claude, to claude authorship, claude contributions, in the git commit messages.

## Core Principles

### 1. Safety First
- **Never delete files without explicit user confirmation**
- **Always provide preview/list mode before destructive operations**
- **Implement comprehensive permission and error handling**
- **Use scoring systems for automated detection rather than simple pattern matching**
- **Gracefully handle permission denied and inaccessible directories**
- **Implement file locking to prevent concurrent executions**
- **Support automated/cron execution with non-interactive mode detection**

### 2. Consistency Across Tools
- **Standardized CLI argument patterns** (`--verbose`, `--debug`, `--delete`, `-y`/`--yes`, `--force`, `--version`)
- **Consistent output formatting** with progress indicators and human-readable sizes
- **Uniform error handling and logging patterns**
- **Shared utility functions** for common operations (size calculation, path handling)
- **Consistent locking mechanisms** to prevent overlapping executions
- **Non-interactive mode support** with automatic detection and `-y` flag for cron/automation

### 3. User Experience
- **Clear, informative output** with progress indicators and human-readable sizes
- **Helpful error messages** with suggested solutions
- **Comprehensive help text** with examples
- **Safe defaults** (list-only mode, require explicit confirmation for destructive actions)

### 4. Self-Contained Design
- **No external dependencies**: Use only Python standard library modules
- **Single-file distribution**: Each tool should be a complete, standalone script
- **Zero installation**: Users can download, `chmod +x`, and run immediately
- **Portable execution**: Scripts work across different Python environments without setup

## Python Code Standards

### File Structure
```python
#!/usr/bin/env python3
"""
Tool Name and Purpose
Version: X.Y
Purpose: Brief description of what the tool does
"""

# Standard library imports only - no external dependencies
import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Optional

# NO third-party imports - keep tools self-contained
# NO local imports - each script should be standalone

VERSION = "X.Y"

# Classes and functions

def main():
    """Main entry point"""
    pass

if __name__ == '__main__':
    main()
```

### Class Design
- **Single responsibility principle**: Each class should have one clear purpose
- **Descriptive class names**: Use names that clearly indicate the class purpose (e.g., `SABnzbdDetector`)
- **Consistent constructor patterns**: Accept configuration parameters in `__init__`
- **Logging methods**: Include `log_verbose()` and `log_debug()` methods for consistent output

### Function Standards
- **Maximum length**: 50-75 lines per function
- **Clear docstrings**: Include purpose, parameters, and return values
- **Type hints**: Use typing annotations for all function parameters and return values
- **Error handling**: Use try/except blocks for file operations and external commands

### Naming Conventions
- **Variables**: `snake_case` (e.g., `sabnzbd_dirs`, `total_bytes`)
- **Functions**: `snake_case` with descriptive verbs (e.g., `analyze_directory`, `get_dir_size`)
- **Classes**: `PascalCase` (e.g., `SABnzbdDetector`, `PlexOrganizer`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `VERSION`, `DEFAULT_THRESHOLD`)
- **Boolean functions**: Prefix with `is_`, `has_`, `can_`, `should_`

### CLI Argument Standards
All tools should implement these standard arguments:
```python
parser.add_argument('path', nargs='?', default='.',
                  help='Directory to process (default: current directory)')
parser.add_argument('--delete', action='store_true',
                  help='Actually perform destructive operations (default: list only)')
parser.add_argument('-y', '--yes', action='store_true',
                  help='Skip confirmation prompts (for non-interactive use)')
parser.add_argument('--verbose', '-v', action='store_true',
                  help='Show verbose output')
parser.add_argument('--debug', action='store_true',
                  help='Show detailed debug output')
parser.add_argument('--force', action='store_true',
                  help='Force execution even if another instance is running')
parser.add_argument('--version', action='version', 
                  version=f'%(prog)s v{VERSION}')
```

### Output Formatting Standards
- **Headers**: Use consistent formatting with version and separator lines
- **Progress indicators**: Show progress for long-running operations
- **Size display**: Use human-readable format (B, K, M, G, T)
- **Status messages**: Use plain text indicators (see Output Message Standards below)
- **Error output**: Send errors to `stderr`, regular output to `stdout`

### Output Message Standards
**IMPORTANT**: Despite the emoji standards listed below, the actual codebase consistently uses plain text indicators for console output. Always follow the existing codebase patterns rather than these theoretical standards.

**Actual Codebase Pattern (USE THIS)**:
```python
print(f"Error: {message}")           # Not ❌
print(f"Warning: {message}")         # Not ⚠️
print(f"SUCCESS: {message}")         # Not ✅
print(f"Processing directory: {path}") # Not 📁
print(f"DRY RUN: {message}")         # Not 🔍
```

**Legacy Emoji Standards (DO NOT USE)**:
These were originally defined but are not used in practice:
- **🎵** Musical note for audio files
- **🎥** Movie camera for video files
- **📁** Folder for directories or file containers
- **📄** Page facing up for single documents or files
- **🗑️** Wastebasket for file deletion operations
- **✅** Check mark button for successful file processes
- **❌** Cross mark for unsuccessful file processes
- **⚠️** Warning sign for warnings and cautions
- **🚫** Prohibited sign for not allowed or bad operations
- **🗄️** File cabinet for archiving operations
- **✨** Sparkles for highlighting successful completion

**Documentation Rule**: Documentation files (README.md, .md files) should use text-based indicators (SUCCESS:, ERROR:, WARNING:) for accessibility and consistency across platforms. Documentation does not use Emoji's.

### Error Handling
- **Graceful degradation**: Continue processing when individual items fail
- **Permission handling**: Catch and handle `PermissionError` appropriately
- **User-friendly messages**: Provide clear error descriptions and suggested actions
- **Exit codes**: Use appropriate exit codes (0 for success, 1 for errors)

### File Operations
- **Use pathlib**: Prefer `pathlib.Path` over `os.path` for path operations
- **Safe deletion**: Use `shutil.rmtree()` with proper error handling
- **Size calculation**: Use system commands (`du`) for accurate directory sizes
- **Permission checks**: Test directory access before processing
- **File locking**: Implement `fcntl`-based locking to prevent concurrent executions
- **Lock cleanup**: Always release locks in finally blocks for proper cleanup

### Documentation Requirements
- **Tool-specific README**: Each tool directory must have a README.md
- **Inline documentation**: Comprehensive docstrings for all classes and functions
- **Usage examples**: Include practical examples in help text and documentation
- **Version tracking**: Maintain version numbers and update documentation accordingly
- **Self-contained documentation**: Each script should include comprehensive help text accessible via `--help`
- **No external documentation dependencies**: All necessary information should be embedded in the script

## Testing Standards

### Test-Driven Development (TDD) Approach
While the project has evolved beyond pure TDD, we follow TDD principles for new features and bug fixes:
- **Red-Green-Refactor**: Write failing tests first, implement minimal code to pass, then refactor
- **Test First for New Features**: Before adding new functionality, write tests that define expected behavior
- **Bug-Driven Testing**: When fixing bugs, first write a test that reproduces the issue
- **Incremental Testing**: Build test coverage incrementally alongside feature development

### Test Infrastructure
- **Comprehensive Test Runner**: Use `tests/run_tests.py` for automated test execution
- **Test Categories**: Organize tests into unit, integration, and performance categories
- **Fixture-based testing**: Use the comprehensive fixture system in `tests/fixtures/` for realistic test scenarios
- **Test data management**: Leverage `FixtureManager` and `MediaLibraryTestCase` for consistent test data handling
- **Self-contained testing**: Tests should not require external dependencies
- **Cross-platform compatibility**: Tests work on macOS, Linux, and Windows with Python 3.7+

### Test Types and Coverage
- **Unit tests**: Test individual functions with various inputs and edge cases
- **Integration tests**: Test complete workflows with sample data
- **Permission tests**: Test behavior with restricted permissions and error conditions
- **Edge cases**: Test with empty directories, special characters, large datasets
- **Regression tests**: Maintain tests for previously fixed bugs
- **Performance tests**: Validate performance with realistic data volumes

### Testing Best Practices
- **Isolated tests**: Each test should be independent and not rely on other tests
- **Descriptive test names**: Use clear, descriptive names that explain what is being tested
- **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases
- **Mock external dependencies**: Use mocks for file system operations and external services when appropriate
- **Test documentation**: Include docstrings explaining complex test scenarios
- **Built-in test modes**: Consider including `--test` or `--self-test` options for basic validation

## Security Considerations
- **Path validation**: Validate all user-provided paths
- **No arbitrary code execution**: Avoid `eval()` or similar dangerous functions
- **Safe subprocess calls**: Use `subprocess.run()` with proper argument handling
- **Permission respect**: Never attempt to escalate privileges
- **Lock file security**: Use temporary directory for lock files with proper permissions
- **PID tracking**: Include process ID in lock files for debugging and cleanup

## Performance Guidelines
- **Efficient file scanning**: Limit directory traversal depth and file counts
- **Progress feedback**: Provide progress indicators for operations > 5 seconds
- **Memory management**: Avoid loading large file lists into memory
- **Lazy evaluation**: Use generators for large datasets when possible
- **Standard library optimization**: Leverage built-in modules for best performance
- **Minimal overhead**: Keep scripts lightweight without external library bloat

## Automation and Cron-Friendly Features

### Non-Interactive Mode Detection
All scripts should include an `is_non_interactive()` function that detects automated environments:
```python
def is_non_interactive() -> bool:
    """
    Detect if we're running in a non-interactive environment (e.g., cron job).
    
    Returns:
        bool: True if running non-interactively, False otherwise
    """
    # Check if stdin is not a TTY (common in cron jobs)
    if not sys.stdin.isatty():
        return True
    
    # Check common environment variables that indicate automation
    automation_vars = ['CRON', 'CI', 'AUTOMATED', 'NON_INTERACTIVE']
    for var in automation_vars:
        if os.environ.get(var):
            return True
    
    # Check if TERM is not set (common in cron)
    if not os.environ.get('TERM'):
        return True
    
    return False
```

### Confirmation Logic Pattern
Implement consistent confirmation logic that respects both the `-y` flag and non-interactive detection:
```python
# Confirmation logic for non-interactive environments
if not args.dry_run:
    if not args.yes and not is_non_interactive():
        # Show interactive confirmation prompt
        response = input("\nProceed with operation? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    elif args.yes or is_non_interactive():
        # Provide feedback for automated execution
        print("Proceeding with operation...")
```

### Argument Validation
Validate the `-y` flag usage:
```python
# Validate arguments
if args.yes and args.dry_run:
    print("Warning: -y/--yes flag has no effect in dry-run mode", file=sys.stderr)
```

### Cron Usage Examples
All help text should include cron usage examples:
```
Cron Usage:
  # Run daily at 3 AM (non-interactive)
  0 3 * * * /usr/local/bin/script_name /path/to/target -y
```

## Code Review Checklist

### Code Quality
- [ ] Follows naming conventions
- [ ] Includes proper error handling
- [ ] Has comprehensive docstrings
- [ ] Implements standard CLI arguments (including `-y`/`--yes` and `--force`)
- [ ] Provides safe preview mode
- [ ] Uses consistent output formatting
- [ ] Implements file locking mechanism
- [ ] Supports both interactive and non-interactive modes
- [ ] Includes `is_non_interactive()` function
- [ ] Implements proper confirmation logic with `-y` flag support
- [ ] Validates `-y` flag usage with dry-run mode
- [ ] Includes cron usage examples in help text
- [ ] Handles cron/automation scenarios properly

### Testing and TDD
- [ ] Includes appropriate tests for new functionality
- [ ] Tests written before or alongside implementation (TDD approach)
- [ ] Tests cover edge cases and error conditions
- [ ] Uses fixture system for realistic test scenarios
- [ ] Tests are isolated and independent
- [ ] Regression tests added for bug fixes
- [ ] Test names are descriptive and clear
- [ ] Updates documentation

### Repository Standards
- [ ] Code follows project repository guidelines (https://github.com/samestrin/media-library-tools/)
- [ ] Changes are documented in appropriate README files
- [ ] Version numbers updated where applicable

These standards ensure consistency, safety, and maintainability across all media library management tools in this project.