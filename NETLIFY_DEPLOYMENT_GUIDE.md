╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║  NETLIFY FRONTEND DEPLOYMENT WITH LOCAL BACKEND GUIDE                 ║
║                                                                        ║
║  Deploy frontend to Netlify                                           ║
║  Keep backend on local machine with dynamic IP                        ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

═════════════════════════════════════════════════════════════════════════
ARCHITECTURE OVERVIEW
═════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│  Users Worldwide                                                    │
│  → https://your-app.netlify.app (Frontend - Netlify CDN)           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                    API requests to /api/*
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Netlify Proxy                                                      │
│  (netlify.toml redirects)                                           │
│  Routes /api/* → https://xxx.ngrok.io                             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                      Internet (Encrypted)
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  ngrok Tunnel (https://xxx.ngrok.io)                               │
│  Public HTTPS URL → Your local machine                             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Your Local Machine                                                 │
│  Backend: http://127.0.0.1:5000 (Flask)                            │
│  GPU: NVIDIA RTX 3090                                              │
│  Processing: Hunyuan3D-2.1 Model                                   │
└─────────────────────────────────────────────────────────────────────┘

═════════════════════════════════════════════════════════════════════════
STEP 1: INSTALL NGROK (Creates Public URL for Local Backend)
═════════════════════════════════════════════════════════════════════════

What is ngrok?
  • Creates a secure tunnel from internet to your local machine
  • Generates a public HTTPS URL for your local backend
  • Handles dynamic IP changes automatically
  • Free tier: 1 tunnel at a time, bandwidth limited but sufficient for testing

Step 1a: Download ngrok

  1. Visit: https://ngrok.com/download
  2. Download for Windows
  3. Extract to a folder (e.g., C:\ngrok\)

Step 1b: Install/Verify
  • Copy ngrok.exe to a known location or add to PATH
  • Test: Open Command Prompt and type: ngrok version
  • Expected: ngrok version X.X.X

Step 1c: Create ngrok Account (Free)

  1. Visit: https://dashboard.ngrok.com/signup
  2. Sign up (free account)
  3. Get your authtoken from dashboard
  4. Run in PowerShell:
     ngrok config add-authtoken YOUR_TOKEN_HERE

═════════════════════════════════════════════════════════════════════════
STEP 2: START LOCAL BACKEND
═════════════════════════════════════════════════════════════════════════

In PowerShell Terminal 1:

  cd c:\Users\johng\Documents\oscar\backend
  python main.py

Expected Output:

- Running on http://127.0.0.1:5000
- GPU initialized
- Ready for requests

Wait: 30-60 seconds for full initialization

═════════════════════════════════════════════════════════════════════════
STEP 3: START NGROK TUNNEL
═════════════════════════════════════════════════════════════════════════

In PowerShell Terminal 2 (KEEP RUNNING):

  ngrok http 5000

Expected Output:
  ┌──────────────────────────────────────────────────────────┐
  │ Session Status    | online                               │
  │ Session URL       | https://xxxx-xxxx-xxxx.ngrok.io      │
  │ Forwarding        | https://xxxx-xxxx-xxxx.ngrok.io → 127.0.0.1:5000 │
  └──────────────────────────────────────────────────────────┘

COPY THIS URL: https://xxxx-xxxx-xxxx.ngrok.io

Note: URL changes when you restart ngrok. Keep ngrok terminal open!

═════════════════════════════════════════════════════════════════════════
STEP 4: UPDATE NETLIFY.TOML WITH NGROK URL
═════════════════════════════════════════════════════════════════════════

File: c:\Users\johng\Documents\oscar\netlify.toml

Find and replace YOUR_NGROK_URL_HERE with your actual ngrok URL:

  Example: https://a1b2c3d4e5f6.ngrok.io

Lines to update:
  • Line 10: environment = { API_BASE = "YOUR_NGROK_URL_HERE" }
  • Line 15: to = "YOUR_NGROK_URL_HERE/api/:splat"
  • Line 19: to = "YOUR_NGROK_URL_HERE/health"

After updating, it should look like:
  environment = { API_BASE = "https://a1b2c3d4e5f6.ngrok.io" }
  to = "https://a1b2c3d4e5f6.ngrok.io/api/:splat"

═════════════════════════════════════════════════════════════════════════
STEP 5: DEPLOY TO NETLIFY
═════════════════════════════════════════════════════════════════════════

Option A: Git-Based Deployment (RECOMMENDED)

  1. Create GitHub Repository
     • Create new repo on GitHub (e.g., orfeas-ai-frontend)
     • Clone locally: git clone https://github.com/your-user/orfeas-ai-frontend.git

  2. Add Files to Git
     cd orfeas-ai-frontend
     cp c:\Users\johng\Documents\oscar\synexa-style-studio.html .
     cp c:\Users\johng\Documents\oscar\netlify.toml .
     cp c:\Users\johng\Documents\oscar\QUICK_START_PRODUCTION.txt .
     git add .
     git commit -m "ORFEAS AI Studio - Frontend deployment"
     git push origin main

  3. Deploy on Netlify
     • Visit: https://app.netlify.com
     • Click: "New site from Git"
     • Select: Your GitHub repository
     • Build settings:
       - Base directory: (leave empty)
       - Build command: (leave empty - static site)
       - Publish directory: . (current directory)
     • Click: "Deploy site"

  4. Wait for Deployment (usually < 1 minute)
     Check the deployment log for any errors

Option B: Direct Upload (QUICK TEST)

  1. Visit: https://app.netlify.com/drop
  2. Drag and drop: synexa-style-studio.html
  3. Netlify creates temporary site (URL like: xxx-xxx-xxx.netlify.app)
  4. Upload netlify.toml to configure API routing
  5. Test connection before moving to permanent site

═════════════════════════════════════════════════════════════════════════
STEP 6: TEST DEPLOYMENT
═════════════════════════════════════════════════════════════════════════

Once deployed to Netlify:

1. Open your Netlify site in browser:
   https://your-site-name.netlify.app

2. Check browser console (F12):
   Look for: [CONFIG] API_BASE: https://xxxx.ngrok.io
   (Should show your ngrok URL, NOT localhost)

3. Test upload:
   • Upload a test image
   • Click "Generate 3D Model"
   • Wait for processing

4. Monitor:
   • Check ngrok terminal (requests showing up?)
   • Check backend logs (GPU processing?)
   • Check browser console (any errors?)

═════════════════════════════════════════════════════════════════════════
NGROK URL RENEWAL & LONG-TERM SETUP
═════════════════════════════════════════════════════════════════════════

Problem: ngrok URL changes when you restart
Solution: Use ngrok reserved domain (upgrade account) or automation

Option 1: Manual Update (Every Restart)
  • Restart ngrok → Get new URL
  • Update netlify.toml with new URL
  • Commit and push to GitHub → Netlify auto-redeploys

Option 2: Use DuckDNS (FREE Alternative to ngrok)
  • More stable than ngrok free tier
  • Static domain name
  • See STEP 7 below

Option 3: CloudFlare Tunnel (FREE, Professional)
  • CloudFlare Tunnel → Expose local to internet
  • Custom domain support
  • No URL changes
  • More complex setup

═════════════════════════════════════════════════════════════════════════
STEP 7: ALTERNATIVE - USE DUCKDNS (OPTIONAL)
═════════════════════════════════════════════════════════════════════════

DuckDNS provides free dynamic DNS without needing ngrok.

Setup (5 minutes):

  1. Visit: https://www.duckdns.org
  2. Sign in with GitHub
  3. Create subdomain: yourname.duckdns.org
  4. Get token from dashboard
  5. Download DuckDNS update script (Windows)
  6. Set it to update every 5 minutes (keeps IP current)
  7. Configure port forwarding on router:
     • Forward port 5000 → your local machine IP
     • Enable HTTPS (use Let's Encrypt)
  8. Update netlify.toml:
     API_BASE = "https://yourname.duckdns.org:5000"

Advantages:
  • Static domain name (yourname.duckdns.org)
  • No URL changes needed
  • Free and open source
  • More control

Disadvantages:
  • Requires port forwarding on home router
  • Slightly more complex setup
  • Your home IP becomes known

═════════════════════════════════════════════════════════════════════════
NETLIFY.TOML CONFIGURATION EXPLAINED
═════════════════════════════════════════════════════════════════════════

[build]
  publish = "."
  → Netlify serves everything from current directory
  command = "echo 'Frontend deployment ready'"
  → No build needed (static HTML)

[[redirects]]
  from = "/api/*"
  to = "YOUR_NGROK_URL_HERE/api/:splat"
  → Frontend request to /api/upload → Backend /api/upload via ngrok

[[redirects]]
  from = "/*"
  to = "synexa-style-studio.html"
  → Serve synexa-style-studio.html for all requests

═════════════════════════════════════════════════════════════════════════
ENVIRONMENT-BASED API CONFIGURATION
═════════════════════════════════════════════════════════════════════════

Updated frontend code (synexa-style-studio.html):

  const API_BASE =
    (typeof window.API_BASE !== 'undefined' && window.API_BASE) ||
    (process.env.REACT_APP_API_BASE) ||
    (window.location.hostname === 'localhost' ? 'http://127.0.0.1:5000' :
     window.location.origin);

Logic:

  1. Check for window.API_BASE (set by Netlify)
  2. Check for process.env (build-time variable)
  3. If localhost → use http://127.0.0.1:5000 (development)
  4. Otherwise → use current origin (Netlify will redirect to ngrok)

Behavior:
  • Local: http://127.0.0.1:5000 (direct)
  • Netlify: ngrok URL (via netlify.toml redirect)
  • Production: https://api.orfeas.ai (when ready)

═════════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
═════════════════════════════════════════════════════════════════════════

Issue 1: "Cannot connect to backend" on Netlify
  Cause: ngrok URL not updated in netlify.toml
  Solution:
    1. Get ngrok URL: ngrok http 5000
    2. Update netlify.toml
    3. Commit and push to GitHub
    4. Netlify auto-redeploys

Issue 2: "API_BASE shows localhost on Netlify"
  Cause: Frontend not detecting environment properly
  Solution:
    1. Open browser DevTools (F12)
    2. Check console: [CONFIG] API_BASE: should show ngrok URL
    3. If wrong, netlify.toml isn't configured
    4. Check netlify.toml for YOUR_NGROK_URL_HERE placeholders

Issue 3: "CORS error in browser console"
  Cause: ngrok URL not properly configured
  Solution:
    1. Check ngrok is running and accessible
    2. Test in browser: https://xxxx.ngrok.io/health
    3. Should see JSON response
    4. If not, backend not responding via ngrok

Issue 4: "ngrok URL keeps changing"
  Problem: Free ngrok tier generates new URL on restart
  Solution:
    Option A: Pay for ngrok reserved domain ($5-10/month)
    Option B: Use DuckDNS (free, see STEP 7)
    Option C: Keep terminal running (ngrok URL stable while running)

Issue 5: "Port 5000 already in use"
  Cause: Another application using port 5000
  Solution:
    netstat -ano | findstr :5000
    (Find PID, then stop that process)
    Or: Start backend on different port
    ngrok http 5001 (if backend on 5001)

═════════════════════════════════════════════════════════════════════════
SECURITY CONSIDERATIONS
═════════════════════════════════════════════════════════════════════════

⚠️ Important for Production:

ngrok URL is PUBLIC (anyone can access):
  ✓ For testing: OK (temporary)
  ✗ For production: NOT recommended (bandwidth limited, URL expires)

Production Solution:

  1. Use CloudFlare Tunnel (more secure)
  2. Set up authenticated ngrok (requires upgrade)
  3. Use custom domain (DuckDNS + SSL)
  4. Deploy backend to cloud (AWS, Google Cloud, Azure)
  5. Use API Gateway/Load Balancer with security rules

For Now (Testing):
  • ngrok is fine for development/testing
  • Keep backend not exposed to sensitive data
  • Monitor ngrok usage (free tier has bandwidth limits)

═════════════════════════════════════════════════════════════════════════
DEPLOYMENT CHECKLIST
═════════════════════════════════════════════════════════════════════════

Before Deploying:
  ☐ Backend running locally (http://127.0.0.1:5000)
  ☐ ngrok installed and configured
  ☐ ngrok tunnel active (ngrok http 5000 running)
  ☐ Got ngrok URL (https://xxxx.ngrok.io)
  ☐ Updated netlify.toml with ngrok URL
  ☐ synexa-style-studio.html updated with environment detection
  ☐ Files committed to GitHub
  ☐ Netlify account created

Deployment:
  ☐ GitHub repo created and connected to Netlify
  ☐ Deploy triggered (auto or manual)
  ☐ Build completed successfully
  ☐ Site URL generated (https://your-site.netlify.app)

Post-Deployment:
  ☐ Opened Netlify site in browser
  ☐ Checked browser console for API_BASE config
  ☐ Tested image upload
  ☐ Tested 3D generation
  ☐ Verified results display correctly
  ☐ Checked all viewers work (Three.js, 3DViewer, download)

═════════════════════════════════════════════════════════════════════════
QUICK START SCRIPT (Windows)
═════════════════════════════════════════════════════════════════════════

Save as: START_NETLIFY_DEPLOYMENT.ps1

```powershell
# Start Local Backend
Write-Host "Starting backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "cd c:\Users\johng\Documents\oscar\backend; python main.py"
Start-Sleep -Seconds 5

# Start ngrok tunnel
Write-Host "Starting ngrok tunnel..." -ForegroundColor Green
Write-Host "ngrok URL will appear below - copy it!" -ForegroundColor Yellow
ngrok http 5000

# After ngrok starts, user will see URL
# User should then:
# 1. Copy ngrok URL
# 2. Update netlify.toml
# 3. Commit to GitHub
# 4. Netlify auto-deploys
```

Run with:
  powershell -ExecutionPolicy Bypass -File START_NETLIFY_DEPLOYMENT.ps1

═════════════════════════════════════════════════════════════════════════
FINAL NOTES
═════════════════════════════════════════════════════════════════════════

This setup allows:
  ✓ Frontend on Netlify (CDN, fast, worldwide)
  ✓ Backend on local machine (develop, test, modify easily)
  ✓ Dynamic IP handled (ngrok automatically)
  ✓ Free tier suitable for development
  ✓ Easy to upgrade when ready

When you're ready for production:
  • Deploy backend to cloud (AWS, Heroku, etc.)
  • Update Netlify with production API endpoint
  • Use CloudFlare or similar for security/DDoS protection
  • Enable authentication and rate limiting

═════════════════════════════════════════════════════════════════════════
