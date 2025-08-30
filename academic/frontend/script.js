// API Configuration
const API_BASE_URL = 'https://nyc-academic-events-api.spergel-joshua.workers.dev';

// Global state
let allEvents = [];
let filteredEvents = [];
let currentPage = 1;
let eventsPerPage = 12;
let currentView = 'grid';

// DOM Elements
const elements = {
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
    prevPage: document.getElementById('prev-page'),
    nextPage: document.getElementById('next-page'),
    pageInfo: document.getElementById('page-info'),
    modal: document.getElementById('event-modal'),
    modalContent: document.getElementById('modal-content'),
    closeModal: document.querySelector('.close')
};

// Initialize the application
async function init() {
    try {
        await loadStats();
        await loadEvents();
        setupEventListeners();
        populateInstitutionFilter();
    } catch (error) {
        console.error('Failed to initialize:', error);
        showError('Failed to load events. Please try again later.');
    }
}

// Load API statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const stats = await response.json();
        
        elements.totalEvents.textContent = stats.total_academic_events || 0;
        elements.totalInstitutions.textContent = stats.total_institutions || 0;
        
        if (stats.last_updated) {
            const date = new Date(stats.last_updated);
            elements.lastUpdated.textContent = date.toLocaleDateString();
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Load all events from API
async function loadEvents() {
    try {
        elements.loading.style.display = 'block';
        elements.eventsContainer.style.display = 'none';
        elements.noResults.style.display = 'none';
        
        const response = await fetch(`${API_BASE_URL}/api/events?limit=100`);
        const data = await response.json();
        
        allEvents = data.events || [];
        filteredEvents = [...allEvents];
        
        elements.loading.style.display = 'none';
        renderEvents();
    } catch (error) {
        console.error('Failed to load events:', error);
        elements.loading.style.display = 'none';
        showError('Failed to load events. Please try again later.');
    }
}

// Populate institution filter dropdown
function populateInstitutionFilter() {
    const institutions = [...new Set(allEvents.map(event => event.source).filter(Boolean))];
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
    
    // Institution filter
    const institution = elements.institutionFilter.value;
    if (institution) {
        filtered = filtered.filter(event => event.source === institution);
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
            event.description.toLowerCase().includes(searchTerm) ||
            (event.source_name && event.source_name.toLowerCase().includes(searchTerm))
        );
    }
    
    filteredEvents = filtered;
    currentPage = 1;
    renderEvents();
}

// Render events with pagination
function renderEvents() {
    const startIndex = (currentPage - 1) * eventsPerPage;
    const endIndex = startIndex + eventsPerPage;
    const pageEvents = filteredEvents.slice(startIndex, endIndex);
    
    if (filteredEvents.length === 0) {
        elements.eventsContainer.style.display = 'none';
        elements.noResults.style.display = 'block';
        elements.pagination.style.display = 'none';
        return;
    }
    
    elements.eventsContainer.style.display = 'block';
    elements.noResults.style.display = 'none';
    
    // Update events count
    elements.eventsCount.textContent = `Events (${filteredEvents.length})`;
    
    // Render event cards
    elements.eventsGrid.innerHTML = pageEvents.map(event => createEventCard(event)).join('');
    
    // Setup pagination
    setupPagination();
    
    // Apply current view
    applyViewMode();
}

// Create event card HTML
function createEventCard(event) {
    const date = event.start_date ? new Date(event.start_date).toLocaleDateString() : 'TBD';
    const institution = event.source_name || event.source || 'Unknown';
    
    return `
        <div class="event-card" onclick="openEventModal('${event.event_id}')">
            <div class="event-title">${escapeHtml(event.name)}</div>
            <div class="event-description">${escapeHtml(event.description || 'No description available')}</div>
            <div class="event-meta">
                <span class="event-date">${date}</span>
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
    elements.eventsGrid.classList.toggle('list-view', currentView === 'list');
}

// Open event modal
async function openEventModal(eventId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/events/${eventId}`);
        const event = await response.json();
        
        if (response.ok) {
            showEventModal(event);
        } else {
            showError('Event not found');
        }
    } catch (error) {
        console.error('Failed to load event details:', error);
        showError('Failed to load event details');
    }
}

// Show event modal with details
function showEventModal(event) {
    const date = event.start_date ? new Date(event.start_date).toLocaleDateString() : 'TBD';
    const endDate = event.end_date ? new Date(event.end_date).toLocaleDateString() : '';
    
    elements.modalContent.innerHTML = `
        <div class="modal-event-title">${escapeHtml(event.name)}</div>
        <div class="modal-event-description">${escapeHtml(event.description || 'No description available')}</div>
        <div class="modal-event-details">
            <div class="modal-detail">
                <div class="modal-detail-label">Date</div>
                <div class="modal-detail-value">${date}${endDate ? ` - ${endDate}` : ''}</div>
            </div>
            <div class="modal-detail">
                <div class="modal-detail-label">Institution</div>
                <div class="modal-detail-value">${escapeHtml(event.source_name || event.source || 'Unknown')}</div>
            </div>
            <div class="modal-detail">
                <div class="modal-detail-label">Venue</div>
                <div class="modal-detail-value">${escapeHtml(event.venue_name || 'TBD')}</div>
            </div>
            <div class="modal-detail">
                <div class="modal-detail-label">Type</div>
                <div class="modal-detail-value">${escapeHtml(event.venue_type || 'Not specified')}</div>
            </div>
        </div>
        ${event.source_url ? `<a href="${event.source_url}" target="_blank" class="modal-source-link">View Original Event</a>` : ''}
    `;
    
    elements.modal.style.display = 'block';
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
    elements.institutionFilter.value = '';
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

// Setup event listeners
function setupEventListeners() {
    // Filter event listeners
    elements.institutionFilter.addEventListener('change', filterEvents);
    elements.dateFrom.addEventListener('change', filterEvents);
    elements.dateTo.addEventListener('change', filterEvents);
    elements.searchInput.addEventListener('input', debounce(filterEvents, 300));
    elements.clearFilters.addEventListener('click', clearFilters);
    
    // View mode listeners
    elements.gridView.addEventListener('click', () => changeView('grid'));
    elements.listView.addEventListener('click', () => changeView('list'));
    
    // Pagination listeners
    elements.prevPage.addEventListener('click', () => goToPage(currentPage - 1));
    elements.nextPage.addEventListener('click', () => goToPage(currentPage + 1));
    
    // Modal listeners
    elements.closeModal.addEventListener('click', closeEventModal);
    elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) {
            closeEventModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.modal.style.display === 'block') {
            closeEventModal();
        }
    });
}

// Debounce function for search input
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
