# 🏗️ ArchiMate MCP Server - Claude Code Assistant Configuration

## Project Overview
Professional Model Context Protocol server for ArchiMate enterprise architecture modeling with AI-powered diagram generation and PlantUML integration.

## Key Features
- **Complete ArchiMate 3.2 Support**: All 55+ elements across 7 layers
- **Intelligent Input Normalization**: Case-insensitive inputs ("function" → "Business_Function", "motivation" → "Motivation")
- **Built-in PlantUML Validation**: Automatic syntax and rendering validation before returning results
- **macOS-Optimized PNG/SVG Generation**: ALWAYS uses headless PlantUML mode to prevent cursor interference
- **FastMCP 2.8+ Integration**: Modern MCP protocol with image support
- **Intelligent Error Analysis**: Real-time error detection with actionable troubleshooting guidance
- **Comprehensive Testing**: 169+ passing tests with 69% coverage and robust error handling
- **Claude Desktop Ready**: Optimized configuration for seamless integration
- **Multi-Layer Support**: All 7 ArchiMate layers with proper aspect detection

## Tech Stack
- **Python 3.11+** with modern async/await
- **FastMCP 2.8+** for MCP protocol implementation
- **UV** for fast package management
- **PlantUML** for diagram generation and validation
- **Pydantic 2.0+** for data validation and input schemas

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --extra dev
```

### Testing
```bash
# Run all tests (169 passing tests, 69% coverage)
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=archi_mcp --cov-report=html

# Run specific test categories
uv run pytest tests/test_server.py             # Core server functionality tests (100% pass)
uv run pytest tests/test_server_coverage.py    # Server coverage improvement tests (100% pass)
uv run pytest tests/test_analysis_tools.py     # Analysis tools comprehensive tests (100% pass)
uv run pytest tests/test_generator_coverage.py # Generator edge case and coverage tests (95% pass)
uv run pytest tests/test_validation_mandatory.py # Validation and MCP integration tests (100% pass)

# Enhanced Testing Workflow with Validation Error Monitoring
# IMPORTANT: Always check validation error logs before and after testing!

# 1. Check validation error logs before testing
cat logs/validation_errors.jsonl

# 2. If errors found, implement fix-test-retest cycle:
#    a) Analyze specific error in logs/validation_errors.jsonl
#    b) Fix the validation issue in source code
#    c) Run targeted tests: uv run pytest tests/test_validation.py -v
#    d) Re-run full test suite: uv run pytest
#    e) Verify error log is clean: cat logs/validation_errors.jsonl

# 3. Run comprehensive MCP testing (only if error log is clean)
uv run python -m pytest testing/ -v

# 4. Monitor validation errors during testing (in separate terminal)
tail -f logs/validation_errors.jsonl

# 5. Post-test validation check (must be empty for passing tests)
wc -l logs/validation_errors.jsonl  # Should show 0 lines for clean tests
```

### Comprehensive Test Suite Documentation

#### New Test Files (Created for Coverage Improvement)

**test_server_coverage.py**: Comprehensive server functionality tests
- Language detection with Slovak/English content
- Custom relationship validation with intelligent synonym matching
- Diagram validation error scenarios (invalid layers, element types, relationships)
- PlantUML validation timeout and error handling
- Element/layer/relationship normalization edge cases
- Configuration parameter handling and environment variables
- Aspect detection for unknown element types
- **Coverage Impact**: Improved server.py coverage from 58% to 62%

**test_analysis_tools.py**: Complete testing of all 4 MCP analysis tools
- `analyze_current_architecture`: Empty architecture, basic stats, layer distribution
- `analyze_recent_errors`: No errors, mock error log, different time windows, invalid JSON, file not found
- `test_element_normalization`: Case insensitive testing, comprehensive normalization validation
- Translation override functionality for Slovak relationship labels
- **Coverage Impact**: 100% test coverage for all analysis tools

**test_generator_coverage.py**: Generator edge cases and error scenarios
- Export error handling (permission errors, disk full, directory creation failures)
- PlantUML generation with complex descriptions, properties, stereotypes
- Layout overrides (direction, grouping, spacing, title/legend)
- Diagram validation (orphaned relationships, duplicate IDs, success scenarios)
- Statistics and information methods (layer usage, element/relationship counts)
- **Coverage Impact**: Partial coverage improvement (some import issues remain)

#### Test Strategy and Methodology
- **Mock-based testing**: Extensive use of `unittest.mock` for error simulation
- **Edge case focus**: Emphasis on boundary conditions and error paths
- **Real-world scenarios**: Tests based on actual usage patterns
- **Validation monitoring**: Integration with error log analysis
- **Performance considerations**: Tests designed to complete quickly while maintaining thoroughness

### Server Operations
```bash
# Start MCP server for Claude Desktop
uv run python src/archi_mcp/server.py

# Test server initialization
uv run python -c "from archi_mcp.server import mcp; print('✅ Server ready')"
```

### Enhanced Validation & Error Monitoring
```bash
# Check current validation error log (critical for debugging)
cat logs/validation_errors.jsonl

# View real-time validation errors during development
tail -f logs/validation_errors.jsonl

# Analyze validation error patterns
grep "element_type" logs/validation_errors.jsonl | head -5

# Test enhanced 4-step validation system
uv run python tests/test_enhanced_validation.py

# Test PlantUML rendering with comprehensive validation
uv run python tests/test_plantuml_validation.py

# Test diagram generation with validation
uv run python examples/generate_sample_diagrams.py

# Clear validation error log (use with caution)
> logs/validation_errors.jsonl
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## Available MCP Tools

### 1. `create_archimate_diagram(diagram: DiagramInput) -> str`
**Core diagram creation tool** - Generate complete ArchiMate diagrams from structured input.
- Supports all ArchiMate 3.2 elements (55+ types) and relationships (12 types)
- Automatic element type and layer normalization (case-insensitive)
- Built-in PlantUML validation before returning results
- PNG/SVG generation with headless Java PlantUML integration (macOS-optimized, prevents focus stealing)
- **Automatic HTTP server** - Starts web server for serving diagrams
- **Direct viewing URLs** - Returns HTTP URLs for immediate diagram viewing
- Returns validated PlantUML code with statistics and viewing URLs

### 2. `analyze_current_architecture() -> str`
**Architecture health assessment tool** - Analyze current architecture state and provide insights.
- Element and relationship statistics by layer
- Architecture completeness assessment
- Layer distribution analysis
- Model health indicators and readiness check

### 3. `test_element_normalization() -> str`
**Element validation tool** - Test element type normalization across all ArchiMate layers.
- Validates case-insensitive input handling ("function" → "Business_Function")
- Tests common element type mappings and transformations
- Verifies layer and relationship type normalization
- Essential for troubleshooting input compatibility issues

### 4. `analyze_recent_errors(minutes: int = 10) -> str`
**Intelligent error analysis tool** - Analyze recent diagram generation errors with actionable guidance.
- Real-time error detection and pattern recognition
- Categorized error reporting (Empty Model, Orphaned Relationships, System Errors)
- Contextual troubleshooting recommendations
- Configurable time window analysis (1-60 minutes)
- Monitors validation error log: `logs/validation_errors.jsonl`


## Project Structure
```
archi-mcp/
├── src/archi_mcp/
│   ├── __init__.py
│   ├── server.py              # Main FastMCP server (480+ lines)
│   ├── archimate/             # ArchiMate modeling components
│   │   ├── elements/          # Element definitions by layer
│   │   ├── relationships.py   # Relationship types and validation
│   │   ├── generator.py       # PlantUML code generation
│   │   └── validator.py       # Model validation
│   ├── templates/             # Template library
│   │   ├── viewpoints.py      # ArchiMate viewpoints
│   │   ├── patterns.py        # Architecture patterns
│   │   └── industry.py        # Industry-specific templates
│   ├── utils/                 # Utilities
│   └── architecture_generator.py # Full architecture generation
├── docs/                      # Comprehensive documentation
├── tests/                     # Comprehensive test suite (115+ tests, 69% coverage)
│   ├── test_server.py             # Core server functionality tests
│   ├── test_server_coverage.py    # Server coverage improvement tests
│   ├── test_analysis_tools.py     # Analysis tools comprehensive tests
│   ├── test_generator_coverage.py # Generator edge case and coverage tests
│   └── test_validation_mandatory.py # Validation and MCP integration tests
├── pyproject.toml            # Project configuration
└── README.md                 # Project overview
```

## Claude Desktop Integration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/patrik/Projects/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/Users/patrik/Projects/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "INFO",
        "ARCHI_MCP_STRICT_VALIDATION": "true"
      }
    }
  }
}
```

## Architecture Generation Examples

### Basic Three-Tier Architecture
```
Generate an ArchiMate diagram showing a three-tier architecture with:
- A business service layer
- An application component layer  
- A technology infrastructure layer
Include the relationships between these layers.
```

### Full Enterprise Architecture
```
Generate a complete enterprise architecture for an online banking portal 
including motivation view, layered view, application structure, and 
implementation roadmap with 4 phases.
```

### Industry-Specific Template
```
Generate an ArchiMate diagram using the banking industry template and 
customize it for a digital transformation project.
```

## Common Issues & Solutions

### "No module named 'fastmcp'"
```bash
uv sync  # Install dependencies
```

### "spawn python ENOENT"
Use full path in Claude Desktop config with `uv` command and `--directory` flag.

### PlantUML validation errors
- **First step:** Check validation error log: `cat logs/validation_errors.jsonl`
- **Element normalization issues:** Check if kebab-case elements are properly converted (business-actor → Business_Actor)
- **Rendering failures:** Ensure Java is installed for PlantUML jar execution
- **JSONL log entries:** Each validation failure is logged with full context for debugging
- **Enhanced fix-test-retest cycle:** 
  1. Check error log before testing: `cat logs/validation_errors.jsonl`
  2. Fix validation issues in source code
  3. Run targeted tests: `uv run pytest tests/test_validation_mandatory.py -v`
  4. Re-run full test suite: `uv run pytest`
  5. Verify error log is clean: `wc -l logs/validation_errors.jsonl` (should be 0)

### PlantUML Headless Mode (CRITICAL REQUIREMENT)
- **ALWAYS use headless mode:** All PlantUML jar executions MUST include `-Djava.awt.headless=true`
- **Focus stealing prevention:** Without headless mode, PlantUML steals desktop focus during PNG/SVG generation
- **Implemented everywhere:** Both server.py and generator.py use headless mode consistently
- **Test compatibility:** All tests and development commands use headless mode
- **Example command:** `java -Djava.awt.headless=true -jar plantuml.jar -tpng diagram.puml`
- **Never remove this flag:** Removing headless mode will cause desktop focus interruption

### Image generation not working in Claude Desktop
- **Multi-format approach:** Server generates PNG files + Base64 URLs + Online preview URLs
- **Check image files:** Look for timestamped PNG files in `/tmp/archimate_*.png`
- **Base64 URLs:** Copy data URLs directly into browser for immediate viewing
- **Online previews:** Use generated PlantUML server URLs for instant preview

### Validation error log monitoring
- **Before testing:** Always check `logs/validation_errors.jsonl` is empty
- **During development:** Use `tail -f logs/validation_errors.jsonl` to monitor real-time errors
- **After fixes:** Verify log is clean with `wc -l logs/validation_errors.jsonl` (should be 0)
- **Pattern analysis:** Use `grep` to find common error patterns for systematic fixes

## Development Guidelines

### Adding New MCP Tools

```python
@mcp.tool()
def your_new_archimate_tool(param1: str, param2: Optional[ElementInput] = None) -> str:
    """
    Tool description for MCP protocol.
    
    Args:
        param1: Required string parameter
        param2: Optional ArchiMate element parameter
        
    Returns:
        Formatted string response with PlantUML code
        
    Raises:
        ArchiMateValidationError: If param1 is invalid
        ArchiMateGenerationError: If generation fails
    """
    # 1. Input validation
    if not param1.strip():
        return "❌ Error: param1 cannot be empty"
    
    # 2. ArchiMate-specific logic
    try:
        if param2:
            element = _create_element_from_data(param2)
            generator.add_element(element)
        
        result = generator.generate_plantuml(title=param1)
        
    except ArchiMateValidationError as e:
        return f"❌ Validation Error: {str(e)}"
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return f"❌ Error: {str(e)}"
    
    # 3. Format response with statistics
    stats = {
        "elements": generator.get_element_count(),
        "relationships": generator.get_relationship_count()
    }
    
    return f"✅ Success: {param1}\n\nStatistics:\n- Elements: {stats['elements']}\n- Relationships: {stats['relationships']}\n\nPlantUML Code:\n```plantuml\n{result}\n```"
```

### Testing New Features

```python
# tests/test_new_feature.py
import pytest
from archi_mcp.server import your_new_archimate_tool
from archi_mcp.server import ElementInput

class TestNewArchiMateTool:
    def test_basic_functionality(self):
        """Test basic tool functionality."""
        result = your_new_archimate_tool("test input")
        
        assert isinstance(result, str)
        assert "✅ Success" in result
        assert "```plantuml" in result
    
    def test_with_element_input(self):
        """Test with ArchiMate element input."""
        element_input = ElementInput(
            id="test_element",
            name="Test Element",
            element_type="Business_Actor",
            layer="Business"
        )
        
        result = your_new_archimate_tool("test", element_input)
        
        assert "Business_Actor" in result
        assert "Test Element" in result
    
    def test_error_handling(self):
        """Test error handling."""
        result = your_new_archimate_tool("")  # Empty input
        
        assert "❌ Error" in result
        assert "cannot be empty" in result
```

### Custom ArchiMate Elements

```python
# src/archi_mcp/archimate/elements/custom.py
from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect

class CustomElement(ArchiMateElement):
    """Custom ArchiMate element for specialized use cases."""
    
    def __init__(self, id: str, name: str, custom_property: str = None, **kwargs):
        super().__init__(
            id=id,
            name=name,
            element_type="Custom_Element",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR,
            **kwargs
        )
        self.custom_property = custom_property
    
    def to_plantuml(self) -> str:
        """Generate custom PlantUML syntax."""
        return f"Business_Element({self.id}, \"{self.name}\")"
```

### Code Style Requirements

```python
# Type hints are REQUIRED for all ArchiMate functions
def create_business_element(element_type: str, 
                          id: str, 
                          name: str,
                          description: Optional[str] = None) -> ArchiMateElement:
    """
    Create business layer ArchiMate element.
    
    Args:
        element_type: Valid business element type (Business_Actor, Business_Process, etc.)
        id: Unique element identifier
        name: Human-readable element name
        description: Optional element description
        
    Returns:
        Configured ArchiMateElement instance
        
    Raises:
        ArchiMateValidationError: If element_type is not valid for business layer
    """
    # Validate business layer element types
    valid_business_types = ["Business_Actor", "Business_Role", "Business_Process", "Business_Service"]
    if element_type not in valid_business_types:
        raise ArchiMateValidationError(f"Invalid business element type: {element_type}")
    
    return ArchiMateElement(
        id=id,
        name=name,
        element_type=element_type,
        layer=ArchiMateLayer.BUSINESS,
        aspect=_get_aspect_for_element_type(element_type),
        description=description
    )

# Error handling is MANDATORY for all ArchiMate operations
try:
    plantuml_result = generator.generate_plantuml()
    validation_result = validator.validate_model(elements, relationships)
except ArchiMateGenerationError as e:
    logger.error(f"PlantUML generation failed: {e}")
    return f"❌ Generation Error: {str(e)}"
except ArchiMateValidationError as e:
    logger.error(f"Model validation failed: {e}")
    return f"❌ Validation Error: {str(e)}"
```

### ArchiMate Compliance Checklist

- [ ] **Element Types**: Only use valid ArchiMate 3.2 element types
- [ ] **Layer Assignment**: Elements assigned to correct layers
- [ ] **Relationship Rules**: Follow ArchiMate relationship matrix
- [ ] **PlantUML Syntax**: Generate valid PlantUML with ArchiMate includes
- [ ] **Documentation**: Include ArchiMate view descriptions
- [ ] **Testing**: Test with all 7 layers and relationship types
- [ ] **Examples**: Provide real-world architecture examples

## Quality Metrics
- ✅ **Enhanced test suite** - 169 passing tests (7 skipped) with 69% code coverage (1075/1548 lines)
- ✅ **Server coverage improvement** - server.py coverage improved from 58% to 62%
- ✅ **Generator coverage improvement** - generator.py coverage improved from 41% to 59%
- ✅ **Comprehensive analysis tools testing** - 100% passing tests for all 4 MCP tools
- ✅ **Language detection testing** - Slovak/English detection with validation
- ✅ **Error analysis testing** - Real-time error log analysis and monitoring
- ✅ **Type hints** throughout codebase
- ✅ **Professional documentation** 
- ✅ **FastMCP 2.8+ integration** with Image object support
- ⚡ **Performance optimized** - Sub-15s response for complex diagrams with PNG generation
- 🏗️ **Production architecture demos** - 8 complete views
- 🔧 **Real-time debugging** - MCP debug logging to /tmp with full traceability

## License
MIT License - Open source, free for commercial and personal use.

## Author
**Mgr. Patrik Skovajsa, Claude Code Assistant**

---

**🎯 Production Ready:** Complete MCP server for AI-powered ArchiMate enterprise architecture modeling.