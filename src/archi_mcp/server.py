"""ArchiMate MCP Server implementation."""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest, 
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
)
from pydantic import BaseModel

from .utils.logging import setup_logging, get_logger
from .utils.exceptions import (
    ArchiMateError,
    ArchiMateValidationError,
    ArchiMateGenerationError,
    ArchiMateTemplateError,
)
from .archimate import (
    ArchiMateElement,
    ArchiMateRelationship,
    ArchiMateGenerator,
    ArchiMateValidator,
    ARCHIMATE_ELEMENTS,
    ARCHIMATE_RELATIONSHIPS,
)
from .archimate.elements.base import ArchiMateLayer, ArchiMateAspect
from .archimate.relationships import RelationshipType, create_relationship
from .archimate.generator import DiagramLayout
from .templates import (
    get_viewpoint_template,
    get_pattern_template,
    get_industry_template,
    ARCHIMATE_VIEWPOINTS,
    ARCHITECTURE_PATTERNS,
    INDUSTRY_TEMPLATES,
)
from .architecture_generator import FullArchitectureGenerator

# Setup logging
setup_logging(level="INFO")
logger = get_logger("archi_mcp.server")


class ArchiMCPServer:
    """ArchiMate MCP Server for generating PlantUML ArchiMate diagrams."""
    
    def __init__(self):
        """Initialize the ArchiMate MCP server."""
        self.server = Server("archi-mcp")
        self.generator = ArchiMateGenerator()
        self.validator = ArchiMateValidator()
        self.full_arch_generator = FullArchitectureGenerator()
        
        # Register MCP tools
        self._register_tools()
        
        logger.info("ArchiMate MCP Server initialized")
    
    def _register_tools(self) -> None:
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available ArchiMate tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="create_archimate_diagram",
                        description="Generate complete ArchiMate diagrams from structured input with elements and relationships",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "elements": {
                                    "type": "array",
                                    "description": "List of ArchiMate elements with properties",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string", "description": "Unique element identifier"},
                                            "name": {"type": "string", "description": "Element display name"},
                                            "element_type": {"type": "string", "description": "ArchiMate element type"},
                                            "layer": {"type": "string", "description": "ArchiMate layer"},
                                            "description": {"type": "string", "description": "Element description"},
                                            "stereotype": {"type": "string", "description": "Element stereotype"}
                                        },
                                        "required": ["id", "name", "element_type", "layer"]
                                    }
                                },
                                "relationships": {
                                    "type": "array",
                                    "description": "List of relationships between elements",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string", "description": "Unique relationship identifier"},
                                            "from_element": {"type": "string", "description": "Source element ID"},
                                            "to_element": {"type": "string", "description": "Target element ID"},
                                            "relationship_type": {"type": "string", "description": "ArchiMate relationship type"},
                                            "direction": {"type": "string", "description": "Optional direction (Up, Down, Left, Right)"},
                                            "description": {"type": "string", "description": "Relationship description"}
                                        },
                                        "required": ["id", "from_element", "to_element", "relationship_type"]
                                    }
                                },
                                "layout": {
                                    "type": "object",
                                    "description": "Layout preferences",
                                    "properties": {
                                        "direction": {"type": "string", "description": "Layout direction (horizontal, vertical, layered)"},
                                        "show_legend": {"type": "boolean", "description": "Show diagram legend"},
                                        "show_title": {"type": "boolean", "description": "Show diagram title"},
                                        "group_by_layer": {"type": "boolean", "description": "Group elements by layer"}
                                    }
                                },
                                "title": {"type": "string", "description": "Diagram title"},
                                "description": {"type": "string", "description": "Diagram description"}
                            },
                            "required": ["elements"]
                        }
                    ),
                    Tool(
                        name="add_archimate_element",
                        description="Add single ArchiMate element to existing diagram",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "element_type": {"type": "string", "description": "ArchiMate element type"},
                                "id": {"type": "string", "description": "Unique element identifier"},
                                "name": {"type": "string", "description": "Element display name"},
                                "layer": {"type": "string", "description": "ArchiMate layer"},
                                "description": {"type": "string", "description": "Element description"},
                                "stereotype": {"type": "string", "description": "Element stereotype"},
                                "properties": {"type": "object", "description": "Additional element properties"}
                            },
                            "required": ["element_type", "id", "name", "layer"]
                        }
                    ),
                    Tool(
                        name="add_archimate_relationship",
                        description="Add relationship between ArchiMate elements",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique relationship identifier"},
                                "from_element": {"type": "string", "description": "Source element ID"},
                                "to_element": {"type": "string", "description": "Target element ID"},
                                "relationship_type": {"type": "string", "description": "ArchiMate relationship type"},
                                "direction": {"type": "string", "description": "Optional direction (Up, Down, Left, Right)"},
                                "description": {"type": "string", "description": "Relationship description"},
                                "label": {"type": "string", "description": "Relationship label"}
                            },
                            "required": ["id", "from_element", "to_element", "relationship_type"]
                        }
                    ),
                    Tool(
                        name="validate_archimate_model",
                        description="Validate ArchiMate model against ArchiMate 3.2 specification",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "strict": {"type": "boolean", "description": "Whether to apply strict validation rules", "default": False}
                            }
                        }
                    ),
                    Tool(
                        name="generate_archimate_template",
                        description="Generate ArchiMate diagram from predefined templates",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "template_type": {
                                    "type": "string",
                                    "description": "Template category",
                                    "enum": ["viewpoint", "pattern", "industry"]
                                },
                                "template_name": {"type": "string", "description": "Specific template name"},
                                "customization": {"type": "object", "description": "Template customization parameters"}
                            },
                            "required": ["template_type", "template_name"]
                        }
                    ),
                    Tool(
                        name="export_archimate_diagram",
                        description="Export ArchiMate diagram to PlantUML format and optionally save to file",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Diagram title"},
                                "description": {"type": "string", "description": "Diagram description"},
                                "output_path": {"type": "string", "description": "Optional output file path"},
                                "clear_after_export": {"type": "boolean", "description": "Clear diagram after export", "default": False}
                            }
                        }
                    ),
                    Tool(
                        name="generate_full_architecture",
                        description="Generate a complete layered enterprise architecture following ArchiMate methodology with multiple coordinated views (Motivation, Business Model Canvas, Value Stream, Strategy & Capability, Layered Views, Interaction Views, Application & Technology Structure, Implementation Roadmap)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "system_description": {
                                    "type": "string", 
                                    "description": "Description of the target system or business problem to architect"
                                },
                                "business_domain": {
                                    "type": "string",
                                    "description": "Business domain (e.g., 'banking', 'healthcare', 'e-commerce', 'manufacturing')",
                                    "default": "general"
                                },
                                "architecture_scope": {
                                    "type": "string",
                                    "description": "Scope of architecture",
                                    "enum": ["enterprise", "system", "application", "component"],
                                    "default": "system"
                                },
                                "include_views": {
                                    "type": "array",
                                    "description": "Which ArchiMate views to include",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "motivation", "business_model_canvas", "value_stream",
                                            "strategy_capability", "layered_view", "interaction_view",
                                            "application_structure", "technology_structure", "implementation_roadmap"
                                        ]
                                    },
                                    "default": ["motivation", "layered_view", "application_structure", "implementation_roadmap"]
                                },
                                "implementation_phases": {
                                    "type": "integer",
                                    "description": "Number of implementation phases for roadmap",
                                    "minimum": 1,
                                    "maximum": 6,
                                    "default": 3
                                }
                            },
                            "required": ["system_description"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "create_archimate_diagram":
                    return await self._create_archimate_diagram(arguments)
                elif name == "add_archimate_element":
                    return await self._add_archimate_element(arguments)
                elif name == "add_archimate_relationship":
                    return await self._add_archimate_relationship(arguments)
                elif name == "validate_archimate_model":
                    return await self._validate_archimate_model(arguments)
                elif name == "generate_archimate_template":
                    return await self._generate_archimate_template(arguments)
                elif name == "export_archimate_diagram":
                    return await self._export_archimate_diagram(arguments)
                elif name == "generate_full_architecture":
                    return await self._generate_full_architecture(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Unknown tool: {name}"
                        )],
                        isError=True
                    )
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
                    )],
                    isError=True
                )
    
    async def _create_archimate_diagram(self, arguments: dict) -> CallToolResult:
        """Create complete ArchiMate diagram."""
        try:
            # Clear existing diagram
            self.generator.clear()
            
            # Add elements
            elements_data = arguments.get("elements", [])
            for elem_data in elements_data:
                element = self._create_element_from_data(elem_data)
                self.generator.add_element(element)
            
            # Add relationships
            relationships_data = arguments.get("relationships", [])
            for rel_data in relationships_data:
                relationship = self._create_relationship_from_data(rel_data)
                self.generator.add_relationship(relationship)
            
            # Set layout if provided
            layout_data = arguments.get("layout", {})
            if layout_data:
                layout = DiagramLayout(**layout_data)
                self.generator.set_layout(layout)
            
            # Generate PlantUML code
            title = arguments.get("title")
            description = arguments.get("description")
            plantuml_code = self.generator.generate_plantuml(title=title, description=description)
            
            # Get diagram statistics
            stats = {
                "elements": self.generator.get_element_count(),
                "relationships": self.generator.get_relationship_count(),
                "layers": self.generator.get_layers_used()
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"ArchiMate diagram created successfully!\n\nStatistics:\n- Elements: {stats['elements']}\n- Relationships: {stats['relationships']}\n- Layers: {', '.join(stats['layers'])}\n\nPlantUML Code:\n```plantuml\n{plantuml_code}\n```"
                )]
            )
            
        except Exception as e:
            raise ArchiMateGenerationError(f"Failed to create diagram: {str(e)}")
    
    async def _add_archimate_element(self, arguments: dict) -> CallToolResult:
        """Add ArchiMate element to diagram."""
        try:
            element = self._create_element_from_data(arguments)
            self.generator.add_element(element)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Element '{element.name}' ({element.element_type}) added successfully to diagram. Total elements: {self.generator.get_element_count()}"
                )]
            )
            
        except Exception as e:
            raise ArchiMateValidationError(f"Failed to add element: {str(e)}")
    
    async def _add_archimate_relationship(self, arguments: dict) -> CallToolResult:
        """Add ArchiMate relationship to diagram."""
        try:
            relationship = self._create_relationship_from_data(arguments)
            self.generator.add_relationship(relationship)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Relationship '{relationship.relationship_type.value}' from '{relationship.from_element}' to '{relationship.to_element}' added successfully. Total relationships: {self.generator.get_relationship_count()}"
                )]
            )
            
        except Exception as e:
            raise ArchiMateValidationError(f"Failed to add relationship: {str(e)}")
    
    async def _validate_archimate_model(self, arguments: dict) -> CallToolResult:
        """Validate ArchiMate model."""
        try:
            strict = arguments.get("strict", False)
            self.validator.strict = strict
            
            errors = self.validator.validate_model(
                self.generator.elements,
                self.generator.relationships
            )
            
            if not errors:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"✅ ArchiMate model validation passed!\n\nModel statistics:\n- Elements: {self.generator.get_element_count()}\n- Relationships: {self.generator.get_relationship_count()}\n- Layers: {', '.join(self.generator.get_layers_used())}\n\nValidation mode: {'Strict' if strict else 'Standard'}"
                    )]
                )
            else:
                error_text = "\n".join([f"- {error}" for error in errors[:10]])  # Limit to first 10 errors
                if len(errors) > 10:
                    error_text += f"\n... and {len(errors) - 10} more errors"
                
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"❌ ArchiMate model validation failed!\n\nFound {len(errors)} error(s):\n{error_text}"
                    )]
                )
                
        except Exception as e:
            raise ArchiMateValidationError(f"Validation failed: {str(e)}")
    
    async def _generate_archimate_template(self, arguments: dict) -> CallToolResult:
        """Generate ArchiMate diagram from template."""
        try:
            template_type = arguments["template_type"]
            template_name = arguments["template_name"]
            customization = arguments.get("customization", {})
            
            # Get template
            template = None
            if template_type == "viewpoint":
                template = get_viewpoint_template(template_name)
                available = list(ARCHIMATE_VIEWPOINTS.keys())
            elif template_type == "pattern":
                template = get_pattern_template(template_name)
                available = list(ARCHITECTURE_PATTERNS.keys())
            elif template_type == "industry":
                template = get_industry_template(template_name)
                available = list(INDUSTRY_TEMPLATES.keys())
            else:
                raise ArchiMateTemplateError(f"Invalid template type: {template_type}")
            
            if not template:
                raise ArchiMateTemplateError(
                    f"Template '{template_name}' not found in {template_type} templates",
                    template_name=template_name,
                    template_type=template_type,
                    details={"available_templates": available}
                )
            
            # Clear existing diagram
            self.generator.clear()
            
            # Apply customization if provided
            elements_data = template.elements.copy()
            relationships_data = template.relationships.copy()
            
            if customization:
                # Apply customizations (element name changes, etc.)
                for elem_data in elements_data:
                    elem_id = elem_data["id"]
                    if elem_id in customization:
                        elem_data.update(customization[elem_id])
            
            # Create elements
            for elem_data in elements_data:
                element = self._create_element_from_data(elem_data)
                self.generator.add_element(element)
            
            # Create relationships
            for rel_data in relationships_data:
                relationship = self._create_relationship_from_data(rel_data)
                self.generator.add_relationship(relationship)
            
            # Set layout from template
            if hasattr(template, 'layout') and template.layout:
                layout = DiagramLayout(**template.layout)
                self.generator.set_layout(layout)
            
            # Generate PlantUML code
            plantuml_code = self.generator.generate_plantuml(
                title=template.name,
                description=template.description
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"ArchiMate diagram generated from {template_type} template '{template_name}'!\n\nTemplate: {template.name}\nDescription: {template.description}\n\nElements: {self.generator.get_element_count()}\nRelationships: {self.generator.get_relationship_count()}\n\nPlantUML Code:\n```plantuml\n{plantuml_code}\n```"
                )]
            )
            
        except Exception as e:
            raise ArchiMateTemplateError(f"Failed to generate template: {str(e)}")
    
    async def _export_archimate_diagram(self, arguments: dict) -> CallToolResult:
        """Export ArchiMate diagram."""
        try:
            title = arguments.get("title")
            description = arguments.get("description")
            output_path = arguments.get("output_path")
            clear_after_export = arguments.get("clear_after_export", False)
            
            # Generate PlantUML code
            plantuml_code = self.generator.generate_plantuml(title=title, description=description)
            
            result_text = "ArchiMate diagram exported successfully!\n\n"
            
            # Save to file if path provided
            if output_path:
                try:
                    output_file = Path(output_path)
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(plantuml_code)
                    
                    result_text += f"Saved to: {output_path}\n"
                except Exception as e:
                    result_text += f"Warning: Could not save to file: {str(e)}\n"
            
            result_text += f"Elements: {self.generator.get_element_count()}\n"
            result_text += f"Relationships: {self.generator.get_relationship_count()}\n"
            result_text += f"Layers: {', '.join(self.generator.get_layers_used())}\n\n"
            result_text += f"PlantUML Code:\n```plantuml\n{plantuml_code}\n```"
            
            # Clear diagram if requested
            if clear_after_export:
                self.generator.clear()
                result_text += "\n\nDiagram cleared after export."
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
            
        except Exception as e:
            raise ArchiMateGenerationError(f"Failed to export diagram: {str(e)}")
    
    async def _generate_full_architecture(self, arguments: dict) -> CallToolResult:
        """Generate complete layered enterprise architecture following ArchiMate methodology."""
        try:
            system_description = arguments["system_description"]
            business_domain = arguments.get("business_domain", "general")
            architecture_scope = arguments.get("architecture_scope", "system")
            include_views = arguments.get("include_views", ["motivation", "layered_view", "application_structure", "implementation_roadmap"])
            implementation_phases = arguments.get("implementation_phases", 3)
            
            # Generate all requested views
            architecture_views = self.full_arch_generator.generate_architecture(
                system_description=system_description,
                business_domain=business_domain,
                architecture_scope=architecture_scope,
                include_views=include_views,
                implementation_phases=implementation_phases
            )
            
            # Format output with proper ArchiMate methodology structure
            result_text = f"# 🏗️ Complete Enterprise Architecture\n\n"
            result_text += f"**System:** {system_description}\n"
            result_text += f"**Domain:** {business_domain.title()}\n"
            result_text += f"**Scope:** {architecture_scope.title()}\n"
            result_text += f"**Views Generated:** {len(architecture_views)}\n\n"
            result_text += "---\n\n"
            
            # Add each view with proper formatting
            view_descriptions = {
                "motivation": "Captures goals, stakeholders, drivers and requirements driving the architecture",
                "business_model_canvas": "Describes the high-level business logic and value proposition",
                "value_stream": "Shows how customer value is generated via capabilities",
                "strategy_capability": "Maps goals to capabilities and their strategic planning",
                "layered_view": "Models business, application, and technology structure in layers",
                "interaction_view": "Shows actor, process and application level interactions",
                "application_structure": "Detailed breakdown of application components and interfaces",
                "technology_structure": "Infrastructure-level component breakdown and relationships",
                "implementation_roadmap": "Represents phased evolution and delivery timeline"
            }
            
            for view_name, plantuml_code in architecture_views.items():
                view_title = view_name.replace("_", " ").title()
                description = view_descriptions.get(view_name, "ArchiMate view")
                
                result_text += f"## {view_title}\n\n"
                result_text += f"*{description}*\n\n"
                result_text += f"```plantuml\n{plantuml_code}\n```\n\n"
                result_text += "---\n\n"
            
            # Add implementation guidance
            result_text += "## 📋 Implementation Guidance\n\n"
            result_text += "### ArchiMate Methodology Notes:\n\n"
            result_text += "- **Motivation View** establishes the 'why' - stakeholder needs and business drivers\n"
            result_text += "- **Layered View** provides the core architectural structure across business, application, and technology\n"
            result_text += "- **Application Structure** details the 'how' of system implementation\n"
            result_text += "- **Implementation Roadmap** defines the 'when' with phased delivery approach\n\n"
            
            result_text += "### Next Steps:\n\n"
            result_text += "1. **Validate** each view with stakeholders\n"
            result_text += "2. **Refine** elements and relationships based on feedback\n"
            result_text += "3. **Detail** critical components in focused views\n"
            result_text += "4. **Align** implementation phases with business priorities\n"
            result_text += "5. **Monitor** architecture evolution against original goals\n\n"
            
            result_text += f"✅ **Architecture Generation Complete**\n"
            result_text += f"Generated {len(architecture_views)} coordinated ArchiMate views following enterprise architecture best practices.\n\n"
            
            # Additional metadata
            total_elements = sum(view.count("(") for view in architecture_views.values())
            total_relationships = sum(view.count("Rel_") for view in architecture_views.values())
            
            result_text += f"**Statistics:**\n"
            result_text += f"- Views: {len(architecture_views)}\n"
            result_text += f"- Estimated Elements: ~{total_elements}\n"
            result_text += f"- Estimated Relationships: ~{total_relationships}\n"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
            
        except Exception as e:
            raise ArchiMateGenerationError(f"Failed to generate full architecture: {str(e)}")
    
    def _create_element_from_data(self, data: dict) -> ArchiMateElement:
        """Create ArchiMateElement from data dictionary."""
        # Map layer string to enum
        layer_str = data["layer"]
        try:
            layer = ArchiMateLayer(layer_str)
        except ValueError:
            raise ArchiMateValidationError(f"Invalid layer: {layer_str}")
        
        # Determine aspect from element type
        element_type = data["element_type"]
        aspect = self._get_aspect_for_element_type(element_type)
        
        return ArchiMateElement(
            id=data["id"],
            name=data["name"],
            element_type=element_type,
            layer=layer,
            aspect=aspect,
            description=data.get("description"),
            stereotype=data.get("stereotype"),
            properties=data.get("properties", {}),
            documentation=data.get("documentation")
        )
    
    def _create_relationship_from_data(self, data: dict) -> ArchiMateRelationship:
        """Create ArchiMateRelationship from data dictionary."""
        return create_relationship(
            relationship_id=data["id"],
            from_element=data["from_element"],
            to_element=data["to_element"],
            relationship_type=data["relationship_type"],
            direction=data.get("direction"),
            description=data.get("description"),
            label=data.get("label")
        )
    
    def _get_aspect_for_element_type(self, element_type: str) -> ArchiMateAspect:
        """Determine aspect for element type."""
        # Active Structure elements
        active_structure = [
            "Business_Actor", "Business_Role", "Business_Collaboration", "Business_Interface",
            "Application_Component", "Application_Collaboration", "Application_Interface",
            "Node", "Device", "System_Software", "Technology_Collaboration", "Technology_Interface",
            "Path", "Communication_Network", "Equipment", "Facility", "Distribution_Network",
            "Stakeholder", "Resource"
        ]
        
        # Passive Structure elements
        passive_structure = [
            "Business_Object", "Business_Contract", "Business_Representation", "Location",
            "Data_Object", "Artifact", "Material", "Meaning", "Value", "Deliverable", 
            "Plateau", "Gap"
        ]
        
        # Behavior elements (everything else)
        if element_type in active_structure:
            return ArchiMateAspect.ACTIVE_STRUCTURE
        elif element_type in passive_structure:
            return ArchiMateAspect.PASSIVE_STRUCTURE
        else:
            return ArchiMateAspect.BEHAVIOR
    
    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="archi-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


def main() -> None:
    """Main entry point for the ArchiMate MCP server."""
    server = ArchiMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()