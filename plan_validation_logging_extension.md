# Validation Logging Extension Plan

## Current State Analysis

### What the `logs` Directory is Designed For
The `logs` directory is **designed but not fully implemented** in the ArchiMate MCP project:

#### 1. **Intended Purpose**
- Store validation errors in `logs/validation_errors.jsonl` (JSONL format)
- Support real-time error monitoring and analysis
- Provide debugging data for the `analyze_recent_errors` MCP tool

#### 2. **Current Implementation Gap**
- Directory exists but is empty
- Documentation extensively references it (`CLAUDE.md` has 15+ references)
- Tests expect it to work (`test_analysis_tools.py` line 181)
- **But actual validation error logging is NOT implemented**

#### 3. **What Works Currently**
- Sophisticated logging setup with Loguru (`src/archi_mcp/utils/logging.py`)
- Failed attempts logging in `exports/failed_attempts/` with timestamped directories
- `analyze_recent_errors` tool exists (but doesn't use logs/)
- Comprehensive test coverage expectations

#### 4. **What's Missing**
- Actual writing to `logs/validation_errors.jsonl`
- Integration between validation errors and logs directory
- Auto-creation of logs directory
- JSONL format error logging

## Code References Found

### 1. **Documentation References** (`CLAUDE.md`)
```bash
# Check validation error logs before and after testing!
cat logs/validation_errors.jsonl
tail -f logs/validation_errors.jsonl
grep "element_type" logs/validation_errors.jsonl | head -5
wc -l logs/validation_errors.jsonl  # Should show 0 lines for clean tests
```

### 2. **Test Expectations** (`tests/test_analysis_tools.py:181`)
```python
error_log_path = Path("logs/validation_errors.jsonl")
```

### 3. **Analysis Tool** (`src/archi_mcp/server.py:2201-2265`)
```python
@mcp.tool()
def analyze_recent_errors(minutes: int = 10) -> str:
    """Analyze recent PlantUML generation errors and provide troubleshooting guidance."""
```

### 4. **Logging Infrastructure** (`src/archi_mcp/utils/logging.py`)
- Uses **Loguru** for enhanced logging
- Supports file output with rotation (10MB files, 7 days retention)
- Includes backtrace and diagnostic information

## Current Alternative: Failed Attempts Logging

Instead of `logs/`, the project currently uses `exports/failed_attempts/`:
- Each failed attempt gets a timestamped directory: `exports/failed_attempts/20250703_165523/`
- Contains: `input.json`, `diagram.puml`, `generation.log`
- This works well for comprehensive failure debugging

## Implementation Plan

### Phase 1: Implement Validation Error Logging
1. **Create JSONL validation error logging**
   - Add validation error capture in `src/archi_mcp/archimate/validator.py`
   - Write errors to `logs/validation_errors.jsonl` in JSONL format
   - Auto-create logs directory if needed

### Phase 2: Integrate with Analysis Tool
2. **Update `analyze_recent_errors` tool**
   - Read from `logs/validation_errors.jsonl`
   - Parse JSONL format for time-based analysis
   - Categorize errors (Empty Model, Orphaned Relationships, System Errors)

### Phase 3: Error Categorization
3. **Implement proper error categorization**
   - Structure JSONL entries with consistent format
   - Include timestamps, error types, context
   - Support filtering by time windows

### Phase 4: Testing Integration
4. **Update test suite**
   - Ensure tests create and clean validation error logs
   - Test the complete validation error flow
   - Verify log rotation and cleanup

## Recommendation

The logs directory represents a **well-designed logging architecture** that's documented and tested but not yet fully implemented in the runtime code. The current failed attempts logging in `exports/` is working well, but the validation error logging to `logs/` needs to be implemented to match the documentation and tests.

**Priority**: Medium - The current error handling works, but completing this feature would provide better debugging capabilities and match the documented behavior.