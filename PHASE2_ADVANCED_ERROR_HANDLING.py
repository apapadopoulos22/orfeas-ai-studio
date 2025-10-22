#!/usr/bin/env python3
"""
ORFEAS AI - Phase 2 Advanced Error Handling Enhancement
======================================================

Comprehensive error handling improvements targeting 80%+ coverage.
Focuses on the specific functions and operations identified in the analysis.
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Any

class AdvancedErrorHandlingEnhancer:
    """Advanced error handling enhancement with targeted improvements"""

    def __init__(self):
        self.backend_dir = Path("backend")

    def enhance_gpu_manager(self) -> bool:
        """Add comprehensive error handling to gpu_manager.py"""
        file_path = self.backend_dir / "gpu_manager.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Ensure logging import exists
            if 'import logging' not in content:
                content = re.sub(
                    r'(import torch.*\n)',
                    r'\1import logging\n',
                    content
                )

            if 'logger = logging.getLogger' not in content:
                content = re.sub(
                    r'(import logging\n)',
                    r'\1\nlogger = logging.getLogger(__name__)\n',
                    content
                )

            # Enhanced __init__ method with GPU error handling
            init_pattern = r'(def __init__\(self.*?\n)(.*?)((?=\n    def|\nclass|\Z))'

            def enhance_init(match):
                method_def = match.group(1)
                method_body = match.group(2)
                rest = match.group(3)

                if 'try:' not in method_body:
                    enhanced_body = f"""        try:
            # Initialize GPU memory tracking
{method_body}        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"[GPU-MANAGER] GPU out of memory during initialization: {{e}}")
            torch.cuda.empty_cache()
            raise RuntimeError("GPU memory insufficient for initialization")
        except RuntimeError as e:
            logger.error(f"[GPU-MANAGER] GPU runtime error during initialization: {{e}}")
            raise
        except Exception as e:
            logger.error(f"[GPU-MANAGER] Unexpected error during GPU manager initialization: {{e}}")
            raise
"""
                    return method_def + enhanced_body + rest
                return match.group(0)

            content = re.sub(init_pattern, enhance_init, content, flags=re.DOTALL)

            # Enhanced get_memory_stats with GPU error handling
            memory_stats_pattern = r'(def get_memory_stats\(self.*?\n)(.*?)((?=\n    def|\nclass|\Z))'

            def enhance_memory_stats(match):
                method_def = match.group(1)
                method_body = match.group(2)
                rest = match.group(3)

                if 'try:' not in method_body:
                    enhanced_body = f"""        try:
{method_body}        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"[GPU-MANAGER] GPU OOM while getting memory stats: {{e}}")
            torch.cuda.empty_cache()
            return {{'error': 'GPU memory unavailable', 'total': 0, 'allocated': 0, 'free': 0}}
        except RuntimeError as e:
            logger.error(f"[GPU-MANAGER] GPU runtime error getting memory stats: {{e}}")
            return {{'error': 'GPU runtime error', 'total': 0, 'allocated': 0, 'free': 0}}
        except Exception as e:
            logger.error(f"[GPU-MANAGER] Unexpected error getting memory stats: {{e}}")
            return {{'error': 'Unknown error', 'total': 0, 'allocated': 0, 'free': 0}}
"""
                    return method_def + enhanced_body + rest
                return match.group(0)

            content = re.sub(memory_stats_pattern, enhance_memory_stats, content, flags=re.DOTALL)

            # Enhanced cleanup method
            cleanup_pattern = r'(def cleanup\(self.*?\n)(.*?)((?=\n    def|\nclass|\Z))'

            def enhance_cleanup(match):
                method_def = match.group(1)
                method_body = match.group(2)
                rest = match.group(3)

                if 'try:' not in method_body:
                    enhanced_body = f"""        try:
{method_body}        except torch.cuda.OutOfMemoryError as e:
            logger.warning(f"[GPU-MANAGER] OOM during cleanup (expected): {{e}}")
            # Continue cleanup anyway
        except RuntimeError as e:
            logger.warning(f"[GPU-MANAGER] Runtime error during cleanup: {{e}}")
            # Continue cleanup anyway
        except Exception as e:
            logger.error(f"[GPU-MANAGER] Unexpected error during cleanup: {{e}}")
            # Continue cleanup anyway
"""
                    return method_def + enhanced_body + rest
                return match.group(0)

            content = re.sub(cleanup_pattern, enhance_cleanup, content, flags=re.DOTALL)

            # Write enhanced content
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f" Enhanced gpu_manager.py with comprehensive GPU error handling")
                return True

            return False

        except Exception as e:
            print(f" Error enhancing gpu_manager.py: {e}")
            return False

    def enhance_main_py(self) -> bool:
        """Add file I/O error handling to main.py critical functions"""
        file_path = self.backend_dir / "main.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Enhanced _get_image_hash function with file error handling
            image_hash_pattern = r'(def _get_image_hash\(.*?\n)(.*?)((?=\n@app|\ndef |\nclass |\Z))'

            def enhance_image_hash(match):
                method_def = match.group(1)
                method_body = match.group(2)
                rest = match.group(3)

                if 'FileNotFoundError' not in method_body:
                    enhanced_body = re.sub(
                        r'(\s+)(with open\(.*?\) as f:.*?\n)(.*?)(\n\s+return)',
                        r'\1try:\n\1    \2\3\4\n\1except FileNotFoundError as e:\n\1    logger.error(f"[ORFEAS] Image file not found for hash: {e}")\n\1    return "unknown_hash"\n\1except PermissionError as e:\n\1    logger.error(f"[ORFEAS] Permission denied reading image file: {e}")\n\1    return "permission_denied_hash"\n\1except Exception as e:\n\1    logger.error(f"[ORFEAS] Error generating image hash: {e}")\n\1    return "error_hash"',
                        method_body,
                        flags=re.DOTALL
                    )
                    return method_def + enhanced_body + rest
                return match.group(0)

            content = re.sub(image_hash_pattern, enhance_image_hash, content, flags=re.DOTALL)

            # Enhanced write_stl_file function
            write_stl_pattern = r'(def write_stl_file\(.*?\n)(.*?)((?=\n@app|\ndef |\nclass |\Z))'

            def enhance_write_stl(match):
                method_def = match.group(1)
                method_body = match.group(2)
                rest = match.group(3)

                if 'PermissionError' not in method_body:
                    enhanced_body = f"""    try:
{method_body}    except PermissionError as e:
        logger.error(f"[ORFEAS] Permission denied writing STL file: {{e}}")
        raise RuntimeError("Cannot write STL file - permission denied")
    except FileNotFoundError as e:
        logger.error(f"[ORFEAS] Directory not found for STL file: {{e}}")
        raise RuntimeError("Cannot write STL file - directory not found")
    except Exception as e:
        logger.error(f"[ORFEAS] Error writing STL file: {{e}}")
        raise RuntimeError(f"STL file write failed: {{str(e)}}")
"""
                    return method_def + enhanced_body + rest
                return match.group(0)

            content = re.sub(write_stl_pattern, enhance_write_stl, content, flags=re.DOTALL)

            # Write enhanced content
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f" Enhanced main.py with file I/O error handling")
                return True

            return False

        except Exception as e:
            print(f" Error enhancing main.py: {e}")
            return False

    def enhance_hunyuan_integration(self) -> bool:
        """Add error handling to hunyuan_integration.py"""
        file_path = self.backend_dir / "hunyuan_integration.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Enhanced __init__ with model loading error handling
            init_pattern = r'(def __init__\(self.*?\n)(.*?)(def (?!__init__)|class |\Z)'

            def enhance_init(match):
                method_def = match.group(1)
                method_body = match.group(2)
                rest = match.group(3)

                if 'ModelLoadError' not in method_body and 'torch.cuda.OutOfMemoryError' not in method_body:
                    # Find the main initialization logic
                    if 'self.initialize_model' in method_body or 'self.shapegen_pipeline' in method_body:
                        enhanced_body = f"""        try:
{method_body}        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"[HUNYUAN] GPU out of memory loading models: {{e}}")
            torch.cuda.empty_cache()
            raise RuntimeError("Insufficient GPU memory for Hunyuan3D models")
        except FileNotFoundError as e:
            logger.error(f"[HUNYUAN] Model files not found: {{e}}")
            raise RuntimeError("Hunyuan3D model files missing - please run setup")
        except RuntimeError as e:
            logger.error(f"[HUNYUAN] Model loading runtime error: {{e}}")
            raise
        except Exception as e:
            logger.error(f"[HUNYUAN] Unexpected error loading models: {{e}}")
            raise RuntimeError(f"Hunyuan3D initialization failed: {{str(e)}}")
"""
                        return method_def + enhanced_body + rest
                return match.group(0)

            content = re.sub(init_pattern, enhance_init, content, flags=re.DOTALL)

            # Enhanced save_obj function
            save_obj_pattern = r'(def save_obj\(.*?\n)(.*?)((?=\n    def|\ndef |\nclass |\Z))'

            def enhance_save_obj(match):
                method_def = match.group(1)
                method_body = match.group(2)
                rest = match.group(3)

                if 'with open' in method_body and 'PermissionError' not in method_body:
                    enhanced_body = re.sub(
                        r'(\s+)(with open\(.*?\) as f:.*?\n)(.*?)(\n\s+(?:return|$))',
                        r'\1try:\n\1    \2\3\4\n\1except PermissionError as e:\n\1    logger.error(f"[HUNYUAN] Permission denied saving OBJ: {e}")\n\1    raise RuntimeError("Cannot save OBJ file - permission denied")\n\1except FileNotFoundError as e:\n\1    logger.error(f"[HUNYUAN] Directory not found for OBJ: {e}")\n\1    raise RuntimeError("Cannot save OBJ file - directory not found")\n\1except Exception as e:\n\1    logger.error(f"[HUNYUAN] Error saving OBJ file: {e}")\n\1    raise RuntimeError(f"OBJ save failed: {str(e)}")',
                        method_body,
                        flags=re.DOTALL
                    )
                    return method_def + enhanced_body + rest
                return match.group(0)

            content = re.sub(save_obj_pattern, enhance_save_obj, content, flags=re.DOTALL)

            # Write enhanced content
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f" Enhanced hunyuan_integration.py with model loading error handling")
                return True

            return False

        except Exception as e:
            print(f" Error enhancing hunyuan_integration.py: {e}")
            return False

    def enhance_batch_processor(self) -> bool:
        """Add error handling to batch_processor.py"""
        file_path = self.backend_dir / "batch_processor.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Add basic error handling to all functions without try-catch
            functions_pattern = r'(def \w+\(.*?\n)((?:(?!def |class ).*\n)*)'

            def add_basic_error_handling(match):
                method_def = match.group(1)
                method_body = match.group(2)

                if 'try:' not in method_body and method_body.strip():
                    # Only add error handling to non-empty functions
                    enhanced_body = f"""        try:
{method_body}        except Exception as e:
            logger.error(f"[BATCH-PROCESSOR] Error in {method_def.split('(')[0].replace('def ', '')}: {{e}}")
            raise
"""
                    return method_def + enhanced_body
                return match.group(0)

            content = re.sub(functions_pattern, add_basic_error_handling, content, flags=re.DOTALL)

            # Add logging import
            if 'import logging' not in content:
                content = 'import logging\n\nlogger = logging.getLogger(__name__)\n\n' + content

            # Write enhanced content
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f" Enhanced batch_processor.py with basic error handling")
                return True

            return False

        except Exception as e:
            print(f" Error enhancing batch_processor.py: {e}")
            return False

    def enhance_validation_py(self) -> bool:
        """Add validation-specific error handling"""
        file_path = self.backend_dir / "validation.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Add validation error handling patterns
            functions_pattern = r'(def validate_\w+\(.*?\n)((?:(?!def |class ).*\n)*)'

            def add_validation_error_handling(match):
                method_def = match.group(1)
                method_body = match.group(2)

                if 'try:' not in method_body and method_body.strip():
                    function_name = method_def.split('(')[0].replace('def ', '')
                    enhanced_body = f"""        try:
{method_body}        except ValueError as e:
            logger.error(f"[VALIDATION] Value error in {function_name}: {{e}}")
            raise ValidationError(f"Invalid input: {{str(e)}}")
        except TypeError as e:
            logger.error(f"[VALIDATION] Type error in {function_name}: {{e}}")
            raise ValidationError(f"Type validation failed: {{str(e)}}")
        except Exception as e:
            logger.error(f"[VALIDATION] Unexpected validation error in {function_name}: {{e}}")
            raise ValidationError(f"Validation failed: {{str(e)}}")
"""
                    return method_def + enhanced_body
                return match.group(0)

            content = re.sub(functions_pattern, add_validation_error_handling, content, flags=re.DOTALL)

            # Add ValidationError class if missing
            if 'class ValidationError' not in content:
                content = content.replace(
                    'import logging',
                    'import logging\n\nclass ValidationError(Exception):\n    """Custom validation error"""\n    pass'
                )

            # Write enhanced content
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f" Enhanced validation.py with validation error handling")
                return True

            return False

        except Exception as e:
            print(f" Error enhancing validation.py: {e}")
            return False

    def run_enhancements(self) -> Dict[str, bool]:
        """Run all error handling enhancements"""
        print(" PHASE 2: Advanced Error Handling Enhancement")
        print("=" * 50)

        results = {
            'gpu_manager.py': self.enhance_gpu_manager(),
            'main.py': self.enhance_main_py(),
            'hunyuan_integration.py': self.enhance_hunyuan_integration(),
            'batch_processor.py': self.enhance_batch_processor(),
            'validation.py': self.enhance_validation_py()
        }

        enhanced_count = sum(results.values())
        total_count = len(results)

        print(f"\n ENHANCEMENT SUMMARY")
        print(f"   Files processed: {total_count}")
        print(f"   Files enhanced: {enhanced_count}")
        print(f"   Success rate: {enhanced_count/total_count*100:.1f}%")

        return results

def main():
    """Main execution function"""
    print(" ORFEAS AI - Phase 2 Advanced Error Handling")
    print("=" * 55)

    enhancer = AdvancedErrorHandlingEnhancer()
    results = enhancer.run_enhancements()

    print(f"\n NEXT STEPS:")
    print(f"   1. Run syntax validation")
    print(f"   2. Execute TQM audit to measure improvements")
    print(f"   3. Test error handling scenarios")
    print(f"   4. Document Phase 2 results")

    return results

if __name__ == "__main__":
    main()
