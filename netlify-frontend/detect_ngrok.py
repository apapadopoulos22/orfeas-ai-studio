#!/usr/bin/env python3
"""
NGROK URL Helper for ORFEAS Deployment
Automatically detects ngrok tunnel and creates updated deployment
"""

import requests
import json
import time
from pathlib import Path

def get_ngrok_url():
    """Get the ngrok HTTPS URL if tunnel is running"""
    try:
        # ngrok exposes API on localhost:4040
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            tunnels = response.json()

            for tunnel in tunnels.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    public_url = tunnel.get('public_url')
                    if public_url and 'ngrok.io' in public_url:
                        return public_url

        return None
    except:
        return None

def create_ngrok_deployment(ngrok_url):
    """Create deployment package with ngrok URL pre-configured"""

    print(f" Creating ngrok-enabled deployment")
    print(f" Tunnel URL: {ngrok_url}")

    # Create updated index.html with ngrok URL
    frontend_dir = Path("c:/Users/johng/Documents/Erevus/orfeas/netlify-frontend")

    # Read the connection-fix template
    template_path = frontend_dir / "connection-fix.html"
    if not template_path.exists():
        print(" Template not found")
        return None

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update the default server URL to ngrok
    updated_content = content.replace(
        'value="http://192.168.1.57:5002"',
        f'value="{ngrok_url}"'
    ).replace(
        'http://localhost:5002',
        ngrok_url
    )

    # Save ngrok version
    ngrok_index_path = frontend_dir / "index-ngrok.html"
    with open(ngrok_index_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f" Created ngrok-enabled frontend: {ngrok_index_path}")

    # Create deployment zip
    import zipfile
    zip_path = Path("c:/Users/johng/Documents/Erevus/orfeas/ORFEAS-ngrok-Deploy.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(ngrok_index_path, "index.html")
        zipf.write(frontend_dir / "studio.html", "studio.html")
        zipf.write(frontend_dir / "netlify.toml", "netlify.toml")

    size_kb = zip_path.stat().st_size / 1024

    print(f"\n NGROK DEPLOYMENT READY:")
    print(f"    File: {zip_path}")
    print(f"    Size: {size_kb:.1f} KB")
    print(f"    Pre-configured for: {ngrok_url}")

    return zip_path

def main():
    print(" NGROK URL Detection for ORFEAS")
    print("="*40)

    # Check if ngrok is running
    ngrok_url = get_ngrok_url()

    if ngrok_url:
        print(f" ngrok tunnel detected!")
        print(f" Public URL: {ngrok_url}")

        # Test if our server is accessible through ngrok
        try:
            test_url = f"{ngrok_url}/api/health"
            print(f" Testing: {test_url}")

            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f" ORFEAS server accessible via ngrok!")
                print(f"   Server: {data.get('server', 'Unknown')}")
                print(f"   Status: {data.get('status', 'Unknown')}")

                # Create deployment package
                zip_path = create_ngrok_deployment(ngrok_url)

                if zip_path:
                    print(f"\n READY FOR DEPLOYMENT:")
                    print(f"   1. Go to: https://app.netlify.com/drop")
                    print(f"   2. Drag: {zip_path.name}")
                    print(f"   3. Site will connect to: {ngrok_url}")
                    print(f"   4. Test global HTTPS access!")

                    print(f"\n SUCCESS! Global HTTPS access to your local ORFEAS AI!")

            else:
                print(f" ORFEAS server not responding via ngrok")
                print(f"   HTTP {response.status_code}")

        except Exception as e:
            print(f" Error testing ngrok connection: {e}")

    else:
        print(" No ngrok tunnel detected")
        print("\n Setup Steps:")
        print("   1. Sign up: https://ngrok.com/signup")
        print("   2. Get authtoken: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("   3. Install token: ngrok config add-authtoken YOUR_TOKEN")
        print("   4. Start tunnel: ngrok http 5002")
        print("   5. Run this script again")

        print("\n Alternative: Use local network access")
        print("   URL: http://192.168.1.57:5002 (same WiFi users)")

if __name__ == "__main__":
    main()
