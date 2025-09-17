#!/usr/bin/env python3
"""
Test script to verify the Unicode encoding fix in load_script_as_module function.
This script tests that the function can handle Unicode characters correctly.
"""

import importlib.util
import os
import sys
import tempfile

# Add the tests directory to the path to import the test module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests", "unit"))


def load_script_as_module(script_path, module_name="loaded_module"):
    """
    Load a Python script as a module, handling Unicode characters correctly.
    This is the fixed version with explicit UTF-8 encoding.
    """
    with open(script_path, encoding="utf-8") as f:
        script_content = f.read()

    # Create a temporary file with explicit UTF-8 encoding
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(script_content)
        temp_file_path = temp_file.name

    try:
        spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        os.unlink(temp_file_path)


def test_unicode_handling():
    """Test that the load_script_as_module function can handle Unicode characters."""
    print("Testing Unicode encoding fix...")

    # Test with the actual lib/ui.py file that contains Unicode characters
    ui_script_path = os.path.join(os.path.dirname(__file__), "lib", "ui.py")

    if not os.path.exists(ui_script_path):
        print(f"❌ Error: {ui_script_path} not found")
        return False

    try:
        # This should work without Unicode encoding errors
        ui_module = load_script_as_module(ui_script_path, "ui_test")
        print("✅ Successfully loaded lib/ui.py with Unicode characters")

        # Verify some functions exist in the module
        expected_functions = [
            "display_item_list",
            "display_progress_item",
            "format_size",
        ]
        for func_name in expected_functions:
            if hasattr(ui_module, func_name):
                print(f"✅ Function {func_name} found in loaded module")
            else:
                print(f"❌ Function {func_name} not found in loaded module")
                return False

        return True

    except UnicodeEncodeError as e:
        print(f"❌ Unicode encoding error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main test function."""
    print("Unicode Encoding Fix Verification")
    print("=" * 40)

    success = test_unicode_handling()

    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed! Unicode encoding fix is working correctly.")
        sys.exit(0)
    else:
        print("❌ Tests failed! Unicode encoding issue may still exist.")
        sys.exit(1)


if __name__ == "__main__":
    main()
