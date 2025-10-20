'use client';

import { useEffect, useRef } from 'react';
// @ts-ignore
import { PageFlip } from 'page-flip';
import { EventData } from '../types/events';
import NavigationControls from './NavigationControls';
import { useEventProcessing } from '../hooks/useEventProcessing';
import { useNavigation } from '../hooks/useNavigation';
import { createNavigationHandlers } from './NavigationHandlers';
import { generatePagesHTML } from './PageGenerator';
import { sanitizeHtml } from '../utils/htmlSanitizer';

interface AcademicBookProps {
  events: EventData[];
}

export default function AcademicBook({ events }: AcademicBookProps) {
  const bookRef = useRef<HTMLDivElement>(null);
  const pageFlipRef = useRef<PageFlip | null>(null);
  const navigationHistoryRef = useRef<number[]>([]);
  const [navigationState, setNavigationState] = useState<NavigationState>({
    currentPage: 0,
    history: [],
    currentSection: 'all'
  });

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
    return institution; // Keep original if no match
  };


  // Sort events by date only (chronological order)
  const sortedEvents = events.sort((a, b) => {
    // Parse dates more robustly
    const parseDate = (dateStr: string) => {
      if (!dateStr) return new Date(0); // Default to epoch for invalid dates
      
      // Try to parse the date string
      const parsed = new Date(dateStr);
      if (isNaN(parsed.getTime())) {
        // If parsing fails, try to extract date parts manually
        const match = dateStr.match(/(\w+)\s+(\d+),\s+(\d+)/);
        if (match) {
          const [, month, day, year] = match;
          const monthIndex = new Date(`${month} 1, 2000`).getMonth();
          return new Date(parseInt(year), monthIndex, parseInt(day));
        }
        return new Date(0);
      }
      return parsed;
    };
    
    const dateA = parseDate(a.date);
    const dateB = parseDate(b.date);
    
    // Sort by date (earliest first)
    return dateA.getTime() - dateB.getTime();
  });

  // Debug: Log first few events to see sorting
  console.log('First 5 events after sorting:');
  sortedEvents.slice(0, 5).forEach((event, index) => {
    console.log(`${index + 1}. ${event.title} - ${event.date} (${event.institution})`);
  });

  // Get unique institutions
  const institutions = [...new Set(events.map(e => cleanInstitutions(e.institution)))].sort();

  // Group events by institution
  const eventsPerPage = 3;

  // Navigation handlers
  const handleGoToPage = (pageNumber: number, isBigJump: boolean = false) => {
    if (pageFlipRef.current) {
      // Store current page in history if it's a big jump
      if (isBigJump && navigationState.currentPage !== pageNumber) {
        navigationHistoryRef.current.push(navigationState.currentPage);
        console.log('Stored page in history:', navigationState.currentPage, 'History:', navigationHistoryRef.current);
      }
      
      pageFlipRef.current.flip(pageNumber);
      setNavigationState(prev => ({
        ...prev,
        currentPage: pageNumber
      }));
    }
  };

  const handleGoToFirstPage = () => {
    handleGoToPage(0, true);
    setNavigationState(prev => ({
      ...prev,
      currentSection: 'all',
      currentInstitution: undefined
    }));
  };

  const handleGoToTableOfContents = () => {
    handleGoToPage(0, true);
  };


  const handleInstitutionClick = (institution: string) => {
    const cleanInstitution = cleanInstitutions(institution);
    const institutionEvents = sortedEvents.filter(event => cleanInstitutions(event.institution) === cleanInstitution);
    
    if (institutionEvents.length > 0) {
      // Calculate correct page numbers using the same logic as page generation
      const tocItemsPerPage = 8;
      const totalTocItems = 1 + institutions.length;
      const tocPages = Math.ceil(totalTocItems / tocItemsPerPage);
      const allEventsPages = Math.ceil(sortedEvents.length / eventsPerPage);
      
      // Calculate institution pages
      const institutionPageCounts = institutions.map(inst => {
        const instEvents = sortedEvents.filter(e => cleanInstitutions(e.institution) === inst);
        return Math.ceil(instEvents.length / eventsPerPage);
      });
      
      const institutionIndex = institutions.indexOf(cleanInstitution);
      const institutionStartPage = tocPages + allEventsPages + 
        institutionPageCounts.slice(0, institutionIndex).reduce((sum, count) => sum + count, 0);
      
      console.log('Navigating to institution:', cleanInstitution, 'at page:', institutionStartPage);
      console.log('Page structure:', { tocPages, allEventsPages, institutionStartPage });
      console.log('Institution index:', institutionIndex, 'Page counts:', institutionPageCounts);
      console.log('TOC would show page:', institutionStartPage + 1);
      
      setNavigationState(prev => ({
        ...prev,
        currentSection: 'institution',
        currentInstitution: cleanInstitution
      }));
      
      // Navigate to the correct page (institutionStartPage is 0-based, same as PageFlip)
      handleGoToPage(institutionStartPage, true);
    }
  };


  const handleGoBack = () => {
    console.log('Go back called, history:', navigationHistoryRef.current);
    if (navigationHistoryRef.current.length > 0) {
      const previousPage = navigationHistoryRef.current.pop();
      console.log('Going back to page:', previousPage);
      
      if (pageFlipRef.current && previousPage !== undefined) {
        pageFlipRef.current.flip(previousPage);
        setNavigationState(prev => ({
          ...prev,
          currentPage: previousPage,
          currentSection: 'all',
          currentInstitution: undefined
        }));
      }
    } else {
      console.log('No history to go back to');
    }
  };

  // Determine if back button should be shown and on which side
  const shouldShowBackButton = navigationHistoryRef.current.length > 0;
  const isCurrentPageEven = navigationState.currentPage % 2 === 0;
  const backButtonSide = isCurrentPageEven ? 'right' : 'left';

  // Arrow key navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (pageFlipRef.current) {
        if (event.key === 'ArrowLeft') {
          event.preventDefault();
          pageFlipRef.current.flipPrev();
        } else if (event.key === 'ArrowRight') {
          event.preventDefault();
          pageFlipRef.current.flipNext();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (bookRef.current && events.length > 0) {
      console.log('Setting up dynamic book with', events.length, 'events...');

      // Set up global handlers BEFORE generating HTML
      (window as any).goToPage = (pageNum: number) => {
        console.log('Global goToPage called with:', pageNum);
        handleGoToPage(pageNum, true); // TOC entries are big jumps
      };
      (window as any).institutionClick = (institution: string) => {
        console.log('Global institutionClick called with:', institution);
        handleInstitutionClick(institution);
      };
      (window as any).goBack = () => {
        console.log('Global goBack called');
        handleGoBack();
      };

      // Generate pages dynamically for events (3-4 events per page) with integrated bookmarks
      const generatePagesHTML = () => {
        let pagesHTML = '';
        let currentPageIndex = 0;

        // No internal bookmarks - moved to external sidebar

        // Calculate page structure first
        const tocItemsPerPage = 8;
        const totalTocItems = 1 + institutions.length; // All Events + institutions
        const tocPages = Math.ceil(totalTocItems / tocItemsPerPage);
        const allEventsPages = Math.ceil(sortedEvents.length / eventsPerPage);
        
        // Calculate institution pages
        const institutionPageCounts = institutions.map(inst => {
          const institutionEvents = sortedEvents.filter(e => cleanInstitutions(e.institution) === inst);
          return Math.ceil(institutionEvents.length / eventsPerPage);
        });
        
        const totalInstitutionPages = institutionPageCounts.reduce((sum, count) => sum + count, 0);
        
        console.log('Page structure:', {
          tocPages,
          allEventsPages,
          totalInstitutionPages,
          totalPages: tocPages + allEventsPages + totalInstitutionPages,
          institutions: institutions.length,
          events: sortedEvents.length
        });
        
        // Create table of contents items with correct page numbers
        const allTocItems = [
          { type: 'all', name: 'All Events', count: events.length, color: '#3b82f6', page: tocPages + 1 },
          ...institutions.map((inst, index) => {
            const institutionStartPage = tocPages + allEventsPages + 
              institutionPageCounts.slice(0, index).reduce((sum, count) => sum + count, 0);
            return {
              type: 'institution', 
              name: inst, 
              count: sortedEvents.filter(e => cleanInstitutions(e.institution) === inst).length, 
              color: '#3b82f6',
              page: institutionStartPage + 1
            };
          })
        ];
        
        console.log('TOC items with page numbers:', allTocItems.map(item => ({
          name: item.name,
          page: item.page
        })));

        // Add table of contents pages
        for (let tocPageIndex = 0; tocPageIndex < allTocItems.length; tocPageIndex += tocItemsPerPage) {
          const tocPageItems = allTocItems.slice(tocPageIndex, tocPageIndex + tocItemsPerPage);
          const tocPageNumber = Math.floor(tocPageIndex / tocItemsPerPage) + 1;

          pagesHTML += `
            <div class="page">
              <div class="page-content">
                <div class="page-main-content">
                  <h2 class="page-header">TABLE OF CONTENTS</h2>
                  <div class="paint-thing-graphic">
                    <svg viewBox="0 0 100 60" class="paint-flame">
                      <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                      <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
                    </svg>
                  </div>
                  <div class="page-text">
                    <div class="book-toc">
                      ${tocPageItems.map(item => `
                        <div class="toc-entry" onclick="window.goToPage(${item.page - 1})">
                          <span class="toc-title">${item.name}</span>
                          <span class="toc-dots"></span>
                          <span class="toc-page">${item.page}</span>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                  <div class="page-footer">${tocPageNumber}</div>
                </div>
              </div>
            </div>
          `;
          currentPageIndex++;
        }

        // Add main events section (all events sorted by date)
        for (let pageIndex = 0; pageIndex < sortedEvents.length; pageIndex += eventsPerPage) {
          const pageEvents = sortedEvents.slice(pageIndex, pageIndex + eventsPerPage);
          const pageNumber = Math.floor(pageIndex / eventsPerPage) + 1;
          const isEvenPage = pageNumber % 2 === 0;

          pagesHTML += `
            <div class="page">
              <div class="page-content">
                <div class="page-main-content">
                  ${shouldShowBackButton && backButtonSide === 'left' ? `
                  <div class="dynamic-back-button left">
                    <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                      ← Back
                    </button>
                  </div>
                  ` : ''}
                  <h2 class="page-header">ALL EVENTS</h2>
                  ${shouldShowBackButton && backButtonSide === 'right' ? `
                  <div class="dynamic-back-button right">
                    <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                      Back →
                    </button>
                  </div>
                  ` : ''}
                  <div class="paint-thing-graphic">
                    <svg viewBox="0 0 100 60" class="paint-flame">
                      <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                      <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
                    </svg>
                  </div>
                  <div class="page-text">
                    ${pageEvents.map((event, eventIndex) => `
                      <div class="event-item ${eventIndex > 0 ? 'event-separator' : ''}">
                        <h3 class="event-title ${event.source_url ? 'clickable-event' : ''}" ${event.source_url ? `onclick="window.open('${event.source_url}', '_blank')"` : ''}>${event.title}</h3>
                        <div class="event-meta">
                          <p><strong class="clickable-institution" onclick="window.institutionClick('${event.institution}')" style="cursor: pointer; color: #3b82f6;">${event.institution}</strong> • <em>${event.date}</em></p>
                          ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                          ${event.category ? `<p><strong>Category:</strong> ${event.category}</p>` : ''}
                        </div>
                        <p class="event-description">${sanitizeHtml(event.description)}</p>
                      </div>
                    `).join('')}
                  </div>
                  <div class="page-footer">${pageNumber}</div>
                </div>
              </div>
            </div>
          `;
        }

        // Add institution-specific sections
        institutions.forEach((institution, institutionIndex) => {
          const institutionEvents = sortedEvents.filter(event => cleanInstitutions(event.institution) === institution);

          for (let pageIndex = 0; pageIndex < institutionEvents.length; pageIndex += eventsPerPage) {
            const pageEvents = institutionEvents.slice(pageIndex, pageIndex + eventsPerPage);
            const pageNumber = Math.floor(pageIndex / eventsPerPage) + 1;
            const isEvenPage = pageNumber % 2 === 0;

            pagesHTML += `
              <div class="page">
                <div class="page-content">
                  <div class="page-main-content">
                    ${shouldShowBackButton && backButtonSide === 'left' ? `
                    <div class="dynamic-back-button left">
                      <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                        ← Back
                      </button>
                    </div>
                    ` : ''}
                    <h2 class="page-header">${institution.toUpperCase()}</h2>
                    ${shouldShowBackButton && backButtonSide === 'right' ? `
                    <div class="dynamic-back-button right">
                      <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                        Back →
                      </button>
                    </div>
                    ` : ''}
                    <div class="paint-thing-graphic">
                      <svg viewBox="0 0 100 60" class="paint-flame">
                        <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                        <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
                      </svg>
                    </div>
                    <div class="page-text">
                      ${pageEvents.map((event, eventIndex) => `
                        <div class="event-item ${eventIndex > 0 ? 'event-separator' : ''}">
                          <h3 class="event-title ${event.source_url ? 'clickable-event' : ''}" ${event.source_url ? `onclick="window.open('${event.source_url}', '_blank')"` : ''}>${event.title}</h3>
                          <div class="event-meta">
                            <p><strong class="clickable-institution" onclick="window.institutionClick('${event.institution}')" style="cursor: pointer; color: #3b82f6;">${event.institution}</strong> • <em>${event.date}</em></p>
                            ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                            ${event.category ? `<p><strong>Category:</strong> ${event.category}</p>` : ''}
                          </div>
                          <p class="event-description">${sanitizeHtml(event.description)}</p>
                        </div>
                      `).join('')}
                    </div>
                    <div class="page-footer">${pageNumber}</div>
                  </div>
                </div>
              </div>
            `;
          }
        });

        return pagesHTML;
      };

      bookRef.current.innerHTML = generatePagesHTML();

      // Initialize PageFlip
      setTimeout(() => {
        if (bookRef.current) {
          console.log('Attempting to initialize PageFlip...');

          try {
            pageFlipRef.current = new PageFlip(bookRef.current, {
              width: 550,  // Base page width
              height: 733,  // Base page height
              size: 'fixed',  // Use fixed size for consistent layout
              minWidth: 315,
              maxWidth: 1100,
              minHeight: 420,
              maxHeight: 1350,
              showCover: false,  // No cover page
              usePortrait: false,  // Allow landscape spreads
              maxShadowOpacity: 0.5,
              mobileScrollSupport: false,
              flippingTime: 600,
              // Add click areas for proper page flipping
              clickAreaWidth: 50,  // Width of clickable area on each side
              clickAreaHeight: 100  // Height of clickable area
            });

            const pages = bookRef.current.querySelectorAll('.page');
            console.log('Found pages for PageFlip:', pages.length);

            if (pages.length > 0) {
              pageFlipRef.current.loadFromHTML(pages);
              console.log('PageFlip initialized successfully!');

              // Add event listeners
              pageFlipRef.current.on('flip', (e: any) => {
                console.log('Page flipped to:', e.data);
                setNavigationState(prev => ({
                  ...prev,
                  currentPage: e.data
                }));
              });

              pageFlipRef.current.on('changeState', (e: any) => {
                console.log('Book state changed to:', e.data);
              });

              // Debug info
              console.log('Total pages:', pageFlipRef.current.getPageCount());
              console.log('Current page:', pageFlipRef.current.getCurrentPageIndex());
            }
          } catch (error) {
            console.error('PageFlip failed:', error);
            // Fallback to static display
            bookRef.current.innerHTML = `
              <div style="width: 100%; height: 100%; background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; border-radius: 8px;">
                <h1 style="font-size: 2rem; font-weight: bold; margin-bottom: 1rem;">Academic Events Book</h1>
                <p style="font-size: 1.2rem; text-align: center;">${events.length} events loaded</p>
                <p style="font-size: 1rem; text-align: center; margin-top: 1rem;">PageFlip initialization failed</p>
              </div>
            `;
          }
        }
      }, 100);
    }

    return () => {
      if (pageFlipRef.current) {
        pageFlipRef.current.destroy();
      }
    };
  }, [events]);

  return (
    <div className="flex flex-col items-center space-y-4 p-4">
      {/* Book Container */}
      <div className="relative flex justify-center">
        <div
          ref={bookRef}
          className="book-container shadow-2xl rounded-lg overflow-hidden"
          style={{ width: '1100px', height: '733px', maxWidth: '100vw' }}
        />
      </div>

      {/* Navigation Controls */}
      <NavigationControls
        navigationState={navigationState}
        onGoToPage={handleGoToPage}
        onGoToFirstPage={handleGoToFirstPage}
        onGoToTableOfContents={handleGoToTableOfContents}
      />
    </div>
  );
}
