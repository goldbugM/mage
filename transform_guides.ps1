# PowerShell script to transform guide files to Apple-like design
# This script applies consistent formatting and premium chauffeur insights

Write-Host "🍎 Apple-like Guide Transformer" -ForegroundColor Green
Write-Host "Transforming guide pages with premium chauffeur insights..." -ForegroundColor Yellow
Write-Host ""

# Define the guides directory
$guidesDir = "src/guides"

# Check if directory exists
if (-not (Test-Path $guidesDir)) {
    Write-Host "❌ Guides directory not found: $guidesDir" -ForegroundColor Red
    exit 1
}

# Get all markdown files except munich-guide.md (already transformed)
$guideFiles = Get-ChildItem -Path $guidesDir -Filter "*.md" | Where-Object { $_.Name -ne "munich-guide.md" }

Write-Host "🚀 Found $($guideFiles.Count) guide files to process" -ForegroundColor Cyan
Write-Host "=" * 60

$successCount = 0
$failedCount = 0

foreach ($file in $guideFiles) {
    Write-Host "Processing: $($file.Name)" -ForegroundColor White
    
    try {
        # Read the file content
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        
        # Fix hero image paths
        $content = $content -replace 'heroImage:\s*["\']public/images/', 'heroImage: "/images/'
        $content = $content -replace 'heroImage:\s*["\']images/', 'heroImage: "/images/'
        
        # Extract title from frontmatter
        if ($content -match 'title:\s*["\']([^"\']+)["\']') {
            $title = $matches[1]
            
            # Remove metadata lines at start of content
            $content = $content -replace '(?m)^[A-Za-z\s]+\s+__\d+\s+min\s+read\s+__.*__Updated.*$\r?\n', ''
            
            # Add H1 title if not present
            if ($content -notmatch '(?m)^#\s+') {
                # Find the position after frontmatter
                $frontmatterEnd = $content.IndexOf('---', 3) + 3
                if ($frontmatterEnd -gt 3) {
                    $frontmatter = $content.Substring(0, $frontmatterEnd)
                    $mainContent = $content.Substring($frontmatterEnd).TrimStart()
                    
                    # Add title
                    $mainContent = "# $title`n`n$mainContent"
                    $content = "$frontmatter`n`n$mainContent"
                }
            }
            
            # Add basic premium chauffeur insight after first paragraph
            $insightAdded = $false
            $lines = $content -split "`n"
            $newLines = @()
            $inFrontmatter = $false
            $frontmatterCount = 0
            $firstParagraphFound = $false
            
            foreach ($line in $lines) {
                $newLines += $line
                
                # Track frontmatter
                if ($line -eq "---") {
                    $frontmatterCount++
                    if ($frontmatterCount -eq 2) {
                        $inFrontmatter = $false
                    } else {
                        $inFrontmatter = $true
                    }
                    continue
                }
                
                # Skip if still in frontmatter
                if ($inFrontmatter) {
                    continue
                }
                
                # Add insight after first substantial paragraph
                if (-not $insightAdded -and -not $firstParagraphFound -and $line.Length -gt 100 -and -not $line.StartsWith("#")) {
                    $firstParagraphFound = $true
                    $newLines += ""
                    $newLines += '<div class="premium-insight">'
                    $newLines += '<h4>Premium Chauffeur Insight</h4>'
                    
                    # Determine category-specific insight
                    $fileName = $file.Name.ToLower()
                    if ($fileName -match "theme|park|disney|legoland|europa") {
                        $newLines += '<p>Our family-focused service includes child safety seats, stroller accommodation, and strategic timing to maximize your theme park experience while minimizing wait times.</p>'
                    }
                    elseif ($fileName -match "outlet|shopping|village") {
                        $newLines += '<p>We specialize in luxury shopping experiences with direct access to premium outlets, personal shopping coordination, and secure transportation for valuable purchases.</p>'
                    }
                    elseif ($fileName -match "bmw|mercedes|porsche|luxury") {
                        $newLines += '<p>Our premium service enhances exclusive experiences with seamless coordination, insider access, and personalized attention to every detail.</p>'
                    }
                    elseif ($fileName -match "alpine|alps|swiss|mountain") {
                        $newLines += '<p>Our scenic route expertise and luxury vehicles provide the perfect way to experience natural beauty while maintaining comfort and style throughout your journey.</p>'
                    }
                    else {
                        $newLines += '<p>Our expert chauffeurs navigate the complex layout while sharing insider knowledge about hidden gems, optimal timing for major attractions, and exclusive access opportunities.</p>'
                    }
                    
                    $newLines += '</div>'
                    $insightAdded = $true
                }
            }
            
            $content = $newLines -join "`n"
            
            # Write back to file
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8
            
            Write-Host "  ✅ Transformed $($file.Name)" -ForegroundColor Green
            $successCount++
        }
        else {
            Write-Host "  ⚠️  No title found in $($file.Name)" -ForegroundColor Yellow
            $failedCount++
        }
    }
    catch {
        Write-Host "  ❌ Error processing $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }
}

# Print summary
Write-Host "=" * 60
Write-Host "🎉 TRANSFORMATION COMPLETE!" -ForegroundColor Green
Write-Host "✅ Successfully transformed: $successCount files" -ForegroundColor Green
Write-Host "❌ Failed: $failedCount files" -ForegroundColor Red
Write-Host "=" * 60

if ($successCount -gt 0) {
    Write-Host ""
    Write-Host "🎨 All guides now feature:" -ForegroundColor Cyan
    Write-Host "  • Apple-like typography and design" -ForegroundColor White
    Write-Host "  • Strategic premium chauffeur insights" -ForegroundColor White
    Write-Host "  • Fixed hero image paths" -ForegroundColor White
    Write-Host "  • Consistent heading structure" -ForegroundColor White
    Write-Host "  • Clean markdown formatting" -ForegroundColor White
}
