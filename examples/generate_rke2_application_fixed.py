#!/usr/bin/env python3
"""
Fixed RKE2 Application Layer Generator using core ArchiMate functions
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

def generate_application_layer():
    """Generate RKE2 Application layer using correct core functions"""
    
    try:
        # Clear generator first
        generator.clear()
        print("🔄 Generator cleared")
        
        # Define application elements
        elements_data = [
            # Core Platform Services
            {
                "id": "rke2_platform",
                "name": "RKE2 Kubernetes Platform v1.32.5",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Main orchestration platform with enterprise hardening"
            },
            {
                "id": "kubernetes_api",
                "name": "Kubernetes API Server Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Central cluster management and orchestration API"
            },
            {
                "id": "container_runtime",
                "name": "Container Runtime Service (containerd)",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Container lifecycle management and execution"
            },
            
            # Storage Services
            {
                "id": "longhorn_storage",
                "name": "Longhorn Storage Service v1.9.0",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Cloud-native distributed block storage with 3-way replication"
            },
            {
                "id": "persistent_volume",
                "name": "Persistent Volume Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Dynamic storage provisioning with automatic volume management"
            },
            {
                "id": "minio_storage",
                "name": "MinIO Object Storage Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "S3-compatible object storage for backup and artifacts"
            },
            
            # Networking and Load Balancing
            {
                "id": "metallb_lb",
                "name": "MetalLB LoadBalancer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Bare-metal load balancing with automatic IP assignment"
            },
            {
                "id": "nginx_ingress",
                "name": "NGINX Ingress Controller v1.12.3",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Layer 7 HTTP/HTTPS routing with SSL termination"
            },
            {
                "id": "traffic_distribution",
                "name": "Traffic Distribution Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Intelligent load balancing across worker nodes"
            },
            {
                "id": "http_routing",
                "name": "HTTP/HTTPS Routing Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Application-level traffic routing with host and path rules"
            },
            
            # Security and Certificate Management
            {
                "id": "cert_manager",
                "name": "Cert-Manager v1.18.0",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Automated TLS certificate provisioning with Let's Encrypt"
            },
            {
                "id": "tls_automation",
                "name": "TLS Certificate Automation Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "SSL/TLS lifecycle management and renewal"
            },
            {
                "id": "kyverno_policy",
                "name": "Kyverno Policy Engine v1.11.1",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Kubernetes-native policy enforcement with 4 controllers"
            },
            {
                "id": "policy_enforcement",
                "name": "Policy Enforcement Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Runtime security validation and admission control"
            },
            
            # Container Registry
            {
                "id": "harbor_registry",
                "name": "Harbor Container Registry",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Enterprise-grade registry with vulnerability scanning"
            },
            {
                "id": "container_registry",
                "name": "Container Registry Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Image storage, distribution, and lifecycle management"
            },
            {
                "id": "harbor_postgresql",
                "name": "Harbor PostgreSQL Database",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Registry metadata and configuration backend"
            },
            {
                "id": "harbor_redis",
                "name": "Harbor Redis Cache",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Image layer caching for improved performance"
            },
            
            # Database Management
            {
                "id": "cnpg_operator",
                "name": "CloudNative PostgreSQL Operator",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Enterprise PostgreSQL management with automated failover"
            },
            {
                "id": "database_management",
                "name": "Database Management Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Database provisioning, backup, and lifecycle automation"
            },
            
            # Monitoring and Observability
            {
                "id": "prometheus_ha",
                "name": "Prometheus v3.4.1 (HA)",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "High-availability metrics collection with 2-server configuration"
            },
            {
                "id": "metrics_collection",
                "name": "Metrics Collection Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Time-series data gathering from all cluster components"
            },
            {
                "id": "grafana_dashboards",
                "name": "Grafana Dashboards v12.0.1",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Advanced visualization platform with 2 replicas"
            },
            {
                "id": "monitoring_visualization",
                "name": "Monitoring Visualization Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Dashboard services with PostgreSQL backend"
            },
            {
                "id": "alertmanager",
                "name": "AlertManager",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Intelligent alerting and notification routing"
            },
            {
                "id": "alerting_service",
                "name": "Alerting & Notification Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Alert aggregation, deduplication, and routing"
            },
            
            # Access Control
            {
                "id": "wireguard_vpn",
                "name": "WireGuard VPN Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Encrypted remote access with per-user configurations"
            },
            {
                "id": "secure_access",
                "name": "Secure Remote Access Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "User authentication and network access control"
            },
            {
                "id": "haproxy_lb",
                "name": "HAProxy API LoadBalancer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "High-availability API server access with health checking"
            },
            {
                "id": "rbac_integration",
                "name": "RBAC Integration Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Role-based access control with namespace isolation"
            },
            
            # Data Objects
            {
                "id": "cluster_config_data",
                "name": "Cluster Configuration Data",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "ConfigMaps, Secrets, RBAC policies, and cluster state"
            },
            {
                "id": "monitoring_data",
                "name": "Monitoring & Metrics Data",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Time-series metrics, logs, and alerting data"
            },
            {
                "id": "container_artifacts",
                "name": "Container Images & Artifacts",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Container images, Helm charts, and deployment artifacts"
            }
        ]
        
        # Create and add elements
        print("📦 Creating application elements...")
        for elem_data in elements_data:
            element_input = ElementInput(**elem_data)
            element = _create_element_from_data(element_input)
            generator.add_element(element)
            print(f"  ✅ Added {element.element_type}: {element.name}")
        
        # Define relationships  
        relationships_data = [
            # Platform service realizations
            {
                "id": "rke2_realizes_k8s_api",
                "from_element": "rke2_platform",
                "to_element": "kubernetes_api",
                "relationship_type": "Realization"
            },
            {
                "id": "rke2_realizes_container",
                "from_element": "rke2_platform",
                "to_element": "container_runtime",
                "relationship_type": "Realization"
            },
            
            # Storage service realizations
            {
                "id": "longhorn_realizes_pv",
                "from_element": "longhorn_storage",
                "to_element": "persistent_volume",
                "relationship_type": "Realization"
            },
            
            # Network service realizations
            {
                "id": "metallb_realizes_traffic",
                "from_element": "metallb_lb",
                "to_element": "traffic_distribution",
                "relationship_type": "Realization"
            },
            {
                "id": "nginx_realizes_routing",
                "from_element": "nginx_ingress",
                "to_element": "http_routing",
                "relationship_type": "Realization"
            },
            
            # Security service realizations
            {
                "id": "cert_mgr_realizes_tls",
                "from_element": "cert_manager",
                "to_element": "tls_automation",
                "relationship_type": "Realization"
            },
            {
                "id": "kyverno_realizes_policy",
                "from_element": "kyverno_policy",
                "to_element": "policy_enforcement",
                "relationship_type": "Realization"
            },
            
            # Registry service realizations
            {
                "id": "harbor_realizes_registry",
                "from_element": "harbor_registry",
                "to_element": "container_registry",
                "relationship_type": "Realization"
            },
            
            # Database service realizations
            {
                "id": "cnpg_realizes_db_mgmt",
                "from_element": "cnpg_operator",
                "to_element": "database_management",
                "relationship_type": "Realization"
            },
            
            # Monitoring service realizations
            {
                "id": "prometheus_realizes_metrics",
                "from_element": "prometheus_ha",
                "to_element": "metrics_collection",
                "relationship_type": "Realization"
            },
            {
                "id": "grafana_realizes_visualization",
                "from_element": "grafana_dashboards",
                "to_element": "monitoring_visualization",
                "relationship_type": "Realization"
            },
            {
                "id": "alertmgr_realizes_alerting",
                "from_element": "alertmanager",
                "to_element": "alerting_service",
                "relationship_type": "Realization"
            },
            
            # Access service realizations
            {
                "id": "wireguard_realizes_access",
                "from_element": "wireguard_vpn",
                "to_element": "secure_access",
                "relationship_type": "Realization"
            },
            {
                "id": "haproxy_realizes_rbac",
                "from_element": "haproxy_lb",
                "to_element": "rbac_integration",
                "relationship_type": "Realization"
            },
            
            # Service dependencies
            {
                "id": "registry_serves_platform",
                "from_element": "container_registry",
                "to_element": "rke2_platform",
                "relationship_type": "Serving"
            },
            {
                "id": "storage_serves_platform",
                "from_element": "persistent_volume",
                "to_element": "rke2_platform",
                "relationship_type": "Serving"
            },
            {
                "id": "monitoring_serves_platform",
                "from_element": "metrics_collection",
                "to_element": "rke2_platform",
                "relationship_type": "Serving"
            },
            
            # Data access relationships
            {
                "id": "platform_accesses_config",
                "from_element": "rke2_platform",
                "to_element": "cluster_config_data",
                "relationship_type": "Access"
            },
            {
                "id": "monitoring_accesses_data",
                "from_element": "prometheus_ha",
                "to_element": "monitoring_data",
                "relationship_type": "Access"
            },
            {
                "id": "registry_accesses_artifacts",
                "from_element": "harbor_registry",
                "to_element": "container_artifacts",
                "relationship_type": "Access"
            }
        ]
        
        # Create and add relationships
        print("🔗 Creating application relationships...")
        for rel_data in relationships_data:
            relationship_input = RelationshipInput(**rel_data)
            relationship = _create_relationship_from_data(relationship_input)
            generator.add_relationship(relationship)
            print(f"  ✅ Added {relationship.relationship_type}: {relationship.from_element} -> {relationship.to_element}")
        
        # Generate PlantUML
        print("📊 Generating PlantUML diagram...")
        plantuml_code = generator.generate_plantuml(
            title="RKE2 Kubernetes Platform - Application Layer",
            description="Comprehensive microservices architecture providing complete Kubernetes platform capabilities"
        )
        
        # Save PlantUML to file
        with open('rke2_application_layer_fixed.puml', 'w') as f:
            f.write(plantuml_code)
        print("💾 Saved PlantUML to rke2_application_layer_fixed.puml")
        
        # Get statistics
        stats = {
            "elements": generator.get_element_count(),
            "relationships": generator.get_relationship_count()
        }
        
        print(f"📈 Statistics: {stats['elements']} elements, {stats['relationships']} relationships")
        
        return plantuml_code, stats
        
    except Exception as e:
        print(f"❌ Error generating application layer: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("🚀 Starting RKE2 Application Layer generation with CORRECT core functions...")
    plantuml_code, stats = generate_application_layer()
    
    if plantuml_code:
        print("\n" + "="*60)
        print("📊 GENERATED PLANTUML CODE (preview):")
        print("="*60)
        print(plantuml_code[:500] + "..." if len(plantuml_code) > 500 else plantuml_code)
        print("="*60)
        print(f"✅ Application layer generation completed successfully!")
        print(f"📈 Final stats: {stats['elements']} elements, {stats['relationships']} relationships")
    else:
        print("❌ Application layer generation failed")
        sys.exit(1)