#!/usr/bin/env python3
"""
Batch converter: Inline styles to CSS classes for multiple HTML files
Processes: synexa-style-studio.html, orfeas-studio.html, material-studio.html, ORFEAS-Connection-Fix/studio.html
"""

import re
from pathlib import Path
from collections import defaultdict

def extract_style_properties(style_str):
    """Extract CSS properties from inline style attribute."""
    properties = {}
    rules = [r.strip() for r in style_str.split(';') if r.strip()]

    for rule in rules:
        if ':' in rule:
            prop, value = rule.split(':', 1)
            prop = prop.strip()
            value = value.strip()
            properties[prop] = value

    return properties

def generate_class_name_from_style(style_value, idx):
    """Generate a unique class name from inline style."""
    # Create hash of style for uniqueness
    style_hash = abs(hash(style_value)) % 100000
    return f"inline-{style_hash}-{idx}"

def fix_html_file(file_path):
    """Convert all inline styles to CSS classes in an HTML file."""

    print(f"\n{'='*70}")
    print(f"Processing: {file_path.name}")
    print(f"{'='*70}")

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all inline style attributes
    style_pattern = r'style\s*=\s*"([^"]*)"'
    matches = list(re.finditer(style_pattern, content))

    if not matches:
        print(f"✅ No inline styles found")
        return False

    print(f"Found {len(matches)} inline style attributes")

    # Group styles by properties (to reuse classes)
    style_groups = {}
    style_to_class = {}
    css_rules = []

    for idx, match in enumerate(matches):
        style_value = match.group(1)
        properties = extract_style_properties(style_value)

        # Create hash of properties for grouping
        prop_str = str(sorted(properties.items()))

        if prop_str not in style_groups:
            class_name = generate_class_name_from_style(style_value, idx)
            style_groups[prop_str] = class_name

            # Generate CSS rule
            css_block = f".{class_name} {{\n"
            for prop, val in sorted(properties.items()):
                css_block += f"  {prop}: {val};\n"
            css_block += "}\n\n"
            css_rules.append(css_block)

        style_to_class[style_value] = style_groups[prop_str]

    print(f"Generated {len(css_rules)} unique CSS classes")

    # Add CSS to stylesheet (before closing </style> tag)
    style_tag_match = re.search(r'</style>', content)
    if not style_tag_match:
        print("ERROR: No </style> tag found")
        return False

    css_content = "".join(css_rules)
    insert_pos = style_tag_match.start()
    content_with_css = content[:insert_pos] + css_content + content[insert_pos:]

    print(f"CSS inserted before </style> tag")

    # Replace inline styles with classes
    result_content = content_with_css
    replacements = 0

    for idx, match in enumerate(matches):
        style_attr = match.group(0)
        style_value = match.group(1)
        class_name = style_to_class[style_value]

        # Find the element with this style and add class
        # Look for pattern: <tag ... style="value" ... >
        element_start = content_with_css.rfind('<', 0, match.start())
        element_end = content_with_css.find('>', match.start())

        if element_start >= 0 and element_end > 0:
            element = content_with_css[element_start:element_end+1]

            # Check if element already has a class
            class_match = re.search(r'class="([^"]*)"', element)

            if class_match:
                # Merge with existing class
                existing_classes = class_match.group(1)
                new_element = element.replace(
                    f'class="{existing_classes}"',
                    f'class="{existing_classes} {class_name}"'
                )
            else:
                # Add new class
                new_element = element.replace(style_attr, f'class="{class_name}"')

            # Remove style attribute
            new_element = new_element.replace(style_attr, '')

            # Replace in result
            result_content = result_content[:element_start] + new_element + result_content[element_end+1:]
            replacements += 1

    print(f"Replaced {replacements} inline style attributes with classes")

    # Write file back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result_content)

    print(f"✅ File saved successfully")
    return True

def main():
    base_path = Path(r'c:\Users\johng\Documents\oscar')

    files_to_fix = [
        base_path / 'synexa-style-studio.html',
        base_path / 'orfeas-studio.html',
        base_path / 'material-studio.html',
        base_path / 'ORFEAS-Connection-Fix' / 'studio.html',
    ]

    total_fixed = 0
    failed = []

    print("\n" + "="*70)
    print("BATCH INLINE STYLES CONVERTER")
    print("="*70)

    for file_path in files_to_fix:
        if file_path.exists():
            try:
                if fix_html_file(file_path):
                    total_fixed += 1
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                failed.append(str(file_path.name))
        else:
            print(f"⚠️  File not found: {file_path}")
            failed.append(str(file_path.name))

    print("\n" + "="*70)
    print("BATCH PROCESSING COMPLETE")
    print("="*70)
    print(f"Successfully fixed: {total_fixed} files")
    if failed:
        print(f"Failed: {len(failed)} files - {', '.join(failed)}")
    else:
        print("✅ All files processed successfully!")

if __name__ == '__main__':
    main()
