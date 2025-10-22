#!/usr/bin/env python3
"""
ORFEAS AI - Phase 1 Validation Script
=====================================

Validates the syntax of enhanced Python files and runs a quick
type hint coverage analysis to measure improvement.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Any

def validate_python_syntax(file_path: Path) -> Dict[str, Any]:
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the AST to check for syntax errors
        ast.parse(content)

        return {
            'file': str(file_path.name),
            'valid': True,
            'error': None
        }

    except SyntaxError as e:
        return {
            'file': str(file_path.name),
            'valid': False,
            'error': f"Syntax error at line {e.lineno}: {e.msg}"
        }
    except Exception as e:
        return {
            'file': str(file_path.name),
            'valid': False,
            'error': f"Error: {str(e)}"
        }

def analyze_type_hint_coverage(file_path: Path) -> Dict[str, Any]:
    """Analyze type hint coverage in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        total_functions = 0
        functions_with_hints = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1

                # Check if function has return annotation and parameter annotations
                has_return_annotation = node.returns is not None
                has_arg_annotations = any(arg.annotation for arg in node.args.args if arg.arg != 'self')

                # Consider function as having hints if it has either return or parameter annotations
                if has_return_annotation or has_arg_annotations:
                    functions_with_hints += 1

        coverage = (functions_with_hints / total_functions * 100) if total_functions > 0 else 100

        return {
            'file': str(file_path.name),
            'total_functions': total_functions,
            'functions_with_hints': functions_with_hints,
            'coverage_percent': coverage
        }

    except Exception as e:
        return {
            'file': str(file_path.name),
            'error': str(e),
            'coverage_percent': 0
        }

def main():
    """Main validation function"""
    print(" PHASE 1: Validation & Coverage Analysis")
    print("=" * 50)

    backend_dir = Path("backend")
    target_files = [
        'gpu_manager.py',
        'main.py',
        'validation.py',
        'batch_processor.py',
        'hunyuan_integration.py',
        'agent_api.py',
        'production_metrics.py',
        'stl_processor.py'
    ]

    print(" SYNTAX VALIDATION:")
    print("-" * 30)

    valid_files = 0
    invalid_files = 0

    for file_name in target_files:
        file_path = backend_dir / file_name

        if not file_path.exists():
            print(f"  {file_name}: File not found")
            continue

        validation = validate_python_syntax(file_path)

        if validation['valid']:
            print(f" {file_name}: Valid syntax")
            valid_files += 1
        else:
            print(f" {file_name}: {validation['error']}")
            invalid_files += 1

    print(f"\n TYPE HINT COVERAGE ANALYSIS:")
    print("-" * 40)

    total_functions = 0
    total_with_hints = 0

    for file_name in target_files:
        file_path = backend_dir / file_name

        if not file_path.exists():
            continue

        coverage = analyze_type_hint_coverage(file_path)

        if 'error' not in coverage:
            total_functions += coverage['total_functions']
            total_with_hints += coverage['functions_with_hints']

            print(f" {file_name}")
            print(f"   Functions: {coverage['total_functions']}")
            print(f"   With hints: {coverage['functions_with_hints']}")
            print(f"   Coverage: {coverage['coverage_percent']:.1f}%")
        else:
            print(f" {file_name}: {coverage['error']}")

    overall_coverage = (total_with_hints / total_functions * 100) if total_functions > 0 else 0

    print(f"\n OVERALL RESULTS:")
    print(f"-" * 20)
    print(f"Syntax validation:")
    print(f"   Valid files: {valid_files}")
    print(f"   Invalid files: {invalid_files}")
    print(f"   Success rate: {(valid_files / (valid_files + invalid_files) * 100):.1f}%")

    print(f"\nType hint coverage:")
    print(f"   Total functions: {total_functions}")
    print(f"   Functions with hints: {total_with_hints}")
    print(f"   Overall coverage: {overall_coverage:.1f}%")
    print(f"   Target coverage: 80.0%")

    if overall_coverage >= 80.0:
        print(f" SUCCESS: Target coverage achieved!")
    else:
        remaining = 80.0 - overall_coverage
        print(f" Progress: {remaining:.1f}% more coverage needed")

    return {
        'valid_files': valid_files,
        'invalid_files': invalid_files,
        'overall_coverage': overall_coverage,
        'target_achieved': overall_coverage >= 80.0
    }

if __name__ == "__main__":
    results = main()

    # Exit with appropriate code
    if results['invalid_files'] > 0:
        sys.exit(1)  # Syntax errors found
    elif results['target_achieved']:
        sys.exit(0)  # Success
    else:
        sys.exit(2)  # More work needed
