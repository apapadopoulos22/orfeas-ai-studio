# GitHub Deployment & Netlify Connection Guide

**Date:** October 26, 2025
**Goal:** Connect GitHub repository and enable automatic Netlify deployments

---

## Step 1: Commit All Changes to Git

### Check Git Status

```powershell
cd C:\Users\johng\Documents\oscar
git status
```

**Expected Output:**

```
On branch main
Changes not staged for commit:
  modified:   orfeas-ai-studio.html
  modified:   backend/main.py

Untracked files:
  PROMPT_ENHANCEMENT_*.md
  TEST_ENHANCEMENT_*.md
```

### Stage All Changes

```powershell
git add -A
```

### Commit with Clear Message

```powershell
git commit -m "feat: Add prompt enhancement feature with LLM support + test enhancement functions

- Added prompt enhancement button with dual strategy (LLM + fallback)
- Enhanced frontend with canvas fallback logic for image operations
- Added /api/enhance-prompt endpoint with Ollama integration
- Created comprehensive test suites for all features
- Improved image enhancement workflow"
```

### Verify Commit

```powershell
git log --oneline -5
```

---

## Step 2: Push to GitHub

### Add GitHub Remote (if not exists)

```powershell
git remote add origin https://github.com/apapadopoulos22/orfeas-ai-studio.git
```

### Verify Remote

```powershell
git remote -v
```

**Expected:**

```
origin  https://github.com/apapadopoulos22/orfeas-ai-studio.git (fetch)
origin  https://github.com/apapadopoulos22/orfeas-ai-studio.git (push)
```

### Push to Main Branch

```powershell
git push -u origin main
```

**Expected Output:**

```
Enumerating objects: 45, done.
Counting objects: 100% (45/45), done.
Delta compression using up to 8 threads: 1.26 MiB | 0.00 MiB/s, done.
Total 45 (delta 0), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (30/30), done.
To https://github.com/apapadopoulos22/orfeas-ai-studio.git
 * [new branch]      main -> main
```

### Verify Push

Visit: <https://github.com/apapadopoulos22/orfeas-ai-studio>

✅ Should see all files pushed
✅ Latest commit message should be visible

---

## Step 3: Create Netlify Deployment

### Login to Netlify

1. Go to <https://netlify.com>
2. Sign in with your account
3. Click **"Add new site"** → **"Import an existing project"**

### Connect GitHub Repository

1. Click **"GitHub"** as your Git provider
2. Authorize Netlify to access your GitHub account
3. Select repository: **orfeas-ai-studio**
4. Select branch: **main**

### Configure Build Settings

**Build Command:**

```bash
# Leave empty or use:
# (no build needed - static HTML)
```

**Publish Directory:**

```
.
(current directory - all HTML files)
```

**Advanced Settings:**

- Click "Show advanced"
- Add environment variables (if needed):

  ```
  REACT_APP_API_BASE=https://your-backend.com/api
  ```

### Deploy

1. Click **"Deploy site"**
2. Netlify will:
   - ✅ Pull from GitHub
   - ✅ Build (if configured)
   - ✅ Deploy to CDN
   - ✅ Generate live URL

**Your site will be at:** `https://[random-name].netlify.app`

---

## Step 4: Configure Automatic Deployments

### Enable Auto-Deploy on Push

Once deployed:

1. Go to Netlify Dashboard
2. Click your site
3. Go to **Settings** → **Build & deploy** → **Continuous deployment**
4. Verify **GitHub** is connected
5. **Auto-publish branch:** Set to **main**

**Now:**

- ✅ Every push to `main` branch triggers build
- ✅ Netlify automatically deploys changes
- ✅ Live URL updates within 1-2 minutes

### Enable Branch Deploys (Optional)

For testing features before production:

1. Settings → Build & deploy → Deploy contexts
2. Enable **Branch deploy**
3. Pattern: `develop`, `staging`, etc.

**Now you can:**

- Push to `develop` branch
- Get separate preview URL
- Test before merging to `main`

---

## Step 5: Custom Domain (Optional)

### Add Custom Domain

1. Netlify Dashboard → Your site
2. Settings → Domain management
3. Click **"Add domain"**
4. Enter your domain (e.g., `orfeas.ai`)
5. Follow DNS setup instructions

---

## Verification Checklist

### GitHub

- [ ] Repository created and visible
- [ ] All files pushed successfully
- [ ] Commit history shows all changes
- [ ] Latest commit is visible

### Netlify

- [ ] Site deployed successfully
- [ ] Live URL working
- [ ] Can access orfeas-ai-studio.html
- [ ] Auto-deploy configured
- [ ] Branch deploys enabled (optional)

### Testing Production Deployment

- [ ] Visit Netlify URL
- [ ] Generate image from text
- [ ] Apply filter
- [ ] Check console for `[FILTERS] Using canvas as source`
- [ ] Crop, resize, remove background - all work
- [ ] Enhance prompt button works

---

## Troubleshooting

### Issue: Push fails with authentication error

```
fatal: Authentication failed
```

**Solution:**

```powershell
# Use Personal Access Token instead of password
git remote set-url origin https://[TOKEN]@github.com/apapadopoulos22/orfeas-ai-studio.git

# Or use SSH:
git remote set-url origin git@github.com:apapadopoulos22/orfeas-ai-studio.git
ssh-keygen -t ed25519
# Add public key to GitHub Settings
```

### Issue: Netlify shows "No builds"

- Verify branch deploy context is set to `main`
- Check GitHub connection under Settings
- Manually trigger build: **Deploys** → **Trigger deploy**

### Issue: Site shows 404 on index

- Verify publish directory is `.` (current directory)
- Check that `orfeas-ai-studio.html` is in root
- Manually set `orfeas-ai-studio.html` as index

### Issue: API calls return 404

- Backend endpoint missing
- Check CORS headers set correctly
- Verify API_BASE in HTML matches backend URL

---

## Post-Deployment Monitoring

### Enable Notifications

1. Netlify → Site settings → Notifications
2. Add Slack/Email notification for deployments
3. Get alerts when builds fail

### Monitor Performance

1. Netlify Analytics
2. Check build times
3. Monitor bandwidth usage

### Check Logs

1. **Deploy logs:** Netlify → Deploys → click build
2. **Function logs:** (if using serverless)
3. **Browser console:** F12 on live site

---

## Automated Workflow

After this setup, your workflow becomes:

```
You make code changes
        ↓
git commit + git push origin main
        ↓
GitHub receives push
        ↓
Netlify webhook triggered
        ↓
Netlify builds site
        ↓
Netlify deploys to CDN
        ↓
Live site updated (1-2 minutes)
        ↓
Everyone sees new version
```

---

## Next Steps

After successful deployment:

1. ✅ Test live site thoroughly
2. ✅ Verify all features work
3. ✅ Monitor build logs for errors
4. ✅ Set up monitoring/alerts
5. ✅ Document your deployment

**Task Complete:** GitHub + Netlify connected and auto-deploying! 🚀

---

**Created:** October 26, 2025
**Guide Version:** 1.0
**Status:** Ready to follow
