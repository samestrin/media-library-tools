# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0-beta] - 2025-09-15

### Added
- **Automated Build and Commit Workflow**: Comprehensive automation to ensure code quality and build reliability
  - Pre-commit hooks that automatically build and validate all tools before allowing commits
  - GitHub Actions CI/CD pipeline that tests builds on multiple operating systems and Python versions
  - Automated validation that built tools pass syntax checking
  - Quality gates to prevent merging broken code
- **Enhanced Build System**: Improvements to the build process for better reliability and error reporting
  - New `--validate` flag to check syntax of built tools
  - Better error handling and exit codes in build script
  - Improved logging for CI/CD environments
- **Development Workflow Documentation**: Clear guidance for contributors on the new workflow
  - Updated CONTRIBUTING.md with detailed build and test instructions
  - New workflow documentation in docs/new_workflow.md
  - Enhanced pre-commit hook setup instructions

### Changed
- **Pre-commit Configuration**: Added build validation hook to ensure code quality
  - Local hook that builds and validates all tools
  - Integrated with existing code formatting and linting hooks
- **Test Runner Enhancements**: Improvements to testing for faster development feedback
  - Enhanced `--fast` mode that runs only unit tests with reduced timeouts
  - Better error reporting and debugging capabilities
- **Documentation Updates**: Comprehensive updates to reflect new workflow
  - Updated README with build process information
  - Enhanced coding standards to include build compatibility requirements

### Testing
- **Cross-platform CI**: GitHub Actions workflow testing on Ubuntu, macOS, and Windows
- **Multi-version Testing**: Tests across Python versions 3.8 through 3.12
- **Comprehensive Coverage**: Unit, integration, and performance tests for both source and built tools
- **Quality Gates**: Automated checks to prevent merging broken code

## [1.2.0-beta] - 2025-08-28

### Added
- **Complete CLI Standardization**: All 9 tools now follow identical command-line interface patterns
  - `--dry-run` flag with default True behavior across all tools
  - `--execute` flag to override dry-run mode and actually perform operations
  - `--verbose` and `--debug` flags for consistent logging levels
  - Standardized mode indicators: "DRY-RUN MODE" vs "EXECUTE MODE" 
  - Consistent help text formatting with cron usage examples
  - Backward compatibility maintained for all existing usage patterns
- **Consistent Banner System**: Standardized ASCII art banner across all tools
  - Professional "MEDIABRARYTOOLS" ASCII art displayed by default
  - `--no-banner` flag to suppress banner display for automation
  - `QUIET_MODE` global configuration for permanent banner suppression
  - Automatic banner suppression in non-interactive environments (cron, CI/CD)
  - Zero-dependency design with embedded banner functions

### Enhanced
- **sabnzbd_cleanup**: Added `--execute` as alias for `--delete` while maintaining backward compatibility
- **All Plex Tools**: Updated to use standardized argument patterns and mode indicators
  - `plex_correct_dirs`: Added execute mode, verbose/debug flags, mode indicators
  - `plex_make_dirs`: Added execute mode, verbose/debug flags, mode indicators  
  - `plex_make_seasons`: Added execute mode, verbose/debug flags, mode indicators
  - `plex_make_years`: Added execute mode, verbose/debug flags, mode indicators
  - `plex_move_movie_extras`: Added execute mode, standardized confirmation logic
  - `plex_movie_subdir_renamer`: Added execute mode, refactored function architecture
  - `plex_make_all_seasons`: Added execute mode, verbose/debug flags, preserved parallel processing
  - `plex_update_tv_years`: Verified compliance as reference implementation

### Testing
- **Comprehensive CLI Test Suite**: New integration tests validate standardization across all tools
- **Behavioral Testing**: Automated tests verify dry-run/execute modes, argument parsing, help text consistency
- **Backward Compatibility**: Tests confirm existing usage patterns continue to work

### Documentation  
- **Updated README**: New CLI Standardization section documenting standard arguments and behavior
- **Version Bump**: Updated to 1.2.0-beta reflecting major CLI improvements
- **Enhanced Examples**: All tools now include consistent cron usage examples in help text

## [1.1.0-beta] - 2025-08-28

### Added
- **Global Configuration System**: Revolutionary new feature enabling default behavior configuration
  - `AUTO_EXECUTE` environment variable for default execution mode across all tools
  - `AUTO_CONFIRM` environment variable for default confirmation behavior
  - Configuration hierarchy: CLI arguments > Environment variables > Local .env > Global ~/.media-library-tools/.env
  - Comprehensive `.env` file support with graceful error handling
  - Boolean value parsing supporting multiple formats: 'true', '1', 'yes', 'on' (case-insensitive)
  
### Enhanced
- **All 9 Media Library Tools** updated with consistent global configuration support:
  - `plex/plex_correct_dirs` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `plex/plex_make_all_seasons` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `plex/plex_make_dirs` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `plex/plex_make_seasons` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `plex/plex_make_years` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `plex/plex_move_movie_extras` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `plex/plex_movie_subdir_renamer` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `plex/plex_update_tv_years` - Now supports AUTO_EXECUTE and AUTO_CONFIRM
  - `SABnzbd/sabnzbd_cleanup` - Now supports AUTO_EXECUTE and AUTO_CONFIRM

### Features
- **Backward Compatibility**: All existing usage patterns continue to work unchanged
- **CLI Precedence**: Explicit command-line flags always override environment variables
- **Automation-Friendly**: Perfect for interactive workflows and cron jobs
- **Zero Dependencies**: Global config implementation uses only Python standard library
- **Robust Error Handling**: Graceful handling of malformed or missing configuration files
- **Non-Interactive Detection**: Automatic environment detection for cron/CI workflows

### Testing
- **Comprehensive Unit Tests**: 8/8 tests passing (100% success rate)
- **Environment Variable Testing**: Complete validation of configuration hierarchy
- **Boolean Parsing Tests**: All supported value formats tested and validated
- **Error Handling Tests**: Malformed configuration file handling verified
- **Integration Tests**: CLI argument precedence and script behavior validation

### Documentation
- **Updated README.md**: Complete global configuration documentation with examples
- **Updated CLAUDE.md**: New Global Configuration Standards section
- **Usage Examples**: Comprehensive examples for all configuration methods
- **Migration Guide**: Clear instructions for adopting global configuration

## [1.0.0-beta] - 2025-08-27

### Added
- **Initial beta release** - First feature-complete version ready for extensive testing
- **SABnzbd Tools**: Complete cleanup and organization suite
  - `sabnzbd_cleanup` - Automated cleanup of SABnzbd download artifacts
- **Plex Media Tools**: Comprehensive media organization toolkit
  - `plex_correct_dirs` - Directory name sanitization and cleanup
  - `plex_make_all_seasons` - Batch season processing for TV shows
  - `plex_make_dirs` - Directory structure creation
  - `plex_make_seasons` - TV show season organization
  - `plex_make_years` - Year-based movie organization
  - `plex_move_movie_extras` - Movie extras management and relocation
  - `plex_movie_subdir_renamer` - Movie subdirectory renaming
  - `plex_update_tv_years` - Update TV show year metadata
- **Plex API Tools**: Server management capabilities
  - `plex_server_episode_refresh` - Automated episode metadata refresh
- **Self-Contained Design**: All tools use Python standard library only
- **Zero Dependencies**: No external packages required for any tool
- **Automation Support**: Full cron/automation compatibility with `-y` flag
- **Safety Features**: Comprehensive dry-run modes and confirmation prompts
- **Cross-Platform**: Works on Linux, macOS, and Windows with Python 3.6+
- **Comprehensive Testing**: Full test suite with fixture-based testing
- **Complete Documentation**: Tool-specific documentation and usage examples

### Features
- **Standardized CLI Interface**: Consistent arguments across all tools
- **Progress Indicators**: Visual feedback for long-running operations
- **File Locking**: Prevents concurrent executions of the same tool
- **Non-Interactive Detection**: Automatic cron-friendly behavior
- **Human-Readable Output**: File sizes and progress in readable formats
- **Robust Error Handling**: Graceful handling of permissions and edge cases
- **Portable Execution**: Download, `chmod +x`, and run immediately

### Documentation
- Complete README with installation and usage instructions
- Tool-specific documentation for each component
- Comprehensive testing documentation and examples
- Project roadmap and development guidelines
- Coding standards and contribution guidelines

### Testing
- Unit tests for all core functionality
- Integration tests for complete workflows
- Performance tests for large datasets
- Cross-platform compatibility testing
- Comprehensive fixture system for realistic test scenarios

## Pre-Release Development (2024-2025)

### Development Phase
All development prior to v1.0.0 was considered pre-release, including:
- Initial tool development and prototyping
- Feature implementation and testing
- Documentation creation and refinement
- Test suite development
- Code standardization and cleanup
- Performance optimization
- Cross-platform compatibility work

---

## Release Notes

### Version 1.0.0-beta Highlights

This release marks the first beta version of Media Library Tools, representing months of development and initial testing. The project has evolved from individual scripts into a comprehensive toolkit ready for extensive testing and feedback.

**Key Achievements:**
- **Feature Complete**: All planned tools have been implemented and are ready for testing
- **Zero Dependencies**: Complete self-containment using only Python standard library
- **Automation First**: Built with automation and cron jobs as primary use cases
- **Safety Focused**: Comprehensive safety features prevent accidental data loss
- **Documentation Complete**: Full documentation coverage for all tools and features

**Beta Testing Notes:**
This beta release is ready for extensive testing. Please:
1. Test all tools thoroughly in your environment
2. Report any bugs or issues you encounter
3. Provide feedback on usability and feature requests
4. Test automation scenarios with the `-y` flag
5. Validate cross-platform compatibility

---

## Future Releases

Future releases will follow semantic versioning:
- **Patch releases (1.0.x)**: Bug fixes and minor improvements
- **Minor releases (1.x.0)**: New features and enhancements
- **Major releases (x.0.0)**: Breaking changes or major architectural updates

See [ROADMAP.md](ROADMAP.md) for planned features and improvements.