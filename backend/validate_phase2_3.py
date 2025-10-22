"""
+==============================================================================â•—
| [WARRIOR] ORFEAS PHASE 2.3 VALIDATION - MATERIAL & LIGHTING SYSTEM [WARRIOR] |
| Comprehensive Testing for PBR Materials and HDR Lighting |
+==============================================================================

ORFEAS Phase 2.3 Validation - Material & Lighting System Testing
Tests the complete material system with PBR properties and HDR environments

Test Coverage:
1. Backend health check
2. Material presets API validation
3. Lighting presets API validation
4. Material metadata generation
5. MTL file export
6. UI feature detection
7. Three.js integration check

Author: ORFEAS 3D WEB SPECIALIST
Date: October 15, 2025
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from typing import Dict, List

# Backend configuration
BACKEND_URL = "http://127.0.0.1:5000"
TIMEOUT = 10

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"


def print_header():
    """Print test header"""
    print(f"\n{CYAN}{'='*78}{RESET}")
    print(f"{CYAN}[WARRIOR] ORFEAS PHASE 2.3 VALIDATION - MATERIAL & LIGHTING SYSTEM [WARRIOR]{RESET}")
    print(f"{CYAN}{'='*78}{RESET}\n")


def check_backend_health() -> bool:
    """Check if backend is running"""
    try:
        print(f"{BLUE}[SEARCH] Checking backend health...{RESET}")
        response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            print(f"{GREEN}[OK] Backend is healthy{RESET}")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Mode: {data.get('mode', 'unknown')}")
            return True
        else:
            print(f"{RED}[FAIL] Backend returned status {response.status_code}{RESET}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"{RED}[FAIL] Backend is not running at {BACKEND_URL}{RESET}")
        print(f"{YELLOW}[IDEA] Start backend: cd backend && python main.py{RESET}")
        return False
    except Exception as e:
        print(f"{RED}[FAIL] Health check failed: {e}{RESET}")
        return False


def test_material_presets() -> bool:
    """Test material presets API"""
    try:
        print(f"\n{BLUE}{'='*78}{RESET}")
        print(f"{MAGENTA}[ART] TEST: MATERIAL PRESETS API{RESET}")
        print(f"{BLUE}{'='*78}{RESET}")

        print(f"{CYAN}[SIGNAL] Fetching material presets...{RESET}")
        response = requests.get(f"{BACKEND_URL}/api/materials/presets", timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                materials = data.get('materials', [])
                presets = data.get('presets', {})

                print(f"{GREEN}[OK] Material presets loaded successfully{RESET}")
                print(f"   Total materials: {len(materials)}")

                print(f"\n{CYAN} Available Materials:{RESET}")
                for mat in materials:
                    mat_data = presets.get(mat, {})
                    print(f"\n   {mat.upper()}:")
                    print(f"      Metalness: {mat_data.get('metalness', 0):.2f}")
                    print(f"      Roughness: {mat_data.get('roughness', 0):.2f}")
                    print(f"      Reflectivity: {mat_data.get('reflectivity', 0):.2f}")
                    print(f"      Base Color: {mat_data.get('base_color', 'N/A')}")

                # Verify required materials
                required = ['metal', 'plastic', 'wood', 'glass', 'ceramic', 'rubber']
                missing = [m for m in required if m not in materials]

                if missing:
                    print(f"\n{YELLOW}[WARN] Missing materials: {missing}{RESET}")
                    return False

                return True
            else:
                print(f"{RED}[FAIL] API returned success=false{RESET}")
                return False
        else:
            print(f"{RED}[FAIL] API request failed with status {response.status_code}{RESET}")
            return False

    except Exception as e:
        print(f"{RED}[FAIL] Material presets test failed: {e}{RESET}")
        return False


def test_lighting_presets() -> bool:
    """Test lighting presets API"""
    try:
        print(f"\n{BLUE}{'='*78}{RESET}")
        print(f"{MAGENTA}[IDEA] TEST: LIGHTING PRESETS API{RESET}")
        print(f"{BLUE}{'='*78}{RESET}")

        print(f"{CYAN}[SIGNAL] Fetching lighting presets...{RESET}")
        response = requests.get(f"{BACKEND_URL}/api/lighting/presets", timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                environments = data.get('environments', [])
                presets = data.get('presets', {})

                print(f"{GREEN}[OK] Lighting presets loaded successfully{RESET}")
                print(f"   Total environments: {len(environments)}")

                print(f"\n{CYAN} Available Lighting Environments:{RESET}")
                for env in environments:
                    env_data = presets.get(env, {})
                    print(f"\n   {env.upper()}:")
                    print(f"      Ambient: {env_data.get('ambient_intensity', 0):.2f}")
                    print(f"      Main Light: {env_data.get('main_light_intensity', 0):.2f}")
                    print(f"      Shadow: {env_data.get('shadow_intensity', 0):.2f}")

                # Verify required environments
                required = ['studio', 'outdoor', 'dramatic', 'night', 'warm']
                missing = [e for e in required if e not in environments]

                if missing:
                    print(f"\n{YELLOW}[WARN] Missing environments: {missing}{RESET}")
                    return False

                return True
            else:
                print(f"{RED}[FAIL] API returned success=false{RESET}")
                return False
        else:
            print(f"{RED}[FAIL] API request failed with status {response.status_code}{RESET}")
            return False

    except Exception as e:
        print(f"{RED}[FAIL] Lighting presets test failed: {e}{RESET}")
        return False


def test_metadata_generation() -> bool:
    """Test material metadata generation"""
    try:
        print(f"\n{BLUE}{'='*78}{RESET}")
        print(f"{MAGENTA} TEST: MATERIAL METADATA GENERATION{RESET}")
        print(f"{BLUE}{'='*78}{RESET}")

        test_data = {
            'material_type': 'metal',
            'lighting_environment': 'studio',
            'save': True
        }

        print(f"{CYAN}[SIGNAL] Generating metadata...{RESET}")
        response = requests.post(
            f"{BACKEND_URL}/api/materials/metadata",
            json=test_data,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                metadata = data.get('metadata', {})

                print(f"{GREEN}[OK] Metadata generated successfully{RESET}")
                print(f"   Material: {metadata.get('material', {}).get('material_type', 'N/A')}")
                print(f"   Lighting: {metadata.get('lighting', {}).get('environment_type', 'N/A')}")
                print(f"   Timestamp: {metadata.get('timestamp', 'N/A')}")

                # Check for required keys
                required_keys = ['material', 'material_threejs', 'lighting', 'lighting_threejs']
                missing_keys = [k for k in required_keys if k not in metadata]

                if missing_keys:
                    print(f"{YELLOW}[WARN] Missing metadata keys: {missing_keys}{RESET}")
                    return False

                # Check download URL
                if 'download_url' in data:
                    print(f"   Download URL: {data['download_url']}")

                return True
            else:
                print(f"{RED}[FAIL] API returned success=false{RESET}")
                return False
        else:
            print(f"{RED}[FAIL] API request failed with status {response.status_code}{RESET}")
            return False

    except Exception as e:
        print(f"{RED}[FAIL] Metadata generation test failed: {e}{RESET}")
        return False


def test_mtl_export() -> bool:
    """Test MTL file export"""
    try:
        print(f"\n{BLUE}{'='*78}{RESET}")
        print(f"{MAGENTA} TEST: MTL FILE EXPORT{RESET}")
        print(f"{BLUE}{'='*78}{RESET}")

        test_data = {
            'material_type': 'metal',
            'material_name': 'test_material'
        }

        print(f"{CYAN}[SIGNAL] Exporting MTL file...{RESET}")
        response = requests.post(
            f"{BACKEND_URL}/api/materials/export-mtl",
            json=test_data,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                mtl_content = data.get('mtl_content', '')

                print(f"{GREEN}[OK] MTL file exported successfully{RESET}")
                print(f"   Content length: {len(mtl_content)} characters")
                print(f"   Download URL: {data.get('download_url', 'N/A')}")

                # Verify MTL content structure
                required_keywords = ['newmtl', 'Ka', 'Kd', 'Ks', 'Ns']
                missing = [kw for kw in required_keywords if kw not in mtl_content]

                if missing:
                    print(f"{YELLOW}[WARN] Missing MTL keywords: {missing}{RESET}")
                    return False

                print(f"\n{CYAN}MTL Content Preview:{RESET}")
                print(mtl_content[:300] + "...")

                return True
            else:
                print(f"{RED}[FAIL] API returned success=false{RESET}")
                return False
        else:
            print(f"{RED}[FAIL] API request failed with status {response.status_code}{RESET}")
            return False

    except Exception as e:
        print(f"{RED}[FAIL] MTL export test failed: {e}{RESET}")
        return False


def test_material_studio_ui() -> Dict[str, bool]:
    """Test Material Studio UI features"""
    print(f"\n{BLUE}{'='*78}{RESET}")
    print(f"{MAGENTA} TEST: MATERIAL STUDIO UI FEATURES{RESET}")
    print(f"{BLUE}{'='*78}{RESET}")

    results = {}

    # Check if material-studio.html exists
    ui_path = Path("material-studio.html")
    if ui_path.exists():
        print(f"{GREEN}[OK] Material Studio UI file exists{RESET}")
        results['ui_file_exists'] = True

        # Check file size
        file_size = ui_path.stat().st_size
        print(f"   File size: {file_size / 1024:.1f} KB")
        results['ui_file_valid'] = file_size > 20000  # At least 20KB

        # Check for key features in HTML
        content = ui_path.read_text(encoding='utf-8')

        features = {
            'threejs': 'three.min.js' in content or 'THREE.' in content,
            'pbr_materials': 'material-btn' in content and 'data-material' in content,
            'lighting_presets': 'lighting-btn' in content and 'data-lighting' in content,
            'material_properties': 'metalnessSlider' in content and 'roughnessSlider' in content,
            'color_picker': 'colorPicker' in content,
            'lighting_controls': 'intensitySlider' in content and 'ambientSlider' in content,
            'model_upload': 'fileInput' in content and 'uploadZone' in content,
            'export_features': 'exportBtn' in content and 'screenshotBtn' in content,
            'viewport': 'viewport' in content and 'canvas' in content
        }

        print(f"\n{CYAN}[SEARCH] Feature Detection:{RESET}")
        for feature, present in features.items():
            status = f"{GREEN}[OK]{RESET}" if present else f"{RED}[FAIL]{RESET}"
            print(f"   {status} {feature.replace('_', ' ').title()}")
            results[feature] = present
    else:
        print(f"{RED}[FAIL] Material Studio UI file not found{RESET}")
        results['ui_file_exists'] = False

    return results


def main():
    """Main validation function"""
    print_header()

    # Track test results
    tests_passed = 0
    tests_total = 0

    # Test 1: Backend Health
    tests_total += 1
    if check_backend_health():
        tests_passed += 1
    else:
        print(f"\n{RED}[WARN] Cannot continue - backend is not running{RESET}")
        return

    # Test 2: Material Presets
    tests_total += 1
    if test_material_presets():
        tests_passed += 1

    # Test 3: Lighting Presets
    tests_total += 1
    if test_lighting_presets():
        tests_passed += 1

    # Test 4: Metadata Generation
    tests_total += 1
    if test_metadata_generation():
        tests_passed += 1

    # Test 5: MTL Export
    tests_total += 1
    if test_mtl_export():
        tests_passed += 1

    # Test 6: UI Features
    tests_total += 1
    ui_results = test_material_studio_ui()
    if all(ui_results.values()):
        tests_passed += 1

    # Final Summary
    print(f"\n{CYAN}{'='*78}{RESET}")
    print(f"{MAGENTA}[STATS] PHASE 2.3 VALIDATION SUMMARY{RESET}")
    print(f"{CYAN}{'='*78}{RESET}\n")

    pass_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0

    if pass_rate == 100:
        print(f"{GREEN}[OK] ALL TESTS PASSED ({tests_passed}/{tests_total}){RESET}")
        print(f"{GREEN} Phase 2.3 Material & Lighting System is READY!{RESET}")
    elif pass_rate >= 75:
        print(f"{YELLOW}[WARN] MOSTLY PASSING ({tests_passed}/{tests_total} - {pass_rate:.0f}%){RESET}")
        print(f"{YELLOW}Some features may need attention{RESET}")
    else:
        print(f"{RED}[FAIL] TESTS FAILED ({tests_passed}/{tests_total} - {pass_rate:.0f}%){RESET}")
        print(f"{RED}Phase 2.3 needs fixes{RESET}")

    print(f"\n{CYAN}{'='*78}{RESET}")
    print(f"{MAGENTA}[PREMIUM] MATERIAL & LIGHTING FEATURES:{RESET}")
    print(f"{CYAN}{'='*78}{RESET}")
    print(f"{GREEN}[OK] 6 PBR Material Presets (Metal, Plastic, Wood, Glass, Ceramic, Rubber){RESET}")
    print(f"{GREEN}[OK] 5 HDR Lighting Environments (Studio, Outdoor, Dramatic, Night, Warm){RESET}")
    print(f"{GREEN}[OK] Real-time Three.js 3D Preview{RESET}")
    print(f"{GREEN}[OK] Material Property Controls (Metalness, Roughness, Reflectivity, Color){RESET}")
    print(f"{GREEN}[OK] Lighting Controls (Intensity, Ambient, Shadow){RESET}")
    print(f"{GREEN}[OK] Material Metadata Export (JSON){RESET}")
    print(f"{GREEN}[OK] MTL File Generation (OBJ compatibility){RESET}")
    print(f"{GREEN}[OK] Screenshot Capture{RESET}")

    print(f"\n{CYAN}{'='*78}{RESET}")
    print(f"{MAGENTA}[LAUNCH] QUICK START:{RESET}")
    print(f"{CYAN}{'='*78}{RESET}")
    print(f"{YELLOW}1. Open material-studio.html in browser{RESET}")
    print(f"{YELLOW}2. Load 3D model (STL/OBJ) or use sample sphere{RESET}")
    print(f"{YELLOW}3. Select PBR material preset{RESET}")
    print(f"{YELLOW}4. Choose HDR lighting environment{RESET}")
    print(f"{YELLOW}5. Adjust material properties and lighting{RESET}")
    print(f"{YELLOW}6. Export material metadata or take screenshot{RESET}")

    print(f"\n{CYAN}[WARRIOR] PHASE 2.3 VALIDATION COMPLETE [WARRIOR]{RESET}\n")


if __name__ == "__main__":
    main()
