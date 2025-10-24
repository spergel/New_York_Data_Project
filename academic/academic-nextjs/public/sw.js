// Service Worker for caching API responses
const CACHE_NAME = 'academic-events-v1';
const API_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Only cache API requests
  if (event.request.url.includes('/api/events')) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response) {
            // Check if cache is still valid
            const cacheTime = response.headers.get('sw-cache-time');
            if (cacheTime && (Date.now() - parseInt(cacheTime)) < API_CACHE_DURATION) {
              console.log('Serving from cache:', event.request.url);
              return response;
            }
          }
          
          // Fetch from network
          return fetch(event.request).then((networkResponse) => {
            // Clone the response to cache it
            const responseToCache = networkResponse.clone();
            const headers = new Headers(responseToCache.headers);
            headers.set('sw-cache-time', Date.now().toString());
            
            const modifiedResponse = new Response(responseToCache.body, {
              status: responseToCache.status,
              statusText: responseToCache.statusText,
              headers: headers
            });
            
            cache.put(event.request, modifiedResponse);
            return networkResponse;
          });
        });
      })
    );
  }
});
