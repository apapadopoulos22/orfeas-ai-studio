# 🚀 ORFEAS AI - Automated Deployment Scripts

Complete automation for testing and deploying ORFEAS AI across all environments.

## 📋 Quick Start

### Option 1: Full Pipeline (Recommended)

Deploy to all environments in sequence:

```powershell
.\DEPLOY_ALL.ps1
```

This runs: Local Test → Staging → Production (with confirmations)

### Option 2: Individual Phases

Run each phase separately:

```powershell
# Test locally
.\DEPLOY_TEST_LOCAL.ps1

# Deploy to staging
.\DEPLOY_STAGING.ps1

# Deploy to production
.\DEPLOY_PRODUCTION.ps1
```

---

## 📦 Script Details

### 1. DEPLOY_TEST_LOCAL.ps1

**Purpose:** Test all optimizations locally before deploying

**What it does:**

- Stops existing backend
- Starts Docker services (Redis, PostgreSQL)
- Installs/updates dependencies
- Tests PostgreSQL connection
- Runs database migration
- Runs unit tests
- Starts backend server
- Runs integration tests

**Duration:** ~2 minutes

**Usage:**

```powershell
.\DEPLOY_TEST_LOCAL.ps1
```

**Output:**

- ✓ Backend running on <http://localhost:5000>
- ✓ Redis on localhost:6379
- ✓ PostgreSQL on localhost:5432

---

### 2. DEPLOY_STAGING.ps1

**Purpose:** Deploy to staging environment for final validation

**What it does:**

- Checks git status (commits if needed)
- Switches to develop branch
- Pulls latest changes
- Runs tests
- Pushes to develop (triggers GitHub Actions)
- Monitors deployment workflow
- Verifies staging health

**Duration:** ~5-10 minutes

**Usage:**

```powershell
.\DEPLOY_STAGING.ps1
```

**Output:**

- ✓ Staging deployed: <https://staging.orfeas.ai>
- GitHub Actions workflow link

**Requirements:**

- GitHub CLI (optional): `winget install GitHub.cli`

---

### 3. DEPLOY_PRODUCTION.ps1

**Purpose:** Deploy to production with blue-green strategy

**What it does:**

- Safety confirmation (requires "yes")
- Checks git status (must be clean)
- Verifies main branch
- Merges develop if needed
- Runs full test suite
- Creates git tag (v2025.10.26-1430)
- Pushes to main (triggers GitHub Actions)
- Monitors blue-green deployment
- Verifies production health

**Duration:** ~10-15 minutes

**Usage:**

```powershell
.\DEPLOY_PRODUCTION.ps1
```

**Output:**

- ✓ Production deployed: <https://orfeas.ai>
- Git tag created: v2025.10.26-HHMM
- Rollback command (if needed)

**Safety Features:**

- Double confirmation required
- Git tag for rollback
- Automated health checks
- Blue-green deployment strategy

---

### 4. DEPLOY_ALL.ps1

**Purpose:** Run complete deployment pipeline

**What it does:**

- Phase 1: Local testing
- Phase 2: Staging deployment
- Phase 3: Production deployment
- Confirmations between each phase

**Duration:** ~20-30 minutes

**Usage:**

```powershell
.\DEPLOY_ALL.ps1
```

---

## 🎯 Deployment Workflow

```text
┌─────────────────┐
│  Local Testing  │  ← DEPLOY_TEST_LOCAL.ps1
└────────┬────────┘
         │ ✓ Tests pass
         ↓
┌─────────────────┐
│  Push to Develop │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ GitHub Actions  │  ← CI: quality, tests, security
└────────┬────────┘
         │ ✓ CI passes
         ↓
┌─────────────────┐
│ Deploy Staging  │  ← DEPLOY_STAGING.ps1
└────────┬────────┘    (Rolling update)
         │ ✓ Staging works
         ↓
┌─────────────────┐
│  Merge to Main  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ GitHub Actions  │  ← Full CI/CD pipeline
└────────┬────────┘
         │ ✓ All checks pass
         ↓
┌─────────────────┐
│ Deploy Prod     │  ← DEPLOY_PRODUCTION.ps1
└────────┬────────┘    (Blue-green deployment)
         │
         ↓
┌─────────────────┐
│   Production    │  ← https://orfeas.ai
└─────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables

All scripts use environment variables from `.env`:

```bash
# Required for local testing
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://orfeas:orfeas@localhost:5432/orfeas_ai
CACHE_ENABLED=1
USE_POSTGRES_QUEUE=1

# Required for deployments
KUBE_CONFIG_STAGING=<base64_kubeconfig>
KUBE_CONFIG_PRODUCTION=<base64_kubeconfig>
SLACK_WEBHOOK_URL=<webhook_url>
```

### GitHub Secrets

Required for GitHub Actions:

```text
KUBE_CONFIG_STAGING       - Kubernetes config for staging
KUBE_CONFIG_PRODUCTION    - Kubernetes config for production
SLACK_WEBHOOK_URL         - Slack notifications
GHCR_TOKEN                - GitHub Container Registry token
```

Set in: GitHub → Settings → Secrets → Actions

---

## 🔍 Monitoring

### During Deployment

**Local:**

```powershell
# Check backend logs
Get-Content backend/logs/backend_requests.log -Tail 50

# Check Docker logs
docker-compose logs -f redis postgres
```

**Staging/Production:**

```powershell
# Watch GitHub Actions
gh run watch

# Check Kubernetes pods
kubectl get pods -n orfeas-staging
kubectl logs -n orfeas-staging -l app=orfeas-backend --tail=50

# Check health
curl https://staging.orfeas.ai/health
curl https://orfeas.ai/health
```

### Post-Deployment

**Grafana Dashboard:**

- URL: <https://grafana.orfeas.ai>
- Dashboard: ORFEAS Optimizations
- Panels: 12 (response times, GPU usage, cache hits, etc.)

**Key Metrics:**

- Response time: <15s target
- Error rate: <1% target
- GPU utilization: 60-80% target
- Cache hit rate: >20% target

---

## 🚨 Troubleshooting

### Local Testing Issues

**Backend won't start:**

```powershell
# Check port 5000
netstat -ano | findstr :5000

# Kill existing process
Get-Process python | Stop-Process -Force

# Check logs
python backend/main.py
```

**PostgreSQL connection failed:**

```powershell
# Check PostgreSQL container
docker ps | findstr postgres

# Restart PostgreSQL
docker-compose -f docker-compose-postgres.yml restart postgres

# Test connection
docker exec -it postgres psql -U orfeas -d orfeas_ai
```

**Tests failing:**

```powershell
# Run specific test
pytest tests/integration/test_progressive_and_cache.py -v

# Skip slow tests
pytest tests/ -m "not slow"
```

---

### Staging Deployment Issues

**GitHub Actions stuck:**

- Check: <https://github.com/apapadopoulos22/orfeas-ai-studio/actions>
- Cancel and retry: `gh run cancel` then push again

**Staging health check failed:**

```powershell
# Check pods
kubectl get pods -n orfeas-staging

# Check logs
kubectl logs -n orfeas-staging -l app=orfeas-backend --tail=100

# Describe deployment
kubectl describe deployment orfeas-backend -n orfeas-staging
```

---

### Production Deployment Issues

**Blue-green deployment failed:**

```powershell
# Check deployment status
kubectl get deployments -n orfeas-production

# Check pods
kubectl get pods -n orfeas-production

# Rollback immediately
kubectl rollout undo deployment/orfeas-backend-green -n orfeas-production
```

**High error rate after deployment:**

```powershell
# Automatic rollback should trigger, but manual rollback:
kubectl rollout undo deployment/orfeas-backend-green -n orfeas-production

# Check error logs
kubectl logs -n orfeas-production -l version=green --tail=200 | grep ERROR
```

---

## 📊 Success Criteria

### Local Testing

- ✓ Backend starts successfully
- ✓ PostgreSQL connection works
- ✓ Unit tests pass
- ✓ Integration tests pass

### Staging Deployment

- ✓ GitHub Actions CI passes
- ✓ Docker image builds
- ✓ Kubernetes deployment succeeds
- ✓ Health check returns 200
- ✓ Smoke tests pass

### Production Deployment

- ✓ All staging criteria met
- ✓ Blue-green deployment completes
- ✓ Traffic switched to green
- ✓ Error rate <1%
- ✓ Response time <15s
- ✓ No rollback triggered

---

## 🎉 Quick Commands

```powershell
# Full pipeline
.\DEPLOY_ALL.ps1

# Local only
.\DEPLOY_TEST_LOCAL.ps1

# Staging only
.\DEPLOY_STAGING.ps1

# Production only
.\DEPLOY_PRODUCTION.ps1

# Stop local backend
Get-Process python | Stop-Process -Force
docker-compose down

# Check deployment status
gh run list --limit 5
kubectl get pods -n orfeas-production

# Rollback production
kubectl rollout undo deployment/orfeas-backend-green -n orfeas-production
```

---

## 📚 Related Documentation

- [Complete Implementation Summary](COMPLETE_IMPLEMENTATION_SUMMARY.md)
- [Production Rollout Plan](PRODUCTION_ROLLOUT_PLAN.md)
- [CI/CD Deployment Guide](docs/CICD_DEPLOYMENT.md)
- [PostgreSQL Migration](docs/POSTGRESQL_MIGRATION.md)
- [Model Pruning Guide](docs/MODEL_PRUNING.md)
- [Kubernetes Setup](k8s/README.md)

---

**Status:** ✅ Production Ready
**Last Updated:** October 26, 2025
**Total Scripts:** 4
**Total Automation:** 100%

🚀 **Happy Deploying!**
