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
      const fetchStart = Date.now();
      console.log('📡 [ProgressiveLoader] Starting API fetch...');
      
      try {
        const response = await fetch('/api/events');
        const fetchTime = Date.now() - fetchStart;
        console.log(`✅ [ProgressiveLoader] API fetch complete in ${fetchTime}ms`);
        
        const parseStart = Date.now();
        const data = await response.json();
        const parseTime = Date.now() - parseStart;
        console.log(`✅ [ProgressiveLoader] JSON parsed (${data.events?.length || 0} events) in ${parseTime}ms`);
        
        const totalTime = Date.now() - fetchStart;
        console.log(`🏁 [ProgressiveLoader] Total load time: ${totalTime}ms`);
        
        onEventsLoaded(data.events);
        onLoadingComplete();
        setLoading(false);
      } catch (error) {
        const errorTime = Date.now() - fetchStart;
        console.error(`❌ [ProgressiveLoader] Error loading events after ${errorTime}ms:`, error);
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
