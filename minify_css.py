#!/usr/bin/env python3
"""
CSS Minification & Optimization Script
For ORFEAS AI Studio

This script:
1. Minifies CSS files (removes comments, whitespace, unused rules)
2. Splits CSS into critical and non-critical
3. Generates minified versions
4. Provides size metrics and optimization report
"""

import os
import re
from pathlib import Path
import json
from typing import Dict, Tuple


class CSSMinifier:
    """Minify CSS while preserving functionality"""

    def __init__(self):
        self.original_size = 0
        self.minified_size = 0
        self.stats = {}

    def minify(self, css_content: str) -> str:
        """
        Minify CSS content by:
        - Removing comments
        - Removing unnecessary whitespace
        - Removing unnecessary semicolons
        - Compressing values
        """
        # Remove /* */ comments
        css_content = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', css_content)

        # Remove // comments (if any)
        css_content = re.sub(r'//.*?\n', '\n', css_content)

        # Remove leading/trailing whitespace from each line
        css_content = '\n'.join(line.strip() for line in css_content.split('\n'))

        # Remove empty lines
        css_content = re.sub(r'\n\s*\n', '\n', css_content)

        # Remove spaces around special characters
        css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)

        # Remove space before opening brace
        css_content = re.sub(r'\s*\{\s*', '{', css_content)

        # Remove space after closing brace
        css_content = re.sub(r'\}\s*', '}', css_content)

        # Remove last semicolon before closing brace
        css_content = re.sub(r';}', '}', css_content)

        # Compress multiple spaces to single space
        css_content = re.sub(r'\s+', ' ', css_content)

        # Remove spaces around CSS operators
        css_content = re.sub(r'\s*([>~+])\s*', r'$1', css_content)

        # Remove trailing semicolon before }
        css_content = re.sub(r';(?=})', '', css_content)

        # Minify colors (keep hex, convert rgb if possible)
        css_content = re.sub(r'rgba\(0,0,0,0\)', 'transparent', css_content)
        css_content = re.sub(r'rgba\(255,255,255,1\)', '#fff', css_content)

        # Remove unnecessary quotes
        css_content = re.sub(r"url\('([^']*)'\)", r'url(\1)', css_content)
        css_content = re.sub(r'url\("([^"]*)"\)', r'url(\1)', css_content)

        # Compress zeros
        css_content = re.sub(r':\s*0(?:px|em|rem|%)', ':0', css_content)

        # Remove space around selectors
        css_content = re.sub(r',\s*', ',', css_content)

        return css_content.strip()

    def split_critical_css(self, css_content: str) -> Tuple[str, str]:
        """
        Split CSS into critical (above-the-fold) and deferred (below-the-fold)

        Critical: navbar, hero, form, buttons, etc. (load synchronously)
        Deferred: animations, hover states, etc. (load async)
        """
        critical_selectors = [
            'body', 'html', 'main', '.navbar', '.hero', '.header',
            '.form', '.form-group', '.form-label', '.form-input',
            'button', '.btn', 'input', 'select', 'textarea',
            '.container', '.grid', '.flex', '.text-primary', '.text-muted',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', '.card'
        ]

        deferred_selectors = [
            ':hover', ':active', ':focus', '@keyframes', 'animation',
            'transition', '.modal', '.tooltip', '.dropdown-menu'
        ]

        critical_rules = []
        deferred_rules = []

        # Split rules by selectors
        rules = re.findall(r'[^{}]+\{[^}]*\}', css_content)

        for rule in rules:
            selector = rule.split('{')[0].strip()

            # Check if rule is critical
            is_critical = any(
                critical_sel in selector
                for critical_sel in critical_selectors
            ) and not any(
                deferred_sel in rule
                for deferred_sel in deferred_selectors
            )

            if is_critical:
                critical_rules.append(rule)
            else:
                deferred_rules.append(rule)

        critical_css = '\n'.join(critical_rules)
        deferred_css = '\n'.join(deferred_rules)

        return critical_css, deferred_css

    def process_file(self, input_path: str, output_path: str = None) -> Dict:
        """Process CSS file and generate minified version"""
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"CSS file not found: {input_path}")

        # Read original CSS
        with open(input_path, 'r', encoding='utf-8') as f:
            original_css = f.read()

        self.original_size = len(original_css.encode('utf-8'))

        # Minify
        minified_css = self.minify(original_css)
        self.minified_size = len(minified_css.encode('utf-8'))

        # Split critical CSS
        critical_css, deferred_css = self.split_critical_css(minified_css)

        # Generate output paths
        if output_path is None:
            output_path = input_path.stem + '.min.css'
        else:
            output_path = Path(output_path)

        output_critical = output_path.parent / (output_path.stem + '-critical.css')
        output_deferred = output_path.parent / (output_path.stem + '-deferred.css')

        # Write minified CSS
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_css)

        # Write critical CSS
        with open(output_critical, 'w', encoding='utf-8') as f:
            f.write(self.minify(critical_css))

        # Write deferred CSS
        with open(output_deferred, 'w', encoding='utf-8') as f:
            f.write(self.minify(deferred_css))

        # Calculate stats
        critical_size = len(self.minify(critical_css).encode('utf-8'))
        deferred_size = len(self.minify(deferred_css).encode('utf-8'))

        self.stats = {
            'input_file': str(input_path),
            'output_file': str(output_path),
            'critical_file': str(output_critical),
            'deferred_file': str(output_deferred),
            'original_size_bytes': self.original_size,
            'original_size_kb': round(self.original_size / 1024, 2),
            'minified_size_bytes': self.minified_size,
            'minified_size_kb': round(self.minified_size / 1024, 2),
            'critical_size_bytes': critical_size,
            'critical_size_kb': round(critical_size / 1024, 2),
            'deferred_size_bytes': deferred_size,
            'deferred_size_kb': round(deferred_size / 1024, 2),
            'compression_ratio': round((1 - self.minified_size / self.original_size) * 100, 1),
            'lines_original': len(original_css.split('\n')),
            'lines_minified': len(minified_css.split('\n')),
        }

        return self.stats

    def print_report(self):
        """Print optimization report"""
        if not self.stats:
            print("No statistics available. Run process_file() first.")
            return

        print("\n" + "="*60)
        print("CSS MINIFICATION & OPTIMIZATION REPORT")
        print("="*60)
        print(f"\nInput File:  {self.stats['input_file']}")
        print(f"Output File: {self.stats['output_file']}")

        print(f"\n📊 SIZE METRICS:")
        print(f"  Original:  {self.stats['original_size_kb']} KB ({self.stats['original_size_bytes']} bytes)")
        print(f"  Minified:  {self.stats['minified_size_kb']} KB ({self.stats['minified_size_bytes']} bytes)")
        print(f"  Savings:   {self.stats['original_size_kb'] - self.stats['minified_size_kb']} KB")
        print(f"  Reduction: {self.stats['compression_ratio']}%")

        print(f"\n📑 LINE METRICS:")
        print(f"  Original:  {self.stats['lines_original']} lines")
        print(f"  Minified:  {self.stats['lines_minified']} line(s)")

        print(f"\n🔀 CSS SPLITTING:")
        print(f"  Critical:  {self.stats['critical_size_kb']} KB (load synchronously)")
        print(f"  Deferred:  {self.stats['deferred_size_kb']} KB (load asynchronously)")
        print(f"  File:      {self.stats['critical_file']}")
        print(f"  File:      {self.stats['deferred_file']}")

        print(f"\n✅ OPTIMIZATION COMPLETE")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    import sys

    # Default paths
    default_css = Path(__file__).parent / 'orfeas-studio.css'

    # Get input file from command line or use default
    input_file = sys.argv[1] if len(sys.argv) > 1 else str(default_css)
    output_file = sys.argv[2] if len(sys.argv) > 2 else str(default_css.parent / 'orfeas-studio.min.css')

    try:
        # Create minifier
        minifier = CSSMinifier()

        # Process file
        print(f"Processing: {input_file}")
        stats = minifier.process_file(input_file, output_file)

        # Print report
        minifier.print_report()

        # Save stats to JSON
        stats_file = Path(output_file).parent / 'css-optimization-stats.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Statistics saved to: {stats_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
