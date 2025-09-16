# SABnzbd Edge Cases Fixture

This fixture contains edge case scenarios for testing error handling and boundary conditions in SABnzbd cleanup operations.

## Scenarios Included

### 1. Permission Issues (`permission_denied/`)
- Directory with restricted permissions to test permission error handling

### 2. Corrupted Downloads (`corrupted_download/`)
- Incomplete download with missing indicator files
- Tests handling of ambiguous download states

### 3. Empty Directories (`empty_dirs/`)
- Empty directories that should be cleaned up
- Tests directory cleanup logic

### 4. Special Characters (`special_chars/`)
- Files and directories with special characters in names
- Tests Unicode and special character handling

### 5. Nested Structure (`deep_nesting/`)
- Deeply nested directory structure
- Tests recursion limits and performance

### 6. Mixed Indicators (`mixed_indicators/`)
- Directory with both SABnzbd and BitTorrent indicators
- Tests conflict resolution logic