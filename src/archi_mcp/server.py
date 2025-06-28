"""ArchiMate MCP Server implementation using FastMCP."""

import json
import sys
import asyncio
import subprocess
import os
import tempfile
import base64
import zlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Image import odstránený - používame iba PNG do /tmp

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
from .conversation_logger import log_mcp_tool_call, save_conversation_log
from .mcp_debug_logger import (
    mcp_debug_logger, 
    log_mcp_call_start, 
    log_mcp_call_result, 
    log_mcp_error,
    get_debug_log_path
)
from .debug_tools import (
    analyze_generator_state,
    analyze_element_normalization_issues,
    identify_architecture_problems
)
from .problem_extractor import (
    extract_recent_problems,
    extract_latest_problems
)

# Setup logging
setup_logging(level="INFO")
logger = get_logger("archi_mcp.server")

# Initialize FastMCP server
mcp = FastMCP("archi-mcp")

# Initialize components
generator = ArchiMateGenerator()
validator = ArchiMateValidator()
full_arch_generator = FullArchitectureGenerator()

# Tool call wrapper for automatic debug logging  
def debug_tool_call(func):
    """Decorator to automatically log MCP tool calls for debugging."""
    import functools
    
    @functools.wraps(func)
    def wrapper(**kwargs):  # Only use **kwargs to avoid *args issue
        tool_name = func.__name__
        parameters = kwargs.copy()
        
        # Convert complex objects to string representation for logging
        log_parameters = {}
        for param_name, param_value in parameters.items():
            if isinstance(param_value, (dict, list)):
                log_parameters[param_name] = param_value
            else:
                log_parameters[param_name] = str(param_value) if param_value is not None else None
        
        # Start logging
        call_id = log_mcp_call_start(tool_name, log_parameters)
        
        try:
            # Execute the tool
            result = func(**kwargs)
            
            # Log successful result
            log_mcp_call_result(call_id, result, success=True)
            
            # Also log to conversation logger for compatibility
            log_mcp_tool_call(tool_name, log_parameters, result, True)
            
            return result
            
        except Exception as e:
            # Log error
            log_mcp_call_result(call_id, str(e), success=False, error=str(e))
            log_mcp_error(e, f"Error in tool: {tool_name}")
            
            # Also log to conversation logger for compatibility
            log_mcp_tool_call(tool_name, log_parameters, str(e), False, str(e))
            
            # Re-raise the exception
            raise
    
    return wrapper

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
    """Create ArchiMateElement from input data with normalization."""
    from .element_normalizer import normalize_element_type, validate_element_id, validate_element_name
    
    # Normalize element type
    normalized_element_type = normalize_element_type(data.element_type)
    
    # Validate and normalize element ID
    normalized_id = validate_element_id(data.id)
    
    # Validate and normalize element name  
    normalized_name = validate_element_name(data.name)
    # Remove quotes for internal storage
    clean_name = normalized_name.strip('"') if normalized_name.startswith('"') else normalized_name
    
    # Map layer string to enum
    try:
        layer = ArchiMateLayer(data.layer)
    except ValueError:
        raise ArchiMateValidationError(f"Invalid layer: {data.layer}")
    
    # Determine aspect from normalized element type
    aspect = _get_aspect_for_element_type(normalized_element_type)
    
    return ArchiMateElement(
        id=normalized_id,
        name=clean_name,
        element_type=normalized_element_type,
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
        "Stakeholder", "Motivation_Stakeholder", "Strategy_Resource"
    ]
    
    # Passive Structure elements
    passive_structure = [
        "Business_Object", "Business_Contract", "Business_Representation", "Location",
        "Data_Object", "Artifact", "Material", "Meaning", "Motivation_Meaning", "Value", "Motivation_Value", 
        "Deliverable", "Implementation_Deliverable", "Plateau", "Implementation_Plateau", "Gap", "Implementation_Gap"
    ]
    
    # Behavior elements (everything else)
    if element_type in active_structure:
        return ArchiMateAspect.ACTIVE_STRUCTURE
    elif element_type in passive_structure:
        return ArchiMateAspect.PASSIVE_STRUCTURE
    else:
        return ArchiMateAspect.BEHAVIOR

# Enhanced validation function with comprehensive logging
def _validate_plantuml_renders(plantuml_code: str, tool_name: str = "unknown", context: dict = None) -> tuple[bool, str]:
    """
    Enhanced PlantUML validation with comprehensive error logging.
    Returns (success: bool, error_message: str)
    """
    from .validation_logger import validation_logger
    
    # Use comprehensive validation with logging
    return validation_logger.validate_plantuml_comprehensive(plantuml_code, tool_name, context)

# MCP Tools using FastMCP decorators
@mcp.tool()
@debug_tool_call
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
        
        # Handle empty diagrams gracefully
        if len(diagram.elements) == 0:
            # Create a minimal valid PlantUML diagram for empty case
            plantuml_code = f"""@startuml
!include <archimate/Archimate>
title {diagram.title or "Empty ArchiMate Diagram"}
note as N1
  No elements defined in this diagram
end note
@enduml"""
        else:
            # Generate PlantUML code for normal diagrams
            plantuml_code = generator.generate_plantuml(title=diagram.title, description=diagram.description)
        
        # MANDATORY: Validate that diagram actually renders (skip validation for empty diagrams)
        if len(diagram.elements) > 0:
            context = {
                "elements_count": len(diagram.elements),
                "relationships_count": len(diagram.relationships) if diagram.relationships else 0,
                "title": diagram.title,
                "has_layout": diagram.layout is not None
            }
            renders_ok, error_msg = _validate_plantuml_renders(plantuml_code, "create_archimate_diagram", context)
            if not renders_ok:
                raise ArchiMateGenerationError(f"Generated diagram failed validation - {error_msg}")
            render_status = "VERIFIED ✅"
        else:
            # Empty diagrams don't need full validation
            render_status = "EMPTY DIAGRAM ✓"
        
        # Get diagram statistics
        stats = {
            "elements": generator.get_element_count(),
            "relationships": generator.get_relationship_count(),
            "layers": generator.get_layers_used()
        }
        
        # Generate PNG to /tmp directory - IBA PNG, žiadne URL ani iné prístupy
        try:
            png_path = generator.generate_png_to_tmp(title=diagram.title)
            png_info = f"📁 **PNG File:** `{png_path}`"
        except Exception as png_error:
            png_info = f"⚠️ **PNG Generation Failed:** {str(png_error)}"
        
        # Vraciam iba jednoduché hlásenie s cestou k PNG súboru
        return f"✅ ArchiMate diagram created and validated successfully!\n\nStatistics:\n- Elements: {stats['elements']}\n- Relationships: {stats['relationships']}\n- Layers: {', '.join(stats['layers'])}\n- Render Status: {render_status}\n- {png_info}\n\n### 📄 PlantUML Source Code\n```plantuml\n{plantuml_code}\n```"
        
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
        
        # MANDATORY: Validate that diagram actually renders
        renders_ok, error_msg = _validate_plantuml_renders(plantuml_code)
        if not renders_ok:
            raise ArchiMateGenerationError(f"Generated template diagram failed validation - {error_msg}")
        
        # Generate PNG to /tmp directory
        try:
            png_path = generator.generate_png_to_tmp(title=template_obj.name)
            png_info = f"📁 **PNG File:** `{png_path}`\n"
        except Exception as png_error:
            png_info = f"⚠️ **PNG Generation Failed:** {str(png_error)}\n"
        
        return f"✅ ArchiMate diagram generated from {template.template_type} template '{template.template_name}' and validated!\n\nTemplate: {template_obj.name}\nDescription: {template_obj.description}\n\nElements: {generator.get_element_count()}\nRelationships: {generator.get_relationship_count()}\nRender Status: VERIFIED ✅\n{png_info}\nPlantUML Code:\n```plantuml\n{plantuml_code}\n```"
        
    except Exception as e:
        raise ArchiMateTemplateError(f"Failed to generate template: {str(e)}")


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
        
        # MANDATORY: Validate all views before returning
        validation_results = {}
        for view_name, plantuml_code in architecture_views.items():
            renders_ok, error_msg = _validate_plantuml_renders(plantuml_code)
            validation_results[view_name] = (renders_ok, error_msg)
            if not renders_ok:
                raise ArchiMateGenerationError(f"Generated view '{view_name}' failed validation - {error_msg}")
        
        for view_name, plantuml_code in architecture_views.items():
            view_title = view_name.replace("_", " ").title()
            description = view_descriptions.get(view_name, "ArchiMate view")
            
            result_text += f"## {view_title} ✅\n\n"
            result_text += f"*{description}*\n\n"
            result_text += f"**Render Status:** VERIFIED ✅\n\n"
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
        
        result_text += f"✅ **Architecture Generation Complete - All Views Validated**\n"
        result_text += f"Generated {len(architecture_views)} coordinated ArchiMate views following enterprise architecture best practices.\n\n"
        
        # Additional metadata
        total_elements = sum(view.count("(") for view in architecture_views.values())
        total_relationships = sum(view.count("Rel_") for view in architecture_views.values())
        
        result_text += f"**Statistics:**\n"
        result_text += f"- Views: {len(architecture_views)}\n"
        result_text += f"- Estimated Elements: ~{total_elements}\n"
        result_text += f"- Estimated Relationships: ~{total_relationships}\n"
        result_text += f"- Validation Status: ALL VIEWS VERIFIED ✅\n"
        
        return result_text
        
    except Exception as e:
        raise ArchiMateGenerationError(f"Failed to generate full architecture: {str(e)}")

# Všetky image testing tools boli odstránené - použitím iba PNG do /tmp

@mcp.tool()
def validate_plantuml_syntax(
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """Validate PlantUML syntax and test renderability using PlantUML jar."""
    try:
        # Generate PlantUML code
        plantuml_code = generator.generate_plantuml(title=title, description=description)
        
        # Create temporary PlantUML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
            f.write(plantuml_code)
            temp_puml = f.name
        
        try:
            # Find PlantUML jar
            plantuml_jar = None
            possible_locations = [
                "/Users/patrik/Projects/archi-mcp/plantuml.jar",
                "./plantuml.jar",
                "/usr/local/bin/plantuml.jar",
                "/opt/homebrew/bin/plantuml.jar"
            ]
            
            for jar_path in possible_locations:
                if os.path.exists(jar_path):
                    plantuml_jar = jar_path
                    break
            
            if not plantuml_jar:
                return f"❌ PlantUML jar not found. Cannot validate syntax.\n\nPlantUML Code:\n```plantuml\n{plantuml_code}\n```"
            
            # Test syntax validation
            check_cmd = [
                "java", "-jar", plantuml_jar,
                "-checkonly",
                temp_puml
            ]
            
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=15)
            
            # Test image generation
            gen_cmd = [
                "java", "-jar", plantuml_jar,
                "-tpng",
                temp_puml
            ]
            
            gen_result = subprocess.run(gen_cmd, capture_output=True, text=True, timeout=30)
            
            # Analyze results - PlantUML may return non-zero even for successful generation
            syntax_valid = check_result.returncode == 0 or "parsing ok" in check_result.stderr.lower()
            render_successful = gen_result.returncode == 0 or gen_result.returncode == 200
            
            # Check if image was actually generated
            generated_image = Path(temp_puml).parent / f"{Path(temp_puml).stem}.png"
            image_created = generated_image.exists()
            
            # Get image size if created
            image_size = 0
            if image_created:
                image_size = generated_image.stat().st_size
                # Clean up generated image
                generated_image.unlink()
            
            # Format validation report
            status = "✅ VALID" if syntax_valid and render_successful and image_created else "❌ INVALID"
            
            report = f"{status} - PlantUML Validation Report\n\n"
            report += f"**Syntax Check:** {'✅ PASSED' if syntax_valid else '❌ FAILED'}\n"
            report += f"**Render Test:** {'✅ PASSED' if render_successful else '❌ FAILED'}\n"
            report += f"**Image Generated:** {'✅ YES' if image_created else '❌ NO'}\n"
            
            if image_created:
                report += f"**Image Size:** {image_size} bytes\n"
            
            report += f"\n**Diagram Statistics:**\n"
            report += f"- Elements: {generator.get_element_count()}\n"
            report += f"- Relationships: {generator.get_relationship_count()}\n"
            report += f"- Layers: {', '.join(generator.get_layers_used())}\n"
            
            # Add error details if any
            if not syntax_valid:
                report += f"\n**Syntax Errors:**\n```\n{check_result.stderr}\n```\n"
            
            if not render_successful:
                report += f"\n**Render Errors:**\n```\n{gen_result.stderr}\n```\n"
            
            report += f"\n**PlantUML Code:**\n```plantuml\n{plantuml_code}\n```"
            
            return report
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_puml):
                os.unlink(temp_puml)
                
    except subprocess.TimeoutExpired:
        raise ArchiMateGenerationError("PlantUML validation timed out")
    except Exception as e:
        raise ArchiMateGenerationError(f"Failed to validate PlantUML syntax: {str(e)}")


# 📝 DEBUG & CONVERSATION LOGGING TOOLS
@mcp.tool()
def get_debug_log_info() -> str:
    """Get information about the current MCP debug log session."""
    try:
        stats = mcp_debug_logger.get_session_stats()
        log_path = get_debug_log_path()
        
        return f"""✅ **MCP Debug Logging Active**

## 📊 Current Session Stats
- **Session ID:** `{stats['session_id']}`
- **Total Tool Calls:** {stats['total_calls']}
- **Successful:** {stats['successful_calls']} ✅
- **Failed:** {stats['failed_calls']} ❌
- **Debug Entries:** {stats['total_entries']}

## 📁 Debug Log File
**Path:** `{log_path}`

This debug log contains:
- 🔧 **Detailed tool call tracking** with parameters and results
- ⏱️ **Timing information** for performance analysis
- 🚨 **Error logging** with full tracebacks
- 💬 **Client-server communication** events
- 📊 **Live session statistics**

The log is automatically updated in real-time as you use MCP tools.
"""
    except Exception as e:
        return f"❌ Failed to get debug log info: {str(e)}"

@mcp.tool()
def save_conversation_to_tmp() -> str:
    """Save current MCP conversation log to markdown file in /tmp directory."""
    try:
        log_path = save_conversation_log()
        debug_path = get_debug_log_path()
        
        return f"""✅ Conversation logs saved successfully!

## 📁 **Conversation Log:** `{log_path}`
- All MCP tool calls with parameters and results
- Conversation timeline
- Session statistics
- Success/failure tracking

## 🐛 **Debug Log:** `{debug_path}`
- Enhanced debug information
- Real-time tool call tracking
- Error tracebacks and timing
- Client-server communication

You can open both files to review the complete session history and debug information."""
    except Exception as e:
        return f"❌ Failed to save conversation log: {str(e)}"

@mcp.tool()
def analyze_current_architecture() -> str:
    """Analyze the current ArchiMate architecture state and identify problems."""
    try:
        # Analyze generator state
        state_analysis = analyze_generator_state(generator)
        
        # Identify architecture problems
        problems = identify_architecture_problems(generator, validator)
        
        # Analyze element normalization
        normalization_analysis = analyze_element_normalization_issues()
        
        # Create comprehensive report
        report = f"""# 🔍 ArchiMate Architecture Analysis Report

## 📊 Current Architecture State

### **Elements:** {state_analysis['element_count']}
### **Relationships:** {state_analysis['relationship_count']}
### **Layers Used:** {', '.join(state_analysis['layers_used']) if state_analysis['layers_used'] else 'None'}

## 🎯 Architecture Health Summary
- **Overall Status:** {'✅ Healthy' if problems['summary']['overall_health'] == 'healthy' else '⚠️ Issues Found'}
- **Critical Issues:** {problems['summary']['total_issues']}
- **Warnings:** {problems['summary']['total_warnings']}

"""

        # Add element details if any exist
        if state_analysis['elements']:
            report += "## 🏗️ Current Elements\n\n"
            for element_id, element in state_analysis['elements'].items():
                report += f"- **{element['name']}** (`{element_id}`)\n"
                report += f"  - Type: {element['element_type']}\n"
                report += f"  - Layer: {element['layer']}\n"
                report += f"  - PlantUML: `{element['plantuml_output']}`\n\n"
        
        # Add relationship details if any exist
        if state_analysis['relationships']:
            report += "## 🔗 Current Relationships\n\n"
            for rel in state_analysis['relationships']:
                report += f"- **{rel['id']}**: {rel['from_element']} → {rel['to_element']}\n"
                report += f"  - Type: {rel['relationship_type']}\n"
                report += f"  - PlantUML: `{rel['plantuml_output']}`\n\n"
        
        # Add critical issues
        if problems['critical_issues']:
            report += "## 🚨 Critical Issues\n\n"
            for issue in problems['critical_issues']:
                report += f"### ❌ {issue.get('issue', 'Unknown Issue')}\n"
                report += f"**Description:** {issue.get('description', issue.get('error', 'No description'))}\n"
                if 'recommendation' in issue:
                    report += f"**Recommendation:** {issue['recommendation']}\n"
                report += "\n"
        
        # Add warnings
        if problems['warnings']:
            report += "## ⚠️ Warnings\n\n"
            for warning in problems['warnings']:
                report += f"### ⚠️ {warning['issue']}\n"
                report += f"**Description:** {warning['description']}\n"
                report += f"**Recommendation:** {warning['recommendation']}\n\n"
        
        # Add element normalization analysis
        normalization_issues = [case for case in normalization_analysis['test_cases'] if case['status'] == 'error']
        if normalization_issues:
            report += "## 🔧 Element Normalization Issues\n\n"
            for issue in normalization_issues:
                report += f"- **{issue['input_type']}** in {issue['layer']} layer: {issue['error']}\n"
        
        # Add recommendations
        if problems['recommendations']:
            report += "\n## 💡 Recommendations\n\n"
            for rec in problems['recommendations']:
                report += f"- {rec}\n"
        
        return report
        
    except Exception as e:
        return f"❌ Failed to analyze architecture: {str(e)}"

@mcp.tool()
def test_element_normalization() -> str:
    """Test element type normalization across all ArchiMate layers."""
    try:
        analysis = analyze_element_normalization_issues()
        
        report = "# 🧪 Element Normalization Test Results\n\n"
        
        # Summary
        total_tests = len(analysis['test_cases'])
        successful_tests = len([case for case in analysis['test_cases'] if case['status'] == 'success'])
        failed_tests = total_tests - successful_tests
        
        report += f"## 📊 Test Summary\n"
        report += f"- **Total Tests:** {total_tests}\n"
        report += f"- **Successful:** {successful_tests} ✅\n"
        report += f"- **Failed:** {failed_tests} ❌\n"
        report += f"- **Success Rate:** {(successful_tests/total_tests*100):.1f}%\n\n"
        
        # Layer-specific results
        report += "## 🏗️ Layer-Specific Mappings\n\n"
        for layer, mappings in analysis['layer_specific_mappings'].items():
            report += f"### {layer.title()} Layer\n"
            for input_type, normalized in mappings.items():
                report += f"- `{input_type}` → `{normalized}`\n"
            report += "\n"
        
        # Failed tests
        if analysis['issues_found']:
            report += "## ❌ Failed Normalizations\n\n"
            for issue in analysis['issues_found']:
                report += f"- **{issue['element_type']}** in {issue['layer']} layer: {issue['error']}\n"
        
        return report
        
    except Exception as e:
        return f"❌ Failed to test element normalization: {str(e)}"

@mcp.tool()
def extract_problems_from_latest_attempt() -> str:
    """Extract and analyze problems from the most recent architecture creation attempt."""
    try:
        analysis = extract_latest_problems()
        
        report = f"""# 🔍 Latest Attempt Problem Analysis

## 📊 Summary
**{analysis['summary']}**

### Quick Stats
- **Total Errors:** {analysis['total_errors']}
- **Timeframe:** {analysis['timeframe']}

"""
        
        # Error type breakdown
        if analysis['error_types']:
            report += "## 🏷️ Error Types\n\n"
            for error_type, count in sorted(analysis['error_types'].items(), key=lambda x: x[1], reverse=True):
                report += f"- **{error_type}**: {count} occurrences\n"
            report += "\n"
        
        # Critical issues
        if analysis['critical_issues']:
            report += "## 🚨 Critical Issues\n\n"
            for issue in analysis['critical_issues']:
                severity_icon = "🚨" if issue['severity'] == 'critical' else "⚠️"
                report += f"### {severity_icon} {issue['issue']}\n"
                report += f"**Description:** {issue['description']}\n"
                report += f"**Recommendation:** {issue['recommendation']}\n\n"
        
        # Pattern analysis
        patterns = analysis['pattern_analysis']
        if any(patterns.values()):
            report += "## 🔍 Pattern Analysis\n\n"
            
            for pattern_type, pattern_list in patterns.items():
                if pattern_list:
                    report += f"### {pattern_type.replace('_', ' ').title()}\n"
                    for pattern in pattern_list:
                        report += f"- {pattern}\n"
                    report += "\n"
        
        # Sample errors for debugging
        if analysis['sample_errors']:
            report += "## 🐛 Sample Errors for Debugging\n\n"
            for i, sample in enumerate(analysis['sample_errors'], 1):
                report += f"### Error {i}: {sample['error_type']}\n"
                report += f"**Tool:** {sample['tool_name']}\n"
                report += f"**Time:** {sample['timestamp']}\n"
                report += f"**Message:** {sample['error_message']}\n"
                if sample['plantuml_sample']:
                    report += f"**PlantUML Sample:**\n```plantuml\n{sample['plantuml_sample']}\n```\n"
                report += "\n"
        
        # Recommendations
        if analysis['recommendations']:
            report += "## 💡 Recommended Actions\n\n"
            for i, rec in enumerate(analysis['recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        return report
        
    except Exception as e:
        return f"❌ Failed to extract problems from latest attempt: {str(e)}"

@mcp.tool()
def extract_problems_from_recent_attempts(minutes: int = 10) -> str:
    """Extract and analyze problems from recent architecture attempts.
    
    Args:
        minutes: Look back this many minutes (default: 10)
    """
    try:
        analysis = extract_recent_problems(minutes)
        
        report = f"""# 🔍 Recent Problems Analysis (Last {minutes} minutes)

## 📊 Summary
**{analysis['summary']}**

### Quick Stats
- **Total Errors:** {analysis['total_errors']}
- **Timeframe:** Last {minutes} minutes

"""
        
        if analysis['total_errors'] == 0:
            report += """## ✅ No Recent Problems
No validation errors detected in the specified timeframe. The architecture generation system appears to be working well.

### Recommendations:
- System is stable for architecture creation
- Safe to proceed with complex diagrams
- Monitoring systems are active and ready
"""
            return report
        
        # Error type breakdown
        if analysis['error_types']:
            report += "## 🏷️ Error Types\n\n"
            for error_type, count in sorted(analysis['error_types'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / analysis['total_errors']) * 100
                report += f"- **{error_type}**: {count} occurrences ({percentage:.1f}%)\n"
            report += "\n"
        
        # Tools with errors
        if analysis['tools_with_errors']:
            report += "## 🔧 Tools with Errors\n\n"
            for tool_name, count in sorted(analysis['tools_with_errors'].items(), key=lambda x: x[1], reverse=True):
                report += f"- **{tool_name}**: {count} errors\n"
            report += "\n"
        
        # Critical issues
        if analysis['critical_issues']:
            report += "## 🚨 Critical Issues Requiring Immediate Action\n\n"
            for issue in analysis['critical_issues']:
                severity_icon = "🚨" if issue['severity'] == 'critical' else "⚠️"
                report += f"### {severity_icon} {issue['issue']}\n"
                report += f"**Severity:** {issue['severity'].upper()}\n"
                report += f"**Description:** {issue['description']}\n"
                report += f"**Recommendation:** {issue['recommendation']}\n\n"
        
        # Recommendations
        if analysis['recommendations']:
            report += "## 💡 Immediate Actions\n\n"
            for i, rec in enumerate(analysis['recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        report += f"\n---\n*Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return report
        
    except Exception as e:
        return f"❌ Failed to extract recent problems: {str(e)}"

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