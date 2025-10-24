'use client';

import { useEffect, useState } from 'react';
import AcademicBook from '@/components/AcademicBook';
import ProgressiveLoader from '@/components/ProgressiveLoader';
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
  const [showBook, setShowBook] = useState(false);

  const handleEventsLoaded = (loadedEvents: EventData[]) => {
    setEvents(loadedEvents);
  };

  const handleLoadingComplete = () => {
    setLoading(false);
    setShowBook(true);
  };

  if (loading) {
    return <ProgressiveLoader onEventsLoaded={handleEventsLoaded} onLoadingComplete={handleLoadingComplete} />;
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
        {showBook && <AcademicBook events={events} />}

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
