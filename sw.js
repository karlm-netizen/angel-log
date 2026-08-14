// Angel-Log Service Worker.
// Eigene Dateien: Netz zuerst, damit Updates sofort ankommen — Cache nur als Offline-Rückfall.
// Kartenkacheln und Leaflet: Cache zuerst, denn am Wasser ist oft kein Netz und einmal
// angeschaute Gewässer sollen offline noch da sein. Wetter-API: nie cachen.
const CACHE  = 'angellog-v51';
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

/* ================= Push: neue Antwort auf ein Ticket (13.08.2026) =================
   Karls Ansage: „Ja mit pushbenachrichtigung, nur von wegen neue antwort auf dein
   ticket, ganz einfach."

   ⚠️ **Ohne Nutzlast.** Der Bot schickt einen leeren Anstoß, der Text steht hier fest.
   Zwei Gründe, und beide zählen:
   1. Der Ticket-Text ginge sonst durch die Server von Apple bzw. Google. Er enthält,
      was jemand an der App auszusetzen hat — das muss dort nicht liegen.
   2. Eine Nutzlast muss verschlüsselt werden (aes128gcm, ECDH je Empfänger). Ohne sie
      genügt die VAPID-Signatur, und das ist deutlich weniger, was schiefgehen kann.

   ⚠️ **`showNotification` ist Pflicht, nicht Kür.** Wer ein Push-Ereignis empfängt und
   nichts anzeigt, wird von den Browsern nach ein paar Malen von der Zustellung
   ausgeschlossen („silent push"). Deshalb wird immer etwas gezeigt — auch wenn die
   Nachricht mal ohne erkennbaren Grund kommt. */
self.addEventListener('push', e => {
  // Falls doch einmal etwas mitkommt, darf es den Handler nicht umwerfen.
  let daten = {};
  try { if (e.data) daten = e.data.json(); } catch { daten = {}; }

  /* ⚠️ **Der Titel IST die Nachricht, ein Rumpf darunter steht nicht mehr da.**
     Hier stand `showNotification('Angel-Log', { body: 'Neue Antwort …' })`. Am iPhone
     kam das als drei Zeilen heraus (Karls Meldung vom 13.08.2026):

         angel-log            ← der Name der Verknüpfung, den setzt iOS selbst davor
         from angel-log       ← das war dieser Titel
         Neue Antwort …       ← der Rumpf

     Der Name der App steht am iPhone ohnehin schon über jeder Nachricht. Ihn im Titel
     zu wiederholen hat ihn nur ein zweites Mal hingeschrieben. Jetzt trägt der Titel
     den Satz, der Rumpf entfällt — eine Zeile Inhalt statt zweimal derselbe Name.

     ⚠️ Auch auf Android und am PC ist das die bessere Fassung: dort steht der Titel
     groß und der Rumpf klein darunter. „Angel-Log / Neue Antwort" hätte die einzige
     echte Auskunft ins Kleingedruckte gesetzt. */
  const text = daten.text || 'Neue Antwort auf deine Meldung.';
  e.waitUntil(self.registration.showNotification(text, {
    icon: './icon-192.png',
    badge: './icon-192.png',
    /* Gleiches `tag` heißt: eine zweite Antwort ersetzt die erste, statt den
       Sperrbildschirm zuzustellen. Bei einem Postfach ist „es liegt etwas an"
       die Auskunft, nicht die Anzahl. */
    tag: 'angel-ticket',
    data: { url: './' }
  }));
});

/* Tippen auf die Nachricht: ein bereits offenes Fenster nach vorn holen, sonst eines
   öffnen. ⚠️ Ohne das Suchen nach einem offenen Fenster öffnet iOS eine **zweite**
   Instanz der App — mit eigenem Zustand, und der Fang, den man gerade eintippt, wäre
   im anderen Fenster. */
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil((async () => {
    const ziel = new URL((e.notification.data && e.notification.data.url) || './', self.location.href).href;
    const fenster = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const f of fenster){
      if (f.url.startsWith(self.registration.scope) && 'focus' in f) return f.focus();
    }
    if (self.clients.openWindow) return self.clients.openWindow(ziel);
  })());
});
