#!/usr/bin/env python3
"""
Date Standardization Helper Script
Helps convert existing scrapers to use standardized date utilities
"""

import os
import re
from pathlib import Path

def find_scrapers_needing_standardization():
    """Find scrapers that need date standardization"""
    scrapers_dir = Path('scrapers')
    scrapers = []
    
    for scraper_file in scrapers_dir.glob('*.py'):
        if scraper_file.name == 'date_utils.py':
            continue
            
        content = scraper_file.read_text(encoding='utf-8')
        
        # Check for non-standardized date patterns
        needs_standardization = False
        issues = []
        
        # Check for .isoformat() calls (good)
        iso_calls = len(re.findall(r'\.isoformat\(\)', content))
        
        # Check for manual datetime formatting (needs fixing)
        strftime_calls = len(re.findall(r'\.strftime\(', content))
        
        # Check for manual date string construction
        manual_dates = len(re.findall(r'datetime\.strptime', content))
        
        # Check for timezone-naive datetime usage
        naive_datetime = len(re.findall(r'datetime\(.*\)', content))
        
        if strftime_calls > 0 or manual_dates > 0 or naive_datetime > 0:
            needs_standardization = True
            if strftime_calls > 0:
                issues.append(f"{strftime_calls} strftime calls")
            if manual_dates > 0:
                issues.append(f"{manual_dates} manual date parsing")
            if naive_datetime > 0:
                issues.append(f"{naive_datetime} naive datetime objects")
        
        scrapers.append({
            'file': scraper_file.name,
            'needs_standardization': needs_standardization,
            'iso_calls': iso_calls,
            'issues': issues,
            'content': content
        })
    
    return scrapers

def generate_migration_guide():
    """Generate a migration guide for standardizing dates"""
    guide = """# Date Standardization Migration Guide

## Overview
This guide helps migrate scrapers from manual date handling to standardized date utilities.

## Before (Manual Date Handling)
```python
# ❌ Manual date parsing
start_date = datetime.strptime(date_str, "%B %d, %Y")
end_date = start_date + timedelta(hours=2)

# ❌ Manual formatting
"start_date": start_date.isoformat(),
"end_date": end_date.isoformat(),
```

## After (Standardized Date Utilities)
```python
# ✅ Import standardized utilities
from date_utils import create_event_dates, standardize_datetime

# ✅ Use standardized functions
start_date, end_date = create_event_dates(date_str, time_str)

# ✅ Dates are already standardized
"start_date": start_date,  # Already ISO format
"end_date": end_date,      # Already ISO format
```

## Migration Steps

### 1. Import Date Utilities
```python
from date_utils import create_event_dates, create_multi_day_event_dates, standardize_datetime
```

### 2. Replace Manual Date Parsing
```python
# Old way
start_date = datetime.strptime(date_str, "%B %d, %Y")
if time_str:
    time_obj = datetime.strptime(time_str, "%I:%M %p").time()
    start_date = start_date.replace(hour=time_obj.hour, minute=time_obj.minute)

# New way
start_date, end_date = create_event_dates(date_str, time_str)
```

### 3. Replace Multi-day Date Parsing
```python
# Old way
if "–" in date_text:
    date_parts = date_text.split("–")
    start_date = parse_date(date_parts[0])
    end_date = parse_date(date_parts[1])

# New way
if "–" in date_text or "-" in date_text:
    date_parts = re.split(r'[–\-]', date_text)
    if len(date_parts) == 2:
        start_date, end_date = create_multi_day_event_dates(
            date_parts[0].strip(), 
            date_parts[1].strip(), 
            time_text
        )
```

### 4. Update Return Statements
```python
# Old way
"start_date": start_date.isoformat() if start_date else None,
"end_date": end_date.isoformat() if end_date else None,

# New way (dates are already standardized)
"start_date": start_date,
"end_date": end_date,
```

### 5. Update Metadata Timestamps
```python
# Old way
"scraped_at": datetime.now().isoformat(),

# New way
"scraped_at": standardize_datetime(datetime.now()),
```

## Benefits of Standardization

1. **Consistent Format**: All dates use ISO 8601 with UTC timezone
2. **Better Parsing**: Handles multiple date formats automatically
3. **Timezone Safety**: All dates are properly timezone-aware
4. **Easier Maintenance**: Centralized date logic
5. **Better Validation**: Built-in date validation and error handling

## Common Date Formats Supported

- "September 3, 2025"
- "Sep 3, 2025"
- "9/3/2025"
- "2025-09-03"
- "September 3" (assumes current year)
- "2:00 PM" or "14:00"
- "2:00 PM – 5:00 PM" (time ranges)

## Testing Your Migration

After migrating, test that:
1. Dates are in ISO 8601 format: `2025-09-03T14:00:00+00:00`
2. All dates have timezone information (`+00:00`)
3. End dates are properly calculated
4. Multi-day events work correctly
"""
    
    with open('DATE_STANDARDIZATION_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("📝 Generated DATE_STANDARDIZATION_GUIDE.md")

def main():
    """Main function to analyze scrapers and generate migration guide"""
    print("🔍 Analyzing scrapers for date standardization needs...")
    
    scrapers = find_scrapers_needing_standardization()
    
    print(f"\n📊 Found {len(scrapers)} scrapers:")
    
    needs_work = []
    already_good = []
    
    for scraper in scrapers:
        if scraper['needs_standardization']:
            needs_work.append(scraper)
            print(f"⚠️  {scraper['file']} - Needs standardization")
            for issue in scraper['issues']:
                print(f"    - {issue}")
        else:
            already_good.append(scraper)
            print(f"✅ {scraper['file']} - Already using ISO format ({scraper['iso_calls']} calls)")
    
    print(f"\n📈 Summary:")
    print(f"✅ Already standardized: {len(already_good)} scrapers")
    print(f"⚠️  Need standardization: {len(needs_work)} scrapers")
    
    if needs_work:
        print(f"\n🎯 Priority scrapers to standardize:")
        for scraper in needs_work[:5]:  # Show top 5
            print(f"   - {scraper['file']}")
    
    # Generate migration guide
    generate_migration_guide()
    
    print(f"\n💡 Next steps:")
    print(f"1. Review DATE_STANDARDIZATION_GUIDE.md")
    print(f"2. Start with scrapers that have the most date parsing issues")
    print(f"3. Use date_utils.py functions for consistent date handling")

if __name__ == "__main__":
    main()



