// API Configuration
const API_BASE_URL = 'https://nyc-academic-events-api.spergel-joshua.workers.dev';

// Debug logging
console.log('🚀 Frontend script loaded!');
console.log('🌐 API Base URL:', API_BASE_URL);

// Helper functions (defined early to avoid reference errors)
function applyFilters() {
    filterEvents();
}

function changePage(page) {
    goToPage(page);
}

function clearAllFilters() {
    clearFilters();
}

// Global state
let allEvents = [];
let filteredEvents = [];
let currentPage = 1;
let eventsPerPage = 12;
let currentView = 'grid';
let currentQuickFilter = 'all';
let currentSortBy = 'date'; // 'date', 'institution', 'name'
let currentSortOrder = 'asc'; // 'asc', 'desc'

// DOM Elements - will be populated after DOM loads
let elements = {};

// Function to initialize DOM elements
function initializeElements() {
    elements = {
        loading: document.getElementById('loading'),
        eventsContainer: document.getElementById('events-container'),
        eventsGrid: document.getElementById('events-grid'),
        noResults: document.getElementById('no-results'),
        pagination: document.getElementById('pagination'),
        eventsCount: document.getElementById('events-count'),
        totalEvents: document.getElementById('total-events'),
        totalInstitutions: document.getElementById('total-institutions'),
        lastUpdated: document.getElementById('last-updated'),
        institutionFilter: document.getElementById('institution-filter'),
        dateFrom: document.getElementById('date-from'),
        dateTo: document.getElementById('date-to'),
        searchInput: document.getElementById('search-input'),
        clearFilters: document.getElementById('clear-filters'),
        gridView: document.getElementById('grid-view'),
        listView: document.getElementById('list-view'),
        sortBy: document.getElementById('sort-by'),
        sortOrder: document.getElementById('sort-order'),
        prevPage: document.getElementById('prev-page'),
        nextPage: document.getElementById('next-page'),
        pageInfo: document.getElementById('page-info'),
        modal: document.getElementById('event-modal'),
        modalContent: document.getElementById('modal-content'),
        closeModal: document.querySelector('.close')
    };
    
    console.log('🔍 DOM elements initialized:', Object.keys(elements).length, 'elements found');
    
    // Check which elements are null
    Object.entries(elements).forEach(([key, element]) => {
        if (!element) {
            console.warn(`⚠️ ${key} is null`);
        }
    });
    
    // Check critical elements
    const criticalElements = ['eventsContainer', 'eventsGrid', 'noResults'];
    criticalElements.forEach(id => {
        if (!elements[id]) {
            console.error(`❌ CRITICAL: ${id} is missing!`);
        }
    });
}

// Initialize the application
async function init() {
    try {
        console.log('🚀 Initializing application...');
        
        // Initialize DOM elements first
        initializeElements();
        console.log('🔍 Checking DOM elements...');
        
        // Check if key elements exist
        const keyElements = ['loading', 'eventsContainer', 'eventsGrid', 'noResults'];
        keyElements.forEach(id => {
            const element = document.getElementById(id);
            console.log(`🔍 ${id}: ${element ? '✅ Found' : '❌ Missing'}`);
        });
        
        await loadStats();
        await loadEvents();
        setupEventListeners();
        populateInstitutionFilter();
        
        console.log('✅ Application initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize:', error);
        showError('Failed to load events. Please try again later.');
    }
}

// Load API statistics and update hero section
async function loadStats() {
    try {
        console.log('📊 Starting to load stats...');
        const statsUrl = `${API_BASE_URL}/api/stats`;
        console.log('📡 Calling stats API:', statsUrl);
        
        const response = await fetch(statsUrl);
        console.log('📥 Stats Response status:', response.status);
        
        const stats = await response.json();
        console.log('📊 Stats Response data:', stats);
        
        // Update hero stats
        const todayCount = getTodayEventsCount();
        const weekCount = getWeekEventsCount();
        
        console.log('📅 Today count:', todayCount);
        console.log('📅 Week count:', weekCount);
        console.log('🏛️ Total sources:', stats.data.sources);
        
        document.getElementById('today-events').textContent = todayCount;
        document.getElementById('week-events').textContent = weekCount;
        document.getElementById('total-institutions').textContent = stats.data.sources || '0';
        
        // Update hero title based on today's events
        const heroTitle = document.getElementById('hero-title');
        const heroSubtitle = document.getElementById('hero-subtitle');
        
        if (todayCount > 0) {
            heroTitle.textContent = `What's Happening Today?`;
            heroSubtitle.textContent = `Discover ${todayCount} academic events across NYC's top institutions`;
        } else {
            heroTitle.textContent = `Discover Academic Events`;
            heroSubtitle.textContent = `Explore upcoming lectures, seminars, and conferences across NYC's universities`;
        }
        
        console.log('✅ Stats loaded successfully');
    } catch (error) {
        console.error('❌ Failed to load stats:', error);
        console.error('❌ Error details:', error.message);
    }
}

// Helper functions for date filtering
function getTodayEventsCount() {
    const today = new Date().toISOString().split('T')[0];
    return allEvents.filter(event => {
        if (!event.start_date) return false;
        // Only count events with valid YYYY-MM-DD format
        if (!/^\d{4}-\d{2}-\d{2}$/.test(event.start_date)) return false;
        return event.start_date >= today;
    }).length;
}

function getWeekEventsCount() {
    const today = new Date();
    const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    const todayStr = today.toISOString().split('T')[0];
    const weekStr = weekFromNow.toISOString().split('T')[0];
    
    return allEvents.filter(event => {
        if (!event.start_date) return false;
        // Only count events with valid YYYY-MM-DD format
        if (!/^\d{4}-\d{2}-\d{2}$/.test(event.start_date)) return false;
        const eventDate = event.start_date;
        return eventDate >= todayStr && eventDate <= weekStr;
    }).length;
}

// Load all events from API
async function loadEvents() {
    try {
        console.log('🔍 Starting to load events...');
        elements.loading.style.display = 'block';
        elements.eventsContainer.style.display = 'none';
        elements.noResults.style.display = 'none';
        
        const apiUrl = `${API_BASE_URL}/api/events?limit=1000`;
        console.log('📡 Calling API:', apiUrl);
        
        // Load all events using the pagination API
        const response = await fetch(apiUrl);
        console.log('📥 API Response status:', response.status);
        console.log('📥 API Response headers:', response.headers);
        
        const data = await response.json();
        console.log('📊 API Response data:', data);
        
        allEvents = data.data.events || [];
        filteredEvents = [...allEvents];
        
        console.log(`✅ Loaded ${allEvents.length} events from API (Total: ${data.data.pagination.total})`);
        console.log('📋 First few events:', allEvents.slice(0, 3));
        
        elements.loading.style.display = 'none';
        renderEvents();
    } catch (error) {
        console.error('❌ Failed to load events:', error);
        console.error('❌ Error details:', error.message);
        elements.loading.style.display = 'none';
        showError('Failed to load events. Please try again later.');
    }
}

// Populate institution filter dropdown
function populateInstitutionFilter() {
    const institutions = [...new Set(allEvents.map(event => event.source_group).filter(Boolean))];
    institutions.sort();
    
    elements.institutionFilter.innerHTML = '<option value="">All Institutions</option>';
    institutions.forEach(institution => {
        const option = document.createElement('option');
        option.value = institution;
        option.textContent = institution.charAt(0).toUpperCase() + institution.slice(1);
        elements.institutionFilter.appendChild(option);
    });
}

// Filter events based on current filters
function filterEvents() {
    let filtered = [...allEvents];
    
    // Filter out past events (events that have already happened)
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    filtered = filtered.filter(event => {
        if (!event.start_date) return false; // Skip events without dates
        
        // Validate date format and filter out past events
        const eventDate = event.start_date;
        
        // Check if it's a valid YYYY-MM-DD format
        if (!/^\d{4}-\d{2}-\d{2}$/.test(eventDate)) {
            return false; // Skip events with invalid date format
        }
        
        // Check if the date is in the future or today
        return eventDate >= todayStr;
    });
    
    // Quick filter (Today, This Week, This Month)
    if (currentQuickFilter !== 'all') {
        switch (currentQuickFilter) {
            case 'today':
                filtered = filtered.filter(event => event.start_date === todayStr);
                break;
            case 'week':
                const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
                const weekStr = weekFromNow.toISOString().split('T')[0];
                filtered = filtered.filter(event => {
                    const eventDate = event.start_date;
                    return eventDate >= todayStr && eventDate <= weekStr;
                });
                break;
            case 'month':
                const monthFromNow = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate());
                const monthStr = monthFromNow.toISOString().split('T')[0];
                filtered = filtered.filter(event => {
                    const eventDate = event.start_date;
                    return eventDate >= todayStr && eventDate <= monthStr;
                });
                break;
        }
    }
    
    // Institution filter
    const institution = elements.institutionFilter.value;
    if (institution) {
        filtered = filtered.filter(event => 
            event.source_group === institution || 
            (event.source_group && event.source_group.toLowerCase().includes(institution.toLowerCase()))
        );
    }
    
    // Event type filter
    const eventType = document.getElementById('event-type-filter')?.value;
    if (eventType) {
        filtered = filtered.filter(event => {
            const eventText = event.name.toLowerCase() + ' ' + (event.description || '').toLowerCase();
            return eventText.includes(eventType.toLowerCase());
        });
    }
    
    // Date range filter
    const dateFrom = elements.dateFrom.value;
    const dateTo = elements.dateTo.value;
    
    if (dateFrom) {
        filtered = filtered.filter(event => event.start_date >= dateFrom);
    }
    if (dateTo) {
        filtered = filtered.filter(event => event.start_date <= dateTo);
    }
    
    // Search filter
    const searchTerm = elements.searchInput.value.toLowerCase();
    if (searchTerm) {
        filtered = filtered.filter(event => 
            event.name.toLowerCase().includes(searchTerm) ||
            (event.description && event.description.toLowerCase().includes(searchTerm)) ||
            (event.source_group && event.source_group.toLowerCase().includes(searchTerm))
        );
    }
    
    // Sort events based on current sort settings
    filtered.sort((a, b) => {
        let comparison = 0;
        
        switch (currentSortBy) {
            case 'date':
                if (!a.start_date || !b.start_date) return 0;
                comparison = a.start_date.localeCompare(b.start_date);
                break;
            case 'institution':
                const instA = (a.source_name || a.source || '').toLowerCase();
                const instB = (b.source_name || b.source || '').toLowerCase();
                comparison = instA.localeCompare(instB);
                break;
            case 'name':
                const nameA = (a.name || '').toLowerCase();
                const nameB = (b.name || '').toLowerCase();
                comparison = nameA.localeCompare(nameB);
                break;
            default:
                comparison = 0;
        }
        
        // Apply sort order
        return currentSortOrder === 'asc' ? comparison : -comparison;
    });
    
    filteredEvents = filtered;
    currentPage = 1;
    renderEvents();
}

// Render events with pagination
function renderEvents() {
    console.log('🎨 renderEvents called with', filteredEvents.length, 'events');
    
    // Safety check - make sure elements exist
    if (!elements.eventsContainer || !elements.eventsGrid || !elements.noResults) {
        console.error('❌ Required DOM elements not found in renderEvents');
        console.error('❌ elements.eventsContainer:', elements.eventsContainer);
        console.error('❌ elements.eventsGrid:', elements.eventsGrid);
        console.error('❌ elements.noResults:', elements.noResults);
        return;
    }
    
    try {
        const startIndex = (currentPage - 1) * eventsPerPage;
        const endIndex = startIndex + eventsPerPage;
        const pageEvents = filteredEvents.slice(startIndex, endIndex);
        
        if (filteredEvents.length === 0) {
            elements.eventsContainer.style.display = 'none';
            elements.noResults.style.display = 'block';
            if (elements.pagination) {
                elements.pagination.style.display = 'none';
            }
            return;
        }
        
        elements.eventsContainer.style.display = 'block';
        elements.noResults.style.display = 'none';
        
        // Update events count
        if (elements.eventsCount) {
            elements.eventsCount.textContent = `Events (${filteredEvents.length})`;
        }
        
        // Remove any existing info messages to prevent duplication
        const existingInfo = document.querySelector('.events-info');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        // Render event cards
        console.log('🎨 Rendering events:', pageEvents.length);
        console.log('🎨 Sample event:', pageEvents[0]);
        
        elements.eventsGrid.innerHTML = pageEvents.map(event => createEventCard(event)).join('');
        
        // Setup pagination
        if (elements.pagination) {
            setupPagination();
        }
        
        // Apply current view
        if (typeof applyViewMode === 'function') {
            applyViewMode();
        }
        
        console.log('✅ Events rendered successfully');
    } catch (error) {
        console.error('❌ Error in renderEvents:', error);
    }
}

// Create event card HTML
function createEventCard(event) {
    // Use same date formatting as modal for consistency
    const formatDate = (dateStr) => {
        if (!dateStr) return 'TBD';
        
        // Try to parse the date string - handle various formats
        let parsedDate;
        
        // First try: YYYY-MM-DD format
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
            const [year, month, day] = dateStr.split('-').map(Number);
            parsedDate = new Date(year, month - 1, day);
        } else {
            // Try to parse other date formats
            parsedDate = new Date(dateStr);
        }
        
        // Validate the parsed date
        if (isNaN(parsedDate.getTime()) || parsedDate.getFullYear() < 1900 || parsedDate.getFullYear() > 2100) {
            return 'TBD';
        }
        
        return parsedDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    };
    
    const date = formatDate(event.start_date);
            const institution = event.source_group || event.source || 'Unknown';
    
    return `
        <div class="event-card" onclick="openEventModal('${event.id}')">
            <div class="event-title">${escapeHtml(event.name)}</div>
            <div class="event-description">${renderSafeHtml(event.description || 'No description available')}</div>
            <div class="event-meta">
                <span class="event-date">
                    <i class="fas fa-calendar-day"></i>
                    ${date}
                </span>
                <span class="event-institution">${escapeHtml(institution)}</span>
            </div>
        </div>
    `;
}

// Setup pagination controls
function setupPagination() {
    const totalPages = Math.ceil(filteredEvents.length / eventsPerPage);
    
    if (totalPages <= 1) {
        elements.pagination.style.display = 'none';
        return;
    }
    
    elements.pagination.style.display = 'flex';
    elements.pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    
    elements.prevPage.disabled = currentPage === 1;
    elements.nextPage.disabled = currentPage === totalPages;
}

// Apply current view mode (grid/list)
function applyViewMode() {
    if (elements.eventsGrid) {
        elements.eventsGrid.classList.toggle('list-view', currentView === 'list');
    }
}

// Update sort order icon
function updateSortOrderIcon() {
    const icon = elements.sortOrder.querySelector('i');
    if (currentSortOrder === 'asc') {
        icon.className = 'fas fa-sort-amount-down';
        elements.sortOrder.title = 'Sort ascending (click to reverse)';
    } else {
        icon.className = 'fas fa-sort-amount-up';
        elements.sortOrder.title = 'Sort descending (click to reverse)';
    }
}

// Open event modal
function openEventModal(eventId) {
    try {
        // Find the event in our already loaded events
        const event = allEvents.find(e => e.id === eventId);
        
        if (event) {
            showEventModal(event);
        } else {
            console.error('Event not found in loaded events:', eventId);
            showError('Event not found');
        }
    } catch (error) {
        console.error('Failed to open event modal:', error);
        showError('Failed to open event modal');
    }
}

// Show event modal with details and calendar integration
function showEventModal(event) {
    // Fix date formatting to avoid timezone issues
    const formatDate = (dateStr) => {
        if (!dateStr) return 'TBD';
        
        // Try to parse the date string - handle various formats
        let parsedDate;
        
        // First try: YYYY-MM-DD format
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
            const [year, month, day] = dateStr.split('-').map(Number);
            parsedDate = new Date(year, month - 1, day);
        } else {
            // Try to parse other date formats
            parsedDate = new Date(dateStr);
        }
        
        // Validate the parsed date
        if (isNaN(parsedDate.getTime()) || parsedDate.getFullYear() < 1900 || parsedDate.getFullYear() > 2100) {
            return 'TBD';
        }
        
        return parsedDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    };
    
    const date = formatDate(event.start_date);
    const endDate = formatDate(event.end_date);
    
    // Clean up institution name
    const formatInstitution = (name) => {
        if (!name) return 'Unknown';
        // Capitalize first letter and clean up formatting
        return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
    };
    
    elements.modalContent.innerHTML = `
        <div class="modal-event-title">${escapeHtml(event.name)}</div>
        <div class="modal-event-description">${renderSafeHtml(event.description || 'No description available')}</div>
        <div class="modal-event-details">
            <div class="modal-detail">
                <div class="modal-detail-label">Date</div>
                <div class="modal-detail-value">${date}${endDate && endDate !== 'TBD' ? ` - ${endDate}` : ''}</div>
            </div>
            <div class="modal-detail">
                <div class="modal-detail-label">Institution</div>
                <div class="modal-detail-value">${escapeHtml(formatInstitution(event.source_group || event.source))}</div>
            </div>
            <div class="modal-detail">
                <div class="modal-detail-label">Venue</div>
                <div class="modal-detail-value">${escapeHtml(event.metadata?.venue?.name || 'TBD')}</div>
            </div>
            <div class="modal-detail">
                <div class="modal-detail-label">Type</div>
                <div class="modal-detail-value">${escapeHtml(event.metadata?.venue?.type || 'Not specified')}</div>
            </div>
        </div>
        ${event.source_url ? `<a href="${event.source_url}" target="_blank" class="modal-source-link">View Original Event</a>` : ''}
    `;
    
    // Store current event for calendar actions
    elements.modal.dataset.currentEvent = JSON.stringify(event);
    
    elements.modal.style.display = 'block';
    
    // Setup calendar action listeners
    setupCalendarActions(event);
}

// Calendar integration functions
function setupCalendarActions(event) {
    // Google Calendar
    document.getElementById('add-to-google').onclick = () => addToGoogleCalendar(event);
    
    // ICS Download
    document.getElementById('download-ics').onclick = () => downloadICSFile(event);
    
    // Outlook
    document.getElementById('add-to-outlook').onclick = () => addToOutlook(event);
    
    // Apple Calendar
    document.getElementById('add-to-apple').onclick = () => addToAppleCalendar(event);
    
    // Share
    document.getElementById('share-event').onclick = () => shareEvent(event);
}

function addToGoogleCalendar(event) {
    // Validate and parse dates
    let startDate, endDate;
    
    if (event.start_date && /^\d{4}-\d{2}-\d{2}$/.test(event.start_date)) {
        const [year, month, day] = event.start_date.split('-').map(Number);
        startDate = new Date(year, month - 1, day);
    } else {
        startDate = new Date();
    }
    
    if (event.end_date && /^\d{4}-\d{2}-\d{2}$/.test(event.end_date)) {
        const [year, month, day] = event.end_date.split('-').map(Number);
        endDate = new Date(year, month - 1, day);
    } else {
        endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000);
    }
    
    // Validate parsed dates
    if (isNaN(startDate.getTime()) || startDate.getFullYear() < 1900 || startDate.getFullYear() > 2100) {
        startDate = new Date();
        endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000);
    }
    
    const googleUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.name)}&dates=${startDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z/${endDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z&details=${encodeURIComponent(event.description || '')}&location=${encodeURIComponent(event.venue_name || '')}`;
    
    window.open(googleUrl, '_blank');
}

function downloadICSFile(event) {
    // Validate and parse dates
    let startDate, endDate;
    
    if (event.start_date && /^\d{4}-\d{2}-\d{2}$/.test(event.start_date)) {
        const [year, month, day] = event.start_date.split('-').map(Number);
        startDate = new Date(year, month - 1, day);
    } else {
        startDate = new Date();
    }
    
    if (event.end_date && /^\d{4}-\d{2}-\d{2}$/.test(event.end_date)) {
        const [year, month, day] = event.end_date.split('-').map(Number);
        endDate = new Date(year, month - 1, day);
    } else {
        endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000);
    }
    
    // Validate parsed dates
    if (isNaN(startDate.getTime()) || startDate.getFullYear() < 1900 || startDate.getFullYear() > 2100) {
        startDate = new Date();
        endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000);
    }
    
    const icsContent = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//NYC Academic Events//Calendar Event//EN',
        'BEGIN:VEVENT',
        `UID:${event.event_id}@academics.somethingtodo.nyc`,
        `DTSTART:${startDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z`,
        `DTEND:${endDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z`,
        `SUMMARY:${event.name}`,
        `DESCRIPTION:${event.description || ''}`,
        `LOCATION:${event.venue_name || ''}`,
        `URL:${event.source_url || ''}`,
        'END:VEVENT',
        'END:VCALENDAR'
    ].join('\r\n');
    
    const blob = new Blob([icsContent], { type: 'text/calendar' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${event.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.ics`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function addToOutlook(event) {
    // Validate and parse dates
    let startDate, endDate;
    
    if (event.start_date && /^\d{4}-\d{2}-\d{2}$/.test(event.start_date)) {
        const [year, month, day] = event.start_date.split('-').map(Number);
        startDate = new Date(year, month - 1, day);
    } else {
        startDate = new Date();
    }
    
    if (event.end_date && /^\d{4}-\d{2}-\d{2}$/.test(event.end_date)) {
        const [year, month, day] = event.end_date.split('-').map(Number);
        endDate = new Date(year, month - 1, day);
    } else {
        endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000);
    }
    
    // Validate parsed dates
    if (isNaN(startDate.getTime()) || startDate.getFullYear() < 1900 || startDate.getFullYear() > 2100) {
        startDate = new Date();
        endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000);
    }
    
    const outlookUrl = `https://outlook.live.com/calendar/0/deeplink/compose?subject=${encodeURIComponent(event.name)}&startdt=${startDate.toISOString()}&enddt=${endDate.toISOString()}&body=${encodeURIComponent(event.description || '')}&location=${encodeURIComponent(event.venue_name || '')}`;
    
    window.open(outlookUrl, '_blank');
}

function addToAppleCalendar(event) {
    // Apple Calendar uses ICS files, so we'll download the ICS file
    downloadICSFile(event);
}

function shareEvent(event) {
    const shareData = {
        title: event.name,
        text: event.description || '',
        url: window.location.href
    };
    
    if (navigator.share) {
        navigator.share(shareData);
    } else {
        // Fallback: copy to clipboard
        const shareText = `${event.name}\n\n${event.description || ''}\n\nView more events: ${window.location.href}`;
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Event details copied to clipboard!');
        });
    }
}

// Close event modal
function closeEventModal() {
    elements.modal.style.display = 'none';
}

// Show error message
function showError(message) {
    elements.loading.innerHTML = `
        <div style="color: #ff4757; font-size: 1.2rem; margin-bottom: 10px;">
            <i class="fas fa-exclamation-triangle"></i>
        </div>
        <p>${message}</p>
    `;
    elements.loading.style.display = 'block';
}

// Clear all filters
function clearFilters() {
    // Reset quick filters
    currentQuickFilter = 'all';
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('.filter-tab[data-filter="all"]').classList.add('active');
    
    // Reset advanced filters
    elements.institutionFilter.value = '';
    document.getElementById('event-type-filter').value = '';
    elements.dateFrom.value = '';
    elements.dateTo.value = '';
    elements.searchInput.value = '';
    filterEvents();
}

// Change view mode
function changeView(mode) {
    currentView = mode;
    elements.gridView.classList.toggle('active', mode === 'grid');
    elements.listView.classList.toggle('active', mode === 'list');
    applyViewMode();
}

// Navigate to page
function goToPage(page) {
    currentPage = page;
    renderEvents();
    window.scrollTo({ top: elements.eventsContainer.offsetTop - 100, behavior: 'smooth' });
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Utility function to render safe HTML (allows basic formatting)
function renderSafeHtml(text) {
    if (!text) return '';
    
    // Clean up common unwanted text patterns first
    let cleanedText = text
        .replace(/Google Calendar ICS View Event →/gi, '')
        .replace(/Add to Google Calendar/gi, '')
        .replace(/Download ICS/gi, '')
        .replace(/View Event/gi, '')
        .replace(/→/g, '')
        .replace(/\s+/g, ' ') // Replace multiple spaces with single space
        .trim();
    
    // Only allow safe HTML tags
    const allowedTags = ['b', 'strong', 'i', 'em', 'u', 'br', 'p', 'div', 'span', 'ul', 'ol', 'li'];
    const allowedAttributes = ['class', 'style'];
    
    // Create a temporary div to parse the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = cleanedText;
    
    // Recursively clean the HTML
    function cleanNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            return node.textContent;
        }
        
        if (node.nodeType === Node.ELEMENT_NODE) {
            const tagName = node.tagName.toLowerCase();
            
            // If tag is not allowed, just return the text content
            if (!allowedTags.includes(tagName)) {
                return node.textContent;
            }
            
            // Clean attributes
            const cleanAttrs = {};
            for (let attr of node.attributes) {
                if (allowedAttributes.includes(attr.name)) {
                    cleanAttrs[attr.name] = attr.value;
                }
            }
            
            // Build clean HTML
            let cleanHtml = `<${tagName}`;
            for (let [name, value] of Object.entries(cleanAttrs)) {
                cleanHtml += ` ${name}="${escapeHtml(value)}"`;
            }
            cleanHtml += '>';
            
            // Process child nodes
            for (let child of node.childNodes) {
                cleanHtml += cleanNode(child);
            }
            
            cleanHtml += `</${tagName}>`;
            return cleanHtml;
        }
        
        return '';
    }
    
    // Clean the HTML and return
    return cleanNode(tempDiv);
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply quick filter (Today, This Week, This Month)
function applyQuickFilter(filter) {
    currentQuickFilter = filter;
    filterEvents();
}

// Setup event listeners for filters and pagination
function setupEventListeners() {
    // Quick filter tabs
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const filter = tab.getAttribute('data-filter');
            applyQuickFilter(filter);
        });
    });
    
    // Advanced filters
    if (elements.institutionFilter) {
        elements.institutionFilter.addEventListener('change', applyFilters);
    }
    if (elements.dateFrom) {
        elements.dateFrom.addEventListener('change', applyFilters);
    }
    if (elements.dateTo) {
        elements.dateTo.addEventListener('change', applyFilters);
    }
    if (elements.searchInput) {
        elements.searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
    if (elements.clearFilters) {
        elements.clearFilters.addEventListener('click', clearAllFilters);
    }
    
    // Pagination
    if (elements.prevPage) {
        elements.prevPage.addEventListener('click', () => goToPage(currentPage - 1));
    }
    if (elements.nextPage) {
        elements.nextPage.addEventListener('click', () => goToPage(currentPage + 1));
    }
    
    // Modal close button
    if (elements.closeModal) {
        elements.closeModal.addEventListener('click', closeEventModal);
    }
    
    // Close modal when clicking outside
    if (elements.modal) {
        elements.modal.addEventListener('click', (e) => {
            if (e.target === elements.modal) {
                closeEventModal();
            }
        });
    }
}

// Populate institution filter dropdown
function populateInstitutionFilter() {
    if (!elements.institutionFilter) return;
    
    // You could fetch this from the API or use a predefined list
    const institutions = [
        'columbia',
        'nyu',
        'cuny',
        'gallatin',
        'isaw',
        'jtsa',
        'cims',
        'cornell_tech',
        'simons_foundation'
    ];
    
    institutions.forEach(inst => {
        const option = document.createElement('option');
        option.value = inst;
        option.textContent = inst.charAt(0).toUpperCase() + inst.slice(1).replace('_', ' ');
        elements.institutionFilter.appendChild(option);
    });
}

// These functions are now defined at the top of the file

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM Content Loaded event fired');
    // Add a small delay to ensure all elements are available
    setTimeout(() => {
        console.log('⏰ Starting initialization after delay...');
        init();
    }, 100);
});
