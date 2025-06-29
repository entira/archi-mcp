# analyze_recent_errors Tool - Comprehensive Documentation

## Overview

The `analyze_recent_errors` tool is a diagnostic and troubleshooting utility designed to identify, analyze, and provide actionable guidance for recent errors in ArchiMate diagram generation. This tool replaces the previous debugging utilities with a focused, intelligent error analysis system.

## Purpose & Business Logic

### Primary Functions
1. **Real-time Error Detection**: Monitors recent ArchiMate diagram generation attempts for issues
2. **Pattern Recognition**: Identifies common error patterns and categorizes problems
3. **Intelligent Troubleshooting**: Provides specific, actionable recommendations based on error analysis
4. **Health Assessment**: Evaluates overall system health and readiness for complex diagram creation

### Key Capabilities
- **Temporal Analysis**: Configurable time window (default: 10 minutes) for error scanning
- **Multi-source Data Collection**: Analyzes server state, file system, and generator components
- **Categorized Error Reporting**: Groups errors by type (Empty Model, Orphaned Relationships, System Errors)
- **Contextual Recommendations**: Provides specific troubleshooting steps based on detected issues

## Function Signature

```python
@mcp.tool()
def analyze_recent_errors(minutes: int = 10) -> str:
    """Analyze recent PlantUML generation errors and provide troubleshooting guidance.
    
    Args:
        minutes: Look back this many minutes for error analysis (default: 10)
        
    Returns:
        Detailed analysis of recent errors with actionable recommendations
    """
```

## Input Parameters

### `minutes` (int, optional)
- **Default**: 10
- **Range**: 1-60 minutes recommended  
- **Purpose**: Defines the time window for error analysis
- **Usage Examples**:
  - `minutes=5`: Quick check for immediate issues
  - `minutes=10`: Standard troubleshooting window
  - `minutes=30`: Extended analysis for persistent problems

## Output Format

The tool returns a comprehensive markdown-formatted report with the following sections:

### Success Case (No Errors)
```markdown
✅ **No Recent Errors Found**

**Analysis Period:** Last 10 minutes
**Status:** System operating normally

### 📊 Current Health Metrics:
- PlantUML generation: ✅ Working
- Element normalization: ✅ Working  
- Validation pipeline: ✅ Working

### 📈 Recommendations:
- System is stable for architecture creation
- Ready for complex multi-layer diagrams
- All normalization functions operational
```

### Error Analysis Case
```markdown
🔍 **Recent Error Analysis** (Last 10 minutes)

## 📊 Summary
**Total Issues Found:** 3
**Error Categories:** 2
**Timeframe:** 21:45:30 - 21:35:30

## 📊 Error Categories:
- **Empty Model**: 1 occurrences
- **Orphaned Relationships**: 2 occurrences

## 🔎 Common Issues:
- No elements in current diagram - may need to create elements first
- Found 2 relationships with missing elements

## 🚀 Troubleshooting Steps:
- Create elements first using create_archimate_diagram with element data
- Ensure DiagramInput contains at least one ElementInput with valid layer and type
- Verify all relationship from_element and to_element IDs match existing element IDs
- Use analyze_current_architecture to check element/relationship consistency
```

## Error Categories

### 1. Empty Model
**Description**: No ArchiMate elements exist in the current diagram
**Common Causes**:
- Generator was cleared but no new elements added
- Failed element creation attempts
- Incorrect DiagramInput structure

**Recommendations**:
- Create elements using `create_archimate_diagram` with valid ElementInput data
- Verify element type and layer normalization
- Check input validation using `test_element_normalization`

### 2. Orphaned Relationships
**Description**: Relationships reference non-existent element IDs
**Common Causes**:
- Element IDs don't match relationship references
- Elements were removed but relationships remained
- Typos in element or relationship ID fields

**Recommendations**:
- Verify all `from_element` and `to_element` IDs exist
- Use `analyze_current_architecture` for consistency checking
- Recreate diagram with proper element-relationship mapping

### 3. System Error
**Description**: Internal server or component errors
**Common Causes**:
- PlantUML JAR file issues
- File system permissions
- Memory or resource constraints

**Recommendations**:
- Check server logs for detailed error information
- Verify PlantUML JAR accessibility
- Test with simple single-element diagrams

## Implementation Details

### Data Sources Analyzed

1. **Generator State**:
   - Current elements count (`generator._elements`)
   - Current relationships count (`generator._relationships`)
   - Element-relationship consistency validation

2. **File System**:
   - Recent PNG generation attempts in `/tmp/archimate_diagram_*.png`
   - File modification timestamps for temporal analysis
   - PlantUML output file validation

3. **Error Patterns**:
   - Element count validation
   - Relationship orphaning detection
   - Component state consistency checks

### Analysis Algorithm

```python
def _extract_recent_problems(minutes: int) -> Dict[str, Any]:
    """
    1. Define cutoff time (now - minutes)
    2. Scan generator state for inconsistencies
    3. Check file system for recent generation attempts
    4. Categorize errors by type and severity
    5. Generate targeted recommendations
    """
```

## Usage Scenarios

### Scenario 1: Troubleshooting Failed Diagram Creation
```
User creates diagram → Diagram fails to generate → Run analyze_recent_errors(5)
→ Get specific guidance on what went wrong
```

### Scenario 2: Preventive Health Check
```
Before complex diagram creation → Run analyze_recent_errors(10)
→ Verify system readiness and resolve any pending issues
```

### Scenario 3: Debugging Relationship Issues
```
Diagram shows missing connections → Run analyze_recent_errors(15)
→ Identify orphaned relationships and get fix recommendations
```

### Scenario 4: Performance Investigation
```
System seems slow → Run analyze_recent_errors(30)
→ Check for accumulating errors that might affect performance
```

## Best Practices

### When to Use
- After diagram generation failures
- Before creating complex multi-layer architectures
- When relationships appear incorrect or missing
- During development and testing of new diagram types

### Recommended Time Windows
- **5 minutes**: Quick immediate issue diagnosis
- **10 minutes**: Standard troubleshooting (default)
- **15-20 minutes**: Investigation of recurring problems
- **30+ minutes**: Extended analysis for persistent issues

### Integration with Other Tools
1. **Pre-creation check**: `analyze_recent_errors()` → `create_archimate_diagram()`
2. **Post-creation validation**: `create_archimate_diagram()` → `analyze_recent_errors()`
3. **Architecture health**: `analyze_current_architecture()` → `analyze_recent_errors()`
4. **Element testing**: `test_element_normalization()` → `analyze_recent_errors()`

## Technical Notes

### Performance Considerations
- Analysis is lightweight and completes in <1 second
- File system scans are limited to `/tmp` directory
- Memory usage is minimal (stores only summary data)

### Error Handling
- All exceptions are caught and reported as system errors
- Failed file system access is handled gracefully
- Generator state errors are categorized appropriately

### Logging Integration
- Uses standard ArchiMate MCP logging framework
- Errors are logged with `logger.error()` for debugging
- Analysis results can be cross-referenced with server logs

## Example Outputs

### Healthy System
```
✅ **No Recent Errors Found**

**Analysis Period:** Last 10 minutes
**Status:** System operating normally
```

### System with Issues
```
🔍 **Recent Error Analysis** (Last 10 minutes)

## 📊 Summary
**Total Issues Found:** 1
**Error Categories:** 1
**Timeframe:** 21:58:45 - 21:48:45

## 📊 Error Categories:
- **Empty Model**: 1 occurrences

## 🔎 Common Issues:
- No elements in current diagram - may need to create elements first

## 🚀 Troubleshooting Steps:
- Create elements first using create_archimate_diagram with element data
- Ensure DiagramInput contains at least one ElementInput with valid layer and type
- Check element normalization using test_element_normalization tool
```

## Relationship to Other Tools

This tool complements the simplified 4-tool ArchiMate MCP API:

1. **`create_archimate_diagram`**: Primary diagram creation
2. **`analyze_current_architecture`**: Current state analysis  
3. **`test_element_normalization`**: Element type validation
4. **`analyze_recent_errors`**: Error analysis and troubleshooting ← **This tool**

Together, these tools provide a complete workflow for robust ArchiMate diagram creation with built-in error detection and resolution guidance.