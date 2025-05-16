@echo off
echo Running all scrapers and categorizing events...

:: Navigate to the project root directory
cd /d "%~dp0"

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Run the script
echo Running main script...
python -m tech.run_all

echo.
echo Done! Check tech\data directory for results.
pause 