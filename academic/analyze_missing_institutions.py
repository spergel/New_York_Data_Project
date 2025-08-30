#!/usr/bin/env python3
"""
Script to analyze which institutions from our scrapers are missing from our current data
"""

import json
import os
import re

def extract_institution_from_filename(filename):
    """Extract institution name from scraper filename"""
    # Remove .py extension and _events suffix
    name = filename.replace('.py', '').replace('_events', '')
    
    # Handle special cases
    if name == 'nyu_cims':
        return 'nyu_cims'
    elif name == 'nyu_engineering':
        return 'nyu_engineering'
    elif name == 'nyu_general':
        return 'nyu_general'
    elif name == 'nyu_education':
        return 'nyu_education'
    elif name == 'nyu_law':
        return 'nyu_law'
    elif name == 'nyu_medicine':
        return 'nyu_medicine'
    elif name == 'nyu_stern':
        return 'nyu_stern'
    elif name == 'columbia_classics':
        return 'columbia_classics'
    elif name == 'columbia_general':
        return 'columbia_general'
    elif name == 'columbia_history':
        return 'columbia_history'
    elif name == 'columbia_law':
        return 'columbia_law'
    elif name == 'columbia_math':
        return 'columbia_math'
    elif name == 'columbia_religion':
        return 'columbia_religion'
    elif name == 'columbia_social_difference':
        return 'columbia_social_difference'
    elif name == 'brooklyn_college':
        return 'brooklyn_college'
    elif name == 'hunter_college':
        return 'hunter_college'
    elif name == 'stjohns':
        return 'stjohns'
    elif name == 'cooper_union':
        return 'cooper_union'
    elif name == 'pratt':
        return 'pratt'
    elif name == 'simons_foundation':
        return 'simons_foundation'
    elif name == 'sof_heyman':
        return 'sof_heyman'
    else:
        return name

def analyze_missing_institutions():
    """Analyze which institutions are missing from our data"""
    
    # Get all scraper files
    scraper_files = [f for f in os.listdir('scrapers') if f.endswith('.py') and f != '__init__.py']
    
    # Extract institutions from scraper filenames
    scraper_institutions = set()
    for filename in scraper_files:
        institution = extract_institution_from_filename(filename)
        scraper_institutions.add(institution)
    
    # Load current data
    try:
        with open('events_test/academic_events_filtered.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        current_institutions = set(event['source'] for event in data['events'])
    except FileNotFoundError:
        current_institutions = set()
        print("⚠️  No current data found. Run scraping first.")
    
    # Find missing institutions
    missing_institutions = scraper_institutions - current_institutions
    
    # Group institutions by type
    columbia_scrapers = [i for i in scraper_institutions if i.startswith('columbia_')]
    nyu_scrapers = [i for i in scraper_institutions if i.startswith('nyu_')]
    cuny_scrapers = [i for i in scraper_institutions if 'college' in i or i in ['hunter_college', 'brooklyn_college']]
    other_scrapers = [i for i in scraper_institutions if not i.startswith('columbia_') and not i.startswith('nyu_') and i not in cuny_scrapers]
    
    # Print analysis
    print("🔍 INSTITUTION ANALYSIS")
    print("=" * 50)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total scrapers: {len(scraper_institutions)}")
    print(f"   Current institutions: {len(current_institutions)}")
    print(f"   Missing institutions: {len(missing_institutions)}")
    
    print(f"\n✅ CURRENT INSTITUTIONS ({len(current_institutions)}):")
    for inst in sorted(current_institutions):
        count = len([e for e in data['events'] if e['source'] == inst])
        print(f"   • {inst} ({count} events)")
    
    print(f"\n❌ MISSING INSTITUTIONS ({len(missing_institutions)}):")
    for inst in sorted(missing_institutions):
        print(f"   • {inst}")
    
    print(f"\n🏛️  COLUMBIA SCRAPERS ({len(columbia_scrapers)}):")
    for inst in sorted(columbia_scrapers):
        status = "✅" if inst in current_institutions else "❌"
        print(f"   {status} {inst}")
    
    print(f"\n🎓 NYU SCRAPERS ({len(nyu_scrapers)}):")
    for inst in sorted(nyu_scrapers):
        status = "✅" if inst in current_institutions else "❌"
        print(f"   {status} {inst}")
    
    print(f"\n🏫 CUNY SCRAPERS ({len(cuny_scrapers)}):")
    for inst in sorted(cuny_scrapers):
        status = "✅" if inst in current_institutions else "❌"
        print(f"   {status} {inst}")
    
    print(f"\n🏢 OTHER INSTITUTIONS ({len(other_scrapers)}):")
    for inst in sorted(other_scrapers):
        status = "✅" if inst in current_institutions else "❌"
        print(f"   {status} {inst}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if missing_institutions:
        print(f"   1. Run scraping for missing institutions")
        print(f"   2. Check if scrapers are working properly")
        print(f"   3. Verify academic event filtering")
        
        print(f"\n🚀 QUICK FIX - Run these scrapers:")
        for inst in sorted(missing_institutions):
            print(f"   python scrapers/{inst}_events.py")
    else:
        print("   ✅ All scrapers are working! No missing institutions.")

if __name__ == "__main__":
    analyze_missing_institutions()
