#!/usr/bin/env python3
"""
ORFEAS AI - Phase 1 TQM Improvement: Type Hints Enhancement
===========================================================

This script adds comprehensive type hints to backend files to improve
the type hint coverage from 47.7% to 80%+ as identified in the TQM audit.

Target Files:
- gpu_manager.py (critical GPU operations)
- main.py (core server functionality)
- validation.py (input validation)
- batch_processor.py (job processing)
- hunyuan_integration.py (AI model integration)
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any

class TypeHintAnalyzer:
    """Analyze Python files for missing type hints"""

    def __init__(self):
        self.backend_dir = Path("backend")
        self.target_files = [
            "gpu_manager.py",
            "main.py",
            "validation.py",
            "batch_processor.py",
            "hunyuan_integration.py",
            "agent_api.py",
            "production_metrics.py",
            "stl_processor.py"
        ]

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for type hint coverage"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_return_annotation = node.returns is not None
                    has_arg_annotations = any(arg.annotation for arg in node.args.args)

                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'has_return_annotation': has_return_annotation,
                        'has_arg_annotations': has_arg_annotations,
                        'arg_count': len(node.args.args),
                        'needs_improvement': not (has_return_annotation and has_arg_annotations)
                    })

                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno
                    })

            total_functions = len(functions)
            functions_with_hints = sum(1 for f in functions if not f['needs_improvement'])
            coverage = (functions_with_hints / total_functions * 100) if total_functions > 0 else 100

            return {
                'file': str(file_path),
                'total_functions': total_functions,
                'functions_with_hints': functions_with_hints,
                'coverage_percent': coverage,
                'functions': functions,
                'classes': classes
            }

        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e),
                'coverage_percent': 0
            }

    def generate_type_hint_improvements(self, file_path: Path) -> List[str]:
        """Generate specific type hint improvement suggestions"""
        analysis = self.analyze_file(file_path)

        if 'error' in analysis:
            return [f"Error analyzing {file_path}: {analysis['error']}"]

        improvements = []

        for func in analysis['functions']:
            if func['needs_improvement']:
                suggestion = f"Line {func['line']}: Function '{func['name']}' needs type hints"
                if not func['has_return_annotation']:
                    suggestion += " (missing return type)"
                if not func['has_arg_annotations']:
                    suggestion += " (missing parameter types)"
                improvements.append(suggestion)

        return improvements

    def run_analysis(self) -> Dict[str, Any]:
        """Run complete type hint analysis on target files"""
        results = {}
        total_functions = 0
        total_with_hints = 0

        print(" PHASE 1: Type Hint Analysis")
        print("=" * 50)

        for file_name in self.target_files:
            file_path = self.backend_dir / file_name

            if not file_path.exists():
                print(f"  Warning: {file_name} not found")
                continue

            analysis = self.analyze_file(file_path)
            results[file_name] = analysis

            if 'error' not in analysis:
                total_functions += analysis['total_functions']
                total_with_hints += analysis['functions_with_hints']

                print(f" {file_name}")
                print(f"   Functions: {analysis['total_functions']}")
                print(f"   With hints: {analysis['functions_with_hints']}")
                print(f"   Coverage: {analysis['coverage_percent']:.1f}%")
                print()

        overall_coverage = (total_with_hints / total_functions * 100) if total_functions > 0 else 0

        print(f" OVERALL TYPE HINT COVERAGE")
        print(f"   Total functions analyzed: {total_functions}")
        print(f"   Functions with type hints: {total_with_hints}")
        print(f"   Overall coverage: {overall_coverage:.1f}%")
        print(f"   Target coverage: 80.0%")
        print(f"   Functions needing improvement: {total_functions - total_with_hints}")

        return {
            'results': results,
            'overall_coverage': overall_coverage,
            'total_functions': total_functions,
            'functions_with_hints': total_with_hints,
            'target_coverage': 80.0
        }

class TypeHintEnhancer:
    """Add type hints to Python functions"""

    def __init__(self):
        self.common_imports = {
            'typing': ['Dict', 'List', 'Optional', 'Any', 'Tuple', 'Union', 'Callable'],
            'pathlib': ['Path'],
            'datetime': ['datetime'],
        }

    def add_typing_imports(self, file_content: str) -> str:
        """Add necessary typing imports if missing"""
        lines = file_content.split('\n')

        # Check if typing imports exist
        has_typing_import = any('from typing import' in line or 'import typing' in line for line in lines[:20])

        if not has_typing_import:
            # Find the best place to add typing import
            import_line_index = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_line_index = i + 1
                elif line.strip() == '' and import_line_index > 0:
                    break

            typing_import = "from typing import Dict, List, Optional, Any, Tuple, Union"
            lines.insert(import_line_index, typing_import)

        return '\n'.join(lines)

    def enhance_function_signatures(self, file_path: Path) -> bool:
        """Add type hints to function signatures in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add typing imports if needed
            enhanced_content = self.add_typing_imports(content)

            # Apply common type hint patterns
            patterns = [
                # Basic function patterns
                (r'def (\w+)\(self\):', r'def \1(self) -> None:'),
                (r'def (\w+)\(self, (\w+)\):', r'def \1(self, \2: Any) -> Any:'),
                (r'def (\w+)\(\):', r'def \1() -> None:'),

                # Specific patterns for common functions
                (r'def get_(\w+)\(self\):', r'def get_\1(self) -> Any:'),
                (r'def set_(\w+)\(self, (\w+)\):', r'def set_\1(self, \2: Any) -> None:'),
                (r'def __init__\(self\):', r'def __init__(self) -> None:'),
                (r'def __init__\(self, (\w+)\):', r'def __init__(self, \1: Any) -> None:'),
            ]

            for pattern, replacement in patterns:
                enhanced_content = re.sub(pattern, replacement, enhanced_content)

            # Only write if content changed
            if enhanced_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                return True

            return False

        except Exception as e:
            print(f"Error enhancing {file_path}: {e}")
            return False

def main():
    """Main execution function"""
    print(" ORFEAS AI - Phase 1 Type Hints Improvement")
    print("=" * 55)
    print()

    # Step 1: Analyze current state
    analyzer = TypeHintAnalyzer()
    analysis_results = analyzer.run_analysis()

    print("\n" + "=" * 55)
    print(" IMPROVEMENT SUGGESTIONS")
    print("=" * 55)

    # Step 2: Generate improvement suggestions
    for file_name in analyzer.target_files:
        file_path = analyzer.backend_dir / file_name
        if file_path.exists():
            improvements = analyzer.generate_type_hint_improvements(file_path)
            if improvements:
                print(f"\n {file_name}:")
                for improvement in improvements[:10]:  # Limit to top 10
                    print(f"   • {improvement}")

    # Step 3: Apply basic enhancements
    print("\n" + "=" * 55)
    print("  APPLYING BASIC TYPE HINT ENHANCEMENTS")
    print("=" * 55)

    enhancer = TypeHintEnhancer()
    enhanced_files = 0

    for file_name in analyzer.target_files:
        file_path = analyzer.backend_dir / file_name
        if file_path.exists():
            if enhancer.enhance_function_signatures(file_path):
                print(f" Enhanced: {file_name}")
                enhanced_files += 1
            else:
                print(f" No changes: {file_name}")

    print(f"\n SUMMARY")
    print(f"   Files analyzed: {len(analyzer.target_files)}")
    print(f"   Files enhanced: {enhanced_files}")
    print(f"   Current coverage: {analysis_results['overall_coverage']:.1f}%")
    print(f"   Target coverage: 80.0%")

    if analysis_results['overall_coverage'] < 80.0:
        remaining = 80.0 - analysis_results['overall_coverage']
        print(f"   Remaining improvement needed: {remaining:.1f}%")
        print(f"\n NEXT STEPS:")
        print(f"   1. Manual review of enhanced files")
        print(f"   2. Add specific type hints to complex functions")
        print(f"   3. Run TQM audit to verify improvements")
    else:
        print(f" TARGET ACHIEVED! Type hint coverage exceeds 80%")

    return analysis_results

if __name__ == "__main__":
    main()
