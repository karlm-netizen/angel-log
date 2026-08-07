# Changelog — Angel-Log

Jede Änderung an der App kommt hier hinein, im selben Commit wie die Änderung selbst.

> Diese Datei ist am 07.08.2026 angelegt worden. Alles davor steht rückwirkend aus den
> Commit-Nachrichten und der Projektnotiz im ki-os-Vault (`04-projects/angel-log.md`)
> hier drin — knapper als dort, aber vollständig.

## 07.08.2026 — „Statistiken", und Punkte statt Zeitraum

Der Reiter heißt jetzt **Statistiken** (Karls Ansage) — Leiste und Überschrift.

**Der Zeitraum ist raus.** An seiner Stelle steht eine Liste **aller Punkte, die gerade auf
der X-Achse liegen**, zum Ankreuzen, dazu „Alle" und „Keine". Bei *Über: Fischart* also alle
Arten, bei *Über: Wassertiefe* alle Stufen. Nur Angekreuztes steht im Bild.

- ⚠️ **Abgewähltes bleibt in der Liste stehen.** Verschwände es, käme man nie wieder heran.
- ⚠️ **Alle angekreuzt wird als `null` gespeichert, nicht als volle Liste.** Der Unterschied
  zählt bei den gespeicherten Auswertungen: `null` nimmt später dazugekommene Werte von
  selbst mit (eine neu gefangene Fischart taucht auf), eine ausdrückliche Liste bleibt bei
  genau dem, was ausgewählt wurde.
- ⚠️ **Ein Achsenwechsel setzt die Auswahl zurück.** „Hecht, Barsch" auf einer Tiefenachse
  hieße: nichts ausgewählt — und das Bild bliebe kommentarlos leer.
- ⚠️ **Eine Lücke mittendrin wird benannt.** Wer aus einer geordneten Achse einen Punkt in
  der Mitte abwählt, bekommt eine Linie, die über die Lücke hinweg verbindet und dort einen
  Verlauf zeigt, den es nicht gibt — derselbe Fehler, gegen den sonst die leeren Stufen
  stehen. Am Rand kürzen ist harmlos und bleibt unkommentiert.
- Die Auswahl gehört zur Auswertung und wird **als Kopie** gespeichert, nicht als Verweis —
  sonst änderte ein Klick im Baukasten stillschweigend die gespeicherte Auswertung mit.
- Die Punkte-Auswahl beschränkt die **X-Achse, nicht den Bestand**: Kacheln und der Zähler
  in der Kopfzeile sagen weiter, wie viele Fänge in der Auswahl liegen.

⚠️ **Was dabei wegfällt:** die Einschränkung auf 30 Tage / 12 Monate / dieses Jahr. Das Alter
eines Fangs schränkt jetzt nichts mehr ein. Über *Über: Monat* oder *Über: Uhrzeit* plus
Punkte-Auswahl lässt sich Zeitliches weiter eingrenzen, nur nicht mehr als Fenster „ab heute
rückwärts".

**Prüfungen:** 353 grün, darunter 16 neue zur Punkte-Auswahl.

## 07.08.2026 — Neues App-Icon

Karls Vorlage (Bild auf Discord, *„nimm das linke als app icon"*): springender Fisch mit
Rute und Haken über einer Welle. Aus dem Entwurf freigestellt, entrauscht (der Entwurf hatte
senkrechte Streifen im Grund) und auf den App-Hintergrund `#0e1418` gesetzt — dieselbe Farbe
wie `theme_color`, damit beim Start kein andersfarbiges Rechteck aufblitzt.

- `icon-192.png` und `icon-512.png` neu, Motiv auf 78 % der Kantenlänge.
- ⚠️ **`icon-maskable-512.png` ist neu und eine eigene Datei.** Vorher trugen beide Icons
  `purpose: "any maskable"`. Android schneidet aus einem maskable Icon einen Kreis heraus —
  ein Icon, das beides sein soll, muss sein Motiv in der inneren 80 %-Zone halten und ist
  dann überall zu klein. Jetzt: normale Icons groß, das maskable mit Motiv auf 60 %.
- `icon.svg` (der alte grüne Fisch) ist **raus** — aus dem Manifest, aus dem Kopf der Seite
  und aus dem Service Worker. Der Browser-Reiter nimmt jetzt `icon-192.png`.
- Service-Worker auf `v12`.

⚠️ **Am iPhone reicht Neuladen nicht.** iOS merkt sich das Symbol beim Anlegen der
Verknüpfung. Alte Verknüpfung vom Home-Bildschirm löschen, Seite in Safari öffnen, über
Teilen → „Zum Home-Bildschirm" neu anlegen.

## 07.08.2026 — Am PC mehrere Auswertungen nebeneinander

Ab 900 px Breite steht neben der eingestellten Auswertung **jede gespeicherte** — ein Raster
aus so vielen Spalten, wie hineinpassen (drei bei 1400 px). Genau dafür gibt es die
gespeicherten: nebeneinander lassen sie sich vergleichen, untereinander muss man sich das
zweite Bild merken. Am Handy bleibt es bei einer; dort wäre alles andere nur Scrollen.

- Jedes Diagramm hat seine **eigene Ablesehilfe**. Ein gemeinsames Fadenkreuz über
  verschiedene Achsen hinweg würde Stellen verbinden, die nichts miteinander zu tun haben.
- Jede gespeicherte Auswertung bringt **ihre eigenen Filter** mit (Gewässer, Zeitraum,
  Fischart) — sie folgt nicht der Filterzeile oben, sonst wäre sie nicht mehr die
  gespeicherte.
- Die **Bedienelemente wachsen bewusst nicht mit** (760 px). Ein Auswahlfeld über zwei Meter
  liest sich schlechter, nicht besser — dieselbe Regel wie bei der Fangliste seit dem 02.08.
- Kacheln, Wenig-Daten-Warnung und der Schlusshinweis laufen über die ganze Breite.
- ⚠️ **Der Verteilungs-Hinweis steht jetzt einmal unter allem statt in jeder Karte.** Bei
  fünf Auswertungen nebeneinander war derselbe Absatz fünfmal kein Hinweis mehr, sondern
  Rauschen. Kartenspezifische Hinweise (Mehrfachzählung bei Farben, „Übrige", fehlende
  Reihenfolge) bleiben je Karte.

**Prüfungen:** 330 grün, darunter zehn neue zum großen Bildschirm — dass mehrere Diagramme
da sind, dass sie in einer Reihe stehen und nicht untereinander, dass am Handy nur eines
bleibt, und dass die geladene Auswertung nicht doppelt erscheint.
⚠️ Diese Prüfungen laufen im iframe über `w.eval(…)`: `state` ist im geladenen Dokument ein
`const` auf oberster Ebene und damit **keine** Eigenschaft von `window` — `w.state` ist
undefined, `w.eval('state…')` sieht die Bindung.

## 07.08.2026 — Statistik-Baukasten, Angelzeit ans Konto

**Die Statistik ist ein Baukasten statt einer Liste.** Vorher standen sechs fertige
Auswertungen zur Wahl (davor siebzehn). Beides beantwortete nie die Frage, die man
gerade hat. Eine Auswertung besteht jetzt aus fünf Angaben:

| Angabe | Was sie tut |
|---|---|
| **Zählen** | alle Fische, oder nur eine Art |
| **Über** | was auf der X-Achse steht — 17 Größen zur Wahl |
| **Aufteilen nach** | je Köder bzw. Köderfarbe eine eigene Kurve (Ankreuzkästchen) |
| **Gewässer** | Einschränkung |
| **Zeitraum** | Einschränkung |

- **Auswertungen lassen sich speichern**, wieder laden, umbenennen, ändern und löschen.
  Sie liegen **am Konto**, nicht nur im Gerät.
- **Alles ist eine Kurve. Balken gibt es nicht mehr.** Vorher fiel alles unter drei Stufen
  auf Balken zurück, und Kategorien blieben grundsätzlich Balken. Jetzt gibt es eine Kurve
  ab dem ersten Fang und für jede der 17 Größen; die X-Achse wird auf mindestens fünf Stufen
  aufgezogen, damit eine Kurve als Kurve zu erkennen ist.
  ⚠️ Das erfindet nichts — die angehängten Stufen haben tatsächlich null Fänge.
- **Echte Achsen.** Y-Achse mit Gitterlinien und Beschriftung (nur ganze Zahlen, Fänge sind
  keine Bruchteile), X-Achse mit Titel darunter. Beschriftet wird nur noch der höchste Punkt
  je Kurve; alles andere liest man an der Achse ab oder tippt es an. Lange Achsentexte werden
  gekürzt und ausgedünnt, vollständig stehen sie in der Ablesehilfe.
- **Ablesehilfe:** Antippen setzt ein Fadenkreuz und zeigt die Werte aller Kurven an dieser Stelle.
- ⚠️ **Der Einwand gegen Kurven über Kategorien** — eine Linie zwischen „Hecht" und „Barsch"
  behauptet eine Reihenfolge, die es nicht gibt — ist damit nicht erledigt, sondern in einen
  **Hinweis unter dem Bild** gewandert: *„Diese Achse hat keine natürliche Reihenfolge …
  aussagekräftig ist die Höhe der Punkte, nicht der Anstieg dazwischen."* Karl kennt ihn und
  will es so; wer hier später etwas ändert, soll ihn nicht neu erfinden müssen.
- **Nebeneffekt, und ein guter:** Tageszeit, Mondphase, Wetter und Wassertrübung haben jetzt
  ihre **natürliche Reihenfolge** statt einer nach Häufigkeit, und ihre leeren Stufen stehen
  mit null drin. Als Balkenliste war das egal, als Kurve ist es der Unterschied zwischen
  richtig und falsch. Nur Fischart, Köder, Köderfarbe und Gewässer stehen weiter nach
  Häufigkeit — sie haben keine natürliche Ordnung.
- **Die obersten beiden Kacheln sind getauscht** — Fischarten steht jetzt vor Fänge.

**Angelzeit und Auswertungen hängen am Konto.** Bis heute lag die aufsummierte Angelzeit
ausschließlich im `localStorage`. Gerettet hat sie einzig das Backup — und das ist am
04.08. ausgebaut worden. Damit war sie das Einzige in der ganzen App, das ein
Gerätewechsel oder gelöschte Browserdaten wirklich gekostet hätten; alle Fänge kommen
über den Sync zurück. Neue Tabelle `angel_werte` (eine Zeile je Konto und Schlüssel).

⚠️ **`supabase.sql` muss dafür einmal neu ausgeführt werden.** Ohne die neue Tabelle
läuft die App weiter, der Abgleich der beiden Werte scheitert aber still.

- Konflikte entscheidet die jüngere Bearbeitung, **nicht der größere Wert**. Naheliegend
  wäre Letzteres, es macht aber „Gesamtzeit direkt setzen" kaputt: eine Korrektur von 40 h
  auf 10 h käme nie gegen den alten Wert an.
- Der **laufende Ansitz** bleibt im Gerät. Ein fremder Startzeitpunkt nützt einem zweiten
  Gerät nichts, und beim Stoppen landet die Dauer ohnehin in der Gesamtzeit.
- Die **Datenschutzerklärung** nennt beides jetzt ausdrücklich, und der Daten-Download
  (Art. 20 DSGVO) enthält sie ebenfalls.

**Farben für übereinanderliegende Kurven.** Sechs Reihenfarben, je eine Stufe für helle
und dunkle Paletten. Rechnerisch geprüft statt nach Augenmaß: Helligkeitsband, Buntheit,
Abstand benachbarter Farben unter simulierter Rot-/Grünblindheit und Kontrast gegen die
Kartenfläche — gegen die dunkelste und hellste der zwölf Paletten.
⚠️ Mehr als sechs Kurven gibt es nicht; was nicht in die ersten fünf passt, wird als
„Übrige" zusammengefasst. Eine siebte Farbe wäre geraten.
⚠️ In den hellen Paletten liegen drei der sechs unter 3:1 — deshalb ist die Legende ab
zwei Kurven Pflicht und nicht abschaltbar.

**Sonstiges:** eigene Texte (Ködername, Gewässer, Name einer Auswertung) werden jetzt
entschärft, bevor sie ins Bild wandern — ein Anführungszeichen im Ködernamen hätte das
SVG zerrissen. Service-Worker auf `v11`.

**Prüfungen:** 319 grün, darunter 13 zum Werte-Abgleich und sechs zum Layout auf
320/360/390 px. Die Layout-Prüfungen laufen über ein iframe mit fester Breite — Chrome
headless ignoriert auf diesem PC `--window-size` fürs Layout und meldet sonst überall
dieselbe Breite.

## 04.08.2026 — Statistik zurück, Backup raus, Anmelde-Pflicht

- Statistik wieder in der App, aber **schmal**: sechs Auswertungen statt siebzehn (`2e808a9`).
- **Backup raus**, der Daten-Download ist unter die Datenschutzerklärung gewandert (`b059cd4`).
- **Verantwortlicher eingetragen**, Sonne wird zum Zahnrad (`84e8908`).
- **Benutzername beim Registrieren**, Anmelden wahlweise damit oder mit E-Mail (`9f8a376`).
- **Anmelde-Pflicht**: Schirm beim Start statt Konto in den Einstellungen (`506fdfe`).
- **Cloud scharf geschaltet** — Projekt eingetragen, Kette gegen den Server geprüft (`8370947`).

## 03.08.2026 — Konto, Cloud-Sync, Datenschutzerklärung (`773a665`)

Konto mit E-Mail/Benutzername, Abgleich über Supabase (EU). Zwei Uhren (Geräteuhr für
Konflikte, Serveruhr fürs Nachladen), Grabsteine für Gelöschtes, Herunterladen in zwei
Schritten. Fotos verkleinert (220 KB je Bild) mit in die Datenbank. Datenschutzerklärung,
die sich anpasst, ob die Cloud konfiguriert ist.

## 02.08.2026 — Auswertung, Trübung, Timer, Breite am PC

- **Statistik-Reiter** mit einer Filterzeile für alles darunter (`83b7e66`), danach
  **auswählen statt scrollen** (`9473cf3`, `fefde6e`) — und am selben Abend auf Karls
  „funktioniert noch nicht so gut" wieder **herausgenommen** (`dd75dcc`, Branch
  `statistik-entwurf`, Tag `statistik-v1`).
- **Wassertrübung** in vier Stufen zum Antippen, dazu Regen der letzten 24/48 h und
  Pegeltrend (`6f6d568`). Automatisch ging nicht: die WSV misst Trübung an sechs
  Messstellen in ganz Deutschland, alle an der Nordsee.
- **Kurven statt Balken** für alles Messbare — bei Messwerten bedeutet die Reihenfolge etwas.
- **Angelzeit-Timer** mit Start/Stopp und aufsummierter Gesamtzeit (`287a820`). Gespeichert
  wird der Startzeitpunkt, nicht ein mitlaufender Zähler — am iPhone wird eine PWA im
  Hintergrund eingefroren. Dazu drei Wege gegen „vergessen zu stoppen" (`d493b3b`).
- **Breite am PC**: die Fangliste füllt so viele Spalten, wie hineinpassen (`ba77adc`).
- **Mondphase und Wetter automatisch** (`8e4561b`). Die Mondphase wird gerechnet statt
  gespeichert — funktioniert offline und reicht beliebig weit zurück.

## 01.08.2026 — Köderfarben als Mehrfachauswahl (`30ce6de`, `9b60301`)

Ein Köder hat selten nur eine Farbe. **Firetiger** liegt als Farbverlauf vor, nicht als
Hex-Wert. ⚠️ Datenformat geändert: gespeichert wird die Liste `farben`, gelesen wird
immer über `farbenVon(rec)` — alte Fänge haben ein einzelnes `farbe`.
Überstehendes Datumsfeld am iPhone behoben (`-webkit-appearance:none`).

## 31.07.2026 — v1

Fangbuch für einen Angel-Kollegen: Fisch, Bedingungen, Köder, Standort auf der Karte,
Fotos. Alles offline im Gerät, alles in einer Datei (`index.html`).
