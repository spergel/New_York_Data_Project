#!/usr/bin/env python3
"""
Script to convert academic events JSON data to Cloudflare Worker format
"""

import json
import os

def convert_events_to_cloudflare():
    """Convert academic events to Cloudflare Worker format"""
    
    # Load the academic events data
    events_file = "events_test/academic_events_filtered.json"
    
    if not os.path.exists(events_file):
        print(f"Error: {events_file} not found. Please run the scraping first.")
        return
    
    with open(events_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    
    if not events:
        print("No events found in the data.")
        return
    
    # Convert events to the format expected by Cloudflare Worker
    cloudflare_events = []
    
    for i, event in enumerate(events, 1):
        # Extract data from the event structure
        cloudflare_event = {
            "id": i,
            "event_id": event.get('id', f"evt_{i}"),
            "name": event.get('name', ''),
            "description": event.get('description', ''),
            "start_date": event.get('start_date', ''),
            "end_date": event.get('end_date', ''),
            "source": event.get('source', ''),
            "source_group": event.get('source_group', ''),
            "source_url": event.get('metadata', {}).get('source_url', ''),
            "source_name": event.get('metadata', {}).get('source_name', ''),
            "venue_name": event.get('metadata', {}).get('venue', {}).get('name', ''),
            "venue_type": event.get('metadata', {}).get('venue', {}).get('type', ''),
            "is_academic": True  # All events in this file are academic
        }
        cloudflare_events.append(cloudflare_event)
    
    # Create the Cloudflare Worker code with the actual data
    worker_code = f"""// Cloudflare Worker for NYC Academic Events API
// This worker serves academic events from the JSON data

// CORS headers for cross-origin requests
const corsHeaders = {{
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
}};

// Academic events data (converted from scraped data)
const academicEvents = {json.dumps(cloudflare_events, indent=2)};

// Helper function to filter events
function filterEvents(events, filters) {{
  let filtered = events;
  
  if (filters.institution) {{
    filtered = filtered.filter(event => event.source === filters.institution);
  }}
  
  if (filters.source_group) {{
    filtered = filtered.filter(event => event.source_group === filters.source_group);
  }}
  
  if (filters.date_from) {{
    filtered = filtered.filter(event => event.start_date >= filters.date_from);
  }}
  
  if (filters.date_to) {{
    filtered = filtered.filter(event => event.start_date <= filters.date_to);
  }}
  
  if (filters.academic_only !== false) {{
    filtered = filtered.filter(event => event.is_academic === true);
  }}
  
  return filtered;
}}

// Helper function to paginate results
function paginateEvents(events, skip = 0, limit = 50) {{
  const total = events.length;
  const paginated = events.slice(skip, skip + limit);
  
  return {{
    events: paginated,
    total: total,
    page: Math.floor(skip / limit) + 1,
    per_page: limit
  }};
}}

// Helper function to get institutions with event counts
function getInstitutions(events) {{
  const institutionMap = new Map();
  
  events.forEach(event => {{
    if (event.is_academic) {{
      const key = event.source_group;
      if (!institutionMap.has(key)) {{
        institutionMap.set(key, {{
          name: event.source_name || event.source_group,
          source_group: event.source_group,
          event_count: 0
        }});
      }}
      institutionMap.get(key).event_count++;
    }}
  }});
  
  return Array.from(institutionMap.values()).sort((a, b) => b.event_count - a.event_count);
}}

// Main request handler
async function handleRequest(request) {{
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {{
    return new Response(null, {{ headers: corsHeaders }});
  }}
  
  try {{
    // Root endpoint
    if (path === '/' || path === '/api') {{
      return new Response(JSON.stringify({{
        message: "NYC Academic Events API",
        version: "1.0.0",
        endpoints: {{
          events: "/api/events",
          event_by_id: "/api/events/{{event_id}}",
          institutions: "/api/institutions",
          stats: "/api/stats"
        }}
      }}), {{ headers: corsHeaders }});
    }}
    
    // Health check
    if (path === '/health') {{
      return new Response(JSON.stringify({{
        status: "healthy",
        service: "nyc-academic-events-api",
        timestamp: new Date().toISOString()
      }}), {{ headers: corsHeaders }});
    }}
    
    // Get all events
    if (path === '/api/events') {{
      const skip = parseInt(url.searchParams.get('skip') || '0');
      const limit = Math.min(parseInt(url.searchParams.get('limit') || '50'), 100);
      const institution = url.searchParams.get('institution');
      const source_group = url.searchParams.get('source_group');
      const date_from = url.searchParams.get('date_from');
      const date_to = url.searchParams.get('date_to');
      const academic_only = url.searchParams.get('academic_only') !== 'false';
      
      const filters = {{ institution, source_group, date_from, date_to, academic_only }};
      const filtered = filterEvents(academicEvents, filters);
      const result = paginateEvents(filtered, skip, limit);
      
      return new Response(JSON.stringify(result), {{ headers: corsHeaders }});
    }}
    
    // Get specific event by ID
    if (path.startsWith('/api/events/')) {{
      const eventId = path.split('/').pop();
      const event = academicEvents.find(e => e.event_id === eventId);
      
      if (!event) {{
        return new Response(JSON.stringify({{ error: "Event not found" }}), {{
          status: 404,
          headers: corsHeaders
        }});
      }}
      
      return new Response(JSON.stringify(event), {{ headers: corsHeaders }});
    }}
    
    // Get institutions
    if (path === '/api/institutions') {{
      const institutions = getInstitutions(academicEvents);
      const result = {{
        institutions: institutions,
        total: institutions.length
      }};
      
      return new Response(JSON.stringify(result), {{ headers: corsHeaders }});
    }}
    
    // Get statistics
    if (path === '/api/stats') {{
      const academicEventsOnly = academicEvents.filter(e => e.is_academic);
      const institutions = getInstitutions(academicEvents);
      
      // Group events by month
      const monthlyStats = {{}};
      academicEventsOnly.forEach(event => {{
        if (event.start_date) {{
          const month = event.start_date.substring(0, 7); // YYYY-MM
          monthlyStats[month] = (monthlyStats[month] || 0) + 1;
        }}
      }});
      
      const result = {{
        total_academic_events: academicEventsOnly.length,
        total_institutions: institutions.length,
        monthly_events: Object.entries(monthlyStats).map(([month, count]) => ({{
          month,
          count
        }})),
        last_updated: new Date().toISOString()
      }};
      
      return new Response(JSON.stringify(result), {{ headers: corsHeaders }});
    }}
    
    // 404 for unknown endpoints
    return new Response(JSON.stringify({{ error: "Endpoint not found" }}), {{
      status: 404,
      headers: corsHeaders
    }});
    
  }} catch (error) {{
    return new Response(JSON.stringify({{ error: "Internal server error" }}), {{
      status: 500,
      headers: corsHeaders
    }});
  }}
}}

// Export the fetch event handler
addEventListener('fetch', event => {{
  event.respondWith(handleRequest(event.request));
}});
"""
    
    # Write the Cloudflare Worker code to a file
    output_file = "cloudflare-worker-with-data.js"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(worker_code)
    
    print(f"✅ Successfully converted {len(cloudflare_events)} events to Cloudflare Worker format!")
    print(f"📁 Output file: {output_file}")
    print(f"📊 Total events: {len(cloudflare_events)}")
    
    # Show some statistics
    sources = set(event['source'] for event in cloudflare_events)
    print(f"🏫 Institutions: {len(sources)}")
    print(f"📅 Date range: {min(event['start_date'] for event in cloudflare_events if event['start_date'])} to {max(event['start_date'] for event in cloudflare_events if event['start_date'])}")

if __name__ == "__main__":
    convert_events_to_cloudflare()
