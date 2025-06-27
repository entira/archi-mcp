# DevOps Guide: Datalan RKE2 Kubernetes Platform

## Overview

This DevOps guide provides comprehensive information for system administrators, DevOps engineers, and platform maintainers working with the Datalan RKE2 Kubernetes deployment system. It covers deployment procedures, maintenance tasks, troubleshooting, and operational best practices.

## System Architecture

### Infrastructure Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    Proxmox VE Cluster                      │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │  Master │ │  Master │ │  Master │ │ Worker  │ │ Worker  ││
│ │   Node  │ │   Node  │ │   Node  │ │  Node   │ │  Node   ││
│ │   #1    │ │   #2    │ │   #3    │ │   #1    │ │   #2    ││
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘│
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                        │
│ │ Worker  │ │ Worker  │ │  Router │                        │
│ │  Node   │ │  Node   │ │   VM    │                        │
│ │   #3    │ │   #4    │ │         │                        │
│ └─────────┘ └─────────┘ └─────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Network Architecture
- **External Network**: `10.20.22.0/24` (Proxmox management network)
- **Internal Cluster Network**: `10.135.0.0/24` (RKE2 nodes - actual deployed)
- **VPN User Network**: `10.30.10.0/24` (WireGuard clients)
- **MetalLB**: LoadBalancer service with automatic IP assignment

### Core Components (Verified Live System)
- **RKE2 v1.32.5+rke2r1**: Kubernetes distribution (current)
- **Longhorn v1.9.0**: Distributed storage with 4 managers + CSI
- **MetalLB**: LoadBalancer (1 controller + 4 speakers in host network)
- **NGINX Ingress v1.12.3**: HTTP/HTTPS routing (single controller)
- **Cert-Manager v1.18.0**: TLS automation (controller + webhook + cainjector)
- **Prometheus v3.4.1**: Monitoring stack (2 servers + 2 alertmanagers HA)
- **Grafana v12.0.1**: Dashboards (2 replicas + PostgreSQL cluster)
- **Harbor Registry**: Container registry with PostgreSQL/Redis/MinIO
- **Kyverno v1.11.1**: Policy engine (4 controllers)
- **CloudNative PostgreSQL**: Enterprise database operator
- **MinIO Operator**: Object storage management
- **HAProxy**: API server load balancing
- **WireGuard**: VPN access

## Prerequisites

### Infrastructure Requirements
1. **Proxmox VE Cluster** with root SSH access
2. **Network Configuration**:
   - One /24 subnet (deployed: `10.135.0.0/24`)
   - VLAN configuration on switches
   - DNS domain with Cloudflare account
3. **Resource Allocation**:
   - **Master nodes**: 3 × (4 vCPU, 6GB RAM, 80GB disk)
   - **Worker nodes**: 4 × (8 vCPU, 16GB RAM, 100GB boot + 300GB data)
   - **Router**: 1 × (2 vCPU, 2GB RAM, 20GB disk)

### Administrative Prerequisites
- **SSH Key**: `id_ed25519_devops` for VM access
- **Ansible Vault**: `vault-metis` file for encrypted variables
- **Network Access**: Ability to reach Proxmox management interface
- **Allocated IP Ranges**: For cluster and VPN networks

## Deployment Procedures

### 1. Environment Setup

#### Clone Repository
```bash
git clone <repository-url>
cd proxmox-rke2/ansible-main
```

#### Install Dependencies
```bash
# Install Ansible
pip install ansible-core

# Install required collections
ansible-galaxy collection install -r collections.yaml
```

#### Configure Environment
Edit configuration files in `inventory/group_vars/all/`:

**Key Configuration Files:**
- `servers.yml`: VM specifications and IPs
- `rke2.yaml`: Kubernetes cluster configuration
- `router.yaml`: VPN and networking settings
- `users.yaml`: User accounts and access

### 2. Infrastructure Deployment

#### Phase 1: Create VMs on Proxmox
```bash
# Create router VM (always required)
ansible-playbook --vault-password-file ~/.ansible/vault-metis \
  -l PVE01 playbooks/proxmox_create_router.yaml

# Create RKE2 cluster VMs
ansible-playbook --vault-password-file ~/.ansible/vault-metis \
  -l PVE01 playbooks/proxmox_create_rke2.yaml
```

#### Phase 2: Configure Router
```bash
# Deploy router services (WireGuard, HAProxy)
ansible-playbook --vault-password-file ~/.ansible/vault-metis \
  playbooks/deploy_router.yaml
```

#### Phase 3: Deploy RKE2 Cluster
```bash
# Install and configure RKE2 cluster
ansible-playbook --vault-password-file ~/.ansible/vault-metis \
  playbooks/deploy_rke2_cluster.yaml
```

### 3. Post-Deployment Configuration

#### Access Cluster
```bash
# Copy kubeconfig from master node (actual deployed IPs)
scp -i ~/.ssh/id_ed25519_devops \
  ubuntu@10.135.0.11:/etc/rancher/rke2/rke2.yaml ~/.kube/config

# Update server endpoint
sed -i 's/127.0.0.1:6443/api.your-domain.com:6443/g' ~/.kube/config

# Verify cluster (expected live output)
kubectl get nodes
# NAME             STATUS   ROLES                       AGE   VERSION
# rke2-master-01   Ready    control-plane,etcd,master   XXd   v1.32.5+rke2r1
# rke2-master-02   Ready    control-plane,etcd,master   XXd   v1.32.5+rke2r1
# rke2-master-03   Ready    control-plane,etcd,master   XXd   v1.32.5+rke2r1
# rke2-worker-01   Ready    <none>                      XXd   v1.32.5+rke2r1
# rke2-worker-02   Ready    <none>                      XXd   v1.32.5+rke2r1
# rke2-worker-03   Ready    <none>                      XXd   v1.32.5+rke2r1
# rke2-worker-04   Ready    <none>                      XXd   v1.32.5+rke2r1
```

#### Verify Services (Live System Status)
```bash
# Check all system pods (verified operational)
kubectl get pods -A

# Expected key namespaces with running pods:
# - longhorn-system: 4 longhorn-manager pods + CSI drivers
# - metallb-system: 1 controller + 4 speaker pods
# - ingress-nginx: 1 controller pod
# - cert-manager: controller + webhook + cainjector
# - monitoring: 2 prometheus + 2 alertmanager + node-exporters
# - harbor-system: Harbor registry with PostgreSQL/Redis/MinIO
# - kyverno: 4 policy engine controllers
# - cnpg-system: CloudNative PostgreSQL operator

# Current cluster resource usage (verified):
kubectl top nodes
# Total CPU: ~1.2 cores, Total Memory: ~11GB
```

## Operational Procedures

### User Management

#### Add New User
1. Edit `inventory/group_vars/all/users.yaml`
2. Add user configuration:
```yaml
users:
  - name: "newuser"
    password: "$6$encrypted_password_hash"
    groups: ["dtln_admins", "sudo"]
    scope: ["ssh_user", "wireguard"]
    wireguard_ip: "10.30.10.15"
    ssh_keys:
      - "ssh-ed25519 AAAAB3... user@hostname"
```
3. Deploy changes:
```bash
ansible-playbook --vault-password-file ~/.ansible/vault-metis \
  playbooks/update_users.yml
```

#### Generate WireGuard Config
User configuration is automatically generated in `/etc/wireguard/clients/` on the router.

**WireGuard Server Configuration** (Router at `10.20.22.11`):
```ini
[Interface]
Address = 10.30.10.1/24
ListenPort = 51820
PrivateKey = <server-private-key>

[Peer] # Daniel Hladik
PublicKey = <user-public-key>
AllowedIPs = 10.30.10.11/32
Endpoint = 10.20.22.11:51820

[Peer] # Noel Pach
PublicKey = <user-public-key>
AllowedIPs = 10.30.10.12/32
Endpoint = 10.20.22.11:51820
```

**Client Configuration Generation**:
Each user receives a configuration file at `/etc/wireguard/clients/<username>.conf`:
```ini
[Interface]
PrivateKey = <user-private-key>
Address = 10.30.10.X/32  # Unique IP per user

[Peer]
PublicKey = <server-public-key>
Endpoint = 10.20.22.11:51820
AllowedIPs = 10.135.0.0/24, 10.30.10.0/24
PersistentKeepalive = 25
```

**User IP Assignments** (From Live Configuration):
- Daniel Hladik: `10.30.10.11/32` (daniel_hladik@datalan.sk)
- Noel Pach: `10.30.10.12/32` (noel_pach@datalan.sk)
- Additional users: `10.30.10.13-20/32` (as configured in `users.yaml`)

**Note**: VPN connects to cluster network `10.135.0.0/24` (actual deployed network)

**Configuration Distribution**:
1. Configurations are generated automatically during user provisioning
2. Retrieve user configs from router: `scp router:/etc/wireguard/clients/<username>.conf`
3. Share configuration files securely with users via encrypted channels

### Cluster Maintenance

#### Update Kubernetes Version
1. Edit `inventory/group_vars/all/rke2.yaml`:
```yaml
rke2_version: "v1.33.0+rke2r1"
```
2. Run update playbook:
```bash
ansible-playbook --vault-password-file ~/.ansible/vault-metis \
  playbooks/deploy_rke2_cluster.yaml --tags update
```

#### Backup Procedures
- **etcd**: Automatically backed up by RKE2 to S3
- **Longhorn**: Scheduled backups to S3 storage
- **Application data**: Configure per-application backup strategies

#### Certificate Management
```bash
# Check certificate status
kubectl get certificates -A

# Force certificate renewal
kubectl delete certificate <cert-name> -n <namespace>
# cert-manager will automatically recreate
```

### Monitoring and Observability

#### Cluster Health Checks
```bash
# Check node status
kubectl get nodes -o wide

# Check resource usage
kubectl top nodes
kubectl top pods -A

# Check cluster events
kubectl get events --sort-by='.lastTimestamp' -A

# Check critical system pods
kubectl get pods -n kube-system
kubectl get pods -n longhorn-system
kubectl get pods -n cattle-system
```

#### Storage Monitoring
```bash
# Check Longhorn volumes
kubectl get volumes -n longhorn-system

# Access Longhorn UI
kubectl port-forward -n longhorn-system svc/longhorn-frontend 8080:80
# Access http://localhost:8080
```

#### Network Monitoring
```bash
# Check MetalLB status
kubectl get configmap config -n metallb-system -o yaml

# Check LoadBalancer services
kubectl get svc --field-selector spec.type=LoadBalancer -A

# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
```

### Security Operations

#### Security Hardening Verification
```bash
# Check AppArmor status
ansible all -i inventory/hosts.yml -m shell \
  -a "sudo aa-status" --vault-password-file ~/.ansible/vault-metis

# Verify SSH configuration
ansible all -i inventory/hosts.yml -m shell \
  -a "sudo sshd -T | grep -E '(PermitRootLogin|PasswordAuthentication|MaxAuthTries)'" \
  --vault-password-file ~/.ansible/vault-metis

# Check firewall rules
ansible all -i inventory/hosts.yml -m shell \
  -a "sudo iptables -L" --vault-password-file ~/.ansible/vault-metis
```

#### RBAC Management
```bash
# List cluster roles
kubectl get clusterroles

# Check user permissions
kubectl auth can-i --list --as=system:serviceaccount:namespace:sa-name

# Create namespace-specific RBAC
kubectl create namespace myapp
kubectl create serviceaccount myapp-sa -n myapp
kubectl create rolebinding myapp-admin --clusterrole=admin --serviceaccount=myapp:myapp-sa -n myapp
```

### Disaster Recovery

#### Cluster Recovery Procedures
1. **etcd Recovery**:
```bash
# List available backups
rke2 etcd-snapshot list

# Restore from backup
rke2 etcd-snapshot restore snapshot-name
```

2. **Node Recovery**:
```bash
# Drain node for maintenance
kubectl drain <node-name> --ignore-daemonsets --force

# Remove failed node
kubectl delete node <node-name>

# Re-deploy node
ansible-playbook --vault-password-file ~/.ansible/vault-metis \
  -l <node-name> playbooks/deploy_rke2_cluster.yaml
```

3. **Storage Recovery**:
   - Use Longhorn UI to restore volumes from S3 backups
   - Restore from snapshot or backup as needed

## Troubleshooting

### Common Issues

#### Node Not Ready
```bash
# Check node status
kubectl describe node <node-name>

# Check RKE2 service
sudo systemctl status rke2-server  # or rke2-agent
sudo journalctl -u rke2-server -f

# Check container runtime
sudo systemctl status containerd
```

#### Pod Scheduling Issues
```bash
# Check node resources
kubectl describe node <node-name>

# Check pod requirements
kubectl describe pod <pod-name>

# Check taints and tolerations
kubectl get nodes -o json | jq '.items[].spec.taints'
```

#### Network Connectivity Problems
```bash
# Check CNI pods
kubectl get pods -n kube-system | grep -E "(flannel|canal)"

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Check network policies
kubectl get networkpolicies -A
```

#### WireGuard VPN Issues
```bash
# Check WireGuard service status on router
ssh router 'sudo systemctl status wg-quick@wg0'

# View WireGuard interface status
ssh router 'sudo wg show'

# Check connected peers
ssh router 'sudo wg show wg0 peers'

# Monitor WireGuard logs
ssh router 'sudo journalctl -u wg-quick@wg0 -f'

# Test VPN connectivity from client
ping 10.135.0.1   # Router internal IP (actual network)
ping 10.135.0.11  # Master node (actual IP)

# Restart WireGuard service if needed
ssh router 'sudo systemctl restart wg-quick@wg0'
```

#### Storage Issues
```bash
# Check Longhorn manager logs
kubectl logs -n longhorn-system -l app=longhorn-manager

# Check volume status
kubectl get pv
kubectl get pvc -A

# Check storage classes
kubectl get storageclass
```

### Log Analysis

#### System Logs
```bash
# RKE2 server logs
sudo journalctl -u rke2-server --since "1 hour ago"

# RKE2 agent logs
sudo journalctl -u rke2-agent --since "1 hour ago"

# Containerd logs
sudo journalctl -u containerd --since "1 hour ago"
```

#### Application Logs
```bash
# Pod logs
kubectl logs <pod-name> -c <container-name>

# Previous container logs
kubectl logs <pod-name> --previous

# Stream logs
kubectl logs -f deployment/<deployment-name>
```

### Performance Tuning

#### Node Optimization
```bash
# Check node resource allocation
kubectl describe node <node-name> | grep -A 10 "Allocated resources"

# Optimize kubelet settings (if needed)
sudo vim /etc/rancher/rke2/config.yaml
# Add kubelet-arg options
```

#### Storage Performance
```bash
# Check disk I/O
iostat -x 1 10

# Monitor Longhorn performance
kubectl top pods -n longhorn-system

# Adjust Longhorn settings via UI or kubectl
```

## Automation and CI/CD

### GitOps Workflow
1. **Development**: Work in feature branches
2. **Testing**: Validate changes in lab environment
3. **Review**: Merge request review process
4. **Deployment**: Automated deployment via CI/CD
5. **Monitoring**: Drift detection and alerting

### CI/CD Pipeline Integration
```yaml
# Example GitLab CI pipeline
stages:
  - validate
  - deploy
  - verify

validate:
  script:
    - ansible-playbook --check playbooks/deploy_rke2_cluster.yaml

deploy:
  script:
    - ansible-playbook playbooks/deploy_rke2_cluster.yaml
  only:
    - main

verify:
  script:
    - kubectl get nodes
    - kubectl get pods -A
```

## Best Practices

### Security
- Regularly update node OS and container images
- Use network policies for pod-to-pod communication
- Implement pod security standards
- Regular security scanning of container images
- Rotate certificates and secrets regularly

### Operations
- Monitor resource usage and plan capacity
- Implement proper backup and recovery procedures
- Use infrastructure as code principles
- Document all manual changes
- Regular cluster health checks

### Performance
- Set appropriate resource requests and limits
- Use node affinity and anti-affinity rules
- Monitor and optimize storage performance
- Regular performance testing

## Support and Escalation

### Internal Support
- **Primary Contact**: martin_dulovic@datalan.sk
- **Documentation**: This guide and internal wiki
- **Team Communication**: Internal Slack/Teams channels

### External Support
- **RKE2**: Rancher support channels
- **Longhorn**: GitHub issues and community
- **Proxmox**: Official support forums

### Emergency Procedures
1. **Assess Impact**: Determine scope and urgency
2. **Immediate Action**: Stabilize critical services
3. **Communication**: Notify stakeholders
4. **Resolution**: Implement fix and verify
5. **Post-Mortem**: Document lessons learned

---

*This DevOps guide provides comprehensive operational procedures for the Datalan RKE2 Kubernetes Platform. Keep this documentation updated as the platform evolves.*