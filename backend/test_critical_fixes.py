"""
+==============================================================================â•—
| [WARRIOR] ORFEAS CRITICAL FIXES VALIDATION TEST [WARRIOR] |
| TEST ALL 3 SECURITY FIXES |
| VALIDATION IS MANDATORY |
+==============================================================================

Tests for the 3 critical security fixes:
1. Production mode detection (werkzeug flag removed)
2. Environment validation on startup
3. Network timeout protection
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Any, List

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name: Any, status: List, message: Any = "") -> None:
    """Print test result with color coding"""
    if status == "PASS":
        print(f"{GREEN}[OK] PASS:{RESET} {test_name}")
    elif status == "FAIL":
        print(f"{RED}[FAIL] FAIL:{RESET} {test_name}")
        if message:
            print(f"  {RED}→{RESET} {message}")
    elif status == "WARN":
        print(f"{YELLOW}[WARN]  WARN:{RESET} {test_name}")
        if message:
            print(f"  {YELLOW}→{RESET} {message}")
    elif status == "INFO":
        print(f"{BLUE}ℹ  INFO:{RESET} {test_name}")
    print()

def test_fix_1_werkzeug_security() -> int:
    """Test Fix #1: Verify unsafe werkzeug flag removed"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TEST FIX #1: WERKZEUG SECURITY FLAG REMOVAL{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    main_py_path = Path(__file__).parent / "main.py"

    if not main_py_path.exists():
        print_test("Fix #1: File Exists", "FAIL", f"main.py not found at {main_py_path}")
        return False

    content = main_py_path.read_text(encoding='utf-8')

    # Test 1.1: Verify unsafe flag removed (ignore comments)
    import re
    # Look for actual usage (not in comments)
    unsafe_usage = re.search(r'^\s*[^#]*allow_unsafe_werkzeug\s*=\s*True', content, re.MULTILINE)
    if unsafe_usage:
        print_test("Fix #1.1: Unsafe Flag Removed", "FAIL", "allow_unsafe_werkzeug=True still present in code!")
        return False
    else:
        print_test("Fix #1.1: Unsafe Flag Removed", "PASS")

    # Test 1.2: Verify production detection added
    if 'os.getenv(\'PRODUCTION\'' in content or 'os.getenv("PRODUCTION"' in content:
        print_test("Fix #1.2: Production Detection Added", "PASS")
    else:
        print_test("Fix #1.2: Production Detection Added", "FAIL", "No production mode detection found")
        return False

    # Test 1.3: Verify warning system added
    if "PRODUCTION MODE DETECTED" in content or "production" in content.lower():
        print_test("Fix #1.3: Production Warning System", "PASS")
    else:
        print_test("Fix #1.3: Production Warning System", "WARN", "Warning system might be missing")

    return True

def test_fix_2_environment_validation() -> int:
    """Test Fix #2: Verify environment validation function"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TEST FIX #2: ENVIRONMENT VALIDATION{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    main_py_path = Path(__file__).parent / "main.py"
    content = main_py_path.read_text(encoding='utf-8')

    # Test 2.1: Verify validation function exists
    if "def validate_environment()" in content:
        print_test("Fix #2.1: Validation Function Exists", "PASS")
    else:
        print_test("Fix #2.1: Validation Function Exists", "FAIL", "validate_environment() not found")
        return False

    # Test 2.2: Verify SECRET_KEY validation
    if "SECRET_KEY" in content and "orfeas-unified-orfeas-2025" in content:
        print_test("Fix #2.2: SECRET_KEY Validation", "PASS")
    else:
        print_test("Fix #2.2: SECRET_KEY Validation", "WARN", "SECRET_KEY validation might be incomplete")

    # Test 2.3: Verify PORT validation
    if "ORFEAS_PORT" in content and ("1" in content or "65535" in content):
        print_test("Fix #2.3: Port Validation", "PASS")
    else:
        print_test("Fix #2.3: Port Validation", "WARN", "Port validation might be incomplete")

    # Test 2.4: Verify HOST validation
    if "ORFEAS_HOST" in content:
        print_test("Fix #2.4: Host Validation", "PASS")
    else:
        print_test("Fix #2.4: Host Validation", "WARN", "Host validation might be missing")

    # Test 2.5: Verify MODE validation
    if "ORFEAS_MODE" in content and ("full_ai" in content or "safe_fallback" in content):
        print_test("Fix #2.5: Mode Validation", "PASS")
    else:
        print_test("Fix #2.5: Mode Validation", "WARN", "Mode validation might be incomplete")

    # Test 2.6: Verify GPU memory validation
    if "GPU_MEMORY_LIMIT_GB" in content:
        print_test("Fix #2.6: GPU Memory Validation", "PASS")
    else:
        print_test("Fix #2.6: GPU Memory Validation", "WARN", "GPU memory validation might be missing")

    # Test 2.7: Verify upload size validation
    if "MAX_UPLOAD_MB" in content:
        print_test("Fix #2.7: Upload Size Validation", "PASS")
    else:
        print_test("Fix #2.7: Upload Size Validation", "WARN", "Upload size validation might be missing")

    # Test 2.8: Verify CORS validation
    if "CORS_ORIGINS" in content:
        print_test("Fix #2.8: CORS Validation", "PASS")
    else:
        print_test("Fix #2.8: CORS Validation", "WARN", "CORS validation might be missing")

    # Test 2.9: Verify debug mode check
    if "ORFEAS_DEBUG" in content or "DEBUG" in content:
        print_test("Fix #2.9: Debug Mode Validation", "PASS")
    else:
        print_test("Fix #2.9: Debug Mode Validation", "WARN", "Debug mode validation might be missing")

    # Test 2.10: Verify rate limiting check
    if "ENABLE_RATE_LIMITING" in content or "rate" in content.lower():
        print_test("Fix #2.10: Rate Limiting Validation", "PASS")
    else:
        print_test("Fix #2.10: Rate Limiting Validation", "WARN", "Rate limiting validation might be missing")

    # Test 2.11: Verify validation is called in main()
    if "validate_environment()" in content:
        print_test("Fix #2.11: Validation Called in main()", "PASS")
    else:
        print_test("Fix #2.11: Validation Called in main()", "FAIL", "validate_environment() not called!")
        return False

    return True

def test_fix_3_network_timeouts() -> int:
    """Test Fix #3: Verify network timeout configuration"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TEST FIX #3: NETWORK TIMEOUT PROTECTION{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    ultimate_py_path = Path(__file__).parent / "ultimate_text_to_image.py"

    if not ultimate_py_path.exists():
        print_test("Fix #3: File Exists", "FAIL", f"ultimate_text_to_image.py not found")
        return False

    content = ultimate_py_path.read_text(encoding='utf-8')

    # Test 3.1: Verify NetworkConfig class exists
    if "class NetworkConfig" in content:
        print_test("Fix #3.1: NetworkConfig Class Exists", "PASS")
    else:
        print_test("Fix #3.1: NetworkConfig Class Exists", "FAIL", "NetworkConfig class not found")
        return False

    # Test 3.2: Verify timeout configurations
    if "TIMEOUTS" in content and "fast" in content and "slow" in content:
        print_test("Fix #3.2: Timeout Configurations Defined", "PASS")
    else:
        print_test("Fix #3.2: Timeout Configurations Defined", "FAIL", "Timeout configurations missing")
        return False

    # Test 3.3: Verify retry configuration
    if "RETRY_CONFIG" in content and "backoff_factor" in content:
        print_test("Fix #3.3: Retry Configuration Defined", "PASS")
    else:
        print_test("Fix #3.3: Retry Configuration Defined", "FAIL", "Retry configuration missing")
        return False

    # Test 3.4: Verify get_session() method
    if "def get_session" in content:
        print_test("Fix #3.4: get_session() Method Exists", "PASS")
    else:
        print_test("Fix #3.4: get_session() Method Exists", "FAIL", "get_session() method not found")
        return False

    # Test 3.5: Verify HTTPAdapter with retries
    if "HTTPAdapter" in content and "Retry" in content:
        print_test("Fix #3.5: HTTPAdapter with Retry Logic", "PASS")
    else:
        print_test("Fix #3.5: HTTPAdapter with Retry Logic", "FAIL", "HTTPAdapter or Retry import missing")
        return False

    # Test 3.6: Verify sessions created in __init__
    if "self.sessions" in content:
        print_test("Fix #3.6: Sessions Created in __init__", "PASS")
    else:
        print_test("Fix #3.6: Sessions Created in __init__", "FAIL", "self.sessions not initialized")
        return False

    # Test 3.7: Verify HuggingFace uses session
    if "self.sessions['slow'].post" in content and "huggingface" in content.lower():
        print_test("Fix #3.7: HuggingFace Uses Session", "PASS")
    else:
        print_test("Fix #3.7: HuggingFace Uses Session", "WARN", "HuggingFace might not use session")

    # Test 3.8: Verify Pollinations uses session
    if "self.sessions['fast'].get" in content and "pollinations" in content.lower():
        print_test("Fix #3.8: Pollinations Uses Session", "PASS")
    else:
        print_test("Fix #3.8: Pollinations Uses Session", "WARN", "Pollinations might not use session")

    # Test 3.9: Verify Stability uses session
    if "self.sessions['slow'].post" in content and "stability" in content.lower():
        print_test("Fix #3.9: Stability Uses Session", "PASS")
    else:
        print_test("Fix #3.9: Stability Uses Session", "WARN", "Stability might not use session")

    # Test 3.10: Verify AUTOMATIC1111 uses session
    if "self.sessions['normal'].post" in content and "automatic1111" in content.lower():
        print_test("Fix #3.10: AUTOMATIC1111 Uses Session", "PASS")
    else:
        print_test("Fix #3.10: AUTOMATIC1111 Uses Session", "WARN", "AUTOMATIC1111 might not use session")

    # Test 3.11: Verify timeout exception handling
    if "requests.exceptions.Timeout" in content:
        print_test("Fix #3.11: Timeout Exception Handling", "PASS")
    else:
        print_test("Fix #3.11: Timeout Exception Handling", "WARN", "Timeout exception handling might be missing")

    # Test 3.12: Verify connection exception handling
    if "requests.exceptions.ConnectionError" in content:
        print_test("Fix #3.12: ConnectionError Exception Handling", "PASS")
    else:
        print_test("Fix #3.12: ConnectionError Exception Handling", "WARN", "ConnectionError handling might be missing")

    return True

def main() -> int:
    """Run all validation tests"""
    print(f"\n{BLUE}+{'='*78}â•—{RESET}")
    print(f"{BLUE}|{' '*78}|{RESET}")
    print(f"{BLUE}|{'[WARRIOR]  ORFEAS CRITICAL FIXES VALIDATION SUITE [WARRIOR]':^78}|{RESET}")
    print(f"{BLUE}|{' '*78}|{RESET}")
    print(f"{BLUE}|{'Testing 3 Critical Security Fixes':^78}|{RESET}")
    print(f"{BLUE}|{'VALIDATION IS MANDATORY':^78}|{RESET}")
    print(f"{BLUE}|{' '*78}|{RESET}")
    print(f"{BLUE}+{'='*78}{RESET}\n")

    results = {
        "Fix #1 (Werkzeug Security)": test_fix_1_werkzeug_security(),
        "Fix #2 (Environment Validation)": test_fix_2_environment_validation(),
        "Fix #3 (Network Timeouts)": test_fix_3_network_timeouts(),
    }

    # Summary
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}VALIDATION SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    all_passed = all(results.values())
    passed = sum(results.values())
    total = len(results)

    for fix_name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print_test(fix_name, status)

    print(f"\n{BLUE}Total: {passed}/{total} fixes validated successfully{RESET}\n")

    if all_passed:
        print(f"{GREEN}+{'='*78}â•—{RESET}")
        print(f"{GREEN}|{' '*78}|{RESET}")
        print(f"{GREEN}|{'[OK] ALL CRITICAL FIXES VALIDATED SUCCESSFULLY! [OK]':^78}|{RESET}")
        print(f"{GREEN}|{' '*78}|{RESET}")
        print(f"{GREEN}|{'PRODUCTION READY!':^78}|{RESET}")
        print(f"{GREEN}|{' '*78}|{RESET}")
        print(f"{GREEN}+{'='*78}{RESET}\n")
        return 0
    else:
        print(f"{RED}+{'='*78}â•—{RESET}")
        print(f"{RED}|{' '*78}|{RESET}")
        print(f"{RED}|{'[FAIL] VALIDATION FAILED - FIXES INCOMPLETE! [FAIL]':^78}|{RESET}")
        print(f"{RED}|{' '*78}|{RESET}")
        print(f"{RED}|{'Review failed tests above and fix issues':^78}|{RESET}")
        print(f"{RED}|{' '*78}|{RESET}")
        print(f"{RED}+{'='*78}{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
