# User Guide: Datalan RKE2 Kubernetes Platform

## Overview

The Datalan RKE2 Kubernetes Platform is a production-grade, automated Kubernetes deployment system built on Proxmox VE infrastructure. This guide provides end-users with essential information on how to access, use, and interact with the platform.

## Platform Architecture

### Infrastructure Components
- **3 Master Nodes**: HA Kubernetes control plane (rke2-master-01/02/03, IPs 10.135.0.11-13)
- **4 Worker Nodes**: Application workload nodes (rke2-worker-01/02/03/04, IPs 10.135.0.21-24)
- **Kubernetes Version**: v1.32.5+rke2r1 (latest)
- **Operating System**: Ubuntu 24.04.2 LTS with kernel 6.8.0
- **Container Runtime**: containerd 2.0.5-k3s1

### Deployed Services (Verified Live)
- **Longhorn v1.9.0**: Distributed storage with 4 managers and CSI drivers
- **MetalLB**: LoadBalancer with 1 controller + 4 speakers in host network mode
- **NGINX Ingress v1.12.3**: HTTP/HTTPS traffic routing (single controller)
- **Cert-Manager v1.18.0**: TLS automation (controller + webhook + cainjector)
- **Prometheus v3.4.1**: Monitoring with 2 servers + 2 alertmanagers in HA
- **Grafana v12.0.1**: Dashboards with 2 replicas + PostgreSQL cluster
- **Harbor Registry**: Container registry with PostgreSQL/Redis/MinIO
- **Kyverno v1.11.1**: Policy engine with 4 controllers
- **CloudNative PostgreSQL**: Enterprise database operator
- **MinIO Operator**: Object storage management
- **WireGuard VPN**: Secure remote access

## Getting Started

### 1. Network Access

#### VPN Access
To access the Kubernetes cluster, you need WireGuard VPN access:

**Network Ranges:**
- **Cluster Network**: `10.135.0.0/24` (actual deployed network)
- **User VPN Network**: `10.30.10.0/24` (your VPN IP)
- **External Network**: `10.20.22.0/24` (router external interface)

**VPN Configuration:**
Your system administrator will provide you with a WireGuard configuration file. The configuration includes:

- **Server Endpoint**: `10.20.22.11:51820` (WireGuard server)
- **Your VPN IP**: Assigned from `10.30.10.0/24` range (e.g., `10.30.10.11/32`)
- **Allowed Networks**: `10.135.0.0/24, 10.30.10.0/24` (cluster and VPN networks)

**Configuration File Location:**
- Generated configurations are stored on the router at `/etc/wireguard/clients/`
- Each user receives a personalized `.conf` file
- Contact your administrator if you need configuration regeneration

**Example WireGuard Client Configuration:**
```ini
[Interface]
PrivateKey = <your-private-key>
Address = 10.30.10.11/32

[Peer]
PublicKey = <server-public-key>
Endpoint = 10.20.22.11:51820
AllowedIPs = 10.135.0.0/24, 10.30.10.0/24
PersistentKeepalive = 25
```

**Setting Up WireGuard Client:**

1. **Install WireGuard** on your device:
   ```bash
   # Linux (Ubuntu/Debian)
   sudo apt install wireguard
   
   # macOS
   brew install wireguard-tools
   # Or install WireGuard app from App Store
   
   # Windows
   # Download WireGuard installer from wireguard.com
   ```

2. **Import Configuration:**
   ```bash
   # Linux command line
   sudo cp your-config.conf /etc/wireguard/wg0.conf
   sudo systemctl enable wg-quick@wg0
   sudo systemctl start wg-quick@wg0
   
   # Or import in WireGuard GUI applications
   ```

3. **Verify Connection:**
   ```bash
   # Test connectivity to cluster
   ping 10.135.0.1    # Router
   ping 10.135.0.11   # Master node
   
   # Check VPN interface
   ip addr show wg0  # Linux
   ```

**Troubleshooting VPN Issues:**
- Ensure firewall allows UDP port 51820
- Check if your configuration file is correctly formatted
- Verify your assigned IP doesn't conflict with others
- Contact administrator if connection fails consistently

#### Key Endpoints
Once connected via VPN:
- **Rancher UI**: `https://rancher.your-domain.com`
- **Kubernetes API**: `https://api.your-domain.com:6443`
- **HAProxy Stats**: `http://10.30.9.1:8080` (admin access)

### 2. Accessing the Cluster

#### Via Harbor Registry UI
1. Navigate to the Harbor container registry interface
2. Log in using your assigned credentials
3. Browse container images and manage repositories
4. Access vulnerability scanning and replication features

#### Via Grafana Monitoring
1. Access Grafana dashboards for cluster monitoring
2. View Prometheus metrics and alerts
3. Monitor application performance and resource utilization
4. Create custom dashboards for your applications

#### Via kubectl (Command Line)
1. Obtain your kubeconfig file from your administrator
2. Save as `~/.kube/config`
3. Verify access:
```bash
kubectl get nodes
kubectl get namespaces

# Expected nodes (verified live):
NAME             STATUS   ROLES                       AGE   VERSION
rke2-master-01   Ready    control-plane,etcd,master   XXd   v1.32.5+rke2r1
rke2-master-02   Ready    control-plane,etcd,master   XXd   v1.32.5+rke2r1
rke2-master-03   Ready    control-plane,etcd,master   XXd   v1.32.5+rke2r1
rke2-worker-01   Ready    <none>                      XXd   v1.32.5+rke2r1
rke2-worker-02   Ready    <none>                      XXd   v1.32.5+rke2r1
rke2-worker-03   Ready    <none>                      XXd   v1.32.5+rke2r1
rke2-worker-04   Ready    <none>                      XXd   v1.32.5+rke2r1
```

#### Via k9s (Terminal UI)
The platform includes k9s for interactive cluster management:
```bash
k9s
```

## Working with Applications

### Namespace Management

Each team/project typically receives their own namespace for isolation:

```bash
# List available namespaces
kubectl get namespaces

# Switch to your namespace
kubectl config set-context --current --namespace=your-namespace
```

### Storage Classes

The platform provides Longhorn storage with different performance tiers:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-app-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 10Gi
```

### Load Balancer Services

Use MetalLB for external access to your applications:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

**LoadBalancer Services**: MetalLB assigns external IPs automatically from configured pool

### Ingress Configuration

For HTTP/HTTPS traffic routing:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - my-app.your-domain.com
    secretName: my-app-tls
  rules:
  - host: my-app.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-service
            port:
              number: 80
```

## Monitoring and Logging

### Cluster Monitoring (Live Implementation)
Access comprehensive monitoring through deployed systems:

**Prometheus Monitoring (v3.4.1)**:
- 2 Prometheus servers in HA configuration
- 2 Alertmanagers for redundant alerting
- Node exporters on all 7 cluster nodes
- Comprehensive metrics collection and storage

**Grafana Dashboards (v12.0.1)**:
- 2 Grafana replicas with HA setup
- PostgreSQL cluster backend (3 nodes)
- Pre-configured dashboards for cluster metrics
- Custom dashboard creation capabilities

### Application Logs
View application logs:
```bash
# Via kubectl
kubectl logs -f deployment/my-app

# Check available namespaces with applications
kubectl get namespaces
```

### Resource Monitoring
Monitor your application resources:
```bash
# Check resource usage
kubectl top pods
kubectl top nodes

# Describe resources for detailed information
kubectl describe pod my-app-pod
```

## Security and RBAC

### User Permissions
The platform implements role-based access control (RBAC):
- **Namespace Admin**: Full access to assigned namespaces
- **Developer**: Read/write access to deployments and services
- **Viewer**: Read-only access to resources

### Service Accounts
For applications requiring Kubernetes API access:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-namespace
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "create", "update", "delete"]
```

### Network Policies
Implement network segmentation:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: my-app-netpol
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: allowed-namespace
```

## Backup and Recovery

### Persistent Data
Your persistent volumes are automatically backed up to S3 via Longhorn:
- **Backup Schedule**: Daily snapshots at 2:00 AM UTC
- **Retention**: 30 days for daily, 12 weeks for weekly
- **Recovery**: Contact admin for restore operations

### Application Backups
Implement application-specific backup strategies:
```yaml
# Example CronJob for database backup
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - pg_dump $DATABASE_URL > /backup/db-$(date +%Y%m%d).sql
```

## Troubleshooting

### Common Issues

#### Pod Not Starting
```bash
# Check pod status and events
kubectl describe pod my-app-pod

# Check logs
kubectl logs my-app-pod

# Check resource constraints
kubectl top pod my-app-pod
```

#### Network Connectivity Issues
```bash
# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Test service connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -qO- http://my-service:80
```

#### Storage Issues
```bash
# Check PVC status
kubectl get pvc

# Check Longhorn UI for storage details
# Access via Rancher UI → Apps → Longhorn
```

### Getting Help

1. **Documentation**: Check this guide and Rancher UI help sections
2. **Logs**: Always check application and system logs first
3. **System Status**: Verify cluster health via Rancher dashboard
4. **Support**: Contact system administrators with:
   - Namespace and application name
   - Error messages or logs
   - Steps to reproduce the issue

## Best Practices

### Resource Management
- Set resource requests and limits for all containers
- Use horizontal pod autoscaling for variable workloads
- Monitor resource usage regularly

### Security
- Use least-privilege service accounts
- Implement network policies for sensitive applications
- Keep container images updated
- Use secrets for sensitive configuration

### High Availability
- Deploy applications across multiple nodes using pod anti-affinity
- Use readiness and liveness probes
- Implement graceful shutdown handling

### Monitoring
- Add health check endpoints to applications
- Use structured logging (JSON format)
- Implement application metrics collection
- Set up alerts for critical application failures

## Support and Contact

For technical support or questions regarding the platform, contact:
- **System Administrator**: martin_dulovic@datalan.sk
- **Platform Documentation**: This guide and internal wiki
- **Emergency Issues**: Follow your organization's incident response procedures

---

*This guide covers the essential aspects of using the Datalan RKE2 Kubernetes Platform. For advanced configuration and administrative tasks, refer to the DevOps Guide.*