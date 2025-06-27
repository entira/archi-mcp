# Claude Desktop MCP Kubernetes Analysis Prompt

## Comprehensive Kubernetes Cluster Analysis Using MCP Server

This prompt is designed to leverage the powerful Kubernetes Model Context Protocol (MCP) server capabilities in Claude Desktop to perform thorough cluster analysis and documentation of the Datalan RKE2 Kubernetes platform.

---

## 🎯 **PRIMARY OBJECTIVE**

Perform a comprehensive, real-time analysis of our RKE2 Kubernetes cluster to:
1. **Validate** actual implementation against documented architecture
2. **Document** live cluster state with concrete evidence
3. **Identify** gaps between planned vs deployed components
4. **Generate** actionable insights for system optimization
5. **Create** detailed cluster inventory with current status

---

## 🔧 **MCP SERVER CAPABILITIES TO UTILIZE**

Based on the available MCP server features, use these tools systematically:

### ✅ **Configuration Analysis**
- View and analyze current Kubernetes configuration
- Detect any configuration changes or drift
- Document .kube/config or in-cluster configuration setup

### ✅ **Generic Kubernetes Resources**
- Perform comprehensive CRUD operations on all resources
- List, get, and analyze any Kubernetes or OpenShift resource
- Create detailed inventory of all deployed resources

### ✅ **Pod Operations & Analysis**
- List pods in all namespaces with detailed status
- Get specific pod information from each namespace
- Show logs for critical system pods
- Get resource usage metrics for all pods
- Execute diagnostic commands in pods when needed

### ✅ **Namespace Management**
- List all Kubernetes namespaces
- Analyze namespace-specific resources and configurations
- Document namespace isolation and RBAC setup

### ✅ **Event Analysis**
- View Kubernetes events across all namespaces
- Monitor cluster health through event patterns
- Identify recurring issues or warnings

### ☸️ **Helm Analysis**
- List all Helm releases across namespaces
- Analyze Helm chart deployments and versions
- Document Helm-managed applications

---

## 📋 **DETAILED ANALYSIS TASKS**

### **Phase 1: Cluster Foundation Analysis**

1. **Node Inventory & Health**
   ```
   → List all cluster nodes with detailed specifications
   → Check node readiness and resource capacity
   → Analyze node labels, taints, and scheduling constraints
   → Document actual vs planned node configuration
   → Verify master/worker role distribution
   ```

2. **Namespace Structure**
   ```
   → List all namespaces in the cluster
   → Analyze resource quotas and limits per namespace
   → Document namespace isolation and RBAC policies
   → Identify system vs application namespaces
   ```

3. **System Component Verification**
   ```
   → Analyze kube-system namespace components
   → Verify etcd cluster health and configuration
   → Check API server configuration and endpoints
   → Validate scheduler and controller-manager status
   → Document CoreDNS and networking components
   ```

### **Phase 2: Application Services Analysis**

4. **Storage System (Longhorn)**
   ```
   → List all Longhorn components in longhorn-system namespace
   → Analyze storage classes and their configurations
   → Check persistent volumes and claims status
   → Verify backup configuration and S3 integration
   → Document storage capacity and utilization
   ```

5. **Network Services**
   ```
   → Analyze MetalLB configuration and IP pools
   → Check NGINX Ingress controller deployment
   → Verify service mesh components (if any)
   → Document LoadBalancer and Ingress resources
   → Check network policies and security rules
   ```

6. **Certificate Management**
   ```
   → List cert-manager components and configurations
   → Check ClusterIssuers and certificate status
   → Verify TLS certificates and expiration dates
   → Document certificate automation setup
   ```

7. **Management Interface (Rancher)**
   ```
   → Analyze Rancher deployment in cattle-system
   → Check Rancher UI accessibility and configuration
   → Verify Fleet GitOps components
   → Document management capabilities and access
   ```

### **Phase 3: Security & Monitoring Analysis**

8. **Security Implementation**
   ```
   → Analyze RBAC roles and bindings across namespaces
   → Check service accounts and their permissions
   → Verify security policies and network policies
   → Document authentication and authorization setup
   → Check for security scanning tools and policies
   ```

9. **Monitoring & Observability**
   ```
   → List monitoring components (Prometheus, Grafana, etc.)
   → Analyze metrics collection and storage
   → Check log aggregation and management (Loki)
   → Verify alerting rules and notification setup
   → Document observability stack completeness
   ```

### **Phase 4: Performance & Resource Analysis**

10. **Resource Utilization**
    ```
    → Get resource usage metrics for all nodes
    → Analyze pod resource requests vs limits
    → Check resource quotas enforcement
    → Identify resource bottlenecks or waste
    → Document capacity planning requirements
    ```

11. **Performance Metrics**
    ```
    → Analyze cluster performance indicators
    → Check pod startup times and readiness
    → Verify service response times and latency
    → Document performance baselines
    ```

---

## 🎯 **SPECIFIC EVIDENCE GATHERING**

For each component, collect these specific details:

### **Evidence Format:**
```
Component: [Component Name]
Namespace: [Namespace]
Status: [Running/Pending/Failed/Unknown]
Replicas: [Current/Desired]
Version: [Image/Chart Version]
Resources: [CPU/Memory Usage]
Configuration: [Key Settings]
Health: [Ready/Unhealthy + Reason]
Issues: [Any Problems Identified]
```

### **Critical Systems to Document:**
- **etcd cluster** (3 masters expected)
- **Kubernetes API servers** (HA configuration)
- **Longhorn storage system** (distributed storage)
- **MetalLB load balancer** (IP pool: 10.30.9.200-250)
- **NGINX Ingress controller** (HTTP/HTTPS routing)
- **Cert-Manager** (TLS automation)
- **Rancher management UI** (v2.11.2 expected)
- **Monitoring stack** (Prometheus/Grafana/Loki)

---

## 📊 **ANALYSIS OUTPUT FORMAT**

Structure your analysis in these sections:

### **1. Executive Summary**
- Cluster health overview (Green/Yellow/Red status)
- Critical findings and recommendations
- Compliance with documented architecture

### **2. Infrastructure Validation**
- Node configuration vs documentation
- Network setup verification
- Resource allocation analysis

### **3. Service Implementation Status**
```
✅ Fully Implemented: [List with evidence]
⚠️ Partially Implemented: [List with gaps identified]
❌ Missing/Failed: [List with reasons]
🔄 In Progress: [List with current status]
```

### **4. Security Posture Assessment**
- RBAC implementation completeness
- Network security policies
- Certificate management status
- Access control verification

### **5. Performance & Resource Report**
- Current resource utilization
- Capacity planning recommendations
- Performance bottlenecks identified

### **6. Actionable Recommendations**
Prioritized list of:
- **Critical Issues** (requiring immediate attention)
- **Optimization Opportunities** (performance/cost improvements)
- **Missing Components** (planned but not implemented)
- **Best Practice Gaps** (security/operational improvements)

---

## 🎯 **SUCCESS CRITERIA**

This analysis is successful when you provide:

1. **Complete cluster inventory** with current status
2. **Evidence-based validation** of documented architecture
3. **Gap analysis** between planned vs actual implementation
4. **Specific recommendations** with actionable steps
5. **Performance baseline** for ongoing monitoring
6. **Security assessment** with concrete findings

---

## 🚀 **EXECUTION INSTRUCTIONS**

**Start your analysis with:**
"I'll now perform a comprehensive analysis of your RKE2 Kubernetes cluster using the MCP server capabilities. This will provide real-time evidence about your cluster's current state and validate it against your documented architecture."

**Then systematically work through each phase**, gathering evidence and building a complete picture of the cluster's actual implementation.

**Focus on providing concrete, actionable insights** rather than generic recommendations.

---

*This prompt leverages the full power of the Kubernetes MCP server to provide deep, real-time insights into your cluster's actual state and performance.*

---

## 🎓 **LESSONS LEARNED FROM DATALAN RKE2 ANALYSIS**

### ✅ **MCP Analysis Success Metrics**
Based on the successful analysis of the Datalan RKE2 cluster:

**Perfect Implementation Discovered:**
- **Cluster Grade**: 9.6/10 (Enterprise Excellence)
- **All Components Operational**: 100% system health
- **Resource Efficiency**: 1.2 cores, 11GB memory (optimal)
- **Enterprise Stack**: Harbor, Prometheus HA, Grafana, CNPG, Kyverno

**Key Discovery Methods That Worked:**
1. **Systematic namespace enumeration** revealed complete enterprise stack
2. **Resource usage analysis** showed excellent efficiency
3. **Node status verification** confirmed perfect HA setup
4. **Version analysis** confirmed latest Kubernetes + components

### 🔍 **Analysis Framework Validation**
This framework successfully identified:
- **Live network configuration** (10.135.0.0/24 vs documented 10.30.9.0/24)
- **Complete monitoring stack** (Prometheus v3.4.1 HA + Grafana v12.0.1)
- **Enterprise applications** not mentioned in original docs (Harbor, CNPG, MinIO)
- **Policy enforcement** (Kyverno with 4 controllers)
- **Performance metrics** (actual resource utilization)

### 📊 **Real System vs Documentation**
**Major Discoveries:**
- **Network**: 10.135.0.0/24 (actual) vs 10.30.9.0/24 (planned)
- **Monitoring**: Fully deployed HA Prometheus/Grafana vs "partially implemented"
- **Database**: CNPG operator deployed vs "planned but not implemented"
- **Policy**: Kyverno enforcement active vs not mentioned
- **Registry**: Harbor fully operational vs not documented

This validates the critical importance of live system analysis over documentation assumptions.

---

*This analysis framework proven effective on enterprise RKE2 deployment with 9.6/10 implementation quality.*