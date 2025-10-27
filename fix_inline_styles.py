#!/usr/bin/env python3
"""
Automated inline styles to CSS classes converter for orfeas-ai-studio.html
Converts all inline style attributes to corresponding CSS classes for webhint compliance.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

def extract_style_properties(style_str: str) -> Dict[str, str]:
    """Extract CSS properties from inline style attribute."""
    properties: Dict[str, str] = {}
    # Split by semicolon, filter empty strings
    rules: List[str] = [r.strip() for r in style_str.split(';') if r.strip()]

    for rule in rules:
        if ':' in rule:
            prop, value = rule.split(':', 1)
            prop = prop.strip()
            value = value.strip()
            properties[prop] = value

    return properties

def properties_to_css(properties: Dict[str, str]) -> str:
    """Convert properties dict to CSS rule block."""
    if not properties:
        return ""

    css_lines: List[str] = []
    for prop, value in properties.items():
        css_lines.append(f"    {prop}: {value};")

    return "\n".join(css_lines)

def generate_class_name(properties: Dict[str, str], index: int) -> str:
    """Generate a unique class name based on properties."""
    # Create a simplified hash-like name from properties
    key_props: List[str] = []
    if 'display' in properties:
        key_props.append(f"d-{properties['display'][:3]}")
    if 'flex' in properties.get('display', ''):
        key_props.append('flex')
    if 'margin-top' in properties:
        mt = properties['margin-top'].replace(' ', '-').replace('.', '_').replace('(', '').replace(')', '')
        key_props.append(f"mt-{mt[:8]}")
    if 'margin-bottom' in properties:
        mb = properties['margin-bottom'].replace(' ', '-').replace('.', '_').replace('(', '').replace(')', '')
        key_props.append(f"mb-{mb[:8]}")
    if 'gap' in properties:
        gap = properties['gap'].replace(' ', '-').replace('.', '_').replace('(', '').replace(')', '')
        key_props.append(f"gap-{gap[:8]}")
    if 'width' in properties:
        w = properties['width'].replace(' ', '').replace('%', 'pct').replace('(', '').replace(')', '')
        key_props.append(f"w-{w[:8]}")
    if 'font-size' in properties:
        fs = properties['font-size'].replace(' ', '-').replace('.', '_').replace('(', '').replace(')', '')[:8]
        key_props.append(f"fs-{fs}")
    if 'color' in properties:
        key_props.append('color')
    if 'background' in properties:
        key_props.append('bg')
    if 'padding' in properties:
        key_props.append('p')
    if 'border' in properties:
        key_props.append('border')
    if 'border-radius' in properties:
        key_props.append('rounded')
    if 'flex' in properties:
        key_props.append('flex')

    if key_props:
        return 'inline-' + '-'.join(key_props)[:40]
    else:
        return f'inline-style-{index}'

def main() -> None:
    """Main function to convert inline styles to CSS classes."""
    html_path: Path = Path(r'c:\Users\johng\Documents\oscar\orfeas-ai-studio.html')

    print("Reading HTML file...")
    with open(html_path, 'r', encoding='utf-8') as f:
        content: str = f.read()

    # Find all inline style attributes
    style_pattern: str = r'style\s*=\s*"([^"]*)"'
    matches: List[Any] = list(re.finditer(style_pattern, content))

    print(f"\nFound {len(matches)} inline style attributes")

    # Group styles to avoid duplicates
    style_groups: Dict[str, Tuple[str, Dict[str, str]]] = {}
    inline_to_class: Dict[str, str] = {}

    for idx, match in enumerate(matches):
        style_value: str = match.group(1)
        properties: Dict[str, str] = extract_style_properties(style_value)

        # Convert properties dict to a hashable string for grouping
        prop_str: str = str(sorted(properties.items()))

        if prop_str not in style_groups:
            class_name: str = generate_class_name(properties, idx)
            style_groups[prop_str] = (class_name, properties)

        inline_to_class[match.group(0)] = style_groups[prop_str][0]

    print(f"Grouped into {len(style_groups)} unique styles")

    # Generate CSS
    print("\nGenerating CSS...")
    css_content = "/* Auto-generated inline style classes */\n"
    for prop_str, (class_name, properties) in style_groups.items():
        css_content += f".{class_name} {{\n"
        css_content += properties_to_css(properties)
        css_content += "\n}\n\n"

    # Find where to insert CSS (before closing </style> tag)
    style_tag_pattern = r'</style>'
    style_matches = list(re.finditer(style_tag_pattern, content))

    if style_matches:
        insert_pos = style_matches[-1].start()
        print(f"Inserting CSS at position {insert_pos}")

        # Insert CSS before closing tag
        content_with_css = content[:insert_pos] + css_content + content[insert_pos:]
    else:
        print("ERROR: Could not find </style> tag")
        return

    # Replace inline styles with classes
    print("\nReplacing inline styles with classes...")
    result_content = content_with_css
    replacements = 0

    for style_attr, class_name in inline_to_class.items():
        new_attr = f'class="{class_name}"'
        # Need to preserve existing class attributes
        result_content = result_content.replace(f'{style_attr}', new_attr, 1)
        replacements += 1

    print(f"Replaced {replacements} inline style attributes")

    # However, we need to handle elements that already have classes
    # Let's do a second pass to merge classes properly
    print("\nMerging with existing classes...")

    # Find all style= attributes with class= nearby
    def merge_style_class(match: Any) -> str:
        """Merge style attribute into class attribute."""
        full_match: str = match.group(0)

        # Extract class and style
        class_match: Any = re.search(r'class="([^"]*)"', full_match)
        style_match: Any = re.search(r'style="([^"]*)"', full_match)

        if not style_match:
            return full_match

        style_value: str = style_match.group(1)
        properties: Dict[str, str] = extract_style_properties(style_value)
        class_name: str = generate_class_name(properties, 0)

        if class_match:
            existing_classes: str = class_match.group(1)
            merged_classes: str = f"{existing_classes} {class_name}"
            result: str = full_match.replace(class_match.group(0), f'class="{merged_classes}"')
            result = result.replace(style_match.group(0), '')
            return result
        else:
            result = full_match.replace(style_match.group(0), f'class="{class_name}"')
            return result

    # Start fresh with original content
    result_content: str = content

    # Generate CSS again (for the second pass)
    style_to_class_map: Dict[str, str] = {}
    css_lines: List[str] = []

    for idx, match in enumerate(matches):
        style_value: str = match.group(1)
        properties: Dict[str, str] = extract_style_properties(style_value)
        prop_str: str = str(sorted(properties.items()))

        if prop_str not in style_to_class_map:
            class_name: str = generate_class_name(properties, idx)
            style_to_class_map[prop_str] = class_name

            css_lines.append(f".{class_name} {{")
            for prop, val in sorted(properties.items()):
                css_lines.append(f"  {prop}: {val};")
            css_lines.append("}")
            css_lines.append("")

    css_content = "\n".join(css_lines)

    # Insert CSS before closing </style>
    style_tag_match = re.search(r'</style>', result_content)
    if style_tag_match:
        insert_pos = style_tag_match.start()
        result_content = result_content[:insert_pos] + css_content + result_content[insert_pos:]

    # Now replace all style attributes
    for idx, match in enumerate(matches):
        style_attr = match.group(0)
        style_value = match.group(1)
        properties: Dict[str, str] = extract_style_properties(style_value)
        prop_str: str = str(sorted(properties.items()))
        class_name: str = style_to_class_map[prop_str]

        # Find this exact style attribute and replace it
        # First, handle the element containing this style
        # Look for the surrounding tag
        element_pattern: str = r'<[^>]*' + re.escape(style_attr) + r'[^>]*>'

        def replace_element(elem_match: Any) -> str:
            elem: str = elem_match.group(0)
            # Extract existing class
            class_match: Any = re.search(r'class="([^"]*)"', elem)
            if class_match:
                existing_classes: str = class_match.group(1)
                new_classes: str = f"{existing_classes} {class_name}"
                elem = elem.replace(class_match.group(0), f'class="{new_classes}"')
            else:
                elem = elem.replace(style_attr, f'class="{class_name}"')

            # Remove the style attribute
            elem = elem.replace(style_attr, '')
            return elem

        result_content = re.sub(element_pattern, replace_element, result_content, count=1)

    # Save the result
    print(f"\nWriting updated HTML...")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(result_content)

    print(f"✅ Fixed {len(matches)} inline style violations")
    print(f"✅ Generated {len(style_to_class_map)} CSS classes")
    print(f"✅ File saved successfully")

if __name__ == '__main__':
    main()
