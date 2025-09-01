// Cloudflare Worker for NYC Academic Events API
// This worker serves academic events data scraped from NYC institutions

import { academicEvents } from './worker_events_code.js';

// CORS headers for cross-origin requests
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};

// Helper function to add CORS headers
function addCorsHeaders(response) {
  const newResponse = new Response(response.body, response);
  Object.entries(corsHeaders).forEach(([key, value]) => {
    newResponse.headers.set(key, value);
  });
  return newResponse;
}

// Helper function to filter events
function filterEvents(events, filters = {}) {
  let filtered = [...events];
  
  // Filter by institution/source
  if (filters.source) {
    filtered = filtered.filter(event => 
      event.source_group && event.source_group.toLowerCase().includes(filters.source.toLowerCase())
    );
  }
  
  // Filter by date range
  if (filters.start_date) {
    filtered = filtered.filter(event => 
      event.start_date >= filters.start_date
    );
  }
  
  if (filters.end_date) {
    filtered = filtered.filter(event => 
      event.end_date <= filters.end_date
    );
  }
  
  // Filter by search term
  if (filters.search) {
    const searchTerm = filters.search.toLowerCase();
    filtered = filtered.filter(event => 
      event.name.toLowerCase().includes(searchTerm) ||
      (event.description && event.description.toLowerCase().includes(searchTerm))
    );
  }
  
  return filtered;
}

// Main request handler
async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders
    });
  }
  
  try {
    // API endpoints
    if (path === '/api/events' || path === '/api/events/') {
      // Get query parameters for filtering
      const search = url.searchParams.get('search');
      const source = url.searchParams.get('source');
      const start_date = url.searchParams.get('start_date');
      const end_date = url.searchParams.get('end_date');
      const limit = parseInt(url.searchParams.get('limit') || '100');
      const offset = parseInt(url.searchParams.get('offset') || '0');
      
      // Apply filters
      let filteredEvents = filterEvents(academicEvents, {
        search,
        source,
        start_date,
        end_date
      });
      
      // Apply pagination
      const total = filteredEvents.length;
      const paginatedEvents = filteredEvents.slice(offset, offset + limit);
      
      const response = {
        success: true,
        data: {
          events: paginatedEvents,
          pagination: {
            total,
            limit,
            offset,
            has_more: offset + limit < total
          },
          filters: {
            search,
            source,
            start_date,
            end_date
          }
        },
        meta: {
          total_events: academicEvents.length
        }
      };
      
      return addCorsHeaders(new Response(JSON.stringify(response, null, 2), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
        }
      }));
    }
    
    // Get specific event by ID
    if (path.startsWith('/api/events/') && path !== '/api/events/') {
      const eventId = path.split('/').pop();
      const event = academicEvents.find(e => e.id === eventId);
      
      if (!event) {
        return addCorsHeaders(new Response(JSON.stringify({
          success: false,
          error: 'Event not found'
        }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }));
      }
      
      return addCorsHeaders(new Response(JSON.stringify({
        success: true,
        data: event
      }, null, 2), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }));
    }
    
    // Get sources/institutions
    if (path === '/api/sources' || path === '/api/sources/') {
      const sources = [...new Set(academicEvents.map(e => e.source_group))].filter(Boolean);
      
      return addCorsHeaders(new Response(JSON.stringify({
        success: true,
        data: sources
      }, null, 2), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }));
    }
    
    // Get API stats
    if (path === '/api/stats' || path === '/api/stats/') {
      const stats = {
        total_events: academicEvents.length,
        sources: [...new Set(academicEvents.map(e => e.source_group))].filter(Boolean).length,
        date_range: {
          earliest: academicEvents.reduce((min, e) => 
            e.start_date < min ? e.start_date : min, academicEvents[0]?.start_date
          ),
          latest: academicEvents.reduce((max, e) => 
            e.start_date > max ? e.start_date : max, academicEvents[0]?.start_date
          )
        }
      };
      
      return addCorsHeaders(new Response(JSON.stringify({
        success: true,
        data: stats
      }, null, 2), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }));
    }
    
    // Health check
    if (path === '/health' || path === '/') {
      return addCorsHeaders(new Response(JSON.stringify({
        status: 'healthy',
        service: 'NYC Academic Events API',
        version: '1.0.0',
        events_count: academicEvents.length
      }, null, 2), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }));
    }
    
    // 404 for unknown endpoints
    return addCorsHeaders(new Response(JSON.stringify({
      success: false,
      error: 'Endpoint not found',
      available_endpoints: [
        'GET /api/events - Get all events with optional filtering',
        'GET /api/events/{id} - Get specific event by ID',
        'GET /api/sources - Get list of institutions',
        'GET /api/stats - Get API statistics',
        'GET /health - Health check'
      ]
    }, null, 2), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    }));
    
  } catch (error) {
    console.error('Worker error:', error);
    return addCorsHeaders(new Response(JSON.stringify({
      success: false,
      error: 'Internal server error',
      message: error.message
    }, null, 2), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    }));
  }
}

// Export the fetch event handler
export default {
  async fetch(request, env, ctx) {
    return handleRequest(request);
  }
};
