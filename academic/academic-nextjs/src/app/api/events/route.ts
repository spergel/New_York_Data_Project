import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

interface RawEvent {
  id: string;
  name: string;
  type: string;
  location_id?: string;
  community_id?: string;
  description: string;
  start_date: string;
  end_date: string;
  category?: string | string[];
  source: string;
  metadata?: {
    source_url?: string;
    source_name?: string;
    venue?: {
      name?: string;
      address?: string;
      type?: string;
    };
  };
}

interface ProcessedEvent {
  title: string;
  institution: string;
  date: string;
  location?: string;
  category?: string[];
  description: string;
  source_url?: string;
}

// Cache for processed events
let cachedEvents: ProcessedEvent[] | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Helper function to filter and paginate events
function getFilteredEvents(events: ProcessedEvent[], filters: {
  search: string;
  category: string;
  institution: string;
  page: number;
  limit: number;
}) {
  let filtered = events;

  // Apply filters
  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter(event => 
      event.title.toLowerCase().includes(searchLower) ||
      event.description.toLowerCase().includes(searchLower) ||
      event.institution.toLowerCase().includes(searchLower)
    );
  }

  if (filters.category) {
    filtered = filtered.filter(event => 
      event.category && event.category.some(cat => cat.toLowerCase().includes(filters.category.toLowerCase()))
    );
  }

  if (filters.institution) {
    filtered = filtered.filter(event => 
      event.institution.toLowerCase().includes(filters.institution.toLowerCase())
    );
  }

  // Apply pagination
  const total = filtered.length;
  const start = (filters.page - 1) * filters.limit;
  const end = start + filters.limit;
  const paginatedEvents = filtered.slice(start, end);

  return NextResponse.json({
    events: paginatedEvents,
    total: total,
    page: filters.page,
    limit: filters.limit,
    totalPages: Math.ceil(total / filters.limit)
  });
}

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const search = url.searchParams.get('search') || '';
    const category = url.searchParams.get('category') || '';
    const institution = url.searchParams.get('institution') || '';
    
    // Pagination parameters
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '50'); // Default 50 events per page

    // Check cache first
    const now = Date.now();
    if (cachedEvents && (now - cacheTimestamp) < CACHE_DURATION) {
      return getFilteredEvents(cachedEvents, { search, category, institution, page, limit });
    }

    let data;
    let dataSource = 'unknown';

    // Try to read real scraped events from public directory
    try {
      const realDataPath = path.join(process.cwd(), 'public', 'scraped_events.json');
      const fileContents = fs.readFileSync(realDataPath, 'utf8');
      data = JSON.parse(fileContents);
      dataSource = 'real_scraped_data';
    } catch (error) {
      // Fallback to sample data if real data not available
      try {
        const samplePath = path.join(process.cwd(), 'src', 'data', 'sample_events.json');
        const fileContents = fs.readFileSync(samplePath, 'utf8');
        data = JSON.parse(fileContents);
        dataSource = 'sample_data';
      } catch (sampleError) {
        
        // Final fallback - return hardcoded sample data
        data = {
          events: [
            {
              id: "fallback_1",
              name: "Quantum Computing Symposium",
              type: "Academic",
              description: "Join leading researchers in quantum computing for presentations on the latest breakthroughs in quantum algorithms, hardware development, and practical applications.",
              start_date: "2025-10-25T14:00:00",
              end_date: "2025-10-25T17:00:00",
              category: ["SCIENCE", "TECHNOLOGY"],
              source: "columbia_cs",
              metadata: {
                source_url: "https://www.cs.columbia.edu/research/quantum-computing/",
                source_name: "Columbia University Computer Science",
                venue: {
                  name: "Davis Auditorium",
                  address: "530 W 120th St, New York, NY 10027",
                  type: "venue"
                }
              }
            },
            {
              id: "fallback_2", 
              name: "Medieval Literature Conference",
              type: "Academic",
              description: "An interdisciplinary conference exploring medieval texts through modern critical lenses, featuring presentations from scholars across multiple disciplines.",
              start_date: "2025-11-02T09:00:00",
              end_date: "2025-11-02T17:00:00",
              category: ["EDUCATION", "HUMANITIES"],
              source: "nyu_gallatin",
              metadata: {
                source_url: "https://gallatin.nyu.edu/academics/conferences.html",
                source_name: "NYU Gallatin School",
                venue: {
                  name: "Bobst Library, Room 119",
                  address: "70 Washington Square S, New York, NY 10012",
                  type: "venue"
                }
              }
            }
          ]
        };
        dataSource = 'hardcoded_fallback';
        console.log(`API: Using hardcoded fallback with ${data.events.length} events`);
      }
    }

    // Transform the data to match our component's expected format
    const processedEvents: ProcessedEvent[] = data.events
      .filter((event: RawEvent) => {
        try {
          // Filter for future events and events with meaningful descriptions
          const eventDate = new Date(event.start_date);
          const now = new Date();
          const isFuture = eventDate >= now;
          const hasDescription = event.description && event.description.length > 10;
          return isFuture && hasDescription;
        } catch (_unused) {
          // Skip events with invalid data
          return false;
        }
      })
      // Remove limit to show all available events
      .map((event: RawEvent) => {
        try {
          // Format the date
          const startDate = new Date(event.start_date);
          const endDate = new Date(event.end_date);
          let dateString = startDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });

          if (startDate.toDateString() === endDate.toDateString()) {
            dateString += ` - ${endDate.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit'
            })}`;
          } else {
            dateString += ` to ${endDate.toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}`;
          }

          // Get institution name
          let institution = event.metadata?.source_name || event.source;
          institution = institution.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

          // Get location
          const location = event.metadata?.venue?.name || event.metadata?.venue?.address || 'Location TBD';

          // Get category (handle both string and array formats)
          let category: string[] = [];
          if (event.category) {
            if (Array.isArray(event.category)) {
              // It's an array
              category = event.category.map(cat => cat.charAt(0).toUpperCase() + cat.slice(1).toLowerCase());
            } else if (typeof event.category === 'string') {
              // It's a string, convert to array
              category = [event.category.charAt(0).toUpperCase() + event.category.slice(1).toLowerCase()];
            }
          }
          if (category.length === 0) {
            category = ['Academic Event'];
          }

          // Clean up description
          let description = event.description;
          if (description.length > 500) {
            description = description.substring(0, 500) + '...';
          }

          return {
            title: event.name,
            institution,
            date: dateString,
            location,
            category,
            description,
            source_url: event.metadata?.source_url
          };
        } catch (error) {
          console.error('API: Error processing event:', event.id, error);
          return null;
        }
      })
      .filter((event: ProcessedEvent | null): event is ProcessedEvent => event !== null);

    
    // Cache the processed events
    cachedEvents = processedEvents;
    cacheTimestamp = Date.now();
    
    return getFilteredEvents(processedEvents, { search, category, institution, page, limit });

  } catch (error) {
    console.error('Error reading events data:', error);
    return NextResponse.json(
      { error: 'Failed to load events data' },
      { status: 500 }
    );
  }
}