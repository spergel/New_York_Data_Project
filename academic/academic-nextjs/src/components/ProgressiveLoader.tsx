'use client';

import { useState, useEffect } from 'react';
import { EventData } from '../types/events';

interface ProgressiveLoaderProps {
  onEventsLoaded: (events: EventData[]) => void;
  onLoadingComplete: () => void;
}

export default function ProgressiveLoader({ onEventsLoaded, onLoadingComplete }: ProgressiveLoaderProps) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const response = await fetch('/api/events');
        const data = await response.json();
        
        onEventsLoaded(data.events);
        onLoadingComplete();
        setLoading(false);
      } catch (error) {
        console.error('Error loading events:', error);
        setLoading(false);
      }
    };

    loadEvents();
  }, [onEventsLoaded, onLoadingComplete]);

  if (!loading) return null;

  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
        <h2>Loading Academic Events</h2>
        <p>Discovering events from NYC institutions...</p>
      </div>
    </div>
  );
}
