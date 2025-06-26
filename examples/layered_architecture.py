"""Layered architecture example using templates."""

from archi_mcp.templates import get_viewpoint_template, get_pattern_template
from archi_mcp.archimate.generator import ArchiMateGenerator, DiagramLayout
from archi_mcp.archimate.elements.base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archi_mcp.archimate.relationships import create_relationship


def create_layered_architecture_from_template():
    """Create a layered architecture using the layered viewpoint template."""
    
    # Get the layered viewpoint template
    template = get_viewpoint_template("layered")
    
    if not template:
        raise ValueError("Layered viewpoint template not found")
    
    # Create generator
    generator = ArchiMateGenerator()
    
    # Set layout to group by layer
    layout = DiagramLayout(
        direction="vertical",
        group_by_layer=True,
        show_legend=True,
        show_title=True
    )
    generator.set_layout(layout)
    
    # Helper function to create element from template data
    def create_element_from_template_data(elem_data):
        # Map layer string to enum
        layer_map = {
            "Business": ArchiMateLayer.BUSINESS,
            "Application": ArchiMateLayer.APPLICATION,
            "Technology": ArchiMateLayer.TECHNOLOGY,
            "Physical": ArchiMateLayer.PHYSICAL,
            "Motivation": ArchiMateLayer.MOTIVATION,
            "Strategy": ArchiMateLayer.STRATEGY,
            "Implementation": ArchiMateLayer.IMPLEMENTATION
        }
        
        # Determine aspect from element type
        def get_aspect(element_type):
            active_structure = [
                "Business_Actor", "Business_Role", "Application_Component",
                "Node", "Device", "System_Software", "Equipment", "Stakeholder"
            ]
            passive_structure = [
                "Business_Object", "Data_Object", "Artifact", "Material",
                "Meaning", "Value", "Deliverable"
            ]
            
            if any(elem_type in element_type for elem_type in active_structure):
                return ArchiMateAspect.ACTIVE_STRUCTURE
            elif any(elem_type in element_type for elem_type in passive_structure):
                return ArchiMateAspect.PASSIVE_STRUCTURE
            else:
                return ArchiMateAspect.BEHAVIOR
        
        return ArchiMateElement(
            id=elem_data["id"],
            name=elem_data["name"],
            element_type=elem_data["element_type"],
            layer=layer_map[elem_data["layer"]],
            aspect=get_aspect(elem_data["element_type"]),
            description=elem_data.get("description")
        )
    
    # Add elements from template
    for elem_data in template.elements:
        element = create_element_from_template_data(elem_data)
        generator.add_element(element)
    
    # Add relationships from template
    for rel_data in template.relationships:
        relationship = create_relationship(
            relationship_id=rel_data["id"],
            from_element=rel_data["from_element"],
            to_element=rel_data["to_element"],
            relationship_type=rel_data["relationship_type"],
            direction=rel_data.get("direction"),
            description=rel_data.get("description")
        )
        generator.add_relationship(relationship)
    
    return generator, template


def create_enhanced_layered_architecture():
    """Create an enhanced layered architecture with additional elements."""
    
    generator, template = create_layered_architecture_from_template()
    
    # Add additional elements to enhance the architecture
    from archi_mcp.archimate.elements import BusinessElement, ApplicationElement, TechnologyElement
    
    # Additional business elements
    customer = BusinessElement.create_business_actor(
        id="customer",
        name="Customer",
        description="End user of the system"
    )
    
    order_process = BusinessElement.create_business_process(
        id="order_process", 
        name="Order Process",
        description="End-to-end order processing"
    )
    
    # Additional application elements
    api_gateway = ApplicationElement.create_application_component(
        id="api_gateway",
        name="API Gateway",
        description="Single entry point for API requests"
    )
    
    user_interface = ApplicationElement.create_application_interface(
        id="user_interface",
        name="User Interface",
        description="Customer-facing interface"
    )
    
    # Additional technology elements
    load_balancer = TechnologyElement.create_device(
        id="load_balancer",
        name="Load Balancer", 
        description="Traffic distribution device"
    )
    
    container_platform = TechnologyElement.create_system_software(
        id="container_platform",
        name="Container Platform",
        description="Container orchestration platform"
    )
    
    # Add new elements
    generator.add_element(customer)
    generator.add_element(order_process)
    generator.add_element(api_gateway)
    generator.add_element(user_interface)
    generator.add_element(load_balancer)
    generator.add_element(container_platform)
    
    # Add relationships for new elements
    customer_uses_interface = create_relationship(
        "customer_uses_ui", "customer", "user_interface", "Serving"
    )
    
    interface_uses_gateway = create_relationship(
        "ui_uses_gateway", "user_interface", "api_gateway", "Flow"
    )
    
    customer_initiates_process = create_relationship(
        "customer_initiates", "customer", "order_process", "Triggering"
    )
    
    balancer_distributes = create_relationship(
        "balancer_distributes", "load_balancer", "api_gateway", "Serving"
    )
    
    container_hosts_gateway = create_relationship(
        "container_hosts_gateway", "container_platform", "api_gateway", "Assignment"
    )
    
    generator.add_relationship(customer_uses_interface)
    generator.add_relationship(interface_uses_gateway)
    generator.add_relationship(customer_initiates_process)
    generator.add_relationship(balancer_distributes)
    generator.add_relationship(container_hosts_gateway)
    
    return generator


def main():
    """Generate and display layered architecture examples."""
    
    print("ArchiMate Layered Architecture Examples")
    print("=" * 50)
    
    # Example 1: Basic layered viewpoint from template
    print("\n1. Basic Layered Viewpoint (from template)")
    print("-" * 40)
    
    try:
        generator, template = create_layered_architecture_from_template()
        
        plantuml_code = generator.generate_plantuml(
            title=template.name,
            description=template.description
        )
        
        print(f"Template: {template.name}")
        print(f"Description: {template.description}")
        print(f"Elements: {generator.get_element_count()}")
        print(f"Relationships: {generator.get_relationship_count()}")
        print(f"Layers: {', '.join(generator.get_layers_used())}")
        
        print(f"\nPlantUML Code:")
        print(plantuml_code[:500] + "..." if len(plantuml_code) > 500 else plantuml_code)
        
    except Exception as e:
        print(f"Error creating basic layered architecture: {e}")
    
    # Example 2: Enhanced layered architecture
    print("\n\n2. Enhanced Layered Architecture")
    print("-" * 40)
    
    try:
        enhanced_generator = create_enhanced_layered_architecture()
        
        enhanced_plantuml = enhanced_generator.generate_plantuml(
            title="Enhanced Layered Architecture",
            description="Extended layered architecture with additional elements and relationships"
        )
        
        print(f"Elements: {enhanced_generator.get_element_count()}")
        print(f"Relationships: {enhanced_generator.get_relationship_count()}")
        print(f"Layers: {', '.join(enhanced_generator.get_layers_used())}")
        
        # Validate the enhanced model
        errors = enhanced_generator.validate_diagram()
        if errors:
            print(f"\nValidation errors:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"- {error}")
            if len(errors) > 5:
                print(f"... and {len(errors) - 5} more errors")
        else:
            print(f"\n✅ Enhanced model validation passed!")
        
        print(f"\nEnhanced PlantUML Code:")
        print(enhanced_plantuml[:500] + "..." if len(enhanced_plantuml) > 500 else enhanced_plantuml)
        
    except Exception as e:
        print(f"Error creating enhanced layered architecture: {e}")
    
    # Example 3: Using pattern template
    print("\n\n3. Three-Tier Pattern (from template)")
    print("-" * 40)
    
    try:
        three_tier_template = get_pattern_template("three_tier")
        
        if three_tier_template:
            print(f"Pattern: {three_tier_template.name}")
            print(f"Description: {three_tier_template.description}")
            print(f"Pattern Type: {three_tier_template.pattern_type}")
            print(f"Elements in template: {len(three_tier_template.elements)}")
            print(f"Relationships in template: {len(three_tier_template.relationships)}")
        else:
            print("Three-tier pattern template not found")
            
    except Exception as e:
        print(f"Error accessing three-tier pattern: {e}")


if __name__ == "__main__":
    main()