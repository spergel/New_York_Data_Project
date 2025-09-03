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
    if (path === '/health') {
      return addCorsHeaders(new Response(JSON.stringify({
        status: 'healthy',
        service: 'NYC Academic Events API',
        version: '1.0.0',
        events_count: academicEvents.length,
        quick_start: 'Visit /docs for full API documentation'
      }, null, 2), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }));
    }
    
    // Main API documentation page
    if (path === '/' || path === '/docs') {
      return addCorsHeaders(new Response(JSON.stringify({
        status: 'healthy',
        service: 'NYC Academic Events API',
        version: '1.0.0',
        events_count: academicEvents.length,
        documentation: {
          base_url: 'https://nyc-academic-events-api.spergel-joshua.workers.dev',
          endpoints: {
            '/api/events': {
              method: 'GET',
              description: 'Get academic events with filtering and pagination',
              query_parameters: {
                search: {
                  type: 'string',
                  description: 'Search events by name or description',
                  example: '?search=lecture'
                },
                source: {
                  type: 'string',
                  description: 'Filter by institution/source (case-insensitive)',
                  example: '?source=columbia',
                  available_values: [...new Set(academicEvents.map(e => e.source_group))].filter(Boolean)
                },
                start_date: {
                  type: 'string',
                  description: 'Filter events starting from this date (ISO format)',
                  example: '?start_date=2025-09-01'
                },
                end_date: {
                  type: 'string',
                  description: 'Filter events ending before this date (ISO format)',
                  example: '?end_date=2025-12-31'
                },
                limit: {
                  type: 'integer',
                  description: 'Number of events to return per page (default: 100, max: 500)',
                  example: '?limit=50'
                },
                offset: {
                  type: 'integer',
                  description: 'Number of events to skip for pagination (default: 0)',
                  example: '?offset=100'
                }
              },
              pagination: {
                description: 'Response includes pagination metadata',
                fields: {
                  total: 'Total number of events matching filters',
                  limit: 'Events per page',
                  offset: 'Events skipped',
                  has_more: 'Boolean indicating if more events exist'
                }
              },
              examples: [
                'GET /api/events - Get first 100 events',
                'GET /api/events?limit=20 - Get first 20 events',
                'GET /api/events?source=nyu&limit=10 - Get 10 NYU events',
                'GET /api/events?search=lecture&limit=5 - Search for lectures, get 5 results',
                'GET /api/events?start_date=2025-09-01&end_date=2025-09-30 - September 2025 events',
                'GET /api/events?offset=100&limit=50 - Get events 101-150 (pagination)'
              ]
            },
            '/api/events/{id}': {
              method: 'GET',
              description: 'Get a specific event by its ID',
              example: 'GET /api/events/evt_nyu_cims_15bb52f6'
            },
            '/api/sources': {
              method: 'GET',
              description: 'Get list of all available institutions/sources',
              example: 'GET /api/sources'
            },
            '/api/stats': {
              method: 'GET',
              description: 'Get API statistics and metadata',
              example: 'GET /api/stats'
            }
          },
          response_format: {
            success: 'Boolean indicating if request was successful',
            data: 'Main response data (varies by endpoint)',
            meta: 'Metadata about the response',
            pagination: 'Pagination information (for events endpoint)',
            filters: 'Applied filters (for events endpoint)'
          },
          filtering_tips: [
            'Use partial matches for source filtering (e.g., "columbia" matches "columbia_classics", "columbia_math")',
            'Date filtering uses ISO 8601 format (YYYY-MM-DD)',
            'Search is case-insensitive and searches both event names and descriptions',
            'Combine multiple filters for precise results'
          ],
          rate_limits: 'No rate limits currently applied',
          caching: 'Responses are cached for 1 hour',
          cors: 'Full CORS support enabled for all origins'
        }
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
