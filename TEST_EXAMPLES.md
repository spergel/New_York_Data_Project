# Scraper Testing Examples

This guide shows practical examples of how to test your scrapers.

## Quick Start

### 1. Test All Scrapers (Recommended First Step)
```bash
# Test all scrapers using existing output files
python test_scrapers.py

# See detailed issues for each scraper
python test_scrapers.py -v

# Generate a detailed JSON report
python test_scrapers.py --report
```

### 2. Test Specific Category
```bash
# Test only academic scrapers
python test_scrapers.py -c academic

# Test only tech scrapers
python test_scrapers.py -c tech

# Test only exercise/community scrapers
python test_scrapers.py -c exercise
```

### 3. Run Scrapers Then Test
```bash
# Run all scrapers and then test them
python test_scrapers.py -r

# Run and test with verbose output
python test_scrapers.py -r -v
```

### 4. Test Individual Scraper
```bash
# Test a specific scraper with detailed validation
python quick_test_scraper.py academic/scrapers/columbia_general_events.py
python quick_test_scraper.py tech/scrapers/pioneer_works_scraper.py
```

## Category-Specific Testing

### Academic Scrapers
```bash
cd academic
python weekly_scraper.py
```
This will:
- Run all ~25 academic scrapers
- Combine all events into one file
- Convert for Cloudflare worker
- Show success/failure for each

### Tech Scrapers
```bash
cd tech
python run_all_scrapers.py
```
This will:
- Run all tech event scrapers
- Categorize events
- Save to data files

### Exercise/Community Scrapers
```bash
cd exercise
python run_all_scrapers.py
```
This will:
- Run parks and community scrapers
- Process event tags
- Save categorized events

## Understanding Test Results

### Success (Green/[PASS])
```
[PASS] columbia_general_events: 100 events
```
All events have required fields and valid dates.

### Warning (Yellow/[WARN])
```
[WARN] nyu_stern_events: 6/8 valid events
```
Most events are valid but some have minor issues (missing descriptions, etc.)

### Failure (Red/[FAIL])
```
[FAIL] cooper_union_events: failed
```
Events missing required fields or have invalid data.

### Common Issues

#### Missing title/name
```
Event 1: Missing required field: title/name
```
**Fix:** Ensure scraper sets either `title` or `name` field

#### Missing start_date
```
Event 1: Missing required field: start_date
```
**Fix:** Check date parsing logic, ensure ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)

#### Events in the past
```
Event is more than 1 week in the past: 2025-09-15
```
**Fix:** Add date filtering to scraper to only get future events

#### Missing description
```
Missing description (warning)
```
**Fix:** Extract description from event page (warning only, won't fail)

## Example Workflow

### Testing a New Scraper

1. **Write the scraper** (e.g., `new_institution_events.py`)

2. **Test it manually:**
   ```bash
   python quick_test_scraper.py academic/scrapers/new_institution_events.py
   ```

3. **Review the output:**
   ```
   [RUN] Running new_institution_events.py...
   [PASS] Scraper ran successfully
   
   [VALIDATE] Validating Output
   [INFO] Output file: academic/scrapers/new_institution_events_debug.json
   [INFO] Found 25 events
   
   [SAMPLE] Sample Events (first 3)
   Event 1:
     Title: Guest Lecture on AI Ethics
     Date: 2025-10-15T18:00:00
     Location: Main Auditorium
     Source: New Institution
     URL: https://...
   ```

4. **Add to category runner** (e.g., `academic/weekly_scraper.py`)

5. **Run full category test:**
   ```bash
   python test_scrapers.py -c academic
   ```

### Debugging a Failing Scraper

1. **Identify the issue:**
   ```bash
   python test_scrapers.py -v -c academic | grep -A 3 "failing_scraper"
   ```

2. **Check the debug file:**
   ```bash
   # On Windows
   type academic\failing_scraper_debug.json | more
   
   # On Linux/Mac
   cat academic/failing_scraper_debug.json | jq '.[0]'
   ```

3. **Test individual scraper:**
   ```bash
   python quick_test_scraper.py academic/scrapers/failing_scraper.py
   ```

4. **Fix issues and retest**

## Expected Output Format

All scrapers should output events in this format:

```json
{
  "events": [
    {
      "id": "unique-event-id",
      "title": "Event Title",        // or "name"
      "start_date": "2025-10-15T18:00:00",  // ISO format
      "end_date": "2025-10-15T20:00:00",
      "location": "Event Location",
      "description": "Event description...",
      "url": "https://example.com/event",
      "source": "Institution/Venue Name"
    }
  ]
}
```

## Continuous Testing

### Run tests before committing:
```bash
# Quick validation of all existing outputs
python test_scrapers.py

# Full test with fresh scraping (takes longer)
python test_scrapers.py -r --report
```

### Check the report:
```bash
cat scraper_test_report.json
```

The report includes:
- Timestamp of test run
- Statistics (total, passed, failed, warnings)
- Detailed results for each scraper
- Sample events
- Specific issues found

## Performance Tips

1. **Test without running scrapers first** (faster):
   ```bash
   python test_scrapers.py
   ```

2. **Run scrapers only when needed** (slower but fresh data):
   ```bash
   python test_scrapers.py -r
   ```

3. **Test one category at a time**:
   ```bash
   python test_scrapers.py -c academic  # Fast
   python test_scrapers.py -c tech      # Fast
   python test_scrapers.py -c exercise  # Fast
   ```

4. **For development, use quick test**:
   ```bash
   python quick_test_scraper.py path/to/your_scraper.py
   ```

## Troubleshooting

### "No output file found"
- The scraper hasn't been run yet, or
- It's saving to an unexpected location
- Run the scraper first: `python academic/scrapers/scraper_name.py`

### "Invalid JSON"
- Check the output file for syntax errors
- Ensure proper UTF-8 encoding
- Use `json.dump()` not manual string building

### "Timeout after 180s"
- Scraper is taking too long
- May be blocked by website
- Check for infinite loops

### Tests failing on Windows
- All emoji characters have been replaced with [TAGS] etc.
- Colors should work in PowerShell and Command Prompt
- If colors don't show, it's cosmetic only

## Advanced Usage

### Custom Validation

Edit `test_scrapers.py` to add custom validation rules:

```python
# Example: Check for specific venue
if event.get('location') == 'Unknown':
    issues.append("Location not properly parsed")
```

### Filtering Test Results

```bash
# Show only failures
python test_scrapers.py -v | grep "\[FAIL\]"

# Count by status
python test_scrapers.py | grep -c "\[PASS\]"
python test_scrapers.py | grep -c "\[FAIL\]"
```

### Automated Testing

Create a GitHub Action or cron job:

```yaml
name: Test Scrapers
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: python test_scrapers.py --report
```

---

## Summary

The testing suite provides:

✅ **Comprehensive validation** - All scrapers tested automatically  
✅ **Detailed reporting** - See exactly what's wrong with each scraper  
✅ **Flexible testing** - Test all, by category, or individual scrapers  
✅ **Color-coded output** - Quickly see what's working  
✅ **JSON reports** - Machine-readable results for CI/CD  
✅ **Quick iteration** - Test individual scrapers during development  

Start with `python test_scrapers.py` and go from there!






