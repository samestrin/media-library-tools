#!/usr/bin/env python3
"""
Build Script for Media Library Tools

This script concatenates the shared utility module (utils.py) with individual tool scripts
to create standalone, self-contained scripts for distribution. It uses marker-based injection
to insert the shared code at the appropriate location within each tool script.

Features:
- Marker-based code injection (# {{include utils.py}})
- Selective rebuild based on modification times
- Enhanced error reporting with categorization and suggestions
- Progress indicators for multi-tool builds
- Comment insertion for debugging and identification
- Preserves executable nature of tool scripts
- Batch processing of all tools at once
- Command-line arguments for flexibility
- Detailed logging for build process
- Summary statistics and reporting
- Comprehensive validation support

Usage:
    python3 build.py --all              # Build all tools (recommended)
    python3 build.py <script_path>      # Build specific script
    python3 build.py --all --validate   # Build and validate all tools
    python3 build.py --clean --all      # Clean rebuild of all tools

The build system automatically detects when files need rebuilding based on modification
times, significantly improving build performance for incremental changes.

Error Handling:
The script provides detailed error categorization and resolution suggestions for:
- Missing source files or dependencies
- Permission issues
- Syntax errors with line-by-line context
- System resource problems
- Encoding issues

Performance:
- Selective rebuild: ~0.001s per unchanged tool
- Force rebuild: ~0.03s per tool
- Typical improvement: 85-97% time savings for incremental builds

Author: Media Library Tools Project
Version: 3.0.0
"""

import argparse
import ast
import logging
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

VERSION = "3.0.0"
MARKER = "# {{include utils.py}}"
UTILS_FILE = "utils.py"
MODULE_MARKER_PATTERN = r"# \{\{include (lib/[\w\.]+)\}\}"  # Pattern for lib includes


# Utility functions from utils.py for banner display
def display_banner(
    script_name: str,
    version: str,
    description: str,
    no_banner_flag: bool = False,
    quiet_mode: bool = False,
) -> None:
    """
    Display standardized banner for media library tools.

    Args:
        script_name: Name of the script
        version: Version string
        description: Brief description of the script
        no_banner_flag: If True, suppress banner display
        quiet_mode: If True, suppress banner display
    """
    # Check suppression conditions (highest to lowest priority)
    if no_banner_flag or quiet_mode or is_non_interactive():
        return

    try:
        # Display standardized ASCII art
        print("┏┳┓┏━╸╺┳┓╻┏━┓╻  ╻┏┓ ┏━┓┏━┓┏━┓╻ ╻╺┳╸┏━┓┏━┓╻  ┏━┓")
        print("┃┃┃┣╸  ┃┃┃┣━┫┃  ┃┣┻┓┣┳┛┣━┫┣┳┛┗┳┛ ┃ ┃ ┃┃ ┃┃  ┗━┓")
        print("╹ ╹┗━╸╺┻┛╹╹ ╹┗━╸╹┗━┛╹┗╸╹ ╹╹┗╸ ╹  ╹ ┗━┛┗━┛┗━╸┗━┛")
        print(f"{script_name} v{version}: {description}")
        print()  # Blank line for separation
    except Exception:
        # Banner display errors should not prevent script execution
        pass


def is_non_interactive() -> bool:
    """
    Detect if running in non-interactive environment (cron, etc.).

    Returns:
        True if non-interactive, False otherwise
    """
    # Check if stdin is not a TTY (common in cron jobs)
    if not sys.stdin.isatty():
        return True

    # Check for common non-interactive environment variables
    non_interactive_vars = ["CRON", "CI", "AUTOMATED", "NON_INTERACTIVE"]
    for var in non_interactive_vars:
        if os.environ.get(var):
            return True

    # Check if TERM is not set or is 'dumb' (common in automated environments)
    term = os.environ.get("TERM", "")
    return bool(not term or term == "dumb")


# Import shared utility functions
from utils import is_windows, should_use_emojis

# format_status_message function (copied from tests/run_tests.py)
def format_status_message(
    message: str, emoji: str = "", fallback_prefix: str = ""
) -> str:
    """
    Format a status message with emoji on supported platforms or fallback text.

    Args:
        message: The main message text
        emoji: The emoji to use on supported platforms
        fallback_prefix: Text prefix to use instead of emoji on unsupported platforms

    Returns:
        Formatted message string
    """
    if should_use_emojis() and emoji:
        return f"{emoji} {message}"
    elif fallback_prefix:
        return f"{fallback_prefix}: {message}"
    else:
        return message


def read_module_content(module_path: str) -> str:
    """
    Read the content of a module file for injection into tool scripts.

    This function loads module content from lib/ directory or utils.py for injection
    into tool scripts at marker locations during the build process.

    Args:
        module_path: Path to the module file (e.g., 'lib/core.py' or 'utils.py')

    Returns:
        str: Complete content of the module as a string

    Raises:
        FileNotFoundError: If the module file is not found
        IOError: If there's an error reading the file (permissions, encoding, etc.)

    Example:
        >>> core_content = read_module_content('lib/core.py')
        >>> utils_content = read_module_content('utils.py')
    """
    module_file = Path(module_path)
    if not module_file.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")

    try:
        with open(module_file, encoding="utf-8") as f:
            content = f.read()

        # Strip shebang line if present to avoid duplicate shebangs in built scripts
        lines = content.split("\n")
        if lines and lines[0].startswith("#!"):
            content = "\n".join(lines[1:])

        return content
    except OSError as e:
        raise OSError(f"Error reading module file {module_path}: {e}") from e


def read_utils_content() -> str:
    """
    Read the content of the utils.py file for injection into tool scripts.

    This function is a wrapper around read_module_content for backward compatibility.
    It loads the shared utility module that contains common functions used across
    multiple media library tools.

    Returns:
        str: Complete content of utils.py as a string

    Raises:
        FileNotFoundError: If utils.py is not found in the current directory
        IOError: If there's an error reading the file (permissions, encoding, etc.)

    Example:
        >>> utils_content = read_utils_content()
        >>> print(len(utils_content))
        8426  # Approximate size of utils.py content
    """
    return read_module_content(UTILS_FILE)


def find_include_markers(script_content: str) -> List[Tuple[str, str]]:
    """
    Find all include markers in script content.

    This function scans script content for both legacy utils.py includes and new
    modular lib includes, returning them in the order they appear.

    Args:
        script_content: The content of the script to scan

    Returns:
        List of tuples (marker, module_path) for each include found

    Example:
        >>> content = "# {{include utils.py}}\\n# {{include lib/core.py}}"
        >>> markers = find_include_markers(content)
        >>> print(markers)
        [('# {{include utils.py}}', 'utils.py'), ('# {{include lib/core.py}}', 'lib/core.py')]
    """
    markers = []
    
    # Find legacy utils.py marker
    if MARKER in script_content:
        markers.append((MARKER, UTILS_FILE))
    
    # Find modular lib includes using regex
    lib_matches = re.finditer(MODULE_MARKER_PATTERN, script_content)
    for match in lib_matches:
        full_marker = match.group(0)
        module_path = match.group(1)
        markers.append((full_marker, module_path))
    
    return markers


def process_multiple_includes(script_content: str) -> str:
    """
    Process multiple include markers in script content.

    This function handles both legacy utils.py includes and new modular lib includes,
    replacing each marker with the appropriate module content.

    Args:
        script_content: The original script content with include markers

    Returns:
        Script content with all includes processed

    Raises:
        FileNotFoundError: If any included module is not found
        OSError: If there's an error reading any module file
    """
    markers = find_include_markers(script_content)
    
    if not markers:
        return script_content
    
    processed_content = script_content
    
    for marker, module_path in markers:
        try:
            module_content = read_module_content(module_path)
            
            # Prepare the injected content with comments
            injected_content = f"""
# ======================================================
# INJECTED MODULE - START
# Generated by build.py v{VERSION}
# Source: {module_path}
# ======================================================

{module_content}

# ======================================================
# INJECTED MODULE - END
# Source: {module_path}
# ======================================================
"""
            
            # Replace the marker with the injected content
            processed_content = processed_content.replace(marker, injected_content)
            
        except Exception as e:
            # Re-raise with context about which module failed
            raise type(e)(f"Failed to process include '{module_path}': {e}") from e
    
    return processed_content


def extract_function_calls(script_content: str) -> Set[str]:
    """
    Extract function calls from Python script content using AST parsing.

    This function analyzes Python code to identify all function calls, which can
    then be used to determine which modules are actually needed.

    Args:
        script_content: Python script content to analyze

    Returns:
        Set of function names that are called in the script

    Example:
        >>> content = "display_banner('test', '1.0', 'desc')\\nformat_size(1024)"
        >>> calls = extract_function_calls(content)
        >>> print(sorted(calls))
        ['display_banner', 'format_size']
    """
    function_calls = set()
    
    try:
        # Parse the script content into an AST
        tree = ast.parse(script_content)
        
        # Walk through all nodes in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Handle direct function calls (e.g., function_name())
                if isinstance(node.func, ast.Name):
                    function_calls.add(node.func.id)
                # Handle attribute calls (e.g., obj.method())
                elif isinstance(node.func, ast.Attribute):
                    function_calls.add(node.func.attr)
    
    except SyntaxError:
        # If we can't parse the script, return empty set
        # This will fall back to including all modules
        pass
    
    return function_calls


def create_function_module_mapping() -> Dict[str, str]:
    """
    Create a mapping of function names to their module locations.

    Returns:
        Dictionary mapping function names to module paths
    """
    mapping = {}
    
    # Core module functions
    core_functions = [
        'is_non_interactive', 'read_global_config_bool', 'is_windows', 
        'should_use_emojis', 'FileLock', 'acquire_lock', 'release_lock'
    ]
    for func in core_functions:
        mapping[func] = 'lib/core.py'
    
    # UI module functions  
    ui_functions = [
        'display_banner', 'format_size', 'confirm_action'
    ]
    for func in ui_functions:
        mapping[func] = 'lib/ui.py'
    
    # Filesystem module functions (when populated)
    filesystem_functions = [
        'get_directory_size', 'validate_directory_path', 'safe_remove_directory',
        'get_subdirectories', 'is_media_file', 'count_files_by_type',
        'normalize_path', 'has_write_permission'
    ]
    for func in filesystem_functions:
        mapping[func] = 'lib/filesystem.py'
    
    # Validation module functions (when populated)
    validation_functions = [
        'validate_path_argument', 'validate_filename', 'validate_positive_integer',
        'validate_regex_pattern', 'validate_directory_writable', 'sanitize_filename',
        'validate_cli_arguments', 'check_required_dependencies', 'validate_file_extension'
    ]
    for func in validation_functions:
        mapping[func] = 'lib/validation.py'
    
    return mapping


def analyze_dependencies(script_content: str) -> List[str]:
    """
    Analyze script content to determine which modules are actually needed.

    This function uses AST parsing to detect function usage and maps those
    functions to the modules that contain them, enabling selective inclusion.

    Args:
        script_content: The script content to analyze

    Returns:
        List of module paths that are actually needed

    Example:
        >>> content = "display_banner('test', '1.0', 'desc')"
        >>> deps = analyze_dependencies(content)
        >>> print(deps)
        ['lib/ui.py', 'lib/core.py']  # ui for display_banner, core for is_non_interactive
    """
    function_calls = extract_function_calls(script_content)
    function_module_map = create_function_module_mapping()
    
    required_modules = set()
    
    # Map function calls to modules
    for func_name in function_calls:
        if func_name in function_module_map:
            required_modules.add(function_module_map[func_name])
    
    # Handle dependencies between modules
    # display_banner depends on is_non_interactive (core module)
    if 'lib/ui.py' in required_modules and 'display_banner' in function_calls:
        required_modules.add('lib/core.py')
    
    # should_use_emojis depends on other core functions
    if 'should_use_emojis' in function_calls:
        required_modules.add('lib/core.py')  # Already there but explicit
    
    return sorted(list(required_modules))


def optimize_includes(script_content: str, verbose: bool = False) -> Tuple[str, List[str]]:
    """
    Optimize include markers based on actual function usage.

    This function analyzes script content to determine which modules are actually
    needed and can suggest optimizations for include markers.

    Args:
        script_content: The script content to analyze
        verbose: Whether to show detailed optimization information

    Returns:
        Tuple of (original_content, suggested_modules)
    """
    # Extract existing includes
    existing_markers = find_include_markers(script_content)
    existing_modules = [module_path for _, module_path in existing_markers]
    
    # Analyze dependencies
    suggested_modules = analyze_dependencies(script_content)
    
    if verbose:
        print(f"  Existing includes: {existing_modules}")
        print(f"  Suggested includes: {suggested_modules}")
        
        # Show potential savings
        if len(suggested_modules) < len(existing_modules):
            savings = len(existing_modules) - len(suggested_modules)
            print(f"  Potential optimization: Remove {savings} unnecessary includes")
        elif len(suggested_modules) > len(existing_modules):
            missing = len(suggested_modules) - len(existing_modules)
            print(f"  Missing dependencies: {missing} modules needed")
    
    return script_content, suggested_modules


def should_rebuild(
    source_path: Path, output_path: Path, dependencies: List[Path] = None
) -> bool:
    """
    Determine if source file needs rebuilding based on modification times.

    This function implements the selective rebuild logic that significantly improves
    build performance by only rebuilding tools when necessary. It compares modification
    times of the source file and its dependencies against the built output.

    Rebuild Triggers:
    1. Output file doesn't exist
    2. Source file is newer than output
    3. Any dependency is newer than output

    Args:
        source_path (Path): Path to the source script to check
        output_path (Path): Path to the built script output
        dependencies (List[Path], optional): List of dependency files to check.
            Common dependencies include utils.py and build.py itself.
            Defaults to None.

    Returns:
        bool: True if rebuilding is needed, False if output is up to date

    Performance Impact:
        - Up to 97% build time reduction for unchanged files
        - Typical check time: <0.001s per file

    Example:
        >>> source = Path('plex/plex_correct_dirs')
        >>> output = Path('build/plex_correct_dirs')
        >>> deps = [Path('utils.py')]
        >>> should_rebuild(source, output, deps)
        False  # Output is up to date
    """
    if not output_path.exists():
        return True

    # Check if source is newer than output
    source_mtime = source_path.stat().st_mtime
    output_mtime = output_path.stat().st_mtime

    if source_mtime > output_mtime:
        return True

    # Check dependencies if provided
    if dependencies:
        for dep_path in dependencies:
            if dep_path.exists():
                dep_mtime = dep_path.stat().st_mtime
                if dep_mtime > output_mtime:
                    return True

    return False


def process_script(
    script_path: Path, output_dir: Optional[Path] = None, force_rebuild: bool = False
) -> bool:
    """
    Process a single script by injecting utils.py content at the marker location.

    This is the core build function that transforms source tool scripts into standalone
    distribution scripts. It performs the following operations:

    1. Checks if rebuild is needed (unless forced)
    2. Reads the source script content
    3. Locates the injection marker: # {{include utils.py}}
    4. Replaces marker with complete utils.py content
    5. Writes the built script to output directory
    6. Preserves executable permissions

    The function includes comprehensive error handling with categorized error messages
    and resolution suggestions for common issues.

    Args:
        script_path (Path): Path to the source script to process
        output_dir (Optional[Path]): Directory to write the built script.
            Defaults to 'build/' subdirectory if not specified.
        force_rebuild (bool): If True, rebuild even if output is up to date.
            Defaults to False for optimal performance.

    Returns:
        bool: True if processing successful, False if any errors occurred

    Side Effects:
        - Creates output directory if it doesn't exist
        - Writes built script to output directory
        - Preserves executable permissions from source
        - Prints progress messages and error details

    Error Handling:
        Provides detailed error categorization for:
        - Missing source files
        - Missing utils.py dependency
        - Permission issues
        - Disk space problems
        - Encoding issues

    Performance:
        - Selective rebuild: ~0.001s for unchanged files
        - Full rebuild: ~0.03s per file
        - Large files (>1MB): May take longer but uncommon

    Example:
        >>> success = process_script(Path('plex/plex_correct_dirs'))
        Built: plex/plex_correct_dirs -> build/plex_correct_dirs
        >>> print(success)
        True
    """
    if not script_path.exists():
        print(format_status_message(f"Script not found: {script_path}", "❌", "ERROR"))
        return False

    # Determine output path
    if output_dir is None:
        output_dir = Path("build")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / script_path.name

    # Check if rebuild is needed (unless forced)
    if not force_rebuild:
        # Read script content to determine dependencies
        try:
            with open(script_path, encoding="utf-8") as f:
                temp_content = f.read()
            markers = find_include_markers(temp_content)
            dependencies = []
            for _, module_path in markers:
                module_file = Path(module_path)
                if module_file.exists():
                    dependencies.append(module_file)
        except Exception:
            # Fallback to just utils.py if we can't read the script
            dependencies = [Path(UTILS_FILE)] if Path(UTILS_FILE).exists() else []
        
        if not should_rebuild(script_path, output_path, dependencies):
            print(format_status_message(f"Skipping {script_path.name} (up to date)", "⏭️", "SKIP"))
            return True

    # Read the original script
    try:
        with open(script_path, encoding="utf-8") as f:
            script_content = f.read()
    except Exception as e:
        category, suggestion = categorize_build_error(e, "reading_source")
        print(format_status_message(f"Build Error ({category}): {script_path}", "❌", "ERROR"))
        print(f"  Details: {e}")
        print(f"  Resolution: {suggestion}")
        return False

    # Process include markers (both legacy and modular)
    markers = find_include_markers(script_content)
    if not markers:
        print(
            format_status_message(f"No include markers found in {script_path} - script will be copied as-is", "⚠️", "WARNING")
        )
        built_content = script_content
    else:
        # Process all includes using the new multiple includes system
        try:
            built_content = process_multiple_includes(script_content)
        except Exception as e:
            category, suggestion = categorize_build_error(e, "reading_modules")
            print(format_status_message(f"Build Error ({category}): {script_path}", "❌", "ERROR"))
            print(f"  Details: {e}")
            print(f"  Resolution: {suggestion}")
            return False

    # Write the built script
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(built_content)

        # Preserve executable permissions
        if script_path.stat().st_mode & 0o111:  # If original is executable
            output_path.chmod(0o755)

        print(format_status_message(f"Built: {script_path} -> {output_path}", "✅", "SUCCESS"))
        return True

    except Exception as e:
        category, suggestion = categorize_build_error(e, "writing_output")
        print(format_status_message(f"Build Error ({category}): {output_path}", "❌", "ERROR"))
        print(f"  Details: {e}")
        print(f"  Resolution: {suggestion}")
        return False


def format_syntax_error(error: SyntaxError, script_path: Path) -> str:
    """
    Format a syntax error with detailed context information.

    Args:
        error: The SyntaxError exception
        script_path: Path to the script that caused the error

    Returns:
        Formatted error message with context
    """
    lines = [
        f"Syntax Error in {script_path.name}:",
        f"  File: {script_path}",
        f"  Line {error.lineno}: {error.text.strip() if error.text else 'N/A'}",
        f"  Error: {error.msg}",
    ]

    if error.offset:
        lines.append(f"  Position: Column {error.offset}")
        if error.text:
            lines.append(f"  Context: {' ' * (error.offset - 1)}^")

    # Add suggestions for common issues
    if "invalid syntax" in error.msg.lower():
        lines.append("\n  Suggestions:")
        lines.append("    - Check for missing parentheses, brackets, or quotes")
        lines.append("    - Verify proper indentation")
        lines.append("    - Look for typos in keywords")
    elif "unexpected indent" in error.msg.lower():
        lines.append("\n  Suggestions:")
        lines.append("    - Check indentation consistency (tabs vs spaces)")
        lines.append("    - Verify proper code block structure")
    elif "unindent" in error.msg.lower():
        lines.append("\n  Suggestions:")
        lines.append("    - Check for missing or extra indentation")
        lines.append("    - Verify proper function/class closure")

    return "\n".join(lines)


def categorize_build_error(error: Exception, context: str) -> Tuple[str, str]:
    """
    Categorize build errors and provide resolution suggestions.

    Args:
        error: The exception that occurred
        context: Context where the error occurred (e.g., 'reading_source', 'writing_output')

    Returns:
        Tuple of (category, suggestion)
    """
    error_msg = str(error).lower()

    if isinstance(error, FileNotFoundError):
        if context == "reading_source":
            return (
                "Missing Source File",
                "Verify the script path exists and is accessible",
            )
        elif context == "reading_utils":
            return "Missing Utils File", "Ensure utils.py exists in the project root"
        elif context == "reading_modules":
            return "Missing Module File", "Ensure all lib/ modules exist and are accessible"
        else:
            return "File Not Found", "Check file paths and permissions"

    elif isinstance(error, PermissionError):
        return (
            "Permission Denied",
            "Check file/directory permissions, try running with appropriate privileges",
        )

    elif isinstance(error, UnicodeDecodeError):
        return (
            "Encoding Issue",
            "File may contain non-UTF-8 characters, check file encoding",
        )

    elif isinstance(error, OSError):
        if "no space left" in error_msg:
            return "Disk Space", "Free up disk space and try again"
        elif "read-only" in error_msg:
            return "Read-Only Filesystem", "Check directory write permissions"
        else:
            return "System Error", "Check system resources and file permissions"

    elif isinstance(error, SyntaxError):
        return (
            "Python Syntax Error",
            "Fix syntax errors in the source file before building",
        )

    else:
        return "Unknown Error", "Check build script logs for more details"


def validate_built_script(script_path: Path) -> bool:
    """
    Validate that a built script is syntactically correct.

    Args:
        script_path: Path to the built script to validate

    Returns:
        True if valid, False otherwise
    """
    if not script_path.exists():
        print(f"Error: Built script not found for validation: {script_path}")
        return False

    try:
        # Try to compile the script to check for syntax errors
        with open(script_path, encoding="utf-8") as f:
            script_content = f.read()

        compile(script_content, str(script_path), "exec")
        return True

    except SyntaxError as e:
        print(format_syntax_error(e, script_path))
        return False

    except Exception as e:
        category, suggestion = categorize_build_error(e, "validation")
        print(f"Validation Error ({category}): {script_path}")
        print(f"  Details: {e}")
        print(f"  Resolution: {suggestion}")
        return False


def find_scripts(search_paths: List[str]) -> List[Path]:
    """
    Find all script files in the given search paths.

    Args:
        search_paths: List of paths to search for scripts

    Returns:
        List of Path objects for found scripts
    """
    scripts = []

    for search_path in search_paths:
        path = Path(search_path)

        if path.is_file():
            # Single file specified
            scripts.append(path)
        elif path.is_dir():
            # Directory specified - find scripts
            for script_path in path.rglob("*"):
                if (
                    script_path.is_file()
                    and not script_path.name.startswith(".")
                    and script_path.suffix == ""  # Extensionless files
                    and script_path.name not in ["build.py", "utils.py"]
                ):  # Exclude build system files
                    # Basic check if it's a Python script
                    try:
                        with open(script_path, encoding="utf-8") as f:
                            first_line = f.readline()
                            if first_line.startswith("#!") and "python" in first_line:
                                scripts.append(script_path)
                    except (OSError, UnicodeDecodeError):
                        continue

    return scripts


def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> None:
    """Setup logging configuration for the build process."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(level=log_level, format=log_format, handlers=handlers)


def generate_build_summary(results: Dict[str, bool], start_time: float) -> None:
    """Generate and display build summary statistics."""
    total_time = time.time() - start_time
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)

    print(f"\n{'=' * 60}")
    print("BUILD SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total scripts processed: {total_count}")
    print(f"Successfully built: {success_count}")
    print(f"Failed: {total_count - success_count}")
    print(f"Success rate: {(success_count / total_count) * 100:.1f}%")
    print(f"Total build time: {total_time:.2f} seconds")

    if success_count < total_count:
        print("\nFAILED SCRIPTS:")
        for script, success in results.items():
            if not success:
                print(f"  {format_status_message(script, '❌', 'ERROR')}")

    if success_count > 0:
        print("\nSUCCESSFUL SCRIPTS:")
        for script, success in results.items():
            if success:
                print(f"  {format_status_message(script, '✅', 'SUCCESS')}")

    print(f"{'=' * 60}")


def build_all_tools(
    output_dir: Path,
    verbose: bool = False,
    validate: bool = False,
    force_rebuild: bool = False,
) -> Dict[str, bool]:
    """Build all tools in the project automatically."""
    results = {}

    # Define standard tool directories in src/
    tool_dirs = ["src/plex", "src/SABnzbd", "src/plex-api"]
    # Map source directories to output directories
    output_mapping = {
        "src/plex": "plex",
        "src/SABnzbd": "SABnzbd",
        "src/plex-api": "plex-api",
    }

    # Count total scripts for progress indication
    total_scripts = 0
    all_scripts = []
    for tool_dir in tool_dirs:
        tool_path = Path(tool_dir)
        if tool_path.exists() and tool_path.is_dir():
            scripts = find_scripts([str(tool_path)])
            for script in scripts:
                script_name = f"{tool_dir}/{script.name}"
                # Determine output directory for this script
                output_subdir = output_mapping[tool_dir]
                target_output_dir = (
                    Path(output_subdir)
                    if output_dir == Path(".")
                    else output_dir / output_subdir
                )
                all_scripts.append((script, script_name, target_output_dir))
                total_scripts += 1

    if verbose and total_scripts > 1:
        print(format_status_message(f"Building {total_scripts} tools...", "🔨", "BUILD"))

    # Process each script with progress indication
    for i, (script, script_name, target_output_dir) in enumerate(all_scripts, 1):
        if verbose and total_scripts > 1:
            print(format_status_message(f"[{i}/{total_scripts}] Building {script_name}...", "🔨", "BUILD"))
        elif verbose:
            print(format_status_message(f"Building {script_name}...", "🔨", "BUILD"))

        success = process_script(script, target_output_dir, force_rebuild)
        results[script_name] = success

        # Validate the built script if requested
        if success and validate:
            built_script_path = target_output_dir / script.name
            if not validate_built_script(built_script_path):
                print(format_status_message(f"Validation failed for {script_name}", "❌", "ERROR"))
                results[script_name] = False

    return results


def main():
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(
        description="Build script for Media Library Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Build all scripts in standard directories
  %(prog)s --all                    # Build all tools in project
  %(prog)s plex/plex_correct_dirs   # Build a specific script
  %(prog)s plex/                    # Build all scripts in plex directory
  %(prog)s --output-dir dist --all  # Build all tools to custom output directory
  %(prog)s --log-file build.log --verbose --all  # Verbose build with logging

The build script looks for the marker '# {{include utils.py}}' in source scripts
and replaces it with the content of utils.py surrounded by comment blocks.
Scripts without the marker are copied as-is.

Source directories: src/plex/, src/SABnzbd/, src/plex-api/
Output directories: plex/, SABnzbd/, plex-api/
        """,
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to scripts or directories to build (default: none when using --all)",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Output directory for built scripts (default: current directory - builds into main folders)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Build all tools from src/ directories into main directories (plex/, SABnzbd/, plex-api/)",
    )

    parser.add_argument("--log-file", type=Path, help="Log file for build process")

    parser.add_argument("--version", action="version", version=f"%(prog)s v{VERSION}")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose output"
    )

    parser.add_argument(
        "--clean", action="store_true", help="Clean output directory before building"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate built scripts for syntax errors",
    )

    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild of all scripts even if up to date",
    )

    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Suppress banner display",
    )

    args = parser.parse_args()

    # Display banner unless suppressed
    display_banner(
        "Media Library Tools Build Script",
        VERSION,
        "Build system for creating standalone media library tools",
        no_banner_flag=args.no_banner,
        quiet_mode=False,
    )

    # Setup logging
    setup_logging(args.verbose, args.log_file)
    logging.info(
        f"Starting build process with Media Library Tools Build Script v{VERSION}"
    )

    # Clean output directory if requested
    if args.clean and args.output_dir.exists():
        import shutil

        # Safety check: don't clean current directory or project root
        current_dir = Path(".").resolve()
        project_root = Path(__file__).parent.resolve()
        output_dir_resolved = args.output_dir.resolve()

        if output_dir_resolved in (current_dir, project_root):
            logging.error(
                f"Cannot clean current directory or project root: {args.output_dir}"
            )
            logging.error(
                "Use a specific output directory with --output-dir for cleaning"
            )
            return 1

        shutil.rmtree(args.output_dir)
        logging.info(f"Cleaned output directory: {args.output_dir}")

    start_time = time.time()

    # Determine what to build
    if args.all:
        # Build all tools automatically
        if args.paths:
            logging.warning("--all flag specified, ignoring individual paths")

        logging.info("Building all tools from src/ directories into main directories")
        results = build_all_tools(
            args.output_dir, args.verbose, args.validate, args.force_rebuild
        )

        if not results:
            print(format_status_message("No scripts found to build in standard directories.", "⚠️", "WARNING"))
            return 1

    else:
        # Build specified paths or default behavior
        if not args.paths:
            # Default to src/ directories only, not entire project
            args.paths = ["src/plex", "src/SABnzbd", "src/plex-api"]

        # Find scripts to build
        scripts = find_scripts(args.paths)

        if not scripts:
            print(format_status_message("No scripts found to build.", "⚠️", "WARNING"))
            return 1

        if args.verbose:
            print(format_status_message(f"Found {len(scripts)} script(s) to build:", "📋", "INFO"))
            for script in scripts:
                print(f"  {script}")
            print()

        # Process each script
        results = {}
        for script in scripts:
            script_name = str(script)
            if args.verbose:
                print(format_status_message(f"Building {script_name}...", "🔨", "BUILD"))
            success = process_script(script, args.output_dir, args.force_rebuild)
            results[script_name] = success

            # Validate the built script if requested
            if success and args.validate:
                built_script_path = args.output_dir / script.name
                if not validate_built_script(built_script_path):
                    print(format_status_message(f"Validation failed for {script_name}", "❌", "ERROR"))
                    results[script_name] = False

    # Generate summary
    generate_build_summary(results, start_time)

    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)

    logging.info(
        f"Build completed: {success_count}/{total_count} scripts built successfully"
    )

    if success_count < total_count:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
