// NYC Academic Events Website JavaScript
class AcademicEventsApp {
    constructor() {
        this.allEvents = [];
        this.filteredEvents = [];
        this.sources = new Set();
        this.categories = new Set();
        this.sortColumn = 'date'; // Default sort by date
        this.sortDirection = 'asc'; // Default ascending

        this.init();
    }

    async init() {
        try {
            await this.loadEvents();
            this.setupEventListeners();
            this.updateStats();
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showError('Failed to load events data');
        }
    }

    async loadEvents() {
        const response = await fetch('https://nyc-academic-events-api.spergel-joshua.workers.dev/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.allEvents = data || [];

        // Extract unique sources and categories
        this.allEvents.forEach(event => {
            if (event.source && event.source !== 'unknown') {
                this.sources.add(this.formatSourceName(event.source));
            } else {
                // Try to infer source for display
                const name = (event.name || event.title || '').toLowerCase();
                const url = event.metadata?.source_url || event.url || '';

                if (name.includes('new school') || name.includes('parsons') || name.includes('eugene lang') || url.includes('newschool.edu')) {
                    this.sources.add('The New School');
                } else if (name.includes('engineering') && (name.includes('nyu') || url.includes('nyu.edu'))) {
                    this.sources.add('NYU Engineering');
                }
            }

            // Handle both string and array categories
            if (event.category) {
                if (Array.isArray(event.category)) {
                    event.category.forEach(cat => this.categories.add(cat));
                } else if (typeof event.category === 'string') {
                    this.categories.add(event.category);
                }
            }
        });

        this.populateFilters();
        this.filterEvents();
        this.displayEvents();
        this.updateSortIndicators(); // Show initial sort indicator
        this.updateLastUpdated(data.scraped_at);
    }

    populateFilters() {
        const sourceFilter = document.getElementById('source-filter');
        const categoryFilter = document.getElementById('category-filter');

        // Populate source filter
        Array.from(this.sources).sort().forEach(source => {
            const option = document.createElement('option');
            option.value = source;
            option.textContent = this.formatSourceName(source);
            sourceFilter.appendChild(option);
        });

        // Populate category filter
        Array.from(this.categories).sort().forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category.charAt(0) + category.slice(1).toLowerCase();
            categoryFilter.appendChild(option);
        });
    }

    setupEventListeners() {
        document.getElementById('source-filter').addEventListener('change', () => this.filterEvents());
        document.getElementById('category-filter').addEventListener('change', () => this.filterEvents());
        document.getElementById('date-filter').addEventListener('change', () => this.filterEvents());
        document.getElementById('reset-filters').addEventListener('click', () => this.resetFilters());
    }

    filterEvents() {
        const sourceFilter = document.getElementById('source-filter').value;
        const categoryFilter = document.getElementById('category-filter').value;
        const dateFilter = document.getElementById('date-filter').value;

        this.filteredEvents = this.allEvents.filter(event => {
            // TEMPORARILY show events with unknown/missing data so we can see what's missing
            // TODO: Re-enable this filtering after fixing Columbia scrapers

            // Try to parse the date - if it fails, hide the event
            try {
                const eventDate = new Date(event.start_date);
                const now = new Date();

                // Hide events that have already happened (past events)
                // Keep today's events and future events
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                if (eventDate < today) {
                    return false;
                }
            } catch (e) {
                return false;
            }

            // For filtering, we need to use the display name, not the source field
            // Get the display name for this event
            let displaySource;
            if (event.source && event.source !== 'unknown') {
                displaySource = this.formatSourceName(event.source);
            } else {
                // Try to infer source from name or URL
                const name = (event.name || event.title || '').toLowerCase();
                const url = event.metadata?.source_url || event.url || '';

                if (name.includes('new school') || name.includes('parsons') || name.includes('eugene lang') || url.includes('newschool.edu')) {
                    displaySource = 'The New School';
                } else if (name.includes('engineering') && (name.includes('nyu') || url.includes('nyu.edu'))) {
                    displaySource = 'NYU Engineering';
                }
            }

            // Source filter - use display name for filtering
            if (sourceFilter && displaySource !== sourceFilter) {
                return false;
            }

            // Category filter - handle both string and array categories
            if (categoryFilter) {
                let eventCategories = [];
                if (Array.isArray(event.category)) {
                    eventCategories = event.category;
                } else if (typeof event.category === 'string') {
                    eventCategories = [event.category];
                }

                if (!eventCategories.includes(categoryFilter)) {
                    return false;
                }
            }

            // Date filter (applied after hiding past events)
            if (dateFilter !== 'all') {
                const eventDate = new Date(event.start_date);
                const now = new Date();
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                const eventDay = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());

                switch (dateFilter) {
                    case 'today':
                        if (eventDay.getTime() !== today.getTime()) return false;
                        break;
                    case 'week':
                        const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
                        if (eventDay < today || eventDay > weekFromNow) return false;
                        break;
                    case 'month':
                        const monthFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
                        if (eventDay < today || eventDay > monthFromNow) return false;
                        break;
                }
            }

            return true;
        });

        this.displayEvents();
        this.updateStats();
    }

    displayEvents() {
        const tbody = document.getElementById('events-body');

        if (this.filteredEvents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No events match the current filters.</td></tr>';
            return;
        }

        // Sort events
        const sortedEvents = this.sortEvents(this.filteredEvents);

        tbody.innerHTML = sortedEvents.map(event => this.createEventRow(event)).join('');

        // Update sort indicators in headers
        this.updateSortIndicators();
    }

    sortEvents(events) {
        return events.sort((a, b) => {
            let aVal, bVal;

            switch (this.sortColumn) {
                case 'date':
                    aVal = new Date(a.start_date);
                    bVal = new Date(b.start_date);
                    break;
                case 'event':
                    aVal = (a.name || a.title || '').toLowerCase();
                    bVal = (b.name || b.title || '').toLowerCase();
                    break;
                case 'institution':
                    aVal = this.formatSourceName(a.source).toLowerCase();
                    bVal = this.formatSourceName(b.source).toLowerCase();
                    break;
                case 'location':
                    const aLoc = a.metadata?.venue?.name || a.venue?.name || '';
                    const bLoc = b.metadata?.venue?.name || b.venue?.name || '';
                    aVal = aLoc.toLowerCase();
                    bVal = bLoc.toLowerCase();
                    break;
                default:
                    return 0;
            }

            if (this.sortDirection === 'asc') {
                return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            } else {
                return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
            }
        });
    }

    sortBy(column) {
        if (this.sortColumn === column) {
            // Toggle direction if same column
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            // New column, default to ascending
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }

        this.displayEvents();
    }

    updateSortIndicators() {
        // Remove all sort indicators
        document.querySelectorAll('.sort-indicator').forEach(indicator => {
            indicator.remove();
        });

        // Add sort indicator to current sort column
        const headers = document.querySelectorAll('th');
        headers.forEach((header, index) => {
            const column = ['date', 'event', 'institution', 'location'][index];
            if (column === this.sortColumn) {
                const indicator = document.createElement('span');
                indicator.className = 'sort-indicator';
                indicator.textContent = this.sortDirection === 'asc' ? ' ▲' : ' ▼';
                header.appendChild(indicator);
            }
        });
    }

    createEventRow(event) {
        const startDate = new Date(event.start_date);

        const formatDate = (date) => {
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
        };

        const formatTime = (date) => {
            return date.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        };

        const dateStr = formatDate(startDate);
        const timeStr = formatTime(startDate);

        const location = event.metadata?.venue?.name || event.venue?.name || (event.location || 'Location TBD');
        const eventUrl = event.metadata?.source_url || event.url;

        // Handle category - it can be a string, array, or missing
        let categories = [];
        if (event.category) {
            if (Array.isArray(event.category)) {
                categories = event.category;
            } else if (typeof event.category === 'string') {
                categories = [event.category];
            }
        }

        // Show missing data indicators and try to infer source from other fields
        let sourceDisplay;
        if (event.source && event.source !== 'unknown') {
            sourceDisplay = this.formatSourceName(event.source);
        } else {
            // Try to infer source from name or URL
            const name = (event.name || event.title || '').toLowerCase();
            const url = event.metadata?.source_url || event.url || '';

            if (name.includes('new school') || name.includes('parsons') || name.includes('eugene lang') || url.includes('newschool.edu')) {
                sourceDisplay = '<span class="inferred-source">The New School</span>';
            } else if (name.includes('engineering') && (name.includes('nyu') || url.includes('nyu.edu'))) {
                sourceDisplay = '<span class="inferred-source">NYU Engineering</span>';
            } else {
                sourceDisplay = `<span style="color: #e74c3c; font-weight: bold;">UNKNOWN INSTITUTION</span>`;
            }
        }

        const locationDisplay = location && location !== 'Location TBD' ?
            this.escapeHtml(location) :
            `<span style="color: #e74c3c;">No location</span>`;

        const titleHtml = eventUrl ?
            `<a href="${this.escapeHtml(eventUrl)}" target="_blank" rel="noopener noreferrer">${this.escapeHtml(event.name || event.title || 'Untitled Event')}</a>` :
            this.escapeHtml(event.name || event.title || 'Untitled Event');

        return `
            <tr>
                <td>${dateStr}<br><small>${timeStr}</small></td>
                <td>${titleHtml}</td>
                <td>${sourceDisplay}</td>
                <td>${locationDisplay}</td>
                <td>${categories.length > 0 ? categories.map(cat => `<span class="event-category">${this.escapeHtml(cat)}</span>`).join(' ') : '<span style="color: #999;">No category</span>'}</td>
            </tr>
        `;
    }

    updateStats() {
        document.getElementById('total-events').textContent = this.allEvents.length;
        document.getElementById('filtered-events').textContent = this.filteredEvents.length;
        document.getElementById('unique-sources').textContent = this.sources.size;
    }

    updateLastUpdated(scrapedAt) {
        if (scrapedAt) {
            const date = new Date(scrapedAt);
            document.getElementById('last-updated').textContent = date.toLocaleString();
        }
    }

    resetFilters() {
        document.getElementById('source-filter').value = '';
        document.getElementById('category-filter').value = '';
        document.getElementById('date-filter').value = 'all';
        this.filterEvents();
    }

    formatSourceName(source) {
        if (!source || source === 'unknown') return 'Unknown';

        // Format source names for display
        const formatted = source.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        // Special formatting for known institutions
        const specialCases = {
            'nyu_cims': 'NYU Courant',
            'columbia': 'Columbia University',
            'nyu_api': 'NYU',
            'new_school': 'The New School',
            'nyu_engineering': 'NYU Engineering',
            'cornell_tech': 'Cornell Tech',
            'cooper_union': 'Cooper Union',
            'fordham': 'Fordham University',
            'gallatin': 'NYU Gallatin',
            'isaw': 'ISAW NYU',
            'jtsa': 'Jewish Theological Seminary',
            'juilliard': 'The Juilliard School',
            'pratt': 'Pratt Institute',
            'simons_foundation': 'Simons Foundation'
        };

        return specialCases[source] || formatted;
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    decodeHtml(html) {
        if (!html) return '';
        const txt = document.createElement('textarea');
        txt.innerHTML = html;
        return txt.value;
    }

    showError(message) {
        const tbody = document.getElementById('events-body');
        tbody.innerHTML = `<tr><td colspan="5" style="color: #e74c3c;">Error: ${message}</td></tr>`;
    }

}

// Global reference for onclick handlers
let app;

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app = new AcademicEventsApp();
});
