# ORFEAS Makers Portal - Netlify Deployment Guide

## Overview

This directory contains the Netlify-optimized frontend for the ORFEAS 3D AI Generation system. The frontend runs on Netlify's global CDN while connecting to your local ORFEAS server for AI processing.

## Architecture

- **Frontend**: Hosted on Netlify (global accessibility)
- **Backend**: Local ORFEAS server (AI processing power)
- **Communication**: CORS-enabled REST API + WebSocket fallback

## Deployment Instructions

### 1. Prepare for Deployment

Ensure your local ORFEAS server is running with CORS enabled:

```powershell
cd "C:\Users\johng\Documents\Erevus\orfeas\backend"
C:\Users\johng\anaconda3\python.exe powerful_3d_server.py

```text

### 2. Deploy to Netlify

#### Option A: Drag & Drop (Fastest)

1. Zip the entire `netlify-frontend` folder

2. Go to [Netlify Drop](https://app.netlify.com/drop)

3. Drag the zip file to deploy instantly

#### Option B: Git Integration (Recommended)

1. Push this folder to a GitHub repository

2. Connect the repo to Netlify

3. Set build command: `echo 'Static site ready'`

4. Set publish directory: `.`

#### Option C: Netlify CLI

```powershell

## Install Netlify CLI

npm install -g netlify-cli

## Login to Netlify

netlify login

## Deploy from this directory

cd "C:\Users\johng\Documents\Erevus\orfeas\netlify-frontend"
netlify deploy --prod --dir .

```text

### 3. Configure CORS on Local Server

Update your local server to allow Netlify domain:

```python

## In your backend server file

from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:*",
    "https://*.netlify.app",
    "https://your-custom-domain.com"
])

```text

### 4. Update Frontend Configuration

After deployment, update the default server URL in the frontend:

```javascript
// In index.html and studio.html
const DEFAULT_SERVER_URL = "https://your-ngrok-url.ngrok.io"; // If using ngrok
// OR keep localhost for same-network access
const DEFAULT_SERVER_URL = "http://your-local-ip:5002";

```text

## Network Access Options

### Option 1: Same Network Access

- Frontend: `https://your-site.netlify.app`
- Backend: `http://192.168.1.XXX:5002` (your local IP)
- Users on same WiFi/network can access

### Option 2: Internet Access via ngrok

```powershell

## Install ngrok

## Download from https://ngrok.com/

## Expose local server to internet

ngrok http 5002

```text

Update frontend to use ngrok URL:

```javascript
const DEFAULT_SERVER_URL = "https://abc123.ngrok.io";

```text

### Option 3: VPN Access

- Set up VPN server on your network
- Users connect via VPN to access local server
- Most secure option for production use

## Features Included

### Frontend Capabilities

-  Real-time 3D preview with Three.js
-  WebSocket + polling fallback
-  Multi-format support (STL, GLB, OBJ)
-  Drag & drop file upload
-  Progress tracking with live updates
-  Mobile-responsive design
-  Connection status monitoring

### Backend Integration

-  CORS-enabled API communication
-  File upload/download handling
-  Real-time job progress tracking
-  Error handling and fallbacks
-  Multi-format 3D generation

## Testing Deployment

### 1. Connection Test

Visit your deployed site and check:

- Server connection status (should show green if reachable)
- Upload a test image
- Verify 3D generation works
- Check download functionality

### 2. Network Debugging

If connection fails:

```javascript
// Open browser console on deployed site
fetch("http://your-server-url:5002/api/health")
  .then((r) => r.json())
  .then((data) => console.log("Server response:", data))
  .catch((err) => console.error("Connection failed:", err));

```text

### 3. CORS Verification

Check browser console for CORS errors:

- Red errors = CORS misconfiguration
- Successful requests = properly configured

## Security Considerations

### Production Setup

1. **Firewall Configuration**: Only allow necessary ports

2. **Authentication**: Add API key authentication if needed

3. **Rate Limiting**: Implement request throttling

4. **HTTPS**: Use SSL certificates for production
5. **Network Isolation**: Consider VPN for sensitive operations

### Development Setup

- Current configuration allows open CORS for testing
- Local network access is relatively secure
- Monitor server logs for suspicious activity

## Troubleshooting

### Common Issues

### Connection Refused

- Check if local server is running
- Verify port 5002 is not blocked by firewall
- Ensure correct IP address/URL in frontend

### CORS Errors

- Add Netlify domain to server CORS configuration
- Check preflight OPTIONS requests are handled

### WebSocket Connection Failed

- System automatically falls back to polling
- Check Socket.IO configuration on server

### File Upload Fails

- Verify server accepts multipart/form-data
- Check file size limits
- Monitor server logs for errors

### Performance Optimization

### Frontend Optimizations

- Enable Netlify's asset optimization
- Configure proper caching headers
- Use CDN for Three.js libraries

### Backend Optimizations

- Enable GPU acceleration for AI processing
- Configure proper memory limits
- Use efficient file compression

## Support

For issues with:

- **Deployment**: Check Netlify documentation
- **Local Server**: Check ORFEAS server logs
- **Network**: Verify firewall and network configuration
- **3D Generation**: Test with local frontend first

The cloud frontend provides global accessibility while keeping your powerful local AI processing secure and under your control!
