#!/usr/bin/env python
"""
BOB AI v9.0 - Phase 1: Environment Verification
Validates Python environment, dependencies, and backend structure
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def check_python_version():
    """Verify Python 3.10+"""
    print_header("PHASE 1.1: Python Version Check")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"Current Python: {version_str}")

    if version.major >= 3 and version.minor >= 10:
        print("✓ Python version: PASS (3.10+)\n")
        return True
    else:
        print(f"✗ Python version: FAIL (requires 3.10+, got {version_str})\n")
        return False

def check_pip():
    """Verify pip installation"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"pip: {result.stdout.strip()}")
        print("✓ pip: PASS\n")
        return True
    except Exception as e:
        print(f"✗ pip: FAIL ({e})\n")
        return False

def check_core_packages():
    """Verify core packages installed"""
    print_header("PHASE 1.2: Core Packages Check")

    packages = {
        "flask": "Flask 2.3+",
        "flask_socketio": "Flask-SocketIO 5.3+",
        "torch": "PyTorch 2.0+",
        "transformers": "Transformers 4.35+",
        "sklearn": "Scikit-learn",
        "numpy": "NumPy 1.24+",
        "pandas": "Pandas",
    }

    all_ok = True
    for package, description in packages.items():
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            print(f"✓ {description}: {version}")
        except ImportError:
            print(f"✗ {package}: NOT INSTALLED")
            all_ok = False

    print()
    return all_ok

def check_backend_structure():
    """Verify backend directory structure"""
    print_header("PHASE 1.3: Backend Structure Check")

    backend_path = Path("backend")
    if not backend_path.exists():
        print(f"✗ Backend directory not found\n")
        return False

    print(f"✓ Backend directory found\n")

    # Check core modules
    core_modules = [
        "bob_ai_knowledge_graph.py",
        "bob_ai_multi_agent_reasoner.py",
        "bob_ai_discipline_mapper.py",
        "bob_ai_integration_hub.py",
        "main.py",
    ]

    all_present = True
    for module in core_modules:
        module_path = backend_path / module
        if module_path.exists():
            size = module_path.stat().st_size
            print(f"✓ {module}: {size:,} bytes")
        else:
            print(f"✗ {module}: NOT FOUND")
            all_present = False

    print()
    return all_present

def check_configuration():
    """Verify configuration files"""
    print_header("PHASE 1.4: Configuration Check")

    config_files = [
        ("backend/.env", ".env configuration"),
        ("backend/requirements.txt", "Python requirements"),
        ("docker-compose.yml", "Docker Compose"),
        ("Dockerfile", "Docker build file"),
    ]

    all_found = True
    for filepath, description in config_files:
        file_path = Path(filepath)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ {description}: {size:,} bytes")
        else:
            print(f"✗ {description}: NOT FOUND")
            all_found = False

    print()
    return all_found

def check_virtual_env():
    """Verify virtual environment"""
    print_header("PHASE 1.5: Virtual Environment Check")

    in_venv = sys.prefix != sys.base_prefix

    if in_venv:
        print(f"✓ Virtual environment: ACTIVE")
        print(f"  Location: {sys.prefix}\n")
        return True
    else:
        print("⚠ Virtual environment: NOT ACTIVE")
        print("  Recommendation: Activate venv with:")
        print("  - Windows: .\\venv\\Scripts\\activate")
        print("  - Linux/Mac: source venv/bin/activate\n")
        return True  # Not critical, just a warning

def check_imports():
    """Test core module imports"""
    print_header("PHASE 1.6: Module Import Test")

    try:
        sys.path.insert(0, str(Path("backend").absolute()))

        print("Importing core modules...")

        from bob_ai_knowledge_graph import KnowledgeGraph
        print("✓ KnowledgeGraph imported")

        from bob_ai_multi_agent_reasoner import MultiAgentReasoner
        print("✓ MultiAgentReasoner imported")

        from bob_ai_discipline_mapper import DisciplineModuleMapper
        print("✓ DisciplineModuleMapper imported")

        from bob_ai_integration_hub import get_bob_ai_hub
        print("✓ BOB AI Integration Hub imported")

        print()
        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}\n")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}\n")
        return False

def generate_summary(results):
    """Generate phase summary"""
    print_header("PHASE 1: SUMMARY")

    all_passed = all(results.values())

    print("Verification Results:")
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check}")

    print()

    if all_passed:
        print("✓ PHASE 1: ALL CHECKS PASSED")
        print("\nEnvironment is ready for next phase.")
        print("Proceed to: Phase 2 - Component Initialization\n")
        return True
    else:
        print("✗ PHASE 1: SOME CHECKS FAILED")
        print("\nFix failures above before proceeding to Phase 2.\n")
        return False

def main():
    """Main verification routine"""
    print("\n" + "=" * 70)
    print("  BOB AI v9.0 - TODO #9: LOCAL DEPLOYMENT")
    print("  Phase 1: Environment Verification")
    print("=" * 70)

    results = {
        "Python Version (3.10+)": check_python_version(),
        "pip Package Manager": check_pip(),
        "Core Packages": check_core_packages(),
        "Backend Structure": check_backend_structure(),
        "Configuration Files": check_configuration(),
        "Virtual Environment": check_virtual_env(),
        "Module Imports": check_imports(),
    }

    success = generate_summary(results)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
