<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# 🏗️ ArchiMate MCP Server - Claude Code Assistant Configuration

## Project Overview
> 📖 **For complete project overview, features, and user documentation, see [README.md](README.md)**

This document contains development-specific instructions and technical details for working with the ArchiMate MCP Server codebase.

## Tech Stack
> 📖 **For complete tech stack and dependencies, see [README.md](README.md#development)**

**Key Development Tools:**
- **UV** for fast package management and virtual environments
- **pytest** for comprehensive testing framework
- **black** + **ruff** for code formatting and linting
- **mypy** for type checking

## Requirements

- Python 3.11+
- uv (recommended) or pip
- Git
- Java 8+ (for PlantUML)
- PlantUML JAR file (see installation command below)

## Development Commands

### Setup
```bash
# Clone the repository
git clone https://github.com/entira/archi-mcp.git
cd archi-mcp

# Install dependencies
uv sync

# Install development dependencies
uv sync --dev

# Download PlantUML JAR (required for diagram generation)
curl -L https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -o plantuml.jar
```

### Testing
```bash
# Run all tests (194 passing tests, 66% coverage)
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=archi_mcp --cov-report=html

# Quick test for development
uv run pytest -xvs
```

### Test Coverage Summary

The test suite includes 194 passing tests with 66% code coverage across 13 test files:

- **Core Functionality**: Server operations, MCP protocol integration
- **ArchiMate Elements**: All 55+ element types across 7 layers
- **Relationships**: All 12 relationship types with validation
- **PlantUML Generation**: Syntax generation and validation
- **XML Export**: ArchiMate Exchange Format export and validation
- **Multi-Language**: Slovak/English detection and translation
- **Error Handling**: Comprehensive error scenarios and recovery
- **Layout Options**: Direction, spacing, grouping configurations

### Server Operations
```bash
# Start MCP server for Claude Desktop
uv run python src/archi_mcp/server.py

# Test server initialization
uv run python -c "from archi_mcp.server import mcp; print('✅ Server ready')"

# Generate sample diagrams
uv run python examples/generate_sample_diagrams.py

# Start HTTP server for diagram viewing (if needed separately)
uv run python -m http.server 8080 --directory exports
```

### Debugging
```bash
# Check generated exports
ls -la exports/

# View latest PlantUML code
cat exports/*/diagram.puml | head -20

# Test PlantUML rendering manually
java -Djava.awt.headless=true -jar plantuml.jar -tpng exports/*/diagram.puml

# Check HTTP server logs
tail -f exports/http_server.log

# Validate XML export
xmllint --noout exports/*/archimate_model.archimate
```

### Code Quality
```bash
# Format code
uv run black src tests
uv run isort src tests

# Lint code
uv run ruff src tests

# Type checking
uv run mypy src
```

## Available MCP Tools
> 📖 **For complete MCP tools documentation and usage examples, see [README.md](README.md#mcp-tools)**

**Development Notes:**
- Both tools are defined in `server.py` with full type annotations
- Input validation uses Pydantic models for schema enforcement
- Error handling includes comprehensive logging for debugging
- Tools are automatically discovered by FastMCP protocol

**Output Files (saved to exports/YYYYMMDD_HHMMSS/):**
- `diagram.puml` - PlantUML source code
- `diagram.png` - Production-ready PNG image
- `diagram.svg` - Vector SVG format (if generated)
- `architecture.md` - Extended documentation with embedded images
- `generation.log` - Comprehensive debug information
- `metadata.json` - Diagram statistics and metadata
- `archimate_model.archimate` - Archi-compatible XML format

## Project Structure
> 📖 **For complete project structure overview, see [README.md](README.md#project-structure)**

**Development-Specific Directories:**
```
tests/                     # 194 passing tests, 66% coverage
├── test_server.py         # Core server functionality
├── test_elements.py       # Element definitions
├── test_relationships.py  # Relationship validation
├── test_generator.py      # PlantUML generation
├── test_xml_export.py     # XML export functionality
└── ...                    # Additional test modules

exports/                   # Generated output (gitignored)  
plantuml.jar               # PlantUML JAR file (download separately)
.github/                   # CI/CD workflows (if any)
```

## Claude Desktop Integration
> 📖 **For complete Claude Desktop configuration, see [README.md](README.md#claude-desktop-configuration)**

**Development Configuration:**
- Use absolute path to your local development directory
- Enable `DEBUG` log level for development: `"ARCHI_MCP_LOG_LEVEL": "DEBUG"`
- Consider enabling experimental features for testing: `"ARCHI_MCP_ENABLE_VALIDATION": "true"`

**Example Development Config:**
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/your/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/path/to/your/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "DEBUG",
        "ARCHI_MCP_ENABLE_VALIDATION": "true",
        "ARCHI_MCP_ENABLE_AUTO_FIX": "true"
      }
    }
  }
}
```

## Interactive Designer Configuration

The ArchiMate MCP Server includes an optional **Interactive Designer** - a web-based UI for real-time diagram visualization and editing. By default, the designer is **disabled** (opt-in) to avoid unnecessary resource usage.

### Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ARCHI_MCP_DESIGNER_ENABLED` | boolean | `false` | Enable/disable interactive designer |
| `ARCHI_MCP_DESIGNER_PORT` | integer | `8080` | HTTP server port (falls back to 8081-8089 if busy) |

### Enable Interactive Designer

**Minimal Configuration (Enable Designer):**
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/patrik/Projects/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/Users/patrik/Projects/archi-mcp",
      "env": {
        "ARCHI_MCP_DESIGNER_ENABLED": "true",
        "ARCHI_MCP_DESIGNER_PORT": "8080"
      }
    }
  }
}
```

**Full Configuration (Designer + Defaults):**
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/patrik/Projects/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/Users/patrik/Projects/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "INFO",
        "ARCHI_MCP_DESIGNER_ENABLED": "true",
        "ARCHI_MCP_DESIGNER_PORT": "8080",
        "ARCHI_MCP_DEFAULT_DIRECTION": "top-bottom",
        "ARCHI_MCP_DEFAULT_SPACING": "comfortable",
        "ARCHI_MCP_DEFAULT_SHOW_TITLE": "true",
        "ARCHI_MCP_DEFAULT_SHOW_LEGEND": "false",
        "ARCHI_MCP_DEFAULT_GROUP_BY_LAYER": "false"
      }
    }
  }
}
```

### Using the Interactive Designer

When enabled, the designer is accessible at:
- **URL:** `http://127.0.0.1:8080/designer.html` (or configured port)
- **Auto-start:** Server starts automatically when MCP server launches
- **Features:** Real-time preview, layout controls, export downloads (PNG/SVG/XML/MD)

**Designer Features:**
- 🎨 Real-time diagram visualization with auto-refresh (2s)
- 🎛️ Interactive layout controls (direction, spacing, grouping)
- 💾 One-click export (PNG, SVG, PlantUML, XML, Markdown)
- 🔄 Auto-regeneration of missing exports
- 📜 **Diagram History Browser** - Browse, filter, and manage all historical diagrams
- 🔍 **Advanced Filtering** - Search by title, date range, element/relationship counts, layers
- 🍴 **Fork Workflow** - Load historical diagrams for editing without modifying originals
- 🗑️ **Bulk Operations** - Delete individual or multiple diagrams, auto-cleanup old exports
- ◀️ **Collapsible Sidebar** - Maximize diagram viewing space with toggle button
- 🔎 **Zoom Controls** - Zoom in/out (25%-500%), mouse wheel support (Ctrl+wheel)
- 📊 Diagram statistics (elements, relationships, layers)

**Workflow:**
1. Start Claude Desktop (designer starts on port 8080)
2. Open `http://127.0.0.1:8080/designer.html` in browser
3. Generate diagrams via Claude Code conversation
4. Designer auto-updates with new diagrams
5. Adjust layout options in designer → regenerates automatically
6. Switch to History tab to browse all past diagrams
7. Use filters to find specific diagrams by criteria
8. Fork historical diagrams to create new versions

**Note:** Designer is disabled by default to reduce resource usage. Enable only when needed for interactive visualization.

### Diagram History Management

The designer includes a comprehensive history management system accessible via the **History tab**:

**Core Features:**
- **History Index** - Fast cached index of all diagrams (`exports/history_index.json`)
- **Tab Navigation** - Switch between Editor and History views
- **Diagram Table** - Sortable table with title, element count, relationship count, date
- **Thumbnails** - Lazy-loaded diagram previews (first 20-50)
- **Protected Latest** - Current diagram cannot be deleted, marked with ⚡ badge

**Filtering & Search:**
- **Text Search** - Filter by diagram title (case-insensitive)
- **Date Range** - From/to date pickers for temporal filtering
- **Count Filters** - Min/max element and relationship count filters
- **Layer Filter** - Multi-select layer filter (Business, Application, Technology, etc.)
- **Apply/Clear** - Explicit filter application with clear button

**Operations:**
- **Fork & Edit** - Loads historical diagram title for creating new version
- **Delete** - Remove individual diagrams (except latest)
- **Bulk Delete** - Select multiple diagrams for batch deletion
- **Auto-Cleanup** - Delete diagrams older than 30 days (configurable, keeps latest 50)
- **Sort Columns** - Click column headers to sort by title, date, counts

**Technical Details:**
- **Backend API Endpoints:**
  - `GET /api/history` - List diagrams with filters (limit, offset, search, dates, counts, layers)
  - `GET /api/history/{timestamp}` - Get specific diagram metadata
  - `POST /api/history/{timestamp}/fork` - Fork diagram to current
  - `DELETE /api/history/{timestamp}` - Delete diagram export
  - `POST /api/history/cleanup` - Bulk cleanup old diagrams
- **Auto-Update** - Index rebuilds automatically after each diagram generation
- **Persistence** - Index file tracks 143+ diagrams with metadata
- **Performance** - Cached index enables sub-100ms loading for large histories

**UI Components:**
- **History Filters Panel** - Collapsible filter controls with apply/clear
- **History Table** - Grid layout with thumbnail, title, counts, date, actions
- **Bulk Actions Bar** - Shows selected count, delete button, cleanup button
- **Status Messages** - Loading states, error handling, success feedback

### Sidebar Collapse & Zoom

**Sidebar Collapse:**
- **Toggle Button** - Located top-right of sidebar (◀/▶ icon)
- **Collapsed Width** - 50px (from 380px)
- **Smooth Animation** - 0.3s ease transition
- **Keyboard Shortcut** - Click button to toggle (future: Cmd+B)
- **State Persistence** - Not saved across sessions (resets on reload)
- **Use Case** - Maximize diagram viewing space for large/complex architectures

**Zoom Controls:**
- **Location** - Bottom-right overlay on diagram container
- **Zoom Range** - 25% to 500% (min 0.25x, max 5x)
- **Zoom Step** - 25% per click
- **Controls:**
  - **+ Button** - Zoom in
  - **- Button** - Zoom out
  - **⟲ Button** - Reset to 100%
  - **Live Indicator** - Shows current zoom level (e.g., "150%")
- **Mouse Wheel** - Hold Ctrl (Windows/Linux) or Cmd (Mac) + scroll wheel
- **Transform** - CSS `transform: scale()` with center origin
- **Cursor** - Changes to grab/grabbing during pan (future feature)
- **Smooth Transitions** - 0.2s ease for button clicks

**Technical Implementation:**
- `toggleSidebar()` - Toggles `.collapsed` class, updates button icon
- `zoomIn()` / `zoomOut()` - Adjusts `currentZoom` variable (0.25-5.0)
- `zoomReset()` - Resets zoom to 1.0
- `updateZoom()` - Applies `transform: scale()` and updates UI
- `initZoomControls()` - Registers wheel event listener with `passive: false`
- Zoom state stored in `currentZoom` variable (not persisted)

## Architecture Examples
> 📖 **For complete architecture examples and demonstrations, see [README.md](README.md#complete-architecture-demonstration)**

**Development Testing:**
- Use `examples/generate_sample_diagrams.py` for testing
- Check `exports/` directory for generated outputs
- Test different language detection with Slovak/English content

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

### PlantUML Headless Mode (CRITICAL REQUIREMENT)
- **ALWAYS use headless mode:** All PlantUML jar executions MUST include `-Djava.awt.headless=true`
- **Focus stealing prevention:** Without headless mode, PlantUML steals desktop focus during PNG/SVG generation
- **Example command:** `java -Djava.awt.headless=true -jar plantuml.jar -tpng diagram.puml`

#### All PlantUML Testing Commands (MANDATORY HEADLESS)
```bash
# Manual PlantUML testing (ALWAYS use headless mode)
java -Djava.awt.headless=true -jar plantuml.jar -tpng diagram.puml
java -Djava.awt.headless=true -jar plantuml.jar -tsvg diagram.puml

# Test PlantUML syntax validation
java -Djava.awt.headless=true -jar plantuml.jar -checkonly diagram.puml

# Test with verbose output
java -Djava.awt.headless=true -jar plantuml.jar -tpng -v diagram.puml
```

### Image generation not working in Claude Desktop
- **Multi-format approach:** Server generates PNG files + Base64 URLs + Online preview URLs
- **Check image files:** Look for timestamped PNG files in `/tmp/archimate_*.png`
- **Base64 URLs:** Copy data URLs directly into browser for immediate viewing
- **Online previews:** Use generated PlantUML server URLs for instant preview

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
- ✅ **Test Suite** - 194 passing tests with 66% code coverage
- ✅ **Production Ready** - Version 1.0.0 stable release
- ✅ **Complete ArchiMate 3.2** - All 55+ elements, 12 relationships, 7 layers
- ✅ **Multi-Language** - Slovak/English auto-detection and translation
- ✅ **Multi-Format Export** - PlantUML, PNG, SVG, XML (experimental)
- ✅ **Type Hints** - Full type annotations throughout codebase
- ✅ **Documentation** - Comprehensive user and developer docs
- ✅ **FastMCP 2.8+** - Modern MCP protocol implementation
- ⚡ **Performance** - Sub-10s generation for complex diagrams
- 🏗️ **Production Demos** - 8 complete architecture views
- 🔧 **HTTP Server** - Built-in web server for instant viewing

## License
MIT License - Open source, free for commercial and personal use.

## Author
**Mgr. Patrik Skovajsa, Claude Code Assistant**

---

**🎯 Production Ready:** Complete MCP server for AI-powered ArchiMate enterprise architecture modeling.