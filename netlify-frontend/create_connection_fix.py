#!/usr/bin/env python3
"""
Create Updated Deployment Package with Connection Fix
"""

import zipfile
from pathlib import Path
import time

def create_connection_fix_deployment():
    """Create deployment with connection fix"""

    print(" Creating Connection Fix Deployment")
    print("="*40)

    # Paths
    frontend_dir = Path("c:/Users/johng/Documents/Erevus/orfeas/netlify-frontend")
    zip_path = Path("c:/Users/johng/Documents/Erevus/orfeas/ORFEAS-Connection-Fix.zip")

    # Files to include
    files_to_include = [
        ("connection-fix.html", "index.html"),  # Main page with connection diagnostics
        ("index-simple.html", "portal.html"),  # Original portal as backup
        ("studio.html", "studio.html"),        # 3D studio
        ("netlify.toml", "netlify.toml")       # Configuration
    ]

    # Create deployment zip
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for source_file, zip_name in files_to_include:
            file_path = frontend_dir / source_file
            if file_path.exists():
                zipf.write(file_path, zip_name)
                print(f" Added: {source_file} → {zip_name}")
            else:
                print(f"  Missing: {source_file}")

    # Get file size
    size_kb = zip_path.stat().st_size / 1024

    print(f"\n Connection Fix Deployment:")
    print(f"    File: {zip_path}")
    print(f"    Size: {size_kb:.1f} KB")
    print(f"    Features: Connection diagnostics + solutions")

    print(f"\n DEPLOY THIS VERSION:")
    print(f"   1. Go to: https://app.netlify.com/drop")
    print(f"   2. Drag: ORFEAS-Connection-Fix.zip")
    print(f"   3. Will show diagnostics and solutions automatically")

    print(f"\n This version detects HTTPS→HTTP issues and provides solutions!")

    return zip_path

if __name__ == "__main__":
    create_connection_fix_deployment()
