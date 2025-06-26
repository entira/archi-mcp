# ArchiMate MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A specialized MCP (Model Context Protocol) server for generating PlantUML ArchiMate diagrams with comprehensive enterprise architecture modeling support.

## 🏗️ Overview

ArchiMate MCP Server fills a crucial gap in the MCP ecosystem by providing dedicated support for ArchiMate enterprise architecture modeling. While existing MCP servers offer general UML diagram generation, this server focuses specifically on ArchiMate 3.2 specification compliance with full support for all layers, elements, and relationships.

### Key Features

- **Complete ArchiMate 3.2 Support**: All 55+ elements across 7 layers
- **Full Relationship Matrix**: All 12 ArchiMate relationship types with directional variants
- **Enterprise Architecture Templates**: Pre-built viewpoints, patterns, and industry-specific templates
- **PlantUML Integration**: Native PlantUML code generation with ArchiMate styling
- **Model Validation**: ArchiMate specification compliance checking
- **Claude Desktop Integration**: Seamless integration with Claude Desktop via MCP

## 🚀 Quick Start

### Installation

```bash
# Install with uv (recommended)
uv add archi-mcp

# Or install with pip
pip install archi-mcp
```

### Claude Desktop Configuration

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "archi-mcp"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### Basic Usage

Once configured, you can use ArchiMate MCP Server through Claude Desktop:

```
Create an ArchiMate diagram showing a three-tier architecture with:
- A business service layer
- An application component layer  
- A technology infrastructure layer
Include the relationships between these layers.
```

## 🏛️ ArchiMate Support

### Supported Layers

- **Business Layer**: Actors, roles, processes, services, objects
- **Application Layer**: Components, services, interfaces, data objects
- **Technology Layer**: Nodes, devices, software, networks, artifacts
- **Physical Layer**: Equipment, facilities, distribution networks, materials
- **Motivation Layer**: Stakeholders, drivers, goals, requirements, principles
- **Strategy Layer**: Resources, capabilities, courses of action, value streams
- **Implementation Layer**: Work packages, deliverables, events, plateaus, gaps

### Supported Relationships

All 12 ArchiMate relationship types with directional variants:
- Access, Aggregation, Assignment, Association
- Composition, Flow, Influence, Realization
- Serving, Specialization, Triggering

### Junction Support

- And/Or junctions for complex relationship modeling
- Grouping and nesting capabilities

## 🛠️ MCP Tools

The server provides 6 comprehensive MCP tools:

### 1. `create_archimate_diagram`
Generate complete ArchiMate diagrams from structured input.

```json
{
  "elements": [
    {
      "id": "customer_service",
      "name": "Customer Service",
      "element_type": "Business_Service",
      "layer": "Business"
    }
  ],
  "relationships": [],
  "title": "Customer Service Architecture"
}
```

### 2. `add_archimate_element`
Add individual elements to existing diagrams.

```json
{
  "element_type": "Application_Component",
  "id": "crm_system", 
  "name": "CRM System",
  "layer": "Application"
}
```

### 3. `add_archimate_relationship`
Create relationships between elements.

```json
{
  "id": "realization_rel",
  "from_element": "crm_system",
  "to_element": "customer_service", 
  "relationship_type": "Realization"
}
```

### 4. `validate_archimate_model`
Validate models against ArchiMate 3.2 specification.

```json
{
  "strict": true
}
```

### 5. `generate_archimate_template`
Generate diagrams from predefined templates.

```json
{
  "template_type": "viewpoint",
  "template_name": "layered",
  "customization": {}
}
```

### 6. `export_archimate_diagram`
Export diagrams to PlantUML format with optional file output.

```json
{
  "title": "Enterprise Architecture",
  "output_path": "./diagrams/architecture.puml"
}
```

## 📚 Templates

### ArchiMate Viewpoints
- **Layered**: Cross-layer relationships and dependencies
- **Service Realization**: How services are realized by components
- **Application Cooperation**: Application component interactions
- **Technology Usage**: Infrastructure and technology stack
- **Motivation**: Stakeholders, drivers, goals, and requirements

### Architecture Patterns
- **Three-Tier Architecture**: Presentation, business logic, data layers
- **Microservices**: Service-oriented architecture with API gateway
- **Event-Driven**: Event producers, consumers, and message flows
- **Layered Service**: Service-oriented layered architecture
- **CQRS**: Command Query Responsibility Segregation pattern

### Industry Templates
- **Banking**: Core banking system architecture
- **E-commerce**: Online retail platform architecture
- **Healthcare**: Hospital information system architecture
- **Manufacturing**: Manufacturing execution system (MES)

## 🧪 Development

### Requirements

- Python 3.11+
- uv (recommended) or pip
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/pskovajsa/archi-mcp.git
cd archi-mcp

# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=archi_mcp --cov-report=html

# Code formatting
uv run black src tests
uv run isort src tests

# Type checking
uv run mypy src

# Linting
uv run ruff src tests
```

### Project Structure

```
archi-mcp/
├── src/archi_mcp/           # Main package
│   ├── archimate/           # ArchiMate modeling components
│   │   ├── elements/        # Element definitions by layer
│   │   ├── relationships.py # Relationship types and validation
│   │   ├── generator.py     # PlantUML code generation
│   │   └── validator.py     # Model validation
│   ├── templates/           # Template library
│   │   ├── viewpoints.py    # ArchiMate viewpoints
│   │   ├── patterns.py      # Architecture patterns
│   │   └── industry.py      # Industry-specific templates
│   ├── utils/               # Utilities
│   └── server.py           # MCP server implementation
├── tests/                   # Comprehensive test suite
├── examples/               # Usage examples
└── docs/                   # Documentation
```

## 📖 Examples

### Basic Three-Tier Architecture

```python
from archi_mcp.archimate.elements import BusinessElement, ApplicationElement, TechnologyElement
from archi_mcp.archimate.relationships import create_relationship
from archi_mcp.archimate.generator import ArchiMateGenerator

# Create elements
business_service = BusinessElement.create_business_service(
    id="customer_service",
    name="Customer Service"
)

app_component = ApplicationElement.create_application_component(
    id="web_app", 
    name="Web Application"
)

tech_node = TechnologyElement.create_node(
    id="app_server",
    name="Application Server"
)

# Create relationships
app_realizes_business = create_relationship(
    "realizes_1", "web_app", "customer_service", "Realization"
)

server_hosts_app = create_relationship(
    "hosts_1", "app_server", "web_app", "Assignment"
)

# Generate diagram
generator = ArchiMateGenerator()
generator.add_element(business_service)
generator.add_element(app_component)
generator.add_element(tech_node)
generator.add_relationship(app_realizes_business)
generator.add_relationship(server_hosts_app)

plantuml_code = generator.generate_plantuml(title="Three-Tier Architecture")
print(plantuml_code)
```

### Using Templates

```python
from archi_mcp.templates import get_pattern_template
from archi_mcp.archimate.generator import ArchiMateGenerator

# Load microservices pattern template
template = get_pattern_template("microservices")

# Create generator and apply template
generator = ArchiMateGenerator()

# Add elements from template
for elem_data in template.elements:
    element = create_element_from_template(elem_data)
    generator.add_element(element)

# Add relationships from template  
for rel_data in template.relationships:
    relationship = create_relationship_from_template(rel_data)
    generator.add_relationship(relationship)

# Generate PlantUML
plantuml_code = generator.generate_plantuml(title=template.name)
```

## 🔧 Configuration

### Environment Variables

- `ARCHI_MCP_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ARCHI_MCP_LOG_FILE`: Optional log file path
- `ARCHI_MCP_STRICT_VALIDATION`: Enable strict ArchiMate validation

### Custom Templates

You can extend the template library by creating custom templates:

```python
from archi_mcp.templates.patterns import PatternTemplate

custom_pattern = PatternTemplate(
    name="Custom Pattern",
    description="My custom architecture pattern", 
    elements=[...],
    relationships=[...],
    pattern_type="custom"
)
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code style and standards
- Submitting pull requests
- Reporting issues
- Adding new templates
- Extending ArchiMate support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ArchiMate® 3.2 Specification](https://www.opengroup.org/archimate-forum/archimate-overview) by The Open Group
- [PlantUML](https://plantuml.com/) for diagram generation capabilities
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for enabling AI assistant integration
- [Anthropic](https://www.anthropic.com/) for Claude and MCP development

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/pskovajsa/archi-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pskovajsa/archi-mcp/discussions)
- **Documentation**: [Project Wiki](https://github.com/pskovajsa/archi-mcp/wiki)

## 🗺️ Roadmap

- [ ] Export to ArchiMate Open Exchange Format
- [ ] Interactive diagram editing capabilities
- [ ] Integration with enterprise architecture tools
- [ ] Advanced model analysis and metrics
- [ ] Collaborative modeling features
- [ ] Web-based diagram viewer

---

**ArchiMate MCP Server** - Bridging enterprise architecture modeling and AI assistance through the Model Context Protocol.