// Cloudflare Worker for NYC Academic Events API
// This worker serves academic events from the JSON data

// CORS headers for cross-origin requests
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

// Sample academic events data (you can replace this with your actual data)
const academicEvents = [
  {
    id: 1,
    event_id: "evt_columbia_classics_abc123",
    name: "Classics Departmental Lecture Series: Stephen Harrison (University of Oxford)",
    description: "Lecture on classical studies",
    start_date: "2025-09-09",
    end_date: "",
    source: "columbia",
    source_group: "columbia_classics",
    source_url: "https://classics.columbia.edu/events",
    source_name: "Columbia University Department of Classics",
    venue_name: "Columbia University",
    venue_type: "Offline",
    is_academic: true
  },
  {
    id: 2,
    event_id: "evt_nyu_stern_def456",
    name: "Business Analytics Seminar",
    description: "Seminar on business analytics",
    start_date: "2025-09-15",
    end_date: "",
    source: "nyu",
    source_group: "nyu_stern",
    source_url: "https://stern.nyu.edu/events",
    source_name: "NYU Stern School of Business",
    venue_name: "NYU Stern",
    venue_type: "Offline",
    is_academic: true
  }
];

// Helper function to filter events
function filterEvents(events, filters) {
  let filtered = events;
  
  if (filters.institution) {
    filtered = filtered.filter(event => event.source === filters.institution);
  }
  
  if (filters.source_group) {
    filtered = filtered.filter(event => event.source_group === filters.source_group);
  }
  
  if (filters.date_from) {
    filtered = filtered.filter(event => event.start_date >= filters.date_from);
  }
  
  if (filters.date_to) {
    filtered = filtered.filter(event => event.start_date <= filters.date_to);
  }
  
  if (filters.academic_only !== false) {
    filtered = filtered.filter(event => event.is_academic === true);
  }
  
  return filtered;
}

// Helper function to paginate results
function paginateEvents(events, skip = 0, limit = 50) {
  const total = events.length;
  const paginated = events.slice(skip, skip + limit);
  
  return {
    events: paginated,
    total: total,
    page: Math.floor(skip / limit) + 1,
    per_page: limit
  };
}

// Helper function to get institutions with event counts
function getInstitutions(events) {
  const institutionMap = new Map();
  
  events.forEach(event => {
    if (event.is_academic) {
      const key = event.source_group;
      if (!institutionMap.has(key)) {
        institutionMap.set(key, {
          name: event.source_name || event.source_group,
          source_group: event.source_group,
          event_count: 0
        });
      }
      institutionMap.get(key).event_count++;
    }
  });
  
  return Array.from(institutionMap.values()).sort((a, b) => b.event_count - a.event_count);
}

// Main request handler
async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }
  
  try {
    // Root endpoint
    if (path === '/' || path === '/api') {
      return new Response(JSON.stringify({
        message: "NYC Academic Events API",
        version: "1.0.0",
        endpoints: {
          events: "/api/events",
          event_by_id: "/api/events/{event_id}",
          institutions: "/api/institutions",
          stats: "/api/stats"
        }
      }), { headers: corsHeaders });
    }
    
    // Health check
    if (path === '/health') {
      return new Response(JSON.stringify({
        status: "healthy",
        service: "nyc-academic-events-api",
        timestamp: new Date().toISOString()
      }), { headers: corsHeaders });
    }
    
    // Get all events
    if (path === '/api/events') {
      const skip = parseInt(url.searchParams.get('skip') || '0');
      const limit = Math.min(parseInt(url.searchParams.get('limit') || '50'), 100);
      const institution = url.searchParams.get('institution');
      const source_group = url.searchParams.get('source_group');
      const date_from = url.searchParams.get('date_from');
      const date_to = url.searchParams.get('date_to');
      const academic_only = url.searchParams.get('academic_only') !== 'false';
      
      const filters = { institution, source_group, date_from, date_to, academic_only };
      const filtered = filterEvents(academicEvents, filters);
      const result = paginateEvents(filtered, skip, limit);
      
      return new Response(JSON.stringify(result), { headers: corsHeaders });
    }
    
    // Get specific event by ID
    if (path.startsWith('/api/events/')) {
      const eventId = path.split('/').pop();
      const event = academicEvents.find(e => e.event_id === eventId);
      
      if (!event) {
        return new Response(JSON.stringify({ error: "Event not found" }), {
          status: 404,
          headers: corsHeaders
        });
      }
      
      return new Response(JSON.stringify(event), { headers: corsHeaders });
    }
    
    // Get institutions
    if (path === '/api/institutions') {
      const institutions = getInstitutions(academicEvents);
      const result = {
        institutions: institutions,
        total: institutions.length
      };
      
      return new Response(JSON.stringify(result), { headers: corsHeaders });
    }
    
    // Get statistics
    if (path === '/api/stats') {
      const academicEventsOnly = academicEvents.filter(e => e.is_academic);
      const institutions = getInstitutions(academicEvents);
      
      // Group events by month
      const monthlyStats = {};
      academicEventsOnly.forEach(event => {
        if (event.start_date) {
          const month = event.start_date.substring(0, 7); // YYYY-MM
          monthlyStats[month] = (monthlyStats[month] || 0) + 1;
        }
      });
      
      const result = {
        total_academic_events: academicEventsOnly.length,
        total_institutions: institutions.length,
        monthly_events: Object.entries(monthlyStats).map(([month, count]) => ({
          month,
          count
        })),
        last_updated: new Date().toISOString()
      };
      
      return new Response(JSON.stringify(result), { headers: corsHeaders });
    }
    
    // 404 for unknown endpoints
    return new Response(JSON.stringify({ error: "Endpoint not found" }), {
      status: 404,
      headers: corsHeaders
    });
    
  } catch (error) {
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Export the fetch event handler
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
