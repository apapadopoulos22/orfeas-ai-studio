# ORFEAS AI - Automatic Netlify Deployment Guide

**Version:** 1.0
**Date:** October 26, 2025
**Status:** Production Ready

---

## 📋 Overview

This guide explains how to set up **completely automatic deployment** of ORFEAS AI Studio to Netlify. After setup, every push to your Git repository automatically triggers a new deployment.

### What You'll Get

✅ **Automatic deployments** on every Git push
✅ **Zero manual deployment steps**
✅ **Global CDN distribution** (80+ locations)
✅ **Preview deployments** for pull requests
✅ **One-click rollback** if needed
✅ **Production monitoring** and analytics

---

## 🚀 Quick Start (5 minutes)

### Option 1: Automated Setup (Recommended)

```powershell
# Run the automatic setup script
.\NETLIFY_AUTO_DEPLOY_SETUP.ps1

# Follow the interactive prompts
# Script will:
# - Verify Git installation
# - Initialize repository
# - Commit files
# - Guide GitHub connection
# - Configure Netlify
```

### Option 2: Manual Setup

Follow the step-by-step guide below.

---

## 🔧 Step-by-Step Setup

### Step 1: Install Prerequisites

#### Git

```powershell
# Download from: https://git-scm.com/download/win
# Or use Chocolatey:
choco install git
```

#### (Optional) Netlify CLI

```powershell
# Install via npm:
npm install -g netlify-cli

# Or just use the Netlify web interface (no CLI needed)
```

### Step 2: Initialize Git Repository

```powershell
# Navigate to project root
cd C:\Users\johng\Documents\oscar

# Initialize Git (if not already done)
git init

# Configure user
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Commit
git commit -m "Initial commit: ORFEAS AI Studio with Netlify deployment"
```

### Step 3: Create GitHub Repository

1. **Go to:** <https://github.com/new>
2. **Fill in:**
   - Repository name: `orfeas-ai-studio`
   - Description: "Enterprise AI platform for 2D→3D generation"
   - Visibility: Public or Private (your choice)
3. **Click:** "Create repository"
4. **Copy** the repository URL (e.g., `https://github.com/username/orfeas-ai-studio.git`)

### Step 4: Push to GitHub

```powershell
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/orfeas-ai-studio.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main

# Future pushes (simplified):
git push origin main
```

### Step 5: Create Netlify Site

1. **Go to:** <https://app.netlify.com>
2. **Click:** "Sign up" or "Sign in" (use GitHub)
3. **Connect GitHub:** Authorize Netlify to access your repositories
4. **Click:** "New site from Git"
5. **Select:** GitHub
6. **Choose:** Your repository (`orfeas-ai-studio`)

### Step 6: Configure Netlify Build

In Netlify's site setup:

```
Build command:     (leave empty)
Publish directory: .
Functions dir:     netlify/functions
```

### Step 7: Add Environment Variables

In Netlify dashboard, go to **Site settings → Environment variables** and add:

```
BACKEND_API=http://localhost:5000
API_BASE=https://your-site.netlify.app
ENVIRONMENT=production
DEVICE=cuda
GPU_MEMORY_LIMIT=0.8
LOCAL_LLM_ENABLED=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
CORS_ORIGINS=*
```

### Step 8: Trigger First Deployment

Your site automatically deploys when you push! To trigger:

```powershell
# Make a small change (e.g., edit a comment in netlify.toml)
# Then commit and push

git add netlify.toml
git commit -m "Trigger initial Netlify deployment"
git push origin main

# Watch deployment at: https://app.netlify.com/sites/your-site/deploys
```

---

## 🔄 Automatic Deployment Workflow

After setup, automatic deployment works like this:

### For Every Change

```powershell
# 1. Make changes to any file
#    (e.g., edit orfeas-ai-studio.html)

# 2. Commit changes
git add .
git commit -m "Add new feature: xyz"

# 3. Push to GitHub
git push origin main

# 4. ✅ Automatic! Netlify sees the push and:
#    - Starts a new build
#    - Deploys to production
#    - Updates your live site
```

### Deployment Timeline

```
t=0s   → Push to GitHub
        git push origin main

t=5s   → Netlify webhook receives notification
        (automatic via GitHub hook)

t=10s  → Build starts
        - Functions compiled
        - Assets optimized
        - Deploy prepared

t=30s  → Deploy starts
        - Files pushed to CDN
        - Configuration applied

t=60s  → ✅ Live!
        Site updated at https://your-site.netlify.app
```

---

## 📊 Deployment Types

### 1. Production Deployment (Main Branch)

```powershell
git push origin main
→ Deploys to https://your-site.netlify.app (production)
```

### 2. Staging Deployment (Develop Branch)

```powershell
git push origin develop
→ Deploys to staging environment
```

### 3. Preview Deployment (Pull Requests)

```powershell
# Create feature branch
git checkout -b feature/new-ui

# Make changes and push
git push origin feature/new-ui

# Create pull request on GitHub
# → Netlify auto-creates preview deployment
# → Test before merging

# After approval, merge to main
git checkout main
git merge feature/new-ui
git push origin main
→ Production deployment triggered
```

---

## 🎯 Workflow Examples

### Example 1: Quick Hotfix

```powershell
# You're on main branch
git checkout main
git pull origin main

# Fix a bug
# (edit some files)

# Commit and push
git add .
git commit -m "fix: critical bug in 3D viewer"
git push origin main

# ✅ Live in ~1 minute!
```

### Example 2: Feature Development

```powershell
# Create feature branch
git checkout -b feature/advanced-materials

# Make changes over several commits
git add feature1.js
git commit -m "Add material editor UI"
git add feature2.js
git commit -m "Add physics simulation"

# Push feature branch
git push origin feature/advanced-materials

# Create Pull Request on GitHub
# → PR = automatic preview deployment
# → Team reviews
# → Tests run automatically

# When approved, merge to main
git checkout main
git merge feature/advanced-materials
git push origin main

# ✅ Feature goes live automatically
```

### Example 3: Environment-Specific Configuration

```powershell
# Update API endpoint based on environment
# netlify.toml context specifies which env gets which variables

# Push to main = production variables used
git push origin main

# Different API endpoints, features, etc. based on branch
```

---

## 📈 Monitoring Deployments

### 1. Netlify Dashboard

Go to: <https://app.netlify.com>

**Site → Deploys tab shows:**

- Deployment status (building/deployed/failed)
- Build logs
- Deployment timestamp
- Commit details
- Rollback option

### 2. Build Notifications

In Netlify Dashboard:

- **Settings → Email notifications**
- Enable: "Deploy succeeded"
- Enable: "Deploy failed"
- Receive email on every deployment

### 3. GitHub Integration

In GitHub repository:

- **Commits list** shows deployment status badges
- **Pull Requests** show preview deployment links
- Click status badge to see Netlify build logs

### 4. Check Deployment Status

```powershell
# View recent deployments
curl https://api.netlify.com/api/v1/sites/YOUR_SITE_ID/deploys

# Or check via Netlify CLI
netlify sites list
netlify status --site YOUR_SITE_ID
```

---

## 🔙 Rollback to Previous Version

### Quick Rollback (1 click)

1. Go to Netlify Dashboard
2. **Deploys** tab
3. Find previous deployment
4. Click **three dots** → **Publish deploy**
5. ✅ Live in seconds

### Why Rollback

- Bug introduced in latest version
- Performance issues
- Third-party service down
- Quick reverting while investigating

---

## ⚙️ Advanced Configuration

### Modify Build Settings

Edit `netlify.toml`:

```toml
[build]
  command = "echo 'Custom build step'"
  functions = "netlify/functions"
  publish = "."

[build.environment]
  CUSTOM_VAR = "value"
```

### Add Redirects

In `netlify.toml`:

```toml
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Conditional Deployment

Deploy only specific changes:

```powershell
# In GitHub, set up branch deploy rules:
# Settings → Branches → Deploy contexts
# - main branch = production
# - develop = staging
# - pull requests = preview
```

---

## 🐛 Troubleshooting

### Issue: Deployment Fails

**Solution:**

1. Check build logs in Netlify Dashboard → Deploys → Click failed deploy
2. Read error message
3. Fix issue locally
4. Commit and push again

Common causes:

- Missing files
- Environment variables not set
- Syntax errors
- Node/build tool issues

### Issue: Site Shows Old Version

**Solution:**

1. Hard refresh: `Ctrl+Shift+Delete` in browser
2. Or: Clear cache in Netlify Dashboard
3. Wait 1-2 minutes for CDN to update
4. Or: Publish previous deploy to rollback

### Issue: API Not Working

**Solution:**

1. Check `BACKEND_API` environment variable
2. Verify backend server is running
3. Check `/api/health` endpoint
4. Review API function logs in Netlify Dashboard

### Issue: Deploy Takes Too Long

**Solution:**

- Normal builds: 1-2 minutes
- If taking >5 minutes:
  1. Check build logs for bottleneck
  2. Optimize build command
  3. Contact Netlify support if persistent

---

## 📚 File Reference

### Key Files for Auto-Deployment

| File | Purpose |
|------|---------|
| `netlify.toml` | Netlify build configuration |
| `.env.netlify` | Environment variables template |
| `netlify/functions/api.js` | API proxy function |
| `netlify/functions/health.js` | Health check endpoint |
| `.github/workflows/deploy.yml` | (Optional) GitHub Actions CI/CD |
| `orfeas-ai-studio.html` | Main frontend (auto-deployed) |

---

## 🔐 Security Best Practices

### 1. Protect Secrets

```powershell
# DON'T push to Git:
# - API keys
# - Passwords
# - Auth tokens

# DO store in Netlify Environment Variables:
# Go to: Settings → Environment variables
```

### 2. Use HTTPS

- ✅ Netlify automatically uses HTTPS
- ✅ SSL certificate auto-renewed
- ✅ Force HTTPS in browser

### 3. Control Deployments

```powershell
# In GitHub Settings → Branch protection rules:
# - Require pull request reviews
# - Require status checks to pass
# - Dismiss stale PR approvals
```

### 4. Audit Logs

- Netlify → **Analytics & Logs** tab
- GitHub → **Audit log** under org settings
- Monitor for unauthorized changes

---

## 💰 Cost & Limits

### Free Tier (Netlify)

- **Deployments:** Unlimited
- **Build time:** 300 minutes/month
- **Bandwidth:** 100 GB/month
- **Functions:** 125,000 invocations/month
- **DNS:** Included

### Upgrade When

- Build time >300 min/month: Upgrade to Pro
- Bandwidth >100 GB/month: Upgrade to Pro
- Need priority support: Upgrade to Pro

---

## 🎓 Learning Resources

- **Netlify Docs:** <https://docs.netlify.com>
- **Netlify CLI:** <https://cli.netlify.com>
- **Git Guide:** <https://git-scm.com/doc>
- **GitHub Actions:** <https://docs.github.com/actions>

---

## ✅ Deployment Checklist

Before pushing to production:

- [ ] Tested locally
- [ ] No console errors
- [ ] API endpoints working
- [ ] Backend service running
- [ ] Environment variables set
- [ ] Commit message is clear
- [ ] No API keys in code
- [ ] Build succeeds locally

---

## 📞 Support

### If something breaks

1. Check Netlify build logs
2. Review recent commits
3. Rollback if needed (1-click)
4. Contact Netlify support (free tier eligible)
5. Check GitHub Actions logs for CI/CD issues

### Quick Debug Checklist

```powershell
# Verify Git status
git status

# Check recent commits
git log --oneline -5

# Verify remotes
git remote -v

# Check branch
git branch

# Verify Netlify config
type netlify.toml

# Check environment variables
# (in Netlify Dashboard Settings)
```

---

## 🎯 Next Steps

1. ✅ Run `NETLIFY_AUTO_DEPLOY_SETUP.ps1`
2. ✅ Verify first deployment succeeds
3. ✅ Test automatic redeploy with small change
4. ✅ Set up build notifications
5. ✅ Monitor site health

---

**Last Updated:** October 26, 2025
**Maintained By:** ORFEAS AI Team
**Status:** Production Ready ✅
