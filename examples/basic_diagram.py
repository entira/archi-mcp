"""Basic ArchiMate diagram example."""

from archi_mcp.archimate.elements import BusinessElement, ApplicationElement, TechnologyElement
from archi_mcp.archimate.relationships import create_relationship
from archi_mcp.archimate.generator import ArchiMateGenerator, DiagramLayout


def create_basic_three_tier_architecture():
    """Create a basic three-tier architecture diagram."""
    
    # Create elements
    business_service = BusinessElement.create_business_service(
        id="customer_service",
        name="Customer Service",
        description="Core customer service functionality"
    )
    
    app_component = ApplicationElement.create_application_component(
        id="web_app",
        name="Web Application",
        description="Customer-facing web application"
    )
    
    data_object = ApplicationElement.create_data_object(
        id="customer_db",
        name="Customer Database",
        description="Customer data storage"
    )
    
    tech_node = TechnologyElement.create_node(
        id="app_server",
        name="Application Server",
        description="Web application hosting server"
    )
    
    db_node = TechnologyElement.create_node(
        id="db_server", 
        name="Database Server",
        description="Database hosting server"
    )
    
    # Create relationships
    app_realizes_service = create_relationship(
        relationship_id="app_realizes_service",
        from_element="web_app",
        to_element="customer_service",
        relationship_type="Realization",
        description="Web app realizes customer service"
    )
    
    app_accesses_data = create_relationship(
        relationship_id="app_accesses_data",
        from_element="web_app",
        to_element="customer_db",
        relationship_type="Access",
        description="Web app accesses customer data"
    )
    
    server_hosts_app = create_relationship(
        relationship_id="server_hosts_app",
        from_element="app_server",
        to_element="web_app",
        relationship_type="Assignment",
        description="Server hosts web application"
    )
    
    db_server_hosts_data = create_relationship(
        relationship_id="db_server_hosts_data",
        from_element="db_server",
        to_element="customer_db",
        relationship_type="Assignment",
        description="Database server hosts data"
    )
    
    # Create generator and add elements
    generator = ArchiMateGenerator()
    
    # Set layout for better visualization
    layout = DiagramLayout(
        direction="vertical",
        group_by_layer=True,
        show_legend=True,
        spacing="wide"
    )
    generator.set_layout(layout)
    
    # Add elements
    generator.add_element(business_service)
    generator.add_element(app_component)
    generator.add_element(data_object)
    generator.add_element(tech_node)
    generator.add_element(db_node)
    
    # Add relationships
    generator.add_relationship(app_realizes_service)
    generator.add_relationship(app_accesses_data)
    generator.add_relationship(server_hosts_app)
    generator.add_relationship(db_server_hosts_data)
    
    return generator


def main():
    """Generate and display the basic diagram."""
    generator = create_basic_three_tier_architecture()
    
    # Generate PlantUML code
    plantuml_code = generator.generate_plantuml(
        title="Basic Three-Tier Architecture",
        description="A simple three-tier architecture showing business, application, and technology layers"
    )
    
    print("Generated PlantUML ArchiMate Diagram:")
    print("=" * 50)
    print(plantuml_code)
    print("=" * 50)
    
    # Display statistics
    print(f"\nDiagram Statistics:")
    print(f"Elements: {generator.get_element_count()}")
    print(f"Relationships: {generator.get_relationship_count()}")
    print(f"Layers used: {', '.join(generator.get_layers_used())}")
    
    # Validate the model
    errors = generator.validate_diagram()
    if errors:
        print(f"\nValidation errors found:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"\n✅ Model validation passed!")


if __name__ == "__main__":
    main()