#!/usr/bin/env python3
"""
Scraper Health Check
This script tests all available scrapers to see which ones are working
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def test_scraper(scraper_path):
    """Test a single scraper and return results"""
    print(f"🔄 Testing {scraper_path.name}...")
    
    try:
        # Run the scraper with a timeout
        result = subprocess.run(
            [sys.executable, str(scraper_path)],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            # Check if it created output files
            output_files = []
            for file in Path('.').glob('*_events_debug.json'):
                output_files.append(file.name)
            
            if output_files:
                # Read the output to see how many events were scraped
                event_count = 0
                for file in output_files:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                event_count += len(data)
                            elif isinstance(data, dict) and 'events' in data:
                                event_count += len(data['events'])
                    except:
                        pass
                
                return {
                    'status': 'working',
                    'events_scraped': event_count,
                    'output_files': output_files,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                return {
                    'status': 'no_output',
                    'events_scraped': 0,
                    'output_files': [],
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
        else:
            return {
                'status': 'failed',
                'events_scraped': 0,
                'output_files': [],
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'events_scraped': 0,
            'output_files': [],
            'stdout': '',
            'stderr': 'Scraper timed out after 2 minutes'
        }
    except Exception as e:
        return {
            'status': 'crashed',
            'events_scraped': 0,
            'output_files': [],
            'stdout': '',
            'stderr': str(e)
        }

def main():
    """Main health check function"""
    print("🏥 NYC Academic Events - Scraper Health Check")
    print("=" * 60)
    
    # Get all scraper files
    scrapers_dir = Path('scrapers')
    if not scrapers_dir.exists():
        print("❌ Scrapers directory not found!")
        return
    
    scraper_files = list(scrapers_dir.glob('*_events.py'))
    print(f"📊 Found {len(scraper_files)} scrapers to test")
    
    # Test each scraper
    results = {}
    working_scrapers = []
    broken_scrapers = []
    total_events = 0
    
    for scraper_path in scraper_files:
        result = test_scraper(scraper_path)
        results[scraper_path.name] = result
        
        if result['status'] == 'working':
            working_scrapers.append(scraper_path.name)
            total_events += result['events_scraped']
        else:
            broken_scrapers.append(scraper_path.name)
        
        # Clean up output files
        for file in result.get('output_files', []):
            try:
                os.remove(file)
            except:
                pass
    
    # Print summary
    print("\n" + "=" * 60)
    print("📈 SCRAPER HEALTH SUMMARY")
    print("=" * 60)
    
    print(f"✅ Working Scrapers: {len(working_scrapers)}")
    print(f"❌ Broken Scrapers: {len(broken_scrapers)}")
    print(f"📊 Total Events Scraped: {total_events}")
    
    if working_scrapers:
        print(f"\n🎉 Working Scrapers:")
        for scraper in working_scrapers:
            result = results[scraper]
            print(f"   ✅ {scraper} - {result['events_scraped']} events")
    
    if broken_scrapers:
        print(f"\n💥 Broken Scrapers:")
        for scraper in broken_scrapers:
            result = results[scraper]
            print(f"   ❌ {scraper} - {result['status']}")
            if result['stderr']:
                print(f"      Error: {result['stderr'][:100]}...")
    
    # Update weekly scraper configuration
    print(f"\n🔧 RECOMMENDATIONS:")
    print(f"   1. Update weekly_scraper.py to include working scrapers")
    print(f"   2. Fix broken scrapers to increase event count")
    print(f"   3. Test scrapers regularly to maintain health")
    
    # Save detailed results
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'total_scrapers': len(scraper_files),
        'working_scrapers': working_scrapers,
        'broken_scrapers': broken_scrapers,
        'total_events': total_events,
        'detailed_results': results
    }
    
    with open('scraper_health_report.json', 'w', encoding='utf-8') as f:
        json.dump(health_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed report saved to scraper_health_report.json")
    
    return health_report

if __name__ == "__main__":
    main()
