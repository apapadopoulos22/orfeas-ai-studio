#!/usr/bin/env python3
"""
ORFEAS Netlify Deployment Creator
Creates deployment-ready zip file for instant Netlify deployment
"""

import zipfile
import os
import json
import time
from pathlib import Path

def create_netlify_deployment():
    """Create deployment zip for Netlify"""

    print("ðŸš€ ORFEAS Netlify Deployment Creator")
    print("="*50)

    # Paths
    frontend_dir = Path("c:/Users/johng/Documents/Erevus/orfeas/netlify-frontend")
    zip_path = Path("c:/Users/johng/Documents/Erevus/orfeas/ORFEAS-Netlify-Deploy.zip")

    # Files to include
    files_to_include = [
        "index.html",
        "studio.html",
        "netlify.toml",
        "package.json",
        "README.md",
        "deployment-config.json"
    ]

    # Create deployment zip
    print(f"ðŸ“¦ Creating deployment package: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in files_to_include:
            file_path = frontend_dir / file_name
            if file_path.exists():
                zipf.write(file_path, file_name)
                print(f"âœ… Added: {file_name}")
            else:
                print(f"âš ï¿½  Missing: {file_name}")

    # Get file size
    size_mb = zip_path.stat().st_size / (1024 * 1024)

    print(f"\nðŸ“Š Deployment Package Created:")
    print(f"   ï¿½ File: {zip_path}")
    print(f"   ï¿½ Size: {size_mb:.2f} MB")
    print(f"   ðŸ•’ Created: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Read deployment config
    config_path = frontend_dir / "deployment-config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)

        print(f"\nï¿½ Server Configuration:")
        print(f"   ï¿½ Local: {config['server_urls']['localhost']}")
        print(f"   ï¿½ Network: {config['server_urls']['local_network']}")
        print(f"   âœ… CORS Ready: {config['cors_configured']}")

    print(f"\nðŸš€ DEPLOYMENT INSTRUCTIONS:")
    print(f"   1. Go to https://app.netlify.com/drop")
    print(f"   2. Drag this file: {zip_path}")
    print(f"   3. Site will deploy instantly!")
    print(f"   4. Test connection to your server")

    print(f"\nðŸ”§ ALTERNATIVE DEPLOYMENT:")
    print(f"   1. Extract zip to folder")
    print(f"   2. Connect GitHub repo to Netlify")
    print(f"   3. Auto-deploy on git push")

    # Create quick deployment guide
    guide_path = Path("c:/Users/johng/Documents/Erevus/orfeas/NETLIFY_DEPLOY_GUIDE.txt")
    with open(guide_path, 'w') as f:
        f.write("ORFEAS NETLIFY DEPLOYMENT GUIDE\n")
        f.write("="*40 + "\n\n")
        f.write(f"Deployment Package: {zip_path}\n")
        f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("INSTANT DEPLOYMENT:\n")
        f.write("1. Go to https://app.netlify.com/drop\n")
        f.write(f"2. Drag: {zip_path.name}\n")
        f.write("3. Site deploys automatically!\n\n")
        f.write("TESTING:\n")
        f.write("1. Visit deployed site\n")
        f.write("2. Check server connection status\n")
        f.write("3. Test file upload and 3D generation\n\n")
        f.write("TROUBLESHOOTING:\n")
        f.write("- Red status = server not reachable\n")
        f.write("- Green status = ready for 3D generation\n")
        f.write("- Check local server is running on port 5002\n")
        f.write("- Ensure firewall allows port 5002\n\n")
        f.write("NETWORK ACCESS:\n")
        f.write("- Same WiFi: Users can access directly\n")
        f.write("- Internet: Use ngrok for external access\n")
        f.write("- VPN: Most secure for production\n")

    print(f"ðŸ“‹ Deployment guide saved: {guide_path}")

    return zip_path

if __name__ == "__main__":
    deployment_zip = create_netlify_deployment()

    print(f"\nï¿½ READY FOR DEPLOYMENT!")
    print(f"Your ORFEAS frontend is ready to go global while keeping")
    print(f"your powerful local AI processing secure and private!")
