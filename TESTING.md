# Scraper Testing Guide

This document explains how to test the event scrapers in this project.

## 🧪 Available Test Tools

### 1. Comprehensive Test Suite (`test_scrapers.py`)
Tests all scrapers and validates their output with detailed reporting.

**Usage:**
```bash
# Test all scrapers (using existing output files)
python test_scrapers.py

# Test with verbose output showing detailed issues
python test_scrapers.py -v

# Run scrapers before testing
python test_scrapers.py -r

# Test specific category only
python test_scrapers.py -c academic
python test_scrapers.py -c tech
python test_scrapers.py -c exercise

# Generate detailed JSON report
python test_scrapers.py --report
```

**Features:**
- ✅ Validates required fields (title, start_date, source)
- ✅ Checks date formats and ranges
- ✅ Warns about missing descriptions/locations
- ✅ Detects duplicate or invalid event IDs
- ✅ Color-coded output (green=pass, yellow=warning, red=fail)
- ✅ Generates detailed JSON reports

### 2. Quick Individual Scraper Test (`quick_test_scraper.py`)
Test a single scraper with detailed output validation.

**Usage:**
```bash
# Test a specific scraper
python quick_test_scraper.py academic/scrapers/columbia_general_events.py
python quick_test_scraper.py tech/scrapers/pioneer_works_scraper.py
python quick_test_scraper.py exercise/scrapers/bryant_park.py
```

**Features:**
- 🔄 Runs the scraper
- 📊 Validates output format
- 📋 Shows sample events
- 📈 Provides summary statistics
- ⚠️  Identifies common issues

### 3. Category-Specific Runners

#### Academic Scrapers
```bash
cd academic
python weekly_scraper.py
```
Runs all ~25 academic institution scrapers and combines results.

#### Tech Scrapers
```bash
cd tech
python run_all_scrapers.py
```
Runs all tech event scrapers and categorizes results.

#### Exercise/Community Scrapers
```bash
cd exercise
python run_all_scrapers.py
```
Runs all parks and community event scrapers.

### 4. Utility Tests
```bash
# Test event categorization
python test_event_utils.py

# Test API endpoints (requires Cloudflare worker running)
cd academic
python test_api_local.py
```

## 📊 Test Output Example

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SCRAPER TEST SUITE                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
Testing ACADEMIC Scrapers
================================================================================

  ✅ columbia_general_events: 100 events
  ✅ columbia_math_events: 2 events
  ⚠️  nyu_stern_events: 6/8 valid events
  ❌ juilliard_events: no_output

================================================================================
TEST SUMMARY
================================================================================

Overall Statistics:
  Total Scrapers: 25
  ✅ Passed: 20
  ⚠️  Warnings: 3
  ❌ Failed: 2

  Pass Rate: 80.0%
```

## 🔍 What Tests Validate

### Required Fields
- ✅ `title` - Event title/name
- ✅ `start_date` - Event start date in ISO format
- ✅ `source` - Source institution/venue name

### Optional but Important
- ⚠️ `description` - Event description (warns if missing/short)
- ⚠️ `location` - Event location (warns if missing)
- ⚠️ `end_date` - Event end date
- ⚠️ `url` - Event URL

### Data Quality Checks
- 📅 Date format validation (ISO 8601)
- 📅 Date range validation (not too far past/future)
- 📝 Description length check (minimum 20 chars)
- 🆔 Event ID validation (no empty IDs)

## 🐛 Common Issues and Fixes

### Issue: "No output file found"
**Cause:** Scraper didn't create output file
**Fix:** 
1. Run scraper manually to see errors
2. Check scraper saves to correct location
3. Verify file naming convention

### Issue: "Missing start_date"
**Cause:** Date parsing failed
**Fix:**
1. Check source website HTML structure
2. Update date parsing logic
3. See `academic/DATE_STANDARDIZATION_GUIDE.md`

### Issue: "Events too far in past"
**Cause:** Scraping past events
**Fix:**
1. Add date filtering to scraper
2. Use `event_filter.py` utilities
3. Filter events before saving

### Issue: "Invalid JSON"
**Cause:** Malformed JSON output
**Fix:**
1. Ensure proper JSON encoding
2. Use `json.dump()` with `ensure_ascii=False`
3. Check for special characters

## 📝 Writing Good Tests

When adding a new scraper:

1. **Follow output format:**
   ```json
   {
     "events": [
       {
         "id": "unique-id",
         "title": "Event Title",
         "start_date": "2025-10-15T18:00:00",
         "end_date": "2025-10-15T20:00:00",
         "location": "Location Name",
         "description": "Event description...",
         "url": "https://...",
         "source": "Institution Name"
       }
     ]
   }
   ```

2. **Test manually first:**
   ```bash
   python quick_test_scraper.py path/to/your_scraper.py
   ```

3. **Add to category runner:**
   - Academic: Add to `academic/weekly_scraper.py` scrapers list
   - Tech: Add to `tech/scrapers/calendar_configs.py` SCRAPERS
   - Exercise: Add to `exercise/run_all_scrapers.py` scrapers list

4. **Run full test suite:**
   ```bash
   python test_scrapers.py -v -c your_category
   ```

## 🚀 CI/CD Integration

To integrate with GitHub Actions or other CI:

```yaml
- name: Test Scrapers
  run: |
    python test_scrapers.py --report
    
- name: Upload Test Report
  uses: actions/upload-artifact@v3
  with:
    name: scraper-test-report
    path: scraper_test_report.json
```

## 📚 Related Documentation

- `academic/DATE_STANDARDIZATION_GUIDE.md` - Date parsing standards
- `academic/SCRAPER_TODO.md` - Scraper improvement tasks
- `tech/TODO.md` - Tech scraper tasks
- `exercise/scrapers/TODO.md` - Exercise scraper tasks

## 🛠️ Troubleshooting

### Tests failing after scraper changes?
1. Check if output format changed
2. Verify date format is ISO 8601
3. Ensure all required fields present

### Need to debug a specific scraper?
```bash
# Run with Python debugger
python -m pdb path/to/scraper.py

# Or add print statements and run directly
python path/to/scraper.py
```

### Want to test scrapers in parallel?
```bash
# Run all categories at once (in separate terminals)
python test_scrapers.py -c academic &
python test_scrapers.py -c tech &
python test_scrapers.py -c exercise &
wait
```

---

**Questions or Issues?** Check the scraper-specific debug files (`*_debug.json`) for raw output, or examine the logs in `scraper.log` files.





