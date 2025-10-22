#!/usr/bin/env python3
"""
Simple Netlify Deployment Creator - Fixed for Upload Issues
"""

import zipfile
import os
from pathlib import Path
import time

def create_simple_deployment():
    """Create a minimal deployment package that Netlify will accept"""

    print(" ORFEAS Simple Netlify Deployment")
    print("="*40)

    # Paths
    frontend_dir = Path("c:/Users/johng/Documents/Erevus/orfeas/netlify-frontend")
    zip_path = Path("c:/Users/johng/Documents/Erevus/orfeas/ORFEAS-Simple-Deploy.zip")

    # Essential files only
    files_to_include = [
        ("index-simple.html", "index.html"),  # Rename for main entry
        ("studio.html", "studio.html"),
        ("netlify.toml", "netlify.toml")
    ]

    # Create clean deployment zip
    print(f" Creating simple deployment: {zip_path}")

    if zip_path.exists():
        zip_path.unlink()  # Remove old version

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

    print(f"\n Simple Deployment Created:")
    print(f"    File: {zip_path}")
    print(f"    Size: {size_kb:.1f} KB")
    print(f"    Files: {len(files_to_include)} essential files only")

    print(f"\n UPLOAD INSTRUCTIONS:")
    print(f"   1. Go to: https://app.netlify.com/drop")
    print(f"   2. Drag: ORFEAS-Simple-Deploy.zip")
    print(f"   3. Should upload instantly (small size)")

    print(f"\n Minimal package - no complex dependencies!")

    return zip_path

if __name__ == "__main__":
    create_simple_deployment()
