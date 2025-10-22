#!/usr/bin/env python3
"""
ORFEAS AI 2D'√ú√≠3D Studio - LLM Integration Test
==================================================
Test script to validate the Enterprise LLM integration

Features Tested:
- LLM API endpoints accessibility
- GitHub Copilot Enterprise integration
- Multi-LLM orchestration capabilities
- Code generation and analysis
- Error handling and fallback mechanisms
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

def test_llm_status() -> int:
    """Test LLM system status endpoint"""
    print("=" * 60)
    print("üß† TESTING LLM SYSTEM STATUS")
    print("=" * 60)

    try:
        response = requests.get('http://localhost:5000/api/llm/status')
        if response.status_code == 200:
            status = response.json()
            print("'√∫√ñ LLM Status Endpoint: SUCCESS")
            print(f"   LLM System Enabled: {status.get('llm_system_enabled', False)}")
            print(f"   Enterprise LLM Manager: {status.get('enterprise_llm_manager', False)}")
            print(f"   Copilot Enterprise: {status.get('copilot_enterprise', False)}")
            print(f"   Multi-LLM Orchestrator: {status.get('multi_llm_orchestrator', False)}")
            return True
        else:
            print(f"'√π√• LLM Status Endpoint: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"'√π√• LLM Status Endpoint: ERROR - {e}")
        return False

def test_llm_models() -> int:
    """Test LLM models information endpoint"""
    print("\nÔ£ø√º¬ß√± TESTING LLM MODELS INFORMATION")
    print("=" * 60)

    try:
        response = requests.get('http://localhost:5000/api/llm/models')
        if response.status_code == 200:
            models = response.json()
            print("'√∫√ñ LLM Models Endpoint: SUCCESS")
            print(f"   Available Models: {len(models.get('available_models', []))}")

            for model in models.get('available_models', [])[:3]:  # Show first 3
                print(f"   ‚Ä¢ {model['name']}: {model['description']}")

            print(f"   Features: {list(models.get('features', {}).keys())}")
            return True
        else:
            print(f"'√π√• LLM Models Endpoint: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"'√π√• LLM Models Endpoint: ERROR - {e}")
        return False

def test_llm_generation() -> int:
    """Test basic LLM content generation"""
    print("\nÔ£ø√º√¨√π TESTING LLM CONTENT GENERATION")
    print("=" * 60)

    try:
        test_data = {
            "prompt": "Explain the concept of 3D model generation from 2D images in simple terms.",
            "task_type": "general",
            "context": {"format": "explanation", "audience": "general"}
        }

        response = requests.post(
            'http://localhost:5000/api/llm/generate',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            print("'√∫√ñ LLM Generation Endpoint: SUCCESS")
            print(f"   Model Used: {result.get('model_used', 'unknown')}")
            print(f"   Confidence Score: {result.get('confidence_score', 0):.2f}")
            print(f"   Content Length: {len(result.get('generated_content', ''))}")
            print(f"   Preview: {result.get('generated_content', '')[:100]}...")
            return True
        else:
            print(f"'√π√• LLM Generation Endpoint: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"'√π√• LLM Generation Endpoint: ERROR - {e}")
        return False

def test_code_generation() -> int:
    """Test GitHub Copilot Enterprise code generation"""
    print("\nüíª TESTING GITHUB COPILOT CODE GENERATION")
    print("=" * 60)

    try:
        test_data = {
            "requirements": "Create a Python function that calculates the area of a triangle given three sides using Heron's formula.",
            "language": "python",
            "context": {"include_tests": True, "include_docs": True}
        }

        response = requests.post(
            'http://localhost:5000/api/llm/code-generate',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            print("'√∫√ñ Code Generation Endpoint: SUCCESS")
            print(f"   Quality Score: {result.get('quality_score', 0):.2f}")
            print(f"   Language: {result.get('language', 'unknown')}")
            print(f"   Code Length: {len(result.get('generated_code', ''))}")
            print(f"   Has Tests: {bool(result.get('tests'))}")
            print(f"   Has Documentation: {bool(result.get('documentation'))}")
            print("\n   Generated Code Preview:")
            print("   " + "‚îÄ" * 50)
            code_preview = result.get('generated_code', '')[:300]
            for line in code_preview.split('\n')[:5]:
                print(f"   {line}")
            print("   " + "‚îÄ" * 50)
            return True
        else:
            print(f"'√π√• Code Generation Endpoint: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"'√π√• Code Generation Endpoint: ERROR - {e}")
        return False

def test_multi_llm_orchestration() -> int:
    """Test multi-LLM task orchestration"""
    print("\nüéØ TESTING MULTI-LLM ORCHESTRATION")
    print("=" * 60)

    try:
        test_data = {
            "task_description": "Analyze the advantages and disadvantages of different 3D file formats (STL, OBJ, GLTF) for web applications.",
            "context": {"complexity": "medium", "format": "detailed_analysis"}
        }

        response = requests.post(
            'http://localhost:5000/api/llm/orchestrate',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            print("'√∫√ñ Multi-LLM Orchestration Endpoint: SUCCESS")
            print(f"   Total Execution Time: {result.get('total_execution_time', 0):.2f}s")
            print(f"   LLM Assignments: {len(result.get('llm_assignments', {}))}")
            print(f"   Result Length: {len(result.get('final_result', ''))}")
            print(f"   Preview: {result.get('final_result', '')[:150]}...")
            return True
        else:
            print(f"'√π√• Multi-LLM Orchestration Endpoint: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"'√π√• Multi-LLM Orchestration Endpoint: ERROR - {e}")
        return False

def test_code_analysis() -> int:
    """Test code quality analysis"""
    print("\nÔ£ø√º√Æ√ß TESTING CODE QUALITY ANALYSIS")
    print("=" * 60)

    try:
        test_code = """
def calculate_area(a, b, c):
    # This function has some quality issues for testing
    s = (a + b + c) / 2
    area = (s * (s - a) * (s - b) * (s - c)) ** 0.5
    return area
"""

        test_data = {
            "code": test_code,
            "language": "python"
        }

        response = requests.post(
            'http://localhost:5000/api/llm/analyze-code',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            print("'√∫√ñ Code Analysis Endpoint: SUCCESS")
            print(f"   Quality Score: {result.get('quality_score', 0):.2f}")
            print(f"   Suggestions Count: {len(result.get('suggestions', []))}")
            print(f"   Refactoring Opportunities: {len(result.get('refactoring_opportunities', []))}")
            print(f"   Language: {result.get('language', 'unknown')}")
            return True
        else:
            print(f"'√π√• Code Analysis Endpoint: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"'√π√• Code Analysis Endpoint: ERROR - {e}")
        return False

def run_comprehensive_llm_tests() -> None:
    """Run all LLM integration tests"""
    print("Ô£ø√º√∂√Ñ ORFEAS AI - ENTERPRISE LLM INTEGRATION TEST SUITE")
    print("=" * 80)
    print("Testing LLM endpoints and functionality...")
    print("=" * 80)

    start_time = time.time()
    tests = [
        ("LLM Status", test_llm_status),
        ("LLM Models", test_llm_models),
        ("LLM Generation", test_llm_generation),
        ("Code Generation", test_code_generation),
        ("Multi-LLM Orchestration", test_multi_llm_orchestration),
        ("Code Analysis", test_code_analysis)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"'√π√• {test_name} Test: EXCEPTION - {e}")

    # Test Summary
    print("\n" + "=" * 80)
    print("üèÅ LLM INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Total Time: {time.time() - start_time:.2f}s")

    if passed == total:
        print("Ô£ø√º√©√¢ ALL LLM TESTS PASSED! Enterprise LLM system is fully functional.")
    elif passed >= total * 0.8:
        print("'√∫√ñ Most LLM tests passed. Minor issues may exist.")
    else:
        print("‚ö†Ô∏è  Multiple LLM test failures. Check server logs.")

    print("\nÔ£ø√º√¨√£ LLM System Configuration:")
    print("   ‚Ä¢ Enterprise LLM Manager: Multi-model intelligent routing")
    print("   ‚Ä¢ GitHub Copilot Enterprise: Advanced code generation")
    print("   ‚Ä¢ Multi-LLM Orchestration: Complex task decomposition")
    print("   ‚Ä¢ Code Quality Analysis: Automated code review")
    print("   ‚Ä¢ Intelligent Debugging: Error analysis and fixes")
    print("   ‚Ä¢ Context-Aware Processing: Smart model selection")

    return passed == total

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code != 200:
            print("'√π√• ORFEAS server is not running or not healthy")
            print("   Please start the server with: python backend/main.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("'√π√• Cannot connect to ORFEAS server at localhost:5000")
        print("   Please start the server with: python backend/main.py")
        sys.exit(1)

    # Run tests
    success = run_comprehensive_llm_tests()
    sys.exit(0 if success else 1)
