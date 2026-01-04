#!/usr/bin/env python3
"""
Date/Timezone Fixer - Finds and reports date handling issues across all scrapers
"""

import os
import re
from pathlib import Path

def check_scraper(file_path):
    """Check a scraper for date/timezone issues"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Issue 1: Using .date().isoformat() which strips timezone
    if '.date().isoformat()' in content:
        issues.append('CRITICAL: Using .date().isoformat() - loses timezone info')
    
    # Issue 2: Using datetime.now().isoformat() without standardization
    if re.search(r'datetime\.now\(\)\.isoformat\(\)', content):
        issues.append('WARNING: datetime.now().isoformat() without standardization')
    
    # Issue 3: Manual timezone creation with timedelta
    if 'timezone(timedelta(' in content:
        issues.append('WARNING: Manual timezone with timedelta - should use NY_TZ')
    
    # Issue 4: Using strftime instead of isoformat
    if '.strftime(' in content and 'date_utils.py' not in str(file_path):
        issues.append('WARNING: Using strftime() instead of standardized format')
    
    # Issue 5: Not importing date_utils
    has_date_utils_import = 'from date_utils import' in content or 'import date_utils' in content
    has_datetime_usage = 'datetime' in content and ('start_date' in content or 'end_date' in content)
    
    if has_datetime_usage and not has_date_utils_import:
        issues.append('CRITICAL: Using datetime but not importing date_utils')
    
    # Issue 6: Directly calling .isoformat() without standardize_datetime
    if re.search(r'\w+\.isoformat\(\)', content) and 'standardize_datetime' not in content:
        if 'date_utils.py' not in str(file_path):
            issues.append('WARNING: Calling .isoformat() without using standardize_datetime()')
    
    # Issue 7: Creating datetime without timezone
    if 'datetime.strptime(' in content and 'tzinfo' not in content and 'standardize_datetime' not in content:
        issues.append('WARNING: datetime.strptime without timezone handling')
    
    return issues

def main():
    print("=" * 70)
    print("DATE/TIMEZONE ISSUE ANALYZER")
    print("=" * 70)
    print()
    
    scrapers_dir = Path('scrapers')
    
    if not scrapers_dir.exists():
        print("Error: scrapers directory not found")
        return
    
    all_issues = {}
    
    for scraper_file in sorted(scrapers_dir.glob('*.py')):
        if scraper_file.name in ['date_utils.py', '__init__.py', 'category_utils.py', 'event_filter.py']:
            continue
        
        issues = check_scraper(scraper_file)
        if issues:
            all_issues[scraper_file.name] = issues
    
    # Report findings
    if not all_issues:
        print("SUCCESS: No date/timezone issues found!")
        return
    
    print(f"Found issues in {len(all_issues)} scrapers:\n")
    
    critical_count = 0
    warning_count = 0
    
    for scraper_name, issues in sorted(all_issues.items()):
        print(f"\n{scraper_name}:")
        for issue in issues:
            if issue.startswith('CRITICAL'):
                print(f"  [!] {issue}")
                critical_count += 1
            else:
                print(f"  [ ] {issue}")
                warning_count += 1
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {critical_count} critical issues, {warning_count} warnings")
    print("=" * 70)
    
    print("\nMost common issues:")
    print("1. Using .date().isoformat() - strips timezone and time info")
    print("2. Not using standardize_datetime() wrapper")
    print("3. datetime.strptime() without timezone handling")
    print("\nRecommended fixes:")
    print("1. Import: from date_utils import create_event_dates, standardize_datetime")
    print("2. Use: start_date, end_date = create_event_dates(date_str, time_str)")
    print("3. Wrap all datetime objects: standardize_datetime(dt)")

if __name__ == "__main__":
    main()

