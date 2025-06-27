# Claude Instructions for ArchiMate MCP Server

## 🎯 Project Overview

This is the **ArchiMate MCP Server** - a specialized Model Context Protocol server for generating PlantUML ArchiMate diagrams with comprehensive enterprise architecture modeling support. The project demonstrates complete ArchiMate 3.2 specification compliance across all 7 architectural layers.

## 🏗️ Architecture Demonstration

The repository contains a **complete architectural blueprint** of the ArchiMate MCP Server itself, showcasing:

- **8 Comprehensive Views** across all 7 ArchiMate layers
- **100% Validated Diagrams** with proper PlantUML syntax
- **Real-world Enterprise Architecture** demonstrating tool capabilities
- **Cross-layer Traceability** from stakeholder goals to technical implementation

## 📁 Key Files and Structure

### Core Implementation
- `src/archi_mcp/server.py` - Main MCP server implementation
- `src/archi_mcp/archimate/` - ArchiMate modeling engine
- `src/archi_mcp/architecture_generator.py` - Full architecture generator
- `tests/` - Comprehensive test suite

### Architecture Documentation
- `ARCHITECTURE_OVERVIEW.md` - Executive summary and vision
- `ARCHITECTURE.md` - Detailed 7-layer architectural analysis  
- `VIEWING_GUIDE.md` - Guide for viewing generated diagrams
- `README.md` - Complete project documentation

### Generated Architecture Views
- `archi_mcp_motivation.puml/.svg` - Motivation Layer (stakeholders, goals)
- `archi_mcp_strategy_layer.puml/.svg` - Strategy Layer (capabilities, resources)
- `archi_mcp_layered_architecture.puml/.svg` - Business/App/Tech layers
- `archi_mcp_application_structure.puml/.svg` - Detailed app components
- `archi_mcp_technology_layer.puml/.svg` - Technology infrastructure
- `archi_mcp_physical_layer.puml/.svg` - Physical infrastructure
- `archi_mcp_implementation_migration.puml/.svg` - Implementation roadmap
- `archi_mcp_multi_layer_integration.puml/.svg` - Cross-layer integration

## 🛠️ Development Commands

### Setup and Testing
```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=archi_mcp --cov-report=html

# Type checking
uv run mypy src

# Linting
uv run ruff src tests

# Code formatting
uv run black src tests
uv run isort src tests
```

### MCP Server Operations
```bash
# Run MCP server
uv run archi-mcp

# Test MCP server locally
uv run python -m archi_mcp.server
```

### Diagram Generation and Validation
```bash
# Validate PlantUML diagrams
java -jar plantuml.jar -checkonly *.puml

# Generate SVG diagrams
java -jar plantuml.jar -tsvg *.puml

# Generate PNG diagrams  
java -jar plantuml.jar -tpng *.puml
```

## 🎯 When Working with This Project

### For Architecture Tasks
1. **Reference the existing architecture** - All 7 layers are fully documented
2. **Use the MCP server itself** - Generate diagrams using the tool
3. **Follow ArchiMate 3.2 standards** - Maintain compliance
4. **Validate all outputs** - Ensure PlantUML syntax is correct

### For Development Tasks
1. **Maintain test coverage** - All changes should be tested
2. **Follow Python best practices** - Use type hints, docstrings
3. **Preserve MCP compliance** - Don't break MCP protocol
4. **Document architectural changes** - Update relevant diagrams

### For Documentation Tasks
1. **Keep diagrams current** - Regenerate if architecture changes
2. **Maintain cross-references** - Ensure docs link correctly
3. **Validate diagram syntax** - All diagrams must render correctly
4. **Update viewing guides** - Help users navigate the architecture

## ⚙️ Technical Constraints

### ArchiMate Compliance
- Must follow ArchiMate 3.2 specification exactly
- All elements must use correct layer assignments
- Relationships must follow ArchiMate rules
- Diagrams must validate against standard

### PlantUML Requirements
- Correct syntax: `Layer_ElementType(id, "name")`
- Proper relationships: `Rel_RelationType(source, target, "label")`
- Valid includes: `!include <archimate/Archimate>`
- Background processing: Use `-Djava.awt.headless=true`

### MCP Protocol
- Implement all required MCP methods
- Provide proper tool schemas
- Handle errors gracefully
- Maintain backward compatibility

## 🚀 Architecture Generation Workflow

When generating new architectures:

1. **Start with Motivation** - Define stakeholders, goals, requirements
2. **Add Strategy Layer** - Define capabilities and resources
3. **Design Business Layer** - Define processes and services
4. **Structure Application Layer** - Define components and data flow
5. **Plan Technology Layer** - Define infrastructure and platforms
6. **Consider Physical Layer** - Define deployment and facilities
7. **Plan Implementation** - Define phases and deliverables
8. **Integrate Layers** - Show cross-layer relationships

## 🔍 Quality Assurance

### Before Committing
- [ ] All tests pass (`uv run pytest`)
- [ ] Type checking passes (`uv run mypy src`)
- [ ] Linting passes (`uv run ruff src`)
- [ ] Code formatted (`uv run black src`)
- [ ] All diagrams validate (`java -jar plantuml.jar -checkonly *.puml`)
- [ ] Documentation updated

### Architecture Validation
- [ ] ArchiMate 3.2 compliance maintained
- [ ] Cross-layer relationships valid
- [ ] All diagrams render correctly
- [ ] Viewing guides updated
- [ ] Examples functional

## 📞 Support and Resources

### Key Documentation
- [ArchiMate 3.2 Specification](https://www.opengroup.org/archimate-forum/archimate-overview)
- [PlantUML ArchiMate](https://plantuml.com/archimate-diagram)
- [Model Context Protocol](https://modelcontextprotocol.io/)

### Project References
- Repository demonstrates complete ArchiMate modeling
- All generated diagrams are self-referential examples
- Architecture serves as both documentation and validation

---

**Important**: This project is both a functional MCP server AND a complete architectural demonstration. When making changes, ensure both aspects remain aligned and validated.