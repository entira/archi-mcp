#!/usr/bin/env python3
"""
Fixed RKE2 Technology Layer Generator using core ArchiMate functions
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

def generate_technology_layer():
    """Generate RKE2 Technology layer using correct core functions"""
    
    try:
        # Clear generator first
        generator.clear()
        print("🔄 Generator cleared")
        
        # Define technology elements
        elements_data = [
            # Container Runtime Technology
            {
                "id": "containerd_runtime",
                "name": "containerd Runtime v1.7.28",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "High-performance container runtime with CRI compatibility"
            },
            {
                "id": "runc_executor",
                "name": "runc Container Executor",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "OCI-compliant container execution engine"
            },
            
            # Kubernetes Core Technology
            {
                "id": "kubernetes_core",
                "name": "Kubernetes Core v1.32.5",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Container orchestration platform with enterprise features"
            },
            {
                "id": "etcd_cluster",
                "name": "etcd Cluster v3.5.16",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Distributed key-value store for cluster state"
            },
            {
                "id": "kube_scheduler",
                "name": "Kubernetes Scheduler",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Pod scheduling and resource allocation service"
            },
            {
                "id": "kube_controller",
                "name": "Kubernetes Controller Manager",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Control loop management for cluster operations"
            },
            
            # Networking Technology
            {
                "id": "cilium_cni",
                "name": "Cilium CNI v1.16.5",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "eBPF-based networking with advanced security features"
            },
            {
                "id": "kube_proxy",
                "name": "kube-proxy Service",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Network proxy for service load balancing"
            },
            {
                "id": "coredns",
                "name": "CoreDNS v1.12.0",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "DNS server and service discovery for cluster"
            },
            
            # Storage Technology
            {
                "id": "csi_driver",
                "name": "Container Storage Interface (CSI)",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Storage orchestration interface for dynamic provisioning"
            },
            {
                "id": "filesystem_storage",
                "name": "Linux Filesystem Storage",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Ext4/XFS persistent storage with LVM support"
            },
            
            # Security Technology
            {
                "id": "apparmor_security",
                "name": "AppArmor Security Module",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Mandatory access control for container security"
            },
            {
                "id": "seccomp_filter",
                "name": "Seccomp System Call Filter",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "System call filtering for container isolation"
            },
            {
                "id": "iptables_firewall",
                "name": "iptables Firewall",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Network packet filtering and traffic control"
            },
            
            # Monitoring Technology
            {
                "id": "prometheus_tsdb",
                "name": "Prometheus Time Series Database",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "High-performance metrics storage and query engine"
            },
            {
                "id": "node_exporter",
                "name": "Node Exporter",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "System metrics collection for hardware monitoring"
            },
            {
                "id": "cadvisor",
                "name": "cAdvisor Container Monitor",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Container resource usage and performance monitoring"
            },
            
            # Database Technology
            {
                "id": "postgresql_engine",
                "name": "PostgreSQL Database Engine v16.6",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "ACID-compliant relational database with streaming replication"
            },
            {
                "id": "redis_cache",
                "name": "Redis In-Memory Cache",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "High-performance key-value store for caching"
            },
            
            # Load Balancing Technology
            {
                "id": "haproxy_engine",
                "name": "HAProxy Load Balancer v3.1.2",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "High-availability HTTP/TCP load balancer"
            },
            {
                "id": "nginx_engine",
                "name": "NGINX Web Server v1.27.3",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "High-performance web server and reverse proxy"
            },
            
            # VPN Technology
            {
                "id": "wireguard_kernel",
                "name": "WireGuard Kernel Module",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Modern VPN implementation with cryptographic security"
            },
            
            # Backup Technology
            {
                "id": "velero_backup",
                "name": "Velero Backup Engine",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Kubernetes-native backup and disaster recovery"
            },
            {
                "id": "restic_storage",
                "name": "Restic Backup Repository",
                "element_type": "Technology_Service",
                "layer": "Technology",
                "description": "Fast, secure, efficient backup program"
            }
        ]
        
        # Create and add elements
        print("🔧 Creating technology elements...")
        for elem_data in elements_data:
            element_input = ElementInput(**elem_data)
            element = _create_element_from_data(element_input)
            generator.add_element(element)
            print(f"  ✅ Added {element.element_type}: {element.name}")
        
        # Define relationships  
        relationships_data = [
            # Container Runtime Dependencies
            {
                "id": "containerd_uses_runc",
                "from_element": "containerd_runtime",
                "to_element": "runc_executor",
                "relationship_type": "Serving"
            },
            {
                "id": "k8s_uses_containerd",
                "from_element": "kubernetes_core",
                "to_element": "containerd_runtime",
                "relationship_type": "Serving"
            },
            
            # Kubernetes Core Dependencies
            {
                "id": "k8s_uses_etcd",
                "from_element": "kubernetes_core",
                "to_element": "etcd_cluster",
                "relationship_type": "Serving"
            },
            {
                "id": "scheduler_serves_k8s",
                "from_element": "kube_scheduler",
                "to_element": "kubernetes_core",
                "relationship_type": "Serving"
            },
            {
                "id": "controller_serves_k8s",
                "from_element": "kube_controller",
                "to_element": "kubernetes_core",
                "relationship_type": "Serving"
            },
            
            # Networking Dependencies
            {
                "id": "cilium_serves_k8s",
                "from_element": "cilium_cni",
                "to_element": "kubernetes_core",
                "relationship_type": "Serving"
            },
            {
                "id": "proxy_serves_k8s",
                "from_element": "kube_proxy",
                "to_element": "kubernetes_core",
                "relationship_type": "Serving"
            },
            {
                "id": "dns_serves_k8s",
                "from_element": "coredns",
                "to_element": "kubernetes_core",
                "relationship_type": "Serving"
            },
            {
                "id": "cilium_uses_iptables",
                "from_element": "cilium_cni",
                "to_element": "iptables_firewall",
                "relationship_type": "Serving"
            },
            
            # Storage Dependencies
            {
                "id": "csi_serves_k8s",
                "from_element": "csi_driver",
                "to_element": "kubernetes_core",
                "relationship_type": "Serving"
            },
            {
                "id": "csi_uses_filesystem",
                "from_element": "csi_driver",
                "to_element": "filesystem_storage",
                "relationship_type": "Serving"
            },
            
            # Security Dependencies
            {
                "id": "apparmor_serves_containerd",
                "from_element": "apparmor_security",
                "to_element": "containerd_runtime",
                "relationship_type": "Serving"
            },
            {
                "id": "seccomp_serves_containerd",
                "from_element": "seccomp_filter",
                "to_element": "containerd_runtime",
                "relationship_type": "Serving"
            },
            
            # Monitoring Dependencies
            {
                "id": "prometheus_uses_tsdb",
                "from_element": "prometheus_tsdb",
                "to_element": "filesystem_storage",
                "relationship_type": "Serving"
            },
            {
                "id": "node_exporter_serves_prometheus",
                "from_element": "node_exporter",
                "to_element": "prometheus_tsdb",
                "relationship_type": "Serving"
            },
            {
                "id": "cadvisor_serves_prometheus",
                "from_element": "cadvisor",
                "to_element": "prometheus_tsdb",
                "relationship_type": "Serving"
            },
            
            # Database Dependencies
            {
                "id": "postgresql_uses_filesystem",
                "from_element": "postgresql_engine",
                "to_element": "filesystem_storage",
                "relationship_type": "Serving"
            },
            {
                "id": "redis_uses_filesystem",
                "from_element": "redis_cache",
                "to_element": "filesystem_storage",
                "relationship_type": "Serving"
            },
            
            # Load Balancer Dependencies
            {
                "id": "haproxy_uses_iptables",
                "from_element": "haproxy_engine",
                "to_element": "iptables_firewall",
                "relationship_type": "Serving"
            },
            {
                "id": "nginx_uses_filesystem",
                "from_element": "nginx_engine",
                "to_element": "filesystem_storage",
                "relationship_type": "Serving"
            },
            
            # VPN Dependencies
            {
                "id": "wireguard_uses_iptables",
                "from_element": "wireguard_kernel",
                "to_element": "iptables_firewall",
                "relationship_type": "Serving"
            },
            
            # Backup Dependencies
            {
                "id": "velero_uses_restic",
                "from_element": "velero_backup",
                "to_element": "restic_storage",
                "relationship_type": "Serving"
            },
            {
                "id": "restic_uses_filesystem",
                "from_element": "restic_storage",
                "to_element": "filesystem_storage",
                "relationship_type": "Serving"
            }
        ]
        
        # Create and add relationships
        print("🔗 Creating technology relationships...")
        for rel_data in relationships_data:
            relationship_input = RelationshipInput(**rel_data)
            relationship = _create_relationship_from_data(relationship_input)
            generator.add_relationship(relationship)
            print(f"  ✅ Added {relationship.relationship_type}: {relationship.from_element} -> {relationship.to_element}")
        
        # Generate PlantUML
        print("📊 Generating PlantUML diagram...")
        plantuml_code = generator.generate_plantuml(
            title="RKE2 Kubernetes Platform - Technology Layer",
            description="Core technology services and infrastructure components supporting the RKE2 platform"
        )
        
        # Save PlantUML to file
        with open('rke2_technology_layer_fixed.puml', 'w') as f:
            f.write(plantuml_code)
        print("💾 Saved PlantUML to rke2_technology_layer_fixed.puml")
        
        # Get statistics
        stats = {
            "elements": generator.get_element_count(),
            "relationships": generator.get_relationship_count()
        }
        
        print(f"📈 Statistics: {stats['elements']} elements, {stats['relationships']} relationships")
        
        return plantuml_code, stats
        
    except Exception as e:
        print(f"❌ Error generating technology layer: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("🚀 Starting RKE2 Technology Layer generation with CORRECT core functions...")
    plantuml_code, stats = generate_technology_layer()
    
    if plantuml_code:
        print("\n" + "="*60)
        print("📊 GENERATED PLANTUML CODE (preview):")
        print("="*60)
        print(plantuml_code[:500] + "..." if len(plantuml_code) > 500 else plantuml_code)
        print("="*60)
        print(f"✅ Technology layer generation completed successfully!")
        print(f"📈 Final stats: {stats['elements']} elements, {stats['relationships']} relationships")
    else:
        print("❌ Technology layer generation failed")
        sys.exit(1)