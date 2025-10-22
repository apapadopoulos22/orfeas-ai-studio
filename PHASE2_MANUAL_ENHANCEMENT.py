#!/usr/bin/env python3
"""
ORFEAS AI - Phase 2 Manual Error Handling Enhancement
====================================================

Carefully add error handling to specific functions without breaking syntax.
"""

import re
from pathlib import Path
from typing import Dict, List

class ManualErrorHandlingEnhancer:
    """Manual, precise error handling enhancement"""

    def __init__(self):
        self.backend_dir = Path("backend")

    def restore_and_enhance_gpu_manager(self) -> bool:
        """Restore gpu_manager.py from git and add targeted error handling"""
        try:
            # Read current version
            file_path = self.backend_dir / "gpu_manager.py"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if already has logger
            if 'logger = logging.getLogger(__name__)' not in content:
                # Add logging import after existing imports
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_pos = i + 1

                lines.insert(insert_pos, 'import logging')
                lines.insert(insert_pos + 1, '')
                lines.insert(insert_pos + 2, 'logger = logging.getLogger(__name__)')
                content = '\n'.join(lines)

            # Add simple error handling to get_memory_stats method
            if 'def get_memory_stats(self):' in content:
                content = re.sub(
                    r'(def get_memory_stats\(self\):\s*\n)((?:.*\n)*?)(\s*return.*\n)',
                    lambda m: (
                        m.group(1) +
                        '        try:\n' +
                        '            ' + m.group(2).replace('\n', '\n            ') +
                        '        except Exception as e:\n' +
                        '            logger.error(f"[GPU-MANAGER] Error getting memory stats: {e}")\n' +
                        '            return {"error": "GPU stats unavailable", "total": 0, "allocated": 0, "free": 0}\n'
                    ),
                    content,
                    flags=re.DOTALL
                )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f" Enhanced gpu_manager.py with error handling")
            return True

        except Exception as e:
            print(f" Error enhancing gpu_manager.py: {e}")
            return False

    def add_simple_error_handling_to_functions(self, file_path: Path, function_patterns: List[str]) -> bool:
        """Add simple try-catch to specific functions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Add logging if missing
            if 'import logging' not in content:
                content = 'import logging\n' + content

            if 'logger = logging.getLogger(__name__)' not in content:
                content = content.replace('import logging', 'import logging\n\nlogger = logging.getLogger(__name__)')

            # Add basic error handling to specific functions
            for pattern in function_patterns:
                # Find function and add basic try-catch
                func_match = re.search(rf'(def {pattern}\([^)]*\):\s*\n)((?:(?!def |class ).*\n)*)', content, re.DOTALL)
                if func_match:
                    func_def = func_match.group(1)
                    func_body = func_match.group(2)

                    if 'try:' not in func_body and func_body.strip():
                        # Add basic try-catch wrapper
                        enhanced_body = f"""        try:
{func_body}        except Exception as e:
            logger.error(f"[{file_path.stem.upper()}] Error in {pattern}: {{e}}")
            raise
"""
                        content = content.replace(func_match.group(0), func_def + enhanced_body)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            print(f" Error enhancing {file_path.name}: {e}")
            return False

    def enhance_specific_files(self) -> Dict[str, bool]:
        """Add error handling to specific high-impact functions"""
        results = {}

        # Define specific functions to enhance for each file
        file_enhancements = {
            'batch_processor.py': ['submit_job', 'process_queue', 'get_job_status'],
            'validation.py': ['validate_image', 'validate_file_type', 'check_file_size'],
            'production_metrics.py': ['track_request', 'record_metric', 'get_metrics'],
            'agent_api.py': ['create_agent', 'execute_task', 'get_agent_status']
        }

        for file_name, functions in file_enhancements.items():
            file_path = self.backend_dir / file_name
            if file_path.exists():
                success = self.add_simple_error_handling_to_functions(file_path, functions)
                results[file_name] = success
                if success:
                    print(f" Enhanced {file_name} with error handling for {len(functions)} functions")
                else:
                    print(f" No changes needed for {file_name}")
            else:
                print(f"  {file_name} not found")
                results[file_name] = False

        return results

    def run_manual_enhancements(self) -> Dict[str, bool]:
        """Run manual error handling enhancements"""
        print(" PHASE 2: Manual Error Handling Enhancement")
        print("=" * 50)

        # First restore and enhance gpu_manager
        gpu_result = self.restore_and_enhance_gpu_manager()

        # Then enhance other files
        other_results = self.enhance_specific_files()

        all_results = {'gpu_manager.py': gpu_result, **other_results}

        enhanced_count = sum(all_results.values())
        total_count = len(all_results)

        print(f"\n MANUAL ENHANCEMENT SUMMARY")
        print(f"   Files processed: {total_count}")
        print(f"   Files enhanced: {enhanced_count}")
        print(f"   Success rate: {enhanced_count/total_count*100:.1f}%")

        return all_results

def main():
    """Main execution function"""
    print(" ORFEAS AI - Phase 2 Manual Error Handling")
    print("=" * 55)

    enhancer = ManualErrorHandlingEnhancer()
    results = enhancer.run_manual_enhancements()

    print(f"\n NEXT STEPS:")
    print(f"   1. Run validation to check improvements")
    print(f"   2. Execute TQM audit for final assessment")

    return results

if __name__ == "__main__":
    main()
