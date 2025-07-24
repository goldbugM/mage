#!/usr/bin/env python3
"""
Transform all guide pages to Apple-like design with premium chauffeur insights.
This script processes all markdown files in the guides directory and applies:
- Consistent Apple-like heading structure
- Premium chauffeur insights based on destination type
- Fixed hero image paths
- Proper H1 titles
- Clean markdown formatting
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class GuideTransformer:
    def __init__(self, guides_dir: str = "src/guides"):
        self.guides_dir = Path(guides_dir)
        
        # Premium chauffeur insights by category
        self.insights = {
            'city': {
                'intro': "Our expert chauffeurs navigate the city's complex layout while sharing insider knowledge about hidden gems, optimal timing for major attractions, and exclusive access opportunities.",
                'luxury': "We provide VIP shopping experiences with direct boutique access, personal shopping coordination, and secure transportation for valuable purchases. Our chauffeurs maintain relationships with luxury store managers for exclusive appointments.",
                'hotels': "We coordinate seamlessly with luxury hotels, providing white-glove service from arrival to departure. Our fleet includes vehicles specifically equipped for luxury hotel standards with preferred partnerships.",
                'culture': "Our cultural concierge services include advance reservations, private guided tours, and strategic routing to maximize your experience while avoiding crowds."
            },
            'theme_park': {
                'intro': "Our family-focused service includes child safety seats, stroller accommodation, and strategic timing to maximize your theme park experience while minimizing wait times.",
                'logistics': "We provide convenient drop-off and pickup coordination, secure storage for purchases, and flexible scheduling to accommodate park hours and special events.",
                'planning': "Our local expertise includes knowledge of peak times, fast-pass strategies, and family-friendly dining reservations to enhance your visit."
            },
            'shopping': {
                'intro': "We specialize in luxury shopping experiences with direct access to premium outlets, personal shopping coordination, and secure transportation for valuable purchases.",
                'vip': "Our VIP shopping services include private appointments, tax-free shopping assistance, and coordination with personal shoppers for an exclusive retail experience.",
                'logistics': "We provide secure storage for purchases, multiple pickup locations, and coordination with shipping services for international deliveries."
            },
            'luxury_experience': {
                'intro': "Our premium service enhances exclusive experiences with seamless coordination, insider access, and personalized attention to every detail.",
                'exclusive': "We arrange exclusive access, private tours, and behind-the-scenes experiences not available to typical visitors through our network of luxury partnerships.",
                'concierge': "Our concierge services extend beyond transportation to include reservations, special arrangements, and coordination with luxury service providers."
            },
            'nature': {
                'intro': "Our scenic route expertise and luxury vehicles provide the perfect way to experience natural beauty while maintaining comfort and style throughout your journey.",
                'seasonal': "We adapt our services to seasonal conditions, providing appropriate vehicles and flexible itineraries to ensure optimal experiences year-round.",
                'activities': "We coordinate outdoor activities, equipment rentals, and guide services while providing comfortable transportation to remote locations."
            }
        }
    
    def categorize_destination(self, filename: str, content: str) -> str:
        """Categorize destination based on filename and content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Theme parks
        if any(park in filename_lower for park in ['disneyland', 'europa-park', 'legoland', 'phantasialand', 'heide-park', 'movie-park', 'theme-parks']):
            return 'theme_park'
        
        # Shopping destinations
        if any(shop in filename_lower for shop in ['outlet', 'village', 'shopping', 'metzingen', 'roermond', 'wertheim', 'ingolstadt', 'la-vallee']):
            return 'shopping'
        
        # Luxury experiences
        if any(lux in filename_lower for lux in ['bmw', 'mercedes', 'porsche', 'yacht', 'casino', 'luxury']):
            return 'luxury_experience'
        
        # Nature/Alpine destinations
        if any(nature in filename_lower for nature in ['alpine', 'alps', 'black-forest', 'swiss', 'zermatt', 'interlaken', 'tirol']):
            return 'nature'
        
        # Default to city
        return 'city'
    
    def fix_hero_image_path(self, content: str) -> str:
        """Fix hero image paths to use correct format."""
        # Fix paths that start with "public/"
        content = re.sub(r'heroImage:\s*["\']public/images/', 'heroImage: "/images/', content)
        # Fix paths that don't start with "/"
        content = re.sub(r'heroImage:\s*["\']images/', 'heroImage: "/images/', content)
        return content
    
    def extract_frontmatter_and_content(self, content: str) -> Tuple[str, str]:
        """Extract frontmatter and main content."""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = f"---{parts[1]}---"
                main_content = parts[2].strip()
                return frontmatter, main_content
        return "", content
    
    def clean_content_start(self, content: str) -> str:
        """Remove redundant metadata lines at the start of content."""
        lines = content.split('\n')
        cleaned_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            # Skip lines that look like metadata (category __X min read __location __date)
            if re.match(r'^[A-Za-z\s]+\s+__\d+\s+min\s+read\s+__.*__Updated.*$', line.strip()):
                continue
            # Skip empty lines at the start
            if not cleaned_lines and not line.strip():
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def add_main_title(self, content: str, title: str) -> str:
        """Add H1 title at the beginning of content if not present."""
        lines = content.split('\n')

        # Check if first non-empty line is already an H1
        for line in lines:
            if line.strip():
                if line.startswith('# '):
                    return content  # Already has H1
                break

        # Add H1 title
        title_line = f"# {title}"
        if lines and lines[0].strip():
            return f"{title_line}\n\n{content}"
        else:
            # Find first non-empty line and insert before it
            for i, line in enumerate(lines):
                if line.strip():
                    lines.insert(i, title_line)
                    lines.insert(i + 1, "")
                    return '\n'.join(lines)

            # If all lines are empty, just add at the beginning
            return f"{title_line}\n\n{content}"

    def normalize_headings(self, content: str) -> str:
        """Normalize heading structure for Apple-like hierarchy."""
        lines = content.split('\n')
        normalized_lines = []

        for line in lines:
            stripped = line.strip()

            # Convert ## to ## (main sections)
            if stripped.startswith('## '):
                normalized_lines.append(line)
            # Convert ### to ### (subsections)
            elif stripped.startswith('### '):
                normalized_lines.append(line)
            # Convert #### to #### (sub-subsections)
            elif stripped.startswith('#### '):
                normalized_lines.append(line)
            # Convert **bold text:** patterns to ### headings
            elif re.match(r'^\*\*[^*]+\*\*\s*:', stripped):
                heading_text = re.sub(r'^\*\*([^*]+)\*\*\s*:?', r'\1', stripped)
                normalized_lines.append(f"### {heading_text}")
            else:
                normalized_lines.append(line)

        return '\n'.join(normalized_lines)

    def create_insight_box(self, insight_text: str) -> str:
        """Create a premium chauffeur insight box."""
        return f'''
<div class="premium-insight">
<h4>Premium Chauffeur Insight</h4>
<p>{insight_text}</p>
</div>'''

    def add_strategic_insights(self, content: str, category: str, title: str) -> str:
        """Add strategic premium chauffeur insights based on content analysis."""
        insights_to_add = []
        content_lower = content.lower()

        # Always add intro insight after first paragraph
        intro_insight = self.insights[category]['intro']

        # Add category-specific insights based on content
        if category == 'city':
            if any(word in content_lower for word in ['shopping', 'luxury', 'boutique', 'chanel', 'louis vuitton']):
                insights_to_add.append(('luxury', self.insights[category]['luxury']))
            if any(word in content_lower for word in ['hotel', 'kempinski', 'mandarin', 'ritz']):
                insights_to_add.append(('hotels', self.insights[category]['hotels']))
            if any(word in content_lower for word in ['museum', 'gallery', 'cultural', 'art']):
                insights_to_add.append(('culture', self.insights[category]['culture']))

        elif category == 'theme_park':
            insights_to_add.append(('logistics', self.insights[category]['logistics']))
            if 'family' in content_lower or 'children' in content_lower:
                insights_to_add.append(('planning', self.insights[category]['planning']))

        elif category == 'shopping':
            insights_to_add.append(('vip', self.insights[category]['vip']))
            insights_to_add.append(('logistics', self.insights[category]['logistics']))

        elif category == 'luxury_experience':
            insights_to_add.append(('exclusive', self.insights[category]['exclusive']))
            insights_to_add.append(('concierge', self.insights[category]['concierge']))

        elif category == 'nature':
            insights_to_add.append(('seasonal', self.insights[category]['seasonal']))
            if any(word in content_lower for word in ['hiking', 'skiing', 'activities']):
                insights_to_add.append(('activities', self.insights[category]['activities']))

        # Limit to 2-3 most relevant insights
        insights_to_add = insights_to_add[:2]

        return self.insert_insights(content, intro_insight, insights_to_add)

    def insert_insights(self, content: str, intro_insight: str, additional_insights: List[Tuple[str, str]]) -> str:
        """Insert insights at strategic locations in the content."""
        lines = content.split('\n')
        result_lines = []

        # Add intro insight after first paragraph
        first_paragraph_end = False
        insight_added = False

        for i, line in enumerate(lines):
            result_lines.append(line)

            # Add intro insight after first substantial paragraph
            if not insight_added and not first_paragraph_end:
                if line.strip() and not line.startswith('#') and len(line.strip()) > 100:
                    # Look ahead to see if next line is empty (end of paragraph)
                    if i + 1 < len(lines) and not lines[i + 1].strip():
                        result_lines.append(self.create_insight_box(intro_insight))
                        insight_added = True
                        first_paragraph_end = True

        # Add additional insights before major sections
        if additional_insights:
            final_lines = []
            insights_iter = iter(additional_insights)
            current_insight = next(insights_iter, None)

            for line in result_lines:
                final_lines.append(line)

                # Add insight before luxury/shopping sections
                if current_insight and line.startswith('## ') and any(keyword in line.lower() for keyword in ['luxury', 'shopping', 'experience', 'cultural']):
                    final_lines.append(self.create_insight_box(current_insight[1]))
                    current_insight = next(insights_iter, None)

            return '\n'.join(final_lines)

        return '\n'.join(result_lines)

    def transform_guide(self, filepath: Path) -> bool:
        """Transform a single guide file."""
        try:
            print(f"Processing: {filepath.name}")

            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter and content
            frontmatter, main_content = self.extract_frontmatter_and_content(content)

            if not frontmatter:
                print(f"  ⚠️  No frontmatter found in {filepath.name}")
                return False

            # Fix hero image path
            frontmatter = self.fix_hero_image_path(frontmatter)

            # Extract title from frontmatter
            title_match = re.search(r'title:\s*["\']([^"\']+)["\']', frontmatter)
            if not title_match:
                print(f"  ⚠️  No title found in {filepath.name}")
                return False

            title = title_match.group(1)

            # Clean and process content
            main_content = self.clean_content_start(main_content)
            main_content = self.add_main_title(main_content, title)
            main_content = self.normalize_headings(main_content)

            # Categorize and add insights
            category = self.categorize_destination(filepath.name, main_content)
            main_content = self.add_strategic_insights(main_content, category, title)

            # Combine frontmatter and content
            final_content = f"{frontmatter}\n\n{main_content}"

            # Write back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)

            print(f"  ✅ Transformed {filepath.name} (category: {category})")
            return True

        except Exception as e:
            print(f"  ❌ Error processing {filepath.name}: {str(e)}")
            return False

    def transform_all_guides(self) -> Dict[str, int]:
        """Transform all guide files in the directory."""
        if not self.guides_dir.exists():
            print(f"❌ Guides directory not found: {self.guides_dir}")
            return {'success': 0, 'failed': 0, 'skipped': 0}

        results = {'success': 0, 'failed': 0, 'skipped': 0}
        guide_files = list(self.guides_dir.glob("*.md"))

        print(f"🚀 Found {len(guide_files)} guide files to process")
        print("=" * 60)

        for filepath in sorted(guide_files):
            # Skip the Munich guide as it's already transformed
            if filepath.name == 'munich-guide.md':
                print(f"Skipping: {filepath.name} (already transformed)")
                results['skipped'] += 1
                continue

            if self.transform_guide(filepath):
                results['success'] += 1
            else:
                results['failed'] += 1

        return results

    def print_summary(self, results: Dict[str, int]):
        """Print transformation summary."""
        print("=" * 60)
        print("🎉 TRANSFORMATION COMPLETE!")
        print(f"✅ Successfully transformed: {results['success']} files")
        print(f"⏭️  Skipped: {results['skipped']} files")
        print(f"❌ Failed: {results['failed']} files")
        print("=" * 60)

        if results['success'] > 0:
            print("\n🎨 All guides now feature:")
            print("  • Apple-like typography and design")
            print("  • Strategic premium chauffeur insights")
            print("  • Fixed hero image paths")
            print("  • Consistent heading structure")
            print("  • Clean markdown formatting")


def main():
    """Main execution function."""
    print("🍎 Apple-like Guide Transformer")
    print("Transforming all guide pages with premium chauffeur insights...")
    print()

    # Initialize transformer
    transformer = GuideTransformer()

    # Transform all guides
    results = transformer.transform_all_guides()

    # Print summary
    transformer.print_summary(results)


if __name__ == "__main__":
    main()
