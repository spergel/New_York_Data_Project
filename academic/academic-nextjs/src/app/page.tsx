'use client';

import { useEffect, useState } from 'react';
import AcademicBook from '@/components/AcademicBook';
import { EventData } from '@/types/events';

interface ApiResponse {
  events: EventData[];
  total: number;
  source: string;
}

export default function Home() {
  const [events, setEvents] = useState<EventData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      console.log('Page: Fetching events...');
      try {
        const response = await fetch('/api/events');
        console.log('Page: Response status:', response.status);
        if (!response.ok) {
          throw new Error('Failed to fetch events');
        }
        const data: ApiResponse = await response.json();
        console.log('Page: Received data:', data);
        setEvents(data.events);
      } catch (err) {
        console.error('Error fetching events:', err);
        setError(err instanceof Error ? err.message : 'Failed to load events');
        // Fallback to sample data
        setEvents([
          {
            title: "Quantum Computing Symposium",
            institution: "Columbia University",
            date: "October 25, 2025",
            location: "Davis Auditorium",
            category: ["SCIENCE", "TECH"],
            description: "Join leading researchers in quantum computing for presentations on the latest breakthroughs in quantum algorithms, hardware development, and practical applications."
          },
          {
            title: "Medieval Literature Conference",
            institution: "New York University",
            date: "November 2, 2025",
            location: "Bobst Library",
            category: ["ARTS", "CULTURE"],
            description: "An interdisciplinary conference exploring medieval texts through modern critical lenses, featuring presentations from scholars across multiple disciplines."
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading academic events...</p>
        </div>
      </div>
    );
  }

  if (error && events.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">Error: {error}</p>
          <p className="text-gray-600 dark:text-gray-400">Using sample data instead.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-2">
    <div className="container mx-auto px-4">
      

        <AcademicBook events={events} />

        <footer className="text-center mt-12 text-sm text-gray-500 dark:text-gray-400 space-y-2">
          <p>
            Built with Next.js and{' '}
            <a
              href="https://nodlik.github.io/StPageFlip/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
            >
              StPageFlip
            </a>
          </p>

        </footer>

      </div>
    </div>
  );
}
