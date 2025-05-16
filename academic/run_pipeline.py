#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import subprocess
from datetime import datetime

# Configure logging
log_dir = "academic/logs"
log_file = os.path.join(log_dir, f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('event_pipeline')

def run_command(command):
    """Run a system command and log the output."""
    logger.info(f"Running command: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    
    stdout, stderr = process.communicate()
    
    if stdout:
        for line in stdout.split('\n'):
            if line.strip():
                logger.info(f"STDOUT: {line}")
                
    if stderr:
        for line in stderr.split('\n'):
            if line.strip():
                logger.error(f"STDERR: {line}")
                
    return process.returncode

def main():
    """Main entry point for the pipeline."""
    try:
        # Set up command line arguments
        parser = argparse.ArgumentParser(description='Run the complete academic event processing pipeline')
        parser.add_argument('--output-dir', default='academic/data', 
                           help='Directory for output files')
        parser.add_argument('--events-path', default='academic/data/events.json', 
                           help='Path to input events file')
        parser.add_argument('--communities-path', default='academic/data/communities.json', 
                           help='Path to communities file')
        parser.add_argument('--verbose', '-v', action='store_true', 
                           help='Enable verbose output')
        parser.add_argument('--skip-tech', action='store_true',
                           help='Skip tech events processing')
        parser.add_argument('--skip-institution', action='store_true',
                           help='Skip institution events processing')
        parser.add_argument('--skip-nymas', action='store_true',
                           help='Skip NYMAS events processing')
        parser.add_argument('--sample', '-s', action='store_true',
                           help='Use sample events when possible instead of scraping')
        args = parser.parse_args()
        
        # Configure more verbose logging if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            verbose_flag = "--verbose"
        else:
            verbose_flag = ""

        # Configure sample flag
        if args.sample:
            sample_flag = "--sample"
        else:
            sample_flag = ""
        
        # Make sure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Define output paths
        tech_events_path = os.path.join(args.output_dir, "tech_science_events.json")
        institution_events_path = os.path.join(args.output_dir, "institution_events.json")
        nymas_events_path = os.path.join(args.output_dir, "nymas_events.json")
        combined_events_path = os.path.join(args.output_dir, "combined_events.json")
        
        # Step 1: Run get_tech_events.py (if not skipped)
        if not args.skip_tech:
            logger.info("Step 1: Extracting tech and science events")
            cmd = f"python academic/get_tech_events.py --output {tech_events_path} --communities-path {args.communities_path} {verbose_flag}"
            returncode = run_command(cmd)
            
            if returncode != 0:
                logger.error("Step 1 failed. Pipeline stopped.")
                return returncode
        else:
            logger.info("Skipping tech events processing as requested")
        
        # Step 2: Run get_specific_institution_events.py (if not skipped)
        if not args.skip_institution:
            logger.info("Step 2: Extracting institution-specific events")
            cmd = f"python academic/get_specific_institution_events.py --output {institution_events_path} --events-path {args.events_path} --communities-path {args.communities_path} {sample_flag} {verbose_flag}"
            returncode = run_command(cmd)
            
            if returncode != 0:
                logger.error("Step 2 failed. Pipeline stopped.")
                return returncode
        else:
            logger.info("Skipping institution events processing as requested")
        
        # Step 3: Run get_nymas_events.py (if not skipped)
        if not args.skip_nymas:
            logger.info("Step 3: Extracting NYMAS events")
            cmd = f"python academic/get_nymas_events.py --output {nymas_events_path} {sample_flag} {verbose_flag}"
            returncode = run_command(cmd)
            
            if returncode != 0:
                logger.error("Step 3 failed. Pipeline stopped.")
                return returncode
        else:
            logger.info("Skipping NYMAS events processing as requested")
        
        # Step 4: Run combine_events.py
        logger.info("Step 4: Combining events from all sources")
        
        # Build the command based on available data
        combine_cmd = f"python academic/combine_events.py --output {combined_events_path} {verbose_flag}"
        
        # Add paths to sources that should be included
        if not args.skip_tech and os.path.exists(tech_events_path):
            combine_cmd += f" --tech-events {tech_events_path}"
            
        if not args.skip_institution and os.path.exists(institution_events_path):
            combine_cmd += f" --institution-events {institution_events_path}"
            
        if not args.skip_nymas and os.path.exists(nymas_events_path):
            combine_cmd += f" --nymas-events {nymas_events_path}"
        
        returncode = run_command(combine_cmd)
        
        if returncode != 0:
            logger.error("Step 4 failed. Pipeline stopped.")
            return returncode
        
        logger.info(f"Pipeline completed successfully. Final output: {combined_events_path}")
        return 0
    
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 