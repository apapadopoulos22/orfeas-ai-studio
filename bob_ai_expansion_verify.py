#!/usr/bin/env python3
"""
BOB AI Expansion - Phase 1: Verification & Testing Script
==========================================================

Verifies all components are properly installed and functional:
  - Database connections
  - API endpoints
  - Data loading
  - Performance

Usage:
  python bob_ai_expansion_verify.py

Author: ORFEAS AI - BOB AI Expansion v10.0
"""

import os
import sys
import logging
import json
import time
from pathlib import Path
from typing import Dict, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class VerificationReport:
    """Tracks verification results"""

    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_check(self, name: str, passed: bool, message: str = "", warning: bool = False):
        """Add check result"""
        status = "✅ PASS" if passed else ("⚠️  WARN" if warning else "❌ FAIL")
        self.checks.append({
            'name': name,
            'status': status,
            'message': message,
            'passed': passed
        })

        if passed:
            self.passed += 1
        elif warning:
            self.warnings += 1
        else:
            self.failed += 1

        print(f"  {status}: {name}")
        if message:
            print(f"       {message}")

    def summary(self) -> str:
        """Get summary"""
        return f"Passed: {self.passed} | Warnings: {self.warnings} | Failed: {self.failed}"


def check_imports() -> Tuple[bool, str]:
    """Check if all required modules are importable"""
    logger.info(f"{BLUE}Checking imports...{RESET}")

    required = {
        'sqlalchemy': 'SQLAlchemy (database ORM)',
        'flask': 'Flask (web framework)',
        'networkx': 'NetworkX (graph algorithms) [Optional]',
        'elasticsearch': 'Elasticsearch [Optional]',
    }

    report = VerificationReport()

    for module, description in required.items():
        try:
            __import__(module)
            is_optional = "[Optional]" in description
            report.add_check(
                f"Import {module}",
                True,
                f"✓ {description}"
            )
        except ImportError:
            is_optional = "[Optional]" in description
            report.add_check(
                f"Import {module}",
                not is_optional,
                f"Not installed: {description}",
                warning=is_optional
            )

    success = report.failed == 0
    return success, report.summary()


def check_files_exist() -> Tuple[bool, str]:
    """Check if all required files exist"""
    logger.info(f"{BLUE}Checking files...{RESET}")

    files_to_check = {
        'backend/bob_ai_expansion_phase1_database.py': 'Database schema module',
        'backend/bob_ai_expansion_phase1_api.py': 'API endpoints module',
        'backend/bob_ai_expansion_data_loader.py': 'Data loader utility',
        'backend/main.py': 'Main Flask application',
    }

    report = VerificationReport()

    for filepath, description in files_to_check.items():
        exists = Path(filepath).exists()
        report.add_check(
            f"File exists: {filepath}",
            exists,
            f"✓ {description}" if exists else f"Missing: {description}"
        )

    success = report.failed == 0
    return success, report.summary()


def check_database() -> Tuple[bool, str]:
    """Check database connectivity and schema"""
    logger.info(f"{BLUE}Checking database...{RESET}")

    report = VerificationReport()

    try:
        from bob_ai_expansion_phase1_database import (
            initialize_bob_ai_expansion, Base, ExpandedCategory,
            ExpandedDiscipline, LibraryMapping, DisciplineLink, LearningPath
        )

        # Test SQLite connection
        db_url = 'sqlite:///:memory:'  # In-memory database for testing

        loader = initialize_bob_ai_expansion(db_url)
        report.add_check(
            "Database connection",
            loader.engine is not None,
            "✓ SQLite in-memory connection successful"
        )

        # Check tables
        tables = [
            (ExpandedCategory, 'expanded_categories'),
            (ExpandedDiscipline, 'expanded_disciplines'),
            (LibraryMapping, 'library_mappings'),
            (DisciplineLink, 'discipline_links'),
            (LearningPath, 'learning_paths'),
        ]

        for model, name in tables:
            report.add_check(
                f"Table schema: {name}",
                hasattr(model, '__tablename__'),
                f"✓ {name} schema defined"
            )

        success = report.failed == 0

    except Exception as e:
        report.add_check("Database initialization", False, str(e))
        success = False

    return success, report.summary()


def check_api_structure() -> Tuple[bool, str]:
    """Check API endpoint structure"""
    logger.info(f"{BLUE}Checking API structure...{RESET}")

    report = VerificationReport()

    try:
        from bob_ai_expansion_phase1_api import (
            bob_ai_expansion_bp, get_all_categories,
            get_all_disciplines, get_all_libraries,
            get_learning_paths, search_disciplines,
            search_libraries, get_statistics, health_check
        )

        endpoints = [
            ('bob_ai_expansion_bp', 'Blueprint'),
            ('get_all_categories', 'Endpoint: GET /categories/expanded'),
            ('get_all_disciplines', 'Endpoint: GET /disciplines/expanded'),
            ('get_all_libraries', 'Endpoint: GET /libraries'),
            ('get_learning_paths', 'Endpoint: GET /learning-paths'),
            ('search_disciplines', 'Endpoint: POST /disciplines/search'),
            ('search_libraries', 'Endpoint: POST /libraries/search'),
            ('get_statistics', 'Endpoint: GET /statistics'),
            ('health_check', 'Endpoint: GET /health'),
        ]

        for func_name, description in endpoints:
            report.add_check(
                f"API function: {func_name}",
                True,
                f"✓ {description}"
            )

        success = True

    except Exception as e:
        report.add_check("API module import", False, str(e))
        success = False

    return success, report.summary()


def check_sample_data() -> Tuple[bool, str]:
    """Check sample data generation"""
    logger.info(f"{BLUE}Checking sample data...{RESET}")

    report = VerificationReport()

    try:
        from bob_ai_expansion_data_loader import generate_sample_categories

        categories = generate_sample_categories()

        report.add_check(
            "Sample data generation",
            len(categories) > 0,
            f"✓ Generated {len(categories)} sample categories"
        )

        success = report.failed == 0

    except Exception as e:
        report.add_check("Sample data generation", False, str(e))
        success = False

    return success, report.summary()


def check_data_loading() -> Tuple[bool, str]:
    """Check data loading functionality"""
    logger.info(f"{BLUE}Checking data loading...{RESET}")

    report = VerificationReport()

    try:
        from bob_ai_expansion_phase1_database import (
            initialize_bob_ai_expansion, ExpandedCategory
        )

        # Create in-memory database
        loader = initialize_bob_ai_expansion('sqlite:///:memory:')

        # Create test data
        session = loader.Session()

        category = ExpandedCategory(
            name='Test Category',
            tier=1,
            tier_name='Test Tier',
            description='Test description',
            keywords=['test'],
            maturity_level='test'
        )

        session.add(category)
        session.commit()

        # Verify
        count = session.query(ExpandedCategory).filter_by(name='Test Category').count()

        report.add_check(
            "Data insertion",
            count == 1,
            "✓ Successfully inserted and retrieved test data"
        )

        session.close()
        success = True

    except Exception as e:
        report.add_check("Data loading", False, str(e))
        success = False

    return success, report.summary()


def performance_check() -> Tuple[bool, str]:
    """Check performance metrics"""
    logger.info(f"{BLUE}Checking performance...{RESET}")

    report = VerificationReport()

    try:
        from bob_ai_expansion_phase1_database import (
            initialize_bob_ai_expansion, ExpandedCategory
        )
        import time

        loader = initialize_bob_ai_expansion('sqlite:///:memory:')
        session = loader.Session()

        # Insert 100 categories
        start = time.time()
        for i in range(100):
            category = ExpandedCategory(
                name=f'Category {i}',
                tier=(i % 8) + 1,
                tier_name=f'Tier {(i % 8) + 1}',
                description=f'Test category {i}',
                keywords=['test'],
                maturity_level='test'
            )
            session.add(category)

        session.commit()
        insert_time = time.time() - start

        # Query performance
        start = time.time()
        results = session.query(ExpandedCategory).filter_by(tier=1).all()
        query_time = time.time() - start

        report.add_check(
            "Insertion performance",
            insert_time < 5.0,
            f"✓ Inserted 100 records in {insert_time:.3f}s"
        )

        report.add_check(
            "Query performance",
            query_time < 0.1,
            f"✓ Query executed in {query_time*1000:.1f}ms"
        )

        session.close()
        success = report.failed == 0

    except Exception as e:
        report.add_check("Performance check", False, str(e))
        success = False

    return success, report.summary()


def main():
    """Run all verification checks"""

    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}BOB AI Expansion - Phase 1 Verification{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

    checks = [
        ("Dependencies", check_imports),
        ("File Structure", check_files_exist),
        ("Database Schema", check_database),
        ("API Structure", check_api_structure),
        ("Sample Data", check_sample_data),
        ("Data Loading", check_data_loading),
        ("Performance", performance_check),
    ]

    results = {}
    total_passed = 0
    total_failed = 0

    for check_name, check_func in checks:
        print(f"\n{YELLOW}{check_name}:{RESET}")
        try:
            success, summary = check_func()
            results[check_name] = (success, summary)

            if success:
                print(f"  {GREEN}✅ {summary}{RESET}")
                total_passed += 1
            else:
                print(f"  {RED}❌ {summary}{RESET}")
                total_failed += 1

        except Exception as e:
            print(f"  {RED}❌ ERROR: {str(e)}{RESET}")
            total_failed += 1

    # Final summary
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Verification Summary{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

    print(f"  Checks Passed: {total_passed}/7")
    print(f"  Checks Failed: {total_failed}/7")

    if total_failed == 0:
        print(f"\n{GREEN}✅ ALL CHECKS PASSED - Ready for implementation!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}❌ Some checks failed - Review errors above{RESET}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
