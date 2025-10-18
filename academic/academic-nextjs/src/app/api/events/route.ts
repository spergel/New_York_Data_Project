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
  category?: string[];
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
  category?: string;
  description: string;
  source_url?: string;
}

export async function GET() {
  try {
    // Use the main academic scraped events
    // From academic-nextjs directory, go up one level to academic, then to scraped_events.json
    let filePath = path.join(process.cwd(), '..', 'scraped_events.json');

    console.log('API: Looking for file at:', filePath);
    console.log('API: Current working directory:', process.cwd());

    const fileContents = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(fileContents);

    // Transform the data to match our component's expected format
    const processedEvents: ProcessedEvent[] = data.events
      .filter((event: RawEvent) => {
        // Filter for future events and events with meaningful descriptions
        const eventDate = new Date(event.start_date);
        const now = new Date();
        return eventDate >= now && event.description && event.description.length > 10;
      })
      // Remove limit to show all available events
      .map((event: RawEvent) => {
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

        // Get category
        const category = event.category && event.category.length > 0
          ? event.category[0].charAt(0).toUpperCase() + event.category[0].slice(1).toLowerCase()
          : 'Academic Event';

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
      });

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
