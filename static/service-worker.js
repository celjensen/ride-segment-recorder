const CACHE_NAME = 'ride-recorder-cache-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/service-worker.js'
];

// Install event, cache necessary files
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event, serve cached content when offline
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        return response || fetch(event.request);
      })
  );
});
