# 🚀 Cloudflare Workers Deployment Guide

## 📋 Prerequisites

1. **Cloudflare Account** - Sign up at [cloudflare.com](https://cloudflare.com)
2. **Wrangler CLI** - Cloudflare's command-line tool
3. **Your academic events data** (already converted)

## 🛠️ Setup Steps

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Login to Cloudflare

```bash
wrangler login
```

### 3. Convert Your Data (Already Done!)

The script `convert_to_cloudflare.py` has already converted your 79 academic events to Cloudflare Worker format. The output file is `cloudflare-worker-with-data.js`.

### 4. Deploy to Cloudflare Workers

```bash
# Deploy to production
wrangler deploy

# Or deploy to staging first
wrangler deploy --env staging
```

### 5. Your API Will Be Available At:

```
https://nyc-academic-events-api.your-subdomain.workers.dev
```

## 🎯 API Endpoints

Once deployed, your API will have these endpoints:

### Root & Health
- `GET /` - API information
- `GET /health` - Health check

### Events
- `GET /api/events` - List all academic events
- `GET /api/events/{event_id}` - Get specific event
- `GET /api/institutions` - List institutions with event counts
- `GET /api/stats` - API statistics

### Query Parameters
- `skip` - Number of events to skip (pagination)
- `limit` - Number of events to return (max 100)
- `institution` - Filter by institution (e.g., 'columbia', 'nyu')
- `source_group` - Filter by source group (e.g., 'columbia_classics')
- `date_from` - Filter events from date (YYYY-MM-DD)
- `date_to` - Filter events to date (YYYY-MM-DD)
- `academic_only` - Return only academic events (default: true)

## 📊 Example API Calls

```bash
# Get all events
curl "https://nyc-academic-events-api.your-subdomain.workers.dev/api/events"

# Get Columbia events only
curl "https://nyc-academic-events-api.your-subdomain.workers.dev/api/events?institution=columbia"

# Get events from a specific date
curl "https://nyc-academic-events-api.your-subdomain.workers.dev/api/events?date_from=2025-09-01"

# Get institutions
curl "https://nyc-academic-events-api.your-subdomain.workers.dev/api/institutions"

# Get statistics
curl "https://nyc-academic-events-api.your-subdomain.workers.dev/api/stats"
```

## 🔄 Updating Events

To update the events data:

1. **Run your scraping pipeline:**
   ```bash
   python main_test.py
   python filter_academic_events.py
   ```

2. **Convert to Cloudflare format:**
   ```bash
   python convert_to_cloudflare.py
   ```

3. **Deploy the updated worker:**
   ```bash
   wrangler deploy
   ```

## 🌐 Custom Domain (Optional)

To use a custom domain:

1. **Add your domain to Cloudflare**
2. **Update `wrangler.toml`:**
   ```toml
   routes = [
     { pattern = "api.yourdomain.com/*", zone_name = "yourdomain.com" }
   ]
   ```
3. **Deploy:**
   ```bash
   wrangler deploy
   ```

## 📈 Benefits of Cloudflare Workers

✅ **Global CDN** - Fast worldwide access  
✅ **Free Tier** - 100,000 requests/day  
✅ **Serverless** - No server management  
✅ **Edge Computing** - Low latency  
✅ **Automatic Scaling** - Handles traffic spikes  
✅ **Built-in CORS** - Cross-origin support  

## 🔧 Development

### Local Testing
```bash
# Start local development server
wrangler dev

# Test locally at http://localhost:8787
```

### Environment Variables
Add any environment variables to `wrangler.toml`:
```toml
[vars]
API_VERSION = "1.0.0"
```

## 📝 Troubleshooting

### Common Issues:

1. **"Worker not found"** - Make sure you're logged in and the worker name is correct
2. **"CORS errors"** - CORS headers are already configured in the worker
3. **"Data not updating"** - Make sure to run the conversion script and redeploy

### Debug Commands:
```bash
# Check worker status
wrangler whoami

# View logs
wrangler tail

# List all workers
wrangler workers list
```

## 🎉 Success!

Once deployed, you'll have a fully functional API serving your 79 academic events from NYC institutions, accessible globally with low latency!

**Your API URL:** `https://nyc-academic-events-api.your-subdomain.workers.dev`
