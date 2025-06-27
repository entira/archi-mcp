#!/usr/bin/env python3
"""
Fixed RKE2 Implementation Layer Generator using core ArchiMate functions
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

def generate_implementation_layer():
    """Generate RKE2 Implementation layer using correct core functions"""
    
    try:
        # Clear generator first
        generator.clear()
        print("🔄 Generator cleared")
        
        # Define implementation elements
        elements_data = [
            # Work Packages for Infrastructure Setup
            {
                "id": "infrastructure_setup",
                "name": "Infrastructure Setup Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Complete datacenter infrastructure preparation and hardware setup"
            },
            {
                "id": "network_configuration",
                "name": "Network Configuration Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Network infrastructure setup including VLANs, security, and load balancing"
            },
            {
                "id": "os_installation",
                "name": "Operating System Installation Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Ubuntu 24.04 LTS installation and hardening on all nodes"
            },
            
            # RKE2 Platform Implementation
            {
                "id": "rke2_cluster_deployment",
                "name": "RKE2 Cluster Deployment Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "RKE2 Kubernetes cluster installation and configuration"
            },
            {
                "id": "storage_implementation",
                "name": "Storage System Implementation Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Longhorn storage and MinIO object storage deployment"
            },
            {
                "id": "monitoring_setup",
                "name": "Monitoring Stack Setup Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Prometheus, Grafana, and AlertManager deployment and configuration"
            },
            
            # Security Implementation
            {
                "id": "security_hardening",
                "name": "Security Hardening Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Kyverno policies, cert-manager, and security scanning implementation"
            },
            {
                "id": "registry_deployment",
                "name": "Container Registry Deployment Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Harbor container registry setup with vulnerability scanning"
            },
            
            # Testing and Validation
            {
                "id": "system_testing",
                "name": "System Testing Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Comprehensive testing of all platform components and integrations"
            },
            {
                "id": "performance_testing",
                "name": "Performance Testing Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Load testing and performance validation of the platform"
            },
            
            # Documentation and Training
            {
                "id": "documentation_creation",
                "name": "Documentation Creation Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Creation of operational procedures and user documentation"
            },
            {
                "id": "team_training",
                "name": "Team Training Work Package",
                "element_type": "Work_Package",
                "layer": "Implementation",
                "description": "Training for DevOps and development teams on platform usage"
            },
            
            # Key Deliverables
            {
                "id": "production_cluster",
                "name": "Production-Ready RKE2 Cluster",
                "element_type": "Deliverable",
                "layer": "Implementation",
                "description": "Fully configured and hardened Kubernetes cluster ready for production workloads"
            },
            {
                "id": "monitoring_dashboard",
                "name": "Comprehensive Monitoring Dashboard",
                "element_type": "Deliverable",
                "layer": "Implementation",
                "description": "Grafana dashboards with complete platform visibility and alerting"
            },
            {
                "id": "security_policies",
                "name": "Security Policy Set",
                "element_type": "Deliverable",
                "layer": "Implementation",
                "description": "Complete set of Kyverno security policies and governance rules"
            },
            {
                "id": "backup_solution",
                "name": "Automated Backup Solution",
                "element_type": "Deliverable",
                "layer": "Implementation",
                "description": "Velero-based backup and disaster recovery solution"
            },
            {
                "id": "container_registry",
                "name": "Enterprise Container Registry",
                "element_type": "Deliverable",
                "layer": "Implementation",
                "description": "Harbor registry with vulnerability scanning and RBAC"
            },
            {
                "id": "operational_procedures",
                "name": "Operational Procedures Documentation",
                "element_type": "Deliverable",
                "layer": "Implementation",
                "description": "Complete documentation for platform operations and maintenance"
            },
            {
                "id": "training_materials",
                "name": "Training Materials and Guides",
                "element_type": "Deliverable",
                "layer": "Implementation",
                "description": "Comprehensive training materials for platform users and administrators"
            },
            
            # Implementation Events/Milestones
            {
                "id": "infrastructure_ready",
                "name": "Infrastructure Ready Milestone",
                "element_type": "Implementation_Event",
                "layer": "Implementation",
                "description": "All physical infrastructure and networking is operational"
            },
            {
                "id": "cluster_operational",
                "name": "Cluster Operational Milestone",
                "element_type": "Implementation_Event",
                "layer": "Implementation",
                "description": "RKE2 cluster is running and ready for application deployment"
            },
            {
                "id": "security_validated",
                "name": "Security Validation Complete",
                "element_type": "Implementation_Event",
                "layer": "Implementation",
                "description": "All security measures tested and validated"
            },
            {
                "id": "production_cutover",
                "name": "Production Cutover Event",
                "element_type": "Implementation_Event",
                "layer": "Implementation",
                "description": "Platform officially moved to production status"
            },
            
            # Implementation Plateaus
            {
                "id": "basic_platform",
                "name": "Basic Platform Plateau",
                "element_type": "Plateau",
                "layer": "Implementation",
                "description": "Core Kubernetes platform with basic services operational"
            },
            {
                "id": "enhanced_platform",
                "name": "Enhanced Platform Plateau",
                "element_type": "Plateau",
                "layer": "Implementation",
                "description": "Platform with monitoring, security, and storage fully implemented"
            },
            {
                "id": "production_platform",
                "name": "Production Platform Plateau",
                "element_type": "Plateau",
                "layer": "Implementation",
                "description": "Complete production-ready platform with all features"
            }
        ]
        
        # Create and add elements
        print("🚧 Creating implementation elements...")
        for elem_data in elements_data:
            element_input = ElementInput(**elem_data)
            element = _create_element_from_data(element_input)
            generator.add_element(element)
            print(f"  ✅ Added {element.element_type}: {element.name}")
        
        # Define relationships  
        relationships_data = [
            # Work package dependencies
            {
                "id": "infra_precedes_network",
                "from_element": "infrastructure_setup",
                "to_element": "network_configuration",
                "relationship_type": "Triggering"
            },
            {
                "id": "network_precedes_os",
                "from_element": "network_configuration",
                "to_element": "os_installation",
                "relationship_type": "Triggering"
            },
            {
                "id": "os_precedes_rke2",
                "from_element": "os_installation",
                "to_element": "rke2_cluster_deployment",
                "relationship_type": "Triggering"
            },
            {
                "id": "rke2_enables_storage",
                "from_element": "rke2_cluster_deployment",
                "to_element": "storage_implementation",
                "relationship_type": "Triggering"
            },
            {
                "id": "rke2_enables_monitoring",
                "from_element": "rke2_cluster_deployment",
                "to_element": "monitoring_setup",
                "relationship_type": "Triggering"
            },
            {
                "id": "rke2_enables_security",
                "from_element": "rke2_cluster_deployment",
                "to_element": "security_hardening",
                "relationship_type": "Triggering"
            },
            {
                "id": "rke2_enables_registry",
                "from_element": "rke2_cluster_deployment",
                "to_element": "registry_deployment",
                "relationship_type": "Triggering"
            },
            
            # Testing dependencies
            {
                "id": "storage_enables_testing",
                "from_element": "storage_implementation",
                "to_element": "system_testing",
                "relationship_type": "Triggering"
            },
            {
                "id": "monitoring_enables_testing",
                "from_element": "monitoring_setup",
                "to_element": "system_testing",
                "relationship_type": "Triggering"
            },
            {
                "id": "security_enables_testing",
                "from_element": "security_hardening",
                "to_element": "system_testing",
                "relationship_type": "Triggering"
            },
            {
                "id": "testing_enables_performance",
                "from_element": "system_testing",
                "to_element": "performance_testing",
                "relationship_type": "Triggering"
            },
            
            # Documentation and training
            {
                "id": "testing_enables_docs",
                "from_element": "performance_testing",
                "to_element": "documentation_creation",
                "relationship_type": "Triggering"
            },
            {
                "id": "docs_enables_training",
                "from_element": "documentation_creation",
                "to_element": "team_training",
                "relationship_type": "Triggering"
            },
            
            # Work packages realize deliverables
            {
                "id": "rke2_realizes_cluster",
                "from_element": "rke2_cluster_deployment",
                "to_element": "production_cluster",
                "relationship_type": "Realization"
            },
            {
                "id": "monitoring_realizes_dashboard",
                "from_element": "monitoring_setup",
                "to_element": "monitoring_dashboard",
                "relationship_type": "Realization"
            },
            {
                "id": "security_realizes_policies",
                "from_element": "security_hardening",
                "to_element": "security_policies",
                "relationship_type": "Realization"
            },
            {
                "id": "storage_realizes_backup",
                "from_element": "storage_implementation",
                "to_element": "backup_solution",
                "relationship_type": "Realization"
            },
            {
                "id": "registry_realizes_registry",
                "from_element": "registry_deployment",
                "to_element": "container_registry",
                "relationship_type": "Realization"
            },
            {
                "id": "docs_realizes_procedures",
                "from_element": "documentation_creation",
                "to_element": "operational_procedures",
                "relationship_type": "Realization"
            },
            {
                "id": "training_realizes_materials",
                "from_element": "team_training",
                "to_element": "training_materials",
                "relationship_type": "Realization"
            },
            
            # Events triggered by work packages
            {
                "id": "infra_triggers_ready",
                "from_element": "network_configuration",
                "to_element": "infrastructure_ready",
                "relationship_type": "Triggering"
            },
            {
                "id": "rke2_triggers_operational",
                "from_element": "rke2_cluster_deployment",
                "to_element": "cluster_operational",
                "relationship_type": "Triggering"
            },
            {
                "id": "security_triggers_validated",
                "from_element": "security_hardening",
                "to_element": "security_validated",
                "relationship_type": "Triggering"
            },
            {
                "id": "training_triggers_cutover",
                "from_element": "team_training",
                "to_element": "production_cutover",
                "relationship_type": "Triggering"
            },
            
            # Plateau relationships
            {
                "id": "cluster_realizes_basic",
                "from_element": "cluster_operational",
                "to_element": "basic_platform",
                "relationship_type": "Realization"
            },
            {
                "id": "security_realizes_enhanced",
                "from_element": "security_validated",
                "to_element": "enhanced_platform",
                "relationship_type": "Realization"
            },
            {
                "id": "cutover_realizes_production",
                "from_element": "production_cutover",
                "to_element": "production_platform",
                "relationship_type": "Realization"
            }
        ]
        
        # Create and add relationships
        print("🔗 Creating implementation relationships...")
        for rel_data in relationships_data:
            relationship_input = RelationshipInput(**rel_data)
            relationship = _create_relationship_from_data(relationship_input)
            generator.add_relationship(relationship)
            print(f"  ✅ Added {relationship.relationship_type}: {relationship.from_element} -> {relationship.to_element}")
        
        # Generate PlantUML
        print("📊 Generating PlantUML diagram...")
        plantuml_code = generator.generate_plantuml(
            title="RKE2 Kubernetes Platform - Implementation Layer",
            description="Implementation roadmap and deliverables for RKE2 platform deployment"
        )
        
        # Save PlantUML to file
        with open('rke2_implementation_layer_fixed.puml', 'w') as f:
            f.write(plantuml_code)
        print("💾 Saved PlantUML to rke2_implementation_layer_fixed.puml")
        
        # Get statistics
        stats = {
            "elements": generator.get_element_count(),
            "relationships": generator.get_relationship_count()
        }
        
        print(f"📈 Statistics: {stats['elements']} elements, {stats['relationships']} relationships")
        
        return plantuml_code, stats
        
    except Exception as e:
        print(f"❌ Error generating implementation layer: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("🚀 Starting RKE2 Implementation Layer generation with CORRECT core functions...")
    plantuml_code, stats = generate_implementation_layer()
    
    if plantuml_code:
        print("\n" + "="*60)
        print("📊 GENERATED PLANTUML CODE (preview):")
        print("="*60)
        print(plantuml_code[:500] + "..." if len(plantuml_code) > 500 else plantuml_code)
        print("="*60)
        print(f"✅ Implementation layer generation completed successfully!")
        print(f"📈 Final stats: {stats['elements']} elements, {stats['relationships']} relationships")
    else:
        print("❌ Implementation layer generation failed")
        sys.exit(1)