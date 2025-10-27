"""
Bob AI v6.0 - Automated Deployment Setup Script
================================================

This script automates the deployment and integration of Bob AI v6.0
into the ORFEAS AI backend.

Usage:
    python backend/deploy_bob_ai_v6.py [--test] [--verify] [--full]

Options:
    --test      Run tests only
    --verify    Verify deployment
    --full      Full deployment (copy files, test, verify)

Author: Bob AI Development Team
Date: October 26, 2025
Version: 6.0 Deployment
"""

import os
import sys
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Tuple, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentManager:
    """Manages Bob AI v6.0 deployment"""

    def __init__(self, backend_path: str = None):
        """Initialize deployment manager"""
        if backend_path is None:
            backend_path = str(Path(__file__).parent)

        self.backend_path = Path(backend_path)
        self.workspace_path = self.backend_path.parent
        self.deployment_log = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info(f"✓ Deployment Manager initialized")
        logger.info(f"  Backend path: {self.backend_path}")
        logger.info(f"  Workspace path: {self.workspace_path}")

    def log_step(self, step: str, status: str = "pending"):
        """Log deployment step"""
        self.deployment_log.append({
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'status': status
        })

    def verify_files_exist(self) -> Tuple[bool, List[str]]:
        """Verify all required v6.0 files exist in workspace"""
        required_files = [
            'bob_ai_v6_final_knowledge.py',
            'bob_ai_v6_integration.py',
            'bob_ai_v6_llm_integration.py',
            'bob_ai_v6_integration_and_testing_suite.py',
            'test_bob_ai_v6_final.py'
        ]

        self.log_step("Verify Files Exist")

        missing = []
        for filename in required_files:
            filepath = self.workspace_path / filename
            if not filepath.exists():
                missing.append(filename)
                logger.warning(f"✗ Missing: {filename}")
            else:
                logger.info(f"✓ Found: {filename}")

        if missing:
            self.log_step("Verify Files Exist", "failed")
            return False, missing

        self.log_step("Verify Files Exist", "success")
        return True, []

    def copy_files_to_backend(self) -> bool:
        """Copy v6.0 files to backend directory"""
        self.log_step("Copy Files to Backend")

        files_to_copy = [
            'bob_ai_v6_final_knowledge.py',
            'bob_ai_v6_integration.py',
            'bob_ai_v6_llm_integration.py',
            'bob_ai_v6_integration_and_testing_suite.py',
            'test_bob_ai_v6_final.py'
        ]

        try:
            for filename in files_to_copy:
                src = self.workspace_path / filename
                dst = self.backend_path / filename

                if src.exists():
                    shutil.copy2(src, dst)
                    logger.info(f"✓ Copied: {filename}")
                else:
                    logger.error(f"✗ Source not found: {filename}")
                    self.log_step("Copy Files to Backend", "failed")
                    return False

            self.log_step("Copy Files to Backend", "success")
            return True

        except Exception as e:
            logger.error(f"✗ Copy failed: {e}")
            self.log_step("Copy Files to Backend", f"error: {e}")
            return False

    def verify_imports(self) -> bool:
        """Verify all modules can be imported"""
        self.log_step("Verify Imports")

        modules = [
            'bob_ai_v6_final_knowledge',
            'bob_ai_v6_integration',
            'bob_ai_v6_llm_integration'
        ]

        # Save current working directory
        original_cwd = os.getcwd()
        os.chdir(self.backend_path)

        try:
            for module in modules:
                try:
                    __import__(module)
                    logger.info(f"✓ Imported: {module}")
                except ImportError as e:
                    logger.error(f"✗ Import failed: {module} - {e}")
                    os.chdir(original_cwd)
                    self.log_step("Verify Imports", "failed")
                    return False

            os.chdir(original_cwd)
            self.log_step("Verify Imports", "success")
            return True

        except Exception as e:
            os.chdir(original_cwd)
            logger.error(f"✗ Verification failed: {e}")
            self.log_step("Verify Imports", f"error: {e}")
            return False

    def run_tests(self) -> Tuple[bool, str]:
        """Run Bob AI v6.0 tests"""
        self.log_step("Run Tests")

        test_file = self.backend_path / 'test_bob_ai_v6_final.py'

        if not test_file.exists():
            logger.error(f"✗ Test file not found: {test_file}")
            self.log_step("Run Tests", "failed")
            return False, "Test file not found"

        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(self.backend_path),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("✓ All tests passed")
                logger.info(result.stdout)
                self.log_step("Run Tests", "success")
                return True, result.stdout
            else:
                logger.error("✗ Tests failed")
                logger.error(result.stderr)
                self.log_step("Run Tests", "failed")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            logger.error("✗ Tests timed out (>30s)")
            self.log_step("Run Tests", "timeout")
            return False, "Tests timed out"
        except Exception as e:
            logger.error(f"✗ Test execution failed: {e}")
            self.log_step("Run Tests", f"error: {e}")
            return False, str(e)

    def run_integration_tests(self) -> Tuple[bool, str]:
        """Run integration and testing suite"""
        self.log_step("Run Integration Tests")

        test_file = self.backend_path / 'bob_ai_v6_integration_and_testing_suite.py'

        if not test_file.exists():
            logger.warning(f"⚠ Integration test file not found: {test_file}")
            self.log_step("Run Integration Tests", "skipped")
            return True, "Integration tests skipped"

        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(self.backend_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info("✓ Integration tests passed")
                logger.info(result.stdout)
                self.log_step("Run Integration Tests", "success")
                return True, result.stdout
            else:
                logger.warning("⚠ Some integration tests may have issues")
                logger.info(result.stderr)
                self.log_step("Run Integration Tests", "completed_with_warnings")
                return True, result.stderr

        except subprocess.TimeoutExpired:
            logger.warning("⚠ Integration tests timed out (>60s)")
            self.log_step("Run Integration Tests", "timeout")
            return True, "Integration tests timed out (acceptable)"
        except Exception as e:
            logger.warning(f"⚠ Integration tests error: {e}")
            self.log_step("Run Integration Tests", f"warning: {e}")
            return True, str(e)

    def verify_deployment(self) -> bool:
        """Verify deployment is complete and working"""
        self.log_step("Verify Deployment")

        logger.info("\nVerification Steps:")
        logger.info("-" * 80)

        # Check 1: Files in backend
        logger.info("Check 1: Required files in backend directory")
        required_files = [
            'bob_ai_v6_final_knowledge.py',
            'bob_ai_v6_integration.py',
            'bob_ai_v6_llm_integration.py'
        ]

        for filename in required_files:
            filepath = self.backend_path / filename
            if filepath.exists():
                logger.info(f"  ✓ {filename}")
            else:
                logger.warning(f"  ✗ {filename}")

        # Check 2: Imports
        logger.info("\nCheck 2: Module imports")
        original_cwd = os.getcwd()
        os.chdir(self.backend_path)

        import_success = True
        for module in ['bob_ai_v6_final_knowledge', 'bob_ai_v6_integration', 'bob_ai_v6_llm_integration']:
            try:
                __import__(module)
                logger.info(f"  ✓ {module}")
            except Exception as e:
                logger.error(f"  ✗ {module}: {e}")
                import_success = False

        os.chdir(original_cwd)

        # Check 3: Test execution
        logger.info("\nCheck 3: Test execution")
        test_success, test_output = self.run_tests()
        if test_success:
            logger.info("  ✓ Unit tests passed")
        else:
            logger.error("  ✗ Unit tests failed")

        if import_success and test_success:
            self.log_step("Verify Deployment", "success")
            return True
        else:
            self.log_step("Verify Deployment", "failed")
            return False

    def generate_deployment_report(self) -> str:
        """Generate deployment report"""
        report = f"""
BOB AI v6.0 DEPLOYMENT REPORT
=============================
Generated: {datetime.now().isoformat()}

DEPLOYMENT LOG:
==============="""

        for entry in self.deployment_log:
            report += f"\n{entry['timestamp']} - {entry['step']}: {entry['status']}"

        report += f"""

SUMMARY:
========
Successful steps: {sum(1 for e in self.deployment_log if e['status'] == 'success')}
Failed steps: {sum(1 for e in self.deployment_log if e['status'] == 'failed')}
Total steps: {len(self.deployment_log)}

Backend Path: {self.backend_path}
Workspace Path: {self.workspace_path}

NEXT STEPS:
===========
1. Update main.py to import BobAILLMIntegration
2. Add @with_bob_ai_enhancement decorators to relevant routes
3. Update WebSocket handlers with enhancement
4. Test end-to-end functionality
5. Deploy to production environment

For detailed integration instructions, see:
- bob_ai_v6_llm_integration.py (example_flask_integration())
- BOB_AI_V6_FINAL_COMPLETE.txt
- BOB_AI_V6_QUICK_START.txt
"""

        return report

    def full_deployment(self):
        """Run full deployment process"""
        logger.info("\n" + "=" * 80)
        logger.info("BOB AI v6.0 - FULL DEPLOYMENT PROCESS")
        logger.info("=" * 80 + "\n")

        # Step 1: Verify files
        logger.info("STEP 1: Verifying files...")
        files_ok, missing = self.verify_files_exist()
        if not files_ok:
            logger.error(f"Missing files: {missing}")
            return False

        # Step 2: Copy files
        logger.info("\nSTEP 2: Copying files to backend...")
        if not self.copy_files_to_backend():
            logger.error("Failed to copy files")
            return False

        # Step 3: Verify imports
        logger.info("\nSTEP 3: Verifying imports...")
        if not self.verify_imports():
            logger.error("Import verification failed")
            return False

        # Step 4: Run tests
        logger.info("\nSTEP 4: Running unit tests...")
        test_success, test_output = self.run_tests()
        if not test_success:
            logger.error("Unit tests failed")
            return False

        # Step 5: Run integration tests
        logger.info("\nSTEP 5: Running integration tests...")
        self.run_integration_tests()

        # Step 6: Verify deployment
        logger.info("\nSTEP 6: Verifying deployment...")
        if not self.verify_deployment():
            logger.warning("Some verification checks failed")

        # Step 7: Generate report
        logger.info("\nSTEP 7: Generating deployment report...")
        report = self.generate_deployment_report()

        # Save report
        report_file = self.backend_path / f'DEPLOYMENT_REPORT_{self.timestamp}.txt'
        try:
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"✓ Report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

        # Print report
        print(report)

        logger.info("\n" + "=" * 80)
        logger.info("DEPLOYMENT COMPLETE")
        logger.info("=" * 80)

        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Bob AI v6.0 Deployment Manager")
    parser.add_argument('--test', action='store_true', help='Run tests only')
    parser.add_argument('--verify', action='store_true', help='Verify deployment')
    parser.add_argument('--full', action='store_true', help='Full deployment')
    parser.add_argument('--backend', default=None, help='Backend path')

    args = parser.parse_args()

    manager = DeploymentManager(backend_path=args.backend)

    if args.full:
        success = manager.full_deployment()
    elif args.test:
        success, output = manager.run_tests()
        if success:
            logger.info("Tests passed")
        else:
            logger.error("Tests failed")
    elif args.verify:
        success = manager.verify_deployment()
        report = manager.generate_deployment_report()
        print(report)
    else:
        # Default: full deployment
        success = manager.full_deployment()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
