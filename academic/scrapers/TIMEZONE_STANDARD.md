# Timezone Standardization

## ALL EVENT TIMES ARE IN NYC TIMEZONE (America/New_York)

All scrapers must store event times in **NYC timezone** (America/New_York). This ensures:
- Consistent display on the website
- No timezone confusion
- Proper handling of EST/EDT automatically

## How to Use

### 1. Creating Datetimes

**Use `create_nyc_datetime()` for creating new datetimes:**
```python
from date_utils import create_nyc_datetime

# Create a datetime in NYC timezone
dt = create_nyc_datetime(2025, 12, 3, 19, 0)  # Dec 3, 2025 at 7:00 PM NYC time
```

**Or use `parse_flexible_date()` which returns NYC timezone-aware datetimes:**
```python
from date_utils import parse_flexible_date

date_obj = parse_flexible_date("December 3, 2025")  # Already in NYC timezone
```

### 2. Converting Existing Datetimes

**Use `to_nyc_datetime()` to convert any datetime to NYC timezone:**
```python
from date_utils import to_nyc_datetime

# Convert UTC or any timezone to NYC
nyc_dt = to_nyc_datetime(some_datetime)
```

**Use `standardize_datetime()` to convert to ISO string in NYC timezone:**
```python
from date_utils import standardize_datetime

# Returns ISO string like "2025-12-03T19:00:00-05:00" (NYC time)
iso_string = standardize_datetime(datetime_obj)
```

### 3. Creating Event Dates

**Use `create_event_dates()` for start/end dates:**
```python
from date_utils import create_event_dates

start_date, end_date = create_event_dates(
    "December 3, 2025",
    "7:00 PM - 9:00 PM",
    duration_hours=2
)
# Both returned as ISO strings in NYC timezone
```

### 4. Display Formatting

**Use `format_display_date()` for display (already converts to NYC time):**
```python
from date_utils import format_display_date

display = format_display_date("2025-12-03T19:00:00-05:00")
# Returns: "December 3, 2025 at 7:00 PM" (NYC time)
```

## What Changed

1. **`standardize_datetime()`** - Now stores in NYC timezone (not UTC)
2. **`parse_flexible_date()`** - Returns NYC timezone-aware datetimes
3. **`create_event_dates()`** - Returns dates in NYC timezone
4. **All display functions** - Convert to NYC time for display

## Scrapers Updated

- ✅ `date_utils.py` - Core functions standardized
- ✅ `nyu_steinhardt_events.py` - Uses NYC timezone
- ✅ `nyu_steinhardt_music_events.py` - Uses NYC timezone
- ✅ `columbia_general_events.py` - Uses NYC timezone
- ✅ `juilliard_events.py` - Already using NYC timezone
- ✅ `jtsa_events.py` - Already using NYC timezone
- ✅ `cooper_union_events.py` - Already using NYC timezone
- ✅ `nypl_events.py` - Already using NYC timezone

## Important Notes

- **NEVER** use `timezone.utc` or convert to UTC for storage
- **NEVER** use `timezone(timedelta(hours=-5))` - use `NY_TZ` instead
- **ALWAYS** use `standardize_datetime()` before storing dates
- **ALWAYS** ensure datetimes have timezone info before calling `.isoformat()`

## Example: Complete Event Date Handling

```python
from date_utils import create_nyc_datetime, standardize_datetime, timedelta

# Parse date from source (assume it's in NYC time)
year, month, day = 2025, 12, 3
hour, minute = 19, 0

# Create datetime in NYC timezone
start_dt = create_nyc_datetime(year, month, day, hour, minute)
end_dt = start_dt + timedelta(hours=2)

# Standardize to ISO strings
start_date = standardize_datetime(start_dt)
end_date = standardize_datetime(end_dt)

# Store in event dict
event = {
    "start_date": start_date,  # "2025-12-03T19:00:00-05:00"
    "end_date": end_date        # "2025-12-03T21:00:00-05:00"
}
```

