'use client';

import { useEffect, useRef } from 'react';
import { EventData } from '../types/events';
import { MobilePageGenerator } from './MobilePageGenerator';

interface MobileAcademicBookProps {
  events: EventData[];
}

export default function MobileAcademicBook({ events }: MobileAcademicBookProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Clean up organizations - group departments under parent institutions
  const cleanInstitutions = (institution: string) => {
    const name = institution.toLowerCase();
    if (name.includes('nyu') || name.includes('new york university') || name.includes('isaw')) return 'New York University';
    if (name.includes('columbia')) return 'Columbia University';
    if (name.includes('cornell')) return 'Cornell University';
    if (name.includes('cooper union')) return 'Cooper Union';
    if (name.includes('pratt')) return 'Pratt Institute';
    if (name.includes('juilliard')) return 'Juilliard School';
    if (name.includes('new school')) return 'The New School';
    if (name.includes('simons')) return 'Simons Foundation';
    if (name.includes('jtsa') || name.includes('jewish theological')) return 'Jewish Theological Seminary';
    return institution;
  };

  // Get unique institutions and categories
  const institutions = [...new Set(events.map(e => cleanInstitutions(e.institution)))].sort();
  const categories = [...new Set(events.flatMap(e => e.category || []))].sort();

  // Initialize scroll functions
  useEffect(() => {
    const scrollToSection = (sectionId: string) => {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    };

    const scrollToInstitution = (institutionName: string) => {
      const sectionId = `institution-${institutionName.toLowerCase().replace(/\s+/g, '-')}`;
      scrollToSection(sectionId);
    };

    const scrollToCategory = (categoryName: string) => {
      const sectionId = `category-${categoryName.toLowerCase().replace(/\s+/g, '-')}`;
      scrollToSection(sectionId);
    };

    // Make functions globally available
    (window as any).scrollToSection = scrollToSection;
    (window as any).scrollToInstitution = scrollToInstitution;
    (window as any).scrollToCategory = scrollToCategory;

    return () => {
      // Cleanup
      delete (window as any).scrollToSection;
      delete (window as any).scrollToInstitution;
      delete (window as any).scrollToCategory;
    };
  }, []);

  const generator = new MobilePageGenerator({
    events,
    institutions,
    categories
  });

  const mobileHTML = generator.generateMobileHTML();

  return (
    <div className="mobile-book-container" ref={containerRef}>
      <div
        className="mobile-book-content"
        dangerouslySetInnerHTML={{ __html: mobileHTML }}
      />

      {/* Floating back to top button */}
      <button
        className="mobile-back-to-top"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        aria-label="Back to top"
      >
        ↑
      </button>
    </div>
  );
}
