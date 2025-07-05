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
- **Comprehensive Testing**: 182+ passing tests with 73% coverage and robust error handling
- **Claude Desktop Ready**: Optimized configuration for seamless integration
- **Multi-Layer Support**: All 7 ArchiMate layers with proper aspect detection

## Tech Stack
- **Python 3.11+** with modern async/await
- **FastMCP 2.8+** for MCP protocol implementation
- **UV** for fast package management
- **PlantUML 1.2025.4** for diagram generation and validation
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
# Run all tests (182 passing tests, 73% coverage)
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

# Enhanced Testing Workflow
# Run comprehensive test suite with multiple validation levels

# 1. Run all tests with coverage
uv run pytest --cov=archi_mcp --cov-report=html

# 2. Run specific test categories for targeted validation
uv run pytest tests/test_server.py             # Core server functionality tests
uv run pytest tests/test_analysis_tools.py     # Element normalization tests
uv run pytest tests/test_validation_mandatory.py # Validation and MCP integration tests

# 3. Run comprehensive MCP testing
uv run python -m pytest testing/ -v
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

**test_analysis_tools.py**: Complete testing of element normalization tool
- `test_element_normalization`: Case insensitive testing, comprehensive normalization validation
- Translation override functionality for Slovak relationship labels
- **Coverage Impact**: 100% test coverage for element normalization tool

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
# Test PlantUML rendering with comprehensive validation
uv run python -c "from archi_mcp.server import _validate_plantuml_renders; print(_validate_plantuml_renders('@startuml\nrectangle A\n@enduml'))"

# Test diagram generation with validation
uv run python -c "from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput; print('Testing validation')"

# Monitor failed attempts for debugging
ls exports/failed_attempts/
```

### Comprehensive Failed Attempts Debugging (NEW)
```bash
# CRITICAL DEBUG LOCATION: Complete failure context saved automatically
# When PNG generation fails, comprehensive debugging data is saved to:
# exports/failed_attempts/YYYYMMDD_HHMMSS_mmm/

# Check all failed attempts
ls exports/failed_attempts/

# Examine specific failure (replace timestamp with actual directory)
# Each failure directory contains 3 critical files:
cd exports/failed_attempts/20250702_191045_123/

# 1. INPUT.JSON - Complete user request that caused the failure
cat input.json  # Full DiagramInput with elements, relationships, layout

# 2. DIAGRAM.PUML - Generated PlantUML code that failed PNG rendering  
cat diagram.puml  # Exact PlantUML code sent to PlantUML jar

# 3. GENERATION.LOG - Complete debug trace with error context
cat generation.log  # Full debug log with timestamps, error details, PlantUML output

# Debug workflow for failures:
# 1. Find latest failure: ls -la exports/failed_attempts/ | tail -1
# 2. Examine input: cat exports/failed_attempts/TIMESTAMP/input.json
# 3. Test PlantUML: java -Djava.awt.headless=true -jar plantuml.jar -tpng exports/failed_attempts/TIMESTAMP/diagram.puml
# 4. Check logs: cat exports/failed_attempts/TIMESTAMP/generation.log

# Reproduce failure locally using saved context:
# Copy input.json content and use create_archimate_diagram MCP tool
# with exact same input to reproduce the issue

# Pattern Analysis across multiple failures
find exports/failed_attempts/ -name "generation.log" -exec grep -l "specific_error" {} \;
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
- **NEW: ArchiMate XML Exchange Export** - Automatic export to Open Group ArchiMate Exchange XML format (only after successful PNG generation)
- **Automatic HTTP server** - Starts web server for serving diagrams
- **Direct viewing URLs** - Returns HTTP URLs for immediate diagram viewing
- Returns validated PlantUML code with statistics and viewing URLs

**Output Files (saved to exports/YYYYMMDD_HHMMSS/):**
- `diagram.puml` - PlantUML source code
- `diagram.png` - Production-ready PNG image
- `diagram.svg` - Vector SVG format (if generated)
- `architecture.md` - Extended documentation with embedded images
- `generation.log` - Comprehensive debug information
- `metadata.json` - Diagram statistics and metadata
- **`archimate_model.archimate`** - ⭐ **NEW: Archi-compatible XML format** (Direct import into Archi tool)

### 2. `test_element_normalization() -> str`
**Element validation tool** - Test element type normalization across all ArchiMate layers.
- Validates case-insensitive input handling ("function" → "Business_Function")
- Tests common element type mappings and transformations
- Verifies layer and relationship type normalization
- Essential for troubleshooting input compatibility issues


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
│   ├── xml_export/            # ⭐ NEW: ArchiMate XML Exchange Export Module
│   │   ├── __init__.py        # Module initialization
│   │   ├── exporter.py        # XML exporter implementation
│   │   ├── validator.py       # XML validation functionality
│   │   └── templates.py       # XML templates and examples
│   └── architecture_generator.py # Full architecture generation
├── docs/                      # Comprehensive documentation
├── tests/                     # Comprehensive test suite (182+ tests, 73% coverage)
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
        "ARCHI_MCP_STRICT_VALIDATION": "true",
        "ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS": "true",
        "ARCHI_MCP_LOCK_SHOW_RELATIONSHIP_LABELS": "true"
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
- **Element normalization issues:** Check if kebab-case elements are properly converted (business-actor → Business_Actor)
- **Rendering failures:** Ensure Java is installed for PlantUML jar execution
- **Debug failed attempts:** Check `exports/failed_attempts/` for comprehensive failure logs
- **Enhanced fix-test-retest cycle:** 
  1. Run validation tests: `uv run pytest tests/test_validation_mandatory.py -v`
  2. Fix validation issues in source code
  3. Re-run full test suite: `uv run pytest`
  4. Check failed attempts: `ls exports/failed_attempts/` for any new failures

### PlantUML Headless Mode (CRITICAL REQUIREMENT)
- **ALWAYS use headless mode:** All PlantUML jar executions MUST include `-Djava.awt.headless=true`
- **Focus stealing prevention:** Without headless mode, PlantUML steals desktop focus during PNG/SVG generation
- **Implemented everywhere:** Both server.py and generator.py use headless mode consistently
- **Test compatibility:** All tests and development commands use headless mode
- **Manual testing:** When testing PlantUML manually, ALWAYS use headless mode
- **Debug commands:** All debugging commands in CLAUDE.md use headless mode
- **Example command:** `java -Djava.awt.headless=true -jar plantuml.jar -tpng diagram.puml`
- **Never remove this flag:** Removing headless mode will cause desktop focus interruption

#### All PlantUML Testing Commands (MANDATORY HEADLESS)
```bash
# Manual PlantUML testing (ALWAYS use headless mode)
java -Djava.awt.headless=true -jar plantuml.jar -tpng diagram.puml
java -Djava.awt.headless=true -jar plantuml.jar -tsvg diagram.puml

# Test PlantUML syntax validation
java -Djava.awt.headless=true -jar plantuml.jar -checkonly diagram.puml

# Debug failed attempts
java -Djava.awt.headless=true -jar plantuml.jar -tpng exports/failed_attempts/TIMESTAMP/diagram.puml

# Test with verbose output
java -Djava.awt.headless=true -jar plantuml.jar -tpng -v diagram.puml
```

### Image generation not working in Claude Desktop
- **Multi-format approach:** Server generates PNG files + Base64 URLs + Online preview URLs
- **Check image files:** Look for timestamped PNG files in `/tmp/archimate_*.png`
- **Base64 URLs:** Copy data URLs directly into browser for immediate viewing
- **Online previews:** Use generated PlantUML server URLs for instant preview

### Validation error monitoring
- **Before testing:** Run validation tests to ensure clean baseline
- **During development:** Monitor failed attempts in `exports/failed_attempts/` for debugging
- **After fixes:** Re-run test suite to verify all validation passes
- **Pattern analysis:** Examine failed attempt logs for systematic error patterns

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
- ✅ **Enhanced test suite** - 182 passing tests with 73% code coverage (1026/1587 lines)
- ✅ **Server coverage improvement** - server.py coverage improved from 58% to 68%
- ✅ **Generator coverage improvement** - generator.py coverage improved from 41% to 59%
- ✅ **Streamlined MCP tools** - 100% passing tests for 2 core MCP tools (simplified API)
- ✅ **Language detection testing** - Slovak/English detection with validation
- ✅ **Element normalization testing** - Comprehensive normalization validation
- ✅ **Type hints** throughout codebase
- ✅ **Professional documentation** 
- ✅ **FastMCP 2.8+ integration** with Image object support
- ⚡ **Performance optimized** - Sub-15s response for complex diagrams with PNG generation
- 🏗️ **Production architecture demos** - 8 complete views
- 🔧 **Real-time debugging** - MCP debug logging to /tmp with full traceability
- ⭐ **NEW: ArchiMate XML Exchange Export** - Standards-compliant Open Group XML format with modular design

## License
MIT License - Open source, free for commercial and personal use.

## Author
**Mgr. Patrik Skovajsa, Claude Code Assistant**

---

**🎯 Production Ready:** Complete MCP server for AI-powered ArchiMate enterprise architecture modeling.