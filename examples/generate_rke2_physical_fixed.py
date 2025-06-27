#!/usr/bin/env python3
"""
Fixed RKE2 Physical Layer Generator using core ArchiMate functions
Uses generator, _create_element_from_data, and _create_relationship_from_data directly
"""

import sys
import os
sys.path.append('src')

try:
    from archi_mcp.server import (
        generator, 
        ElementInput, 
        RelationshipInput, 
        _create_element_from_data, 
        _create_relationship_from_data
    )
    print("✅ ArchiMate core functions imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def generate_physical_layer():
    """Generate RKE2 Physical layer using correct core functions"""
    
    try:
        # Clear generator first
        generator.clear()
        print("🔄 Generator cleared")
        
        # Define physical elements (only Equipment, Facility, Distribution_Network, Material)
        elements_data = [
            # Physical Equipment - Servers
            {
                "id": "server_hardware_rack1",
                "name": "Server Hardware Rack #1",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "Physical server rack containing master and worker nodes"
            },
            {
                "id": "server_hardware_rack2",
                "name": "Server Hardware Rack #2",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "Physical server rack containing worker nodes and storage"
            },
            {
                "id": "storage_hardware",
                "name": "Storage Hardware Array",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "High-performance NVMe SSD hardware for persistent storage"
            },
            {
                "id": "backup_hardware",
                "name": "Backup Storage Hardware",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "Large capacity storage hardware for backups"
            },
            
            # Network Equipment
            {
                "id": "network_switches",
                "name": "Network Switch Hardware",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "48-port managed switches with 10Gb uplinks"
            },
            {
                "id": "firewall_appliance",
                "name": "Firewall Appliance",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "Enterprise firewall hardware for perimeter security"
            },
            {
                "id": "load_balancer_appliance",
                "name": "Load Balancer Appliance",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "Dedicated hardware load balancer"
            },
            
            # Power and Cooling Equipment
            {
                "id": "ups_system",
                "name": "Uninterruptible Power Supply",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "Redundant UPS system for power protection"
            },
            {
                "id": "cooling_system",
                "name": "Datacenter Cooling System",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "HVAC system for temperature and humidity control"
            },
            {
                "id": "power_distribution",
                "name": "Power Distribution Units (PDUs)",
                "element_type": "Equipment",
                "layer": "Physical",
                "description": "Intelligent power distribution with monitoring"
            },
            
            # Physical Distribution Networks
            {
                "id": "electrical_network",
                "name": "Electrical Power Distribution",
                "element_type": "Distribution_Network",
                "layer": "Physical",
                "description": "Electrical power distribution throughout datacenter"
            },
            {
                "id": "network_cabling",
                "name": "Network Cabling Infrastructure",
                "element_type": "Distribution_Network",
                "layer": "Physical",
                "description": "Fiber and copper network cabling system"
            },
            {
                "id": "cooling_distribution",
                "name": "Cooling Distribution System", 
                "element_type": "Distribution_Network",
                "layer": "Physical",
                "description": "Air conditioning and cooling distribution network"
            },
            
            # Physical Materials
            {
                "id": "server_components",
                "name": "Server Component Materials",
                "element_type": "Material",
                "layer": "Physical",
                "description": "CPUs, RAM, storage drives, motherboards"
            },
            {
                "id": "network_materials",
                "name": "Network Cable Materials",
                "element_type": "Material",
                "layer": "Physical",
                "description": "Fiber optic cables, copper cables, connectors"
            },
            {
                "id": "power_materials",
                "name": "Power Cable Materials",
                "element_type": "Material",
                "layer": "Physical",
                "description": "Power cables, outlets, surge protectors"
            },
            
            # Facility
            {
                "id": "datacenter_facility",
                "name": "Datalan Datacenter Facility",
                "element_type": "Facility",
                "layer": "Physical",
                "description": "Secure datacenter facility with redundant infrastructure"
            },
            {
                "id": "server_room",
                "name": "Server Room",
                "element_type": "Facility",
                "layer": "Physical",
                "description": "Climate-controlled server room with raised floors"
            },
            {
                "id": "network_room",
                "name": "Network Operations Room",
                "element_type": "Facility",
                "layer": "Physical",
                "description": "Dedicated room for network equipment and monitoring"
            }
        ]
        
        # Create and add elements
        print("🏗️ Creating physical elements...")
        for elem_data in elements_data:
            element_input = ElementInput(**elem_data)
            element = _create_element_from_data(element_input)
            generator.add_element(element)
            print(f"  ✅ Added {element.element_type}: {element.name}")
        
        # Define relationships  
        relationships_data = [
            # Equipment composition relationships
            {
                "id": "rack1_uses_server_components",
                "from_element": "server_hardware_rack1",
                "to_element": "server_components",
                "relationship_type": "Access"
            },
            {
                "id": "rack2_uses_server_components",
                "from_element": "server_hardware_rack2",
                "to_element": "server_components",
                "relationship_type": "Access"
            },
            {
                "id": "storage_uses_components",
                "from_element": "storage_hardware",
                "to_element": "server_components",
                "relationship_type": "Access"
            },
            {
                "id": "network_uses_materials",
                "from_element": "network_switches",
                "to_element": "network_materials",
                "relationship_type": "Access"
            },
            
            # Power distribution relationships
            {
                "id": "ups_distributes_power",
                "from_element": "ups_system",
                "to_element": "electrical_network",
                "relationship_type": "Serving"
            },
            {
                "id": "pdu_distributes_power",
                "from_element": "power_distribution",
                "to_element": "electrical_network",
                "relationship_type": "Serving"
            },
            {
                "id": "electrical_powers_racks",
                "from_element": "electrical_network",
                "to_element": "server_hardware_rack1",
                "relationship_type": "Serving"
            },
            {
                "id": "electrical_powers_storage",
                "from_element": "electrical_network",
                "to_element": "storage_hardware",
                "relationship_type": "Serving"
            },
            {
                "id": "electrical_powers_network",
                "from_element": "electrical_network",
                "to_element": "network_switches",
                "relationship_type": "Serving"
            },
            
            # Network cabling relationships
            {
                "id": "switches_use_cabling",
                "from_element": "network_switches",
                "to_element": "network_cabling",
                "relationship_type": "Serving"
            },
            {
                "id": "cabling_uses_materials",
                "from_element": "network_cabling",
                "to_element": "network_materials",
                "relationship_type": "Access"
            },
            
            # Cooling distribution
            {
                "id": "cooling_distributes_air",
                "from_element": "cooling_system",
                "to_element": "cooling_distribution",
                "relationship_type": "Serving"
            },
            {
                "id": "cooling_serves_server_room",
                "from_element": "cooling_distribution",
                "to_element": "server_room",
                "relationship_type": "Serving"
            },
            {
                "id": "cooling_serves_network_room",
                "from_element": "cooling_distribution",
                "to_element": "network_room",
                "relationship_type": "Serving"
            },
            
            # Facility aggregation relationships
            {
                "id": "datacenter_contains_server_room",
                "from_element": "datacenter_facility",
                "to_element": "server_room",
                "relationship_type": "Aggregation"
            },
            {
                "id": "datacenter_contains_network_room",
                "from_element": "datacenter_facility",
                "to_element": "network_room",
                "relationship_type": "Aggregation"
            },
            {
                "id": "server_room_houses_racks",
                "from_element": "server_room",
                "to_element": "server_hardware_rack1",
                "relationship_type": "Aggregation"
            },
            {
                "id": "server_room_houses_rack2",
                "from_element": "server_room",
                "to_element": "server_hardware_rack2",
                "relationship_type": "Aggregation"
            },
            {
                "id": "server_room_houses_storage",
                "from_element": "server_room",
                "to_element": "storage_hardware",
                "relationship_type": "Aggregation"
            },
            {
                "id": "network_room_houses_switches",
                "from_element": "network_room",
                "to_element": "network_switches",
                "relationship_type": "Aggregation"
            },
            {
                "id": "network_room_houses_firewall",
                "from_element": "network_room",
                "to_element": "firewall_appliance",
                "relationship_type": "Aggregation"
            },
            {
                "id": "network_room_houses_lb",
                "from_element": "network_room",
                "to_element": "load_balancer_appliance",
                "relationship_type": "Aggregation"
            },
            
            # Infrastructure support relationships
            {
                "id": "datacenter_houses_ups",
                "from_element": "datacenter_facility",
                "to_element": "ups_system",
                "relationship_type": "Aggregation"
            },
            {
                "id": "datacenter_houses_cooling",
                "from_element": "datacenter_facility",
                "to_element": "cooling_system",
                "relationship_type": "Aggregation"
            },
            {
                "id": "datacenter_houses_pdu",
                "from_element": "datacenter_facility",
                "to_element": "power_distribution",
                "relationship_type": "Aggregation"
            }
        ]
        
        # Create and add relationships
        print("🔗 Creating physical relationships...")
        for rel_data in relationships_data:
            relationship_input = RelationshipInput(**rel_data)
            relationship = _create_relationship_from_data(relationship_input)
            generator.add_relationship(relationship)
            print(f"  ✅ Added {relationship.relationship_type}: {relationship.from_element} -> {relationship.to_element}")
        
        # Generate PlantUML
        print("📊 Generating PlantUML diagram...")
        plantuml_code = generator.generate_plantuml(
            title="RKE2 Kubernetes Platform - Physical Layer",
            description="Physical infrastructure supporting the RKE2 Kubernetes platform deployment"
        )
        
        # Save PlantUML to file
        with open('rke2_physical_layer_fixed.puml', 'w') as f:
            f.write(plantuml_code)
        print("💾 Saved PlantUML to rke2_physical_layer_fixed.puml")
        
        # Get statistics
        stats = {
            "elements": generator.get_element_count(),
            "relationships": generator.get_relationship_count()
        }
        
        print(f"📈 Statistics: {stats['elements']} elements, {stats['relationships']} relationships")
        
        return plantuml_code, stats
        
    except Exception as e:
        print(f"❌ Error generating physical layer: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("🚀 Starting RKE2 Physical Layer generation with CORRECT core functions...")
    plantuml_code, stats = generate_physical_layer()
    
    if plantuml_code:
        print("\n" + "="*60)
        print("📊 GENERATED PLANTUML CODE (preview):")
        print("="*60)
        print(plantuml_code[:500] + "..." if len(plantuml_code) > 500 else plantuml_code)
        print("="*60)
        print(f"✅ Physical layer generation completed successfully!")
        print(f"📈 Final stats: {stats['elements']} elements, {stats['relationships']} relationships")
    else:
        print("❌ Physical layer generation failed")
        sys.exit(1)