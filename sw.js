// Angel-Log Service Worker.
// Eigene Dateien: Netz zuerst, damit Updates sofort ankommen — Cache nur als Offline-Rückfall.
// Kartenkacheln und Leaflet: Cache zuerst, denn am Wasser ist oft kein Netz und einmal
// angeschaute Gewässer sollen offline noch da sein. Wetter-API: nie cachen.
const CACHE  = 'angellog-v2';
const TILES  = 'angellog-tiles';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icon.svg', './icon-192.png', './icon-512.png'];
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

  const isTile  = url.hostname.endsWith('tile.openstreetmap.org');
  const isVendor = url.hostname === 'unpkg.com';

  if (isTile || isVendor){
    e.respondWith(
      caches.open(TILES).then(c =>
        c.match(req).then(hit => hit || fetch(req).then(r => {
          if (r.ok || r.type === 'opaque'){ c.put(req, r.clone()); if (isTile) trimTiles(); }
          return r;
        }))
      )
    );
    return;
  }

  if (url.origin !== location.origin) return;

  e.respondWith(
    fetch(req)
      .then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return r; })
      .catch(() => caches.match(req).then(m => m || caches.match('./index.html')))
  );
});
