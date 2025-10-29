'use client';

import { EventData } from '../types/events';
import { sanitizeHtml, sanitizeTitle, escapeForJS } from '../utils/htmlSanitizer';

interface PageGeneratorProps {
  events: EventData[];
  institutions: string[];
  categories: string[];
  shouldShowBackButton: boolean;
  backButtonSide: 'left' | 'right';
}

export class PageGenerator {
  private events: EventData[];
  private institutions: string[];
  private categories: string[];
  private shouldShowBackButton: boolean;
  private backButtonSide: 'left' | 'right';

  constructor(props: PageGeneratorProps) {
    this.events = props.events;
    this.institutions = props.institutions;
    this.categories = props.categories;
    this.shouldShowBackButton = props.shouldShowBackButton;
    this.backButtonSide = props.backButtonSide;
  }

  // Clean up organizations - group departments under parent institutions
  private cleanInstitutions = (institution: string) => {
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
  private getSortedEvents = () => {
    return this.events.sort((a, b) => {
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
  };

  generatePagesHTML = (): string => {
    const generationStart = Date.now();
    console.log('📄 [PageGenerator] Starting page HTML generation...');
    
    const sortedEvents = this.getSortedEvents();
    const eventsPerPage = 3;
    let pagesHTML = '';

    // Calculate page structure first
    const calcStart = Date.now();
    const tocItemsPerPage = 8;
    const totalTocItems = 1 + this.institutions.length + this.categories.length; // All Events + institutions + categories
    const tocPages = Math.ceil(totalTocItems / tocItemsPerPage);
    const allEventsPages = Math.ceil(sortedEvents.length / eventsPerPage);
    
    // Calculate institution pages
    const institutionPageCounts = this.institutions.map(inst => {
      const institutionEvents = sortedEvents.filter(e => this.cleanInstitutions(e.institution) === inst);
      return Math.ceil(institutionEvents.length / eventsPerPage);
    });

    // Calculate category pages
    const categoryPageCounts = this.categories.map(cat => {
      const categoryEvents = sortedEvents.filter(e => e.category && e.category.includes(cat));
      return Math.ceil(categoryEvents.length / eventsPerPage);
    });
    
    const totalInstitutionPages = institutionPageCounts.reduce((sum, count) => sum + count, 0);
    const totalCategoryPages = categoryPageCounts.reduce((sum, count) => sum + count, 0);
    
    // Calculate actual TOC pages (including blank page if needed)
    const actualTocPages = tocPages + (tocPages % 2 === 1 ? 1 : 0);
    const calcTime = Date.now() - calcStart;
    console.log(`✅ [PageGenerator] Page calculations complete in ${calcTime}ms (${actualTocPages} TOC pages, ${allEventsPages} event pages)`);
    
    // Create table of contents items with correct page numbers
    // +1 to account for the publisher's page
    const allTocItems = [
      { type: 'all', name: 'All Events', count: this.events.length, color: '#3b82f6', page: actualTocPages + 1 + 1 },
      ...this.institutions.map((inst, index) => {
        const institutionStartPage = actualTocPages + allEventsPages + 
          institutionPageCounts.slice(0, index).reduce((sum, count) => sum + count, 0);
        return {
          type: 'institution', 
          name: inst, 
          count: sortedEvents.filter(e => this.cleanInstitutions(e.institution) === inst).length, 
          color: '#10b981',
          page: institutionStartPage + 1 + 1
        };
      }),
      ...this.categories.map((cat, index) => {
        const categoryStartPage = actualTocPages + allEventsPages + totalInstitutionPages +
          categoryPageCounts.slice(0, index).reduce((sum, count) => sum + count, 0);
        return {
          type: 'category',
          name: cat,
          count: sortedEvents.filter(e => e.category && e.category.includes(cat)).length,
          color: '#f59e0b',
          page: categoryStartPage + 1 + 1
        };
      })
    ];

    // Add publisher's page
    pagesHTML += this.generatePublisherPage();

    // Add table of contents pages
    pagesHTML += this.generateTocPages(allTocItems, tocItemsPerPage, tocPages);

    // Add main events section
    pagesHTML += this.generateAllEventsPages(sortedEvents, eventsPerPage, actualTocPages);

    // Add institution-specific sections
    pagesHTML += this.generateInstitutionPages(sortedEvents, eventsPerPage, actualTocPages, allEventsPages, institutionPageCounts);

    // Add category-specific sections
    pagesHTML += this.generateCategoryPages(sortedEvents, eventsPerPage, actualTocPages, allEventsPages, totalInstitutionPages, categoryPageCounts);

    const totalTime = Date.now() - generationStart;
    const htmlSize = new Blob([pagesHTML]).size;
    console.log(`🏁 [PageGenerator] HTML generation complete: ${(htmlSize / 1024).toFixed(2)} KB in ${totalTime}ms`);

    return pagesHTML;
  };

  private generatePublisherPage = (): string => {
    return `
      <div class="page">
        <div class="page-content">
          <div class="page-main-content">
            <h2 class="page-header">PUBLISHER</h2>
            <div class="paint-thing-graphic">
              <svg viewBox="0 0 100 60" class="paint-flame">
                <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
              </svg>
            </div>
            <div class="page-text">
              <div class="publisher-content">
                <div class="publisher-logo">
                  <h3 style="color: #dc2626; margin-bottom: 1rem; font-size: 1.5rem;">SomethingToDo</h3>
                </div>
                <div class="publisher-description">
                  <p style="margin-bottom: 1.5rem; line-height: 1.6;">
                    <strong>Joshua Spergel</strong> is a New York-based developer and data enthusiast passionate about discovering and sharing events across the city. With a keen interest in web scraping and data collection, Joshua creates tools to help people find interesting academic, tech, and cultural events happening in NYC.
                  </p>
                  <p style="margin-bottom: 1.5rem; line-height: 1.6;">
                    Through his work, Joshua aims to connect the academic and tech communities by making event discovery more accessible and enjoyable.
                  </p>
                  <div class="publisher-links" style="margin-bottom: 1.5rem;">
                    <p><strong>Visit our sites:</strong></p>
                    <ul style="list-style: none; padding: 0;">
                      <li style="margin-bottom: 0.5rem;">
                        <a href="https://somethingtodo.nyc" target="_blank" style="color: #3b82f6; text-decoration: none; border-bottom: 1px solid #3b82f6;">
                          somethingtodo.nyc
                        </a>
                        <span style="color: #6b7280; margin-left: 0.5rem;">- Academic & Cultural Events</span>
                      </li>
                      <li>
                        <a href="https://tech.somethingtodo.nyc" target="_blank" style="color: #10b981; text-decoration: none; border-bottom: 1px solid #10b981;">
                          tech.somethingtodo.nyc
                        </a>
                        <span style="color: #6b7280; margin-left: 0.5rem;">- Tech & Startup Events</span>
                      </li>
                    </ul>
                  </div>
                  <div class="publisher-contact">
                    <p style="margin-bottom: 0.5rem;"><strong>Contact:</strong></p>
                    <p style="color: #6b7280;">
                      Email: <a href="mailto:spergel.joshua@gmail.com" style="color: #3b82f6; text-decoration: none;">spergel.joshua@gmail.com</a>
                    </p>
                    <p style="color: #6b7280;">
                      Location: New York, NY
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div class="page-footer">i</div>
          </div>
        </div>
      </div>
    `;
  };

  private generateTocPages = (allTocItems: any[], tocItemsPerPage: number, tocPages: number): string => {
    let pagesHTML = '';

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
                  ${tocPageItems.map(item => {
                    let clickHandler = '';
                    if (item.type === 'all') {
                      clickHandler = `window.goToPage(${item.page - 1})`;
                    } else if (item.type === 'institution') {
                      clickHandler = `window.institutionClick('${escapeForJS(item.name)}')`;
                    } else if (item.type === 'category') {
                      clickHandler = `window.categoryClick('${escapeForJS(item.name)}')`;
                    }
                    return `
                    <div class="toc-entry" onclick="${clickHandler}" style="cursor: pointer;">
                      <span class="toc-title" style="color: ${item.color};">${item.name} (${item.count})</span>
                      <span class="toc-dots"></span>
                      <span class="toc-page">${item.page}</span>
                    </div>
                    `;
                  }).join('')}
                </div>
              </div>
              <div class="page-footer">${tocPageNumber}</div>
            </div>
          </div>
        </div>
      `;
    }

    // Ensure TOC has even number of pages by adding blank page if needed
    if (tocPages % 2 === 1) {
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
                  <div class="toc-entry" style="text-align: center; padding: 2rem;">
                    <span class="toc-title" style="color: #6b7280; font-style: italic;">(Continued on next page)</span>
                  </div>
                </div>
              </div>
              <div class="page-footer">${tocPages + 1}</div>
            </div>
          </div>
        </div>
      `;
    }

    return pagesHTML;
  };

  private generateAllEventsPages = (sortedEvents: EventData[], eventsPerPage: number, actualTocPages: number): string => {
    let pagesHTML = '';
    let globalPageNumber = actualTocPages + 1; // Start after TOC pages

    for (let pageIndex = 0; pageIndex < sortedEvents.length; pageIndex += eventsPerPage) {
      const pageEvents = sortedEvents.slice(pageIndex, pageIndex + eventsPerPage);
      const shouldShowRibbon = globalPageNumber % 2 === 0;

      pagesHTML += `
        <div class="page">
          <div class="page-content">
            <div class="page-main-content">
              ${this.shouldShowBackButton && this.backButtonSide === 'left' ? `
              <div class="dynamic-back-button left">
                <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                  ← Back
                </button>
              </div>
              ` : ''}
              <h2 class="page-header">ALL EVENTS</h2>
              ${this.shouldShowBackButton && this.backButtonSide === 'right' ? `
              <div class="dynamic-back-button right">
                <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                  Back →
                </button>
              </div>
              ` : ''}
              ${shouldShowRibbon ? `
              <div class="page-bookmark" onclick="window.goToPage(0)" title="Go to Table of Contents" style="cursor: pointer;">
                <div class="page-bookmark-inner">
                  <span class="page-bookmark-text">Table of Contents</span>
                </div>
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
                    <h3 class="event-title ${event.source_url ? 'clickable-event' : ''}" ${event.source_url ? `onclick="window.open('${event.source_url}', '_blank')"` : ''}>${sanitizeTitle(event.title)}</h3>
                    <div class="event-meta">
                      <p><strong class="clickable-institution" onclick="window.institutionClick('${escapeForJS(event.institution)}')" style="cursor: pointer; color: #3b82f6;">${event.institution}</strong> • <em>${event.date}</em></p>
                      ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                      ${event.category && event.category.length > 0 ? `<p><strong>Categories:</strong> ${event.category.map(cat => `<span class="clickable-category" onclick="window.categoryClick('${escapeForJS(cat)}')" style="cursor: pointer; color: #f59e0b;">${cat}</span>`).join(', ')}</p>` : ''}
                    </div>
                    <div class="event-description">${sanitizeHtml(event.description)}</div>
                  </div>
                `).join('')}
              </div>
              <div class="page-footer">${globalPageNumber}</div>
            </div>
          </div>
        </div>
      `;
      globalPageNumber++; // Increment global page number
    }

    return pagesHTML;
  };

  private generateInstitutionPages = (sortedEvents: EventData[], eventsPerPage: number, actualTocPages: number, allEventsPages: number, institutionPageCounts: number[]): string => {
    let pagesHTML = '';
    let globalPageNumber = actualTocPages + allEventsPages + 1;

    this.institutions.forEach((institution) => {
      const institutionEvents = sortedEvents.filter(event => this.cleanInstitutions(event.institution) === institution);

      for (let pageIndex = 0; pageIndex < institutionEvents.length; pageIndex += eventsPerPage) {
        const pageEvents = institutionEvents.slice(pageIndex, pageIndex + eventsPerPage);
        const shouldShowRibbon = globalPageNumber % 2 === 0;

        pagesHTML += `
          <div class="page">
            <div class="page-content">
              <div class="page-main-content">
                ${this.shouldShowBackButton && this.backButtonSide === 'left' ? `
                <div class="dynamic-back-button left">
                  <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                    ← Back
                  </button>
                </div>
                ` : ''}
                <h2 class="page-header">${institution.toUpperCase()}</h2>
                ${this.shouldShowBackButton && this.backButtonSide === 'right' ? `
                <div class="dynamic-back-button right">
                  <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                    Back →
                  </button>
                </div>
                ` : ''}
                ${shouldShowRibbon ? `
                <div class="page-bookmark" onclick="window.goToPage(0)" title="Go to Table of Contents" style="cursor: pointer;">
                  <div class="page-bookmark-inner">
                    <span class="page-bookmark-text">Table of Contents</span>
                  </div>
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
                      <h3 class="event-title ${event.source_url ? 'clickable-event' : ''}" ${event.source_url ? `onclick="window.open('${event.source_url}', '_blank')"` : ''}>${sanitizeTitle(event.title)}</h3>
                      <div class="event-meta">
                        <p><strong class="clickable-institution" onclick="window.institutionClick('${escapeForJS(event.institution)}')" style="cursor: pointer; color: #3b82f6;">${event.institution}</strong> • <em>${event.date}</em></p>
                        ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                        ${event.category && event.category.length > 0 ? `<p><strong>Categories:</strong> ${event.category.map(cat => `<span class="clickable-category" onclick="window.categoryClick('${escapeForJS(cat)}')" style="cursor: pointer; color: #f59e0b;">${cat}</span>`).join(', ')}</p>` : ''}
                      </div>
                      <div class="event-description">${sanitizeHtml(event.description)}</div>
                    </div>
                  `).join('')}
                </div>
                <div class="page-footer">${globalPageNumber}</div>
              </div>
            </div>
          </div>
        `;
        globalPageNumber++; // Increment global page number
      }
    });

    return pagesHTML;
  };

  private generateCategoryPages = (sortedEvents: EventData[], eventsPerPage: number, actualTocPages: number, allEventsPages: number, totalInstitutionPages: number, categoryPageCounts: number[]): string => {
    let pagesHTML = '';
    let globalPageNumber = actualTocPages + allEventsPages + totalInstitutionPages + 1;

    this.categories.forEach((category) => {
      const categoryEvents = sortedEvents.filter(event =>
        event.category && event.category.includes(category)
      );

      for (let pageIndex = 0; pageIndex < categoryEvents.length; pageIndex += eventsPerPage) {
        const pageEvents = categoryEvents.slice(pageIndex, pageIndex + eventsPerPage);
        const shouldShowRibbon = globalPageNumber % 2 === 0;

        pagesHTML += `
          <div class="page">
            <div class="page-content">
              <div class="page-main-content">
                ${this.shouldShowBackButton && this.backButtonSide === 'left' ? `
                <div class="dynamic-back-button left">
                  <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                    ← Back
                  </button>
                </div>
                ` : ''}
                <h2 class="page-header" style="color: #f59e0b;">${category.toUpperCase()}</h2>
                ${this.shouldShowBackButton && this.backButtonSide === 'right' ? `
                <div class="dynamic-back-button right">
                  <button class="back-btn" onclick="window.goBack()" title="Go back to previous page">
                    Back →
                  </button>
                </div>
                ` : ''}
                ${shouldShowRibbon ? `
                <div class="page-bookmark" onclick="window.goToPage(0)" title="Go to Table of Contents" style="cursor: pointer;">
                  <div class="page-bookmark-inner">
                    <span class="page-bookmark-text">Table of Contents</span>
                  </div>
                </div>
                ` : ''}
                <div class="paint-thing-graphic">
                  <svg viewBox="0 0 100 60" class="paint-flame">
                    <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#f59e0b" opacity="0.8"/>
                    <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#fbbf24" opacity="0.7"/>
                  </svg>
                </div>
                <div class="page-text">
                  ${pageEvents.map((event, eventIndex) => `
                    <div class="event-item ${eventIndex > 0 ? 'event-separator' : ''}">
                      <h3 class="event-title ${event.source_url ? 'clickable-event' : ''}" ${event.source_url ? `onclick="window.open('${event.source_url}', '_blank')"` : ''}>${sanitizeTitle(event.title)}</h3>
                      <div class="event-meta">
                        <p><strong class="clickable-institution" onclick="window.institutionClick('${escapeForJS(event.institution)}')" style="cursor: pointer; color: #10b981;">${event.institution}</strong> • <em>${event.date}</em></p>
                        ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                        ${event.category && event.category.length > 0 ? `<p><strong>Categories:</strong> ${event.category.map(cat => `<span class="clickable-category" onclick="window.categoryClick('${escapeForJS(cat)}')" style="cursor: pointer; color: #f59e0b;">${cat}</span>`).join(', ')}</p>` : ''}
                      </div>
                      <div class="event-description">${sanitizeHtml(event.description)}</div>
                    </div>
                  `).join('')}
                </div>
                <div class="page-footer">${globalPageNumber}</div>
              </div>
            </div>
          </div>
        `;
        globalPageNumber++; // Increment global page number
      }
    });

    return pagesHTML;
  };
}
