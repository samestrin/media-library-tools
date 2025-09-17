# Enhanced Build System Documentation

## Overview

The enhanced build system removes the 1200-line ceiling constraint while maintaining the self-contained philosophy through modular library organization and selective inclusion capabilities.

## New Include Patterns

### Modular Includes
```python
# Include specific modules instead of entire utils.py
# {{include lib/core.py}}
# {{include lib/ui.py}}
# {{include lib/filesystem.py}}
# {{include lib/validation.py}}
```

### Module Responsibilities

#### lib/core.py
Essential utilities that most tools need:
- `is_non_interactive()` - Detects non-interactive environments
- `read_global_config_bool()` - Reads boolean configuration
- `acquire_lock()` / `release_lock()` - File locking functions
- `is_windows()` - Platform detection
- `should_use_emojis()` - Emoji support detection

#### lib/ui.py
User interface and formatting functions:
- `display_banner()` - Standardized banner display
- `format_status_message()` - Status message formatting
- `confirm_action()` - User confirmation prompts
- `format_size()` - Bytes to human-readable conversion

#### lib/filesystem.py
File and directory operations:
- Directory traversal utilities
- Path validation functions
- Safe file operation helpers
- Size calculation functions

#### lib/validation.py
Input validation and error handling:
- Argument validation functions
- Error handling patterns
- Data sanitization utilities
- Type checking helpers

## Migration Guide

### For Existing Tools
1. Replace `# {{include utils.py}}` with specific module includes
2. Update imports to reference new module locations
3. Test thoroughly to ensure functionality equivalence

### Example Migration

Before:
```python
#!/usr/bin/env python3
"""
Tool description
"""

# {{include utils.py}}

# Tool-specific code using functions like:
# display_banner()
# is_non_interactive()
# format_size()
```

After:
```python
#!/usr/bin/env python3
"""
Tool description
"""

# {{include lib/core.py}}
# {{include lib/ui.py}}

# Tool-specific code (functions used from modules above)
```

## Build System Features

### Dependency Analysis
The build system automatically analyzes source code to determine which modules are actually needed, optimizing the built tool size.

### Backward Compatibility
The old `# {{include utils.py}}` pattern continues to work during the transition period.

### Build-time Validation
- Verifies all included functions are used
- Warns about unused includes
- Detects circular dependencies

## Advanced Features (Future)

### Function-Level Inclusion
Planned for future implementation:
```python
# {{include lib/ui.py:display_banner,format_status_message}}
```

### Dependency Tree Visualization
Will provide visual representation of module dependencies for optimization.

## Best Practices

### Module Selection
Only include modules you actually use to minimize built tool size.

### Migration Strategy
Migrate tools gradually, one at a time, to minimize risk.

### Testing
Thoroughly test migrated tools to ensure functionality equivalence.

## Troubleshooting

### Common Issues
1. **Missing Function**: Ensure you've included the correct module
2. **Import Errors**: Check that all dependencies are included
3. **Build Failures**: Verify include syntax and module names

### Getting Help
- Check the compatibility report for known issues
- Review migration plan for guidance
- Consult performance analysis for optimization tips