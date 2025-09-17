#!/usr/bin/env python3
"""
Unit tests for enhanced UI display functions in lib/ui.py

This test module validates the enhanced UI display functions including:
- List display functions (display_item_list, display_summary_list, display_progress_item)
- Table display functions (display_stats_table, display_results_table)
- Enhanced status message formatting (format_status_message)
- Existing functions compatibility (display_banner, format_size, confirm_action)
"""

import importlib.util
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path


def load_script_as_module(script_path: str, module_name: str):
    """
    Load an extensionless Python script as a module for testing.

    Args:
        script_path: Path to the extensionless script
        module_name: Name to assign to the loaded module

    Returns:
        The loaded module
    """
    script_path = Path(script_path)

    # Create temporary .py file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_py_path = temp_file.name

        # Copy script content to temporary .py file
        with open(script_path, encoding="utf-8") as original:
            temp_file.write(original.read())

    try:
        # Load module from temporary .py file
        spec = importlib.util.spec_from_file_location(module_name, temp_py_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        # Clean up temporary file
        Path(temp_py_path).unlink(missing_ok=True)


class TestUIFunctions(unittest.TestCase):
    """Test cases for enhanced UI display functions in lib/ui.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Load lib/ui.py as a module
        ui_path = Path(__file__).parent.parent.parent / "lib" / "ui.py"
        self.ui = load_script_as_module(ui_path, "ui_module")

        # Capture stdout for testing output
        self.captured_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output

    def tearDown(self):
        """Clean up after tests"""
        sys.stdout = self.original_stdout

    def get_output(self):
        """Get captured output and reset buffer"""
        output = self.captured_output.getvalue()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
        return output

    # Test format_size function (existing function)
    def test_format_size_bytes(self):
        """Test format_size with byte values"""
        self.assertEqual(self.ui.format_size(500), "500B")
        self.assertEqual(self.ui.format_size(1023), "1023B")

    def test_format_size_kilobytes(self):
        """Test format_size with kilobyte values"""
        self.assertEqual(self.ui.format_size(1024), "1.0K")
        self.assertEqual(self.ui.format_size(1536), "1.5K")
        self.assertEqual(self.ui.format_size(1024 * 1023), "1023.0K")

    def test_format_size_megabytes(self):
        """Test format_size with megabyte values"""
        self.assertEqual(self.ui.format_size(1024 * 1024), "1.0M")
        self.assertEqual(self.ui.format_size(1024 * 1024 * 2.5), "2.5M")

    def test_format_size_gigabytes(self):
        """Test format_size with gigabyte values"""
        self.assertEqual(self.ui.format_size(1024 * 1024 * 1024), "1.0G")
        self.assertEqual(self.ui.format_size(1024 * 1024 * 1024 * 5.25), "5.2G")

    def test_format_size_terabytes(self):
        """Test format_size with terabyte values"""
        self.assertEqual(self.ui.format_size(1024 * 1024 * 1024 * 1024), "1.0T")

    def test_format_size_zero(self):
        """Test format_size with zero value"""
        self.assertEqual(self.ui.format_size(0), "0B")

    # Test format_status_message function
    def test_format_status_message_with_emoji(self):
        """Test format_status_message with emoji support"""
        # Mock should_use_emojis to return True
        original_should_use_emojis = self.ui.should_use_emojis
        self.ui.should_use_emojis = lambda: True

        result = self.ui.format_status_message("Test message", "✅", "SUCCESS")
        self.assertEqual(result, "✅ Test message")

        # Restore original function
        self.ui.should_use_emojis = original_should_use_emojis

    def test_format_status_message_with_fallback(self):
        """Test format_status_message with text fallback"""
        # Mock should_use_emojis to return False
        original_should_use_emojis = self.ui.should_use_emojis
        self.ui.should_use_emojis = lambda: False

        result = self.ui.format_status_message("Test message", "✅", "SUCCESS")
        self.assertEqual(result, "SUCCESS: Test message")

        # Restore original function
        self.ui.should_use_emojis = original_should_use_emojis

    def test_format_status_message_no_prefix(self):
        """Test format_status_message with no prefix"""
        original_should_use_emojis = self.ui.should_use_emojis
        self.ui.should_use_emojis = lambda: False

        result = self.ui.format_status_message("Test message", "✅", "")
        self.assertEqual(result, "Test message")

        # Restore original function
        self.ui.should_use_emojis = original_should_use_emojis

    # Test display_item_list function
    def test_display_item_list_basic(self):
        """Test display_item_list with basic list"""
        items = ["file1.mp4", "file2.mkv", "file3.avi"]
        self.ui.display_item_list(items, "Test Files")

        output = self.get_output()
        self.assertIn("Test Files (3):", output)
        self.assertIn("  - file1.mp4", output)
        self.assertIn("  - file2.mkv", output)
        self.assertIn("  - file3.avi", output)

    def test_display_item_list_numbered(self):
        """Test display_item_list with numbered list"""
        items = ["first.mp4", "second.mkv"]
        self.ui.display_item_list(items, "Numbered Files", numbered=True)

        output = self.get_output()
        self.assertIn("Numbered Files (2):", output)
        self.assertIn("  1. first.mp4", output)
        self.assertIn("  2. second.mkv", output)

    def test_display_item_list_no_count(self):
        """Test display_item_list without count in title"""
        items = ["file1.mp4"]
        self.ui.display_item_list(items, "Files", show_count=False)

        output = self.get_output()
        self.assertIn("Files:", output)
        self.assertNotIn("(1)", output)

    def test_display_item_list_empty(self):
        """Test display_item_list with empty list"""
        self.ui.display_item_list([], "Empty List")

        output = self.get_output()
        self.assertIn("Empty List: None found", output)

    def test_display_item_list_no_title(self):
        """Test display_item_list without title"""
        items = ["file1.mp4", "file2.mkv"]
        self.ui.display_item_list(items)

        output = self.get_output()
        self.assertIn("  - file1.mp4", output)
        self.assertIn("  - file2.mkv", output)
        self.assertNotIn(":", output)  # No title should mean no colon

    def test_display_item_list_custom_indent(self):
        """Test display_item_list with custom indentation"""
        items = ["file1.mp4"]
        self.ui.display_item_list(items, indent="    ")

        output = self.get_output()
        self.assertIn("    - file1.mp4", output)

    # Test display_summary_list function
    def test_display_summary_list_basic(self):
        """Test display_summary_list with basic summary data"""
        summary = {"Files processed": 15, "Files skipped": 3, "Errors encountered": 1}
        self.ui.display_summary_list(summary, "Processing Summary")

        output = self.get_output()
        self.assertIn("Processing Summary:", output)
        self.assertIn("Files processed   : 15", output)
        self.assertIn("Files skipped     : 3", output)
        self.assertIn("Errors encountered: 1", output)

    def test_display_summary_list_no_title(self):
        """Test display_summary_list without title"""
        summary = {"Count": 42}
        self.ui.display_summary_list(summary)

        output = self.get_output()
        self.assertIn("Count: 42", output)
        # Without title, output is just "Count: 42" (no leading spaces)
        self.assertEqual(output.strip(), "Count: 42")

    def test_display_summary_list_empty(self):
        """Test display_summary_list with empty dictionary"""
        self.ui.display_summary_list({}, "Empty Summary")

        output = self.get_output()
        self.assertIn("Empty Summary:", output)

    def test_display_summary_list_alignment(self):
        """Test display_summary_list key alignment"""
        summary = {"Short": 1, "Very long key name": 2}
        self.ui.display_summary_list(summary)

        output = self.get_output()
        lines = output.strip().split("\n")
        # Both lines should align at the colon
        short_line = [line for line in lines if "Short" in line][0]
        long_line = [line for line in lines if "Very long key name" in line][0]

        # Check that the shorter key is padded to align with longer key
        self.assertIn("Short             :", short_line)
        self.assertIn("Very long key name:", long_line)

    # Test display_progress_item function
    def test_display_progress_item_basic(self):
        """Test display_progress_item with basic parameters"""
        self.ui.display_progress_item(3, 10, "movie.mp4")

        output = self.get_output()
        self.assertEqual(output.strip(), "[3/10] Processing: movie.mp4")

    def test_display_progress_item_custom_prefix(self):
        """Test display_progress_item with custom prefix"""
        self.ui.display_progress_item(1, 5, "file.txt", "Analyzing")

        output = self.get_output()
        self.assertEqual(output.strip(), "[1/5] Analyzing: file.txt")

    def test_display_progress_item_large_numbers(self):
        """Test display_progress_item with large numbers"""
        self.ui.display_progress_item(999, 1000, "final.mp4")

        output = self.get_output()
        self.assertEqual(output.strip(), "[999/1000] Processing: final.mp4")

    # Test display_stats_table function
    def test_display_stats_table_basic(self):
        """Test display_stats_table with basic statistics"""
        stats = {"Total files": 1250, "Total size": 15728640, "Average size": 12582}
        self.ui.display_stats_table(stats, "File Statistics")

        output = self.get_output()
        self.assertIn("File Statistics:", output)
        self.assertIn("Total files : 1250", output)
        self.assertIn("Total size  : 15728640", output)
        self.assertIn("Average size: 12582", output)

    def test_display_stats_table_with_formatter(self):
        """Test display_stats_table with value formatter"""
        stats = {"Total size": 15728640, "Average size": 12582}
        self.ui.display_stats_table(stats, "Formatted Stats", self.ui.format_size)

        output = self.get_output()
        self.assertIn("Total size  : 15.0M", output)
        self.assertIn("Average size: 12.3K", output)

    def test_display_stats_table_no_title(self):
        """Test display_stats_table without title"""
        stats = {"Count": 42}
        self.ui.display_stats_table(stats)

        output = self.get_output()
        self.assertIn("Count: 42", output)
        # Should not have extra newline at start since no title
        self.assertFalse(output.startswith("\n"))

    def test_display_stats_table_empty(self):
        """Test display_stats_table with empty stats"""
        self.ui.display_stats_table({}, "Empty Stats")

        output = self.get_output()
        self.assertEqual(output, "")  # Should produce no output

    # Test display_results_table function
    def test_display_results_table_basic(self):
        """Test display_results_table with basic data"""
        data = [
            ["file1.mp4", "1.2 GB", "Processed"],
            ["file2.mkv", "850 MB", "Skipped"],
        ]
        headers = ["Filename", "Size", "Status"]
        self.ui.display_results_table(data, headers, "Processing Results")

        output = self.get_output()
        self.assertIn("Processing Results:", output)
        self.assertIn("Filename", output)
        self.assertIn("Size", output)
        self.assertIn("Status", output)
        self.assertIn("file1.mp4", output)
        self.assertIn("1.2 GB", output)
        self.assertIn("Processed", output)
        self.assertIn("file2.mkv", output)
        self.assertIn("850 MB", output)
        self.assertIn("Skipped", output)
        # Should have separator line
        self.assertIn("---", output)

    def test_display_results_table_no_title(self):
        """Test display_results_table without title"""
        data = [["test.mp4", "OK"]]
        headers = ["File", "Status"]
        self.ui.display_results_table(data, headers)

        output = self.get_output()
        self.assertIn("File", output)
        self.assertIn("Status", output)
        self.assertIn("test.mp4", output)
        self.assertIn("OK", output)
        # Should not start with newline since no title
        self.assertFalse(output.startswith("\n"))

    def test_display_results_table_empty_data(self):
        """Test display_results_table with empty data"""
        self.ui.display_results_table([], ["Header"], "Empty Table")

        output = self.get_output()
        self.assertIn("Empty Table: No data to display", output)

    def test_display_results_table_empty_headers(self):
        """Test display_results_table with empty headers"""
        data = [["data"]]
        self.ui.display_results_table(data, [], "No Headers")

        output = self.get_output()
        self.assertIn("No Headers: No data to display", output)

    def test_display_results_table_column_width_limiting(self):
        """Test display_results_table with long content that gets truncated"""
        data = [["very_long_filename_that_should_be_truncated.mp4", "OK"]]
        headers = ["File", "Status"]
        self.ui.display_results_table(data, headers, max_width=20)

        output = self.get_output()
        # Should contain truncation indicator
        self.assertIn("...", output)

    def test_display_results_table_alignment(self):
        """Test display_results_table column alignment"""
        data = [["short.mp4", "OK"], ["very_long_filename.mp4", "Error"]]
        headers = ["Filename", "Status"]
        self.ui.display_results_table(data, headers)

        output = self.get_output()
        lines = output.strip().split("\n")

        # Find header line and data lines
        header_line = None
        data_lines = []
        for line in lines:
            if "Filename" in line and "Status" in line:
                header_line = line
            elif "short.mp4" in line or "very_long_filename.mp4" in line:
                data_lines.append(line)

        self.assertIsNotNone(header_line)
        self.assertEqual(len(data_lines), 2)

        # Check that all lines have pipe separators and basic alignment
        self.assertIn("|", header_line)
        for data_line in data_lines:
            self.assertIn("|", data_line)

        # Verify that both filenames and statuses are present
        full_output = "\n".join(data_lines)
        self.assertIn("short.mp4", full_output)
        self.assertIn("very_long_filename.mp4", full_output)
        self.assertIn("OK", full_output)
        self.assertIn("Error", full_output)


class TestUIFunctionsIntegration(unittest.TestCase):
    """Integration tests for UI functions with modular imports"""

    def setUp(self):
        """Set up test fixtures"""
        # Load lib/ui.py as a module
        ui_path = Path(__file__).parent.parent.parent / "lib" / "ui.py"
        self.ui = load_script_as_module(ui_path, "ui_module")

        # Capture stdout for testing output
        self.captured_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output

    def tearDown(self):
        """Clean up after tests"""
        sys.stdout = self.original_stdout

    def get_output(self):
        """Get captured output and reset buffer"""
        output = self.captured_output.getvalue()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
        return output

    def test_module_imports_correctly(self):
        """Test that the UI module imports correctly"""
        # Test that all expected functions are available
        expected_functions = [
            "display_banner",
            "format_size",
            "confirm_action",
            "format_status_message",
            "display_item_list",
            "display_summary_list",
            "display_progress_item",
            "display_stats_table",
            "display_results_table",
        ]

        for func_name in expected_functions:
            self.assertTrue(
                hasattr(self.ui, func_name),
                f"Function {func_name} not found in UI module",
            )
            self.assertTrue(
                callable(getattr(self.ui, func_name)),
                f"Attribute {func_name} is not callable",
            )

    def test_combined_ui_workflow(self):
        """Test a complete UI workflow using multiple functions"""
        # Note: Banner is suppressed in non-interactive mode, so we skip that

        # Display item list
        files = ["file1.mp4", "file2.mkv"]
        self.ui.display_item_list(files, "Files to process", numbered=True)

        # Display progress
        self.ui.display_progress_item(1, 2, "file1.mp4")

        # Display summary
        summary = {"Processed": 2, "Errors": 0}
        self.ui.display_summary_list(summary, "Final Summary")

        # Display stats table
        stats = {"Total size": 1048576}
        self.ui.display_stats_table(stats, "Statistics", self.ui.format_size)

        output = self.get_output()

        # Verify all components are present (except banner which is suppressed)
        self.assertIn("Files to process (2):", output)
        self.assertIn("1. file1.mp4", output)
        self.assertIn("[1/2] Processing: file1.mp4", output)
        self.assertIn("Final Summary:", output)
        self.assertIn("Processed: 2", output)
        self.assertIn("Statistics:", output)
        self.assertIn("Total size: 1.0M", output)


if __name__ == "__main__":
    unittest.main()
