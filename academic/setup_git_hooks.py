#!/usr/bin/env python3
"""
Setup Git Hooks for Automatic Scraping
This script sets up Git hooks that automatically run scrapers when code is updated

TESTING: This comment was added to test the automatic Git hooks!
TESTING 2: Testing complete automation with Cloudflare account fix!
FINAL TEST: Testing complete end-to-end automation with working scrapers!
"""

import os
import sys
from pathlib import Path

def create_pre_commit_hook():
    """Create a pre-commit hook that runs scrapers before committing"""
    hook_content = '''#!/bin/bash
# Pre-commit hook: Run scrapers before committing
echo "Pre-commit: Running scrapers to ensure fresh data..."

# Change to the academic directory
cd "$(dirname "$0")/.."

# Run the weekly scraper to get fresh data
python academic/weekly_scraper.py

# Check if scraping was successful
if [ $? -eq 0 ]; then
    echo "Scraping completed successfully - proceeding with commit"
    exit 0
else
    echo "Scraping failed - commit aborted"
    echo "Fix the scraping issues before committing"
    exit 1
fi
'''
    
    return hook_content

def create_post_commit_hook():
    """Create a post-commit hook that deploys after committing"""
    hook_content = '''#!/bin/bash
# Post-commit hook: Deploy updated API after committing
echo "Post-commit: Deploying updated API..."

# Change to the academic directory
cd "$(dirname "$0")/.."

# Deploy the updated worker
cd academic
npx wrangler deploy --env=""

if [ $? -eq 0 ]; then
    echo "API deployed successfully!"
    echo "Available at: https://nyc-academic-events-api.spergel-joshua.workers.dev"
else
    echo "API deployment failed"
    echo "Check the deployment logs"
fi
'''
    
    return hook_content

def create_pre_push_hook():
    """Create a pre-push hook that ensures data is fresh before pushing"""
    hook_content = '''#!/bin/bash
# Pre-push hook: Ensure data is fresh before pushing to GitHub
echo "Pre-push: Checking data freshness..."

# Change to the academic directory
cd "$(dirname "$0")/.."

# Check if we have recent data (within last hour)
if [ -f "academic/scraped_events.json" ]; then
    # Get file modification time
    file_time=$(stat -c %Y "academic/scraped_events.json")
    current_time=$(date +%s)
    time_diff=$((current_time - file_time))
    
    # If data is older than 1 hour, run scrapers
    if [ $time_diff -gt 3600 ]; then
        echo "Data is older than 1 hour, running scrapers..."
        python academic/weekly_scraper.py
        
        if [ $? -eq 0 ]; then
            echo "Fresh data obtained - proceeding with push"
            exit 0
        else
            echo "Failed to get fresh data - push aborted"
            exit 1
        fi
    else
        echo "Data is fresh (${time_diff}s old) - proceeding with push"
        exit 0
    fi
else
    echo "No data file found, running scrapers..."
    python academic/weekly_scraper.py
    
    if [ $? -eq 0 ]; then
        echo "Data created - proceeding with push"
        exit 0
    else
        echo "Failed to create data - push aborted"
        exit 1
    fi
fi
'''
    
    return hook_content

def setup_git_hooks():
    """Set up all Git hooks"""
    print("Setting up Git Hooks for Automatic Scraping")
    print("=" * 60)
    
    # Get the Git hooks directory
    git_dir = Path('.git')
    if not git_dir.exists():
        print("Not in a Git repository!")
        print("Run 'git init' first, or navigate to the repository root")
        return False
    
    hooks_dir = git_dir / 'hooks'
    if not hooks_dir.exists():
        hooks_dir.mkdir(parents=True)
    
    hooks_created = []
    
    # Create pre-commit hook
    pre_commit_file = hooks_dir / 'pre-commit'
    with open(pre_commit_file, 'w', encoding='utf-8') as f:
        f.write(create_pre_commit_hook())
    os.chmod(pre_commit_file, 0o755)  # Make executable
    hooks_created.append('pre-commit')
    print("Created pre-commit hook (runs scrapers before commit)")
    
    # Create post-commit hook
    post_commit_file = hooks_dir / 'post-commit'
    with open(post_commit_file, 'w', encoding='utf-8') as f:
        f.write(create_post_commit_hook())
    os.chmod(post_commit_file, 0o755)  # Make executable
    hooks_created.append('post-commit')
    print("Created post-commit hook (deploys API after commit)")
    
    # Create pre-push hook
    pre_push_file = hooks_dir / 'pre-push'
    with open(pre_push_file, 'w', encoding='utf-8') as f:
        f.write(create_pre_push_hook())
    os.chmod(pre_push_file, 0o755)  # Make executable
    hooks_created.append('pre-push')
    print("Created pre-push hook (ensures fresh data before push)")
    
    print(f"Successfully created {len(hooks_created)} Git hooks!")
    print("=" * 60)
    print("What happens now:")
    print("1. Pre-commit: Runs scrapers before every commit")
    print("2. Post-commit: Deploys API after every commit")
    print("3. Pre-push: Ensures fresh data before pushing to GitHub")
    print("\nYour workflow is now:")
    print("git add . -> git commit -> git push")
    print("    |           |           |")
    print("(scrapers)   (deploy)    (verify)")
    
    return True

def main():
    """Main setup function"""
    print("NYC Academic Events - Git Hooks Setup")
    print("=" * 60)
    
    if setup_git_hooks():
        print("\nNext time you commit, scrapers will run automatically!")
        print("Try: git add . && git commit -m 'Update scrapers'")
    else:
        print("\nSetup failed. Check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
