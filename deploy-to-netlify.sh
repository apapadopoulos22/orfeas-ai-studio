#!/bin/bash
# Netlify Deployment Script for ORFEAS AI Frontend
# This script prepares and deploys the frontend to Netlify

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ORFEAS AI - Netlify Frontend Deployment Script            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ ERROR: Git is not installed"
    echo "Please install Git from https://git-scm.com/"
    exit 1
fi

# Check if netlify-cli is installed
if ! command -v netlify &> /dev/null; then
    echo "⚠️  netlify-cli not found. Installing..."
    npm install -g netlify-cli
fi

# Get user input
echo ""
read -p "Enter your ngrok URL (https://xxxx.ngrok.io): " NGROK_URL
if [ -z "$NGROK_URL" ]; then
    echo "❌ ngrok URL cannot be empty"
    exit 1
fi

read -p "Enter GitHub repository name (e.g., orfeas-ai-frontend): " REPO_NAME
if [ -z "$REPO_NAME" ]; then
    echo "❌ Repository name cannot be empty"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  ngrok URL: $NGROK_URL"
echo "  Repository: $REPO_NAME"
echo ""

# Create project directory
DEPLOY_DIR="/tmp/orfeas-netlify-deploy"
rm -rf "$DEPLOY_DIR" 2>/dev/null
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# Copy files
echo "[1/5] Copying project files..."
cp /path/to/synexa-style-studio.html .
cp /path/to/netlify.toml .
cp /path/to/QUICK_START_PRODUCTION.txt .

# Update netlify.toml with ngrok URL
echo "[2/5] Updating netlify.toml with ngrok URL..."
sed -i "s|YOUR_NGROK_URL_HERE|$NGROK_URL|g" netlify.toml

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "[3/5] Initializing git repository..."
    git init
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
fi

# Add and commit files
echo "[4/5] Committing files..."
git add .
git config user.email "deployer@orfeas.local"
git config user.name "ORFEAS Deployer"
git commit -m "ORFEAS AI Studio - Frontend deployment to Netlify with ngrok backend" || true

# Deploy to Netlify
echo "[5/5] Deploying to Netlify..."
netlify deploy --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Visit your Netlify site URL"
echo "  2. Check console: [CONFIG] API_BASE should show $NGROK_URL"
echo "  3. Test image upload and generation"
echo ""
echo "Remember: Keep ngrok tunnel running with START_NGROK_TUNNEL.bat"
echo ""
