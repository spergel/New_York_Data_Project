#!/usr/bin/env python3
"""
File Watcher for Real-Time Scraping
This script watches for changes in scraper files and automatically runs them
"""

import time
import os
import sys
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ScraperFileHandler(FileSystemEventHandler):
    """Handle file system events for scraper files"""
    
    def __init__(self):
        self.last_run = {}  # Track last run time for each file
        self.cooldown = 5   # Minimum seconds between runs for same file
    
    def on_modified(self, event):
        """Called when a file is modified"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only watch Python files in the scrapers directory
        if not (file_path.suffix == '.py' and 'scrapers' in str(file_path)):
            return
        
        # Check cooldown to avoid multiple runs
        current_time = time.time()
        if file_path.name in self.last_run:
            if current_time - self.last_run[file_path.name] < self.cooldown:
                return
        
        self.last_run[file_path.name] = current_time
        
        print(f"🔄 File changed: {file_path.name}")
        self.run_scraper(file_path)
    
    def run_scraper(self, file_path):
        """Run a specific scraper"""
        try:
            print(f"🚀 Running {file_path.name}...")
            
            # Run the scraper
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ {file_path.name} completed successfully")
                
                # Optionally run the full weekly scraper to combine all events
                print("🔄 Running full weekly scraper to combine events...")
                weekly_result = subprocess.run(
                    [sys.executable, 'weekly_scraper.py'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if weekly_result.returncode == 0:
                    print("✅ Weekly scraper completed - events combined!")
                    
                    # Optionally deploy the updated worker
                    print("🚀 Deploying updated worker...")
                    deploy_result = subprocess.run(
                        ['npx', 'wrangler', 'deploy', '--env=""'],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if deploy_result.returncode == 0:
                        print("✅ Worker deployed successfully!")
                        print("🌐 API updated at: https://nyc-academic-events-api.spergel-joshua.workers.dev")
                    else:
                        print("❌ Worker deployment failed")
                        
                else:
                    print("❌ Weekly scraper failed")
                    
            else:
                print(f"❌ {file_path.name} failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {file_path.name} timed out")
        except Exception as e:
            print(f"💥 Error running {file_path.name}: {e}")

def main():
    """Main file watcher function"""
    print("👀 NYC Academic Events - File Watcher")
    print("=" * 60)
    print("🔍 Watching for changes in scraper files...")
    print("💡 Modify any scraper file to automatically run it!")
    print("🔄 Press Ctrl+C to stop watching")
    print("=" * 60)
    
    # Get the scrapers directory
    scrapers_dir = Path('scrapers')
    if not scrapers_dir.exists():
        print("❌ Scrapers directory not found!")
        return
    
    # Set up the file watcher
    event_handler = ScraperFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(scrapers_dir), recursive=False)
    
    try:
        observer.start()
        print(f"✅ Watching {scrapers_dir} for changes...")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping file watcher...")
        observer.stop()
    
    observer.join()
    print("👋 File watcher stopped")

if __name__ == "__main__":
    main()
