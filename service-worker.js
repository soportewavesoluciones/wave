self.addEventListener('install', function(event) {
    event.waitUntil(
      caches.open('wave-cache').then(function(cache) {
        return cache.addAll([
          '/index.html',
          '/style.css',
          '/script.js'
          // Aquí incluye cualquier otro archivo que desees cachear
        ]);
      })
    );
});

  self.addEventListener('fetch', function(event) {
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
});
  