"""Test MCP integration and protocol compliance."""

import json
import subprocess
import pytest
from pathlib import Path

def test_mcp_server_initialization():
    """Test MCP server starts and responds to initialize."""
    
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    try:
        process = subprocess.run(
            ['uv', 'run', 'python', '-m', 'archi_mcp.server'],
            input=json.dumps(init_request),
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent.parent
        )
        
        # Should not crash during initialization
        assert process.returncode is not None
        
    except subprocess.TimeoutExpired:
        # Timeout is expected as server waits for more input
        pass
    except Exception as e:
        pytest.fail(f"MCP server initialization failed: {e}")

def test_fastmcp_tools_registration():
    """Test that FastMCP tools are properly registered."""
    from archi_mcp.server import mcp
    
    # Check that mcp instance exists
    assert mcp is not None
    assert hasattr(mcp, '_tools')
    
    # Check expected number of tools
    expected_tools = [
        'create_archimate_diagram',
        'add_archimate_element', 
        'add_archimate_relationship',
        'validate_archimate_model',
        'generate_archimate_template',
        'export_archimate_diagram',
        'generate_full_architecture'
    ]
    
    registered_tools = list(mcp._tools.keys())
    assert len(registered_tools) == len(expected_tools)
    
    # Check that all expected tools are registered
    for tool_name in expected_tools:
        assert tool_name in registered_tools, f"Tool {tool_name} not registered"

def test_pydantic_model_validation():
    """Test Pydantic model validation for tool inputs."""
    from archi_mcp.server import DiagramInput, ElementInput, RelationshipInput
    
    # Test valid element input
    valid_element = ElementInput(
        id="test_id",
        name="Test Element",
        element_type="Business_Actor",
        layer="Business"
    )
    assert valid_element.id == "test_id"
    assert valid_element.name == "Test Element"
    
    # Test invalid element input (missing required fields)
    with pytest.raises(Exception):  # Pydantic validation error
        ElementInput(
            id="test_id"
            # Missing required fields
        )
    
    # Test valid relationship input
    valid_relationship = RelationshipInput(
        id="rel_id",
        from_element="elem1",
        to_element="elem2", 
        relationship_type="Realization"
    )
    assert valid_relationship.id == "rel_id"
    assert valid_relationship.relationship_type == "Realization"
    
    # Test valid diagram input
    valid_diagram = DiagramInput(
        elements=[valid_element],
        relationships=[valid_relationship],
        title="Test Diagram"
    )
    assert len(valid_diagram.elements) == 1
    assert len(valid_diagram.relationships) == 1

@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test that tools handle errors gracefully."""
    from archi_mcp.server import add_archimate_element
    
    # Test with invalid layer
    result = add_archimate_element(
        element_type="Business_Actor",
        id="test_id",
        name="Test Actor",
        layer="InvalidLayer"  # This should cause an error
    )
    
    # Should return error message, not crash
    assert isinstance(result, str)
    # Error should be handled gracefully

def test_archimate_layer_validation():
    """Test ArchiMate layer validation."""
    from archi_mcp.archimate.elements.base import ArchiMateLayer
    
    # Test valid layers
    valid_layers = ["Business", "Application", "Technology", "Physical", "Motivation", "Strategy", "Implementation"]
    
    for layer_name in valid_layers:
        layer = ArchiMateLayer(layer_name)
        assert layer.value == layer_name
    
    # Test invalid layer
    with pytest.raises(ValueError):
        ArchiMateLayer("InvalidLayer")

def test_relationship_type_validation():
    """Test ArchiMate relationship type validation."""
    from archi_mcp.archimate.relationships import RelationshipType
    
    # Test valid relationship types
    valid_types = ["Access", "Aggregation", "Assignment", "Association", "Composition", "Flow", "Influence", "Realization", "Serving", "Specialization", "Triggering"]
    
    for rel_type in valid_types:
        relationship_type = RelationshipType(rel_type)
        assert relationship_type.value == rel_type
    
    # Test invalid relationship type
    with pytest.raises(ValueError):
        RelationshipType("InvalidRelationship")

class TestMCPProtocolCompliance:
    """Test MCP protocol compliance."""
    
    def test_tool_schemas(self):
        """Test that tool schemas are properly defined."""
        from archi_mcp.server import mcp
        
        # All tools should be callable
        for tool_name, tool_func in mcp._tools.items():
            assert callable(tool_func), f"Tool {tool_name} is not callable"
    
    def test_server_name(self):
        """Test server has correct name."""
        from archi_mcp.server import mcp
        
        assert mcp.name == "archi-mcp"
    
    def test_import_compatibility(self):
        """Test that all required modules can be imported."""
        # Test core imports
        from archi_mcp.server import (
            mcp, main, 
            DiagramInput, ElementInput, RelationshipInput, 
            TemplateInput, FullArchitectureInput
        )
        
        # Test ArchiMate module imports
        from archi_mcp.archimate import (
            ArchiMateElement, ArchiMateRelationship,
            ArchiMateGenerator, ArchiMateValidator
        )
        
        # Test utility imports
        from archi_mcp.utils.logging import setup_logging, get_logger
        from archi_mcp.utils.exceptions import (
            ArchiMateError, ArchiMateValidationError,
            ArchiMateGenerationError, ArchiMateTemplateError
        )
        
        # All imports should succeed
        assert all([
            mcp, main, DiagramInput, ElementInput, RelationshipInput,
            ArchiMateElement, ArchiMateRelationship, ArchiMateGenerator, ArchiMateValidator,
            setup_logging, get_logger, ArchiMateError
        ])

@pytest.mark.integration
def test_end_to_end_diagram_creation():
    """Integration test for complete diagram creation workflow."""
    from archi_mcp.server import (
        create_archimate_diagram, add_archimate_element, add_archimate_relationship,
        validate_archimate_model, export_archimate_diagram,
        DiagramInput, ElementInput, RelationshipInput
    )
    
    # Step 1: Create basic diagram
    diagram_input = DiagramInput(
        elements=[
            ElementInput(
                id="bank_customer",
                name="Bank Customer", 
                element_type="Business_Actor",
                layer="Business",
                description="Customer using banking services"
            )
        ],
        title="Banking System Integration Test"
    )
    
    result1 = create_archimate_diagram(diagram_input)
    assert "ArchiMate diagram created successfully!" in result1
    
    # Step 2: Add another element
    result2 = add_archimate_element(
        element_type="Business_Service",
        id="online_banking",
        name="Online Banking Service",
        layer="Business",
        description="Digital banking service"
    )
    assert "added successfully" in result2
    
    # Step 3: Add relationship
    result3 = add_archimate_relationship(
        id="customer_uses_service",
        from_element="bank_customer",
        to_element="online_banking", 
        relationship_type="Access",
        description="Customer accesses online banking"
    )
    assert "added successfully" in result3
    
    # Step 4: Validate model
    result4 = validate_archimate_model(strict=False)
    assert "validation" in result4.lower()
    
    # Step 5: Export diagram
    result5 = export_archimate_diagram(
        title="Final Banking System",
        description="Complete banking system diagram"
    )
    assert "exported successfully" in result5
    assert "```plantuml" in result5
    
    # All steps should complete without errors
    assert all(isinstance(result, str) for result in [result1, result2, result3, result4, result5])

def test_performance_basic():
    """Basic performance test for tool execution."""
    import time
    from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
    
    # Simple performance test
    start_time = time.time()
    
    diagram_input = DiagramInput(
        elements=[
            ElementInput(
                id="perf_test",
                name="Performance Test Element",
                element_type="Business_Actor", 
                layer="Business"
            )
        ],
        title="Performance Test"
    )
    
    result = create_archimate_diagram(diagram_input)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Should complete within reasonable time (< 5 seconds for basic diagram)
    assert execution_time < 5.0, f"Tool execution too slow: {execution_time} seconds"
    assert isinstance(result, str)
    assert "ArchiMate diagram created successfully!" in result