#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOB AI Mega Expansion - Integration & Deployment Script
========================================================

This script integrates the 5000-discipline knowledge base with ORFEAS AI
and demonstrates usage patterns.

Usage:
    python integrate_mega_expansion.py
    python integrate_mega_expansion.py --export json
    python integrate_mega_expansion.py --export csv
    python integrate_mega_expansion.py --stats
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Import the mega library database
try:
    from bob_ai_mega_library_database_5000 import (
        DISCIPLINE_LIBRARY_MAP,
        get_discipline_libraries,
        get_all_python_packages,
        get_all_tools,
        get_all_resources,
        export_to_json,
        get_statistics,
    )
    print("[OK] Successfully imported bob_ai_mega_library_database_5000")
except ImportError as e:
    print(f"[ERROR] Error importing mega library: {e}")
    sys.exit(1)

# ============================================================================
# INTEGRATION FUNCTIONS
# ============================================================================

class MegaExpansionIntegration:
    """Integrates mega expansion with ORFEAS AI"""

    @staticmethod
    def display_statistics():
        """Display expansion statistics"""
        stats = get_statistics()

        print("\n" + "="*80)
        print("BOB AI MEGA EXPANSION - STATISTICS")
        print("="*80)
        print(f"\n📊 Knowledge Base Size:")
        print(f"   • Total Disciplines: {stats['total_disciplines']}")
        print(f"   • Python Packages: {stats['unique_python_packages']}")
        print(f"   • CLI Tools: {stats['unique_cli_tools']}")
        print(f"   • Learning Resources: {stats['unique_resources']}")

        print(f"\n📦 Top Python Packages:")
        for i, pkg in enumerate(sorted(stats['python_packages'])[:20], 1):
            print(f"   {i:2d}. {pkg}")

        print(f"\n🛠️  Top CLI Tools:")
        for i, tool in enumerate(sorted(stats['cli_tools'])[:15], 1):
            print(f"   {i:2d}. {tool}")

    @staticmethod
    def display_discipline_sample(discipline_name: str):
        """Display sample discipline information"""
        libraries = get_discipline_libraries(discipline_name)

        print("\n" + "="*80)
        print(f"DISCIPLINE: {discipline_name}")
        print("="*80)
        print(f"\n📚 Python Packages:")
        for pkg in libraries.get('packages', []):
            print(f"   • {pkg}")

        print(f"\n🛠️  Tools & CLI:")
        for tool in libraries.get('tools', []):
            print(f"   • {tool}")

        print(f"\n📖 Resources:")
        for resource in libraries.get('resources', []):
            print(f"   • {resource}")

    @staticmethod
    def generate_requirements_file(output_path: str = "requirements_expanded.txt"):
        """Generate pip requirements file with all packages"""
        packages = get_all_python_packages()

        with open(output_path, 'w') as f:
            f.write("# BOB AI Mega Expansion - Complete Requirements\n")
            f.write("# Generated from 5000+ discipline library mappings\n\n")

            for pkg in sorted(packages):
                f.write(f"{pkg}\n")

        print(f"✅ Generated requirements file: {output_path}")
        print(f"   Total packages: {len(packages)}")

    @staticmethod
    def export_knowledge_base(format: str = 'json', output_path: str = None):
        """Export knowledge base in various formats"""
        if format == 'json':
            if output_path is None:
                output_path = 'bob_ai_knowledge_base.json'

            data = export_to_json()
            with open(output_path, 'w') as f:
                f.write(data)

            print(f"✅ Exported to JSON: {output_path}")

        elif format == 'csv':
            if output_path is None:
                output_path = 'bob_ai_knowledge_base.csv'

            import csv
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Discipline', 'Packages', 'Tools', 'Resources'])

                for discipline, data in sorted(DISCIPLINE_LIBRARY_MAP.items()):
                    packages = ';'.join(data.get('packages', []))
                    tools = ';'.join(data.get('tools', []))
                    resources = ';'.join(data.get('resources', []))
                    writer.writerow([discipline, packages, tools, resources])

            print(f"✅ Exported to CSV: {output_path}")

        elif format == 'markdown':
            if output_path is None:
                output_path = 'BOB_AI_KNOWLEDGE_BASE.md'

            with open(output_path, 'w') as f:
                f.write("# BOB AI Mega Expansion Knowledge Base\n\n")
                f.write(f"Total Disciplines: {len(DISCIPLINE_LIBRARY_MAP)}\n\n")

                for discipline, data in sorted(DISCIPLINE_LIBRARY_MAP.items()):
                    f.write(f"## {discipline}\n\n")

                    f.write("### Python Packages\n")
                    for pkg in data.get('packages', []):
                        f.write(f"- {pkg}\n")
                    f.write("\n")

                    f.write("### Tools\n")
                    for tool in data.get('tools', []):
                        f.write(f"- {tool}\n")
                    f.write("\n")

                    f.write("### Resources\n")
                    for resource in data.get('resources', []):
                        f.write(f"- {resource}\n")
                    f.write("\n")

            print(f"✅ Exported to Markdown: {output_path}")

    @staticmethod
    def create_learning_path(start_discipline: str, hours_available: int = 100):
        """Generate learning path with library recommendations"""
        print(f"\n📚 Learning Path: {start_discipline} ({hours_available} hours)")
        print("="*80)

        libraries = get_discipline_libraries(start_discipline)
        estimated_hours = 15  # Default

        print(f"\nCore Discipline: {start_discipline}")
        print(f"Estimated Hours: {estimated_hours}")
        print(f"\nRequired Libraries:")
        for pkg in libraries.get('packages', []):
            print(f"  pip install {pkg}")

        print(f"\nSetup Commands:")
        print(f"  # Install all dependencies")
        print(f"  pip install {' '.join(libraries.get('packages', []))}")
        print(f"\nTools to Learn:")
        for tool in libraries.get('tools', []):
            print(f"  • {tool}")

        print(f"\nLearning Resources:")
        for resource in libraries.get('resources', []):
            print(f"  • {resource}")

    @staticmethod
    def compare_disciplines(disciplines: List[str]):
        """Compare libraries across multiple disciplines"""
        print(f"\n🔄 Comparing Disciplines: {', '.join(disciplines)}")
        print("="*80)

        all_packages = set()
        discipline_packages = {}

        for disc in disciplines:
            libs = get_discipline_libraries(disc)
            packages = set(libs.get('packages', []))
            discipline_packages[disc] = packages
            all_packages.update(packages)

        print(f"\nCommon Packages (Used by all):")
        common = set.intersection(*discipline_packages.values()) if discipline_packages else set()
        if common:
            for pkg in sorted(common):
                print(f"  • {pkg}")
        else:
            print("  (No common packages)")

        print(f"\nUnique Packages:")
        for disc in disciplines:
            unique = discipline_packages[disc] - common
            if unique:
                print(f"\n  {disc}:")
                for pkg in sorted(unique):
                    print(f"    • {pkg}")

    @staticmethod
    def generate_deployment_script():
        """Generate deployment script"""
        script = """#!/bin/bash
# BOB AI Mega Expansion - Deployment Script

echo "🚀 Deploying BOB AI Mega Expansion..."

# Install all Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
"""

        packages = get_all_python_packages()
        script += f"pip install {' '.join(sorted(packages))}\n"

        script += """
echo "✅ Python packages installed"

# Create integration test
echo "🧪 Running integration tests..."
python -c "from bob_ai_mega_library_database_5000 import get_statistics; print(get_statistics())"

echo "✅ Deployment complete!"
"""

        with open('deploy_mega_expansion.sh', 'w') as f:
            f.write(script)

        print("✅ Generated deployment script: deploy_mega_expansion.sh")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main integration function"""
    parser = argparse.ArgumentParser(
        description='BOB AI Mega Expansion - Integration & Deployment'
    )

    parser.add_argument('--stats', action='store_true', help='Display statistics')
    parser.add_argument('--discipline', type=str, help='Display discipline information')
    parser.add_argument('--export', type=str, choices=['json', 'csv', 'markdown'],
                       help='Export knowledge base')
    parser.add_argument('--requirements', action='store_true',
                       help='Generate requirements.txt')
    parser.add_argument('--learning-path', type=str, help='Generate learning path')
    parser.add_argument('--compare', nargs='+', help='Compare disciplines')
    parser.add_argument('--deploy-script', action='store_true',
                       help='Generate deployment script')

    args = parser.parse_args()

    if args.stats:
        MegaExpansionIntegration.display_statistics()

    elif args.discipline:
        MegaExpansionIntegration.display_discipline_sample(args.discipline)

    elif args.export:
        MegaExpansionIntegration.export_knowledge_base(args.export)

    elif args.requirements:
        MegaExpansionIntegration.generate_requirements_file()

    elif args.learning_path:
        MegaExpansionIntegration.create_learning_path(args.learning_path)

    elif args.compare:
        MegaExpansionIntegration.compare_disciplines(args.compare)

    elif args.deploy_script:
        MegaExpansionIntegration.generate_deployment_script()

    else:
        print("\n" + "="*80)
        print("BOB AI MEGA EXPANSION - INTEGRATION TOOL")
        print("="*80)
        print("\nUsage Examples:")
        print("  python integrate_mega_expansion.py --stats")
        print("  python integrate_mega_expansion.py --discipline 'Linear Regression'")
        print("  python integrate_mega_expansion.py --export json")
        print("  python integrate_mega_expansion.py --requirements")
        print("  python integrate_mega_expansion.py --learning-path 'Machine Learning'")
        print("  python integrate_mega_expansion.py --compare 'TensorFlow' 'PyTorch'")
        print("  python integrate_mega_expansion.py --deploy-script")
        print("\nFor help:")
        print("  python integrate_mega_expansion.py --help")

if __name__ == '__main__':
    main()
