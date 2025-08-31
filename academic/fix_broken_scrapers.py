#!/usr/bin/env python3
"""
Fix Broken Scrapers
This script fixes the common issues in broken scrapers:
1. Changes output directory from 'events_test/' to current directory
2. Updates file naming to match working pattern
3. Fixes other common issues
"""

import os
import re
from pathlib import Path

def fix_scraper_file(file_path):
    """Fix a single scraper file"""
    print(f"🔧 Fixing {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Fix 1: Change events_test/ directory to current directory
        if 'events_test/' in content:
            content = content.replace('events_test/', '')
            changes_made.append("Fixed output directory path")
        
        # Fix 2: Update file naming to match working pattern
        # Change from: "filename.json" to "filename_debug.json"
        if '.json"' in content and '_debug.json"' not in content:
            # Find the specific line with the file save
            content = re.sub(
                r'with open\("([^"]+)\.json", "w"',
                r'with open("\1_debug.json", "w"',
                content
            )
            changes_made.append("Updated file naming to _debug.json")
        
        # Fix 3: Ensure proper error handling for file operations
        if 'with open(' in content and 'try:' not in content:
            # Add try-catch around file operations if missing
            content = re.sub(
                r'(with open\("[^"]+", "w", encoding="utf-8"\) as f:.*?json\.dump.*?\))',
                r'try:\n        \1\nexcept Exception as e:\n        print(f"Error saving file: {e}")',
                content,
                flags=re.DOTALL
            )
            changes_made.append("Added error handling for file operations")
        
        # Fix 4: Update print statements to be more informative
        if 'print(f"' in content and 'events scraped:' in content:
            content = re.sub(
                r'print\(f"([^"]+events scraped: \d+)"\)',
                r'print(f"\1")',
                content
            )
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Fixed: {', '.join(changes_made)}")
            return True
        else:
            print(f"   ⚠️  No changes needed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error fixing {file_path.name}: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 NYC Academic Events - Fix Broken Scrapers")
    print("=" * 60)
    
    scrapers_dir = Path('scrapers')
    if not scrapers_dir.exists():
        print("❌ Scrapers directory not found!")
        return
    
    # Get all scraper files
    scraper_files = list(scrapers_dir.glob('*_events.py'))
    print(f"📊 Found {len(scraper_files)} scrapers to check")
    
    # List of known broken scrapers (from health check)
    broken_scrapers = [
        'brooklyn_college_events.py',
        'columbia_classics_events.py',
        'columbia_history_events.py',
        'columbia_law_events.py',
        'columbia_math_events.py',
        'columbia_religion_events.py',
        'columbia_social_difference_events.py',
        'cooper_union_events.py',
        'fordham_events.py',
        'hunter_college_events.py',
        'juilliard_events.py',
        'miller_events.py',
        'nyu_education_events.py',
        'nyu_general_events.py',
        'nyu_law_events.py',
        'nyu_medicine_events.py',
        'nyu_stern_events.py',
        'pratt_events.py',
        'simons_foundation_events.py',
        'sof_heyman_events.py',
        'stjohns_events.py'
    ]
    
    fixed_count = 0
    total_broken = len(broken_scrapers)
    
    print(f"\n🔧 Fixing {total_broken} broken scrapers...")
    print("=" * 60)
    
    for scraper_name in broken_scrapers:
        scraper_path = scrapers_dir / scraper_name
        if scraper_path.exists():
            if fix_scraper_file(scraper_path):
                fixed_count += 1
        else:
            print(f"⚠️  {scraper_name} not found, skipping")
    
    print("\n" + "=" * 60)
    print("📈 FIXING SUMMARY")
    print("=" * 60)
    print(f"✅ Fixed: {fixed_count}/{total_broken} scrapers")
    print(f"❌ Remaining broken: {total_broken - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 Next steps:")
        print(f"   1. Run health check: python check_scraper_health.py")
        print(f"   2. Test fixed scrapers individually")
        print(f"   3. Update weekly_scraper.py with newly working scrapers")
        print(f"   4. Run weekly scraper to get more events!")
    
    return fixed_count

if __name__ == "__main__":
    main()
