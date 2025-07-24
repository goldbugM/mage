#!/usr/bin/env python3
"""
Image Optimization Script for Travel Blog
Converts PNG images to optimized WebP and JPEG formats with multiple sizes
"""

import os
import sys
from PIL import Image, ImageOps
import argparse
from pathlib import Path
import json

class ImageOptimizer:
    def __init__(self, input_dir="public/images", output_dir="public/images/optimized"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Image size configurations
        self.card_sizes = {
            'mobile': (400, 267),
            'tablet': (500, 333),
            'desktop': (600, 400)
        }
        
        self.hero_sizes = {
            'mobile': (800, 450),
            'tablet': (1200, 675),
            'desktop': (1920, 1080)
        }
        
        # Quality settings
        self.webp_quality = 80
        self.jpeg_quality = 85
        
        # Statistics
        self.stats = {
            'processed': 0,
            'original_size': 0,
            'optimized_size': 0,
            'files_created': []
        }

    def is_hero_image(self, filename):
        """Check if image is a hero image based on naming convention"""
        return '-hero.' in filename.lower()

    def resize_and_optimize(self, image_path, is_hero=False):
        """Resize and optimize a single image"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Auto-orient based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Choose size configuration
                sizes = self.hero_sizes if is_hero else self.card_sizes
                
                base_name = image_path.stem
                original_size = image_path.stat().st_size
                self.stats['original_size'] += original_size
                
                print(f"Processing: {image_path.name}")
                print(f"  Original size: {original_size / 1024:.1f} KB")
                
                for size_name, (width, height) in sizes.items():
                    # Calculate new dimensions maintaining aspect ratio
                    img_ratio = img.width / img.height
                    target_ratio = width / height
                    
                    if img_ratio > target_ratio:
                        # Image is wider, fit to width
                        new_width = width
                        new_height = int(width / img_ratio)
                    else:
                        # Image is taller, fit to height
                        new_height = height
                        new_width = int(height * img_ratio)
                    
                    # Resize image
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Create WebP version
                    webp_path = self.output_dir / f"{base_name}-{size_name}.webp"
                    resized_img.save(
                        webp_path,
                        'WebP',
                        quality=self.webp_quality,
                        method=6,  # Best compression
                        optimize=True
                    )
                    
                    # Create JPEG fallback
                    jpeg_path = self.output_dir / f"{base_name}-{size_name}.jpg"
                    resized_img.save(
                        jpeg_path,
                        'JPEG',
                        quality=self.jpeg_quality,
                        optimize=True,
                        progressive=True
                    )
                    
                    # Track file sizes
                    webp_size = webp_path.stat().st_size
                    jpeg_size = jpeg_path.stat().st_size
                    self.stats['optimized_size'] += webp_size + jpeg_size
                    
                    self.stats['files_created'].extend([str(webp_path), str(jpeg_path)])
                    
                    print(f"    {size_name}: WebP {webp_size / 1024:.1f} KB, JPEG {jpeg_size / 1024:.1f} KB")
                
                self.stats['processed'] += 1
                print(f"  ✓ Completed\n")
                
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    def process_all_images(self):
        """Process all PNG images in the input directory"""
        png_files = list(self.input_dir.glob("*.png"))
        
        if not png_files:
            print(f"No PNG files found in {self.input_dir}")
            return
        
        print(f"Found {len(png_files)} PNG files to process\n")
        
        for image_path in png_files:
            # Skip temporary files
            if image_path.name.startswith('~'):
                continue
                
            is_hero = self.is_hero_image(image_path.name)
            self.resize_and_optimize(image_path, is_hero)

    def generate_html_examples(self):
        """Generate HTML examples for responsive images"""
        examples_dir = self.output_dir / "html_examples"
        examples_dir.mkdir(exist_ok=True)

        # Card image example
        card_html = """<!-- Responsive Card Image Example -->
<picture class="card-image">
    <source media="(max-width: 768px)"
            srcset="optimized/image-name-mobile.webp"
            type="image/webp">
    <source media="(max-width: 768px)"
            srcset="optimized/image-name-mobile.jpg">
    <source media="(max-width: 1024px)"
            srcset="optimized/image-name-tablet.webp"
            type="image/webp">
    <source media="(max-width: 1024px)"
            srcset="optimized/image-name-tablet.jpg">
    <source srcset="optimized/image-name-desktop.webp"
            type="image/webp">
    <img src="optimized/image-name-desktop.jpg"
         alt="Description"
         loading="lazy"
         width="600"
         height="400">
</picture>"""

        # Hero image example
        hero_html = """<!-- Responsive Hero Background Example -->
<section class="hero">
    <picture>
        <source media="(max-width: 768px)"
                srcset="optimized/hero-name-mobile.webp"
                type="image/webp">
        <source media="(max-width: 768px)"
                srcset="optimized/hero-name-mobile.jpg">
        <source media="(max-width: 1024px)"
                srcset="optimized/hero-name-tablet.webp"
                type="image/webp">
        <source media="(max-width: 1024px)"
                srcset="optimized/hero-name-tablet.jpg">
        <source srcset="optimized/hero-name-desktop.webp"
                type="image/webp">
        <img src="optimized/hero-name-desktop.jpg"
             alt="Hero Description"
             class="hero-background"
             width="1920"
             height="1080">
    </picture>
    <div class="hero-content">
        <h1>Your Title</h1>
        <p>Your description</p>
    </div>
</section>"""

        with open(examples_dir / "card_image_example.html", 'w', encoding='utf-8') as f:
            f.write(card_html)

        with open(examples_dir / "hero_image_example.html", 'w', encoding='utf-8') as f:
            f.write(hero_html)

        print(f"HTML examples saved to {examples_dir}")

    def generate_replacement_script(self):
        """Generate a script to automatically update HTML files"""
        script_content = '''#!/usr/bin/env python3
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
'''

        script_path = self.output_dir / "update_html.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        print(f"HTML update script saved to {script_path}")

    def print_statistics(self):
        """Print optimization statistics"""
        if self.stats['processed'] == 0:
            print("No images were processed.")
            return
        
        original_mb = self.stats['original_size'] / (1024 * 1024)
        optimized_mb = self.stats['optimized_size'] / (1024 * 1024)
        savings = ((self.stats['original_size'] - self.stats['optimized_size']) / self.stats['original_size']) * 100
        
        print("=" * 60)
        print("OPTIMIZATION STATISTICS")
        print("=" * 60)
        print(f"Images processed: {self.stats['processed']}")
        print(f"Files created: {len(self.stats['files_created'])}")
        print(f"Original total size: {original_mb:.2f} MB")
        print(f"Optimized total size: {optimized_mb:.2f} MB")
        print(f"Space saved: {savings:.1f}%")
        print(f"Output directory: {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Optimize images for web performance')
    parser.add_argument('--input', '-i', default='public/images', 
                       help='Input directory containing PNG images')
    parser.add_argument('--output', '-o', default='public/images/optimized',
                       help='Output directory for optimized images')
    parser.add_argument('--webp-quality', type=int, default=80,
                       help='WebP quality (1-100)')
    parser.add_argument('--jpeg-quality', type=int, default=85,
                       help='JPEG quality (1-100)')
    
    args = parser.parse_args()
    
    # Check if Pillow is installed
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow library is required. Install it with:")
        print("pip install Pillow")
        sys.exit(1)
    
    # Create optimizer
    optimizer = ImageOptimizer(args.input, args.output)
    optimizer.webp_quality = args.webp_quality
    optimizer.jpeg_quality = args.jpeg_quality
    
    print("🖼️  Image Optimization Script")
    print("=" * 40)
    print(f"Input directory: {optimizer.input_dir}")
    print(f"Output directory: {optimizer.output_dir}")
    print(f"WebP quality: {optimizer.webp_quality}")
    print(f"JPEG quality: {optimizer.jpeg_quality}")
    print()
    
    # Process images
    optimizer.process_all_images()
    
    # Generate HTML examples
    optimizer.generate_html_examples()

    # Generate replacement script
    optimizer.generate_replacement_script()

    # Print statistics
    optimizer.print_statistics()
    
    print("\n✅ Optimization complete!")
    print("\nNext steps:")
    print("1. Update your HTML to use the optimized images")
    print("2. Check the html_examples folder for responsive image code")
    print("3. Test your website performance")

if __name__ == "__main__":
    main()
