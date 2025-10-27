# 🆘 AUTOMATED DEPLOYMENT - TROUBLESHOOTING & ERROR RECOVERY

**Project:** BOB AI v9.0
**Type:** Error Recovery Reference
**Created:** October 27, 2025
**Status:** ✅ Complete

---

## 📋 OVERVIEW

This guide provides comprehensive troubleshooting for both automated deployment scripts and manual recovery procedures when issues occur.

---

## 🔴 CRITICAL ERRORS & SOLUTIONS

### Error 1: Docker Not Found or Not Running

**Symptoms:**

```
ERROR: Docker daemon not running
ERROR: docker: command not found
ERROR: Cannot connect to Docker daemon
```

**Diagnosis:**

```bash
# Check if Docker is installed
docker --version

# Check if Docker daemon is running
docker ps
```

**Solutions:**

**Windows:**

```powershell
# Option 1: Start Docker Desktop
# Start menu → Docker Desktop

# Option 2: Verify installation
docker --version
docker info
```

**Linux:**

```bash
# Check Docker service
sudo systemctl status docker

# Start Docker if not running
sudo systemctl start docker

# Enable auto-start
sudo systemctl enable docker
```

**Mac:**

```bash
# Start Docker Desktop from Applications
# Verify running
docker ps
```

**Prevention:**

- Configure Docker to start automatically
- Add startup script to deployment workflow
- Monitor Docker daemon health regularly

---

### Error 2: Docker Compose Not Found

**Symptoms:**

```
ERROR: docker-compose: command not found
ERROR: 'docker-compose' is not installed
ERROR: Compose version not supported
```

**Diagnosis:**

```bash
# Check Docker Compose version
docker-compose --version
# or
docker compose version  # Docker 2.0+
```

**Solutions:**

**Installation:**

```bash
# Using pip (recommended)
pip install docker-compose

# Using apt (Linux)
sudo apt-get install docker-compose

# Using brew (Mac)
brew install docker-compose

# Using Windows Installer
# Download from: https://github.com/docker/compose/releases
```

**Verify Installation:**

```bash
docker-compose --version
# Should output: Docker Compose version 2.40.0+
```

**Recovery:**

```bash
# If version mismatch, upgrade
pip install --upgrade docker-compose

# Verify after upgrade
docker-compose --version
```

---

### Error 3: Python Version Mismatch

**Symptoms:**

```
ERROR: Python version 3.10.5 is below minimum 3.11.9
ERROR: SyntaxError: invalid syntax (Python 2 vs 3)
ERROR: ModuleNotFoundError: package requires Python 3.11+
```

**Diagnosis:**

```bash
python --version
python -c "import sys; print(sys.version_info)"
```

**Solutions:**

**Windows:**

```powershell
# Download Python 3.11.9+ from python.org
# Run installer with "Add Python to PATH" checked

# Verify after installation
python --version

# Create virtual environment
python -m venv venv
venv\Scripts\activate
```

**Linux:**

```bash
# Using apt
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Using pyenv (recommended for multiple versions)
curl https://pyenv.run | bash
pyenv install 3.11.9
pyenv global 3.11.9
```

**Mac:**

```bash
# Using Homebrew
brew install python@3.11

# Using pyenv
brew install pyenv
pyenv install 3.11.9
pyenv global 3.11.9
```

**Verify:**

```bash
python --version  # Should be 3.11.9+
python -m pip --version  # Should be present
```

---

### Error 4: Port 5000 Already in Use

**Symptoms:**

```
ERROR: Address already in use
ERROR: Port 5000 is already allocated
ERROR: Cannot bind to port 5000
```

**Diagnosis:**

**Windows:**

```powershell
# Find process on port 5000
netstat -ano | findstr :5000

# Get full details
Get-NetTCPConnection -LocalPort 5000
```

**Linux/Mac:**

```bash
# Find process on port 5000
lsof -i :5000
ss -tulpn | grep 5000
```

**Solutions:**

**Option 1: Kill Existing Process**

**Windows:**

```powershell
# Find PID from previous command output
# Example: PID is 1234
taskkill /PID 1234 /F
```

**Linux/Mac:**

```bash
# Kill process
lsof -ti:5000 | xargs kill -9
```

**Option 2: Use Different Port**

```bash
# Edit docker-compose.yml
# Change port mapping from 5000:5000 to 5001:5000

# Or set environment variable
export PORT=5001
docker-compose up -d
```

**Option 3: Stop Existing Service**

```bash
# If it's another deployment running
docker-compose down

# Or stop specific container
docker stop <container-name>
```

**Prevention:**

- Always stop deployment before restarting
- Use `docker-compose down` properly
- Monitor port usage before deployment
- Document which services use which ports

---

### Error 5: Insufficient Disk Space

**Symptoms:**

```
ERROR: No space left on device
ERROR: Cannot write to disk
ERROR: Docker build failed (disk full)
```

**Diagnosis:**

**Windows:**

```powershell
Get-Volume
```

**Linux/Mac:**

```bash
df -h
du -sh /*
```

**Solutions:**

**Free up space:**

```bash
# Remove Docker unused resources
docker system prune -a --volumes
# Caution: This removes unused images/containers/volumes

# Clean Docker images only
docker image prune -a

# Clean old containers
docker container prune

# Check space after cleanup
df -h  # Linux/Mac
Get-Volume  # Windows
```

**Find large files:**

```bash
# Linux/Mac: Find files > 100MB
find / -type f -size +100M -exec ls -lh {} \;

# Remove old logs
rm -f /var/log/*.log*
```

**Alternative deployment locations:**

```bash
# Move deployment to different drive with more space
# Update path in deployment script
```

**Prevention:**

- Monitor disk space regularly
- Clean up old Docker images periodically
- Set up automated cleanup
- Have at least 10GB free before deployment

---

### Error 6: Docker Build Fails

**Symptoms:**

```
ERROR: Docker build failed
ERROR: Build context exceeded limits
ERROR: Dockerfile syntax error
```

**Diagnosis:**

```bash
# Check Docker log
docker-compose build --verbose

# Verify Dockerfile syntax
docker build --progress=plain .
```

**Solutions:**

**Option 1: Clean rebuild**

```bash
# Remove old images
docker rmi $(docker images -q)

# Remove build cache
docker builder prune -a

# Rebuild
docker-compose build --no-cache
```

**Option 2: Check Dockerfile**

```bash
# View Dockerfile
cat Dockerfile

# Common issues:
# - Syntax errors
# - Missing dependencies
# - Invalid base image
# - Permission issues
```

**Option 3: Fix dependencies**

```bash
# Update base image
# FROM python:3.11.9-slim (current)

# Update requirements.txt
pip freeze > requirements.txt

# Rebuild
docker-compose build --no-cache
```

**Debug with intermediate image:**

```bash
# Build step by step
docker build -t debug:1 --target stage1 .
```

---

### Error 7: Services Won't Start

**Symptoms:**

```
ERROR: Container exited with code 1
ERROR: Service health check failed
ERROR: Container logs show errors
```

**Diagnosis:**

```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs
docker-compose logs service_name

# Check specific service
docker-compose logs --tail=50 -f
```

**Solutions:**

**Option 1: Check configuration**

```bash
# Verify docker-compose.yml
docker-compose config

# Verify environment
cat .env

# Check for typos/syntax errors
```

**Option 2: Review service logs**

```bash
# Get full logs
docker-compose logs service_name --tail=100

# Follow in real-time
docker-compose logs -f

# Look for:
# - Connection errors
# - Port conflicts
# - Missing dependencies
# - Environment variable issues
```

**Option 3: Restart services**

```bash
# Full restart
docker-compose down
docker-compose up -d

# Specific service restart
docker-compose restart service_name

# With rebuild
docker-compose up -d --build
```

**Option 4: Fix environment**

```bash
# Verify .env file exists
ls -la .env

# Check required variables
grep -E "^[A-Z_]+" .env

# Update if missing
echo "KEY=value" >> .env
```

---

### Error 8: Health Check Failures

**Symptoms:**

```
ERROR: Health endpoint not responding
ERROR: HTTP 500 from /health
ERROR: Connection refused
```

**Diagnosis:**

```bash
# Test health endpoint
curl http://localhost:5000/health

# Check service logs
docker-compose logs

# Verify port is open
netstat -an | grep 5000

# Check if service is running
docker-compose ps
```

**Solutions:**

**Option 1: Wait for service initialization**

```bash
# Services take time to start
# Wait 30-60 seconds after startup

# Monitor logs during startup
docker-compose logs -f

# Look for "Ready to accept connections" message
```

**Option 2: Check configuration**

```bash
# Verify health check config in docker-compose.yml
# Ensure endpoint path is correct

# Check app configuration
cat config.py
cat settings.json
```

**Option 3: Verify service is running**

```bash
# Get service status
docker-compose ps

# If not running, start it
docker-compose up -d service_name

# Check logs for errors
docker-compose logs service_name
```

**Option 4: Test connectivity**

```bash
# From host
curl http://localhost:5000/health

# From Docker
docker exec container_name curl http://localhost:5000/health

# Test with verbose output
curl -v http://localhost:5000/health
```

---

## 🟡 WARNING MESSAGES & REMEDIATION

### Warning 1: High Memory Usage

**Message:**

```
WARNING: Container memory at 85% of limit
WARNING: Memory pressure detected
```

**Action:**

```bash
# Monitor memory
docker stats

# Find memory hogs
docker stats --no-stream | sort -k 4 -h

# Increase limits if needed
# Edit docker-compose.yml:
# mem_limit: 4g
# memswap_limit: 6g
```

---

### Warning 2: High CPU Usage

**Message:**

```
WARNING: CPU usage sustained at >80%
WARNING: Container CPU throttled
```

**Action:**

```bash
# Monitor CPU
docker stats

# Check for processes using CPU
ps aux | sort -k3 -h

# Optimize or reduce load
docker-compose down
docker-compose up -d --scale service=2  # Scale if possible
```

---

### Warning 3: Disk I/O Issues

**Message:**

```
WARNING: Disk I/O performance degraded
WARNING: Read/write latency high
```

**Action:**

```bash
# Check disk performance
iostat -x 1

# Monitor Docker disk usage
docker system df

# Clean up if needed
docker system prune -a
```

---

## 🟢 RECOVERY PROCEDURES

### Recovery 1: Rollback Deployment

**If deployment fails after partial completion:**

```bash
# Step 1: Stop all services
docker-compose down

# Step 2: Remove new images (optional)
docker rmi $(docker images | grep "bob-ai" | awk '{print $3}')

# Step 3: Check git status
git status
git log --oneline -5

# Step 4: Revert if needed
git revert <commit>
# or
git reset --hard <previous-commit>

# Step 5: Try deployment again
python deploy_local_all_phases.py
```

---

### Recovery 2: Clean State Reset

**For complete reset to clean state:**

```bash
# 1. Stop all services
docker-compose down -v  # Also remove volumes

# 2. Remove all Bob AI containers/images
docker ps -a | grep bob-ai | awk '{print $1}' | xargs docker rm -f
docker images | grep bob-ai | awk '{print $3}' | xargs docker rmi -f

# 3. Clean Docker system
docker system prune -a --volumes

# 4. Verify clean state
docker ps -a
docker images

# 5. Restart deployment
python deploy_local_all_phases.py
```

---

### Recovery 3: Configuration Recovery

**If configuration is corrupted:**

```bash
# 1. Backup current config
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup

# 2. Restore from version control
git checkout .env
git checkout docker-compose.yml

# 3. Verify configuration
docker-compose config

# 4. Restart services
docker-compose down
docker-compose up -d
```

---

### Recovery 4: Gradual Service Recovery

**If some services fail but others work:**

```bash
# 1. Identify failed services
docker-compose ps

# 2. Check logs for each failed service
docker-compose logs service_1
docker-compose logs service_2

# 3. Restart failed services
docker-compose restart service_1
docker-compose restart service_2

# 4. Monitor recovery
docker-compose logs -f

# 5. Full restart if needed
docker-compose down
docker-compose up -d
```

---

## 📊 HEALTH CHECK PROCEDURES

### Pre-Deployment Health Check

```bash
# Run before deployment
echo "=== Pre-Deployment Checks ==="

# Check Python
python --version

# Check Docker
docker --version
docker ps

# Check Docker Compose
docker-compose --version

# Check disk space
# Windows: dir C:
# Linux/Mac: df -h

# Check ports
# Windows: netstat -ano | findstr :5000
# Linux/Mac: lsof -i :5000
```

### Post-Deployment Health Check

```bash
# Run after deployment
echo "=== Post-Deployment Checks ==="

# Check containers running
docker-compose ps

# Check health endpoint
curl http://localhost:5000/health

# Check logs
docker-compose logs --tail=20

# Check resource usage
docker stats --no-stream

# Verify network
docker network ls
docker network inspect oscar_default  # or network name
```

---

## 🧪 DIAGNOSTIC COMMANDS

### Collect Diagnostic Information

```bash
# Create diagnostic report
{
  echo "=== System Information ==="
  echo "Date: $(date)"
  echo "OS: $(uname -a)"
  echo ""
  echo "=== Python ==="
  python --version
  echo ""
  echo "=== Docker ==="
  docker --version
  docker ps -a
  echo ""
  echo "=== Docker Compose ==="
  docker-compose --version
  docker-compose ps
  echo ""
  echo "=== Service Logs ==="
  docker-compose logs --tail=50
  echo ""
  echo "=== Disk Usage ==="
  df -h
  echo ""
  echo "=== Memory Usage ==="
  free -h
} | tee diagnostic_report.txt
```

### Interactive Troubleshooting

```bash
# 1. Enter service container
docker-compose exec service_name /bin/bash

# 2. Check service status
ps aux
systemctl status service_name

# 3. Test connectivity
curl http://localhost:5000/health
ping google.com

# 4. Check logs
tail -f /var/log/service.log

# 5. Exit container
exit
```

---

## 📞 ESCALATION PROCEDURE

**If standard troubleshooting fails:**

1. **Collect Information**

   ```bash
   # Run diagnostic command (above)
   # Save output: diagnostic_report.txt
   ```

2. **Review Documentation**
   - AUTOMATED_DEPLOYMENT_GUIDE.md
   - LOCAL_DEPLOYMENT_TODOS_REGISTRY.md
   - DEPLOYMENT_QUICK_START_CARD.md

3. **Check Logs**

   ```bash
   docker-compose logs > full_logs.txt
   cat full_logs.txt
   ```

4. **Try Alternative Approach**
   - Use manual deployment from TODOS_REGISTRY
   - Try different Python version
   - Try on different machine

5. **Contact Support**
   - Provide diagnostic_report.txt
   - Include deployment logs
   - Describe steps taken
   - Note error messages

---

## 📚 REFERENCE

**Error Categories:**

1. Environment (Docker, Python, dependencies)
2. Configuration (.env, docker-compose.yml)
3. Resources (disk, memory, ports)
4. Services (startup, health, logs)
5. Network (connectivity, DNS)

**Solution Categories:**

1. Install/Upgrade (missing components)
2. Restart/Reset (service restart, cache clear)
3. Reconfigure (settings update)
4. Recovery (rollback, fallback)
5. Escalate (when above fails)

---

**Version:** 1.0
**Status:** ✅ Complete
**Last Updated:** October 27, 2025
**Project:** BOB AI v9.0
