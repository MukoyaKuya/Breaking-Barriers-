// Breaking Barriers International - Service Worker
// Provides offline functionality and caching for PWA

const CACHE_NAME = 'bbi-cache-v1';
const OFFLINE_URL = '/offline/';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
    '/',
    '/offline/',
    '/static/images/logo.png',
];

// Install event - cache essential assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('BBI SW: Caching essential assets');
                return cache.addAll(PRECACHE_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('BBI SW: Removing old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - network-first strategy with offline fallback
self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    // Skip admin and API requests
    if (event.request.url.includes('/admin/') || event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Clone the response before caching
                const responseClone = response.clone();

                // Cache successful responses for static assets
                if (response.status === 200 && event.request.url.includes('/static/')) {
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }

                return response;
            })
            .catch(() => {
                // Network failed - try cache first
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }

                        // If it's a navigation request, show offline page
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }

                        // Return a simple offline response for other requests
                        return new Response('Offline', {
                            status: 503,
                            statusText: 'Service Unavailable',
                            headers: new Headers({ 'Content-Type': 'text/plain' }),
                        });
                    });
            })
    );
});
