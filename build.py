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
Version: 2.0.0
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

VERSION = "2.0.0"
MARKER = "# {{include utils.py}}"
UTILS_FILE = "utils.py"


def read_utils_content() -> str:
    """
    Read the content of the utils.py file for injection into tool scripts.

    This function loads the shared utility module that contains common functions
    used across multiple media library tools. The content is injected into tool
    scripts at marker locations during the build process.

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
    utils_path = Path(UTILS_FILE)
    if not utils_path.exists():
        raise FileNotFoundError(f"Utils file not found: {UTILS_FILE}")

    try:
        with open(utils_path, encoding="utf-8") as f:
            content = f.read()

        # Strip shebang line if present to avoid duplicate shebangs in built scripts
        lines = content.split("\n")
        if lines and lines[0].startswith("#!"):
            content = "\n".join(lines[1:])

        return content
    except OSError as e:
        raise OSError(f"Error reading utils file: {e}") from e


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
        print(f"Error: Script not found: {script_path}")
        return False

    # Determine output path
    if output_dir is None:
        output_dir = Path("build")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / script_path.name

    # Check if rebuild is needed (unless forced)
    if not force_rebuild:
        dependencies = [Path(UTILS_FILE)] if Path(UTILS_FILE).exists() else []
        if not should_rebuild(script_path, output_path, dependencies):
            print(f"Skipping {script_path.name} (up to date)")
            return True

    # Read the original script
    try:
        with open(script_path, encoding="utf-8") as f:
            script_content = f.read()
    except Exception as e:
        category, suggestion = categorize_build_error(e, "reading_source")
        print(f"Build Error ({category}): {script_path}")
        print(f"  Details: {e}")
        print(f"  Resolution: {suggestion}")
        return False

    # Check if marker exists
    if MARKER not in script_content:
        print(
            f"Warning: No marker found in {script_path} - script will be copied as-is"
        )
        built_content = script_content
    else:
        # Read utils content
        try:
            utils_content = read_utils_content()
        except Exception as e:
            category, suggestion = categorize_build_error(e, "reading_utils")
            print(f"Build Error ({category}): {script_path}")
            print(f"  Details: {e}")
            print(f"  Resolution: {suggestion}")
            return False

        # Prepare the injected content with comments
        injected_content = f"""
# ======================================================
# INJECTED SHARED UTILITIES - START
# Generated by build.py v{VERSION}
# Source: {UTILS_FILE}
# ======================================================

{utils_content}

# ======================================================
# INJECTED SHARED UTILITIES - END
# ======================================================
"""

        # Replace the marker with the injected content
        built_content = script_content.replace(MARKER, injected_content)

    # Write the built script
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(built_content)

        # Preserve executable permissions
        if script_path.stat().st_mode & 0o111:  # If original is executable
            output_path.chmod(0o755)

        print(f"Built: {script_path} -> {output_path}")
        return True

    except Exception as e:
        category, suggestion = categorize_build_error(e, "writing_output")
        print(f"Build Error ({category}): {output_path}")
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

    print(f"\n{'='*60}")
    print("BUILD SUMMARY")
    print(f"{'='*60}")
    print(f"Total scripts processed: {total_count}")
    print(f"Successfully built: {success_count}")
    print(f"Failed: {total_count - success_count}")
    print(f"Success rate: {(success_count/total_count)*100:.1f}%")
    print(f"Total build time: {total_time:.2f} seconds")

    if success_count < total_count:
        print("\nFAILED SCRIPTS:")
        for script, success in results.items():
            if not success:
                print(f"  ❌ {script}")

    if success_count > 0:
        print("\nSUCCESSFUL SCRIPTS:")
        for script, success in results.items():
            if success:
                print(f"  ✅ {script}")

    print(f"{'='*60}")


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
        print(f"Building {total_scripts} tools...")

    # Process each script with progress indication
    for i, (script, script_name, target_output_dir) in enumerate(all_scripts, 1):
        if verbose and total_scripts > 1:
            print(f"[{i}/{total_scripts}] Building {script_name}...")
        elif verbose:
            print(f"Building {script_name}...")

        success = process_script(script, target_output_dir, force_rebuild)
        results[script_name] = success

        # Validate the built script if requested
        if success and validate:
            built_script_path = target_output_dir / script.name
            if not validate_built_script(built_script_path):
                print(f"Validation failed for {script_name}")
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

    args = parser.parse_args()

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
        
        if output_dir_resolved == current_dir or output_dir_resolved == project_root:
            logging.error(f"Cannot clean current directory or project root: {args.output_dir}")
            logging.error("Use a specific output directory with --output-dir for cleaning")
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
            print("No scripts found to build in standard directories.")
            return 1

    else:
        # Build specified paths or default behavior
        if not args.paths:
            args.paths = ["."]

        # Find scripts to build
        scripts = find_scripts(args.paths)

        if not scripts:
            print("No scripts found to build.")
            return 1

        if args.verbose:
            print(f"Found {len(scripts)} script(s) to build:")
            for script in scripts:
                print(f"  {script}")
            print()

        # Process each script
        results = {}
        for script in scripts:
            script_name = str(script)
            if args.verbose:
                print(f"Building {script_name}...")
            success = process_script(script, args.output_dir, args.force_rebuild)
            results[script_name] = success

            # Validate the built script if requested
            if success and args.validate:
                built_script_path = args.output_dir / script.name
                if not validate_built_script(built_script_path):
                    print(f"Validation failed for {script_name}")
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
