#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOB AI API Endpoints - Integration Script
==========================================

This script automatically integrates the BOB AI API endpoints blueprint
into the main.py Flask application.

Usage:
    python integrate_bob_ai_api.py

The script will:
1. Check if main.py exists
2. Add import statement if not already present
3. Add blueprint registration if not already present
4. Create backup of original main.py
5. Verify integration

Run this BEFORE starting the backend.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_success(text):
    """Print success message"""
    print(f"✓ {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")


def print_error(text):
    """Print error message"""
    print(f"✗ {text}")


def check_file_exists(filepath):
    """Check if file exists"""
    if not os.path.exists(filepath):
        print_error(f"File not found: {filepath}")
        return False
    print_success(f"Found: {filepath}")
    return True


def create_backup(filepath):
    """Create backup of original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    try:
        shutil.copy2(filepath, backup_path)
        print_success(f"Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print_error(f"Failed to create backup: {e}")
        return None


def read_file(filepath):
    """Read file contents"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        return None


def write_file(filepath, content):
    """Write file contents"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print_error(f"Failed to write file: {e}")
        return False


def add_import_statement(content):
    """Add import statement for BOB AI blueprint"""
    import_line = "from bob_ai_api_endpoints import bob_ai_blueprint"

    # Check if already present
    if import_line in content:
        print_warning("Import statement already present, skipping...")
        return content, False

    # Find a good place to add import (after other blueprint imports if they exist)
    # Pattern: Look for existing imports that look like "from ... import"
    lines = content.split('\n')
    insert_index = None

    # Look for the last import line
    for i, line in enumerate(lines):
        if line.startswith('from ') and 'import' in line:
            insert_index = i + 1
        elif line.startswith('import ') and insert_index is None:
            insert_index = i + 1

    if insert_index is None:
        # If no imports found, try to find after initial comments
        for i, line in enumerate(lines):
            if not line.startswith('#') and line.strip() != '':
                insert_index = i
                break

    if insert_index is None:
        insert_index = 10  # Default to line 10

    # Insert import
    lines.insert(insert_index, import_line)
    new_content = '\n'.join(lines)

    print_success(f"Added import at line {insert_index + 1}")
    return new_content, True


def add_blueprint_registration(content):
    """Add blueprint registration to Flask app"""
    registration = """
# Register BOB AI Mega Expansion endpoints
app.register_blueprint(bob_ai_blueprint)
logger.info("[ORFEAS] BOB AI Mega Expansion API endpoints registered")
"""

    # Check if already present
    if "bob_ai_blueprint" in content and "register_blueprint" in content:
        print_warning("Blueprint registration already present, skipping...")
        return content, False

    # Find a good place to add registration (after other blueprint registrations)
    # Look for other register_blueprint calls
    lines = content.split('\n')
    insert_index = None

    # Look for the last register_blueprint or CORS setup
    for i, line in enumerate(lines):
        if 'register_blueprint' in line or 'CORS' in line:
            insert_index = i + 1

    if insert_index is None:
        # Try to find after app initialization (app = Flask)
        for i, line in enumerate(lines):
            if 'app = Flask' in line:
                insert_index = i + 10
                break

    if insert_index is None:
        insert_index = len(lines) - 50  # Default to near end

    # Insert registration
    lines.insert(insert_index, registration)
    new_content = '\n'.join(lines)

    print_success(f"Added blueprint registration at line {insert_index + 1}")
    return new_content, True


def verify_integration(main_py_path):
    """Verify that integration was successful"""
    content = read_file(main_py_path)
    if not content:
        return False

    checks = {
        'Import present': 'from bob_ai_api_endpoints import bob_ai_blueprint' in content,
        'Registration present': 'app.register_blueprint(bob_ai_blueprint)' in content,
        'Logging added': '[ORFEAS] BOB AI Mega Expansion API endpoints' in content,
    }

    print("\nVerification Results:")
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print_success(check_name)
        else:
            print_error(check_name)
            all_passed = False

    return all_passed


def main():
    """Main integration function"""
    print_header("BOB AI API Endpoints Integration")

    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(script_dir, "main.py")
    endpoints_py_path = os.path.join(script_dir, "bob_ai_api_endpoints.py")

    print("Step 1: Checking files...\n")

    # Check main.py
    if not check_file_exists(main_py_path):
        print_error("main.py not found. Are you in the backend directory?")
        return False

    # Check endpoints
    if not check_file_exists(endpoints_py_path):
        print_error("bob_ai_api_endpoints.py not found. Please create it first.")
        return False

    # Create backup
    print("\nStep 2: Creating backup...\n")
    backup = create_backup(main_py_path)
    if not backup:
        return False

    # Read main.py
    print("\nStep 3: Reading main.py...\n")
    content = read_file(main_py_path)
    if not content:
        return False
    print_success("Read main.py successfully")

    # Add import
    print("\nStep 4: Adding import statement...\n")
    content, import_added = add_import_statement(content)

    # Add registration
    print("\nStep 5: Adding blueprint registration...\n")
    content, registration_added = add_blueprint_registration(content)

    # Write back
    print("\nStep 6: Writing updated main.py...\n")
    if not write_file(main_py_path, content):
        print_error("Failed to write main.py. Restoring backup...")
        shutil.copy2(backup, main_py_path)
        return False
    print_success("main.py updated successfully")

    # Verify
    print("\nStep 7: Verifying integration...\n")
    if not verify_integration(main_py_path):
        print_warning("Some checks failed. Review the integration manually.")
        print_warning(f"Backup saved to: {backup}")

    # Summary
    print_header("Integration Complete")
    print(f"""
✓ BOB AI API Endpoints integrated into main.py
✓ Backup created: {backup}

Next steps:
1. Start the backend: python main.py
2. Test the endpoints:
   - curl http://localhost:5000/api/disciplines/health
   - curl http://localhost:5000/api/disciplines/all?limit=5

API Documentation:
   - See: BOB_AI_API_INTEGRATION_GUIDE.md

For more information:
   - Check backend logs for "[ORFEAS] BOB AI Mega Expansion" messages
   - Review BOB_AI_API_INTEGRATION_GUIDE.md for endpoint details
    """)

    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        exit(1)
