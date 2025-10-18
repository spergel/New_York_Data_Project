'use client';

import { useEffect, useRef, useState } from 'react';
// @ts-ignore
import { PageFlip } from 'page-flip';
import { EventData, NavigationState, BookmarkData } from '../types/events';
import TableOfContents from './TableOfContents';
import PageContent from './PageContent';
import NavigationControls from './NavigationControls';
import BookmarkRibbon from './BookmarkRibbon';

interface AcademicBookProps {
  events: EventData[];
}

export default function AcademicBook({ events }: AcademicBookProps) {
  const bookRef = useRef<HTMLDivElement>(null);
  const pageFlipRef = useRef<PageFlip | null>(null);
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


  // Sort events by date, then category, then university
  const sortedEvents = events.sort((a, b) => {
    const dateA = new Date(a.date).getTime();
    const dateB = new Date(b.date).getTime();
    if (dateA !== dateB) return dateA - dateB;
    
    const categoryA = a.category || '';
    const categoryB = b.category || '';
    if (categoryA !== categoryB) return categoryA.localeCompare(categoryB);
    
    const universityA = a.institution;
    const universityB = b.institution;
    return universityA.localeCompare(universityB);
  });

  // Get unique institutions
  const institutions = [...new Set(events.map(e => cleanInstitutions(e.institution)))].sort();

  // Group events by institution for bookmarks
  const eventsPerPage = 3;
  const locationGroups: BookmarkData[] = institutions.map(institution => ({
    institution,
    count: events.filter(e => cleanInstitutions(e.institution) === institution).length,
    firstPageIndex: 0 // Will be calculated properly
  }));

  // Navigation handlers
  const handleGoToPage = (pageNumber: number) => {
    if (pageFlipRef.current) {
      pageFlipRef.current.flip(pageNumber);
      setNavigationState(prev => ({
        ...prev,
        currentPage: pageNumber
      }));
    }
  };

  const handleGoToFirstPage = () => {
    handleGoToPage(0);
    setNavigationState(prev => ({
      ...prev,
      currentSection: 'all',
      currentInstitution: undefined
    }));
  };

  const handleGoToTableOfContents = () => {
    handleGoToPage(0);
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
      
      setNavigationState(prev => ({
        ...prev,
        currentSection: 'institution',
        currentInstitution: cleanInstitution
      }));
      
      // Navigate to the correct page (institutionStartPage is already 0-based)
      handleGoToPage(institutionStartPage);
    }
  };

  const handleBookmarkClick = (institution: string) => {
    handleInstitutionClick(institution);
  };

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
        handleGoToPage(pageNum);
      };
      (window as any).bookmarkClick = (institution: string) => {
        console.log('Global bookmarkClick called with:', institution);
        handleBookmarkClick(institution);
      };
      (window as any).institutionClick = (institution: string) => {
        console.log('Global institutionClick called with:', institution);
        handleInstitutionClick(institution);
      };

      // Generate pages dynamically for events (3-4 events per page) with integrated bookmarks
      const generatePagesHTML = () => {
        let pagesHTML = '';
        let currentPageIndex = 0;

        // Create institution bookmarks HTML
        const bookmarkRibbonHTML = locationGroups
          .sort((a, b) => a.institution.localeCompare(b.institution))
          .map((bookmark) => `
            <div class="book-bookmark" onclick="window.bookmarkClick('${bookmark.institution}')" title="${bookmark.institution} (${bookmark.count} events)">
              <span class="bookmark-label">${bookmark.institution.length > 12 ? `${bookmark.institution.substring(0, 10)}...` : bookmark.institution}</span>
              <span class="bookmark-number">(${bookmark.count})</span>
            </div>
          `).join('');

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
                ${!isEvenPage ? `
                <div class="book-bookmarks-container">
                  ${bookmarkRibbonHTML}
                </div>
                ` : ''}

                <div class="page-main-content ${!isEvenPage ? 'has-bookmarks' : ''}">
                  <h2 class="page-header">ALL EVENTS</h2>
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
                        <p class="event-description">${event.description}</p>
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
                  ${!isEvenPage ? `
                  <div class="book-bookmarks-container">
                    ${bookmarkRibbonHTML}
                  </div>
                  ` : ''}

                    <div class="page-main-content ${!isEvenPage ? 'has-bookmarks' : ''}">
                      <h2 class="page-header">${institution.toUpperCase()}</h2>
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
                          <p class="event-description">${event.description}</p>
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
      {/* Book Container with Integrated Bookmarks */}
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
