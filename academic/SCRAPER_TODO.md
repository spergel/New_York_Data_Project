# Academic Events Scraper TODO List

## 🎯 Current Status
- **Total Working Scrapers**: 22
- **Total Events Collected**: 299
- **Date Standardization**: 4/26 scrapers completed (15%)
- **Last Updated**: 2025-09-03

## ✅ Working Scrapers (22 total)

### High Quality Data
- **columbia_classics_events.py** - ✅ 23 events (good data)
- **columbia_general_events.py** - ✅ 100 → 45 events (filtered, good data)
- **columbia_math_events.py** - ✅ 2 events (good data)
- **cornell_tech_events.py** - ✅ 2 events (good data)
- **fordham_events.py** - ✅ 6 events (Google Calendar, good data)
- **gallatin_events.py** - ✅ 21 → 20 events (filtered, good data)
- **isaw_events.py** - ✅ 5 → 4 events (filtered, good data)
- **jtsa_events.py** - ✅ 10 → 9 events (filtered, good data)
- **juilliard_events.py** - ✅ 20 events (good data)
- **miller_events.py** - ✅ 57 events (good data)
- **new_school_events.py** - ✅ 80 → 56 events (filtered, good data)
- **nyu_api_events.py** - ✅ 44 → 34 events (filtered, good data)
- **nyu_cims_events.py** - ✅ 60 events (good data)
- **nyu_education_events.py** - ✅ 2 events (good data)
- **nyu_engineering.py** - ✅ 40 → 13 events (filtered, good data)
- **nyu_law_events.py** - ✅ 9 events (good data)
- **nyu_medicine_events.py** - ✅ 2 events (good data)
- **simons_foundation_events.py** - ✅ 9 events (good data, recently fixed)

### Scrapers with Issues (Still Working but Need Fixing)

#### 🚨 LOW PRIORITY - POOR EVENT SOURCES
These scrapers are working but the institutions don't have quality events worth fixing:

- **nyu_stern_events.py** - ⚠️ 8 events (SKIP - institution has poor events)
  - **Status**: Working but getting crap data because NYU Stern doesn't have real events
  - **Decision**: Skip fixing - not worth the effort

- **cooper_union_events.py** - ⚠️ 2 events (SKIP - institution has poor events)  
  - **Status**: Working but getting crap data because Cooper Union doesn't have real events
  - **Decision**: Skip fixing - not worth the effort

#### ✅ RECENTLY FIXED
- **pratt_events.py** - ✅ 14 events (COMPLETELY REWRITTEN - now getting real data!)
  - **Previous Issues**: NO start dates, NO end dates, NO descriptions (just event names)
  - **Current Status**: Getting proper dates, times, descriptions, URLs, and detailed info
  - **Data Quality**: Excellent - real events with full details
  - **Improvement**: 6 → 14 events (133% increase!)

#### ⚠️ NEEDS INVESTIGATION
- **sof_heyman_events.py** - ⚠️ Status unclear, needs testing

## ❌ Broken Scrapers (0 total)
All scrapers are currently running successfully.

## 🔧 TODO: Fix Scrapers Getting Crap Data

### Priority 1: Complete Rewrites Needed
*None currently - all major scrapers are working well!*

### 🚫 SKIPPED - Not Worth Fixing
1. **nyu_stern_events.py** - Institution has poor events
   - **Decision**: Skip - not worth the effort
   - **Reason**: NYU Stern doesn't have quality academic events

2. **cooper_union_events.py** - Institution has poor events  
   - **Decision**: Skip - not worth the effort
   - **Reason**: Cooper Union doesn't have quality academic events

### ✅ COMPLETED
3. **pratt_events.py** - COMPLETELY REWRITTEN ✅
   - [x] Investigate actual Pratt events page structure
   - [x] Rewrite to get real dates, descriptions, and more events
   - [x] Add proper event filtering
   - **Result**: Now getting 6 real events with full details!



### Priority 2: Investigate and Fix
4. **sof_heyman_events.py** - Status unclear
   - [ ] Test if it's actually working
   - [ ] Check data quality
   - [ ] Fix any issues found

## 📅 Date Standardization Priority

### High Priority (Most Manual Date Parsing)
- **gallatin_events.py** - 8 manual date parsing calls
- **cornell_tech_events.py** - 3 manual date parsing calls  
- **sof_heyman_events.py** - 3 manual date parsing calls
- **nyu_cims_events.py** - 2 manual date parsing calls + 1 naive datetime
- **nyu_engineering.py** - 2 manual date parsing calls

### Medium Priority
- **columbia_general_events.py** - 2 manual date parsing calls
- **nyu_cims_events.py** - 2 manual date parsing calls
- **pratt_events.py** - 4 naive datetime objects (already migrated)

### Low Priority (Minimal Issues)
- All other scrapers with 1 manual date parsing call

## 🚀 TODO: Add New Scrapers

### Potential New Sources
- **brooklyn_college_events.py** - No output, needs investigation
- **columbia_history_events.py** - No output, needs investigation  
- **columbia_law_events.py** - Deleted (was getting 0 events)
- **columbia_religion_events.py** - Deleted (was getting 0 events)
- **columbia_social_difference_events.py** - No output, needs investigation
- **hunter_college_events.py** - Deleted (was getting 0 events)
- **stjohns_events.py** - No output, needs investigation

## 📊 Data Quality Improvements

### Event Filtering
- [x] Basic event filtering implemented (removes fairs, office hours, etc.)
- [x] Date filtering implemented (removes past events)
- [ ] Improve filter accuracy
- [ ] Add more sophisticated filtering rules

### Data Standardization
- [x] Basic event structure standardized
- [x] Date standardization utilities created (`date_utils.py`)
- [x] Pratt scraper migrated to standardized dates
- [ ] Migrate remaining 22 scrapers to use standardized date utilities
- [ ] Standardize venue information
- [ ] Add missing metadata fields

## 🧪 Testing and Validation

### Current Testing
- [x] Individual scraper testing
- [x] Big scraper integration testing
- [x] Event filtering validation
- [ ] Data quality validation
- [ ] Frontend integration testing

### Validation Needed
- [ ] Verify event dates are accurate
- [ ] Check for duplicate events
- [ ] Validate event descriptions
- [ ] Test frontend with real data

## 🚀 Deployment and Infrastructure

### Current Status
- [x] Cloudflare worker deployed
- [x] API endpoints working
- [x] Automatic deployment from weekly scraper
- [ ] Monitor API performance
- [ ] Set up error monitoring

### Improvements Needed
- [ ] Better error handling in scrapers
- [ ] Logging and monitoring
- [ ] Automatic retry for failed scrapers
- [ ] Performance optimization

## 📈 Success Metrics

### Current Performance
- **Total Events**: 299
- **Working Scrapers**: 22/22 (100%)
- **Data Quality**: Mixed (some excellent, some poor)

### Goals
- **Target Events**: 500+ high-quality events
- **Working Scrapers**: 25+ scrapers
- **Data Quality**: 90%+ events with complete information
- **Coverage**: All major NYC academic institutions

## 🔄 Weekly Process

### Current Workflow
1. ✅ Run all 22 scrapers
2. ✅ Combine events (299 total)
3. ✅ Apply filtering
4. ✅ Convert for Cloudflare worker
5. ✅ Deploy to Cloudflare
6. ✅ Generate updated worker code

### Improvements Needed
- [ ] Better error reporting
- [ ] Performance monitoring
- [ ] Automatic quality checks
- [ ] Notification system for failures

---

**Last Updated**: 2025-09-03  
**Next Review**: Weekly after scraper runs  
**Priority**: Fix crap data scrapers first, then add new sources
