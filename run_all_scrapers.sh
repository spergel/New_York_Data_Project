#!/bin/bash

# Navigate to project root directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the script
echo "Running all scrapers and categorizing events..."
python -m tech.run_all

# Print completion message
echo "Done! Check tech/data directory for results." 