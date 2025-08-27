# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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