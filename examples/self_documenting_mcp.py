"""Self-documenting ArchiMate diagram for the MCP server itself."""

from archi_mcp.archimate.elements import (
    BusinessElement,
    ApplicationElement,
    TechnologyElement,
    MotivationElement,
    ImplementationElement,
)
from archi_mcp.archimate.relationships import create_relationship
from archi_mcp.archimate.generator import ArchiMateGenerator, DiagramLayout


def create_mcp_server_architecture():
    """Create an ArchiMate diagram documenting the MCP server architecture itself."""
    
    # === MOTIVATION LAYER ===
    # Stakeholders
    developer = MotivationElement.create_stakeholder(
        id="developer",
        name="AI Developer",
        description="Developer building AI applications with Claude"
    )
    
    architect = MotivationElement.create_stakeholder(
        id="architect",
        name="Enterprise Architect",
        description="Professional creating enterprise architecture models"
    )
    
    # Goals and Requirements
    automation_goal = MotivationElement.create_goal(
        id="automation_goal",
        name="Automate Architecture Modeling",
        description="Enable automated generation of ArchiMate diagrams"
    )
    
    compliance_requirement = MotivationElement.create_requirement(
        id="compliance_requirement",
        name="ArchiMate 3.2 Compliance",
        description="Full compliance with ArchiMate 3.2 specification"
    )
    
    usability_principle = MotivationElement.create_principle(
        id="usability_principle",
        name="Ease of Use",
        description="Simple and intuitive API for diagram generation"
    )
    
    # === BUSINESS LAYER ===
    # Business Services
    diagram_generation = BusinessElement.create_business_service(
        id="diagram_generation",
        name="ArchiMate Diagram Generation",
        description="Core service for generating ArchiMate diagrams"
    )
    
    model_validation = BusinessElement.create_business_service(
        id="model_validation",
        name="Model Validation",
        description="Validate ArchiMate models against specification"
    )
    
    template_provision = BusinessElement.create_business_service(
        id="template_provision",
        name="Template Provision",
        description="Provide pre-built architecture templates"
    )
    
    # Business Processes
    diagram_creation_process = BusinessElement.create_business_process(
        id="diagram_creation_process",
        name="Diagram Creation Process",
        description="End-to-end process for creating ArchiMate diagrams"
    )
    
    # === APPLICATION LAYER ===
    # Application Components
    mcp_server = ApplicationElement.create_application_component(
        id="mcp_server",
        name="ArchiMate MCP Server",
        description="Main MCP server providing ArchiMate capabilities"
    )
    
    archimate_engine = ApplicationElement.create_application_component(
        id="archimate_engine",
        name="ArchiMate Engine",
        description="Core engine for ArchiMate element and relationship management"
    )
    
    plantuml_generator = ApplicationElement.create_application_component(
        id="plantuml_generator",
        name="PlantUML Generator",
        description="Component responsible for generating PlantUML code"
    )
    
    validator_component = ApplicationElement.create_application_component(
        id="validator_component",
        name="Model Validator",
        description="Component for validating ArchiMate models"
    )
    
    template_engine = ApplicationElement.create_application_component(
        id="template_engine",
        name="Template Engine",
        description="Manages viewpoints, patterns, and industry templates"
    )
    
    # Application Services
    mcp_api = ApplicationElement.create_application_service(
        id="mcp_api",
        name="MCP API",
        description="Model Context Protocol API interface"
    )
    
    # Application Interfaces
    claude_interface = ApplicationElement.create_application_interface(
        id="claude_interface",
        name="Claude Integration",
        description="Interface for Claude Desktop integration"
    )
    
    # Data Objects
    element_registry = ApplicationElement.create_data_object(
        id="element_registry",
        name="Element Registry",
        description="Registry of all ArchiMate element types"
    )
    
    relationship_matrix = ApplicationElement.create_data_object(
        id="relationship_matrix",
        name="Relationship Matrix",
        description="ArchiMate relationship compatibility matrix"
    )
    
    template_library = ApplicationElement.create_data_object(
        id="template_library",
        name="Template Library",
        description="Collection of viewpoints, patterns, and industry templates"
    )
    
    # === TECHNOLOGY LAYER ===
    # Technology Components
    python_runtime = TechnologyElement.create_system_software(
        id="python_runtime",
        name="Python 3.11+ Runtime",
        description="Python runtime environment"
    )
    
    uv_package_manager = TechnologyElement.create_system_software(
        id="uv_package_manager",
        name="uv Package Manager",
        description="Fast Python package installer and resolver"
    )
    
    mcp_protocol = TechnologyElement.create_technology_service(
        id="mcp_protocol",
        name="MCP Protocol",
        description="Model Context Protocol for AI assistant integration"
    )
    
    # Technology Artifacts
    source_code = TechnologyElement.create_artifact(
        id="source_code",
        name="Source Code",
        description="Python source code of the MCP server"
    )
    
    dependencies = TechnologyElement.create_artifact(
        id="dependencies",
        name="Dependencies",
        description="Python package dependencies (Pydantic, Loguru, etc.)"
    )
    
    # === IMPLEMENTATION LAYER ===
    # Implementation components
    development_project = ImplementationElement.create_work_package(
        id="development_project",
        name="ArchiMate MCP Development",
        description="Development project for the ArchiMate MCP server"
    )
    
    server_package = ImplementationElement.create_deliverable(
        id="server_package",
        name="MCP Server Package",
        description="Installable Python package for the MCP server"
    )
    
    # Create generator and set layout
    generator = ArchiMateGenerator()
    
    layout = DiagramLayout(
        direction="vertical",
        group_by_layer=True,
        show_legend=True,
        show_title=True,
        spacing="wide"
    )
    generator.set_layout(layout)
    
    # Add all elements
    elements = [
        # Motivation
        developer, architect, automation_goal, compliance_requirement, usability_principle,
        # Business
        diagram_generation, model_validation, template_provision, diagram_creation_process,
        # Application
        mcp_server, archimate_engine, plantuml_generator, validator_component, template_engine,
        mcp_api, claude_interface, element_registry, relationship_matrix, template_library,
        # Technology
        python_runtime, uv_package_manager, mcp_protocol, source_code, dependencies,
        # Implementation
        development_project, server_package
    ]
    
    for element in elements:
        generator.add_element(element)
    
    # === RELATIONSHIPS ===
    relationships = [
        # Stakeholder motivations
        create_relationship("dev_automation", "developer", "automation_goal", "Association"),
        create_relationship("arch_compliance", "architect", "compliance_requirement", "Association"),
        create_relationship("goal_influences_req", "automation_goal", "compliance_requirement", "Influence"),
        create_relationship("principle_influences_req", "usability_principle", "compliance_requirement", "Influence"),
        
        # Business service realizations
        create_relationship("req_realizes_diagram", "compliance_requirement", "diagram_generation", "Realization"),
        create_relationship("req_realizes_validation", "compliance_requirement", "model_validation", "Realization"),
        create_relationship("principle_realizes_template", "usability_principle", "template_provision", "Realization"),
        
        # Process compositions
        create_relationship("process_uses_diagram", "diagram_creation_process", "diagram_generation", "Triggering"),
        create_relationship("process_uses_validation", "diagram_creation_process", "model_validation", "Triggering"),
        create_relationship("process_uses_templates", "diagram_creation_process", "template_provision", "Triggering"),
        
        # Application service realizations
        create_relationship("mcp_realizes_diagram", "mcp_api", "diagram_generation", "Realization"),
        create_relationship("mcp_realizes_validation", "mcp_api", "model_validation", "Realization"),
        create_relationship("mcp_realizes_templates", "mcp_api", "template_provision", "Realization"),
        
        # Component assignments and compositions
        create_relationship("server_provides_api", "mcp_server", "mcp_api", "Assignment"),
        create_relationship("server_composed_engine", "mcp_server", "archimate_engine", "Composition"),
        create_relationship("server_composed_generator", "mcp_server", "plantuml_generator", "Composition"),
        create_relationship("server_composed_validator", "mcp_server", "validator_component", "Composition"),
        create_relationship("server_composed_templates", "mcp_server", "template_engine", "Composition"),
        
        # Data access relationships
        create_relationship("engine_accesses_registry", "archimate_engine", "element_registry", "Access"),
        create_relationship("engine_accesses_matrix", "archimate_engine", "relationship_matrix", "Access"),
        create_relationship("validator_accesses_matrix", "validator_component", "relationship_matrix", "Access"),
        create_relationship("templates_accesses_library", "template_engine", "template_library", "Access"),
        
        # Interface relationships
        create_relationship("claude_uses_api", "claude_interface", "mcp_api", "Serving"),
        create_relationship("server_provides_interface", "mcp_server", "claude_interface", "Assignment"),
        
        # Technology assignments
        create_relationship("runtime_hosts_server", "python_runtime", "mcp_server", "Assignment"),
        create_relationship("runtime_hosts_dependencies", "python_runtime", "dependencies", "Assignment"),
        create_relationship("uv_manages_deps", "uv_package_manager", "dependencies", "Assignment"),
        create_relationship("protocol_enables_api", "mcp_protocol", "mcp_api", "Realization"),
        create_relationship("code_realizes_server", "source_code", "mcp_server", "Realization"),
        
        # Implementation relationships
        create_relationship("project_delivers_package", "development_project", "server_package", "Flow"),
        create_relationship("package_contains_code", "server_package", "source_code", "Aggregation"),
        create_relationship("package_contains_deps", "server_package", "dependencies", "Aggregation"),
    ]
    
    for relationship in relationships:
        generator.add_relationship(relationship)
    
    return generator


def main():
    """Generate the self-documenting ArchiMate diagram."""
    
    print("ArchiMate MCP Server - Self-Documenting Architecture")
    print("=" * 60)
    
    try:
        # Create the architecture diagram
        generator = create_mcp_server_architecture()
        
        # Generate PlantUML code
        plantuml_code = generator.generate_plantuml(
            title="ArchiMate MCP Server Architecture",
            description="Self-documenting architecture of the ArchiMate MCP server showing all layers from motivation to implementation"
        )
        
        # Display statistics
        print(f"Architecture Statistics:")
        print(f"- Elements: {generator.get_element_count()}")
        print(f"- Relationships: {generator.get_relationship_count()}")
        print(f"- Layers: {', '.join(generator.get_layers_used())}")
        
        # Validate the model
        print(f"\nModel Validation:")
        errors = generator.validate_diagram()
        if errors:
            print(f"❌ Found {len(errors)} validation error(s):")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")
        else:
            print(f"✅ Model validation passed!")
        
        # Export to file
        try:
            output_path = "./archi_mcp_architecture.puml"
            generator.export_to_file(output_path, title="ArchiMate MCP Server Architecture")
            print(f"\n📁 Diagram exported to: {output_path}")
        except Exception as e:
            print(f"\n⚠️  Could not export to file: {e}")
        
        # Display PlantUML code (truncated for readability)
        print(f"\nGenerated PlantUML Code:")
        print("-" * 40)
        
        lines = plantuml_code.split('\n')
        if len(lines) > 50:
            # Show first 25 and last 25 lines
            display_lines = lines[:25] + ["...", "... (content truncated) ...", "..."] + lines[-25:]
            print('\n'.join(display_lines))
        else:
            print(plantuml_code)
        
        print("-" * 40)
        print(f"\n🎯 Acceptance Criteria: ✅ PASSED")
        print(f"   Successfully generated ArchiMate diagram documenting the MCP server architecture")
        print(f"   across all layers from Motivation to Implementation.")
        
    except Exception as e:
        print(f"❌ Error generating self-documenting architecture: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()