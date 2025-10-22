#!/usr/bin/env python3
"""
ORFEAS AI - Phase 2 Error Handling Validation
=============================================

Validate syntax and measure error handling improvements after Phase 2 enhancements.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Any

class Phase2Validator:
    """Validate Phase 2 error handling improvements"""

    def __init__(self):
        self.backend_dir = Path("backend")
        self.target_files = [
            "gpu_manager.py",
            "main.py",
            "hunyuan_integration.py",
            "batch_processor.py",
            "validation.py",
            "stl_processor.py",
            "production_metrics.py",
            "agent_api.py"
        ]

    def validate_python_syntax(self, file_path: Path) -> Dict[str, Any]:
        """Validate Python syntax of enhanced file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse with AST
            ast.parse(content)

            return {
                'file': file_path.name,
                'syntax_valid': True,
                'error': None
            }

        except SyntaxError as e:
            return {
                'file': file_path.name,
                'syntax_valid': False,
                'error': f"Syntax error at line {e.lineno}: {e.msg}"
            }
        except Exception as e:
            return {
                'file': file_path.name,
                'syntax_valid': False,
                'error': f"Parse error: {str(e)}"
            }

    def analyze_error_handling_coverage(self, file_path: Path) -> Dict[str, Any]:
        """Analyze error handling coverage after enhancements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            total_functions = 0
            functions_with_error_handling = 0
            error_handling_patterns = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1

                    # Check for try-except blocks
                    has_try_except = any(isinstance(child, ast.Try) for child in ast.walk(node))

                    if has_try_except:
                        functions_with_error_handling += 1

                        # Analyze specific error types being caught
                        for child in ast.walk(node):
                            if isinstance(child, ast.Try):
                                for handler in child.handlers:
                                    if handler.type:
                                        if isinstance(handler.type, ast.Name):
                                            error_handling_patterns.append(handler.type.id)
                                        elif isinstance(handler.type, ast.Attribute):
                                            error_handling_patterns.append(f"{handler.type.value.id}.{handler.type.attr}")

            coverage = (functions_with_error_handling / total_functions * 100) if total_functions > 0 else 100

            return {
                'file': file_path.name,
                'total_functions': total_functions,
                'functions_with_error_handling': functions_with_error_handling,
                'coverage_percent': coverage,
                'error_types_handled': list(set(error_handling_patterns)),
                'improvement_applied': coverage > 50  # Assuming 50% was baseline
            }

        except Exception as e:
            return {
                'file': file_path.name,
                'error': str(e),
                'coverage_percent': 0
            }

    def check_specific_enhancements(self, file_path: Path) -> Dict[str, Any]:
        """Check for specific error handling patterns we added"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            enhancements_found = []

            # Check for GPU error handling
            if 'torch.cuda.OutOfMemoryError' in content:
                enhancements_found.append('GPU OutOfMemoryError handling')

            # Check for file I/O error handling
            if 'FileNotFoundError' in content and 'PermissionError' in content:
                enhancements_found.append('File I/O error handling')

            # Check for model loading error handling
            if 'ModelLoadError' in content or ('FileNotFoundError' in content and 'model' in content):
                enhancements_found.append('Model loading error handling')

            # Check for validation error handling
            if 'ValidationError' in content:
                enhancements_found.append('Validation error handling')

            # Check for logging integration
            if 'logger.error' in content:
                enhancements_found.append('Error logging integration')

            return {
                'file': file_path.name,
                'enhancements_found': enhancements_found,
                'enhancement_count': len(enhancements_found)
            }

        except Exception as e:
            return {
                'file': file_path.name,
                'error': str(e),
                'enhancement_count': 0
            }

    def run_validation(self) -> Dict[str, Any]:
        """Run comprehensive Phase 2 validation"""
        print(" PHASE 2: Error Handling Validation")
        print("=" * 50)

        syntax_results = []
        coverage_results = []
        enhancement_results = []

        total_functions = 0
        total_with_error_handling = 0

        for file_name in self.target_files:
            file_path = self.backend_dir / file_name

            if not file_path.exists():
                print(f"  Warning: {file_name} not found")
                continue

            # Syntax validation
            syntax_result = self.validate_python_syntax(file_path)
            syntax_results.append(syntax_result)

            if syntax_result['syntax_valid']:
                print(f" {file_name}: Syntax valid")
            else:
                print(f" {file_name}: {syntax_result['error']}")
                continue

            # Coverage analysis
            coverage_result = self.analyze_error_handling_coverage(file_path)
            coverage_results.append(coverage_result)

            if 'error' not in coverage_result:
                total_functions += coverage_result['total_functions']
                total_with_error_handling += coverage_result['functions_with_error_handling']

                print(f" {file_name}: {coverage_result['coverage_percent']:.1f}% error handling coverage")
                print(f"   Functions: {coverage_result['functions_with_error_handling']}/{coverage_result['total_functions']}")
                print(f"   Error types: {', '.join(coverage_result['error_types_handled'][:5])}")

            # Enhancement check
            enhancement_result = self.check_specific_enhancements(file_path)
            enhancement_results.append(enhancement_result)

            if 'error' not in enhancement_result:
                print(f" {file_name}: {enhancement_result['enhancement_count']} specific enhancements")
                for enhancement in enhancement_result['enhancements_found']:
                    print(f"   • {enhancement}")

            print()

        # Overall statistics
        overall_coverage = (total_with_error_handling / total_functions * 100) if total_functions > 0 else 0
        syntax_success_rate = sum(1 for r in syntax_results if r['syntax_valid']) / len(syntax_results) * 100

        print(" PHASE 2 VALIDATION SUMMARY")
        print("=" * 50)
        print(f"   Syntax validation success rate: {syntax_success_rate:.1f}%")
        print(f"   Overall error handling coverage: {overall_coverage:.1f}%")
        print(f"   Total functions analyzed: {total_functions}")
        print(f"   Functions with error handling: {total_with_error_handling}")
        print(f"   Target coverage: 80.0%")

        if overall_coverage >= 80.0:
            print(f" PHASE 2 TARGET ACHIEVED!")
            print(f"   Error handling coverage exceeds 80%")
        else:
            remaining = 80.0 - overall_coverage
            print(f" PROGRESS MADE - {remaining:.1f}% remaining to reach 80% target")

        return {
            'syntax_results': syntax_results,
            'coverage_results': coverage_results,
            'enhancement_results': enhancement_results,
            'overall_coverage': overall_coverage,
            'syntax_success_rate': syntax_success_rate,
            'target_achieved': overall_coverage >= 80.0
        }

def main():
    """Main validation execution"""
    print(" ORFEAS AI - Phase 2 Error Handling Validation")
    print("=" * 55)
    print()

    validator = Phase2Validator()
    results = validator.run_validation()

    print(f"\n VALIDATION COMPLETE")
    print(f"   Files validated: {len(validator.target_files)}")
    print(f"   Syntax success: {results['syntax_success_rate']:.1f}%")
    print(f"   Error handling coverage: {results['overall_coverage']:.1f}%")
    print(f"   Target achieved: {'Yes' if results['target_achieved'] else 'No'}")

    return results

if __name__ == "__main__":
    main()
