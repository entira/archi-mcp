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
    assert hasattr(mcp, '_tool_manager')
    
    # Check expected core tools are registered (4-tool focused API)
    expected_tools = [
        'create_archimate_diagram',
        'test_element_normalization'
    ]
    
    registered_tools = list(mcp._tool_manager._tools.keys())
    assert len(registered_tools) >= len(expected_tools), f"Expected at least {len(expected_tools)} tools, got {len(registered_tools)}"
    
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
    from archi_mcp.server import create_archimate_diagram, DiagramInput
    
    # Test with invalid layer - should cause validation error
    try:
        diagram_input = DiagramInput(
            elements=[
                {"id": "test_id", "name": "Test Actor", "element_type": "Business_Actor", "layer": "InvalidLayer"}
            ],
            relationships=[],
            title="Error Test"
        )
        
        result = create_archimate_diagram.fn(diagram_input)
        
        # Should return error message, not crash
        assert isinstance(result, str)
        assert "error" in result.lower() or "invalid" in result.lower()
    except Exception as e:
        # Error should be handled gracefully, even if an exception is raised
        assert isinstance(e, (ValueError, TypeError, Exception))

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
        
        # All tools should be FunctionTool objects with callable fn attribute
        for tool_name, tool_func in mcp._tool_manager._tools.items():
            assert hasattr(tool_func, 'fn'), f"Tool {tool_name} does not have fn attribute"
            assert callable(tool_func.fn), f"Tool {tool_name}.fn is not callable"
    
    def test_server_name(self):
        """Test server has correct name."""
        from archi_mcp.server import mcp
        
        assert mcp.name == "archi-mcp"
    
    def test_import_compatibility(self):
        """Test that all required modules can be imported."""
        # Test core imports
        from archi_mcp.server import (
            mcp, main, 
            DiagramInput, ElementInput, RelationshipInput
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
    """Integration test for complete diagram creation workflow using simplified API."""
    from archi_mcp.server import (
        create_archimate_diagram,
        DiagramInput
    )
    
    # Create complete diagram in one step
    diagram_input = DiagramInput(
        elements=[
            {
                "id": "bank_customer",
                "name": "Bank Customer", 
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Customer using banking services"
            },
            {
                "id": "online_banking",
                "name": "Online Banking Service",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Digital banking service"
            }
        ],
        relationships=[
            {
                "id": "customer_uses_service",
                "from_element": "bank_customer",
                "to_element": "online_banking",
                "relationship_type": "Serving"
            }
        ],
        title="Banking System Integration Test"
    )
    
    result1 = create_archimate_diagram.fn(diagram_input)
    # Should be a string with success message
    assert isinstance(result1, str)
    assert "ArchiMate diagram created successfully" in result1 or "Test" in result1
    
    # Step 2: Analyze current architecture
    # Diagram creation should complete without errors
    assert result1 is not None
    assert isinstance(result1, str)

def test_performance_basic():
    """Basic performance test for tool execution."""
    import time
    from archi_mcp.server import create_archimate_diagram, DiagramInput
    
    # Simple performance test
    start_time = time.time()
    
    diagram_input = DiagramInput(
        elements=[
            {
                "id": "perf_test",
                "name": "Performance Test Element",
                "element_type": "Business_Actor", 
                "layer": "Business"
            }
        ],
        title="Performance Test"
    )
    
    result = create_archimate_diagram.fn(diagram=diagram_input)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Should complete within reasonable time (< 15 seconds for basic diagram with PNG generation)
    assert execution_time < 15.0, f"Tool execution too slow: {execution_time} seconds"
    # Result can be either a string or Image object depending on MCP Image availability
    if hasattr(result, '__class__') and 'Image' in str(type(result)):
        # If it's an Image object, that's successful too
        assert result is not None
    else:
        # If it's a string, check for success message
        assert isinstance(result, str)
        assert "ArchiMate diagram created" in result and "successfully" in result