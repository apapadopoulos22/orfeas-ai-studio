# Production Deployment Checklist - ORFEAS AI Studio

**Last Updated**: October 26, 2025
**Environment**: Ubuntu 20.04+ / Linux
**Target**: Enterprise Production (24/7 availability)

---

## Pre-Deployment (Week Before)

### System Preparation

- [ ] **Infrastructure ready**
  - [ ] Server provisioned (8+ CPU cores, 32GB+ RAM, RTX 3090+ GPU)
  - [ ] NVIDIA CUDA 12.0+ installed
  - [ ] NVIDIA drivers updated
  - [ ] Ubuntu 20.04 LTS fully updated (`sudo apt update && sudo apt upgrade`)
  - [ ] Disk space verified (500GB+ SSD for models + outputs)

- [ ] **Network configuration**
  - [ ] DNS records pointing to server
  - [ ] SSL certificate acquired (Let's Encrypt or commercial)
  - [ ] Firewall configured (UFW or AWS Security Groups)
  - [ ] Ports open: 80, 443, 22 (SSH)
  - [ ] Port 6379 closed to external traffic (Redis internal only)

- [ ] **Monitoring and logging**
  - [ ] ELK Stack / CloudWatch configured (optional but recommended)
  - [ ] Application log rotation setup
  - [ ] Error tracking (Sentry/Datadog) configured
  - [ ] Uptime monitoring enabled (UptimeRobot / New Relic)

---

## Installation Phase (Day 1)

### 1. System Dependencies

```bash
# Execute on production server
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    build-essential \
    git \
    curl \
    wget \
    vim \
    htop \
    tmux \
    supervisor \
    nginx \
    redis-server \
    uwsgidecorator \
    libssl-dev \
    libffi-dev

# Verify versions
python3.10 --version
pip3 --version
redis-server --version
nginx -v
```

- [ ] All dependencies installed successfully

### 2. GPU Setup

```bash
# Check GPU
nvidia-smi

# Expected output:
# - GPU model (RTX 3090 or similar)
# - CUDA version (12.0+)
# - Memory: 24GB+

# Install CUDA toolkit (if not present)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-1804
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt update
sudo apt install -y cuda-toolkit-12-0

# Install cuDNN
# Download from NVIDIA website and install manually
# Or use conda: conda install -c conda-forge cudnn
```

- [ ] GPU detected and functional
- [ ] CUDA version >= 12.0
- [ ] cuDNN installed

### 3. Create Application User

```bash
# Create service user
sudo useradd -m -s /bin/bash orfeas
sudo usermod -aG sudo orfeas

# Create application directory
sudo mkdir -p /opt/orfeas-ai-studio
sudo chown -R orfeas:orfeas /opt/orfeas-ai-studio
sudo chmod -R 755 /opt/orfeas-ai-studio

# Create logs directory
sudo mkdir -p /var/log/orfeas
sudo chown -R orfeas:orfeas /var/log/orfeas
sudo chmod -R 755 /var/log/orfeas

# Create data directory
sudo mkdir -p /data/orfeas/{models,outputs,cache}
sudo chown -R orfeas:orfeas /data/orfeas
sudo chmod -R 755 /data/orfeas
```

- [ ] Service user 'orfeas' created
- [ ] Directories created with proper permissions
- [ ] User can write to all required paths

### 4. Clone Repository

```bash
# Clone as orfeas user
sudo -u orfeas git clone https://github.com/apapadopoulos22/orfeas-ai-studio.git \
    /opt/orfeas-ai-studio

cd /opt/orfeas-ai-studio

# Verify clone
ls -la backend/
ls -la frontend/
```

- [ ] Repository cloned successfully
- [ ] All files present and readable

### 5. Python Environment Setup

```bash
# As orfeas user
cd /opt/orfeas-ai-studio
python3.10 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Verify key packages
pip show torch redis flask socketio gunicorn
```

- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] Key packages verified

### 6. Model Download

```bash
# Download Hunyuan3D models (~20 GB)
cd /opt/orfeas-ai-studio

# Run setup script (creates cache in /data/orfeas/models)
source venv/bin/activate
python backend/setup_model_cache.py

# Wait for download to complete
# Time: 10-30 minutes depending on connection

# Verify download
ls -lh /data/orfeas/models/
du -sh /data/orfeas/models/*
```

- [ ] Models downloaded successfully
- [ ] Total size ~20 GB
- [ ] Models readable by orfeas user

### 7. Environment Configuration

Create `/etc/orfeas/orfeas.env`:

```bash
sudo mkdir -p /etc/orfeas
sudo touch /etc/orfeas/orfeas.env
sudo chown orfeas:orfeas /etc/orfeas/orfeas.env
sudo chmod 600 /etc/orfeas/orfeas.env
```

Content:

```bash
# Flask
FLASK_ENV=production
FLASK_APP=backend.main:app
DEBUG=false

# GPU & CUDA
DEVICE=cuda
ORT_TENSORRT_UNAVAILABLE=1
XFORMERS_DISABLED=1
GPU_MEMORY_LIMIT=0.8
CUDA_MODULE_LOADING=LAZY
HOME=/home/orfeas

# Paths
HY3DGEN_MODELS=/data/orfeas/models
OUTPUTS_DIR=/data/orfeas/outputs
CACHE_DIR=/data/orfeas/cache

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=<STRONG_PASSWORD_HERE>
REDIS_POOL_MAX_CONNECTIONS=50

# Cache TTL
CACHE_TTL_SHORT=300
CACHE_TTL_MEDIUM=3600
CACHE_TTL_LONG=604800

# CORS
CORS_ORIGINS=https://orfeas-studio.example.com

# Logging
LOG_LEVEL=info
ENABLE_MONITORING=true

# LLM
LOCAL_LLM_ENABLED=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=mistral
```

- [ ] Environment file created at `/etc/orfeas/orfeas.env`
- [ ] All paths configured correctly
- [ ] Redis password set securely

---

## Redis Setup (Day 1, Afternoon)

### 1. Configure Redis

Edit `/etc/redis/redis.conf`:

```bash
sudo nano /etc/redis/redis.conf
```

Key changes:

```ini
bind 127.0.0.1
port 6379
requirepass <STRONG_PASSWORD_HERE>
maxmemory 8gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
```

- [ ] Redis configuration updated
- [ ] Password set
- [ ] Persistence enabled

### 2. Start Redis

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server

# Test connection
redis-cli -a <PASSWORD> ping
```

- [ ] Redis running successfully
- [ ] Password verified
- [ ] PING responds with PONG

### 3. Backup Configuration

```bash
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
```

- [ ] Redis config backed up

---

## Gunicorn Setup (Day 1, Late Afternoon)

### 1. Verify Configuration

```bash
cd /opt/orfeas-ai-studio
source venv/bin/activate

# Check gunicorn.conf.py
cat gunicorn.conf.py

# Test configuration
gunicorn -c gunicorn.conf.py --check-config backend.main:app
```

- [ ] gunicorn.conf.py exists
- [ ] Configuration valid

### 2. Test Gunicorn Locally

```bash
# Run in foreground (watch for errors)
cd /opt/orfeas-ai-studio
source venv/bin/activate
gunicorn -c gunicorn.conf.py backend.main:app

# In another terminal, test endpoint
curl -k http://localhost:5000/health

# Should return: {"status": "ok"}
```

- [ ] Gunicorn starts without errors
- [ ] Application loads successfully
- [ ] Health endpoint responds

### 3. Stop Gunicorn

```
Press Ctrl+C in terminal running gunicorn
```

---

## Nginx Setup (Day 2, Morning)

### 1. Create Nginx Configuration

Create `/etc/nginx/sites-available/orfeas-ai-studio`:

```bash
sudo nano /etc/nginx/sites-available/orfeas-ai-studio
```

Use content from: PRODUCTION_DEPLOYMENT_GUIDE.md (Nginx Configuration section)

- [ ] Nginx config created

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/orfeas-ai-studio \
    /etc/nginx/sites-enabled/orfeas-ai-studio

# Remove default
sudo rm /etc/nginx/sites-enabled/default

# Test
sudo nginx -t
```

- [ ] Site enabled
- [ ] Configuration valid

### 3. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx

sudo certbot certonly --nginx -d orfeas-studio.example.com

# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

- [ ] SSL certificate obtained
- [ ] Auto-renewal enabled

### 4. Start Nginx

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

- [ ] Nginx running
- [ ] Enabled on boot

---

## Systemd Service Setup (Day 2, Afternoon)

### 1. Create Service File

Copy provided `orfeas-ai-studio.service` to:

```bash
sudo cp orfeas-ai-studio.service /etc/systemd/system/
```

- [ ] Service file copied

### 2. Configure Service

Edit `/etc/systemd/system/orfeas-ai-studio.service`:

```bash
sudo nano /etc/systemd/system/orfeas-ai-studio.service
```

Key sections to verify:

```ini
[Service]
User=orfeas
Group=orfeas
EnvironmentFile=/etc/orfeas/orfeas.env
WorkingDirectory=/opt/orfeas-ai-studio
ExecStart=/opt/orfeas-ai-studio/venv/bin/gunicorn -c gunicorn.conf.py backend.main:app
Restart=always
RestartSec=10
```

- [ ] Service file configured
- [ ] Paths correct
- [ ] Environment file referenced

### 3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable orfeas-ai-studio
sudo systemctl start orfeas-ai-studio
sudo systemctl status orfeas-ai-studio

# View logs
journalctl -u orfeas-ai-studio -f

# Wait for startup (model loading takes ~24 seconds)
sleep 30
```

- [ ] Service starts successfully
- [ ] No startup errors
- [ ] Model loads successfully

---

## Testing & Verification (Day 2, Late Afternoon)

### 1. Health Endpoints

```bash
# HTTP health check
curl -k http://localhost/health

# HTTPS health check (after SSL)
curl -k https://orfeas-studio.example.com/health

# Expected response:
# {"status": "ok", "version": "1.0", "gpu": "available"}
```

- [ ] Health endpoint responds

### 2. Redis Connectivity

```bash
# Test Redis connection
redis-cli -a <PASSWORD> ping

# Check connected clients
redis-cli -a <PASSWORD> CLIENT LIST

# View memory
redis-cli -a <PASSWORD> INFO memory
```

- [ ] Redis responds
- [ ] Authentication working
- [ ] Memory available

### 3. Application Functionality

```bash
# Test generation endpoint (short timeout)
curl -X POST https://orfeas-studio.example.com/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/test.jpg",
    "settings": {"quality": "medium"}
  }'

# Expected: Job ID returned
```

- [ ] Generation endpoint responds
- [ ] Job ID created
- [ ] No authentication errors

### 4. WebSocket Connectivity

```bash
# Test WebSocket via browser console
# Open browser to: https://orfeas-studio.example.com
# In browser console:
const socket = io('https://orfeas-studio.example.com');
socket.on('connect', () => console.log('Connected!'));
```

- [ ] WebSocket connects successfully

### 5. Load Testing (Optional)

```bash
# Install locust
pip install locust

# Run load test (adjust --host and --users as needed)
locust -f backend/tests/locustfile.py \
  --host https://orfeas-studio.example.com \
  --users 10 \
  --spawn-rate 2 \
  --run-time 5m

# Monitor: http://localhost:8089
```

- [ ] Load test passes without errors
- [ ] Response times acceptable
- [ ] No memory leaks detected

---

## Monitoring Setup (Day 3, Morning)

### 1. Application Monitoring

```bash
# View real-time logs
journalctl -u orfeas-ai-studio -f

# Monitor performance
top -u orfeas
ps aux | grep gunicorn

# Monitor GPU
watch -n 1 nvidia-smi
```

- [ ] Logging system functional
- [ ] Process monitoring working

### 2. Redis Monitoring

```bash
# Redis slowlog
redis-cli -a <PASSWORD> slowlog get 10

# Memory usage
redis-cli -a <PASSWORD> info memory

# Real-time monitor
redis-cli -a <PASSWORD> monitor
```

- [ ] Redis monitoring active

### 3. Set Up Log Rotation

Create `/etc/logrotate.d/orfeas`:

```bash
sudo nano /etc/logrotate.d/orfeas
```

Content:

```
/var/log/orfeas/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 orfeas orfeas
    sharedscripts
}
```

- [ ] Log rotation configured

---

## Backup & Recovery (Day 3, Afternoon)

### 1. Create Backup Script

Create `/opt/orfeas-ai-studio/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR=/backups/orfeas
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup Redis
redis-cli -a <PASSWORD> BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup application config
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/orfeas /etc/nginx/sites-available/orfeas-ai-studio

# Backup outputs (optional, may be large)
# tar -czf $BACKUP_DIR/outputs_$DATE.tar.gz /data/orfeas/outputs

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR"
```

```bash
sudo chmod +x /opt/orfeas-ai-studio/backup.sh
```

- [ ] Backup script created

### 2. Schedule Backups

```bash
# Add crontab entry (daily at 2 AM)
sudo crontab -e

# Add line:
0 2 * * * /opt/orfeas-ai-studio/backup.sh
```

- [ ] Backup scheduled

### 3. Off-Site Backup (AWS S3 Optional)

```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Upload backups to S3
aws s3 sync /backups/orfeas s3://my-backup-bucket/orfeas/
```

- [ ] Off-site backup configured (optional)

---

## Security Hardening (Day 3, Late Afternoon)

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny Redis from external
sudo ufw deny from any to any port 6379

# Check status
sudo ufw status
```

- [ ] Firewall enabled
- [ ] Only necessary ports open

### 2. SSH Hardening

```bash
sudo nano /etc/ssh/sshd_config

# Changes:
# PermitRootLogin no
# PasswordAuthentication no
# X11Forwarding no

sudo systemctl restart ssh
```

- [ ] SSH hardened
- [ ] Key-based auth required

### 3. Set File Permissions

```bash
# Restrict sensitive files
sudo chmod 600 /etc/orfeas/orfeas.env
sudo chmod 600 /etc/redis/redis.conf

# Verify
ls -la /etc/orfeas/orfeas.env
ls -la /etc/redis/redis.conf
```

- [ ] Sensitive files restricted

### 4. Set Up Fail2Ban (Optional)

```bash
sudo apt install -y fail2ban

# Create config
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

- [ ] Fail2Ban enabled (optional)

---

## Documentation & Handoff (Day 4)

### 1. Update Documentation

- [ ] PRODUCTION_DEPLOYMENT_GUIDE.md reviewed
- [ ] REDIS_SETUP_GUIDE.md completed
- [ ] Custom runbook created (copy from guide)

### 2. Create Operational Manual

Document:

- [ ] Emergency restart procedures
- [ ] Log locations
- [ ] Redis CLI commands
- [ ] GPU monitoring commands
- [ ] Common errors and solutions

### 3. Team Training

- [ ] Team can start/stop services
- [ ] Team can view logs
- [ ] Team understands monitoring
- [ ] Team knows backup/restore procedure

### 4. Final Verification

```bash
# Full system check
sudo systemctl status redis-server  # Should be active
sudo systemctl status nginx          # Should be active
sudo systemctl status orfeas-ai-studio  # Should be active

# Health endpoints all return 200
curl -k https://orfeas-studio.example.com/health
curl -k https://orfeas-studio.example.com/api/status

# Redis working
redis-cli -a <PASSWORD> ping  # PONG

# No errors in logs
journalctl -u orfeas-ai-studio -n 20 | grep -i error
```

- [ ] All services running
- [ ] All endpoints responding
- [ ] No critical errors in logs

---

## Post-Deployment (Week 1)

### Daily Checks

- [ ] Service status (systemctl status orfeas-ai-studio)
- [ ] Error logs (journalctl -u orfeas-ai-studio)
- [ ] GPU temperature (nvidia-smi)
- [ ] Disk space (df -h)
- [ ] Memory usage (free -h)

### Weekly Checks

- [ ] Redis backup exists
- [ ] SSL certificate expires >30 days
- [ ] Backup to S3 successful
- [ ] Performance metrics normal
- [ ] No security alerts

### Monthly Tasks

- [ ] Update dependencies (pip install --upgrade -r requirements.txt)
- [ ] Review and rotate logs
- [ ] Test backup restoration procedure
- [ ] Security patch applications
- [ ] Performance baseline review

---

## Rollback Procedure (If Needed)

```bash
# 1. Stop services
sudo systemctl stop orfeas-ai-studio
sudo systemctl stop nginx

# 2. Restore from backup
sudo cp /backups/orfeas/config_<DATE>.tar.gz /tmp/
cd /tmp
tar -xzf config_<DATE>.tar.gz
# Review and copy files back as needed

# 3. Restore Redis if needed
redis-cli shutdown
cp /backups/orfeas/redis_<DATE>.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb
sudo systemctl start redis-server

# 4. Start services
sudo systemctl start orfeas-ai-studio
sudo systemctl start nginx

# 5. Verify
curl -k https://orfeas-studio.example.com/health
```

- [ ] Rollback procedure documented
- [ ] Team trained on rollback

---

## Success Criteria

✅ **All of the following should be true:**

- [ ] All services running without errors
- [ ] Health endpoints returning 200 OK
- [ ] WebSocket connections stable
- [ ] Generation jobs completing successfully
- [ ] Redis caching active
- [ ] GPU detected and functional
- [ ] SSL certificate valid
- [ ] Backups automated and verified
- [ ] Logs monitored and aggregated
- [ ] Monitoring alerts configured
- [ ] Team trained and ready
- [ ] Runbook completed
- [ ] No critical security issues

---

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| DevOps Lead | [Name] | [Phone] | [Email] |
| On-Call Eng | [Name] | [Phone] | [Email] |
| Security | [Name] | [Phone] | [Email] |

---

**Deployment Status**: [ ] COMPLETE ✅

**Date Completed**: _______________
**Deployed By**: _______________
**Verified By**: _______________

---

For detailed procedures, see:

- PRODUCTION_DEPLOYMENT_GUIDE.md
- REDIS_SETUP_GUIDE.md
- BACKEND_STARTUP_GUIDE.md
