# ORFEAS AI - Enterprise Deployment Guide

**Document:** Production deployment, scaling, monitoring, and operations guide
**Version:** 2.1 (Enterprise Edition)
**Last Updated:** October 2025

## Overview

This guide covers complete deployment strategies for ORFEAS AI systems.

---

## Pre-Deployment Checklist

### System Requirements

- **Minimum:** RTX 3090 (24GB VRAM), 32GB RAM, 500GB SSD
- **Recommended:** 2x RTX 3090, 64GB RAM, 1TB NVMe SSD
- **Network:** 1Gbps+ Ethernet connection

### Pre-Flight Checks

```powershell

## Windows PowerShell - Pre-deployment validation

function Test-DeploymentReadiness {
    Write-Host "[DEPLOY] Starting pre-flight checks..." -ForegroundColor Blue

    # Check Python version

    $pythonVersion = python --version 2>&1
    if ($pythonVersion -notmatch "3\.(10|11|12)") {
        Write-Host "✗ Python 3.10+ required, found: $pythonVersion" -ForegroundColor Red
        return $false
    }
    Write-Host "✓ Python version OK: $pythonVersion" -ForegroundColor Green

    # Check GPU access

    $gpuCheck = nvidia-smi 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ GPU not accessible" -ForegroundColor Red
        return $false
    }
    Write-Host "✓ GPU accessible" -ForegroundColor Green

    # Check required packages

    $requiredPkgs = @('flask', 'torch', 'transformers', 'requests')
    foreach ($pkg in $requiredPkgs) {
        python -c "import $pkg" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Missing package: $pkg" -ForegroundColor Red
            return $false
        }
    }
    Write-Host "✓ All required packages installed" -ForegroundColor Green

    # Check disk space

    $diskFree = (Get-Volume | Where-Object {$_.DriveLetter -eq 'C'}).SizeRemaining / 1GB
    if ($diskFree -lt 100) {
        Write-Host "✗ Insufficient disk space: ${diskFree}GB free (100GB required)" -ForegroundColor Red
        return $false
    }
    Write-Host "✓ Disk space OK: ${diskFree}GB free" -ForegroundColor Green

    Write-Host "[DEPLOY] ✓ All checks passed!" -ForegroundColor Green
    return $true
}

Test-DeploymentReadiness

```text

---

## Local Development Setup

### 5-Minute Startup

```powershell

## 1. Clone repository with submodules

git clone --recursive https://github.com/your-org/orfeas.git
cd orfeas

## 2. Install dependencies

pip install -r backend/requirements.txt

## 3. Download models (one-time, ~30GB)

python backend/download_models.py

## 4. Start backend

cd backend
python main.py  # Runs on http://127.0.0.1:5000

## 5. In another terminal, start frontend

cd frontend
python -m http.server 8000

```text

### Environment Configuration

```bash

## .env - Development environment

FLASK_ENV=development
FLASK_DEBUG=1
DEVICE=cuda
XFORMERS_DISABLED=1
GPU_MEMORY_LIMIT=0.8
MAX_CONCURRENT_JOBS=3
LOG_LEVEL=DEBUG
ENABLE_MONITORING=true
LOCAL_LLM_ENABLED=true
LOCAL_LLM_ENDPOINT=http://localhost:11434

```text

---

## Docker Deployment

### Single-Container Deployment

```dockerfile

## Dockerfile - Production-ready image

FROM nvidia/cuda:12.0.1-runtime-ubuntu22.04

WORKDIR /app

## Install system dependencies

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

## Copy application

COPY backend/ /app/backend/
COPY Hunyuan3D-2.1/ /app/Hunyuan3D-2.1/

## Install Python dependencies

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

## Set environment

ENV FLASK_APP=backend/main.py
ENV DEVICE=cuda
ENV XFORMERS_DISABLED=1
ENV GPU_MEMORY_LIMIT=0.8

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "backend.main:app"]

```text

### Docker Compose Stack

```yaml

## docker-compose.yml - Complete 7-service stack

version: '3.8'

services:

  # Backend API

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:

      - "5000:5000"

    environment:
      DEVICE: cuda
      GPU_MEMORY_LIMIT: 0.8
      MAX_CONCURRENT_JOBS: 3
    volumes:

      - ./backend:/app/backend
      - ./models:/app/models

    deploy:
      resources:
        reservations:
          devices:

            - driver: nvidia

              count: 1
              capabilities: [gpu]
    networks:

      - orfeas-network

    restart: unless-stopped

  # Frontend Web Server

  frontend:
    image: nginx:alpine
    ports:

      - "8080:80"

    volumes:

      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf:ro

    depends_on:

      - backend

    networks:

      - orfeas-network

    restart: unless-stopped

  # Redis Cache

  redis:
    image: redis:7-alpine
    ports:

      - "6379:6379"

    volumes:

      - redis_data:/data

    networks:

      - orfeas-network

    restart: unless-stopped

  # Prometheus Monitoring

  prometheus:
    image: prom/prometheus:latest
    ports:

      - "9090:9090"

    volumes:

      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus

    command:

      - '--config.file=/etc/prometheus/prometheus.yml'

    networks:

      - orfeas-network

    restart: unless-stopped

  # Grafana Dashboard

  grafana:
    image: grafana/grafana:latest
    ports:

      - "3000:3000"

    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:

      - grafana_data:/var/lib/grafana

    depends_on:

      - prometheus

    networks:

      - orfeas-network

    restart: unless-stopped

  # GPU Metrics Exporter

  gpu-exporter:
    image: nvidia/cuda:12.0.1-runtime-ubuntu22.04
    command: ["python", "-m", "nvidia_ml_py3", "--port", "9445"]
    ports:

      - "9445:9445"

    deploy:
      resources:
        reservations:
          devices:

            - driver: nvidia

              count: all
              capabilities: [gpu]
    networks:

      - orfeas-network

    restart: unless-stopped

  # Local LLM (Ollama)

  ollama:
    image: ollama/ollama:latest
    ports:

      - "11434:11434"

    environment:
      OLLAMA_NUM_GPU: 1
      OLLAMA_MODELS: ./models
    volumes:

      - ollama_data:/root/.ollama

    deploy:
      resources:
        reservations:
          devices:

            - driver: nvidia

              count: 1
              capabilities: [gpu]
    networks:

      - orfeas-network

    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
  ollama_data:

networks:
  orfeas-network:
    driver: bridge

```text

### Docker Deployment Commands

```powershell

## Build and run

docker-compose up -d

## Check logs

docker-compose logs -f backend

## Health check

docker-compose ps

## Stop

docker-compose down

## Clean up

docker-compose down -v  # Remove volumes too

```text

---

## Kubernetes Deployment

### Helm Chart Structure

```yaml

## helm/orfeas/Chart.yaml

apiVersion: v2
name: orfeas
description: ORFEAS AI 2D3D Studio
version: 2.1.0
appVersion: "2.1"

```text

### Kubernetes Deployment Manifest

```yaml

## k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: orfeas-backend
  namespace: orfeas
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: orfeas-backend
  template:
    metadata:
      labels:
        app: orfeas-backend
    spec:

      # GPU scheduling

      nodeSelector:
        accelerator: nvidia-gpu

      # Pod scheduling rules

      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:

          - weight: 100

            podAffinityTerm:
              labelSelector:
                matchExpressions:

                - key: app

                  operator: In
                  values:

                  - orfeas-backend

              topologyKey: kubernetes.io/hostname

      containers:

      - name: backend

        image: your-registry/orfeas:2.1
        imagePullPolicy: IfNotPresent
        ports:

        - containerPort: 5000

        # Resource requests/limits

        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "24Gi"
            cpu: "8"
            nvidia.com/gpu: "1"

        # Environment variables

        env:

        - name: DEVICE

          value: "cuda"

        - name: GPU_MEMORY_LIMIT

          value: "0.8"

        - name: MAX_CONCURRENT_JOBS

          value: "3"

        # Health checks

        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        # Volume mounts

        volumeMounts:

        - name: models

          mountPath: /app/models

        - name: cache

          mountPath: /app/cache

      volumes:

      - name: models

        persistentVolumeClaim:
          claimName: orfeas-models

      - name: cache

        emptyDir: {}

---

## k8s/service.yaml

apiVersion: v1
kind: Service
metadata:
  name: orfeas-backend
  namespace: orfeas
spec:
  type: LoadBalancer
  selector:
    app: orfeas-backend
  ports:

  - protocol: TCP

    port: 5000
    targetPort: 5000

---

## k8s/pvc.yaml

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: orfeas-models
  namespace: orfeas
spec:
  accessModes:

    - ReadWriteMany

  storageClassName: nfs-slow
  resources:
    requests:
      storage: 100Gi

```text

---

## Cloud Platforms

### AWS Deployment

```python

## backend/aws_deployment.py

import boto3
import json

class AWSDeploymentManager:
    """Manage ORFEAS on AWS."""

    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)

    def launch_gpu_instance(self):
        """Launch GPU EC2 instance."""
        response = self.ec2.run_instances(
            ImageId='ami-0c55b159cbfafe1f0',  # Deep Learning AMI
            InstanceType='g4dn.12xlarge',  # 4x T4 GPUs
            MinCount=1,
            MaxCount=1,
            KeyName='orfeas-key',
            SecurityGroups=['orfeas-sg'],
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': 500,
                        'VolumeType': 'gp3',
                        'DeleteOnTermination': True
                    }
                }
            ]
        )

        instance_id = response['Instances'][0]['InstanceId']
        print(f"[AWS] Instance launched: {instance_id}")
        return instance_id

    def upload_models_to_s3(self, local_dir, bucket, prefix='models'):
        """Upload models to S3."""
        import os
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                s3_key = f"{prefix}/{file}"
                self.s3.upload_file(local_path, bucket, s3_key)
                print(f"[AWS] Uploaded: s3://{bucket}/{s3_key}")

```text

### Azure Deployment

```python

## backend/azure_deployment.py

from azure.identity import DefaultAzureCredential
from azure.containerregistry import ContainerRegistryClient

class AzureDeploymentManager:
    """Manage ORFEAS on Azure."""

    def __init__(self, registry_url):
        self.registry_url = registry_url
        self.client = ContainerRegistryClient(
            registry_url,
            credential=DefaultAzureCredential()
        )

    def push_image_to_registry(self, image_name, image_tag):
        """Push Docker image to Azure Container Registry."""
        import subprocess

        full_image = f"{self.registry_url}/{image_name}:{image_tag}"
        subprocess.run([
            'docker', 'tag',
            f"{image_name}:{image_tag}",
            full_image
        ])
        subprocess.run(['docker', 'push', full_image])
        print(f"[AZURE] Image pushed: {full_image}")

```text

---

## CI/CD Pipelines

### GitHub Actions Pipeline

```yaml

## .github/workflows/deploy.yml

name: Deploy ORFEAS

on:
  push:
    branches: [main, production]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:

    - uses: actions/checkout@v3

    - name: Set up Python

      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies

      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-cov

    - name: Run tests

      run: |
        pytest backend/tests/ -m unit --cov=backend

    - name: Upload coverage

      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:

    - uses: actions/checkout@v3

    - name: Log in to Container Registry

      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push Docker image

      uses: docker/build-push-action@v4
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        labels: version=${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/production'

    steps:

    - uses: actions/checkout@v3

    - name: Deploy to Kubernetes

      run: |
        kubectl set image deployment/orfeas-backend \
          backend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

```text

---

## Monitoring & Observability

### Prometheus Configuration

```yaml

## prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:

    - static_configs:
        - targets: []

rule_files:

  - 'alerts.yml'

scrape_configs:

  - job_name: 'orfeas'

    static_configs:

      - targets: ['localhost:5000']

  - job_name: 'gpu-metrics'

    static_configs:

      - targets: ['localhost:9445']

  - job_name: 'redis'

    static_configs:

      - targets: ['localhost:6379']

```text

### Alert Rules

```yaml

## alerts.yml

groups:

  - name: orfeas_alerts

    rules:

    - alert: HighGPUMemoryUsage

      expr: gpu_memory_used / gpu_memory_total > 0.9
      for: 5m
      annotations:
        summary: "GPU memory usage exceeds 90%"

    - alert: HighLatency

      expr: request_duration_seconds > 30
      for: 5m
      annotations:
        summary: "Request latency exceeds 30 seconds"

    - alert: JobQueueBacklog

      expr: job_queue_length > 50
      for: 10m
      annotations:
        summary: "Job queue has more than 50 items"

```text

---

## Scaling & Load Balancing

### Nginx Configuration

```text

## nginx.conf

upstream backend {
    server backend-1:5000 weight=1 max_fails=3 fail_timeout=30s;
    server backend-2:5000 weight=1 max_fails=3 fail_timeout=30s;
    server backend-3:5000 weight=1 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.orfeas.ai;

    # Rate limiting

    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

```text

---

## Disaster Recovery

### Backup Strategy

```python

## backend/backup_manager.py

import os
import shutil
from datetime import datetime

class BackupManager:
    """Handle backup and recovery operations."""

    @staticmethod
    def backup_models(source_dir, backup_dir):
        """Backup models to secondary storage."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'models_{timestamp}')

        shutil.copytree(source_dir, backup_path)
        print(f"[BACKUP] Models backed up to {backup_path}")

        return backup_path

    @staticmethod
    def restore_models(backup_path, target_dir):
        """Restore models from backup."""
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        shutil.copytree(backup_path, target_dir)
        print(f"[RESTORE] Models restored from {backup_path}")

```text

---

## Production Hardening

### Security Checklist

- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Enable authentication/authorization
- [ ] Set up rate limiting
- [ ] Enable logging and monitoring
- [ ] Configure automatic backups
- [ ] Set up disaster recovery
- [ ] Perform security audit
- [ ] Enable intrusion detection
- [ ] Set up DDoS protection

### Production .env

```bash
FLASK_ENV=production
DEBUG=0
DEVICE=cuda
GPU_MEMORY_LIMIT=0.8
MAX_CONCURRENT_JOBS=3
LOG_LEVEL=WARNING
ENABLE_HTTPS=true
SSL_CERT_PATH=/etc/ssl/orfeas.crt
SSL_KEY_PATH=/etc/ssl/orfeas.key

```text

---

This deployment guide covers all major deployment scenarios from development through enterprise production environments.
