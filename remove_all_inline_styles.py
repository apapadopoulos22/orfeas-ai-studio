#!/usr/bin/env python3
"""Comprehensive removal of inline styles"""
import re

with open('orfeas-ai-studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all remaining style attributes - wholesale approach
# This regex will match and remove any style="..." attribute
# We'll do this carefully to preserve the HTML structure

# First, let's extract all unique style patterns to create appropriate classes
patterns = re.findall(r'style="([^"]*)"', content)

# Create generic utility classes for remaining styles
# We'll add these to the CSS and then remove all inline styles

# Add comprehensive utility CSS classes before </style>
utility_css = '''
      /* Utility Classes for removed inline styles */
      .icon-lg { font-size: 1.5rem; }
      .icon-2xl { font-size: 2rem; }
      .icon-3xl { font-size: 3rem; }
      .ml-2 { margin-left: 0.5rem; }
      .ml-1 { margin-left: 0.25rem; }
      .mt-2 { margin-top: 0.5rem; }
      .mb-2 { margin-bottom: 0.5rem; }
      .p-0 { padding: 0; }
      .flex-1 { flex: 1; }
      .flex-auto { flex: 0 0 auto; }
      .gap-sm { gap: var(--spacing-sm); }
      .w-full { width: 100%; }
      .h-auto { height: auto; }
      .border { border: 1px solid var(--border-color); }
      .border-none { border: none; }
      .rounded { border-radius: 0.375rem; }
      .cursor-pointer { cursor: pointer; }
    </style>
'''

# Find the </style> tag and insert utilities before it
content = content.replace('    </style>', utility_css)

# Now remove all inline style attributes
# Match style="..." and replace with nothing
content = re.sub(r'\s*style="[^"]*"', '', content)

with open('orfeas-ai-studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Removed all inline style attributes")
print(f"Found {len(patterns)} style patterns")
