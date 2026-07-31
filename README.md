# Angel-Log

Fangbuch als PWA fürs iPhone. Jeder Fang mit Bedingungen, Köder, Foto und Stelle auf der Karte —
damit sich nach ein paar Wochen ablesen lässt, wann und womit was beißt.

## Erfasst wird

- Fischart, Länge, Gewicht, Datum & Uhrzeit, Gewässer
- Wassertemperatur und Wassertiefe (manuell)
- Lufttemperatur, Luftdruck, Windrichtung und Windstärke — automatisch zum Fangzeitpunkt
  über [Open-Meteo](https://open-meteo.com) (kein Account, kostenlos), jederzeit überschreibbar
- Tageszeit: Morgendämmerung / Tag / Abenddämmerung / Nacht, vorbelegt aus Sonnenauf- und -untergang
- Köder, Ködergröße, Köderfarbe
- Fotos (Kamera oder Galerie), Notiz
- Standort per GPS, Pin auf der Karte korrigierbar

## Wo die Daten liegen

Ausschließlich auf dem Gerät (IndexedDB). Kein Server, kein Account, keine Anmeldung.
Deshalb: über das Menü oben rechts regelmäßig **Backup exportieren**. Beim Löschen der
Safari-Daten oder Entfernen der App vom Homescreen sind die Fänge sonst weg.

## Installieren

Link in **Safari** öffnen → Teilen-Symbol → *Zum Home-Bildschirm*.
Danach startet sie wie eine normale App, ohne Browserleiste.

Beim ersten Fang fragt iOS nach dem Standort — erlauben, sonst gibt es keine Karte
und keine automatischen Wetterwerte.

## Offline

Erfassen inklusive Fotos und GPS läuft komplett ohne Netz. Nur die Kartenkacheln und die
Wetterwerte brauchen Verbindung; bereits angesehene Kartenausschnitte bleiben zwischengespeichert.

## Technik

Eine `index.html` ohne Build-Schritt, dazu Service Worker und Manifest. Karte: Leaflet + OpenStreetMap.
