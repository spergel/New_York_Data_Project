@echo off
REM Test all scrapers with detailed output
echo ====================================
echo Testing All Scrapers (Verbose Mode)
echo ====================================
python test_scrapers.py -v --report
echo.
echo Report saved to scraper_test_report.json
pause






