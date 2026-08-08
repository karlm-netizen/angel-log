// Angel-Log Service Worker.
// Eigene Dateien: Netz zuerst, damit Updates sofort ankommen — Cache nur als Offline-Rückfall.
// Kartenkacheln und Leaflet: Cache zuerst, denn am Wasser ist oft kein Netz und einmal
// angeschaute Gewässer sollen offline noch da sein. Wetter-API: nie cachen.
const CACHE  = 'angellog-v21';
const TILES  = 'angellog-tiles';
/* ⚠️ Die sechs Ladebildschirm-Fotos gehören hier hinein. Ohne sie im Cache stünde am
   Wasser ohne Netz ein Ladebildschirm ohne Bild — und genau dort wird die App benutzt.
   Zusammen knapp 1 MB, einmal beim Einrichten geholt; je Start wird nur eins gezeigt. */
const SPLASH = ['./splash-1.jpg', './splash-2.jpg', './splash-3.jpg',
                './splash-4.jpg', './splash-5.jpg', './splash-6.jpg'];
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-512.png',
  './apple-touch-icon.png', ...SPLASH,
  './leaflet/leaflet.js', './leaflet/leaflet.css',
  './leaflet/images/marker-icon.png', './leaflet/images/marker-icon-2x.png',
  './leaflet/images/marker-shadow.png', './leaflet/images/layers.png', './leaflet/images/layers-2x.png'];
const TILE_MAX = 800;

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => Promise.all(ASSETS.map(a => c.add(a).catch(() => {}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== TILES).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Ältestes Drittel wegwerfen, wenn der Kachel-Cache zu groß wird.
async function trimTiles(){
  const c = await caches.open(TILES);
  const keys = await c.keys();
  if (keys.length <= TILE_MAX) return;
  await Promise.all(keys.slice(0, keys.length - TILE_MAX + 200).map(k => c.delete(k)));
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Wetterdaten immer frisch holen.
  if (url.hostname === 'api.open-meteo.com') return;

  // Kartenkacheln: erst Cache, dann Netz — und ein Netzfehler darf die Anfrage
  // nicht platzen lassen, sonst meldet die Karte fälschlich einen Ausfall.
  if (url.hostname.endsWith('tile.openstreetmap.org')){
    e.respondWith(
      caches.open(TILES).then(c =>
        c.match(req).then(hit => hit || fetch(req).then(r => {
          if (r.ok || r.type === 'opaque'){ c.put(req, r.clone()); trimTiles(); }
          return r;
        }).catch(() => Response.error()))
      )
    );
    return;
  }

  // Alles Fremde (Supabase, PEGELONLINE, Marine-API) läuft ungefiltert durch.
  // ⚠️ Konto- und Fangdaten dürfen nie in einen Cache — sie gehören ins Gerät
  // und in die Datenbank, nicht in einen Zwischenspeicher, den niemand leert.
  if (url.origin !== location.origin) return;

  e.respondWith(
    fetch(req)
      .then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return r; })
      .catch(() => caches.match(req).then(m => m || caches.match('./index.html')))
  );
});
