# ORFEAS Linux Setup - Decision Flowchart & Quick Start

## 🚀 What's Your Situation?

### Flowchart

```
START: Do you have Linux installed?
│
├─ YES → Go to: "Linux System Ready"
│
└─ NO → Do you want dual-boot (keep Windows)?
    │
    ├─ YES → Go to: "Set Up Dual Boot"
    │
    └─ NO → Do you have another computer for Linux?
        │
        ├─ YES → Go to: "Remote Linux Setup"
        │
        └─ NO → Consider: VMware/VirtualBox (Limited GPU support)
```

---

## 📋 Path 1: Set Up Dual Boot (Windows + Linux)

**Time Required:** 2-3 hours (includes backup, download, install)

### Quick Checklist

- [ ] Back up all important data (USB external drive)
- [ ] Have Linux ISO downloaded (~3.3GB for Ubuntu 22.04)
- [ ] Have bootable USB ready (8GB+)
- [ ] Disable Windows Fast Startup
- [ ] Have 100GB free space on disk

### Steps

1. **Read:** `LINUX_INSTALLATION_GUIDE.md` (5 min)
2. **Backup data** (30-60 min)
3. **Shrink Windows partition** (5-30 min)
4. **Create bootable USB** (10 min)
5. **Install Ubuntu** (20-40 min)
6. **Install GPU drivers** (15 min)
7. **Install Docker** (10 min)
8. **Deploy ORFEAS** (10-25 min)

### After Dual Boot is Ready

→ Skip to "**Path 3: Deploy ORFEAS**"

---

## 📋 Path 2: Remote Linux Setup (Deploy from Windows to Linux Server)

**Time Required:** 30-60 minutes (deployment only)

### Prerequisites

- Linux system already running (Ubuntu 22.04 LTS)
- SSH access from Windows to Linux
- NVIDIA GPU on Linux system
- 100GB+ free storage

### Quick Steps

```powershell
# From Windows PowerShell:
.\deploy_linux_fixed.ps1 -RemoteHost "user@192.168.1.100" -Action Initialize

# Or manual:
ssh user@192.168.1.100
cd /opt/orfeas
./deploy_linux.sh
```

### After Deployment Completes

→ Verify: `curl http://192.168.1.100:5000/api/health`

---

## 📋 Path 3: Deploy ORFEAS (Linux System Already Ready)

**Time Required:** 10-25 minutes (deployment only)

### Prerequisites

- Linux system running (Ubuntu 22.04+)
- NVIDIA driver installed
- Docker & NVIDIA Container Toolkit installed
- 100GB+ free storage (for models + outputs)

### Quick Steps

**Option A: Automated (Recommended)**

```bash
cd /opt/orfeas
chmod +x deploy_linux.sh
./deploy_linux.sh
# Fully automated - takes 5-25 minutes
```

**Option B: Manual Docker Compose**

```bash
cd /opt/orfeas
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f backend
```

### After Deployment

```bash
# Verify health
curl http://localhost:5000/api/health

# Test 3D generation
python3 << 'EOF'
import requests
from pathlib import Path

img = Path('backend/test_images/test_image.png')
with open(img, 'rb') as f:
    resp = requests.post('http://localhost:5000/api/generate/3d', files={'image': f})
    print(f"Status: {resp.status_code}")
    print(resp.json())
EOF

# Result: Should see .stl mesh file with true 3D geometry
```

---

## 🎯 Choose Your Path

### 🟢 "I'm starting from scratch"

```
1. Read: LINUX_INSTALLATION_GUIDE.md
2. Follow: Steps 1-9 (Dual boot setup)
3. Jump to: Path 3 deployment
```

### 🟢 "I have Linux but need to deploy ORFEAS"

```
1. Read: LINUX_DEPLOYMENT_GUIDE.md
2. Run: ./deploy_linux.sh
3. Verify: curl http://localhost:5000/api/health
```

### 🟢 "I'm deploying from Windows to remote Linux"

```
1. Run: .\deploy_linux_fixed.ps1 -RemoteHost "user@server" -Action Initialize
2. Verify: curl http://server:5000/api/health
```

### 🟡 "I have Docker already running"

```
1. Verify: docker ps
2. Run: docker-compose up -d
3. Verify: curl http://localhost:5000/api/health
```

---

## 📚 Reading Guide

### For Complete Beginners (Do all of these in order)

1. This file (Decision flowchart)
2. `LINUX_INSTALLATION_GUIDE.md` (Install Linux)
3. `LINUX_DEPLOYMENT_GUIDE.md` (Deploy ORFEAS)
4. `LINUX_QUICK_REFERENCE.sh` (Save for reference)

### For Linux Users (Skip installation)

1. `LINUX_DEPLOYMENT_GUIDE.md` (Setup & deploy)
2. `LINUX_QUICK_REFERENCE.sh` (Commands)
3. `CUDA_MEMORY_OPTIMIZATION.md` (If issues occur)

### For Advanced Users

1. `LINUX_QUICK_REFERENCE.sh` (Copy commands)
2. `CUDA_MEMORY_OPTIMIZATION.md` (Understand memory)
3. `deploy_linux.sh` (Review automation)

### For Troubleshooting Only

1. `LINUX_QUICK_REFERENCE.sh` → "TROUBLESHOOTING" section
2. `CUDA_MEMORY_OPTIMIZATION.md` → "Troubleshooting Memory Issues"
3. `LINUX_DEPLOYMENT_GUIDE.md` → Search for your issue

---

## 🔍 System Requirements Checklist

### Hardware

- [ ] NVIDIA GPU (RTX 3090 or compatible with 24GB+ VRAM)
- [ ] CPU with 8+ cores
- [ ] 32GB+ system RAM
- [ ] 100GB+ free SSD space (for OS, models, outputs)

### Software (After Linux Install)

- [ ] Ubuntu 22.04 LTS or equivalent Linux
- [ ] NVIDIA driver 535+ installed
- [ ] Docker 24.0+ installed
- [ ] NVIDIA Container Toolkit installed
- [ ] curl command available
- [ ] python3 installed (for testing)

### Verification Commands

```bash
# Run these BEFORE deploying ORFEAS

# Check GPU
nvidia-smi
# Expected: Driver Version: 535+, CUDA Version: 12.1

# Check Docker
docker --version
# Expected: Docker version 24.0+

# Check NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi
# Expected: GPU visible inside container

# Check storage
df -h /
# Expected: 100GB+ available

# Check network
curl -I https://www.google.com
# Expected: HTTP/1.1 200 or 301
```

---

## ⏱️ Time Estimates by Path

### Path 1: Dual Boot from Scratch

| Step | Time |
|------|------|
| Backup data | 30-60 min |
| Partition disk | 5-30 min |
| Download & create USB | 20-40 min |
| Install Ubuntu | 20-40 min |
| Install drivers | 15 min |
| Install Docker | 10 min |
| Deploy ORFEAS | 15-25 min |
| **TOTAL** | **2-3 hours** |

### Path 2: Remote Linux (Already has OS)

| Step | Time |
|------|------|
| Read deployment guide | 5 min |
| Run deployment script | 10-25 min |
| Verify & test | 5 min |
| **TOTAL** | **20-35 min** |

### Path 3: Local Linux (Already has OS)

| Step | Time |
|------|------|
| Read quick reference | 3 min |
| Run deploy_linux.sh | 10-25 min |
| Verify & test | 5 min |
| **TOTAL** | **20-35 min** |

---

## 🆘 If Something Goes Wrong

### During Linux Installation

→ See: `LINUX_INSTALLATION_GUIDE.md` → "Troubleshooting"

### During ORFEAS Deployment

→ See: `LINUX_DEPLOYMENT_GUIDE.md` → "Troubleshooting"

### GPU/Memory Issues

→ See: `CUDA_MEMORY_OPTIMIZATION.md` → "Troubleshooting Memory Issues"

### Quick Commands

→ See: `LINUX_QUICK_REFERENCE.sh` → "TROUBLESHOOTING"

---

## 📞 Document Quick Links

| Question | Read This |
|----------|-----------|
| How do I install Linux? | `LINUX_INSTALLATION_GUIDE.md` |
| How do I deploy ORFEAS? | `LINUX_DEPLOYMENT_GUIDE.md` |
| Why is GPU memory failing? | `CUDA_MEMORY_OPTIMIZATION.md` |
| What commands do I need? | `LINUX_QUICK_REFERENCE.sh` |
| What was delivered? | `DELIVERY_SUMMARY.md` |
| Where do I start? | `INDEX.md` (you are here!) |

---

## ✅ Success Criteria

**After deployment, you should have:**

- ✅ Linux system running (Ubuntu 22.04+)
- ✅ NVIDIA driver working (nvidia-smi shows GPU)
- ✅ Docker running (docker ps works)
- ✅ ORFEAS backend running (curl health check passes)
- ✅ Model loaded (logs show "SUCCESS")
- ✅ 3D generation working (test generates .stl file)
- ✅ True 3D output (not 2.5D heightfield)

**To verify everything:**

```bash
# 1. GPU ready?
nvidia-smi

# 2. Docker ready?
docker ps

# 3. ORFEAS ready?
curl http://localhost:5000/api/health

# 4. 3D generation works?
python3 backend/test_generation.py

# Expected: /outputs/mesh_*.stl file with ~600K triangles
```

---

## 🚀 Next Steps

**Choose Your Path:**

1. **Never installed Linux?**
   → Start: `LINUX_INSTALLATION_GUIDE.md` (Step 1)

2. **Have Linux, need ORFEAS?**
   → Start: `LINUX_DEPLOYMENT_GUIDE.md` (Step 1)

3. **Have everything, just deploy?**
   → Start: `./deploy_linux.sh`

4. **Remote deployment from Windows?**
   → Start: `.\deploy_linux_fixed.ps1 -RemoteHost "user@server" -Action Initialize`

---

**Status:** ✅ Ready to proceed with your chosen path!

**All documents available in:** `c:\Users\johng\Documents\oscar\`
