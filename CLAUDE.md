# 🏗️ ArchiMate MCP Server - Claude Code Assistant Configuration

## Project Overview
Professional Model Context Protocol server for ArchiMate enterprise architecture modeling with AI-powered diagram generation and PlantUML integration.

## Key Features
- **Complete ArchiMate 3.2 Support**: All 55+ elements across 7 layers
- **Full Architecture Generation**: Automated enterprise architecture following ArchiMate Cookbook methodology
- **PlantUML Integration**: Native PlantUML code generation with ArchiMate styling
- **Model Validation**: ArchiMate specification compliance checking
- **Enterprise Templates**: Pre-built viewpoints, patterns, and industry-specific templates
- **Claude Desktop Integration**: Seamless integration with Claude Desktop via MCP
- **Multi-View Architecture**: Motivation, Strategy, Business, Application, Technology, Physical, Implementation layers

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
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=archi_mcp --cov-report=html
```

### Server Operations
```bash
# Start MCP server for Claude Desktop
uv run python src/archi_mcp/server.py

# Test server initialization
uv run python -c "from archi_mcp.server import mcp; print('✅ Server ready')"
```

### PlantUML Validation
```bash
# Validate all generated diagrams
uv run python tests/test_plantuml_validation.py

# Test diagram generation
uv run python examples/generate_sample_diagrams.py
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
Generate complete ArchiMate diagrams from structured input with elements and relationships.
- Supports all ArchiMate 3.2 elements and relationships
- Configurable layout and styling options
- Returns PlantUML code with statistics

### 2. `add_archimate_element(element_type: str, id: str, name: str, layer: str, ...) -> str`
Add single ArchiMate element to existing diagram.
- All 7 ArchiMate layers supported
- Optional description, stereotype, and properties
- Automatic aspect detection (Active/Passive Structure, Behavior)

### 3. `add_archimate_relationship(id: str, from_element: str, to_element: str, relationship_type: str, ...) -> str`
Add relationship between ArchiMate elements.
- All 12 ArchiMate relationship types
- Optional direction, description, and labels
- Automatic validation against ArchiMate rules

### 4. `validate_archimate_model(strict: bool = False) -> str`
Validate ArchiMate model against ArchiMate 3.2 specification.
- Standard and strict validation modes
- Comprehensive error reporting
- Layer and relationship compatibility checking

### 5. `generate_archimate_template(template: TemplateInput) -> str`
Generate ArchiMate diagram from predefined templates.
- **Viewpoints**: Layered, Service Realization, Application Cooperation, Technology Usage, Motivation
- **Patterns**: Three-Tier Architecture, Microservices, Event-Driven, CQRS
- **Industries**: Banking, E-commerce, Healthcare, Manufacturing

### 6. `export_archimate_diagram(title: str = None, description: str = None, output_path: str = None, ...) -> str`
Export ArchiMate diagram to PlantUML format with optional file output.
- File saving with automatic directory creation
- Configurable titles and descriptions
- Optional diagram clearing after export

### 7. `generate_full_architecture(architecture: FullArchitectureInput) -> str`
Generate complete layered enterprise architecture following ArchiMate methodology.
- **Multiple Coordinated Views**: Motivation, Business Model Canvas, Value Stream, Strategy & Capability, Layered Views, Interaction Views, Application & Technology Structure, Implementation Roadmap
- **ArchiMate Cookbook Methodology**: Automated architecture generation following enterprise architecture best practices
- **Configurable Scope**: Enterprise, system, application, or component level
- **Implementation Phases**: 1-6 phases with detailed roadmap

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
      "args": ["run", "--directory", "/Users/patrik/Projects/archi-mcp", "python", "src/archi_mcp/server.py"],
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
- Ensure Java is installed for PlantUML
- Check element and relationship naming compliance
- Use strict validation mode for detailed error reporting

## Quality Metrics
- ✅ **Comprehensive test suite** - Full coverage
- ✅ **Type hints** throughout codebase
- ✅ **Professional documentation**
- ✅ **FastMCP 2.8+ integration**
- ⚡ **Fast performance** (<1s tool response)
- 🏗️ **Production architecture demos** - 8 complete views

## License
MIT License - Open source, free for commercial and personal use.

## Author
**Mgr. Patrik Skovajsa, Claude Code Assistant**

---

**🎯 Production Ready:** Complete MCP server for AI-powered ArchiMate enterprise architecture modeling.