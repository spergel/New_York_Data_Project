#!/usr/bin/env python3
"""
Run All Scrapers and Combine Events

This script runs all scrapers from different domains (academic, tech, exercise)
and then combines their results into a unified dataset.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import importlib.util
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('run_all_and_combine.log'), logging.StreamHandler()]
)

def run_script(script_path: str, cwd: str = None):
    """Run a Python script in a subprocess"""
    try:
        logging.info(f"Running script: {script_path}")
        
        # Use the current working directory if not specified
        if cwd is None:
            cwd = os.path.dirname(script_path)
        
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Log the output
        if result.stdout:
            logging.info(f"Output from {script_path}:\n{result.stdout}")
        
        # Log any errors
        if result.stderr:
            logging.error(f"Errors from {script_path}:\n{result.stderr}")
        
        # Check if the script ran successfully
        if result.returncode != 0:
            logging.error(f"Script {script_path} failed with return code {result.returncode}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error running script {script_path}: {e}")
        return False

def run_module(module_path: str, function_name: str = "main"):
    """Import and run a Python module's function"""
    try:
        logging.info(f"Running module: {module_path} - function: {function_name}")
        
        # Import the module
        spec = importlib.util.spec_from_file_location("module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the specified function
        if hasattr(module, function_name):
            getattr(module, function_name)()
            return True
        else:
            logging.error(f"Function {function_name} not found in module {module_path}")
            return False
    except Exception as e:
        logging.error(f"Error running module {module_path}: {e}")
        return False

def main():
    """Main function to run all scrapers and combine events"""
    start_time = time.time()
    logging.info("Starting the process to run all scrapers and combine events")
    
    # Define paths to the main scripts
    academic_script = os.path.join("academic", "main.py")
    tech_script = os.path.join("tech", "run_all_scrapers.py")
    exercise_script = os.path.join("exercise", "run_all_scrapers.py")
    combine_script = "combine_events.py"
    
    # Run academic scrapers
    if os.path.exists(academic_script):
        logging.info("Running academic scrapers...")
        success = run_script(academic_script)
        if not success:
            logging.warning("Academic scrapers did not complete successfully")
    else:
        logging.warning(f"Academic script not found: {academic_script}")
    
    # Run tech scrapers
    if os.path.exists(tech_script):
        logging.info("Running tech scrapers...")
        success = run_script(tech_script)
        if not success:
            logging.warning("Tech scrapers did not complete successfully")
    else:
        logging.warning(f"Tech script not found: {tech_script}")
    
    # Run exercise scrapers
    if os.path.exists(exercise_script):
        logging.info("Running exercise scrapers...")
        success = run_script(exercise_script)
        if not success:
            logging.warning("Exercise scrapers did not complete successfully")
    else:
        logging.warning(f"Exercise script not found: {exercise_script}")
    
    # Combine all events
    logging.info("Combining events from all sources...")
    if os.path.exists(combine_script):
        success = run_script(combine_script)
        if not success:
            logging.error("Failed to combine events")
        else:
            logging.info("Successfully combined events from all sources")
    else:
        logging.error(f"Combine script not found: {combine_script}")
    
    # Calculate and log the total execution time
    end_time = time.time()
    execution_time = end_time - start_time
    logging.info(f"Total execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    main() 