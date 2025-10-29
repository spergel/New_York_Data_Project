'use client';

import { EventData } from '../types/events';
import { sanitizeHtml, sanitizeTitle, escapeForJS } from '../utils/htmlSanitizer';

interface MobilePageGeneratorProps {
  events: EventData[];
  institutions: string[];
  categories: string[];
}

export class MobilePageGenerator {
  private events: EventData[];
  private institutions: string[];
  private categories: string[];

  constructor(props: MobilePageGeneratorProps) {
    this.events = props.events;
    this.institutions = props.institutions;
    this.categories = props.categories;
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

  generateMobileHTML = (): string => {
    const sortedEvents = this.getSortedEvents();
    let sectionsHTML = '';

    // Add publisher section
    sectionsHTML += this.generatePublisherSection();

    // Add table of contents section
    sectionsHTML += this.generateTocSection(sortedEvents);

    // Add main events section
    sectionsHTML += this.generateAllEventsSection(sortedEvents);

    // Add institution-specific sections
    sectionsHTML += this.generateInstitutionSections(sortedEvents);

    // Add category-specific sections
    sectionsHTML += this.generateCategorySections(sortedEvents);

    return sectionsHTML;
  };

  private generatePublisherSection = (): string => {
    return `
      <section id="publisher" class="mobile-section publisher-section">
        <div class="mobile-section-content">
          <div class="mobile-section-header">
            <h1 class="mobile-section-title">PUBLISHER</h1>
            <div class="mobile-paint-graphic">
              <svg viewBox="0 0 100 60" class="mobile-paint-flame">
                <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
              </svg>
            </div>
          </div>
          <div class="mobile-section-body">
            <div class="mobile-publisher-content">
              <div class="mobile-publisher-logo">
                <h2 style="color: #dc2626; margin-bottom: 1.5rem; font-size: 2rem;">SomethingToDo</h2>
              </div>
              <div class="mobile-publisher-description">
                <p style="margin-bottom: 1.5rem; line-height: 1.6; font-size: 1.1rem;">
                  <strong>Joshua Spergel</strong> is a New York-based developer and data enthusiast passionate about discovering and sharing events across the city. With a keen interest in web scraping and data collection, Joshua creates tools to help people find interesting academic, tech, and cultural events happening in NYC.
                </p>
                <p style="margin-bottom: 1.5rem; line-height: 1.6; font-size: 1.1rem;">
                  Through his work, Joshua aims to connect the academic and tech communities by making event discovery more accessible and enjoyable.
                </p>
                <div class="mobile-publisher-links" style="margin-bottom: 1.5rem;">
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
                <div class="mobile-publisher-contact">
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
        </div>
      </section>
    `;
  };

  private generateTocSection = (sortedEvents: EventData[]): string => {
    const tocItems = [
      { type: 'all', name: 'All Events', count: this.events.length, color: '#3b82f6', id: 'all-events' },
      ...this.institutions.map((inst) => ({
        type: 'institution',
        name: inst,
        count: sortedEvents.filter(e => this.cleanInstitutions(e.institution) === inst).length,
        color: '#10b981',
        id: `institution-${inst.toLowerCase().replace(/\s+/g, '-')}`
      })),
      ...this.categories.map((cat) => ({
        type: 'category',
        name: cat,
        count: sortedEvents.filter(e => e.category && e.category.includes(cat)).length,
        color: '#f59e0b',
        id: `category-${cat.toLowerCase().replace(/\s+/g, '-')}`
      }))
    ];

    return `
      <section id="toc" class="mobile-section toc-section">
        <div class="mobile-section-content">
          <div class="mobile-section-header">
            <h1 class="mobile-section-title">TABLE OF CONTENTS</h1>
            <div class="mobile-paint-graphic">
              <svg viewBox="0 0 100 60" class="mobile-paint-flame">
                <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
              </svg>
            </div>
          </div>
          <div class="mobile-section-body">
            <div class="mobile-toc">
              ${tocItems.map(item => {
                const clickHandler = item.type === 'all'
                  ? `window.scrollToSection('${item.id}')`
                  : item.type === 'institution'
                  ? `window.scrollToInstitution('${escapeForJS(item.name)}')`
                  : `window.scrollToCategory('${escapeForJS(item.name)}')`;
                return `
                <div class="mobile-toc-entry" onclick="${clickHandler}" style="cursor: pointer;">
                  <span class="mobile-toc-title" style="color: ${item.color};">${item.name} (${item.count})</span>
                  <span class="mobile-toc-arrow">→</span>
                </div>
                `;
              }).join('')}
            </div>
          </div>
        </div>
      </section>
    `;
  };

  private generateAllEventsSection = (sortedEvents: EventData[]): string => {
    return `
      <section id="all-events" class="mobile-section events-section">
        <div class="mobile-section-content">
          <div class="mobile-section-header">
            <h1 class="mobile-section-title">ALL EVENTS</h1>
            <div class="mobile-paint-graphic">
              <svg viewBox="0 0 100 60" class="mobile-paint-flame">
                <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
              </svg>
            </div>
          </div>
          <div class="mobile-section-body">
            <div class="mobile-events-grid">
              ${sortedEvents.map((event, index) => {
                const eventId = `event-${index}-${event.title.toLowerCase().replace(/\s+/g, '-').substring(0, 20)}`;
                return `
                <div class="mobile-event-card ${index > 0 ? 'mobile-event-separator' : ''}" data-event-id="${eventId}">
                  <div class="mobile-event-header" onclick="window.toggleEventDescription('${eventId}')" style="cursor: pointer;">
                    <div class="mobile-event-header-content">
                      <h3 class="mobile-event-title ${event.source_url ? 'mobile-clickable-event' : ''}"
                          ${event.source_url ? `onclick="event.stopPropagation(); window.open('${event.source_url}', '_blank')"` : 'onclick="event.stopPropagation(); window.toggleEventDescription(\'' + eventId + '\')"'}>
                        ${sanitizeTitle(event.title)}
                      </h3>
                      <div class="mobile-event-meta" onclick="event.stopPropagation();">
                        <p>
                          <strong class="mobile-clickable-institution"
                                 onclick="window.scrollToInstitution('${escapeForJS(event.institution)}')"
                                 style="cursor: pointer; color: #3b82f6;">
                            ${event.institution}
                          </strong> • <em>${event.date}</em>
                        </p>
                        ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                        ${event.category && event.category.length > 0 ? `<p><strong>Categories:</strong> ${event.category.map(cat => `<span class="mobile-clickable-category" onclick="window.scrollToCategory('${escapeForJS(cat)}')" style="cursor: pointer; color: #f59e0b;">${cat}</span>`).join(', ')}</p>` : ''}
                      </div>
                    </div>
                    <button class="mobile-event-expand-btn" aria-label="Toggle description" onclick="event.stopPropagation(); window.toggleEventDescription('${eventId}');">
                      <span class="mobile-event-expand-icon">></span>
                    </button>
                  </div>
                  <div class="mobile-event-description mobile-event-description-collapsed" id="${eventId}-description">
                    ${sanitizeHtml(event.description)}
                  </div>
                </div>
              `;
              }).join('')}
            </div>
          </div>
        </div>
      </section>
    `;
  };

  private generateInstitutionSections = (sortedEvents: EventData[]): string => {
    return this.institutions.map(institution => {
      const institutionEvents = sortedEvents.filter(event => this.cleanInstitutions(event.institution) === institution);
      const sectionId = `institution-${institution.toLowerCase().replace(/\s+/g, '-')}`;

      return `
        <section id="${sectionId}" class="mobile-section institution-section">
          <div class="mobile-section-content">
            <div class="mobile-section-header">
              <h1 class="mobile-section-title">${institution.toUpperCase()}</h1>
              <div class="mobile-paint-graphic">
                <svg viewBox="0 0 100 60" class="mobile-paint-flame">
                  <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#10b981" opacity="0.8"/>
                  <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#34d399" opacity="0.7"/>
                </svg>
              </div>
            </div>
            <div class="mobile-section-body">
              <div class="mobile-events-grid">
                ${institutionEvents.map((event, index) => {
                  const eventId = `inst-${institution.toLowerCase().replace(/\s+/g, '-')}-${index}-${event.title.toLowerCase().replace(/\s+/g, '-').substring(0, 20)}`;
                  return `
                  <div class="mobile-event-card ${index > 0 ? 'mobile-event-separator' : ''}" data-event-id="${eventId}">
                    <div class="mobile-event-header" onclick="window.toggleEventDescription('${eventId}')" style="cursor: pointer;">
                      <div class="mobile-event-header-content">
                        <h3 class="mobile-event-title ${event.source_url ? 'mobile-clickable-event' : ''}"
                            ${event.source_url ? `onclick="event.stopPropagation(); window.open('${event.source_url}', '_blank')"` : 'onclick="event.stopPropagation(); window.toggleEventDescription(\'' + eventId + '\')"'}>
                          ${sanitizeTitle(event.title)}
                        </h3>
                        <div class="mobile-event-meta" onclick="event.stopPropagation();">
                          <p>
                            <strong class="mobile-clickable-institution"
                                   onclick="window.scrollToInstitution('${escapeForJS(event.institution)}')"
                                   style="cursor: pointer; color: #10b981;">
                              ${event.institution}
                            </strong> • <em>${event.date}</em>
                          </p>
                          ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                          ${event.category && event.category.length > 0 ? `<p><strong>Categories:</strong> ${event.category.map(cat => `<span class="mobile-clickable-category" onclick="window.scrollToCategory('${escapeForJS(cat)}')" style="cursor: pointer; color: #f59e0b;">${cat}</span>`).join(', ')}</p>` : ''}
                        </div>
                      </div>
                      <button class="mobile-event-expand-btn" aria-label="Toggle description" onclick="event.stopPropagation(); window.toggleEventDescription('${eventId}');">
                        <span class="mobile-event-expand-icon">›</span>
                      </button>
                    </div>
                    <div class="mobile-event-description mobile-event-description-collapsed" id="${eventId}-description">
                      ${sanitizeHtml(event.description)}
                    </div>
                  </div>
                `;
                }).join('')}
              </div>
            </div>
          </div>
        </section>
      `;
    }).join('');
  };

  private generateCategorySections = (sortedEvents: EventData[]): string => {
    return this.categories.map(category => {
      const categoryEvents = sortedEvents.filter(event =>
        event.category && event.category.includes(category)
      );
      const sectionId = `category-${category.toLowerCase().replace(/\s+/g, '-')}`;

      return `
        <section id="${sectionId}" class="mobile-section category-section">
          <div class="mobile-section-content">
            <div class="mobile-section-header">
              <h1 class="mobile-section-title" style="color: #f59e0b;">${category.toUpperCase()}</h1>
              <div class="mobile-paint-graphic">
                <svg viewBox="0 0 100 60" class="mobile-paint-flame">
                  <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#f59e0b" opacity="0.8"/>
                  <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#fbbf24" opacity="0.7"/>
                </svg>
              </div>
            </div>
            <div class="mobile-section-body">
              <div class="mobile-events-grid">
                ${categoryEvents.map((event, index) => {
                  const eventId = `cat-${category.toLowerCase().replace(/\s+/g, '-')}-${index}-${event.title.toLowerCase().replace(/\s+/g, '-').substring(0, 20)}`;
                  return `
                  <div class="mobile-event-card ${index > 0 ? 'mobile-event-separator' : ''}" data-event-id="${eventId}">
                    <div class="mobile-event-header" onclick="window.toggleEventDescription('${eventId}')" style="cursor: pointer;">
                      <div class="mobile-event-header-content">
                        <h3 class="mobile-event-title ${event.source_url ? 'mobile-clickable-event' : ''}"
                            ${event.source_url ? `onclick="event.stopPropagation(); window.open('${event.source_url}', '_blank')"` : 'onclick="event.stopPropagation(); window.toggleEventDescription(\'' + eventId + '\')"'}>
                          ${sanitizeTitle(event.title)}
                        </h3>
                        <div class="mobile-event-meta" onclick="event.stopPropagation();">
                          <p>
                            <strong class="mobile-clickable-institution"
                                   onclick="window.scrollToInstitution('${escapeForJS(event.institution)}')"
                                   style="cursor: pointer; color: #10b981;">
                              ${event.institution}
                            </strong> • <em>${event.date}</em>
                          </p>
                          ${event.location && event.location !== 'Location TBD' ? `<p><strong>Location:</strong> ${event.location}</p>` : ''}
                          ${event.category && event.category.length > 0 ? `<p><strong>Categories:</strong> ${event.category.map(cat => `<span class="mobile-clickable-category" onclick="window.scrollToCategory('${escapeForJS(cat)}')" style="cursor: pointer; color: #f59e0b;">${cat}</span>`).join(', ')}</p>` : ''}
                        </div>
                      </div>
                      <button class="mobile-event-expand-btn" aria-label="Toggle description" onclick="event.stopPropagation(); window.toggleEventDescription('${eventId}');">
                        <span class="mobile-event-expand-icon">›</span>
                      </button>
                    </div>
                    <div class="mobile-event-description mobile-event-description-collapsed" id="${eventId}-description">
                      ${sanitizeHtml(event.description)}
                    </div>
                  </div>
                `;
                }).join('')}
              </div>
            </div>
          </div>
        </section>
      `;
    }).join('');
  };
}

