#!/usr/bin/env python3
"""
HTML Update Script - Automatically replace image references with optimized versions
"""

import re
import os
from pathlib import Path

def update_card_images(html_content, image_name):
    """Replace card image with responsive picture element"""
    base_name = image_name.replace('-hero.png', '').replace('.png', '')

    # Pattern to match card images
    pattern = rf'<img src="[^"]*{re.escape(image_name)}"[^>]*>'

    replacement = f"""<picture class="card-image">
    <source media="(max-width: 768px)" srcset="public/images/optimized/{base_name}-mobile.webp" type="image/webp">
    <source media="(max-width: 768px)" srcset="public/images/optimized/{base_name}-mobile.jpg">
    <source media="(max-width: 1024px)" srcset="public/images/optimized/{base_name}-tablet.webp" type="image/webp">
    <source media="(max-width: 1024px)" srcset="public/images/optimized/{base_name}-tablet.jpg">
    <source srcset="public/images/optimized/{base_name}-desktop.webp" type="image/webp">
    <img src="public/images/optimized/{base_name}-desktop.jpg" alt="{base_name.replace('-', ' ').title()}" loading="lazy" width="600" height="400">
</picture>"""

    return re.sub(pattern, replacement, html_content)

def update_hero_backgrounds(html_content, image_name):
    """Replace hero background images with optimized versions"""
    base_name = image_name.replace('-hero.png', '').replace('.png', '')

    # Pattern to match hero background styles
    pattern = rf"background-image:[^;]*{re.escape(image_name)}[^;]*;"

    replacement = f"background-image: url('../../public/images/optimized/{base_name}-desktop.webp');"

    return re.sub(pattern, replacement, html_content)

def process_html_files():
    """Process all HTML files and update image references"""
    html_files = []

    # Find all HTML files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                html_files.append(Path(root) / file)

    print(f"Found {len(html_files)} HTML files to process")

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Update all image references
            optimized_dir = Path('public/images/optimized')
            if optimized_dir.exists():
                for webp_file in optimized_dir.glob('*-desktop.webp'):
                    base_name = webp_file.stem.replace('-desktop', '')
                    original_name = f"{base_name}.png"
                    hero_name = f"{base_name}-hero.png"

                    # Update card images
                    content = update_card_images(content, original_name)
                    content = update_card_images(content, hero_name)

                    # Update hero backgrounds
                    content = update_hero_backgrounds(content, hero_name)

            # Save if changed
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated: {html_file}")

        except Exception as e:
            print(f"Error processing {html_file}: {e}")

if __name__ == "__main__":
    print("🔄 Updating HTML files with optimized images...")
    process_html_files()
    print("✅ HTML update complete!")
