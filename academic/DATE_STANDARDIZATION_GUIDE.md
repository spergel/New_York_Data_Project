# Date Standardization Migration Guide

## Overview
This guide helps migrate scrapers from manual date handling to standardized date utilities.

## Before (Manual Date Handling)
```python
# ❌ Manual date parsing
start_date = datetime.strptime(date_str, "%B %d, %Y")
end_date = start_date + timedelta(hours=2)

# ❌ Manual formatting
"start_date": start_date.isoformat(),
"end_date": end_date.isoformat(),
```

## After (Standardized Date Utilities)
```python
# ✅ Import standardized utilities
from date_utils import create_event_dates, standardize_datetime

# ✅ Use standardized functions
start_date, end_date = create_event_dates(date_str, time_str)

# ✅ Dates are already standardized
"start_date": start_date,  # Already ISO format
"end_date": end_date,      # Already ISO format
```

## Migration Steps

### 1. Import Date Utilities
```python
from date_utils import create_event_dates, create_multi_day_event_dates, standardize_datetime
```

### 2. Replace Manual Date Parsing
```python
# Old way
start_date = datetime.strptime(date_str, "%B %d, %Y")
if time_str:
    time_obj = datetime.strptime(time_str, "%I:%M %p").time()
    start_date = start_date.replace(hour=time_obj.hour, minute=time_obj.minute)

# New way
start_date, end_date = create_event_dates(date_str, time_str)
```

### 3. Replace Multi-day Date Parsing
```python
# Old way
if "–" in date_text:
    date_parts = date_text.split("–")
    start_date = parse_date(date_parts[0])
    end_date = parse_date(date_parts[1])

# New way
if "–" in date_text or "-" in date_text:
    date_parts = re.split(r'[–\-]', date_text)
    if len(date_parts) == 2:
        start_date, end_date = create_multi_day_event_dates(
            date_parts[0].strip(), 
            date_parts[1].strip(), 
            time_text
        )
```

### 4. Update Return Statements
```python
# Old way
"start_date": start_date.isoformat() if start_date else None,
"end_date": end_date.isoformat() if end_date else None,

# New way (dates are already standardized)
"start_date": start_date,
"end_date": end_date,
```

### 5. Update Metadata Timestamps
```python
# Old way
"scraped_at": datetime.now().isoformat(),

# New way
"scraped_at": standardize_datetime(datetime.now()),
```

## Benefits of Standardization

1. **Consistent Format**: All dates use ISO 8601 with UTC timezone
2. **Better Parsing**: Handles multiple date formats automatically
3. **Timezone Safety**: All dates are properly timezone-aware
4. **Easier Maintenance**: Centralized date logic
5. **Better Validation**: Built-in date validation and error handling

## Common Date Formats Supported

- "September 3, 2025"
- "Sep 3, 2025"
- "9/3/2025"
- "2025-09-03"
- "September 3" (assumes current year)
- "2:00 PM" or "14:00"
- "2:00 PM – 5:00 PM" (time ranges)

## Testing Your Migration

After migrating, test that:
1. Dates are in ISO 8601 format: `2025-09-03T14:00:00+00:00`
2. All dates have timezone information (`+00:00`)
3. End dates are properly calculated
4. Multi-day events work correctly
