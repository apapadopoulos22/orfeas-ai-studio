#!/usr/bin/env python3
"""Fix Unicode replacement characters in synexa-style-studio.html"""

import sys

# Read as binary, find replacement char positions
with open('synexa-style-studio.html', 'rb') as f:
    data = f.read()

# Replace U+FFFD (ef bf bd in UTF-8) with empty string
replacement_char_bytes = b'\xef\xbf\xbd'
if replacement_char_bytes in data:
    count = data.count(replacement_char_bytes)
    print(f"Found {count} Unicode replacement chars")
    # Fix by removing them
    fixed_data = data.replace(replacement_char_bytes, b'')
    with open('synexa-style-studio.html', 'wb') as f:
        f.write(fixed_data)
    print("Fixed: Removed all Unicode replacement characters")
else:
    print("No replacement chars found")
