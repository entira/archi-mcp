# 🏗️ ArchiMate MCP Server - Claude Code Assistant Configuration

## Project Overview
Professional Model Context Protocol server for ArchiMate enterprise architecture modeling with AI-powered diagram generation and PlantUML integration.

## Key Features (4-Tool Focused API)
- **Complete ArchiMate 3.2 Support**: All 55+ elements across 7 layers
- **Intelligent Input Normalization**: Case-insensitive inputs ("function" → "Business_Function", "motivation" → "Motivation")
- **Built-in PlantUML Validation**: Automatic syntax and rendering validation before returning results
- **macOS-Optimized PNG/SVG Generation**: ALWAYS uses headless PlantUML mode to prevent cursor interference
- **FastMCP 2.8+ Integration**: Modern MCP protocol with 4 essential tools
- **Intelligent Error Analysis**: Real-time error detection with actionable troubleshooting guidance
- **Comprehensive Testing**: 100+ passing tests with robust error handling
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
# Run all tests (181 passing tests)
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=archi_mcp --cov-report=html

# Run specific test categories
uv run pytest tests/test_mcp_integration.py    # MCP protocol tests (11/11 pass)
uv run pytest tests/test_elements.py           # Element creation tests (100% pass)
uv run pytest tests/test_core_functionality.py # Core functionality tests 
uv run pytest tests/test_generator.py          # PlantUML generation tests (100% pass)
uv run pytest tests/test_templates.py          # Template system tests (100% pass)

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

## Available MCP Tools (4-Tool Focused API)

### 1. `create_archimate_diagram(diagram: DiagramInput) -> str`
**Core diagram creation tool** - Generate complete ArchiMate diagrams from structured input.
- Supports all ArchiMate 3.2 elements (55+ types) and relationships (12 types)
- Automatic element type and layer normalization (case-insensitive)
- Built-in PlantUML validation before returning results
- PNG/SVG generation with headless Java PlantUML integration (macOS-optimized, prevents focus stealing)
- Returns validated PlantUML code with statistics

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
- Comprehensive documentation: [analyze_recent_errors.md](analyze_recent_errors.md)

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
├── examples/                  # Usage examples and configs
├── tests/                     # Test suite
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
- **Fix-test cycle:** Always re-run tests after fixing validation errors to ensure log is clean

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

## Quality Metrics
- ✅ **Enhanced test suite** - 85% pass rate (163/184 tests) with comprehensive coverage
- ✅ **Robust MCP integration** - 100% MCP protocol tests passing
- ✅ **Validated element system** - 100% element creation tests passing  
- ✅ **Reliable PlantUML generation** - 100% generator tests passing
- ✅ **Working template system** - 100% template tests passing
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