#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix mojibake and corrupted navigation in orfeas-ai-studio.html"""

import re

def fix_html():
    with open('orfeas-ai-studio.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove corrupted characters
    replacements = [
        ('2D→3D', '2D to 3D'),
        ('↔', ''),
        ('s™ï¸', ''),
        (''', "'"),
        (''', "'"),
        ('â€', ''),
        ('ï»¿', ''),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    # Find and fix the nav section
    nav_start = content.find('<nav class="nav">')
    if nav_start > 0:
        nav_end = content.find('</nav>', nav_start)
        if nav_end > 0:
            new_section = '''<nav class="nav">
      <div class="nav-content">
        <a href="#" class="nav-logo" onclick="showSection('hero')">
          <div class="nav-logo-icon">🎨</div>
          <span>ORFEAS AI Studio</span>
        </a>

        <ul class="nav-links">
          <li><a class="nav-link" onclick="showSection('hero')">Home</a></li>
          <li><a class="nav-link" onclick="showSection('3Dstudio')">3D Studio</a></li>
          <li><a class="nav-link" onclick="showSection('image')">Image Editor</a></li>
          <li><a class="nav-link" onclick="showSection('2.5Dstudio')">2.5D Studio</a></li>
          <li><a class="nav-link" onclick="showSection('replicator')">Replicator</a></li>
          <li><a class="nav-link" onclick="showSection('about')">About</a></li>
        </ul>

        <div class="nav-actions">
          <button class="btn btn-primary" onclick="showSection('3Dstudio')">
            Launch Studio
          </button>
        </div>
      </div>
    </nav>'''

            content = content[:nav_start] + new_section + content[nav_end + 6:]

    with open('orfeas-ai-studio.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print('✓ Mojibake fixed')
    print('✓ Navigation tabs restored')

if __name__ == '__main__':
    fix_html()
