#!/usr/bin/env bash
# ORFEAS AI - Quick Auto-Deploy Script
# Run this once to set up automatic Netlify deployments

echo "=========================================="
echo "ORFEAS AI - AUTOMATIC NETLIFY DEPLOYMENT"
echo "=========================================="
echo ""

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "✓ Git found: $(git --version)"
echo ""

# Get current directory
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$PROJECT_ROOT" || exit 1

echo "Project root: $PROJECT_ROOT"
echo ""

# Step 1: Initialize Git if needed
if [ ! -d ".git" ]; then
    echo "[1/5] Initializing Git repository..."
    git init
    git config user.name "ORFEAS Deploy Bot"
    git config user.email "deploy@orfeas-ai.local"
else
    echo "[1/5] ✓ Git repository already exists"
fi

# Step 2: Add files
echo "[2/5] Staging Netlify configuration files..."
git add netlify.toml .env.netlify netlify/functions/* *.html

# Step 3: Commit if changes exist
if [ -n "$(git status --short)" ]; then
    echo "[3/5] Committing changes..."
    git commit -m "chore: automatic Netlify deployment configuration"
else
    echo "[3/5] ✓ Files already committed"
fi

# Step 4: Show next steps
echo ""
echo "[4/5] Displaying next steps..."
echo ""
echo "=========================================="
echo "DEPLOYMENT SETUP ALMOST COMPLETE!"
echo "=========================================="
echo ""
echo "Now complete these manual steps:"
echo ""
echo "1. CREATE GITHUB REPOSITORY"
echo "   → Visit: https://github.com/new"
echo "   → Create new repository"
echo "   → Copy repository URL"
echo ""
echo "2. PUSH TO GITHUB"
echo "   → Run: git remote add origin YOUR_REPO_URL"
echo "   → Run: git branch -M main"
echo "   → Run: git push -u origin main"
echo ""
echo "3. CONNECT TO NETLIFY"
echo "   → Visit: https://app.netlify.com"
echo "   → Sign in with GitHub"
echo "   → Click: New site from Git"
echo "   → Select your repository"
echo "   → Accept defaults (will use netlify.toml)"
echo "   → Site deploys automatically!"
echo ""
echo "4. ADD ENVIRONMENT VARIABLES"
echo "   → In Netlify: Settings → Environment variables"
echo "   → Add variables from .env.netlify"
echo ""
echo "5. TEST AUTOMATIC DEPLOYMENT"
echo "   → Make a change to a file"
echo "   → Run: git commit -am 'test: automatic deployment'"
echo "   → Run: git push origin main"
echo "   → Watch: https://app.netlify.com (should deploy in ~1 min)"
echo ""
echo "[5/5] ✓ Setup complete!"
echo ""
echo "=========================================="
echo "✅ AUTOMATIC DEPLOYMENT IS READY"
echo "=========================================="
echo ""
echo "Every future push to main branch will:"
echo "  1. Trigger Netlify build"
echo "  2. Deploy your site"
echo "  3. Update live URL automatically"
echo ""
