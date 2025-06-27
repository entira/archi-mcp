#!/usr/bin/env python3
"""
Correct RKE2 Motivation Layer Generator using core ArchiMate functions
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

def generate_motivation_layer():
    """Generate RKE2 Motivation layer using correct core functions"""
    
    try:
        # Clear generator first
        generator.clear()
        print("🔄 Generator cleared")
        
        # Define motivation elements
        elements_data = [
            # Stakeholders
            {
                "id": "datalan_management",
                "name": "Datalan Management", 
                "element_type": "Stakeholder",
                "layer": "Motivation",
                "description": "Business sponsor seeking cost reduction and deployment acceleration"
            },
            {
                "id": "devops_team",
                "name": "DevOps Team (Martin Dulović)",
                "element_type": "Stakeholder",
                "layer": "Motivation", 
                "description": "Technical architect and primary implementer"
            },
            {
                "id": "it_operations",
                "name": "IT Operations Team",
                "element_type": "Stakeholder",
                "layer": "Motivation",
                "description": "Platform operators responsible for maintenance"
            },
            {
                "id": "dev_teams", 
                "name": "Development Teams",
                "element_type": "Stakeholder",
                "layer": "Motivation",
                "description": "Platform consumers deploying applications"
            },
            
            # Drivers
            {
                "id": "manual_processes",
                "name": "Manual Deployment Processes", 
                "element_type": "Driver",
                "layer": "Motivation",
                "description": "Legacy manual procedures creating bottlenecks"
            },
            {
                "id": "high_costs",
                "name": "High Operational Costs",
                "element_type": "Driver", 
                "layer": "Motivation",
                "description": "Resource-intensive operations requiring automation"
            },
            {
                "id": "security_gaps",
                "name": "Security Vulnerabilities",
                "element_type": "Driver",
                "layer": "Motivation",
                "description": "Critical security gaps requiring hardening (3/10 rating)"
            },
            {
                "id": "scalability_needs",
                "name": "Scalability Requirements",
                "element_type": "Driver",
                "layer": "Motivation", 
                "description": "Business growth demanding elastic infrastructure"
            },
            
            # Goals
            {
                "id": "automated_deployment",
                "name": "Automated Kubernetes Deployment",
                "element_type": "Goal",
                "layer": "Motivation",
                "description": "Eliminate manual intervention through IaC"
            },
            {
                "id": "cost_reduction", 
                "name": "Reduced Operational Costs",
                "element_type": "Goal",
                "layer": "Motivation",
                "description": "Achieve 40-60% operational cost reduction"
            },
            {
                "id": "faster_deployment",
                "name": "Faster Application Deployment",
                "element_type": "Goal",
                "layer": "Motivation",
                "description": "Reduce deployment time from days to minutes"
            },
            {
                "id": "enhanced_security",
                "name": "Enhanced Security Posture", 
                "element_type": "Goal",
                "layer": "Motivation",
                "description": "Enterprise-grade security controls and compliance"
            },
            {
                "id": "standardization",
                "name": "Standardized Deployments",
                "element_type": "Goal",
                "layer": "Motivation",
                "description": "Consistent, repeatable deployment processes"
            },
            
            # Requirements
            {
                "id": "production_grade",
                "name": "Production-Grade Platform",
                "element_type": "Requirement",
                "layer": "Motivation",
                "description": "Enterprise SLA with 99.9% uptime target"
            },
            {
                "id": "high_availability", 
                "name": "High Availability Architecture",
                "element_type": "Requirement",
                "layer": "Motivation",
                "description": "No single points of failure with auto-failover"
            },
            {
                "id": "security_hardening",
                "name": "Automated Security Hardening", 
                "element_type": "Requirement",
                "layer": "Motivation",
                "description": "CIS compliance with AppArmor and RBAC"
            },
            {
                "id": "monitoring_req",
                "name": "Real-Time Monitoring",
                "element_type": "Requirement",
                "layer": "Motivation",
                "description": "Comprehensive observability with Prometheus/Grafana"
            }
        ]
        
        # Create and add elements
        print("📦 Creating motivation elements...")
        for elem_data in elements_data:
            element_input = ElementInput(**elem_data)
            element = _create_element_from_data(element_input)
            generator.add_element(element)
            print(f"  ✅ Added {element.element_type}: {element.name}")
        
        # Define relationships
        relationships_data = [
            # Stakeholder concerns
            {
                "id": "mgmt_concerns_costs",
                "from_element": "datalan_management", 
                "to_element": "high_costs",
                "relationship_type": "Association"
            },
            {
                "id": "devops_addresses_manual",
                "from_element": "devops_team",
                "to_element": "manual_processes", 
                "relationship_type": "Association"
            },
            {
                "id": "ops_security_concern",
                "from_element": "it_operations",
                "to_element": "security_gaps",
                "relationship_type": "Association"
            },
            
            # Driver influences  
            {
                "id": "manual_drives_automation",
                "from_element": "manual_processes",
                "to_element": "automated_deployment",
                "relationship_type": "Influence"
            },
            {
                "id": "costs_drive_reduction", 
                "from_element": "high_costs",
                "to_element": "cost_reduction",
                "relationship_type": "Influence"
            },
            {
                "id": "security_drives_hardening",
                "from_element": "security_gaps",
                "to_element": "enhanced_security",
                "relationship_type": "Influence"
            },
            {
                "id": "scalability_drives_standardization",
                "from_element": "scalability_needs", 
                "to_element": "standardization",
                "relationship_type": "Influence"
            },
            
            # Goal realizations
            {
                "id": "automation_realizes_production",
                "from_element": "automated_deployment",
                "to_element": "production_grade",
                "relationship_type": "Realization"
            },
            {
                "id": "cost_goal_realizes_efficiency",
                "from_element": "cost_reduction",
                "to_element": "high_availability",
                "relationship_type": "Realization"
            },
            {
                "id": "security_goal_realizes_hardening", 
                "from_element": "enhanced_security",
                "to_element": "security_hardening",
                "relationship_type": "Realization"
            },
            {
                "id": "faster_deployment_realizes_monitoring",
                "from_element": "faster_deployment",
                "to_element": "monitoring_req",
                "relationship_type": "Realization"
            }
        ]
        
        # Create and add relationships
        print("🔗 Creating motivation relationships...")
        for rel_data in relationships_data:
            relationship_input = RelationshipInput(**rel_data)
            relationship = _create_relationship_from_data(relationship_input)
            generator.add_relationship(relationship)
            print(f"  ✅ Added {relationship.relationship_type}: {relationship.from_element} -> {relationship.to_element}")
        
        # Generate PlantUML
        print("📊 Generating PlantUML diagram...")
        plantuml_code = generator.generate_plantuml(
            title="RKE2 Kubernetes Platform - Motivation Layer",
            description="Strategic drivers and business context for RKE2 platform implementation"
        )
        
        # Save PlantUML to file
        with open('rke2_motivation_layer_fixed.puml', 'w') as f:
            f.write(plantuml_code)
        print("💾 Saved PlantUML to rke2_motivation_layer_fixed.puml")
        
        # Get statistics
        stats = {
            "elements": generator.get_element_count(),
            "relationships": generator.get_relationship_count()
        }
        
        print(f"📈 Statistics: {stats['elements']} elements, {stats['relationships']} relationships")
        
        return plantuml_code, stats
        
    except Exception as e:
        print(f"❌ Error generating motivation layer: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("🚀 Starting RKE2 Motivation Layer generation with CORRECT core functions...")
    plantuml_code, stats = generate_motivation_layer()
    
    if plantuml_code:
        print("\n" + "="*60)
        print("📊 GENERATED PLANTUML CODE:")
        print("="*60)
        print(plantuml_code[:500] + "..." if len(plantuml_code) > 500 else plantuml_code)
        print("="*60)
        print(f"✅ Motivation layer generation completed successfully!")
        print(f"📈 Final stats: {stats['elements']} elements, {stats['relationships']} relationships")
    else:
        print("❌ Motivation layer generation failed")
        sys.exit(1)