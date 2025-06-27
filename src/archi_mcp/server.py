"""ArchiMate MCP Server implementation using FastMCP."""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field

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

# Initialize FastMCP server
mcp = FastMCP("archi-mcp")

# Initialize components
generator = ArchiMateGenerator()
validator = ArchiMateValidator()
full_arch_generator = FullArchitectureGenerator()

# Pydantic models for input validation
class ElementInput(BaseModel):
    id: str = Field(..., description="Unique element identifier")
    name: str = Field(..., description="Element display name")
    element_type: str = Field(..., description="ArchiMate element type")
    layer: str = Field(..., description="ArchiMate layer")
    description: Optional[str] = Field(None, description="Element description")
    stereotype: Optional[str] = Field(None, description="Element stereotype")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional element properties")

class RelationshipInput(BaseModel):
    id: str = Field(..., description="Unique relationship identifier")
    from_element: str = Field(..., description="Source element ID")
    to_element: str = Field(..., description="Target element ID")
    relationship_type: str = Field(..., description="ArchiMate relationship type")
    direction: Optional[str] = Field(None, description="Optional direction (Up, Down, Left, Right)")
    description: Optional[str] = Field(None, description="Relationship description")
    label: Optional[str] = Field(None, description="Relationship label")

class LayoutInput(BaseModel):
    direction: Optional[str] = Field(None, description="Layout direction (horizontal, vertical, layered)")
    show_legend: Optional[bool] = Field(None, description="Show diagram legend")
    show_title: Optional[bool] = Field(None, description="Show diagram title")
    group_by_layer: Optional[bool] = Field(None, description="Group elements by layer")

class DiagramInput(BaseModel):
    elements: List[ElementInput] = Field(..., description="List of ArchiMate elements with properties")
    relationships: Optional[List[RelationshipInput]] = Field(default_factory=list, description="List of relationships between elements")
    layout: Optional[LayoutInput] = Field(None, description="Layout preferences")
    title: Optional[str] = Field(None, description="Diagram title")
    description: Optional[str] = Field(None, description="Diagram description")

class TemplateInput(BaseModel):
    template_type: str = Field(..., description="Template category (viewpoint, pattern, industry)")
    template_name: str = Field(..., description="Specific template name")
    customization: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Template customization parameters")

class FullArchitectureInput(BaseModel):
    system_description: str = Field(..., description="Description of the target system or business problem to architect")
    business_domain: str = Field(default="general", description="Business domain (e.g., 'banking', 'healthcare', 'e-commerce', 'manufacturing')")
    architecture_scope: str = Field(default="system", description="Scope of architecture (enterprise, system, application, component)")
    include_views: List[str] = Field(
        default=["motivation", "layered_view", "application_structure", "implementation_roadmap"],
        description="Which ArchiMate views to include"
    )
    implementation_phases: int = Field(default=3, ge=1, le=6, description="Number of implementation phases for roadmap")

# Utility functions
def _create_element_from_data(data: ElementInput) -> ArchiMateElement:
    """Create ArchiMateElement from input data."""
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

def _create_relationship_from_data(data: RelationshipInput) -> ArchiMateRelationship:
    """Create ArchiMateRelationship from input data."""
    return create_relationship(
        relationship_id=data.id,
        from_element=data.from_element,
        to_element=data.to_element,
        relationship_type=data.relationship_type,
        direction=data.direction,
        description=data.description,
        label=data.label
    )

def _get_aspect_for_element_type(element_type: str) -> ArchiMateAspect:
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

# MCP Tools using FastMCP decorators
@mcp.tool()
def create_archimate_diagram(diagram: DiagramInput) -> str:
    """Generate complete ArchiMate diagrams from structured input with elements and relationships."""
    try:
        # Clear existing diagram
        generator.clear()
        
        # Add elements
        for elem_data in diagram.elements:
            element = _create_element_from_data(elem_data)
            generator.add_element(element)
        
        # Add relationships
        for rel_data in diagram.relationships:
            relationship = _create_relationship_from_data(rel_data)
            generator.add_relationship(relationship)
        
        # Set layout if provided
        if diagram.layout:
            layout = DiagramLayout(
                direction=diagram.layout.direction,
                show_legend=diagram.layout.show_legend,
                show_title=diagram.layout.show_title,
                group_by_layer=diagram.layout.group_by_layer
            )
            generator.set_layout(layout)
        
        # Generate PlantUML code
        plantuml_code = generator.generate_plantuml(title=diagram.title, description=diagram.description)
        
        # Get diagram statistics
        stats = {
            "elements": generator.get_element_count(),
            "relationships": generator.get_relationship_count(),
            "layers": generator.get_layers_used()
        }
        
        return f"ArchiMate diagram created successfully!\n\nStatistics:\n- Elements: {stats['elements']}\n- Relationships: {stats['relationships']}\n- Layers: {', '.join(stats['layers'])}\n\nPlantUML Code:\n```plantuml\n{plantuml_code}\n```"
        
    except Exception as e:
        raise ArchiMateGenerationError(f"Failed to create diagram: {str(e)}")

@mcp.tool()
def add_archimate_element(
    element_type: str,
    id: str,
    name: str,
    layer: str,
    description: Optional[str] = None,
    stereotype: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> str:
    """Add single ArchiMate element to existing diagram."""
    try:
        element_input = ElementInput(
            id=id,
            name=name,
            element_type=element_type,
            layer=layer,
            description=description,
            stereotype=stereotype,
            properties=properties or {}
        )
        element = _create_element_from_data(element_input)
        generator.add_element(element)
        
        return f"Element '{element.name}' ({element.element_type}) added successfully to diagram. Total elements: {generator.get_element_count()}"
        
    except Exception as e:
        raise ArchiMateValidationError(f"Failed to add element: {str(e)}")

@mcp.tool()
def add_archimate_relationship(
    id: str,
    from_element: str,
    to_element: str,
    relationship_type: str,
    direction: Optional[str] = None,
    description: Optional[str] = None,
    label: Optional[str] = None
) -> str:
    """Add relationship between ArchiMate elements."""
    try:
        relationship_input = RelationshipInput(
            id=id,
            from_element=from_element,
            to_element=to_element,
            relationship_type=relationship_type,
            direction=direction,
            description=description,
            label=label
        )
        relationship = _create_relationship_from_data(relationship_input)
        generator.add_relationship(relationship)
        
        return f"Relationship '{relationship.relationship_type.value}' from '{relationship.from_element}' to '{relationship.to_element}' added successfully. Total relationships: {generator.get_relationship_count()}"
        
    except Exception as e:
        raise ArchiMateValidationError(f"Failed to add relationship: {str(e)}")

@mcp.tool()
def validate_archimate_model(strict: bool = False) -> str:
    """Validate ArchiMate model against ArchiMate 3.2 specification."""
    try:
        validator.strict = strict
        
        errors = validator.validate_model(
            generator.elements,
            generator.relationships
        )
        
        if not errors:
            return f"✅ ArchiMate model validation passed!\n\nModel statistics:\n- Elements: {generator.get_element_count()}\n- Relationships: {generator.get_relationship_count()}\n- Layers: {', '.join(generator.get_layers_used())}\n\nValidation mode: {'Strict' if strict else 'Standard'}"
        else:
            error_text = "\n".join([f"- {error}" for error in errors[:10]])  # Limit to first 10 errors
            if len(errors) > 10:
                error_text += f"\n... and {len(errors) - 10} more errors"
            
            return f"❌ ArchiMate model validation failed!\n\nFound {len(errors)} error(s):\n{error_text}"
            
    except Exception as e:
        raise ArchiMateValidationError(f"Validation failed: {str(e)}")

@mcp.tool()
def generate_archimate_template(template: TemplateInput) -> str:
    """Generate ArchiMate diagram from predefined templates."""
    try:
        # Get template
        template_obj = None
        if template.template_type == "viewpoint":
            template_obj = get_viewpoint_template(template.template_name)
            available = list(ARCHIMATE_VIEWPOINTS.keys())
        elif template.template_type == "pattern":
            template_obj = get_pattern_template(template.template_name)
            available = list(ARCHITECTURE_PATTERNS.keys())
        elif template.template_type == "industry":
            template_obj = get_industry_template(template.template_name)
            available = list(INDUSTRY_TEMPLATES.keys())
        else:
            raise ArchiMateTemplateError(f"Invalid template type: {template.template_type}")
        
        if not template_obj:
            raise ArchiMateTemplateError(
                f"Template '{template.template_name}' not found in {template.template_type} templates",
                template_name=template.template_name,
                template_type=template.template_type,
                details={"available_templates": available}
            )
        
        # Clear existing diagram
        generator.clear()
        
        # Apply customization if provided
        elements_data = template_obj.elements.copy()
        relationships_data = template_obj.relationships.copy()
        
        if template.customization:
            # Apply customizations (element name changes, etc.)
            for elem_data in elements_data:
                elem_id = elem_data["id"]
                if elem_id in template.customization:
                    elem_data.update(template.customization[elem_id])
        
        # Create elements
        for elem_data in elements_data:
            element_input = ElementInput(**elem_data)
            element = _create_element_from_data(element_input)
            generator.add_element(element)
        
        # Create relationships
        for rel_data in relationships_data:
            relationship_input = RelationshipInput(**rel_data)
            relationship = _create_relationship_from_data(relationship_input)
            generator.add_relationship(relationship)
        
        # Set layout from template
        if hasattr(template_obj, 'layout') and template_obj.layout:
            layout = DiagramLayout(**template_obj.layout)
            generator.set_layout(layout)
        
        # Generate PlantUML code
        plantuml_code = generator.generate_plantuml(
            title=template_obj.name,
            description=template_obj.description
        )
        
        return f"ArchiMate diagram generated from {template.template_type} template '{template.template_name}'!\n\nTemplate: {template_obj.name}\nDescription: {template_obj.description}\n\nElements: {generator.get_element_count()}\nRelationships: {generator.get_relationship_count()}\n\nPlantUML Code:\n```plantuml\n{plantuml_code}\n```"
        
    except Exception as e:
        raise ArchiMateTemplateError(f"Failed to generate template: {str(e)}")

@mcp.tool()
def export_archimate_diagram(
    title: Optional[str] = None,
    description: Optional[str] = None,
    output_path: Optional[str] = None,
    clear_after_export: bool = False
) -> str:
    """Export ArchiMate diagram to PlantUML format and optionally save to file."""
    try:
        # Generate PlantUML code
        plantuml_code = generator.generate_plantuml(title=title, description=description)
        
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
        
        result_text += f"Elements: {generator.get_element_count()}\n"
        result_text += f"Relationships: {generator.get_relationship_count()}\n"
        result_text += f"Layers: {', '.join(generator.get_layers_used())}\n\n"
        result_text += f"PlantUML Code:\n```plantuml\n{plantuml_code}\n```"
        
        # Clear diagram if requested
        if clear_after_export:
            generator.clear()
            result_text += "\n\nDiagram cleared after export."
        
        return result_text
        
    except Exception as e:
        raise ArchiMateGenerationError(f"Failed to export diagram: {str(e)}")

@mcp.tool()
def generate_full_architecture(architecture: FullArchitectureInput) -> str:
    """Generate a complete layered enterprise architecture following ArchiMate methodology with multiple coordinated views."""
    try:
        # Generate all requested views
        architecture_views = full_arch_generator.generate_architecture(
            system_description=architecture.system_description,
            business_domain=architecture.business_domain,
            architecture_scope=architecture.architecture_scope,
            include_views=architecture.include_views,
            implementation_phases=architecture.implementation_phases
        )
        
        # Format output with proper ArchiMate methodology structure
        result_text = f"# 🏗️ Complete Enterprise Architecture\n\n"
        result_text += f"**System:** {architecture.system_description}\n"
        result_text += f"**Domain:** {architecture.business_domain.title()}\n"
        result_text += f"**Scope:** {architecture.architecture_scope.title()}\n"
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
        
        return result_text
        
    except Exception as e:
        raise ArchiMateGenerationError(f"Failed to generate full architecture: {str(e)}")

def main() -> None:
    """Main entry point for the ArchiMate MCP server."""
    logger.info("Starting ArchiMate MCP Server with FastMCP")
    
    try:
        # Run the FastMCP server
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()