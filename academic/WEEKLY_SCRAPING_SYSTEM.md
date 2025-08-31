# 🚀 NYC Academic Events - Weekly Scraping System

This system automatically scrapes academic events from multiple NYC institutions and deploys them to a Cloudflare Worker API every week.

## 🎯 **What We've Built**

### **✅ Fixed Pagination & Sorting**
- **Proper pagination** with `page` and `per_page` parameters
- **Multiple sorting options**: date, name, institution, ID
- **Advanced filtering** by institution, date range, search terms
- **Real-time data** from 603+ academic events

### **✅ Automated Weekly Updates**
- **Automatic scraping** every Sunday at 2 AM UTC
- **Data conversion** and cleaning for optimal API performance
- **Automatic deployment** to Cloudflare Workers
- **GitHub Actions** workflow for reliability

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scrapers      │    │  Data Pipeline   │    │ Cloudflare API  │
│                 │    │                  │    │                 │
│ • Columbia      │───▶│ • Combine Events │───▶│ • 603 Events    │
│ • NYU           │    │ • Convert Format │    │ • Pagination    │
│ • CUNY          │    │ • Clean Data     │    │ • Sorting       │
│ • Gallatin      │    │ • Validate       │    │ • Filtering     │
│ • ISAWA         │    │                  │    │ • Search        │
│ • JTSA          │    │                  │    │                 │
│ • CIMS          │    │                  │    │                 │
│ • Cornell Tech  │    │                  │    │                 │
│ • Simons        │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 **File Structure**

```
academic/
├── cloudflare-worker.js          # Main API worker (603 events)
├── weekly_scraper.py             # Automated scraping orchestrator
├── convert_events_for_worker.py  # Convert scraped data to worker format
├── update_worker_with_real_events.py  # Update worker with real events
├── scraped_events.json           # Raw scraped data (603 events)
├── worker_events.json            # Cleaned data for worker
├── .github/workflows/
│   └── weekly-scraping.yml      # GitHub Actions automation
└── scrapers/                     # Individual institution scrapers
    ├── columbia_scraper.py
    ├── nyu_scraper.py
    ├── cuny_scraper.py
    └── ... (other scrapers)
```

## 🔄 **Weekly Scraping Process**

### **1. Automatic Execution (Every Sunday 2 AM UTC)**
```bash
# GitHub Actions automatically runs:
python weekly_scraper.py
```

### **2. What Happens Each Week**
1. **Run all scrapers** for each institution
2. **Combine events** from all sources
3. **Remove duplicates** based on event IDs
4. **Convert format** for Cloudflare worker
5. **Update worker code** with new events
6. **Deploy to Cloudflare** automatically
7. **Send notification** with results

### **3. Manual Execution**
```bash
cd academic
python weekly_scraper.py
```

## 🛠️ **API Endpoints**

### **Base URL**
```
https://nyc-academic-events-api.spergel-joshua.workers.dev
```

### **Available Endpoints**
- `GET /api/events` - Get all events with pagination & filtering
- `GET /api/events/{event_id}` - Get specific event
- `GET /api/institutions` - Get all institutions with event counts
- `GET /api/stats` - Get API statistics and event counts

### **Query Parameters**
| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `page` | Page number | 1 | `?page=2` |
| `per_page` | Events per page | 50 | `?per_page=10` |
| `sort_by` | Sort field | `date` | `?sort_by=name` |
| `sort_order` | Sort direction | `asc` | `?sort_order=desc` |
| `institution` | Filter by institution | - | `?institution=columbia` |
| `date_from` | Filter from date | - | `?date_from=2025-09-01` |
| `date_to` | Filter to date | - | `?date_to=2025-09-30` |
| `search` | Search in names/descriptions | - | `?search=lecture` |

### **Sorting Options**
- **`date`** - Sort by event start date
- **`name`** - Sort alphabetically by event name
- **`institution`** - Sort by institution name
- **`id`** - Sort by event ID

## 🧪 **Testing the API**

### **Test Pagination**
```bash
# Page 1 (first 5 events)
curl "https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events?page=1&per_page=5"

# Page 2 (next 5 events)
curl "https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events?page=2&per_page=5"
```

### **Test Sorting**
```bash
# Sort by name (alphabetical)
curl "https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events?sort_by=name&sort_order=asc"

# Sort by date (chronological)
curl "https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events?sort_by=date&sort_order=desc"
```

### **Test Filtering**
```bash
# Filter by institution
curl "https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events?institution=columbia"

# Search for specific terms
curl "https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events?search=lecture"
```

## 📊 **Current Data Stats**

- **Total Events**: 603
- **Academic Events**: 82 (filtered)
- **Total Pages**: 17 (with 5 events per page)
- **Institutions**: Columbia, NYU, CUNY, Gallatin, ISAWA, JTSA, CIMS, Cornell Tech, Simons Foundation
- **Categories**: EDUCATION, HEALTH, SCIENCE, ARTS, MATHEMATICS, ARCHAEOLOGY, RELIGIOUS_STUDIES, MUSIC, COMPUTER_SCIENCE, PHYSICS

## 🚀 **Deployment**

### **Manual Deployment**
```bash
cd academic
npx wrangler deploy --env=""
```

### **Automatic Deployment**
- **GitHub Actions** runs every Sunday at 2 AM UTC
- **Automatic scraping** → **Data conversion** → **Worker update** → **Cloudflare deployment**
- **No manual intervention** required

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Pagination not working**
   - Check that you're using `page` and `per_page` parameters
   - Ensure the worker has been deployed with the latest code

2. **Events not updating**
   - Verify the weekly scraper is running
   - Check GitHub Actions for any failures
   - Manually run `python weekly_scraper.py`

3. **API errors**
   - Check Cloudflare worker logs
   - Verify the worker is deployed and running
   - Test with simple queries first

### **Manual Recovery**
```bash
# If automatic scraping fails, manually run:
cd academic
python weekly_scraper.py

# Or just update the worker:
python update_worker_with_real_events.py
npx wrangler deploy --env=""
```

## 📈 **Monitoring & Maintenance**

### **Health Checks**
- **API Health**: `GET /health`
- **Statistics**: `GET /api/stats`
- **Event Counts**: Check total events in stats endpoint

### **Performance Metrics**
- **Response Time**: Monitor API response times
- **Event Count**: Track total events over time
- **Scraper Success**: Monitor weekly scraping success rate

### **Data Quality**
- **Duplicate Detection**: Automatic removal of duplicate events
- **Data Validation**: Check for missing required fields
- **Format Consistency**: Ensure all events follow the same structure

## 🎉 **Success Metrics**

- ✅ **Pagination Fixed**: Now shows different events on each page
- ✅ **Sorting Working**: Events can be sorted by date, name, institution
- ✅ **Real Data**: 603 actual events instead of 8 fake ones
- ✅ **Automation**: Weekly updates without manual intervention
- ✅ **API Performance**: Fast responses with proper filtering

## 🔮 **Future Enhancements**

- **Real-time updates** (instead of weekly)
- **Event notifications** for new events
- **Advanced analytics** and reporting
- **Mobile app** integration
- **Calendar sync** capabilities
- **Social sharing** features

---

**Last Updated**: August 31, 2025  
**Next Scraping**: Sunday, September 7, 2025 at 2 AM UTC  
**API Status**: ✅ Active and Healthy  
**Total Events**: 603  
**API URL**: https://nyc-academic-events-api.spergel-joshua.workers.dev
