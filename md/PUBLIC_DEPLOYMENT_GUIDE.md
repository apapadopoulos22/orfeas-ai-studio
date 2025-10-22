# ORFEAS BACKEND PUBLIC DEPLOYMENT GUIDE

## # # ORFEAS AI Project

## # # Deploy local AI backend to public internet with HTTPS

---

## # # [TARGET] DEPLOYMENT OPTIONS

## # # **OPTION 1: NGROK TUNNEL** [FAST] (FASTEST - 2 MINUTES)

## # # Perfect for

- Quick testing and demos
- Temporary public access
- Instant HTTPS without certificates
- Free tier available

## # # Pros

- [OK] Setup in under 2 minutes
- [OK] Automatic HTTPS (no cert config)
- [OK] No router configuration needed
- [OK] Works behind any firewall
- [OK] Web interface for request inspection

## # # Cons

- [WARN] Free tier: 2-hour sessions (must reconnect)
- [WARN] Random URL changes on restart (upgrade for static)
- [WARN] 40 requests/minute limit (free tier)

## # # Setup

```powershell

## Install ngrok

winget install ngrok

## Deploy backend

.\DEPLOY_BACKEND_PUBLIC.ps1 -Method ngrok

## Output example

## [SIGNAL] PUBLIC URL: https://a1b2c3d4.ngrok.io

```text

## # # Pricing

- Free: 1 agent, random URLs, 40 req/min
- Basic ($8/mo): Static domain, 60 req/min
- Pro ($20/mo): Multiple domains, unlimited bandwidth

---

## # # **OPTION 2: CLOUDFLARE TUNNEL** [SECURE] (PRODUCTION GRADE)

## # # Perfect for (2)

- Long-term deployment
- Production applications
- Free forever solution
- Enterprise security

## # # Pros (2)

- [OK] Completely free (no limits)
- [OK] DDoS protection included
- [OK] Persistent URL (doesn't change)
- [OK] Custom domain support
- [OK] Better performance (Cloudflare CDN)

## # # Cons (2)

- [WAIT] Slightly longer setup (5-10 minutes)
- [EDIT] Requires Cloudflare account (free)

## # # Setup (2)

```powershell

## Install cloudflared

Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"

## Deploy backend

.\DEPLOY_BACKEND_PUBLIC.ps1 -Method cloudflare

## Follow browser prompts to login

## Get permanent *.trycloudflare.com URL

```text

## # # Features

- Zero Trust security
- Access policies (IP whitelist, auth)
- Analytics and logs
- Custom domains (with Cloudflare DNS)

---

## # # **OPTION 3: PORT FORWARDING + DDNS** [CONFIG] (TRADITIONAL)

## # # Perfect for (3)

- Full control over deployment
- No third-party dependencies
- Custom domain with your ISP

## # # Pros (3)

- [OK] No monthly costs
- [OK] Direct connection (lowest latency)
- [OK] Full control

## # # Cons (3)

- [WARN] Requires router access (admin password)
- [WARN] Manual HTTPS setup (Let's Encrypt recommended)
- [WARN] Security configuration complexity
- [WARN] ISP may block port 80/443

## # # Setup (3)

1. **Router Port Forwarding:**

   ```text
   Login: http://192.168.1.1 (or your router IP)
   Navigate: Advanced → Port Forwarding
   Add Rule:

- External Port: 5000
- Internal IP: [Your PC's local IP]
- Internal Port: 5000
- Protocol: TCP

   ```text

1. **Get Public IP:**

   ```powershell
   (Invoke-WebRequest -Uri "https://api.ipify.org").Content

   # Example output: 203.0.113.45

   ```text

1. **Setup Dynamic DNS:**

- No-IP: https://www.noip.com (free subdomain)
- DuckDNS: https://www.duckdns.org (simple)
- Dynu: https://www.dynu.com (advanced)

1. **HTTPS with Caddy (Recommended):**

   ```powershell

   # Install Caddy reverse proxy

   winget install Caddy

   # Caddyfile config:

   yourdomain.ddns.net {
       reverse_proxy localhost:5000
   }

   # Auto-generates Let's Encrypt cert

   caddy run

   ```text

---

## # # [LAUNCH] QUICK START (RECOMMENDED: NGROK)

```powershell

## 1. Deploy backend to public internet

.\DEPLOY_BACKEND_PUBLIC.ps1 -Method ngrok

## 2. Copy public URL from output

## Example: https://a1b2c3d4.ngrok.io

## 3. Update frontend automatically

.\UPDATE_FRONTEND_PUBLIC_URL.ps1

## 4. Test connection

Invoke-WebRequest -Uri "https://a1b2c3d4.ngrok.io/api/health"

```text

## # # That's it

---

## # #  SECURITY BEST PRACTICES

## # # **1. Enable CORS Properly**

```python

## backend/main.py already configured

CORS(app, origins=["*"])  # In production, whitelist your domains

```text

## # # **2. Add API Authentication** (Optional but Recommended)

```python

## Add to main.py

API_KEY = os.getenv('ORFEAS_API_KEY', 'your-secret-key')

@app.before_request
def verify_api_key():
    if request.endpoint == 'health':
        return  # Allow health checks

    key = request.headers.get('X-API-Key')
    if key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

```text

```javascript
// In orfeas-studio.html
fetch(BACKEND_URL + "/api/generate", {
  headers: {
    "X-API-Key": "your-secret-key",
  },
});

```text

## # # **3. Rate Limiting** (Already Implemented)

```python

## backend/validation.py has RateLimiter class

## Default: 10 requests/minute per IP

```text

## # # **4. HTTPS Only** (Enforced by Ngrok/Cloudflare)

Both Ngrok and Cloudflare automatically provide HTTPS.

---

## # # [STATS] MONITORING & DEBUGGING

## # # **Ngrok Web Interface**

```text
http://localhost:4040

```text

- View all requests in real-time
- Replay requests for testing
- Inspect headers and payloads
- Check response times

## # # **Backend Logs**

```powershell

## View live logs

Get-Content backend.log -Wait

## Search for errors

Select-String -Path backend.log -Pattern "ERROR"

```text

## # # **GPU Utilization**

```powershell

## Check GPU status

nvidia-smi

## Monitor continuously (update every 1 second)

nvidia-smi -l 1

```text

---

## # # [CONTROL] GPU OPTIMIZATION

Backend automatically uses GPU if available:

```python

## Detected in main.py startup

## [OK] GPU ACCELERATION: ENABLED

## Device: NVIDIA GeForce RTX 4080

## Memory: 16.00 GB total

## CUDA: 12.1

```text

## # # Maximize Performance

1. Close other GPU applications (games, video editing)

2. Increase `MAX_BATCH_SIZE` in `main.py` (if high VRAM)

3. Enable `torch.cuda.amp` for mixed precision (faster inference)

---

## # # [WEB] DEPLOYING FRONTEND (COMPLETE SOLUTION)

Once backend is public, deploy frontend to static hosting:

## # # **Netlify (Recommended)**

```bash

## 1. Install Netlify CLI

npm install -g netlify-cli

## 2. Deploy

cd /path/to/orfeas
netlify deploy --prod

## 3. Set environment variable

## Site settings → Environment → Add variable

## BACKEND_URL = https://your-ngrok-url.io

```text

## # # **Vercel**

```bash

## 1. Install Vercel CLI

npm install -g vercel

## 2. Deploy

vercel --prod

## 3. Add environment variable in dashboard

```text

## # # **GitHub Pages**

```bash

## 1. Create gh-pages branch

git checkout -b gh-pages

## 2. Copy orfeas-studio.html to index.html

cp orfeas-studio.html index.html

## 3. Push to GitHub

git add .
git commit -m "Deploy frontend"
git push origin gh-pages

## 4. Enable GitHub Pages in repo settings

```text

---

## # # [ORFEAS] COMPLETE DEPLOYMENT ARCHITECTURE

```text

  USER DEVICE (Phone, Laptop, Tablet)
  > https://orfeas-studio.netlify.app

                       HTTPS
                      â–¼

  NGROK/CLOUDFLARE TUNNEL
  > https://abc123.ngrok.io → localhost:5000

                       HTTP (Local)
                      â–¼

  YOUR PC (Windows)
  > ORFEAS Backend (Flask + SocketIO)
  > Python AI Stack (PyTorch, Hunyuan3D)
  > GPU (CUDA, DirectML)
  > Local Models (AUTOMATIC1111, ComfyUI)

```text

## # # Benefits

- [OK] Users access via HTTPS (secure)
- [OK] Backend runs on your local GPU (powerful)
- [OK] No cloud costs (except optional Ngrok Pro)
- [OK] Full control over AI models and data

---

## # #  TROUBLESHOOTING

## # # **"Backend not starting"**

```powershell

## Check Python errors

cd backend
python main.py

## Install missing dependencies

pip install -r requirements.txt

```text

## # # **"Ngrok tunnel not connecting"**

```powershell

## Check ngrok auth token

ngrok authtoken YOUR_AUTH_TOKEN

## Get token from: https://dashboard.ngrok.com/get-started/your-authtoken

```text

## # # **"Frontend can't connect to backend"**

```powershell

## Verify backend URL in frontend

Select-String -Path orfeas-studio.html -Pattern "BACKEND_URL"

## Should match ngrok URL

```text

## # # **"GPU not detected"**

```powershell

## Check CUDA installation

nvidia-smi

## Reinstall PyTorch with CUDA

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

```text

---

## # #  SUPPORT

## # # Documentation

- Ngrok: https://ngrok.com/docs
- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/

## # # ORFEAS Issues

- Check: `md/` directory for detailed guides
- Logs: `backend.log`
- GPU Issues: `backend/gpu_manager.py`

---

## # # [WARRIOR] ORFEAS PROTOCOL

## # # Maximum efficiency deployment achieved

[ORFEAS] **Backend: Public + GPU-accelerated**
[WEB] **Frontend: Static hosting ready**
[LAUNCH] **Performance: Production grade**

## # # ORFEAS AI - AI SOVEREIGNTY NOW
