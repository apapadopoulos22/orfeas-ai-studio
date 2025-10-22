// ============================================================================
// ðŸ”¥ ORFEAS OPTIMIZATION 22: Advanced Service Worker
// PWA Offline Support with Intelligent Caching Strategies
// ============================================================================

const CACHE_VERSION = 'orfeas-v1.0.0';
const CACHE_NAME = `${CACHE_VERSION}-static`;
const RUNTIME_CACHE = `${CACHE_VERSION}-runtime`;
const API_CACHE = `${CACHE_VERSION}-api`;
const IMAGE_CACHE = `${CACHE_VERSION}-images`;

// Cache duration (in seconds)
const CACHE_DURATION = {
    static: 30 * 24 * 60 * 60,      // 30 days
    runtime: 7 * 24 * 60 * 60,       // 7 days
    api: 5 * 60,                      // 5 minutes
    images: 24 * 60 * 60              // 24 hours
};

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/orfeas-studio.html',
    '/manifest.json',
    // Add other critical static assets
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/health',
    '/api/models',
    '/api/templates'
];

// ============================================================================
// SERVICE WORKER LIFECYCLE EVENTS
// ============================================================================

/**
 * Install Event - Cache static assets
 */
self.addEventListener('install', (event) => {
    console.log('ðŸ”§ [Service Worker] Installing...');

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('ðŸ“¦ [Service Worker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('âœ… [Service Worker] Installation complete');
                return self.skipWaiting(); // Activate immediately
            })
            .catch((error) => {
                console.error('âŒ [Service Worker] Installation failed:', error);
            })
    );
});

/**
 * Activate Event - Clean up old caches
 */
self.addEventListener('activate', (event) => {
    console.log('âš¡ [Service Worker] Activating...');

    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        // Delete old caches
                        if (!cacheName.startsWith(CACHE_VERSION)) {
                            console.log(`ðŸ—‘ï¸ [Service Worker] Deleting old cache: ${cacheName}`);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('âœ… [Service Worker] Activation complete');
                return self.clients.claim(); // Take control immediately
            })
    );
});

/**
 * Fetch Event - Intelligent caching strategies
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Ignore non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Ignore chrome-extension and other non-http(s) requests
    if (!url.protocol.startsWith('http')) {
        return;
    }

    // Apply different strategies based on request type
    if (isStaticAsset(url)) {
        event.respondWith(cacheFirst(request, CACHE_NAME));
    } else if (isAPIRequest(url)) {
        event.respondWith(networkFirst(request, API_CACHE));
    } else if (isImageRequest(url)) {
        event.respondWith(cacheFirst(request, IMAGE_CACHE));
    } else {
        event.respondWith(staleWhileRevalidate(request, RUNTIME_CACHE));
    }
});

/**
 * Message Event - Handle commands from main thread
 */
self.addEventListener('message', (event) => {
    console.log('ðŸ“¨ [Service Worker] Message received:', event.data);

    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data.type === 'CLEAR_CACHE') {
        clearAllCaches().then(() => {
            event.ports[0].postMessage({ success: true });
        });
    }

    if (event.data.type === 'GET_CACHE_SIZE') {
        getCacheSize().then((size) => {
            event.ports[0].postMessage({ size });
        });
    }
});

/**
 * Background Sync Event - Retry failed requests
 */
self.addEventListener('sync', (event) => {
    console.log('ðŸ”„ [Service Worker] Background sync:', event.tag);

    if (event.tag === 'sync-failed-requests') {
        event.waitUntil(syncFailedRequests());
    }
});

// ============================================================================
// CACHING STRATEGIES
// ============================================================================

/**
 * Cache First Strategy - Check cache before network
 * Best for: Static assets that don't change often
 */
async function cacheFirst(request, cacheName) {
    try {
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            console.log('âœ… [Cache First] Served from cache:', request.url);
            return cachedResponse;
        }

        console.log('ðŸŒ [Cache First] Fetching from network:', request.url);
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.error('âŒ [Cache First] Failed:', error);
        return new Response('Offline - Content not available', { status: 503 });
    }
}

/**
 * Network First Strategy - Try network before cache
 * Best for: API requests that need fresh data
 */
async function networkFirst(request, cacheName) {
    try {
        console.log('ðŸŒ [Network First] Fetching from network:', request.url);
        const networkResponse = await fetch(request, { timeout: 3000 });

        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('âš ï¸ [Network First] Network failed, trying cache:', error.message);
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            console.log('âœ… [Network First] Served from cache:', request.url);
            return cachedResponse;
        }

        console.error('âŒ [Network First] Both network and cache failed');
        return new Response(JSON.stringify({ error: 'Offline and no cached data' }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Stale While Revalidate - Serve cache immediately, update in background
 * Best for: Content that can be slightly stale
 */
async function staleWhileRevalidate(request, cacheName) {
    const cachedResponse = await caches.match(request);

    const fetchPromise = fetch(request)
        .then((networkResponse) => {
            if (networkResponse.ok) {
                const cache = caches.open(cacheName);
                cache.then(c => c.put(request, networkResponse.clone()));
            }
            return networkResponse;
        })
        .catch((error) => {
            console.log('âš ï¸ [Stale While Revalidate] Network update failed:', error.message);
            return cachedResponse;
        });

    if (cachedResponse) {
        console.log('âœ… [Stale While Revalidate] Served from cache, updating in background');
        return cachedResponse;
    }

    console.log('ðŸŒ [Stale While Revalidate] No cache, waiting for network');
    return fetchPromise;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Check if request is for static asset
 */
function isStaticAsset(url) {
    const staticExtensions = ['.html', '.css', '.js', '.woff', '.woff2', '.ttf'];
    return staticExtensions.some(ext => url.pathname.endsWith(ext));
}

/**
 * Check if request is API call
 */
function isAPIRequest(url) {
    return url.pathname.startsWith('/api/') || url.port === '5000';
}

/**
 * Check if request is for image
 */
function isImageRequest(url) {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'];
    return imageExtensions.some(ext => url.pathname.endsWith(ext));
}

/**
 * Sync failed requests when back online
 */
async function syncFailedRequests() {
    console.log('ðŸ”„ [Background Sync] Syncing failed requests...');

    // Get failed requests from IndexedDB (to be implemented)
    const failedRequests = await getFailedRequests();

    for (const req of failedRequests) {
        try {
            await fetch(req.url, req.options);
            console.log('âœ… [Background Sync] Request succeeded:', req.url);
            await removeFailedRequest(req.id);
        } catch (error) {
            console.error('âŒ [Background Sync] Request still failing:', req.url);
        }
    }
}

/**
 * Clear all caches
 */
async function clearAllCaches() {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames.map(name => caches.delete(name)));
    console.log('ðŸ—‘ï¸ [Service Worker] All caches cleared');
}

/**
 * Get total cache size
 */
async function getCacheSize() {
    const cacheNames = await caches.keys();
    let totalSize = 0;

    for (const name of cacheNames) {
        const cache = await caches.open(name);
        const keys = await cache.keys();

        for (const request of keys) {
            const response = await cache.match(request);
            const blob = await response.blob();
            totalSize += blob.size;
        }
    }

    return totalSize;
}

/**
 * Get failed requests from IndexedDB (placeholder)
 */
async function getFailedRequests() {
    // TODO: Implement IndexedDB storage for failed requests
    return [];
}

/**
 * Remove failed request from IndexedDB (placeholder)
 */
async function removeFailedRequest(id) {
    // TODO: Implement IndexedDB removal
}

// ============================================================================
// PUSH NOTIFICATION HANDLER (Future Enhancement)
// ============================================================================

self.addEventListener('push', (event) => {
    console.log('ðŸ“¬ [Service Worker] Push notification received');

    const options = {
        body: event.data ? event.data.text() : 'New update available!',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        vibrate: [200, 100, 200]
    };

    event.waitUntil(
        self.registration.showNotification('ORFEAS Studio', options)
    );
});

self.addEventListener('notificationclick', (event) => {
    console.log('ðŸ”” [Service Worker] Notification clicked');
    event.notification.close();

    event.waitUntil(
        clients.openWindow('/')
    );
});

console.log('ðŸš€ [Service Worker] Loaded and ready');
