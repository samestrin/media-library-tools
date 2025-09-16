#!/usr/bin/env python3
"""
Media Library Tools - Test Runner
Version: 1.0
Purpose: Comprehensive test runner for the media library tools test suite
"""

import os
import sys
import argparse
import unittest
import time
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from io import StringIO

# Add utils to path for test configuration
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

try:
    from test_config import (
        TEST_CONFIG, TEST_CATEGORIES, TEST_PATHS,
        validate_test_environment, setup_test_environment,
        cleanup_test_environment
    )
except ImportError:
    # Fallback configuration if test_config is not available
    TEST_CONFIG = {
        'verbose': False,
        'debug': False,
        'cleanup_on_success': True,
        'test_timeout': 300
    }
    # TEST_CATEGORIES is imported from test_config.py above
    TEST_PATHS = {'tests_dir': Path(__file__).parent}
    
    def validate_test_environment():
        return {'basic_validation': True}
    
    def setup_test_environment():
        return True
    
    def cleanup_test_environment():
        return True

VERSION = "1.0"


class TestResult:
    """Container for test execution results."""
    
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.skipped = 0
        self.duration = 0.0
        self.output = ""
        self.error_details = []
    
    @property
    def total(self) -> int:
        """Total number of tests run."""
        return self.passed + self.failed + self.errors + self.skipped
    
    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    @property
    def is_successful(self) -> bool:
        """Whether all tests passed."""
        return self.failed == 0 and self.errors == 0


class TestRunner:
    """Main test runner class."""
    
    def __init__(self, args):
        self.args = args
        self.tests_dir = TEST_PATHS.get('tests_dir', Path(__file__).parent)
        self.results: List[TestResult] = []
        self.start_time = 0.0
        self.end_time = 0.0
        
        # Handle built tools testing
        if hasattr(args, 'built_tools') and args.built_tools:
            self.build_dir = Path(args.build_dir)
            if not self.build_dir.is_absolute():
                self.build_dir = self.tests_dir / self.build_dir
            
            if not self.build_dir.exists():
                print(f"❌ Build directory not found: {self.build_dir}")
                print("Run 'python build.py --all' to build tools first")
                sys.exit(1)
            
            self._setup_built_tools_environment()
    
    def _setup_built_tools_environment(self):
        """Setup environment variables to point tests at built tools."""
        # Add build directory to PATH so tests find built tools
        current_path = os.environ.get('PATH', '')
        build_dir_str = str(self.build_dir.absolute())
        
        if build_dir_str not in current_path:
            os.environ['PATH'] = f"{build_dir_str}:{current_path}"
        
        # Set environment variable to indicate we're testing built tools
        os.environ['TESTING_BUILT_TOOLS'] = 'true'
        os.environ['BUILD_TOOLS_DIR'] = build_dir_str
        
        if not self.args.quiet:
            print(f"🔧 Testing built tools from: {self.build_dir}")
    
    def discover_tests(self, pattern: str = None, subdir: str = None) -> List[str]:
        """
        Discover test files based on pattern and optional subdirectory.
        
        Args:
            pattern: File pattern to match (e.g., 'test_*.py')
            subdir: Specific subdirectory to search in
            
        Returns:
            List of test file paths
        """
        if pattern is None:
            pattern = 'test_*.py'
        
        test_files = []
        
        if subdir:
            # Search in specific subdirectory
            search_dir = self.tests_dir / subdir
            if search_dir.exists() and search_dir.is_dir():
                for test_file in search_dir.glob(pattern):
                    if test_file.is_file():
                        test_files.append(str(test_file))
        else:
            # Search in main tests directory
            for test_file in self.tests_dir.glob(pattern):
                if test_file.is_file() and test_file.name != 'run_tests.py':
                    test_files.append(str(test_file))
            
            # Search in subdirectories (unit, integration, performance, examples)
            test_subdirs = ['unit', 'integration', 'performance', 'examples']
            for subdir_name in test_subdirs:
                subdir_path = self.tests_dir / subdir_name
                if subdir_path.exists() and subdir_path.is_dir():
                    for test_file in subdir_path.glob(pattern):
                        if test_file.is_file():
                            test_files.append(str(test_file))
            
            # Also check any other subdirectories that might exist
            for subdir_path in self.tests_dir.iterdir():
                if (subdir_path.is_dir() and 
                    not subdir_path.name.startswith('.') and 
                    subdir_path.name not in test_subdirs):
                    for test_file in subdir_path.glob(pattern):
                        if test_file.is_file():
                            test_files.append(str(test_file))
        
        return sorted(test_files)
    
    def run_test_file(self, test_file: str, timeout: int = None) -> TestResult:
        """
        Run a single test file.
        
        Args:
            test_file: Path to the test file
            timeout: Maximum execution time in seconds
            
        Returns:
            TestResult object with execution results
        """
        result = TestResult(test_file)
        
        if timeout is None:
            timeout = TEST_CONFIG.get('test_timeout', 300)
        
        try:
            start_time = time.time()
            
            # Prepare test execution command
            if getattr(self.args, 'coverage', False):
                # Run tests under coverage in a subprocess with parallel data
                cmd = [
                    sys.executable, '-m', 'coverage', 'run', '-p', '-m', 'unittest',
                    'discover', '-s', str(Path(test_file).parent), '-p', Path(test_file).name
                ]
            else:
                cmd = [
                    sys.executable, '-m', 'unittest', 'discover', '-s',
                    str(Path(test_file).parent), '-p', Path(test_file).name
                ]
            
            if self.args.verbose:
                cmd.append('-v')
            
            # Run the test
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.tests_dir
            )
            
            result.duration = time.time() - start_time
            result.output = process.stdout + process.stderr
            
            # Parse unittest output to extract test counts
            self._parse_unittest_output(result, process.stdout, process.stderr)
            
            if process.returncode != 0 and result.failed == 0 and result.errors == 0:
                # If process failed but we didn't detect test failures,
                # treat it as an error
                result.errors = 1
                result.error_details.append(f"Process exited with code {process.returncode}")
            
        except subprocess.TimeoutExpired:
            result.duration = timeout
            result.errors = 1
            result.error_details.append(f"Test timed out after {timeout} seconds")
            result.output = "Test execution timed out"
            
        except Exception as e:
            result.duration = time.time() - start_time if 'start_time' in locals() else 0
            result.errors = 1
            result.error_details.append(f"Test execution failed: {str(e)}")
            result.output = f"Error running test: {str(e)}"
        
        return result
    
    def _parse_unittest_output(self, result: TestResult, stdout: str, stderr: str) -> None:
        """
        Parse unittest output to extract test statistics.
        
        Args:
            result: TestResult object to update
            stdout: Standard output from unittest
            stderr: Standard error from unittest
        """
        output = stdout + stderr
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for unittest summary line
            if 'Ran ' in line and ' test' in line:
                try:
                    # Extract number of tests run
                    parts = line.split()
                    if len(parts) >= 2:
                        result.passed = int(parts[1])
                except (ValueError, IndexError):
                    pass
            
            # Look for failure/error indicators
            if line.startswith('FAILED ('):
                # Parse failure details
                failure_info = line[8:-1]  # Remove 'FAILED (' and ')'
                parts = failure_info.split(', ')
                
                for part in parts:
                    if 'failures=' in part:
                        try:
                            result.failed = int(part.split('=')[1])
                            result.passed -= result.failed
                        except (ValueError, IndexError):
                            pass
                    elif 'errors=' in part:
                        try:
                            result.errors = int(part.split('=')[1])
                            result.passed -= result.errors
                        except (ValueError, IndexError):
                            pass
                    elif 'skipped=' in part:
                        try:
                            result.skipped = int(part.split('=')[1])
                            result.passed -= result.skipped
                        except (ValueError, IndexError):
                            pass
            
            # Collect error details
            if line.startswith('ERROR:') or line.startswith('FAIL:'):
                result.error_details.append(line)
    
    def run_category(self, category: str) -> List[TestResult]:
        """
        Run all tests in a specific category.
        
        Args:
            category: Test category name
            
        Returns:
            List of TestResult objects
        """
        if category not in TEST_CATEGORIES:
            print(f"❌ Unknown test category: {category}")
            return []
        
        category_config = TEST_CATEGORIES[category]
        pattern = category_config.get('pattern', 'test_*.py')
        timeout = category_config.get('timeout', TEST_CONFIG.get('test_timeout', 300))
        subdir = category_config.get('subdir')
        
        search_location = f"in {subdir}/" if subdir else "in tests/"
        print(f"\n🧪 Running {category} tests (pattern: {pattern} {search_location})")
        print("=" * 60)
        
        test_files = self.discover_tests(pattern, subdir)
        if not test_files:
            print(f"⚠️  No test files found for pattern: {pattern}")
            return []
        
        category_results = []
        for test_file in test_files:
            print(f"\n📄 Running: {Path(test_file).name}")
            result = self.run_test_file(test_file, timeout)
            category_results.append(result)
            
            # Print immediate results
            status = "✅" if result.is_successful else "❌"
            print(f"{status} {result.passed} passed, {result.failed} failed, "
                  f"{result.errors} errors, {result.skipped} skipped "
                  f"({result.duration:.2f}s)")
            
            if not result.is_successful and self.args.verbose:
                for error in result.error_details[:3]:  # Show first 3 errors
                    print(f"   {error}")
        
        return category_results
    
    def run_all_tests(self) -> None:
        """
        Run all tests based on the specified categories or patterns.
        """
        self.start_time = time.time()
        
        if self.args.categories:
            # Run specific categories
            for category in self.args.categories:
                category_results = self.run_category(category)
                self.results.extend(category_results)
        elif self.args.pattern:
            # Run tests matching a specific pattern
            print(f"\n🧪 Running tests matching pattern: {self.args.pattern}")
            print("=" * 60)
            
            test_files = self.discover_tests(self.args.pattern)
            if not test_files:
                print(f"⚠️  No test files found for pattern: {self.args.pattern}")
                return
            
            for test_file in test_files:
                print(f"\n📄 Running: {Path(test_file).name}")
                result = self.run_test_file(test_file)
                self.results.append(result)
                
                status = "✅" if result.is_successful else "❌"
                print(f"{status} {result.passed} passed, {result.failed} failed, "
                      f"{result.errors} errors, {result.skipped} skipped "
                      f"({result.duration:.2f}s)")
        else:
            # Run all test categories
            for category in TEST_CATEGORIES.keys():
                if not self.args.skip_categories or category not in self.args.skip_categories:
                    category_results = self.run_category(category)
                    self.results.extend(category_results)
        
        self.end_time = time.time()
    
    def generate_summary(self) -> None:
        """
        Generate and display a comprehensive test summary.
        """
        if not self.results:
            print("\n⚠️  No tests were run.")
            return
        
        total_duration = self.end_time - self.start_time
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)
        total_tests = total_passed + total_failed + total_errors + total_skipped
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests Run: {total_tests}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print(f"🚫 Errors: {total_errors}")
        print(f"⏭️  Skipped: {total_skipped}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r.is_successful]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            print("-" * 40)
            for result in failed_tests:
                test_name = Path(result.name).name
                print(f"  {test_name}: {result.failed} failed, {result.errors} errors")
                
                if self.args.verbose and result.error_details:
                    for error in result.error_details[:2]:  # Show first 2 errors
                        print(f"    - {error}")
        
        # Performance summary
        if self.args.show_performance:
            print("\n⏱️  PERFORMANCE SUMMARY:")
            print("-" * 40)
            sorted_results = sorted(self.results, key=lambda r: r.duration, reverse=True)
            for result in sorted_results[:5]:  # Show top 5 slowest
                test_name = Path(result.name).name
                print(f"  {test_name}: {result.duration:.2f}s")
        
        # Overall result
        if total_failed == 0 and total_errors == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n💥 {total_failed + total_errors} TESTS FAILED")

        # If coverage enabled, show where reports are located
        if getattr(self.args, 'coverage', False):
            cov_dir = Path('results') / 'coverage_html'
            cov_xml = Path('results') / 'coverage.xml'
            print("\n📚 Coverage reports:")
            print(f"  HTML: {cov_dir}/index.html")
            print(f"  XML:  {cov_xml}")
    
    def save_report(self) -> None:
        """
        Save test results to a file if requested.
        """
        if not self.args.output_file:
            return
        
        output_path = Path(self.args.output_file)
        
        try:
            with open(output_path, 'w') as f:
                f.write(f"Media Library Tools - Test Report\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {self.end_time - self.start_time:.2f}s\n\n")
                
                for result in self.results:
                    f.write(f"Test: {Path(result.name).name}\n")
                    f.write(f"  Passed: {result.passed}\n")
                    f.write(f"  Failed: {result.failed}\n")
                    f.write(f"  Errors: {result.errors}\n")
                    f.write(f"  Skipped: {result.skipped}\n")
                    f.write(f"  Duration: {result.duration:.2f}s\n")
                    
                    if result.error_details:
                        f.write(f"  Error Details:\n")
                        for error in result.error_details:
                            f.write(f"    {error}\n")
                    f.write("\n")
            
            print(f"\n📄 Test report saved to: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Media Library Tools Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_tests.py
  
  # Run specific test categories
  python run_tests.py --categories unit integration
  
  # Run tests matching a pattern
  python run_tests.py --pattern "test_sabnzbd_*.py"
  
  # Run with verbose output and save report
  python run_tests.py --verbose --output-file test_report.txt
  
  # Skip performance tests
  python run_tests.py --skip-categories performance
  
  # Quick validation run
  python run_tests.py --categories unit --fast
  
  # Test against built tools instead of source
  python run_tests.py --built-tools
  
  # Test built tools with custom build directory
  python run_tests.py --built-tools --build-dir ../dist
"""
    )
    
    # Test selection options
    parser.add_argument('--categories', nargs='+', 
                       choices=list(TEST_CATEGORIES.keys()),
                       help='Test categories to run')
    parser.add_argument('--skip-categories', nargs='+',
                       choices=list(TEST_CATEGORIES.keys()),
                       help='Test categories to skip')
    parser.add_argument('--pattern', 
                       help='File pattern to match (e.g., "test_sabnzbd_*.py")')
    
    # Execution options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose test output')
    parser.add_argument('--debug', action='store_true',
                       help='Show debug information')
    parser.add_argument('--fast', action='store_true',
                       help='Run tests with reduced timeouts and selective testing')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Skip cleanup of test data')
    
    # Output options
    parser.add_argument('--output-file', '-o',
                       help='Save test report to file')
    parser.add_argument('--show-performance', action='store_true',
                       help='Show performance summary')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimize output (only show summary)')
    
    # Coverage options
    parser.add_argument('--coverage', action='store_true',
                       help='Collect test coverage using coverage.py')
    parser.add_argument('--cov-html', action='store_true',
                       help='Generate HTML coverage report (default when --coverage)')
    parser.add_argument('--cov-xml', action='store_true',
                       help='Generate XML coverage report (default when --coverage)')
    parser.add_argument('--cov-term', action='store_true',
                       help='Show terminal coverage summary (default when --coverage)')
    parser.add_argument('--cov-erase', action='store_true',
                       help='Erase previous coverage data before running tests')
    
    # Environment options
    parser.add_argument('--setup-only', action='store_true',
                       help='Only set up test environment, don\'t run tests')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate test environment')
    parser.add_argument('--cleanup-only', action='store_true',
                       help='Only clean up test environment')
    
    # Build system options
    parser.add_argument('--built-tools', action='store_true',
                       help='Test against built tool files in build/ directory instead of source files')
    parser.add_argument('--build-dir', default='../build',
                       help='Directory containing built tools (default: ../build)')
    
    parser.add_argument('--version', action='version', 
                       version=f'%(prog)s v{VERSION}')
    
    args = parser.parse_args()
    
    # Handle special modes
    if args.validate_only:
        print("🔍 Validating test environment...")
        validation_results = validate_test_environment()
        
        print("\nValidation Results:")
        for check, result in validation_results.items():
            status = "✅" if result else "❌"
            print(f"  {check}: {status}")
        
        if all(validation_results.values()):
            print("\n✅ Test environment is ready")
            sys.exit(0)
        else:
            print("\n❌ Test environment validation failed")
            sys.exit(1)
    
    if args.setup_only:
        print("🔧 Setting up test environment...")
        if setup_test_environment():
            print("✅ Test environment setup complete")
            sys.exit(0)
        else:
            print("❌ Test environment setup failed")
            sys.exit(1)
    
    if args.cleanup_only:
        print("🧹 Cleaning up test environment...")
        if cleanup_test_environment():
            print("✅ Test environment cleanup complete")
            sys.exit(0)
        else:
            print("❌ Test environment cleanup failed")
            sys.exit(1)
    
    # Validate test environment before running tests
    if not args.quiet:
        print(f"Media Library Tools Test Runner v{VERSION}")
        print("=" * 50)
        
        print("\n🔍 Validating test environment...")
        validation_results = validate_test_environment()
        failed_checks = [k for k, v in validation_results.items() if not v]
        
        if failed_checks:
            print(f"❌ Environment validation failed: {failed_checks}")
            print("Run with --setup-only to fix environment issues")
            sys.exit(1)
        else:
            print("✅ Test environment validated")
    
    # Adjust configuration for fast mode
    if args.fast:
        # In fast mode, only run unit tests unless otherwise specified
        if not args.categories and not args.pattern:
            args.categories = ['unit']
        
        # Reduce timeouts for faster feedback
        for category in TEST_CATEGORIES.values():
            category['timeout'] = min(category.get('timeout', 60), 30)
        TEST_CONFIG['test_timeout'] = 30
    
    # Create and run test runner
    runner = TestRunner(args)
    
    try:
        # Prepare coverage environment if requested
        if args.coverage:
            # Ensure coverage is available
            try:
                import coverage  # type: ignore
            except Exception:
                print("\n❌ coverage.py is not installed. Install dev deps to use --coverage.")
                sys.exit(1)

            # Erase previous data if requested
            if args.cov_erase:
                subprocess.run([sys.executable, '-m', 'coverage', 'erase'], check=False)

        runner.run_all_tests()
        
        if not args.quiet:
            runner.generate_summary()
        
        runner.save_report()

        # Combine and generate coverage reports if requested
        if args.coverage:
            results_dir = Path('results')
            cov_html_dir = results_dir / 'coverage_html'
            cov_xml_file = results_dir / 'coverage.xml'
            results_dir.mkdir(parents=True, exist_ok=True)
            cov_html_dir.mkdir(parents=True, exist_ok=True)

            # Combine parallel data and generate reports
            subprocess.run([sys.executable, '-m', 'coverage', 'combine'], check=False)
            if args.cov_term or (not args.cov_html and not args.cov_xml):
                subprocess.run([sys.executable, '-m', 'coverage', 'report', '--skip-empty'], check=False)
            if args.cov_html or args.coverage:
                subprocess.run([sys.executable, '-m', 'coverage', 'html', '-d', str(cov_html_dir)], check=False)
            if args.cov_xml or args.coverage:
                subprocess.run([sys.executable, '-m', 'coverage', 'xml', '-o', str(cov_xml_file)], check=False)
        
        # Cleanup if requested
        if not args.no_cleanup and TEST_CONFIG.get('cleanup_on_success', True):
            if all(r.is_successful for r in runner.results):
                if not args.quiet:
                    print("\n🧹 Cleaning up test data...")
                cleanup_test_environment()
        
        # Exit with appropriate code
        if any(not r.is_successful for r in runner.results):
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
