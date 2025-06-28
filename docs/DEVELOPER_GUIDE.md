# 🛠️ ArchiMate MCP Server - Developer Guide

**Complete development guide for extending, customizing, and contributing to the ArchiMate MCP server.**

## 🏗️ Architecture Overview

### Core Components

```
archi-mcp/
├── src/archi_mcp/
│   ├── __init__.py                 # Package initialization
│   ├── server.py                   # Main FastMCP server (480+ lines)
│   ├── archimate/                  # ArchiMate modeling components
│   │   ├── elements/               # Element definitions by layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base classes and enums
│   │   │   ├── business.py        # Business layer elements
│   │   │   ├── application.py     # Application layer elements
│   │   │   ├── technology.py      # Technology layer elements
│   │   │   ├── physical.py        # Physical layer elements
│   │   │   ├── motivation.py      # Motivation layer elements
│   │   │   ├── strategy.py        # Strategy layer elements
│   │   │   └── implementation.py  # Implementation layer elements
│   │   ├── relationships.py       # Relationship types and validation
│   │   ├── generator.py           # PlantUML code generation
│   │   └── validator.py           # Model validation
│   ├── templates/                  # Template library
│   │   ├── __init__.py
│   │   ├── viewpoints.py          # ArchiMate viewpoints
│   │   ├── patterns.py            # Architecture patterns
│   │   └── industry.py            # Industry-specific templates
│   ├── utils/                      # Utilities
│   │   ├── __init__.py
│   │   ├── logging.py             # Logging configuration
│   │   └── exceptions.py          # Custom exceptions
│   └── architecture_generator.py  # Full architecture generation
├── tests/                          # Test suite
├── examples/                       # Usage examples and configs
└── docs/                          # Documentation
```

### Technology Stack

- **FastMCP 2.8+**: Modern MCP framework with decorators
- **Python 3.11+**: Async/await support and type hints
- **Pydantic 2.0+**: Data validation and serialization
- **PlantUML**: Diagram generation and validation
- **UV**: Fast Python package management

### Key Design Patterns

1. **Tool-Based Architecture**: Each function is a separate MCP tool with @mcp.tool() decorator
2. **Pydantic Validation**: All inputs validated with Pydantic models
3. **ArchiMate Compliance**: Strict adherence to ArchiMate 3.2 specification
4. **Layered Generation**: Supports all 7 ArchiMate layers with proper relationships
5. **Template System**: Extensible template library for common patterns

## 🔧 Development Setup

### Environment Setup

```bash
# 1. Clone and setup
git clone https://github.com/entira/archi-mcp.git
cd archi-mcp

# 2. Install with dev dependencies
uv sync --extra dev

# 3. Install pre-commit hooks (if available)
uv run pre-commit install

# 4. Verify setup
uv run pytest
uv run python -m archi_mcp.server
```

### Development Tools

```bash
# Code formatting
uv run black src/ tests/

# Linting
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# Testing with coverage
uv run pytest --cov=archi_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py -v

# Test PlantUML validation
uv run pytest tests/test_plantuml_validation.py
```

## 🛠️ Core Functions

### 1. ArchiMate Element Creation

```python
def _create_element_from_data(data: ElementInput) -> ArchiMateElement:
    """
    Core function for creating ArchiMate elements.
    
    ArchiMate-specific requirements:
    - Proper layer assignment (Business, Application, Technology, etc.)
    - Correct aspect detection (Active/Passive Structure, Behavior)
    - Element type validation against ArchiMate 3.2 spec
    - Unique ID enforcement
    """
    # Map layer string to enum
    try:
        layer = ArchiMateLayer(data.layer)
    except ValueError:
        raise ArchiMateValidationError(f"Invalid layer: {data.layer}")
    
    # Determine aspect from element type
    aspect = _get_aspect_for_element_type(data.element_type)
    
    return ArchiMateElement(
        id=data.id,
        name=data.name,
        element_type=data.element_type,
        layer=layer,
        aspect=aspect,
        description=data.description,
        stereotype=data.stereotype,
        properties=data.properties,
        documentation=None
    )
```

### 2. PlantUML Generation Engine

```python
def generate_plantuml_archimate(elements: List[ArchiMateElement], 
                              relationships: List[ArchiMateRelationship],
                              title: str = None) -> str:
    """
    Generate PlantUML code with ArchiMate syntax.
    
    Features:
    - Proper ArchiMate includes (!include <archimate/Archimate>)
    - Layer-specific element syntax (Business_Actor(id, "name"))
    - Relationship syntax (Rel_Access(source, target, "label"))
    - Layout and styling options
    """
    plantuml_lines = [
        "@startuml",
        "!include <archimate/Archimate>",
        "!define ARCHIMATE_COLOR_SCHEME modern"
    ]
    
    if title:
        plantuml_lines.append(f"title {title}")
    
    # Add elements by layer
    for layer in ArchiMateLayer:
        layer_elements = [e for e in elements if e.layer == layer]
        if layer_elements:
            plantuml_lines.append(f"' {layer.value} Layer")
            for element in layer_elements:
                element_line = f"{layer.value}_{element.element_type}({element.id}, \"{element.name}\")"
                plantuml_lines.append(element_line)
            plantuml_lines.append("")
    
    # Add relationships
    if relationships:
        plantuml_lines.append("' Relationships")
        for rel in relationships:
            rel_line = f"Rel_{rel.relationship_type.value}({rel.from_element}, {rel.to_element}"
            if rel.description:
                rel_line += f", \"{rel.description}\""
            rel_line += ")"
            plantuml_lines.append(rel_line)
    
    plantuml_lines.append("@enduml")
    return "\n".join(plantuml_lines)
```

### 3. Architecture Generation Engine

```python
class FullArchitectureGenerator:
    """
    AI-powered architecture generation following ArchiMate Cookbook methodology.
    
    Generates multiple coordinated views:
    - Motivation View: Goals, stakeholders, requirements
    - Strategy View: Capabilities, resources, courses of action
    - Business View: Processes, services, actors
    - Application View: Components, services, interfaces
    - Technology View: Infrastructure, platforms, networks
    - Implementation View: Projects, deliverables, milestones
    """
    
    def generate_architecture(self, system_description: str, 
                            business_domain: str = "general",
                            include_views: List[str] = None) -> Dict[str, str]:
        """Generate complete multi-view architecture."""
        
        architecture_views = {}
        
        if "motivation" in include_views:
            architecture_views["motivation"] = self._generate_motivation_view(
                system_description, business_domain
            )
        
        if "layered_view" in include_views:
            architecture_views["layered_view"] = self._generate_layered_view(
                system_description, business_domain
            )
        
        # ... additional views
        
        return architecture_views
    
    def _generate_motivation_view(self, system_description: str, domain: str) -> str:
        """Generate motivation layer with stakeholders, goals, and requirements."""
        # Implementation based on ArchiMate Cookbook methodology
        pass
```

## 🔌 Adding New Tools

### Tool Development Pattern

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

### Example: Adding Architecture Analysis Tool

```python
@mcp.tool()
def analyze_architecture_complexity(architecture: FullArchitectureInput) -> str:
    """Analyze architecture complexity and provide recommendations."""
    
    # Generate architecture views
    views = full_arch_generator.generate_architecture(
        system_description=architecture.system_description,
        business_domain=architecture.business_domain,
        include_views=architecture.include_views
    )
    
    # Analyze complexity metrics
    total_elements = sum(view.count("(") for view in views.values())
    total_relationships = sum(view.count("Rel_") for view in views.values())
    layer_coverage = len(architecture.include_views)
    
    # Calculate complexity score
    complexity_score = (total_elements * 0.3) + (total_relationships * 0.5) + (layer_coverage * 2)
    
    if complexity_score < 10:
        complexity_level = "Low"
        recommendation = "Consider adding more detail to business and application layers"
    elif complexity_score < 25:
        complexity_level = "Medium" 
        recommendation = "Good balance of detail, consider validation with stakeholders"
    else:
        complexity_level = "High"
        recommendation = "Consider breaking into focused views or simplifying relationships"
    
    return f"""# 🔍 Architecture Complexity Analysis

**System:** {architecture.system_description}
**Domain:** {architecture.business_domain}

## Metrics
- **Total Elements:** {total_elements}
- **Total Relationships:** {total_relationships}
- **Layer Coverage:** {layer_coverage}/7 layers
- **Complexity Score:** {complexity_score:.1f}

## Assessment
**Complexity Level:** {complexity_level}

## Recommendations
{recommendation}

## Next Steps
1. Review each view for stakeholder alignment
2. Validate element relationships follow ArchiMate rules
3. Consider implementation feasibility
4. Plan phased delivery approach
"""
```

## 🧪 Testing

### Unit Test Structure

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
    
    def test_plantuml_syntax(self):
        """Test PlantUML syntax compliance."""
        result = your_new_archimate_tool("syntax test")
        
        # Extract PlantUML code
        plantuml_start = result.find("```plantuml\n") + len("```plantuml\n")
        plantuml_end = result.find("\n```", plantuml_start)
        plantuml_code = result[plantuml_start:plantuml_end]
        
        # Validate syntax
        assert "@startuml" in plantuml_code or "startuml" in plantuml_code
        assert "@enduml" in plantuml_code or "enduml" in plantuml_code
        assert "!include" in plantuml_code or "archimate" in plantuml_code.lower()
```

### Integration Testing

```python
# tests/test_integration_new_feature.py
import pytest
from archi_mcp.server import (
    create_archimate_diagram, your_new_archimate_tool,
    DiagramInput, ElementInput
)

@pytest.mark.integration
def test_tool_integration_workflow():
    """Test integration with existing tools."""
    
    # Step 1: Create base diagram
    diagram_input = DiagramInput(
        elements=[
            ElementInput(
                id="integration_test",
                name="Integration Test Element",
                element_type="Business_Process",
                layer="Business"
            )
        ],
        title="Integration Test"
    )
    
    result1 = create_archimate_diagram(diagram_input)
    assert "ArchiMate diagram created successfully!" in result1
    
    # Step 2: Use new tool
    result2 = your_new_archimate_tool("integration test")
    assert "✅ Success" in result2
    
    # Both tools should work together without conflicts
    assert isinstance(result1, str)
    assert isinstance(result2, str)
```

### Performance Testing

```python
def test_tool_performance():
    """Test tool performance with larger inputs."""
    import time
    
    # Create large architecture input
    architecture_input = FullArchitectureInput(
        system_description="Large enterprise system with multiple domains",
        business_domain="enterprise",
        include_views=["motivation", "layered_view", "application_structure", "implementation_roadmap"],
        implementation_phases=5
    )
    
    start_time = time.time()
    result = generate_full_architecture(architecture_input)
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Should complete within reasonable time
    assert execution_time < 10.0, f"Tool too slow: {execution_time} seconds"
    assert isinstance(result, str)
    assert "Complete Enterprise Architecture" in result
```

## 🔧 Customization

### Adding Custom ArchiMate Elements

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
            layer=ArchiMateLayer.BUSINESS,  # or appropriate layer
            aspect=ArchiMateAspect.BEHAVIOR,
            **kwargs
        )
        self.custom_property = custom_property
    
    def to_plantuml(self) -> str:
        """Generate custom PlantUML syntax."""
        return f"Business_Element({self.id}, \"{self.name}\")"

# Register in _get_aspect_for_element_type function
def _get_aspect_for_element_type(element_type: str) -> ArchiMateAspect:
    # Add custom element types
    custom_elements = ["Custom_Element", "Special_Component"]
    
    if element_type in custom_elements:
        return ArchiMateAspect.BEHAVIOR
    
    # ... existing logic
```

### Custom Template Creation

```python
# src/archi_mcp/templates/custom_patterns.py
from .base import PatternTemplate

CUSTOM_MICROSERVICES_TEMPLATE = PatternTemplate(
    name="Enhanced Microservices",
    description="Microservices with enhanced monitoring and security",
    elements=[
        {
            "id": "api_gateway",
            "name": "API Gateway",
            "element_type": "Application_Component",
            "layer": "Application",
            "description": "Central API gateway with rate limiting"
        },
        {
            "id": "auth_service",
            "name": "Authentication Service", 
            "element_type": "Application_Service",
            "layer": "Application",
            "description": "OAuth2/JWT authentication"
        },
        {
            "id": "monitoring_service",
            "name": "Monitoring Service",
            "element_type": "Application_Service", 
            "layer": "Application",
            "description": "Centralized logging and metrics"
        }
    ],
    relationships=[
        {
            "id": "gateway_auth",
            "from_element": "api_gateway",
            "to_element": "auth_service",
            "relationship_type": "Access"
        },
        {
            "id": "gateway_monitoring", 
            "from_element": "api_gateway",
            "to_element": "monitoring_service",
            "relationship_type": "Serving"
        }
    ],
    pattern_type="microservices_enhanced"
)

# Add to patterns registry
CUSTOM_PATTERNS = {
    "microservices_enhanced": CUSTOM_MICROSERVICES_TEMPLATE
}
```

### Custom Architecture Generator

```python
class CustomArchitectureGenerator(FullArchitectureGenerator):
    """Extended architecture generator with custom patterns."""
    
    def generate_security_architecture(self, system_description: str) -> Dict[str, str]:
        """Generate security-focused architecture views."""
        
        return {
            "security_view": self._generate_security_view(system_description),
            "threat_model": self._generate_threat_model(system_description),
            "compliance_view": self._generate_compliance_view(system_description)
        }
    
    def _generate_security_view(self, system_description: str) -> str:
        """Generate security-focused ArchiMate view."""
        
        security_elements = [
            # Security actors
            ("security_officer", "Security Officer", "Business_Role", "Business"),
            ("threat_actor", "External Threat", "Business_Actor", "Business"),
            
            # Security services
            ("authentication", "Authentication Service", "Application_Service", "Application"),
            ("authorization", "Authorization Service", "Application_Service", "Application"),
            ("encryption", "Encryption Service", "Application_Service", "Application"),
            
            # Security infrastructure
            ("firewall", "Firewall", "Node", "Technology"),
            ("ids", "Intrusion Detection", "System_Software", "Technology")
        ]
        
        plantuml_lines = [
            "@startuml",
            "!include <archimate/Archimate>",
            "title Security Architecture View",
            ""
        ]
        
        # Add elements
        for elem_id, name, elem_type, layer in security_elements:
            plantuml_lines.append(f"{layer}_{elem_type}({elem_id}, \"{name}\")")
        
        # Add security relationships
        plantuml_lines.extend([
            "",
            "' Security Relationships",
            "Rel_Access(security_officer, authentication, \"Manages\")",
            "Rel_Serving(authentication, authorization, \"Provides identity\")",
            "Rel_Assignment(firewall, encryption, \"Protects\")",
            "Rel_Influence(threat_actor, firewall, \"Attempts breach\")"
        ])
        
        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)
```

## 🌐 Advanced Features

### Adding Diagram Export Formats

```python
@mcp.tool()
    format: str = "plantuml",
    include_metadata: bool = True,
    output_path: Optional[str] = None
) -> str:
    """Export diagram in multiple formats with metadata."""
    
    plantuml_code = generator.generate_plantuml()
    
    if format == "plantuml":
        result = plantuml_code
        
    elif format == "json":
        # Export as JSON for programmatic processing
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": "1.0.0",
                "elements_count": generator.get_element_count(),
                "relationships_count": generator.get_relationship_count()
            },
            "elements": [elem.to_dict() for elem in generator.elements],
            "relationships": [rel.to_dict() for rel in generator.relationships],
            "plantuml": plantuml_code
        }
        result = json.dumps(export_data, indent=2)
        
    elif format == "archimate_xml":
        # Export to ArchiMate Open Exchange Format
        result = generate_archimate_xml(generator.elements, generator.relationships)
        
    else:
        return f"❌ Error: Unsupported format '{format}'"
    
    # Save to file if requested
    if output_path:
        file_extension = {"plantuml": ".puml", "json": ".json", "archimate_xml": ".xml"}
        full_path = f"{output_path}{file_extension.get(format, '.txt')}"
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return f"✅ Exported to {full_path}\n\nContent:\n{result}"
    
    return result
```

### Performance Optimization

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def cached_architecture_generation(
    system_description: str, 
    business_domain: str,
    views_tuple: tuple  # Convert list to tuple for hashing
) -> Dict[str, str]:
    """Cache architecture generation results for performance."""
    
    views_list = list(views_tuple)
    return full_arch_generator.generate_architecture(
        system_description=system_description,
        business_domain=business_domain,
        include_views=views_list
    )

# Advanced caching with expiry
architecture_cache = {}

def get_cached_architecture(system_description: str, **kwargs) -> Dict[str, str]:
    """Get cached architecture with expiry."""
    
    cache_key = hash((system_description, frozenset(kwargs.items())))
    now = datetime.now()
    
    if cache_key in architecture_cache:
        cached_result, timestamp = architecture_cache[cache_key]
        if (now - timestamp) < timedelta(hours=1):  # 1 hour cache
            return cached_result
    
    # Generate new architecture
    result = full_arch_generator.generate_architecture(
        system_description=system_description,
        **kwargs
    )
    architecture_cache[cache_key] = (result, now)
    
    return result
```

### Async Optimization

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_architecture_generation(architecture_input: FullArchitectureInput) -> str:
    """Generate architecture asynchronously for better performance."""
    
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            lambda: full_arch_generator.generate_architecture(
                system_description=architecture_input.system_description,
                business_domain=architecture_input.business_domain,
                architecture_scope=architecture_input.architecture_scope,
                include_views=architecture_input.include_views,
                implementation_phases=architecture_input.implementation_phases
            )
        )
    
    # Format result asynchronously
    formatted_result = await loop.run_in_executor(
        executor,
        lambda: format_architecture_result(result, architecture_input)
    )
    
    return formatted_result
```

## 🔍 Debugging

### Logging Setup

```python
import logging
from datetime import datetime

# Configure structured logging for ArchiMate operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'archimate_mcp_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('archi_mcp')

# Add to tools for debugging
@mcp.tool()
def debug_archimate_model(include_details: bool = False) -> str:
    """Debug current ArchiMate model state."""
    
    logger.info("Debug tool called")
    
    try:
        elements = generator.elements
        relationships = generator.relationships
        
        debug_info = {
            "model_statistics": {
                "elements": len(elements),
                "relationships": len(relationships),
                "layers": list(set(elem.layer.value for elem in elements))
            }
        }
        
        if include_details:
            debug_info["elements"] = [
                {
                    "id": elem.id,
                    "name": elem.name,
                    "type": elem.element_type,
                    "layer": elem.layer.value,
                    "aspect": elem.aspect.value
                }
                for elem in elements
            ]
            
            debug_info["relationships"] = [
                {
                    "id": rel.id,
                    "from": rel.from_element,
                    "to": rel.to_element,
                    "type": rel.relationship_type.value
                }
                for rel in relationships
            ]
        
        logger.info(f"Debug completed: {debug_info['model_statistics']}")
        return f"🔍 Debug Information:\n\n{json.dumps(debug_info, indent=2)}"
        
    except Exception as e:
        logger.error(f"Debug tool error: {str(e)}", exc_info=True)
        return f"❌ Debug error: {str(e)}"
```

### ArchiMate Validation Debugging

```python
def debug_archimate_validation(elements: List[ArchiMateElement], 
                             relationships: List[ArchiMateRelationship]) -> Dict[str, Any]:
    """Debug ArchiMate model validation issues."""
    
    validation_report = {
        "elements": {"valid": [], "issues": []},
        "relationships": {"valid": [], "issues": []},
        "cross_validation": {"valid": [], "issues": []}
    }
    
    # Validate elements
    for element in elements:
        try:
            # Check element type against layer
            expected_layer = get_expected_layer_for_element_type(element.element_type)
            if element.layer == expected_layer:
                validation_report["elements"]["valid"].append(element.id)
            else:
                validation_report["elements"]["issues"].append({
                    "element_id": element.id,
                    "issue": f"Element type {element.element_type} not expected in layer {element.layer.value}",
                    "expected_layer": expected_layer.value
                })
        except Exception as e:
            validation_report["elements"]["issues"].append({
                "element_id": element.id,
                "issue": str(e)
            })
    
    # Validate relationships
    for relationship in relationships:
        try:
            # Check if relationship type is valid between element types
            from_elem = next((e for e in elements if e.id == relationship.from_element), None)
            to_elem = next((e for e in elements if e.id == relationship.to_element), None)
            
            if from_elem and to_elem:
                if is_valid_relationship(from_elem, to_elem, relationship.relationship_type):
                    validation_report["relationships"]["valid"].append(relationship.id)
                else:
                    validation_report["relationships"]["issues"].append({
                        "relationship_id": relationship.id,
                        "issue": f"Invalid relationship {relationship.relationship_type.value} between {from_elem.element_type} and {to_elem.element_type}"
                    })
            else:
                validation_report["relationships"]["issues"].append({
                    "relationship_id": relationship.id,
                    "issue": "Referenced elements not found"
                })
        except Exception as e:
            validation_report["relationships"]["issues"].append({
                "relationship_id": relationship.id,
                "issue": str(e)
            })
    
    return validation_report
```

## 📦 Building and Distribution

### Building Package

```bash
# Build package
uv build

# Check package
uv run twine check dist/*

# Install locally for testing
uv pip install dist/archi_mcp-1.0.0-py3-none-any.whl

# Test installation
python -c "from archi_mcp.server import mcp; print('✅ Package installed correctly')"
```

### Version Management

```python
# src/archi_mcp/__init__.py
__version__ = "1.0.0"

# Auto-update version in tools
@mcp.tool()
def get_server_info() -> str:
    """Get ArchiMate MCP server information."""
    from archi_mcp import __version__
    
    return f"""# 🏗️ ArchiMate MCP Server

**Version:** {__version__}
**Protocol:** FastMCP 2.8+
**ArchiMate:** 3.2 Specification
**Python:** {sys.version}

**Capabilities:**
- All 7 ArchiMate layers supported
- 55+ ArchiMate elements
- 12 relationship types  
- Template library with patterns
- Full architecture generation
- PlantUML export with validation

**Tools Available:** {len(mcp._tools)}
"""
```

## 🤝 Contributing

### Pull Request Process

1. **Fork and clone**
2. **Create feature branch**: `git checkout -b feature/archimate-enhancement`
3. **Follow ArchiMate standards**: Ensure compliance with ArchiMate 3.2
4. **Add comprehensive tests**: Test all layers and element types
5. **Update documentation**: Include PlantUML examples
6. **Submit PR**: Clear description with architecture diagrams

### Code Style Guidelines

```python
# Type hints are required for all ArchiMate functions
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

# Use descriptive variable names following ArchiMate terminology
motivation_elements = [stakeholder, goal, requirement, principle]
layered_architecture_views = generate_multi_layer_views(motivation_elements)

# Error handling is mandatory for all ArchiMate operations
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

---

**🚀 Ready to extend and enhance the ArchiMate MCP server with enterprise architecture best practices!**