#!/usr/bin/env python3
"""
Fixed RKE2 Motivation Layer Generator using direct MCP tools
Proper error handling and direct function calls
"""

import sys
import os
sys.path.append('src')

try:
    from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput, RelationshipInput
    print("✅ ArchiMate MCP tools imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def generate_motivation_layer():
    """Generate RKE2 Motivation layer with proper error handling"""
    
    try:
        # Define motivation elements with proper ArchiMate types
        elements = [
            # Stakeholders
            ElementInput(
                id="datalan_management",
                name="Datalan Management", 
                element_type="Stakeholder",
                layer="Motivation",
                description="Business sponsor seeking cost reduction and deployment acceleration"
            ),
            ElementInput(
                id="devops_team",
                name="DevOps Team (Martin Dulović)",
                element_type="Stakeholder",
                layer="Motivation", 
                description="Technical architect and primary implementer"
            ),
            ElementInput(
                id="it_operations",
                name="IT Operations Team",
                element_type="Stakeholder",
                layer="Motivation",
                description="Platform operators responsible for maintenance"
            ),
            ElementInput(
                id="dev_teams", 
                name="Development Teams",
                element_type="Stakeholder",
                layer="Motivation",
                description="Platform consumers deploying applications"
            ),
            
            # Drivers
            ElementInput(
                id="manual_processes",
                name="Manual Deployment Processes", 
                element_type="Driver",
                layer="Motivation",
                description="Legacy manual procedures creating bottlenecks"
            ),
            ElementInput(
                id="high_costs",
                name="High Operational Costs",
                element_type="Driver", 
                layer="Motivation",
                description="Resource-intensive operations requiring automation"
            ),
            ElementInput(
                id="security_gaps",
                name="Security Vulnerabilities",
                element_type="Driver",
                layer="Motivation",
                description="Critical security gaps requiring hardening"
            ),
            ElementInput(
                id="scalability_needs",
                name="Scalability Requirements",
                element_type="Driver",
                layer="Motivation", 
                description="Business growth demanding elastic infrastructure"
            ),
            
            # Goals
            ElementInput(
                id="automated_deployment",
                name="Automated Kubernetes Deployment",
                element_type="Goal",
                layer="Motivation",
                description="Eliminate manual intervention through IaC"
            ),
            ElementInput(
                id="cost_reduction", 
                name="Reduced Operational Costs",
                element_type="Goal",
                layer="Motivation",
                description="Achieve 40-60% operational cost reduction"
            ),
            ElementInput(
                id="faster_deployment",
                name="Faster Application Deployment",
                element_type="Goal",
                layer="Motivation",
                description="Reduce deployment time from days to minutes"
            ),
            ElementInput(
                id="enhanced_security",
                name="Enhanced Security Posture", 
                element_type="Goal",
                layer="Motivation",
                description="Enterprise-grade security controls and compliance"
            ),
            ElementInput(
                id="standardization",
                name="Standardized Deployments",
                element_type="Goal",
                layer="Motivation",
                description="Consistent, repeatable deployment processes"
            ),
            
            # Requirements
            ElementInput(
                id="production_grade",
                name="Production-Grade Platform",
                element_type="Requirement",
                layer="Motivation",
                description="Enterprise SLA with 99.9% uptime target"
            ),
            ElementInput(
                id="high_availability", 
                name="High Availability Architecture",
                element_type="Requirement",
                layer="Motivation",
                description="No single points of failure with auto-failover"
            ),
            ElementInput(
                id="security_hardening",
                name="Automated Security Hardening", 
                element_type="Requirement",
                layer="Motivation",
                description="CIS compliance with AppArmor and RBAC"
            ),
            ElementInput(
                id="monitoring_req",
                name="Real-Time Monitoring",
                element_type="Requirement",
                layer="Motivation",
                description="Comprehensive observability with Prometheus/Grafana"
            ),
            ElementInput(
                id="backup_recovery",
                name="Automated Backup and Recovery",
                element_type="Requirement", 
                layer="Motivation",
                description="Disaster recovery with RTO < 4h, RPO < 1h"
            )
        ]
        
        # Define relationships
        relationships = [
            # Stakeholder concerns
            RelationshipInput(
                id="mgmt_concerns_costs",
                from_element="datalan_management", 
                to_element="high_costs",
                relationship_type="Association"
            ),
            RelationshipInput(
                id="devops_addresses_manual",
                from_element="devops_team",
                to_element="manual_processes", 
                relationship_type="Association"
            ),
            RelationshipInput(
                id="ops_security_concern",
                from_element="it_operations",
                to_element="security_gaps",
                relationship_type="Association"
            ),
            RelationshipInput(
                id="devs_need_scalability",
                from_element="dev_teams",
                to_element="scalability_needs",
                relationship_type="Association"
            ),
            
            # Driver influences  
            RelationshipInput(
                id="manual_drives_automation",
                from_element="manual_processes",
                to_element="automated_deployment",
                relationship_type="Influence"
            ),
            RelationshipInput(
                id="costs_drive_reduction", 
                from_element="high_costs",
                to_element="cost_reduction",
                relationship_type="Influence"
            ),
            RelationshipInput(
                id="security_drives_hardening",
                from_element="security_gaps",
                to_element="enhanced_security",
                relationship_type="Influence"
            ),
            RelationshipInput(
                id="scalability_drives_standardization",
                from_element="scalability_needs", 
                to_element="standardization",
                relationship_type="Influence"
            ),
            
            # Goal realizations
            RelationshipInput(
                id="automation_realizes_production",
                from_element="automated_deployment",
                to_element="production_grade",
                relationship_type="Realization"
            ),
            RelationshipInput(
                id="cost_goal_realizes_efficiency",
                from_element="cost_reduction",
                to_element="high_availability",
                relationship_type="Realization"
            ),
            RelationshipInput(
                id="security_goal_realizes_hardening", 
                from_element="enhanced_security",
                to_element="security_hardening",
                relationship_type="Realization"
            ),
            RelationshipInput(
                id="faster_deployment_realizes_monitoring",
                from_element="faster_deployment",
                to_element="monitoring_req",
                relationship_type="Realization"
            ),
            RelationshipInput(
                id="standardization_realizes_backup",
                from_element="standardization",
                to_element="backup_recovery", 
                relationship_type="Realization"
            )
        ]
        
        # Create diagram input
        diagram_input = DiagramInput(
            elements=elements,
            relationships=relationships,
            title="RKE2 Kubernetes Platform - Motivation Layer",
            description="Strategic drivers and business context for RKE2 platform implementation"
        )
        
        print("📊 Generating motivation layer diagram...")
        
        # Generate diagram using MCP tools
        result = create_archimate_diagram(diagram_input)
        
        if result and "successfully" in result:
            print("✅ Motivation layer diagram generated successfully")
            return result
        else:
            print(f"⚠️ Warning: Unexpected result format: {result[:100]}...")
            return result
            
    except Exception as e:
        print(f"❌ Error generating motivation layer: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Starting RKE2 Motivation Layer generation with direct MCP tools...")
    result = generate_motivation_layer()
    
    if result:
        print("\n" + "="*50)
        print(result)
        print("="*50)
        print("✅ Motivation layer generation completed successfully")
    else:
        print("❌ Motivation layer generation failed")
        sys.exit(1)