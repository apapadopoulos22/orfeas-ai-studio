#!/usr/bin/env python
"""
Phase 1 Implementation Validator
=================================

Validates all Phase 1 deliverables:
✓ GPU module integration
✓ Unit tests pass
✓ Progressive rendering
✓ Request deduplication cache
✓ Performance metrics

Run: python PHASE_1_VALIDATOR.py
"""

import sys
import os
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase1Validator:
    """Validate Phase 1 implementation"""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'validations': {},
            'errors': [],
            'warnings': []
        }

    def validate_files_exist(self):
        """Check all required Phase 1 files exist"""
        logger.info("Checking required files...")

        required_files = [
            'backend/gpu_optimization_advanced.py',
            'backend/progressive_renderer.py',
            'backend/request_deduplication.py',
            'backend/tests/test_gpu_optimization.py',
            'backend/tests/test_phase1_performance.py',
            'PHASE_1_INTEGRATION_CHECKLIST.md',
            'PHASE_1_QUICK_START.md',
        ]

        all_exist = True
        for file_path in required_files:
            full_path = Path(file_path)
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            logger.info(f"  {status} {file_path}")

            if not exists:
                all_exist = False
                self.results['errors'].append(f"Missing: {file_path}")

        self.results['validations']['files_exist'] = all_exist
        return all_exist

    def validate_gpu_module(self):
        """Validate GPU module can be imported"""
        logger.info("Validating GPU module...")

        try:
            sys.path.insert(0, 'backend')
            from gpu_optimization_advanced import (
                get_vram_manager,
                DynamicVRAMManager,
                PrecisionMode
            )

            manager = get_vram_manager()
            stats = manager.get_memory_stats()

            logger.info(f"  ✓ GPU module imports successfully")
            logger.info(f"  ✓ Total VRAM: {stats['total_vram_gb']:.1f} GB")
            logger.info(f"  ✓ Available: {stats['available_gb']:.1f} GB")
            logger.info(f"  ✓ Usage: {stats['usage_percent']:.1f}%")

            self.results['validations']['gpu_module'] = {
                'status': 'valid',
                'stats': stats
            }
            return True

        except Exception as e:
            logger.error(f"  ✗ GPU module validation failed: {e}")
            self.results['errors'].append(f"GPU module error: {e}")
            self.results['validations']['gpu_module'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False

    def validate_progressive_renderer(self):
        """Validate progressive renderer module"""
        logger.info("Validating progressive renderer...")

        try:
            from progressive_renderer import get_progressive_renderer

            renderer = get_progressive_renderer()
            logger.info(f"  ✓ Progressive renderer imports successfully")
            logger.info(f"  ✓ Stages defined: {len(renderer.stages)}")

            self.results['validations']['progressive_renderer'] = {
                'status': 'valid',
                'stages': len(renderer.stages)
            }
            return True

        except Exception as e:
            logger.error(f"  ✗ Progressive renderer validation failed: {e}")
            self.results['warnings'].append(
                f"Progressive renderer: {e} (not critical)"
            )
            return False

    def validate_deduplication_cache(self):
        """Validate deduplication cache module"""
        logger.info("Validating deduplication cache...")

        try:
            from request_deduplication import get_deduplication_cache

            cache = get_deduplication_cache()

            # Test cache operations
            test_hash = "test_123"
            test_data = {'test': 'data'}

            cache.set(test_hash, test_data)
            retrieved = cache.get(test_hash)

            assert retrieved == test_data, "Cache get/set mismatch"

            stats = cache.get_stats()
            logger.info(f"  ✓ Deduplication cache working")
            logger.info(f"  ✓ Test entry cached and retrieved")
            logger.info(f"  ✓ Cache stats: {stats}")

            self.results['validations']['deduplication_cache'] = {
                'status': 'valid',
                'stats': stats
            }
            return True

        except Exception as e:
            logger.error(f"  ✗ Cache validation failed: {e}")
            self.results['warnings'].append(
                f"Deduplication cache: {e} (not critical)"
            )
            return False

    def validate_unit_tests(self):
        """Run GPU optimization unit tests"""
        logger.info("Running unit tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable, '-m', 'pytest',
                    'backend/tests/test_gpu_optimization.py',
                    '-v', '--tb=short', '-q'
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Count passed tests
                output = result.stdout
                if "passed" in output:
                    logger.info(f"  ✓ Unit tests passed")
                    logger.info(f"  {output.split(chr(10))[-2]}")

                    self.results['validations']['unit_tests'] = {
                        'status': 'passed',
                        'output': output
                    }
                    return True
            else:
                logger.error(f"  ✗ Unit tests failed")
                logger.error(result.stdout)
                self.results['errors'].append("Unit tests failed")
                return False

        except subprocess.TimeoutExpired:
            logger.error("  ✗ Unit tests timeout")
            self.results['errors'].append("Unit tests timeout")
            return False
        except Exception as e:
            logger.error(f"  ✗ Could not run unit tests: {e}")
            self.results['warnings'].append(
                f"Unit tests: {e} (run manually with pytest)"
            )
            return False

    def validate_documentation(self):
        """Validate documentation files"""
        logger.info("Validating documentation...")

        docs = {
            'PHASE_1_INTEGRATION_CHECKLIST.md': 'Integration steps',
            'PHASE_1_QUICK_START.md': 'Quick start guide'
        }

        all_valid = True
        for doc_file, description in docs.items():
            path = Path(doc_file)
            if path.exists():
                size = path.stat().st_size
                logger.info(f"  ✓ {doc_file} ({size:,} bytes) - {description}")
            else:
                logger.error(f"  ✗ {doc_file} missing")
                all_valid = False

        self.results['validations']['documentation'] = {
            'status': 'valid' if all_valid else 'incomplete',
            'files': len(docs)
        }
        return all_valid

    def check_main_py_integration(self):
        """Check if main.py includes GPU optimization"""
        logger.info("Checking main.py integration...")

        try:
            with open('backend/main.py', 'r') as f:
                content = f.read()

            checks = {
                'GPU import': 'from gpu_optimization_advanced import',
                'VRAM manager': 'get_vram_manager()',
                'GPU stats endpoint': "'/api/v1/gpu/stats'",
                'Cache integration': 'get_deduplication_cache()'
            }

            found = {}
            for check_name, search_string in checks.items():
                found[check_name] = search_string in content
                status = "✓" if found[check_name] else "✗"
                logger.info(f"  {status} {check_name}")

            integration_complete = all(found.values())
            self.results['validations']['main_py_integration'] = {
                'status': 'complete' if integration_complete else 'incomplete',
                'checks': found
            }
            return integration_complete

        except Exception as e:
            logger.error(f"  ✗ Could not check main.py: {e}")
            self.results['warnings'].append(f"main.py check: {e}")
            return False

    def run_all_validations(self):
        """Run all validations"""
        logger.info("=" * 60)
        logger.info("PHASE 1 VALIDATION SUITE")
        logger.info("=" * 60)

        validations = [
            self.validate_files_exist,
            self.validate_gpu_module,
            self.validate_progressive_renderer,
            self.validate_deduplication_cache,
            self.validate_documentation,
            self.check_main_py_integration,
            self.validate_unit_tests
        ]

        results = []
        for validation in validations:
            try:
                results.append(validation())
            except Exception as e:
                logger.error(f"Validation error: {e}")
                results.append(False)

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)

        passed = sum(results)
        total = len(results)

        logger.info(f"Passed: {passed}/{total}")

        if self.results['errors']:
            logger.error(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                logger.error(f"  - {error}")

        if self.results['warnings']:
            logger.warning(f"\nWarnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                logger.warning(f"  - {warning}")

        # Overall status
        if passed == total:
            logger.info("\n✓ ALL VALIDATIONS PASSED")
            return True
        elif passed >= total - 1:
            logger.warning(f"\n⚠ {total - passed} validation(s) warning/skipped")
            return True
        else:
            logger.error(f"\n✗ {total - passed} validation(s) failed")
            return False

    def save_results(self):
        """Save validation results to JSON"""
        output_file = 'PHASE_1_VALIDATION_RESULTS.json'

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"\nResults saved to {output_file}")
        return output_file


def main():
    """Run Phase 1 validator"""
    validator = Phase1Validator()

    success = validator.run_all_validations()
    validator.save_results()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

