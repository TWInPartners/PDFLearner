const CACHE_NAME = 'pdf-flashcards-v1';
const urlsToCache = [
    '/',
    '/manifest.json',
    // Add other static assets here
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline functionality
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // Handle background sync for flashcard data
            syncFlashcardData()
        );
    }
});

async function syncFlashcardData() {
    try {
        // This would sync any offline changes when connection is restored
        console.log('Background sync triggered');
        // Implementation would depend on your data storage strategy
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// Push notifications (optional feature)
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'New flashcard study reminder!',
        icon: '/icon-192x192.png',
        badge: '/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '2'
        },
        actions: [
            {
                action: 'explore',
                title: 'Study Now',
                icon: '/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/icons/xmark.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('PDF Flashcards', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
        // Open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
