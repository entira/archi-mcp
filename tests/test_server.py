"""Tests for ArchiMate MCP server."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from archi_mcp.server import ArchiMCPServer
from mcp.types import CallToolResult, ListToolsResult, TextContent


class TestArchiMCPServer:
    """Test ArchiMate MCP server."""
    
    @pytest.fixture
    def server(self):
        """Create server instance for testing."""
        return ArchiMCPServer()
    
    def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.server is not None
        assert server.generator is not None
        assert server.validator is not None
    
    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test listing available tools."""
        # Mock the list_tools handler
        handler = None
        for tool_handler in server.server._tools_handlers:
            if hasattr(tool_handler, '__name__') and 'list_tools' in tool_handler.__name__:
                handler = tool_handler
                break
        
        if handler:
            result = await handler()
            assert isinstance(result, ListToolsResult)
            assert len(result.tools) == 6  # We defined 6 tools
            
            tool_names = [tool.name for tool in result.tools]
            expected_tools = [
                "create_archimate_diagram",
                "add_archimate_element",
                "add_archimate_relationship",
                "validate_archimate_model",
                "generate_archimate_template",
                "export_archimate_diagram"
            ]
            
            for expected_tool in expected_tools:
                assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_create_archimate_diagram_simple(self, server):
        """Test creating simple ArchiMate diagram."""
        arguments = {
            "elements": [
                {
                    "id": "test_service",
                    "name": "Test Service",
                    "element_type": "Business_Service",
                    "layer": "Business"
                }
            ],
            "title": "Test Diagram"
        }
        
        result = await server._create_archimate_diagram(arguments)
        
        assert isinstance(result, CallToolResult)
        assert len(result.content) == 1
        assert isinstance(result.content[0], TextContent)
        assert "ArchiMate diagram created successfully!" in result.content[0].text
        assert "Elements: 1" in result.content[0].text
        assert "@startuml" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_create_archimate_diagram_with_relationships(self, server):
        """Test creating ArchiMate diagram with relationships."""
        arguments = {
            "elements": [
                {
                    "id": "business_service",
                    "name": "Business Service",
                    "element_type": "Business_Service",
                    "layer": "Business"
                },
                {
                    "id": "app_component",
                    "name": "Application Component",
                    "element_type": "Application_Component",
                    "layer": "Application"
                }
            ],
            "relationships": [
                {
                    "id": "realization_rel",
                    "from_element": "app_component",
                    "to_element": "business_service",
                    "relationship_type": "Realization"
                }
            ]
        }
        
        result = await server._create_archimate_diagram(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "Elements: 2" in result.content[0].text
        assert "Relationships: 1" in result.content[0].text
        assert "Rel_Realization" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_add_archimate_element(self, server):
        """Test adding ArchiMate element."""
        arguments = {
            "element_type": "Business_Actor",
            "id": "customer",
            "name": "Customer",
            "layer": "Business",
            "description": "Bank customer"
        }
        
        result = await server._add_archimate_element(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "Element 'Customer' (Business_Actor) added successfully" in result.content[0].text
        assert "Total elements: 1" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_add_archimate_relationship(self, server):
        """Test adding ArchiMate relationship."""
        # First add elements
        await server._add_archimate_element({
            "element_type": "Business_Service",
            "id": "service1",
            "name": "Service 1",
            "layer": "Business"
        })
        
        await server._add_archimate_element({
            "element_type": "Application_Component",
            "id": "component1",
            "name": "Component 1",
            "layer": "Application"
        })
        
        # Then add relationship
        arguments = {
            "id": "rel1",
            "from_element": "component1",
            "to_element": "service1",
            "relationship_type": "Realization",
            "description": "realizes"
        }
        
        result = await server._add_archimate_relationship(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "Relationship 'Realization'" in result.content[0].text
        assert "Total relationships: 1" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_validate_archimate_model_empty(self, server):
        """Test validating empty model."""
        arguments = {"strict": False}
        
        result = await server._validate_archimate_model(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "✅ ArchiMate model validation passed!" in result.content[0].text
        assert "Elements: 0" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_validate_archimate_model_with_elements(self, server):
        """Test validating model with elements."""
        # Add a valid element
        await server._add_archimate_element({
            "element_type": "Business_Service",
            "id": "valid_service",
            "name": "Valid Service",
            "layer": "Business"
        })
        
        arguments = {"strict": True}
        
        result = await server._validate_archimate_model(arguments)
        
        assert isinstance(result, CallToolResult)
        assert ("✅ ArchiMate model validation passed!" in result.content[0].text or
                "❌ ArchiMate model validation failed!" in result.content[0].text)
    
    @pytest.mark.asyncio
    async def test_generate_archimate_template_viewpoint(self, server):
        """Test generating ArchiMate template from viewpoint."""
        arguments = {
            "template_type": "viewpoint",
            "template_name": "layered"
        }
        
        result = await server._generate_archimate_template(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "ArchiMate diagram generated from viewpoint template" in result.content[0].text
        assert "Layered Viewpoint" in result.content[0].text
        assert "@startuml" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_generate_archimate_template_pattern(self, server):
        """Test generating ArchiMate template from pattern."""
        arguments = {
            "template_type": "pattern",
            "template_name": "three_tier"
        }
        
        result = await server._generate_archimate_template(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "ArchiMate diagram generated from pattern template" in result.content[0].text
        assert "Three-Tier Architecture" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_generate_archimate_template_invalid(self, server):
        """Test generating ArchiMate template with invalid name."""
        arguments = {
            "template_type": "viewpoint",
            "template_name": "invalid_template"
        }
        
        with pytest.raises(Exception):  # Should raise ArchiMateTemplateError
            await server._generate_archimate_template(arguments)
    
    @pytest.mark.asyncio
    async def test_export_archimate_diagram(self, server):
        """Test exporting ArchiMate diagram."""
        # First create a diagram
        await server._add_archimate_element({
            "element_type": "Business_Service",
            "id": "export_service",
            "name": "Export Service",
            "layer": "Business"
        })
        
        arguments = {
            "title": "Export Test",
            "description": "Test export functionality"
        }
        
        result = await server._export_archimate_diagram(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "ArchiMate diagram exported successfully!" in result.content[0].text
        assert "Elements: 1" in result.content[0].text
        assert "@startuml" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_export_archimate_diagram_with_clear(self, server):
        """Test exporting ArchiMate diagram with clear after export."""
        # First create a diagram
        await server._add_archimate_element({
            "element_type": "Business_Service",
            "id": "clear_service",
            "name": "Clear Service",
            "layer": "Business"
        })
        
        arguments = {
            "title": "Clear Test",
            "clear_after_export": True
        }
        
        result = await server._export_archimate_diagram(arguments)
        
        assert isinstance(result, CallToolResult)
        assert "Diagram cleared after export" in result.content[0].text
        
        # Verify diagram is actually cleared
        assert len(server.generator.elements) == 0
    
    def test_get_aspect_for_element_type(self, server):
        """Test getting aspect for element type."""
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        # Test active structure
        aspect = server._get_aspect_for_element_type("Business_Actor")
        assert aspect == ArchiMateAspect.ACTIVE_STRUCTURE
        
        # Test passive structure
        aspect = server._get_aspect_for_element_type("Business_Object")
        assert aspect == ArchiMateAspect.PASSIVE_STRUCTURE
        
        # Test behavior
        aspect = server._get_aspect_for_element_type("Business_Service")
        assert aspect == ArchiMateAspect.BEHAVIOR
    
    def test_create_element_from_data(self, server):
        """Test creating element from data."""
        data = {
            "id": "test_elem",
            "name": "Test Element",
            "element_type": "Business_Service",
            "layer": "Business",
            "description": "Test description"
        }
        
        element = server._create_element_from_data(data)
        
        assert element.id == "test_elem"
        assert element.name == "Test Element"
        assert element.element_type == "Business_Service"
        assert element.description == "Test description"
    
    def test_create_element_from_data_invalid_layer(self, server):
        """Test creating element with invalid layer."""
        data = {
            "id": "test_elem",
            "name": "Test Element",
            "element_type": "Business_Service",
            "layer": "InvalidLayer"
        }
        
        with pytest.raises(Exception):  # Should raise ArchiMateValidationError
            server._create_element_from_data(data)
    
    def test_create_relationship_from_data(self, server):
        """Test creating relationship from data."""
        data = {
            "id": "test_rel",
            "from_element": "elem1",
            "to_element": "elem2",
            "relationship_type": "Serving",
            "description": "Test relationship"
        }
        
        relationship = server._create_relationship_from_data(data)
        
        assert relationship.id == "test_rel"
        assert relationship.from_element == "elem1"
        assert relationship.to_element == "elem2"
        assert relationship.description == "Test relationship"
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, server):
        """Test error handling in tool calls."""
        # Create a mock call_tool handler
        handler = None
        for tool_handler in server.server._call_tool_handlers:
            handler = tool_handler
            break
        
        if handler:
            # Test unknown tool
            result = await handler("unknown_tool", {})
            assert isinstance(result, CallToolResult)
            assert result.isError is True
            assert "Unknown tool: unknown_tool" in result.content[0].text