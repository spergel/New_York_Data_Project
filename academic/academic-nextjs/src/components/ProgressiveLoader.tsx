'use client';

import { useState, useEffect } from 'react';
import { EventData } from '../types/events';
import LoadingSkeleton from './LoadingSkeleton';

interface ProgressiveLoaderProps {
  onEventsLoaded: (events: EventData[]) => void;
  onLoadingComplete: () => void;
}

export default function ProgressiveLoader({ onEventsLoaded, onLoadingComplete }: ProgressiveLoaderProps) {
  const [loading, setLoading] = useState(true);
  const [loadingMessage, setLoadingMessage] = useState('Loading events...');

  useEffect(() => {
    const loadEvents = async () => {
      try {
        setLoadingMessage('Fetching events from NYC institutions...');
        const response = await fetch('/api/events?limit=1000'); // Load all events (high limit)
        const data = await response.json();
        
        setLoadingMessage(`Loaded ${data.events.length} of ${data.total} events`);
        
        onEventsLoaded(data.events);
        onLoadingComplete();
        setLoading(false);
      } catch (error) {
        console.error('Error loading events:', error);
        setLoadingMessage('Error loading events. Using fallback data.');
        setLoading(false);
      }
    };

    loadEvents();
  }, [onEventsLoaded, onLoadingComplete]);

  if (!loading) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Progress message */}
      <div className="text-center py-8">
        <div className="inline-flex items-center gap-3 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
          <span className="text-gray-700 dark:text-gray-300">{loadingMessage}</span>
        </div>
      </div>
      
      {/* Skeleton cards */}
      <LoadingSkeleton />
    </div>
  );
}
