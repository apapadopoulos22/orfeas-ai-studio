# 🚀 AUTOMATED LOCAL DEPLOYMENT - USAGE GUIDE

**Project:** BOB AI v9.0
**Status:** ✅ Production Ready
**Created:** October 27, 2025

---

## 📋 OVERVIEW

Two automated deployment scripts have been created to run all deployment phases automatically:

1. **deploy_local_all_phases.py** - Cross-platform Python script
2. **deploy_local_all_phases.ps1** - Windows PowerShell script

Both scripts orchestrate 7 complete deployment phases with comprehensive logging and error handling.

---

## 🎯 QUICK START

### Option 1: Python Script (Recommended for Linux/Mac/Windows with Python)

```bash
cd /path/to/oscar
python deploy_local_all_phases.py
```

### Option 2: PowerShell Script (Windows)

```powershell
cd C:\Users\YourName\Documents\oscar
.\deploy_local_all_phases.ps1
```

---

## 📊 WHAT GETS DEPLOYED

### 7 Automated Phases

**Phase 1: Environment Verification** (1-2 minutes)

- ✅ Check Python version (3.11.9+)
- ✅ Check Docker (28.5.1+)
- ✅ Check Docker Compose (2.40.0+)
- ✅ Verify backend structure
- ✅ Check dependencies

**Phase 2: Configuration Setup** (1-2 minutes)

- ✅ Verify .env file
- ✅ Check configuration files
- ✅ Validate requirements.txt
- ✅ Prepare deployment environment

**Phase 3: Docker Build** (10-15 minutes)

- ✅ Build Docker image
- ✅ Verify image creation
- ✅ Prepare containers

**Phase 4: Services Startup** (2-5 minutes)

- ✅ Start Docker services
- ✅ Initialize containers
- ✅ Verify services running
- ✅ Check service status

**Phase 5: Automated Verification** (10-15 minutes)

- ✅ Run environment verification script
- ✅ Run component initialization tests
- ✅ Run backend initialization tests
- ✅ Run Docker verification
- ✅ Run end-to-end testing
- ✅ Run final verification checklist

**Phase 6: Health Checks** (2-3 minutes)

- ✅ Check health endpoint
- ✅ Retrieve service logs
- ✅ Verify system status

**Phase 7: Deployment Summary** (1 minute)

- ✅ Print deployment results
- ✅ Display next steps
- ✅ Create deployment log
- ✅ Show troubleshooting tips

**Total Time: ~70 minutes for first deployment**

---

## 🔧 SYSTEM REQUIREMENTS

### Minimum Requirements

- **Python:** 3.11.9+
- **Docker:** 28.5.1+
- **Docker Compose:** 2.40.0+
- **RAM:** 4 GB minimum
- **Disk Space:** 5 GB free

### Recommended

- **RAM:** 8 GB+
- **Disk Space:** 10 GB+
- **GPU:** NVIDIA GPU with CUDA 12.1 (optional)

---

## 📖 DETAILED USAGE

### Python Script

#### Basic Usage

```bash
python deploy_local_all_phases.py
```

#### With Logging

```bash
python deploy_local_all_phases.py 2>&1 | tee deployment.log
```

#### Exit Codes

- **0:** Deployment successful
- **1:** Deployment failed or incomplete

### PowerShell Script

#### Basic Usage

```powershell
.\deploy_local_all_phases.ps1
```

#### With Execution Policy (if needed)

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\deploy_local_all_phases.ps1
```

#### With Logging

```powershell
.\deploy_local_all_phases.ps1 | Tee-Object -FilePath deployment.log
```

---

## 📊 OUTPUT & LOGGING

### Real-Time Output

The script provides real-time colored output:

- 🟢 **Green (✅)** - Successful operations
- 🔴 **Red (❌)** - Failed operations
- 🟡 **Yellow (⚠️)** - Warnings
- 🔵 **Blue/Cyan** - Information messages

### Deployment Log

After completion, a `deployment_log.json` file is created with:

- Deployment timestamp
- Overall status (SUCCESS/FAILED)
- Per-phase results
- Total deployment time

### Example Log Entry

```json
{
  "timestamp": "2025-10-27T14:30:45.123456",
  "status": "SUCCESS",
  "phases": {
    "phase_1_environment": "Completed",
    "phase_2_configuration": "Completed",
    "phase_3_docker_build": "Completed",
    "phase_4_startup": "Completed",
    "phase_5_verification": "Completed",
    "phase_6_health_checks": "Completed",
    "phase_7_summary": "Completed"
  },
  "deployment_time_minutes": 1.16
}
```

---

## 🚨 TROUBLESHOOTING

### Issue: "Docker not found or not running"

**Solution:**

```bash
# Install Docker
docker --version
docker ps  # Should return something

# Start Docker service
# Windows: Use Docker Desktop
# Linux: sudo systemctl start docker
# Mac: Start Docker Desktop
```

### Issue: "Docker Compose not installed"

**Solution:**

```bash
# Install Docker Compose
pip install docker-compose
# or
apt-get install docker-compose  # Linux
```

### Issue: "Python version mismatch"

**Solution:**

```bash
# Check Python version
python --version  # Should be 3.11.9+

# If not correct, install Python 3.11.9
# Then create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Issue: "Port 5000 already in use"

**Solution:**

```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Issue: "Docker image build fails"

**Solution:**

```bash
# Check Docker resources
docker system df  # Show disk usage

# Clean up if needed
docker system prune -a --volumes

# Try build again
docker-compose build --no-cache
```

### Issue: "Services won't start"

**Solution:**

```bash
# Check logs
docker-compose logs
docker-compose logs service_name

# Verify configuration
cat docker-compose.yml

# Try restarting
docker-compose down
docker-compose up -d
```

---

## 🔄 COMMON WORKFLOWS

### First-Time Deployment

```bash
# 1. Clone repository
git clone <repo-url>
cd oscar

# 2. Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Run automated deployment
python deploy_local_all_phases.py

# 4. Wait for completion (~70 minutes)
# 5. Check results and logs
```

### Redeployment (Fresh Start)

```bash
# 1. Stop existing services
docker-compose down

# 2. Remove old images (optional)
docker rmi bob-ai:latest

# 3. Run deployment again
python deploy_local_all_phases.py
```

### Quick Verification

```bash
# After deployment, verify manually:
curl http://localhost:5000/health
docker-compose ps
docker-compose logs --tail=20
```

### Partial Redeploy

```bash
# If only configuration changed:
docker-compose up -d  # Just restart

# If code changed:
docker-compose build  # Rebuild
docker-compose up -d  # Restart
```

---

## 📈 PERFORMANCE MONITORING

### During Deployment

```bash
# In another terminal, monitor Docker
docker stats
```

### After Deployment

```bash
# Check system health
docker-compose ps
docker-compose logs -f
curl http://localhost:5000/health
```

### Performance Targets

- Component Init: 40ms ✅
- Query Response: <5ms ✅
- Throughput: 10+ q/sec ✅
- CPU Usage: <50% ✅
- Memory: <2GB ✅

---

## 🔐 SECURITY NOTES

### Before Production

1. **Review .env file** - Ensure no secrets are exposed
2. **Update Docker registry** - Use private registry if needed
3. **Configure authentication** - Set up API authentication
4. **Enable HTTPS** - Use SSL/TLS certificates
5. **Network isolation** - Configure firewall rules

### Best Practices

- Don't commit .env to version control
- Use secrets manager for sensitive data
- Enable Docker security scanning
- Monitor container logs for errors
- Keep Docker and Python updated

---

## 📚 NEXT STEPS AFTER DEPLOYMENT

### 1. Verify Deployment

```bash
# Test health endpoint
curl http://localhost:5000/health

# Check service status
docker-compose ps

# Review logs
docker-compose logs
```

### 2. Run Manual Tests

```bash
# Access API
curl http://localhost:5000/api/health

# Query knowledge base
curl http://localhost:5000/api/query

# Test reasoning
curl http://localhost:5000/api/reason
```

### 3. Monitor Performance

```bash
# Watch logs
docker-compose logs -f

# Monitor resources
docker stats

# Check metrics
curl http://localhost:5000/metrics
```

### 4. Review Documentation

- See: DEPLOYMENT_QUICK_START_CARD.md
- See: API_REFERENCE_V9.md
- See: USAGE_GUIDE_V9.md

---

## 🆘 GET HELP

### If Deployment Fails

1. **Check logs:**

   ```bash
   docker-compose logs
   ```

2. **Review error messages** in script output

3. **Consult troubleshooting guide:**
   - TROUBLESHOOTING_FAQ_V9.md
   - This deployment guide

4. **Manual deployment:**
   - Use LOCAL_DEPLOYMENT_TODOS_REGISTRY.md
   - Follow step-by-step instructions

5. **Contact support:**
   - See support contacts in registry

---

## 📋 DEPLOYMENT CHECKLIST

Before running deployment:

- [ ] Python 3.11.9+ installed
- [ ] Docker 28.5.1+ installed
- [ ] Docker Compose 2.40.0+ installed
- [ ] 5+ GB disk space available
- [ ] Port 5000 available
- [ ] .env file exists (or will be created)
- [ ] Docker daemon is running
- [ ] Internet connection available (for pulling images)

After deployment:

- [ ] All 7 phases completed
- [ ] deployment_log.json created
- [ ] docker-compose ps shows all containers running
- [ ] Health check endpoint responding
- [ ] Logs show no critical errors
- [ ] Performance targets verified

---

## 🎯 SUCCESS CRITERIA

Your deployment is successful when:

✅ All 7 phases complete
✅ deployment_log.json shows SUCCESS status
✅ `docker-compose ps` shows all containers UP
✅ Health endpoint returns HTTP 200
✅ No critical errors in logs
✅ Performance within targets
✅ System ready for use

---

## 📞 SUPPORT INFORMATION

**Documentation:**

- API Reference: API_REFERENCE_V9.md
- Usage Guide: USAGE_GUIDE_V9.md
- Troubleshooting: TROUBLESHOOTING_FAQ_V9.md
- Operations: OPERATIONS_MANUAL.md

**Scripts:**

- Python: deploy_local_all_phases.py
- PowerShell: deploy_local_all_phases.ps1

**Registry:**

- Complete checklist: LOCAL_DEPLOYMENT_TODOS_REGISTRY.md
- Quick reference: DEPLOYMENT_QUICK_START_CARD.md

---

**Version:** 1.0
**Created:** October 27, 2025
**Status:** ✅ Production Ready
**Project:** BOB AI v9.0
