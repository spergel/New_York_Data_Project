import schedule
import time
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_scraper():
    try:
        logging.info("Starting scraper...")
        subprocess.run(['python', 'main.py'], check=True)
        logging.info("Scraper completed successfully")
    except Exception as e:
        logging.error(f"Error running scraper: {str(e)}")

def main():
    # Schedule the job to run every Sunday at 1 AM
    schedule.every().sunday.at("01:00").do(run_scraper)
    
    # Log that the scheduler has started
    logging.info("Scheduler started. Will run every Sunday at 1 AM.")
    print("Scheduler is running. Check scheduler.log for details.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()