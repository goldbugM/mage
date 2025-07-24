# Premium Chauffeur Travel Blog - Eleventy Project

A modern, maintainable static site built with Eleventy (11ty) for the Premium Chauffeur luxury travel blog.

## 🚀 Project Overview

This project has been refactored from a collection of individual HTML files into a modern, templated system using Eleventy. The refactor eliminates code duplication, separates content from presentation, and provides a scalable workflow for adding new content.

## 📁 Project Structure

```
├── src/                          # Source directory
│   ├── _includes/               # Templates and layouts
│   │   ├── layouts/            # Page layouts
│   │   │   ├── base.njk       # Base HTML template
│   │   │   └── guide.njk      # Guide page template
│   │   └── partials/          # Reusable components
│   │       ├── header.njk     # Site header
│   │       └── footer.njk     # Site footer
│   ├── _data/                  # Global data files
│   ├── guides/                 # Travel guide content (Markdown)
│   ├── public/                 # Static assets
│   │   ├── css/               # Stylesheets
│   │   ├── js/                # JavaScript files
│   │   └── images/            # Images
│   └── index.njk              # Homepage template
├── _site/                      # Generated site (output)
├── .eleventy.js               # Eleventy configuration
├── package.json               # Node.js dependencies
└── README.md                  # This file
```

## 🛠 Installation & Setup

1. **Install Node.js** (version 14 or higher)

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Development server:**
   ```bash
   npm start
   ```
   This starts a local development server with live reload at `http://localhost:8080`

4. **Build for production:**
   ```bash
   npm run build
   ```
   This generates the static site in the `_site` directory

## 📝 Adding New Travel Guides

### Method 1: Create Markdown File Manually

1. Create a new `.md` file in `src/guides/` directory
2. Add YAML front matter with required fields:

```yaml
---
title: "Your Guide Title"
description: "Brief description of the destination"
heroImage: "/public/images/your-hero-image.jpg"
category: "Guide Category"
location: "City, Country"
date: 2025-01-23
tags: ['guides', 'category-tag']
layout: layouts/guide.njk
---
```

3. Write your content in Markdown below the front matter
4. Build the site to see your new guide

### Method 2: Use the Migration Script

If you have existing HTML files to convert:

1. Place your HTML file in the root directory
2. Update the `guide_categories` dictionary in `migrate_content.py`
3. Run the migration script:
   ```bash
   python migrate_content.py
   ```

## 🏷 Content Categories & Tags

The site organizes content into the following categories:

- **German Destinations** (`german`): German cities and regions
- **European Destinations** (`european`): Other European locations
- **Automotive Experiences** (`automotive`): Car-related attractions
- **Alpine Retreats** (`alpine`): Mountain destinations
- **Coastal Elegance** (`coastal`): Seaside locations
- **Theme Parks** (`theme-parks`): Entertainment venues
- **Shopping Destinations** (`shopping`): Retail locations

## 🎨 Customization

### Styling
- Main styles are in `src/public/css/main.css`
- Uses CSS custom properties for easy theming
- Apple-inspired design system with glassmorphism effects

### Templates
- Base layout: `src/_includes/layouts/base.njk`
- Guide layout: `src/_includes/layouts/guide.njk`
- Homepage: `src/index.njk`

### JavaScript
- Main functionality in `src/public/js/main.js`
- Handles page navigation, mobile menu, and lazy loading

## 🔧 Configuration

The Eleventy configuration is in `.eleventy.js` and includes:

- **Collections**: Automatic grouping by tags
- **Filters**: Custom filters for content processing
- **Passthrough Copy**: Static asset handling
- **Watch Targets**: File watching for development

## 📊 Collections

The following collections are automatically generated:

- `collections.guides` - All travel guides
- `collections.germanGuides` - German destinations
- `collections.europeanGuides` - European destinations
- `collections.automotiveGuides` - Automotive experiences
- `collections.themeParks` - Theme park guides
- `collections.shopping` - Shopping destinations
- `collections.alpine` - Alpine destinations
- `collections.coastal` - Coastal destinations

## 🚀 Deployment

The generated `_site` directory contains the complete static website and can be deployed to any static hosting service:

- **Netlify**: Connect your Git repository for automatic deployments
- **Vercel**: Deploy directly from Git with zero configuration
- **GitHub Pages**: Use GitHub Actions for automated builds
- **Traditional hosting**: Upload the `_site` contents via FTP

## 📈 Performance Features

- **Optimized CSS**: Consolidated stylesheets with minimal redundancy
- **Lazy Loading**: Images load as they enter the viewport
- **Clean URLs**: SEO-friendly URL structure
- **Responsive Design**: Mobile-first approach
- **Fast Navigation**: Client-side page switching for categories

## 🔍 SEO Features

- **Meta Tags**: Comprehensive meta tag support
- **Open Graph**: Social media sharing optimization
- **Canonical URLs**: Proper canonical URL structure
- **Semantic HTML**: Accessible and semantic markup
- **Reading Time**: Automatic reading time calculation

## 🛡 Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Progressive enhancement for older browsers
- Mobile-responsive design
- Touch-friendly navigation

## 📞 Support

For questions or issues with this Eleventy setup, refer to:
- [Eleventy Documentation](https://www.11ty.dev/docs/)
- [Nunjucks Template Documentation](https://mozilla.github.io/nunjucks/)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Built with ❤️ using Eleventy Static Site Generator**
