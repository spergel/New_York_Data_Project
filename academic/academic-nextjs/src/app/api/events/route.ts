import { NextResponse } from 'next/server';
import fs from 'fs/promises';
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

// Helper function to filter events
function getFilteredEvents(events: ProcessedEvent[], filters: {
  search: string;
  category: string;
  institution: string;
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

  return NextResponse.json({
    events: filtered,
    total: filtered.length
  });
}

export async function GET(request: Request) {
  const apiStartTime = Date.now();
  console.log('🚀 [API] Starting GET /api/events');
  
  try {
    const url = new URL(request.url);
    const search = url.searchParams.get('search') || '';
    const category = url.searchParams.get('category') || '';
    const institution = url.searchParams.get('institution') || '';

    // Check cache first
    const now = Date.now();
    if (cachedEvents && (now - cacheTimestamp) < CACHE_DURATION) {
      const cacheTime = Date.now() - apiStartTime;
      console.log(`⚡ [API] Cache hit! Returning cached events (${cachedEvents.length} events) in ${cacheTime}ms`);
      return getFilteredEvents(cachedEvents, { search, category, institution });
    }
    
    console.log('📂 [API] Cache miss - loading from file');

    let data;
    let dataSource = 'unknown';

    // Try to read real scraped events from public directory (async for better performance)
    const fileReadStart = Date.now();
    try {
      const realDataPath = path.join(process.cwd(), 'public', 'scraped_events.json');
      console.log(`📖 [API] Reading file: ${realDataPath}`);
      const fileContents = await fs.readFile(realDataPath, 'utf8');
      const fileReadTime = Date.now() - fileReadStart;
      console.log(`✅ [API] File read complete: ${fileContents.length} bytes in ${fileReadTime}ms`);
      
      const parseStart = Date.now();
      data = JSON.parse(fileContents);
      const parseTime = Date.now() - parseStart;
      console.log(`✅ [API] JSON parsed: ${data.events?.length || 0} events in ${parseTime}ms`);
      dataSource = 'real_scraped_data';
    } catch (error) {
      // Fallback to sample data if real data not available
      try {
        const samplePath = path.join(process.cwd(), 'src', 'data', 'sample_events.json');
        const fileContents = await fs.readFile(samplePath, 'utf8');
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
    const processingStart = Date.now();
    console.log(`🔄 [API] Processing ${data.events.length} events...`);
    
    // Optimized: Pre-compute current time once (for event filtering)
    const currentTime = Date.now();
    
    // Faster date formatting function (avoiding locale-dependent methods)
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December'];
    const formatDate = (date: Date): string => {
      const month = monthNames[date.getMonth()];
      const day = date.getDate();
      const year = date.getFullYear();
      const hours = date.getHours();
      const minutes = date.getMinutes();
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const displayHours = hours % 12 || 12;
      const displayMinutes = minutes.toString().padStart(2, '0');
      
      return `${month} ${day}, ${year} ${displayHours}:${displayMinutes} ${ampm}`;
    };
    
    // Optimized: Single pass filter + map
    const processedEvents: ProcessedEvent[] = [];
    const eventCount = data.events.length;
    
    for (let i = 0; i < eventCount; i++) {
      const event = data.events[i];
      
      try {
        // Quick filter check first
        if (!event.description || event.description.length <= 10) continue;
        
        const eventDate = new Date(event.start_date);
        if (isNaN(eventDate.getTime()) || eventDate.getTime() < currentTime) continue;
        
        // Process the event
        const startDate = new Date(event.start_date);
        const endDate = new Date(event.end_date);
        
        let dateString = formatDate(startDate);
        
        if (startDate.toDateString() === endDate.toDateString()) {
          const endHours = endDate.getHours();
          const endMinutes = endDate.getMinutes();
          const endAmpm = endHours >= 12 ? 'PM' : 'AM';
          const endDisplayHours = endHours % 12 || 12;
          const endDisplayMinutes = endMinutes.toString().padStart(2, '0');
          dateString += ` - ${endDisplayHours}:${endDisplayMinutes} ${endAmpm}`;
        } else {
          dateString += ` to ${formatDate(endDate)}`;
        }

        // Get institution name (optimized string operations)
        let institution = event.metadata?.source_name || event.source;
        institution = institution.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());

        // Get location
        const location = event.metadata?.venue?.name || event.metadata?.venue?.address || 'Location TBD';

        // Get category (optimized)
        let category: string[] = [];
        if (event.category) {
          if (Array.isArray(event.category)) {
            category = event.category.map(cat => {
              const first = cat.charAt(0).toUpperCase();
              const rest = cat.slice(1).toLowerCase();
              return first + rest;
            });
          } else if (typeof event.category === 'string') {
            const first = event.category.charAt(0).toUpperCase();
            const rest = event.category.slice(1).toLowerCase();
            category = [first + rest];
          }
        }
        if (category.length === 0) {
          category = ['Academic Event'];
        }

        // Clean up description (optimized)
        const description = event.description.length > 500 
          ? event.description.substring(0, 500) + '...'
          : event.description;

        processedEvents.push({
          title: event.name,
          institution,
          date: dateString,
          location,
          category,
          description,
          source_url: event.metadata?.source_url
        });
      } catch (error) {
        // Skip invalid events silently
        continue;
      }
    }

    const processingTime = Date.now() - processingStart;
    console.log(`✅ [API] Processing complete: ${processedEvents.length} events processed in ${processingTime}ms`);
    
    // Cache the processed events
    cachedEvents = processedEvents;
    cacheTimestamp = Date.now();
    
    const totalTime = Date.now() - apiStartTime;
    console.log(`🏁 [API] Total API request time: ${totalTime}ms`);
    
    return getFilteredEvents(processedEvents, { search, category, institution });

  } catch (error) {
    console.error('Error reading events data:', error);
    return NextResponse.json(
      { error: 'Failed to load events data' },
      { status: 500 }
    );
  }
}