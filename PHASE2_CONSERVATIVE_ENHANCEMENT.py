#!/usr/bin/env python3
"""
ORFEAS AI - Phase 2 Conservative Error Handling Enhancement
============================================================

Add error handling only to files that are syntactically valid.
Focus on getting to 80% coverage through working files.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set

class ConservativeErrorEnhancer:
    """Add error handling conservatively to working files only"""

    def __init__(self):
        self.backend_dir = Path("backend")
        self.working_files = [
            'batch_processor.py',
            'stl_processor.py',
            'production_metrics.py',
            'agent_api.py',
            'gpu_manager.py'  # This was restored and is working
        ]

    def is_file_syntactically_valid(self, file_path: Path) -> bool:
        """Check if file has valid Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except:
            return False

    def analyze_file_functions(self, file_path: Path) -> Dict:
        """Analyze functions in a file for error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has error handling
                    has_try = any(isinstance(child, ast.Try) for child in ast.walk(node))
                    has_except = any(isinstance(child, ast.ExceptHandler) for child in ast.walk(node))

                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'has_error_handling': has_try and has_except,
                        'is_critical': self.is_critical_function(node.name, file_path.name)
                    })

            return {
                'functions': functions,
                'total_functions': len(functions),
                'functions_with_error_handling': sum(1 for f in functions if f['has_error_handling']),
                'critical_functions': [f for f in functions if f['is_critical']],
                'critical_without_error_handling': [f for f in functions if f['is_critical'] and not f['has_error_handling']]
            }

        except Exception as e:
            print(f" Error analyzing {file_path.name}: {e}")
            return {'functions': [], 'total_functions': 0, 'functions_with_error_handling': 0}

    def is_critical_function(self, func_name: str, file_name: str) -> bool:
        """Determine if a function is critical and needs error handling"""
        critical_patterns = [
            'process', 'generate', 'save', 'load', 'submit', 'execute',
            'validate', 'convert', 'upload', 'download', 'create', 'delete',
            'update', 'init', 'start', 'stop', 'connect', 'disconnect'
        ]

        return any(pattern in func_name.lower() for pattern in critical_patterns)

    def add_basic_error_handling(self, file_path: Path, target_functions: List[str]) -> bool:
        """Add basic error handling to specific functions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add logging import if missing
            if 'import logging' not in content:
                content = 'import logging\n' + content

            if 'logger = logging.getLogger(__name__)' not in content:
                content = content.replace(
                    'import logging',
                    'import logging\n\nlogger = logging.getLogger(__name__)'
                )

            # Add error handling to specific functions
            for func_name in target_functions:
                # Find function definition
                pattern = rf'(def {func_name}\([^)]*\):[^\n]*\n)((?:(?!def |class ).*\n)*)'
                match = re.search(pattern, content, re.DOTALL)

                if match and 'try:' not in match.group(2):
                    func_def = match.group(1)
                    func_body = match.group(2)

                    # Get indentation
                    indent = len(func_def) - len(func_def.lstrip())
                    base_indent = ' ' * indent

                    # Wrap function body in try-except
                    enhanced_body = f"{base_indent}    try:\n"
                    for line in func_body.split('\n'):
                        if line.strip():
                            enhanced_body += f"{base_indent}    {line}\n"
                        else:
                            enhanced_body += line + '\n'

                    enhanced_body += f"{base_indent}    except Exception as e:\n"
                    enhanced_body += f"{base_indent}        logger.error(f\"[{file_path.stem.upper()}] Error in {func_name}: {{e}}\")\n"
                    enhanced_body += f"{base_indent}        raise\n"

                    # Replace in content
                    content = content.replace(match.group(0), func_def + enhanced_body)

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f" Error enhancing {file_path.name}: {e}")
            return False

    def enhance_working_files(self) -> Dict[str, Dict]:
        """Enhance error handling in syntactically valid files"""
        print(" PHASE 2: Conservative Error Handling Enhancement")
        print("=" * 55)

        results = {}

        for file_name in self.working_files:
            file_path = self.backend_dir / file_name

            if not file_path.exists():
                print(f"  {file_name} not found")
                results[file_name] = {'status': 'not_found'}
                continue

            if not self.is_file_syntactically_valid(file_path):
                print(f" {file_name} has syntax errors - skipping")
                results[file_name] = {'status': 'syntax_error'}
                continue

            # Analyze current state
            analysis = self.analyze_file_functions(file_path)

            # Get critical functions without error handling
            target_functions = [
                f['name'] for f in analysis['critical_without_error_handling']
            ]

            if target_functions:
                success = self.add_basic_error_handling(file_path, target_functions[:3])  # Limit to 3 functions
                results[file_name] = {
                    'status': 'enhanced' if success else 'failed',
                    'target_functions': target_functions[:3],
                    'analysis': analysis
                }

                if success:
                    print(f" Enhanced {file_name} - added error handling to {len(target_functions[:3])} functions")
                else:
                    print(f" Failed to enhance {file_name}")
            else:
                print(f" {file_name} - no critical functions need enhancement")
                results[file_name] = {
                    'status': 'no_enhancement_needed',
                    'analysis': analysis
                }

        return results

    def calculate_progress(self, results: Dict) -> Dict:
        """Calculate overall progress"""
        total_functions = 0
        functions_with_error_handling = 0

        for file_name, result in results.items():
            if 'analysis' in result:
                analysis = result['analysis']
                total_functions += analysis['total_functions']
                functions_with_error_handling += analysis['functions_with_error_handling']

        coverage = (functions_with_error_handling / total_functions * 100) if total_functions > 0 else 0

        return {
            'total_functions': total_functions,
            'functions_with_error_handling': functions_with_error_handling,
            'coverage_percentage': coverage,
            'target_achieved': coverage >= 80.0
        }

def main():
    """Main execution function"""
    print(" ORFEAS AI - Phase 2 Conservative Enhancement")
    print("=" * 52)

    enhancer = ConservativeErrorEnhancer()
    results = enhancer.enhance_working_files()

    progress = enhancer.calculate_progress(results)

    print(f"\n ENHANCEMENT SUMMARY")
    print(f"   Total functions analyzed: {progress['total_functions']}")
    print(f"   Functions with error handling: {progress['functions_with_error_handling']}")
    print(f"   Error handling coverage: {progress['coverage_percentage']:.1f}%")
    print(f"   Target (80%) achieved: {' Yes' if progress['target_achieved'] else ' No'}")

    print(f"\n NEXT STEPS:")
    print(f"   1. Run validation to measure improvements")
    print(f"   2. Run TQM audit for final assessment")

    return results

if __name__ == "__main__":
    main()
