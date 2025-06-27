"""Example of generating full enterprise architecture using the ArchiMate methodology."""

import asyncio
from archi_mcp.server import ArchiMCPServer


async def test_full_architecture_generation():
    """Test the complete architecture generation feature."""
    
    server = ArchiMCPServer()
    
    # Example 1: Online Banking Portal
    print("🏦 Example 1: Online Banking Portal")
    print("=" * 50)
    
    banking_args = {
        "system_description": "Online Banking Portal for retail customers with mobile app, web interface, and core banking integration",
        "business_domain": "banking",
        "architecture_scope": "system",
        "include_views": ["motivation", "layered_view", "application_structure", "implementation_roadmap"],
        "implementation_phases": 4
    }
    
    try:
        result = await server._generate_full_architecture(banking_args)
        print("✅ Banking architecture generated successfully!")
        print("Preview (first 1000 characters):")
        print("-" * 40)
        print(result.content[0].text[:1000] + "...")
        print("-" * 40)
    except Exception as e:
        print(f"❌ Error generating banking architecture: {e}")
    
    print("\n\n")
    
    # Example 2: E-commerce Platform
    print("🛒 Example 2: E-commerce Platform")
    print("=" * 50)
    
    ecommerce_args = {
        "system_description": "Multi-vendor e-commerce platform with inventory management, payment processing, and analytics",
        "business_domain": "e-commerce",
        "architecture_scope": "enterprise",
        "include_views": ["motivation", "business_model_canvas", "layered_view", "application_structure", "technology_structure", "implementation_roadmap"],
        "implementation_phases": 3
    }
    
    try:
        result = await server._generate_full_architecture(ecommerce_args)
        print("✅ E-commerce architecture generated successfully!")
        print("Preview (first 1000 characters):")
        print("-" * 40)
        print(result.content[0].text[:1000] + "...")
        print("-" * 40)
    except Exception as e:
        print(f"❌ Error generating e-commerce architecture: {e}")
    
    print("\n\n")
    
    # Example 3: Healthcare Management System
    print("🏥 Example 3: Healthcare Management System")
    print("=" * 50)
    
    healthcare_args = {
        "system_description": "Integrated healthcare management system with patient records, appointment scheduling, and billing",
        "business_domain": "healthcare",
        "architecture_scope": "system",
        "include_views": ["motivation", "value_stream", "strategy_capability", "layered_view", "interaction_view", "implementation_roadmap"],
        "implementation_phases": 5
    }
    
    try:
        result = await server._generate_full_architecture(healthcare_args)
        print("✅ Healthcare architecture generated successfully!")
        print("Preview (first 1000 characters):")
        print("-" * 40)
        print(result.content[0].text[:1000] + "...")
        print("-" * 40)
    except Exception as e:
        print(f"❌ Error generating healthcare architecture: {e}")
    
    print("\n\n")
    
    # Example 4: Custom System
    print("⚙️ Example 4: Custom IoT Platform")
    print("=" * 50)
    
    iot_args = {
        "system_description": "IoT data analytics platform for smart city infrastructure monitoring and management",
        "business_domain": "general",
        "architecture_scope": "system",
        "include_views": ["motivation", "layered_view", "application_structure", "technology_structure", "implementation_roadmap"],
        "implementation_phases": 6
    }
    
    try:
        result = await server._generate_full_architecture(iot_args)
        print("✅ IoT platform architecture generated successfully!")
        print("Preview (first 1000 characters):")
        print("-" * 40)
        print(result.content[0].text[:1000] + "...")
        print("-" * 40)
    except Exception as e:
        print(f"❌ Error generating IoT architecture: {e}")


def demonstrate_claude_usage():
    """Demonstrate how to use this feature in Claude Desktop."""
    
    print("\n\n" + "="*80)
    print("📖 CLAUDE DESKTOP USAGE GUIDE")
    print("="*80)
    
    print("""
🎯 How to Use the Full Architecture Generator in Claude Desktop:

1. **Basic Usage:**
   Generate a complete architecture for an online banking portal:
   
   "Generate a full enterprise architecture for an online banking portal"

2. **Detailed Request:**
   "Create a comprehensive ArchiMate architecture for a multi-vendor e-commerce platform 
   including motivation view, business model canvas, layered view, application structure, 
   and a 4-phase implementation roadmap"

3. **Domain-Specific Architecture:**
   "Design a complete healthcare management system architecture with patient records, 
   appointment scheduling, and billing for a hospital network"

4. **Custom Business Domain:**
   "Generate an enterprise architecture for an IoT data analytics platform for smart 
   city infrastructure monitoring, include all views with 6 implementation phases"

🔧 Available Parameters:
- **system_description**: What you want to architect (required)
- **business_domain**: banking, healthcare, e-commerce, manufacturing, general
- **architecture_scope**: enterprise, system, application, component  
- **include_views**: motivation, business_model_canvas, value_stream, strategy_capability,
                    layered_view, interaction_view, application_structure, 
                    technology_structure, implementation_roadmap
- **implementation_phases**: 1-6 phases (default: 3)

📋 What You Get:
✅ Multiple coordinated ArchiMate diagrams in PlantUML format
✅ Complete methodology following ArchiMate 3.2 specification
✅ Implementation guidance and next steps
✅ Domain-specific elements and relationships
✅ Professional architecture documentation

🚀 Examples:
- "Architecture for online banking portal with 4 implementation phases"
- "E-commerce platform architecture including business model canvas"
- "Healthcare system with motivation, layered, and interaction views"
- "Manufacturing MES system with technology structure and roadmap"
""")
    
    print("="*80)


if __name__ == "__main__":
    # Run the test examples
    asyncio.run(test_full_architecture_generation())
    
    # Show usage guide
    demonstrate_claude_usage()