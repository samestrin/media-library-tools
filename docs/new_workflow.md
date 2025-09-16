# Media Library Tools - New Build and Commit Workflow

## Overview

This document describes the new automated build and commit workflow for the Media Library Tools project. The workflow ensures that all code changes are properly validated before being merged into the main branch.

## New Workflow Steps

### 1. Development
- Work on source files as before
- Ensure your code includes the `# {{include utils.py}}` marker where shared utilities should be injected
- Run unit tests during development: `python tests/run_tests.py --categories unit`

### 2. Pre-commit Validation
When you commit your changes, the following automated steps will run:
1. Code formatting with Black
2. Code linting with Ruff
3. Security scanning with Bandit
4. Build all tools with validation: `python build.py --all --clean --validate`
5. Test built tools with fast unit tests: `python tests/run_tests.py --built-tools --fast`

If any step fails, the commit will be rejected. You'll need to fix the issues before committing.

### 3. Pull Request Process
When you create a pull request, GitHub Actions will run a comprehensive test suite:
1. Build all tools on multiple operating systems and Python versions
2. Test source tools
3. Test built tools
4. Run integration tests (on Linux with Python 3.10)
5. Generate and upload coverage reports

### 4. Merging
Before merging, all status checks must pass:
- All pre-commit hooks
- All GitHub Actions jobs
- Required code reviews

## Command Reference

### Development Commands
```bash
# Run fast unit tests during development
python tests/run_tests.py --fast

# Build and validate tools
python build.py --all --clean --validate

# Test built tools
python tests/run_tests.py --built-tools --fast
```

### Pre-commit Hook Management
```bash
# Install pre-commit hooks (required)
pip install pre-commit
pre-commit install

# Run pre-commit hooks manually
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

### Troubleshooting
If you encounter issues with the pre-commit hooks:

1. **Hook fails during commit**:
   ```bash
   # See detailed error output
   pre-commit run --verbose
   
   # Run specific hook
   pre-commit run build-tools
   ```

2. **Build validation fails**:
   ```bash
   # Run build with verbose output
   python build.py --all --clean --validate --verbose
   
   # Check specific built tool
   python -m py_compile build/plex_correct_dirs
   ```

3. **Skip hooks temporarily** (not recommended):
   ```bash
   git commit --no-verify -m "commit message"
   ```

## Benefits of the New Workflow

1. **Improved Quality**: Automated validation catches issues early
2. **Faster Feedback**: Fast test modes provide quick feedback during development
3. **Consistent Builds**: Ensures all distributed tools are properly built
4. **Cross-platform Compatibility**: Tests on multiple operating systems
5. **Reduced Manual Work**: Automation handles repetitive tasks

## Rollback Procedure

If the new workflow causes issues:
1. Disable pre-commit hooks: `pre-commit uninstall`
2. Contact the development team
3. Create an issue describing the problem