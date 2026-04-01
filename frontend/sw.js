// ─── HabitGrow Service Worker ───────────────────────────────────────────────
// Incrementa CACHE_VERSION en cada deploy para invalidar caché anterior.
const CACHE_VERSION = 'anim004';
const CACHE_NAME = `habitgrow-cache-${CACHE_VERSION}`;

// Assets que se pre-cachean (solo imágenes y recursos lentos)
const PRECACHE_ASSETS = [
  './assets/icon.png',
  './assets/mascotas/Gizzmo/Idle.jpg',
  './assets/mascotas/Gizzmo/animations/tap.webp',
  './js/petAnimator.js'
];

// ── INSTALL: pre-cachear solo assets pesados ─────────────────────────────────
self.addEventListener('install', event => {
  // Activa este SW inmediatamente sin esperar a que cierren las pestañas
  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(PRECACHE_ASSETS);
    })
  );
});

// ── ACTIVATE: eliminar cachés antiguas y tomar control de inmediato ───────────
self.addEventListener('activate', event => {
  event.waitUntil(
    Promise.all([
      // Tomar control de todas las pestañas abiertas sin recargar
      clients.claim(),
      // Eliminar todos los cachés que no sean el actual
      caches.keys().then(cacheNames =>
        Promise.all(
          cacheNames
            .filter(name => name !== CACHE_NAME)
            .map(name => caches.delete(name))
        )
      )
    ])
  );
});

// ── FETCH: estrategia según tipo de recurso ───────────────────────────────────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // 1. Ignorar peticiones a la API — siempre van a la red
  if (url.pathname.includes('/api/')) return;

  // 2. HTML, JS y CSS → Network-First (siempre fresco, cache como fallback)
  const isDocument = event.request.destination === 'document';
  const isScript   = event.request.destination === 'script';
  const isStyle    = event.request.destination === 'style';

  if (isDocument || isScript || isStyle) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Guardar copia fresca en cache
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request)) // Fallback offline
    );
    return;
  }

  // 3. Imágenes y otros assets → Cache-First (cambian poco)
  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request).then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      });
    })
  );
});

// ── PUSH: Manejar notificaciones entrantes ──────────────────────────────────────
self.addEventListener('push', event => {
  let data = {
    title: 'HabitGrow',
    body: '¡Es hora de revisar tus hábitos!',
    url: '/'
  };
  
  try {
    if (event.data) {
      data = event.data.json();
    }
  } catch (e) {
    console.warn('Push event received non-JSON data:', event.data.text());
    try {
        data.body = event.data.text();
    } catch(e2) {}
  }

  const title = data.title || 'HabitGrow';
  const options = {
    body: data.body,
    icon: './assets/icon.png',
    badge: './assets/icon.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// ── NOTIFICATION CLICK: Abrir la app al hacer clic ─────────────────────────────
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  const targetUrl = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      for (const client of windowClients) {
        if (new URL(client.url, self.location.origin).pathname === new URL(targetUrl, self.location.origin).pathname) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
