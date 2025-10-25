# 🚀 ORFEAS AI - Kubernetes Deployment Guide

**Version:** 1.0.0
**Last Updated:** October 25, 2025

---

## 📋 Overview

This directory contains Kubernetes manifests for deploying ORFEAS AI with:

- **Auto-scaling** - 3-10 replicas based on CPU/GPU/queue metrics
- **GPU Support** - NVIDIA GPU scheduling
- **High Availability** - Multi-replica deployment with rolling updates
- **Load Balancing** - Service with session affinity
- **Resource Limits** - CPU, memory, and GPU quotas
- **Network Policies** - Secure pod communication
- **Persistent Storage** - Model cache and outputs

---

## 🗂️ Files

```text
k8s/
├── namespace.yaml      # Namespace, quotas, limits, network policies
├── configmap.yaml      # Configuration and secrets
├── deployment.yaml     # Main backend deployment + PVCs
├── service.yaml        # LoadBalancer and internal services
├── hpa.yaml           # HorizontalPodAutoscaler
└── README.md          # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- NVIDIA GPU operator installed
- StorageClass: `fast-ssd` and `standard`
- Prometheus Adapter (for custom metrics)

### Deploy

```bash
# Create namespace and resources
kubectl apply -f k8s/namespace.yaml

# Create secrets (update first!)
kubectl apply -f k8s/configmap.yaml

# Deploy backend
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Verify deployment
kubectl get pods -n orfeas-ai
kubectl get svc -n orfeas-ai
kubectl get hpa -n orfeas-ai
```

---

## 📊 Auto-Scaling

### Metrics

The HPA scales based on:

1. **CPU Utilization** - Target: 70%
2. **Memory Utilization** - Target: 80%
3. **Queue Depth** - Target: 5 jobs/pod
4. **GPU Utilization** - Target: 75%

### Scaling Behavior

**Scale Up:**

- Fast response: Max 50% or 2 pods per minute
- No stabilization window

**Scale Down:**

- Conservative: Max 10% or 1 pod per minute
- 5-minute stabilization window

### Example

```bash
# Check HPA status
kubectl get hpa orfeas-backend-hpa -n orfeas-ai

# Output:
# NAME                   REFERENCE                     TARGETS                        MINPODS   MAXPODS   REPLICAS
# orfeas-backend-hpa     Deployment/orfeas-backend     65%/70% (CPU), 72%/75% (GPU)   3         10        5

# Watch scaling events
kubectl get hpa orfeas-backend-hpa -n orfeas-ai -w
```

---

## 🖥️ GPU Configuration

### Node Labeling

```bash
# Label GPU nodes
kubectl label nodes node1 nvidia.com/gpu=true
kubectl label nodes node2 nvidia.com/gpu=true

# Verify
kubectl get nodes -l nvidia.com/gpu=true
```

### GPU Resources

Each pod requests:

- **GPU:** 1 NVIDIA GPU
- **VRAM:** 24GB (RTX 3090 or equivalent)
- **CPU:** 4 cores (request), 8 cores (limit)
- **Memory:** 16Gi (request), 32Gi (limit)

### Verify GPU Allocation

```bash
# Check GPU allocation
kubectl describe node node1 | grep nvidia.com/gpu

# Check pod GPU
kubectl exec -n orfeas-ai orfeas-backend-xxxxx -- nvidia-smi
```

---

## 💾 Persistent Storage

### Volume Claims

**Model Cache (100GB SSD):**

- Fast SSD storage
- ReadWriteMany access
- Shared across pods
- Stores downloaded AI models

**Outputs (500GB):**

- Standard storage
- ReadWriteMany access
- Stores generated 3D models
- Can be backed by S3/NFS

### Verify Storage

```bash
# Check PVCs
kubectl get pvc -n orfeas-ai

# Check PVC usage
kubectl exec -n orfeas-ai orfeas-backend-xxxxx -- df -h /app/models
kubectl exec -n orfeas-ai orfeas-backend-xxxxx -- df -h /app/backend/outputs
```

---

## 🔧 Configuration

### Update ConfigMap

```bash
# Edit configuration
kubectl edit configmap orfeas-config -n orfeas-ai

# Or apply changes
kubectl apply -f k8s/configmap.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment/orfeas-backend -n orfeas-ai
```

### Update Secrets

```bash
# Update secrets
kubectl create secret generic orfeas-secrets \
  --from-literal=redis-password=your-password \
  --from-literal=database-password=your-db-password \
  --from-literal=api-key=your-api-key \
  --namespace=orfeas-ai \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods
kubectl rollout restart deployment/orfeas-backend -n orfeas-ai
```

---

## 🔍 Monitoring

### Pod Status

```bash
# Get all pods
kubectl get pods -n orfeas-ai

# Describe pod
kubectl describe pod orfeas-backend-xxxxx -n orfeas-ai

# Pod logs
kubectl logs -n orfeas-ai orfeas-backend-xxxxx -f

# Previous logs (if crashed)
kubectl logs -n orfeas-ai orfeas-backend-xxxxx --previous
```

### Service Health

```bash
# Get services
kubectl get svc -n orfeas-ai

# Get LoadBalancer IP
kubectl get svc orfeas-backend -n orfeas-ai -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Test health endpoint
curl http://<LOADBALANCER_IP>/health
```

### Metrics

```bash
# HPA metrics
kubectl get hpa orfeas-backend-hpa -n orfeas-ai

# Pod metrics
kubectl top pods -n orfeas-ai

# Node metrics
kubectl top nodes
```

---

## 🔄 Deployment Updates

### Rolling Update

```bash
# Update image
kubectl set image deployment/orfeas-backend \
  backend=orfeas/backend:v2.0.0 \
  -n orfeas-ai

# Watch rollout
kubectl rollout status deployment/orfeas-backend -n orfeas-ai

# Rollout history
kubectl rollout history deployment/orfeas-backend -n orfeas-ai
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/orfeas-backend -n orfeas-ai

# Rollback to specific revision
kubectl rollout undo deployment/orfeas-backend -n orfeas-ai --to-revision=2
```

### Blue-Green Deployment

```bash
# Deploy new version with different label
kubectl apply -f k8s/deployment-v2.yaml

# Switch traffic
kubectl patch service orfeas-backend -n orfeas-ai \
  -p '{"spec":{"selector":{"version":"v2"}}}'

# Remove old version
kubectl delete deployment orfeas-backend-v1 -n orfeas-ai
```

---

## 🐛 Troubleshooting

### Pod Not Starting

```bash
# Check pod events
kubectl describe pod orfeas-backend-xxxxx -n orfeas-ai

# Common issues:
# - ImagePullBackOff: Check image name and registry
# - CrashLoopBackOff: Check logs
# - Pending: Check resource quotas and node capacity
```

### GPU Not Detected

```bash
# Check GPU operator
kubectl get pods -n gpu-operator-resources

# Check node labels
kubectl get nodes --show-labels | grep nvidia

# Verify GPU plugin
kubectl get daemonset -n kube-system -l name=nvidia-device-plugin-daemonset
```

### Service Not Accessible

```bash
# Check service
kubectl get svc orfeas-backend -n orfeas-ai

# Check endpoints
kubectl get endpoints orfeas-backend -n orfeas-ai

# Check network policy
kubectl get networkpolicy -n orfeas-ai

# Test from inside cluster
kubectl run -n orfeas-ai test-pod --rm -it --image=curlimages/curl -- \
  curl http://orfeas-backend-internal:5000/health
```

### HPA Not Scaling

```bash
# Check HPA status
kubectl describe hpa orfeas-backend-hpa -n orfeas-ai

# Check metrics server
kubectl top nodes
kubectl top pods -n orfeas-ai

# Check Prometheus Adapter (for custom metrics)
kubectl get apiservice v1beta1.custom.metrics.k8s.io
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1
```

---

## 📈 Performance Tuning

### Resource Limits

Adjust based on workload:

```yaml
resources:
  requests:
    memory: "16Gi"  # Increase for larger models
    cpu: "4"        # Increase for more parallel processing
    nvidia.com/gpu: 1
  limits:
    memory: "32Gi"
    cpu: "8"
    nvidia.com/gpu: 1
```

### Replica Count

```bash
# Manual scaling (overrides HPA temporarily)
kubectl scale deployment orfeas-backend -n orfeas-ai --replicas=5

# Update HPA min/max
kubectl patch hpa orfeas-backend-hpa -n orfeas-ai \
  -p '{"spec":{"minReplicas":5,"maxReplicas":15}}'
```

### Node Affinity

Add to deployment for specific node types:

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node.kubernetes.io/instance-type
          operator: In
          values:
          - p3.2xlarge  # AWS GPU instance type
```

---

## 🔐 Security

### Network Policies

Restrict traffic:

- Pods can only communicate within namespace
- Monitoring namespace can scrape metrics
- Egress to Redis and external HTTPS only

### RBAC

Create ServiceAccount with limited permissions:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: orfeas-backend
  namespace: orfeas-ai
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: orfeas-backend-role
  namespace: orfeas-ai
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
```

### Pod Security

Add security context:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
    - ALL
```

---

## 📚 Additional Resources

- **Kubernetes Docs:** <https://kubernetes.io/docs/>
- **NVIDIA GPU Operator:** <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/>
- **HPA Guide:** <https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/>
- **Prometheus Adapter:** <https://github.com/kubernetes-sigs/prometheus-adapter>

---

## 🎯 Production Checklist

- [ ] Update secrets in configmap.yaml
- [ ] Configure StorageClass
- [ ] Install NVIDIA GPU operator
- [ ] Install Prometheus Adapter
- [ ] Set up monitoring (Grafana + Prometheus)
- [ ] Configure LoadBalancer/Ingress
- [ ] Set up TLS certificates
- [ ] Configure backup for PVCs
- [ ] Test auto-scaling
- [ ] Document disaster recovery

---

**Document Version:** 1.0.0
**Last Updated:** October 25, 2025
**Maintainer:** ORFEAS AI DevOps Team
