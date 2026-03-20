// Estrategia Cache-First para estáticos
const CACHE_NAME = 'habitgrow-cache-v1';
const urlsToCache = [
  './',
  './index.html',
  './dashboard.html',
  './css/style.css',
  './css/dashboard.css',
  './js/auth.js',
  './js/dashboard.js',
  './js/pwa.js',
  './assets/icon.png',
  './assets/mascotas/Gizzmo/Idle.jpg'
  // Puedes añadir más assets relevantes
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  // Ignorar peticiones a la API para asegurar frescura de datos
  if (event.request.url.includes('/api/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Devuelve cache si existe, sino hace fetch
        return response || fetch(event.request);
      })
  );
});

// Limpieza de cachés antiguas
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
