# Angel-Log

Fangbuch als PWA fürs iPhone. Jeder Fang mit Bedingungen, Köder, Foto und Stelle auf der Karte —
damit sich nach ein paar Wochen ablesen lässt, wann und womit was beißt.

## Erfasst wird

- Fischart, Länge, Gewicht, Datum & Uhrzeit, Gewässer
- Lufttemperatur, Luftdruck, Windrichtung und Windstärke — automatisch zum Fangzeitpunkt
  über [Open-Meteo](https://open-meteo.com) (kein Account, kostenlos), jederzeit überschreibbar
- Wassertemperatur — ebenfalls automatisch, aus zwei Quellen (siehe unten)
- Wassertiefe (manuell)
- Tageszeit: Morgendämmerung / Tag / Abenddämmerung / Nacht, vorbelegt aus Sonnenauf- und -untergang
- Köder, Ködergröße, Köderfarbe
- Fotos (Kamera oder Galerie), Notiz
- Standort per GPS, Pin auf der Karte korrigierbar

## Woher die Wassertemperatur kommt

Zwei Quellen, in dieser Reihenfolge:

1. **[PEGELONLINE](https://www.pegelonline.wsv.de) der WSV** — echte Messwerte an den
   Bundeswasserstraßen, minütlich aktualisiert. Die App nimmt die nächstgelegene Messstelle
   im Umkreis von 25 km und zeigt Name und Entfernung an. Auch rückwirkend abfragbar,
   falls der Fang erst später eingetragen wird.
2. **Open-Meteo Marine** — Oberflächentemperatur, nur an der Küste und auf See, Modellwert.

Für abgelegene Seen, Weiher und Teiche gibt es keine dieser Quellen. Dann bleibt das Feld
leer und muss selbst gemessen werden — ein geschätzter Wert wäre für spätere Auswertungen
schlimmer als gar keiner. Jeder Fang merkt sich, woher sein Wert stammt (Messstelle,
Meeresmodell oder selbst gemessen), damit sich die Zahlen später sauber vergleichen lassen.

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
