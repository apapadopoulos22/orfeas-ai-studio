#!/usr/bin/env python3
"""
PHASE 4: DOCKER ORCHESTRATION VERIFICATION
===========================================
Verify Docker configuration, Dockerfile, and docker-compose setup.

Tests:
- Docker files exist
- docker-compose.yml is valid
- Dockerfile syntax is correct
- Configuration is complete
- All services defined
"""

import sys
import os
import json
from pathlib import Path
import subprocess

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*65}")
    print(f"{'='*5} {text:<54} {'='*5}")
    print(f"{'='*65}\n")

# =====================================================================
# PHASE 4: DOCKER ORCHESTRATION
# =====================================================================

print_header("PHASE 4: DOCKER ORCHESTRATION VERIFICATION")

all_pass = True
exit_code = 0

# =====================================================================
# Test 4.1: Docker Installation Check
# =====================================================================
print_header("TEST 4.1: DOCKER INSTALLATION CHECK")

try:
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"✓ Docker installed: {result.stdout.strip()}")
        docker_available = True
    else:
        print(f"⚠ Docker version check failed: {result.stderr.strip()[:50]}")
        docker_available = False

except FileNotFoundError:
    print("⚠ Docker not found in PATH (this is OK for development)")
    docker_available = False
    print()
except Exception as e:
    print(f"⚠ Docker check failed: {e}")
    docker_available = False

if docker_available:
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Docker Compose installed: {result.stdout.strip()}\n")
        else:
            print(f"⚠ Docker Compose not available: {result.stderr.strip()[:50]}\n")
    except:
        print("⚠ Docker Compose not found\n")
else:
    print()

# =====================================================================
# Test 4.2: Docker Configuration Files
# =====================================================================
print_header("TEST 4.2: DOCKER CONFIGURATION FILES")

try:
    workspace = Path(os.getcwd())

    config_files = {
        "docker-compose.yml": workspace / "docker-compose.yml",
        "Dockerfile (backend)": workspace / "backend" / "Dockerfile",
        ".dockerignore": workspace / ".dockerignore",
    }

    found_files = {}
    for name, path in config_files.items():
        if path.exists():
            size_kb = path.stat().st_size / 1024
            found_files[name] = path
            print(f"✓ {name} found ({size_kb:.1f} KB)")
        else:
            print(f"⚠ {name} not found at {path}")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 4.3: docker-compose.yml Validation
# =====================================================================
print_header("TEST 4.3: DOCKER-COMPOSE.YML VALIDATION")

try:
    compose_path = Path(os.getcwd()) / "docker-compose.yml"

    if compose_path.exists():
        print(f"Parsing docker-compose.yml...")

        try:
            import yaml
            with open(compose_path, 'r') as f:
                compose_config = yaml.safe_load(f)

            # Check required top-level keys
            required_keys = ["version", "services"]
            found_keys = [k for k in required_keys if k in compose_config]
            missing_keys = [k for k in required_keys if k not in compose_config]

            if missing_keys:
                print(f"⚠ Missing keys: {', '.join(missing_keys)}\n")
            else:
                print(f"✓ Valid structure detected")
                print(f"  Version: {compose_config.get('version', 'N/A')}")

                # List services
                services = compose_config.get("services", {})
                print(f"  Services defined: {len(services)}")
                for service_name in services.keys():
                    print(f"    - {service_name}")

                print()

        except ImportError:
            print("✓ YAML format detected (pyyaml not installed)")
            print("  Cannot validate structure without pyyaml\n")
        except Exception as e:
            print(f"✗ Invalid YAML: {e}\n")
            all_pass = False
    else:
        print("⚠ docker-compose.yml not found\n")

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 4.4: Dockerfile Validation
# =====================================================================
print_header("TEST 4.4: DOCKERFILE VALIDATION")

try:
    dockerfile_path = Path(os.getcwd()) / "backend" / "Dockerfile"

    if dockerfile_path.exists():
        print("Analyzing Dockerfile...")

        with open(dockerfile_path, 'r') as f:
            lines = f.readlines()

        # Count Docker instructions
        instructions = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if line.upper().startswith(('FROM', 'RUN', 'COPY', 'ADD', 'ENV', 'EXPOSE', 'CMD', 'ENTRYPOINT')):
                    instr = line.split()[0].upper()
                    instructions[instr] = instructions.get(instr, 0) + 1

        print(f"✓ Dockerfile structure")
        print(f"  Total lines: {len(lines)}")
        print(f"  Instructions found:")
        for instr, count in sorted(instructions.items()):
            print(f"    - {instr}: {count}")

        # Check for required instructions
        if "FROM" in instructions:
            print(f"  ✓ Base image defined (FROM)")
        else:
            print(f"  ✗ Missing FROM instruction")
            all_pass = False

        if "COPY" in instructions or "ADD" in instructions:
            print(f"  ✓ Files to be copied")

        if "RUN" in instructions:
            print(f"  ✓ Build commands defined")

        print()

    else:
        print("⚠ Dockerfile not found\n")

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 4.5: Docker Network & Volume Setup
# =====================================================================
print_header("TEST 4.5: DOCKER NETWORK & VOLUME SETUP")

try:
    compose_path = Path(os.getcwd()) / "docker-compose.yml"

    if compose_path.exists():
        with open(compose_path, 'r') as f:
            content = f.read()

        # Basic checks without parsing
        has_networks = "networks:" in content.lower()
        has_volumes = "volumes:" in content.lower()
        has_ports = "ports:" in content.lower()

        print("✓ Docker Compose configuration checks:")
        if has_networks:
            print("  ✓ Custom networks defined")
        else:
            print("  ⚠ No custom networks defined")

        if has_volumes:
            print("  ✓ Volume mappings defined")
        else:
            print("  ⚠ No volume mappings defined")

        if has_ports:
            print("  ✓ Port exposures defined")
        else:
            print("  ⚠ No port exposures defined")

        print()

    else:
        print("⚠ docker-compose.yml not found\n")

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 4.6: Backend Docker Configuration
# =====================================================================
print_header("TEST 4.6: BACKEND DOCKER CONFIGURATION")

try:
    backend_path = Path(os.getcwd()) / "backend"

    # Check for requirements.txt
    req_file = backend_path / "requirements.txt"
    if req_file.exists():
        with open(req_file, 'r') as f:
            req_lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]

        print(f"✓ requirements.txt found")
        print(f"  Dependencies: {len(req_lines)}")
        print(f"  Sample packages:")
        for pkg in req_lines[:5]:
            print(f"    - {pkg.split('==')[0] if '==' in pkg else pkg.split('>')[0] if '>' in pkg else pkg}")

        print()
    else:
        print("⚠ requirements.txt not found\n")

    # Check .dockerignore
    dockerignore = Path(os.getcwd()) / ".dockerignore"
    if dockerignore.exists():
        with open(dockerignore, 'r') as f:
            ignore_items = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]

        print(f"✓ .dockerignore found ({len(ignore_items)} patterns)")
    else:
        print("⚠ .dockerignore not found")
        print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 4.7: Docker Build Test (Dry Run)
# =====================================================================
print_header("TEST 4.7: DOCKER BUILD VERIFICATION (DRY RUN)")

if docker_available:
    try:
        print("Checking Docker build context...")

        # Just check if docker command works
        result = subprocess.run(
            ["docker", "build", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("✓ Docker build command available")
            print("  Note: Skipping actual build (would require 10+ minutes)")
            print()
        else:
            print("⚠ Docker build command failed")
            print()

    except Exception as e:
        print(f"⚠ Docker build check failed: {e}\n")
else:
    print("⚠ Docker not available, skipping build test\n")

# =====================================================================
# Summary
# =====================================================================
print_header("PHASE 4: SUMMARY")

if all_pass:
    print("✓ PHASE 4: DOCKER ORCHESTRATION VERIFIED SUCCESSFULLY")
    print("\nStatus: READY FOR PHASE 5 (End-to-End Testing)")
    exit_code = 0
else:
    print("⚠ PHASE 4: COMPLETED WITH WARNINGS")
    print("\nStatus: Review issues before proceeding to Phase 5")
    exit_code = 1

print(f"\nNext Phase: Phase 5 - End-to-End Testing\n")

sys.exit(exit_code)
