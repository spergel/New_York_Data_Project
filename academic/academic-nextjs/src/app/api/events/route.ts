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

export async function GET() {
  try {
    let data;

    // Try multiple paths for the scraped events file
    const possiblePaths = [
      path.join(process.cwd(), 'public', 'scraped_events.json'),
      path.join(process.cwd(), 'scraped_events.json'),
      path.join(process.cwd(), '..', 'scraped_events.json'),
      path.join(process.cwd(), 'src', 'data', 'scraped_events.json')
    ];

    let foundRealData = false;
    for (const filePath of possiblePaths) {
      try {
        console.log(`API: Trying to read from ${filePath}`);
        const fileContents = fs.readFileSync(filePath, 'utf8');
        data = JSON.parse(fileContents);
        console.log(`API: Successfully loaded real scraped data with ${data.total_events} events from ${filePath}`);
        foundRealData = true;
        break;
      } catch (error) {
        console.log(`API: Failed to read from ${filePath}: ${error}`);
        continue;
      }
    }

    if (!foundRealData) {
      // Fallback to sample data if real data not available
      console.log('API: Real scraped data not found in any location, using sample data');
      const samplePath = path.join(process.cwd(), 'src', 'data', 'sample_events.json');
      const fileContents = fs.readFileSync(samplePath, 'utf8');
      data = JSON.parse(fileContents);
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

    console.log(`API: Returning ${processedEvents.length} events`);
    
    return NextResponse.json({
      events: processedEvents,
      total: processedEvents.length,
      source: 'NYC Academic Events'
    });

  } catch (error) {
    console.error('Error reading events data:', error);
    return NextResponse.json(
      { error: 'Failed to load events data' },
      { status: 500 }
    );
  }
}
