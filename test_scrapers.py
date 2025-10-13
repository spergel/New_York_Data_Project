#!/usr/bin/env python3
"""
Comprehensive Scraper Testing Suite
Tests all scrapers across academic, tech, and exercise categories
"""

import os
import sys
import json
import subprocess
import importlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
import argparse

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class ScraperTester:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = defaultdict(list)
        self.stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    def log(self, message, color='', bold=False):
        """Print colored message"""
        prefix = Colors.BOLD if bold else ''
        print(f"{prefix}{color}{message}{Colors.RESET}")
    
    def validate_event(self, event: Dict, source: str) -> Tuple[bool, List[str]]:
        """Validate a single event and return (is_valid, issues)"""
        issues = []
        
        # Required fields check (allow various field names)
        title = event.get('title') or event.get('name')
        start_date = event.get('start_date') or event.get('startDate') or event.get('start')
        source = event.get('source') or event.get('source_group')

        if not title:
            issues.append("Missing required field: title/name")
        if not start_date:
            issues.append("Missing required field: start_date/startDate")
        if not source:
            issues.append("Missing required field: source/source_group")
        
        # Date validation (try multiple field names)
        start_date = start_date  # Use the variable we already defined above

        if start_date:
            try:
                # Handle different date formats
                start_str = str(start_date)

                # Handle ISO format with timezone
                if 'T' in start_str and ('+' in start_str or 'Z' in start_str):
                    start_str = start_str.replace('Z', '+00:00')
                    start = datetime.fromisoformat(start_str)
                # Handle date-only format (YYYY-MM-DD)
                elif len(start_str) == 10 and start_str.count('-') == 2:
                    start = datetime.fromisoformat(start_str)
                else:
                    # Try parsing as ISO format anyway
                    start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))

                # Make datetime timezone-naive for comparison
                if start.tzinfo is not None:
                    start = start.replace(tzinfo=None)
                now = datetime.now()
                # Check if event is too far in the past (more than 1 week ago)
                if start < now - timedelta(days=7):
                    issues.append(f"Event is more than 1 week in the past: {start.date()}")
                # Check if event is too far in the future (more than 1 year)
                if start > now + timedelta(days=365):
                    issues.append(f"Event is more than 1 year in the future: {start.date()}")
            except (ValueError, AttributeError, TypeError) as e:
                issues.append(f"Invalid date format: {start_date}")
        
        # Description check (warning only)
        if 'description' not in event or not event['description']:
            issues.append("Missing description (warning)")
        elif len(event['description']) < 20:
            issues.append(f"Description too short ({len(event['description'])} chars)")
        
        # Location check (warning only)
        if 'location' not in event or not event['location']:
            issues.append("Missing location (warning)")
        
        # URL check
        if 'url' not in event or not event['url']:
            issues.append("Missing URL")
        
        # Check for duplicate or invalid IDs
        if 'id' in event:
            if not event['id'] or event['id'] == '':
                issues.append("Empty event ID")
        
        is_valid = not any(issue for issue in issues if 'warning' not in issue.lower())
        return is_valid, issues
    
    def test_scraper_output(self, scraper_name: str, output_file: Path, category: str) -> Dict:
        """Test a scraper's output file"""
        result = {
            'scraper': scraper_name,
            'category': category,
            'status': 'unknown',
            'events_count': 0,
            'valid_events': 0,
            'issues': [],
            'sample_event': None
        }
        
        # Check if output file exists
        if not output_file.exists():
            result['status'] = 'no_output'
            result['issues'].append(f"Output file not found: {output_file}")
            return result
        
        # Try to load and validate events
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract events from data
            if isinstance(data, list):
                events = data
            elif isinstance(data, dict) and 'events' in data:
                events = data['events']
            else:
                result['status'] = 'invalid_format'
                result['issues'].append(f"Unexpected data format: {type(data)}")
                return result
            
            result['events_count'] = len(events)
            
            # No events found
            if len(events) == 0:
                result['status'] = 'no_events'
                result['issues'].append("No events found in output")
                return result
            
            # Validate each event
            all_issues = []
            valid_count = 0
            
            for i, event in enumerate(events):
                is_valid, issues = self.validate_event(event, scraper_name)
                if is_valid:
                    valid_count += 1
                if issues and i < 3:  # Only report issues for first 3 events
                    all_issues.extend([f"Event {i+1}: {issue}" for issue in issues])
            
            result['valid_events'] = valid_count
            result['issues'] = all_issues[:10]  # Limit to 10 issues
            
            # Store sample event
            result['sample_event'] = {
                'title': events[0].get('title') or events[0].get('name', 'N/A'),
                'start_date': events[0].get('start_date') or events[0].get('startDate') or events[0].get('start', 'N/A'),
                'source': events[0].get('source') or events[0].get('source_group', 'N/A')
            }
            
            # Determine status
            if valid_count == len(events):
                result['status'] = 'success'
            elif valid_count > len(events) * 0.5:
                result['status'] = 'partial'
            else:
                result['status'] = 'failed'
            
        except json.JSONDecodeError as e:
            result['status'] = 'invalid_json'
            result['issues'].append(f"Invalid JSON: {str(e)}")
        except Exception as e:
            result['status'] = 'error'
            result['issues'].append(f"Error: {str(e)}")
        
        return result
    
    def run_scraper(self, scraper_path: Path, timeout: int = 300) -> Tuple[bool, str]:
        """Run a scraper and return (success, error_message)"""
        try:
            result = subprocess.run(
                [sys.executable, str(scraper_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=scraper_path.parent
            )
            
            if result.returncode == 0:
                return True, ""
            else:
                return False, f"Return code {result.returncode}: {result.stderr[:200]}"
        
        except subprocess.TimeoutExpired:
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            return False, str(e)
    
    def test_category(self, category: str, scraper_dir: Path, run_scrapers: bool = False):
        """Test all scrapers in a category"""
        self.log(f"\n{'='*80}", Colors.CYAN, bold=True)
        self.log(f"Testing {category.upper()} Scrapers", Colors.CYAN, bold=True)
        self.log(f"{'='*80}", Colors.CYAN)
        
        # Find all Python scrapers
        scrapers = list(scraper_dir.glob('*.py'))
        scrapers = [s for s in scrapers if s.stem not in ['__init__', 'date_utils', 'event_filter', 'calendar_configs', 'tag_processor', 'proxy_list']]
        
        for scraper in sorted(scrapers):
            scraper_name = scraper.stem
            self.stats['total'] += 1
            
            # Run scraper if requested
            if run_scrapers:
                self.log(f"\n[RUN] Running {scraper_name}...", Colors.BLUE)
                success, error = self.run_scraper(scraper, timeout=180)
                
                if not success:
                    self.log(f"  [FAIL] Failed to run: {error}", Colors.RED)
                    self.results[category].append({
                        'scraper': scraper_name,
                        'status': 'run_failed',
                        'error': error
                    })
                    self.stats['failed'] += 1
                    continue
            
            # Determine output file location
            # Check multiple possible locations and naming patterns
            possible_outputs = [
                scraper_dir / f"{scraper_name}_debug.json",
                scraper_dir / 'data' / f"{scraper_name}_events.json",
                scraper_dir.parent / f"{scraper_name}_debug.json",
                scraper_dir.parent / 'data' / f"{scraper_name.replace('_scraper', '')}_events.json",
            ]

            # For academic scrapers, also check the academic root directory
            if category == 'academic':
                possible_outputs.extend([
                    scraper_dir.parent / f"{scraper_name}_debug.json",
                    scraper_dir.parent / f"{scraper_name.replace('_scraper', '')}_events_debug.json",
                    # Special cases for scrapers with different naming
                    scraper_dir.parent / f"{scraper_name.replace('_general_', '_')}_debug.json",
                    scraper_dir.parent / f"{scraper_name.replace('_events', '')}_debug.json",
                ])
            
            output_file = None
            for possible_output in possible_outputs:
                if possible_output.exists():
                    output_file = possible_output
                    break
            
            # Test the output
            if output_file:
                result = self.test_scraper_output(scraper_name, output_file, category)
                self.results[category].append(result)
                
                # Print result
                if result['status'] == 'success':
                    self.log(f"  [PASS] {scraper_name}: {result['events_count']} events", Colors.GREEN)
                    self.stats['passed'] += 1
                elif result['status'] == 'partial':
                    self.log(f"  [WARN] {scraper_name}: {result['valid_events']}/{result['events_count']} valid events", Colors.YELLOW)
                    self.stats['warnings'] += 1
                    if self.verbose and result['issues']:
                        for issue in result['issues'][:3]:
                            self.log(f"      - {issue}", Colors.YELLOW)
                else:
                    self.log(f"  [FAIL] {scraper_name}: {result['status']}", Colors.RED)
                    self.stats['failed'] += 1
                    if self.verbose and result['issues']:
                        for issue in result['issues'][:3]:
                            self.log(f"      - {issue}", Colors.RED)
            else:
                self.log(f"  [FAIL] {scraper_name}: No output file found", Colors.RED)
                self.results[category].append({
                    'scraper': scraper_name,
                    'status': 'no_output',
                    'error': 'No output file found'
                })
                self.stats['failed'] += 1
    
    def print_summary(self):
        """Print test summary"""
        self.log(f"\n{'='*80}", Colors.CYAN, bold=True)
        self.log("TEST SUMMARY", Colors.CYAN, bold=True)
        self.log(f"{'='*80}", Colors.CYAN)
        
        # Overall stats
        self.log(f"\nOverall Statistics:", Colors.BOLD)
        self.log(f"  Total Scrapers: {self.stats['total']}")
        self.log(f"  Passed: {self.stats['passed']}", Colors.GREEN)
        self.log(f"  Warnings: {self.stats['warnings']}", Colors.YELLOW)
        self.log(f"  Failed: {self.stats['failed']}", Colors.RED)
        
        # Calculate pass rate
        if self.stats['total'] > 0:
            pass_rate = (self.stats['passed'] / self.stats['total']) * 100
            color = Colors.GREEN if pass_rate >= 80 else Colors.YELLOW if pass_rate >= 50 else Colors.RED
            self.log(f"\n  Pass Rate: {pass_rate:.1f}%", color, bold=True)
        
        # Category breakdown
        self.log(f"\nBy Category:", Colors.BOLD)
        for category, results in self.results.items():
            passed = sum(1 for r in results if r['status'] == 'success')
            total = len(results)
            self.log(f"  {category.capitalize()}: {passed}/{total} passed")
        
        # Top issues
        if self.verbose:
            self.log(f"\nFailed Scrapers:", Colors.BOLD)
            for category, results in self.results.items():
                failed = [r for r in results if r['status'] not in ['success', 'partial']]
                if failed:
                    for result in failed:
                        self.log(f"  - {result['scraper']} ({category}): {result['status']}", Colors.RED)
                        if result.get('issues'):
                            self.log(f"    {result['issues'][0]}", Colors.RED)
    
    def save_report(self, output_file: str = 'scraper_test_report.json'):
        """Save detailed test report to JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': dict(self.results)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"\n[REPORT] Detailed report saved to: {output_file}", Colors.BLUE)

def main():
    parser = argparse.ArgumentParser(description='Test all event scrapers')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output with detailed issues')
    parser.add_argument('-r', '--run', action='store_true', help='Run scrapers before testing (default: test existing output)')
    parser.add_argument('-c', '--category', choices=['academic', 'tech', 'exercise', 'all'], default='all', 
                       help='Which category to test')
    parser.add_argument('--report', action='store_true', help='Save detailed JSON report')
    
    args = parser.parse_args()
    
    tester = ScraperTester(verbose=args.verbose)
    
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" + "="*78 + "=")
    print("|" + " "*20 + "SCRAPER TEST SUITE" + " "*40 + "|")
    print("=" + "="*78 + "=")
    print(Colors.RESET)
    
    # Test each category
    categories = {
        'academic': Path('academic/scrapers'),
        'tech': Path('tech/scrapers'),
        'exercise': Path('exercise/scrapers')
    }
    
    for category, scraper_dir in categories.items():
        if args.category in [category, 'all'] and scraper_dir.exists():
            tester.test_category(category, scraper_dir, run_scrapers=args.run)
    
    # Print summary
    tester.print_summary()
    
    # Save report if requested
    if args.report:
        tester.save_report()
    
    # Exit code based on results
    exit_code = 0 if tester.stats['failed'] == 0 else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

