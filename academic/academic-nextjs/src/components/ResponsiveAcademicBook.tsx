'use client';

import { useEffect, useState } from 'react';
import AcademicBook from './AcademicBook';
import MobileAcademicBook from './MobileAcademicBook';
import { EventData } from '../types/events';

interface ResponsiveAcademicBookProps {
  events: EventData[];
}

export default function ResponsiveAcademicBook({ events }: ResponsiveAcademicBookProps) {
  const [isMobile, setIsMobile] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkScreenSize = () => {
      // Use 768px as the breakpoint for mobile
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      setIsLoading(false);
    };

    // Check initial screen size
    checkScreenSize();

    // Add resize listener
    window.addEventListener('resize', checkScreenSize);

    return () => {
      window.removeEventListener('resize', checkScreenSize);
    };
  }, []);

  // Show loading state while determining screen size
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner" style={{ width: 40, height: 40, border: '4px solid #374151', borderTop: '4px solid #3b82f6', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 1rem' }}></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Render mobile scrolling view for small screens
  if (isMobile) {
    return <MobileAcademicBook events={events} />;
  }

  // Render flipbook view for desktop
  return <AcademicBook events={events} />;
}
