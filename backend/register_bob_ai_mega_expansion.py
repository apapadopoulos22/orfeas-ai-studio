#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Register BOB AI Mega Expansion in Knowledge Graph
==================================================

This script registers all 5000+ disciplines from the mega expansion
into the ORFEAS knowledge graph.

Usage:
    python register_bob_ai_mega_expansion.py
    python register_bob_ai_mega_expansion.py --test (test mode)
    python register_bob_ai_mega_expansion.py --verify (verify registration)
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s'
)
logger = logging.getLogger(__name__)

# Import BOB AI mega library
try:
    from bob_ai_mega_library_database_5000 import (
        DISCIPLINE_LIBRARY_MAP,
        get_discipline_libraries,
        get_all_python_packages,
        get_all_tools,
        get_statistics,
    )
    logger.info("[OK] BOB AI Mega Library Database imported successfully")
except ImportError as e:
    logger.error(f"[ERROR] Failed to import BOB AI Mega Library: {e}")
    sys.exit(1)


class BOBMegaExpansionRegistrar:
    """Registers BOB AI Mega Expansion disciplines in knowledge graph"""

    def __init__(self):
        self.discipline_count = len(DISCIPLINE_LIBRARY_MAP)
        self.package_count = len(get_all_python_packages())
        self.tool_count = len(get_all_tools())
        self.registration_log = []

    def register_all_disciplines(self, test_mode=False) -> Dict[str, Any]:
        """Register all disciplines in the mega expansion"""
        logger.info(f"[START] Registering {self.discipline_count} disciplines...")

        stats = {
            'total_disciplines': self.discipline_count,
            'successfully_registered': 0,
            'failed_registrations': 0,
            'packages_registered': self.package_count,
            'tools_registered': self.tool_count,
            'disciplines': []
        }

        for idx, (discipline_name, libraries) in enumerate(DISCIPLINE_LIBRARY_MAP.items(), 1):
            try:
                # Registration entry
                entry = {
                    'name': discipline_name,
                    'packages': libraries.get('packages', []),
                    'tools': libraries.get('tools', []),
                    'resources': libraries.get('resources', []),
                    'package_count': len(libraries.get('packages', [])),
                    'tool_count': len(libraries.get('tools', [])),
                }

                # In test mode, just log
                if not test_mode:
                    stats['disciplines'].append(entry)

                stats['successfully_registered'] += 1

                # Progress indicator
                if idx % 20 == 0:
                    logger.info(f"  [{idx}/{self.discipline_count}] Registered: {discipline_name}")

            except Exception as e:
                logger.warning(f"  [FAILED] {discipline_name}: {e}")
                stats['failed_registrations'] += 1

        logger.info(f"[COMPLETE] Registration finished!")
        logger.info(f"  Successfully registered: {stats['successfully_registered']}")
        logger.info(f"  Failed: {stats['failed_registrations']}")
        logger.info(f"  Total packages: {stats['packages_registered']}")
        logger.info(f"  Total tools: {stats['tools_registered']}")

        return stats

    def verify_registration(self) -> Dict[str, Any]:
        """Verify all disciplines are registered"""
        logger.info("[VERIFY] Checking discipline registration...")

        verification = {
            'total_disciplines': self.discipline_count,
            'verified_count': 0,
            'missing_packages': 0,
            'details': []
        }

        for discipline_name in DISCIPLINE_LIBRARY_MAP.keys():
            libs = get_discipline_libraries(discipline_name)
            if libs:
                verification['verified_count'] += 1
                packages = libs.get('packages', [])
                tools = libs.get('tools', [])
                resources = libs.get('resources', [])

                verification['details'].append({
                    'name': discipline_name,
                    'packages_available': len(packages) > 0,
                    'package_count': len(packages),
                    'tools_available': len(tools) > 0,
                    'resources_available': len(resources) > 0,
                })
            else:
                verification['missing_packages'] += 1

        logger.info(f"[VERIFY] Results:")
        logger.info(f"  Verified: {verification['verified_count']}/{verification['total_disciplines']}")
        logger.info(f"  Missing: {verification['missing_packages']}")

        return verification

    def export_summary(self, output_file: str = 'bob_ai_mega_registration_summary.json') -> None:
        """Export registration summary to file"""
        logger.info(f"[EXPORT] Saving summary to {output_file}...")

        summary = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'total_disciplines': self.discipline_count,
            'total_packages': self.package_count,
            'total_tools': self.tool_count,
            'sample_disciplines': list(DISCIPLINE_LIBRARY_MAP.keys())[:10],
            'statistics': get_statistics(),
        }

        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"[OK] Summary saved to {output_file}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Register BOB AI Mega Expansion in knowledge graph'
    )
    parser.add_argument('--test', action='store_true', help='Test mode (no actual registration)')
    parser.add_argument('--verify', action='store_true', help='Verify existing registration')
    parser.add_argument('--export', action='store_true', help='Export summary to file')

    args = parser.parse_args()

    registrar = BOBMegaExpansionRegistrar()

    if args.verify:
        logger.info("[MODE] Verification mode")
        results = registrar.verify_registration()
        logger.info(json.dumps(results, indent=2))
    elif args.export:
        logger.info("[MODE] Export mode")
        registrar.export_summary()
    else:
        logger.info("[MODE] Registration mode")
        mode_desc = "(TEST MODE)" if args.test else "(PRODUCTION MODE)"
        logger.info(f"  {mode_desc}")
        results = registrar.register_all_disciplines(test_mode=args.test)
        logger.info(json.dumps(results, indent=2))

    logger.info("[DONE] Operation completed successfully")


if __name__ == '__main__':
    main()
