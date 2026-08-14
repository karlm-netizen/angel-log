# Changelog — Angel-Log

Jede Änderung an der App kommt hier hinein, im selben Commit wie die Änderung selbst.

> Diese Datei ist am 07.08.2026 angelegt worden. Alles davor steht rückwirkend aus den
> Commit-Nachrichten und der Projektnotiz im ki-os-Vault (`04-projects/angel-log.md`)
> hier drin — knapper als dort, aber vollständig.

## 14.08.2026 (v51) — Die Einführung passt wieder zur App

Karls Ansage: *„Einführung aktualisieren das die auf das neue app dising zugeschnitten ist und
ergänzen."*

Zwischen dem 12. und 13.08. hat sich die Bedienung geändert — **vier Reiter unten statt Kacheln,
Home als erste Ansicht, Einstellungen als eigene Seite**. Die Einführung beschrieb noch den Stand
davor. **Home kam darin überhaupt nicht vor**, obwohl die App dort aufgeht: die erste Ansicht,
die jemand sieht, war die einzige, die niemand erklärt hat.

- 🏠 **Neue Karte: „Beim nächsten Öffnen landest du hier."** Angelzeit, Wetter am Wasser mit den
  nächsten Stunden, und — sobald genug Fänge da sind — wann es bisher am besten lief. Dazu die
  vier Bereiche der Leiste.
  ⚠️ **Sie steht direkt hinter der Führung, und das ist kein Zufall.** `fuehrungBeenden()`
  schaltet die Einführung genau eine Karte weiter — die Karte erscheint also **im Moment des
  Speicherns**, wenn der Benutzer tatsächlich auf Home landet. Davor stünde sie vor einer leeren
  App: ohne einen einzigen Fang kann Home weder Angelzeit noch Prognose zeigen.
- 🎣 **„Dein Fangbuch"** nennt jetzt, was die Liste seit dem 13.08. wirklich ist: Bildkacheln
  nebeneinander, mit Suche, Sortierung und Karte.
- 📈 **„Und dann wird es interessant"** sagt, wo die Auswertungen stecken (unter „Fänge") und
  dass man sie selbst zusammenstellt — und dass ausschließlich mit den eigenen Fängen gerechnet
  wird.
- ⚠️ **Ein sechster Führungsschritt auf die Reiterleiste war gebaut und ist wieder raus.**
  `#fab-save` ruft `fuehrungBeenden()`, bevor gespeichert wird — wer dem Schritt davor folgt und
  wirklich speichert, hätte ihn nie gesehen. Er wäre nur für die erreichbar gewesen, die statt
  auf „Speichern" auf „Weiter" tippen. Die Leiste erklärt stattdessen die Home-Karte, und die
  kommt genau an der richtigen Stelle.
- ⚠️ **Die alte Regel gilt weiter: keine Bedienungsanleitung.** Die Karten sagen weiter, was die
  App tut, und nennen die Bereiche nur nebenbei. Wer eine Liste von Knöpfen lesen wollte, hätte
  sie nicht gelesen.

**632 Prüfungen grün** (von 630). Eine davon leitet die Bereiche **aus der Leiste selbst** ab:
kommt ein Reiter dazu oder wird einer umbenannt, fällt sie. Ohne das beschreibt die Einführung
irgendwann wieder einen Aufbau von vorgestern, und niemand merkt es, weil beides für sich
genommen stimmig aussieht.

⚠️ Die Prüfung fiel zuerst mit „Bereich *0* wird nicht genannt" — der Einstellungen-Reiter trägt
die rote Zahl als Kindelement, und die zählt zum Text, auch wenn sie versteckt ist.

## 14.08.2026 (v50) — Nach dem Abschicken einer Meldung kommt die Frage

Karls Ansage: *„Nachdem man ein Ticket abgeschickt hat fragen ob benachrichtiguen angezeigt
werden sollen."*

Bisher stand die Benachrichtigung als Knopf in den Einstellungen — man musste wissen, dass es
sie gibt. Jetzt kommt die Frage im einzigen Moment, in dem sie sich von selbst erklärt:
**direkt nachdem eine Meldung rausgegangen ist.** Zwei Antworten, „Ja, benachrichtigen" und
„Nein danke".

- ⚠️ **Erst die eigene Frage, dann der Systemdialog — und das ist keine Höflichkeit.** Ein
  Gerät fragt genau **einmal**. Wer wegtippt, hat Benachrichtigungen dauerhaft aus, und die App
  kann das nie wieder ändern; nur die Geräte-Einstellungen können es. Deshalb löst der Kasten
  von sich aus nichts aus — der Systemdialog kommt erst nach einem Tipp auf „Ja".
  ⚠️ **iOS verlangt dafür ohnehin eine Nutzergeste.** Eine Frage, die beim Abschicken
  automatisch den Systemdialog aufriefe, verbrennt die eine Chance also wirkungslos.
- **Gefragt wird nur, wenn die Antwort etwas ändert.** Nicht ohne Konto (dann weiß niemand,
  wohin die Antwort gehört), nicht in Safari ohne Home-Bildschirm (dort gibt es keinen
  PushManager), nicht nach einer Ablehnung des Geräts, nicht wenn es schon läuft — und nach
  einem „Nein danke" nie wieder.
- ⚠️ Der Kasten steht **außerhalb** des Meldeformulars. Darin wäre er beim Abschicken
  mit zugeklappt worden und nie zu sehen gewesen.
- ⚠️ **Die Entscheidung steht in einer eigenen Funktion, getrennt vom Einsammeln des
  Zustands.** Sonst hinge jede Prüfung daran, ob der Prüf-Browser gerade einen PushManager hat
  und ein Konto angemeldet ist — dann misst die Prüfung den Prüflauf und nicht die Regel.

**630 Prüfungen grün** (von 620), darunter eine, die den Systemdialog abfängt und zählt: die
Frage allein darf ihn nicht auslösen.

## 14.08.2026 (v49) — Wie alt die Vorhersage ist, und Fotos in jedem Format

Zwei Ansagen von Karl.

### 🕒 Der Stand der Wettervorhersage steht oben — und läuft mit

*„Wetterprognose aktuell (Uhrzeit Datum nach oben und in min und Stunden wielange letzte
Aktualisierung her ist) nach 6 Stunden in gelb oder rot."*

Der Zeitstempel stand als **letzte** Zeile unter dem Stundenstreifen — also hinter allem, was er
einordnen soll. Jetzt steht er direkt unter dem Ort, ganz oben, und nennt drei Dinge:
**Uhrzeit, Datum und wie lange es her ist** („Stand 16:42 · 14.08.2026 · vor 12 Min").

- **Nach 6 Stunden wird die Zeile gelb, nach 12 Stunden rot.**
- ⚠️ **Die Angabe wird nachgeführt, nicht einmal geschrieben.** Eine Zeile, die beim Zeichnen
  „vor 1 Min" sagt und das drei Stunden lang stehen lässt, ist schlechter als gar keine: sie
  behauptet Frische. Am Wasser bleibt die App stundenlang offen, ohne neu zu zeichnen — genau
  dort soll sie ja etwas sagen. Ein Wecker führt sie alle 30 Sekunden nach, und beim
  Zurückholen der App aus dem App-Switcher sofort.
- ⚠️ **Die 30 Minuten, nach denen die App von selbst neu holt, sind etwas anderes als diese
  sechs Stunden.** Solange Netz da ist, wird die Zeile nie gelb. Sie färbt sich genau dann,
  wenn seit Stunden nichts mehr durchkam — dieselbe stille Strecke, die diese Woche dreimal
  zugeschlagen hat: es sieht alles normal aus, nur die Zahlen sind von gestern.
- ⚠️ Ganze Sätze mit Platzhalter statt zusammengeklebter Wortstücke: „vor" + Zahl + „Min"
  ergäbe auf Englisch „ago 3 min".

### 📷 Alle Fotos werden komplett angezeigt, egal welches Format

*„Alle Fotos komplett anzeigen egal welches format."*

Die Kachel war am 13.08. hochkant geworden, damit Handyfotos nicht mehr oben und unten
beschnitten werden. **Für ein Querformat-Foto blieb der Schnitt** — `cover` füllt die Kachel und
schneidet ab, was nicht ins Verhältnis passt. Jetzt `contain`: jedes Format wird ganz gezeigt,
dafür bleibt Rand. Auch die kleine Vorschau im Formular schnitt zu und tut es nicht mehr.

- ⚠️ **`object-position:top` ist hier kein Geschmack, sondern der Grund, warum der Text nichts
  verdeckt.** Mittig ausgerichtet säße ein Querformat-Foto genau so tief, dass die Textleiste
  in sein letztes Viertel liefe — und dort steht beim Angeln der Fisch.
- ⚠️ **Karls Ansage vom 13.08. gilt weiter** („der Text liegt auf dem Foto"). Beides zusammen
  geht, weil der **Bildkasten** die Kachel weiterhin ganz füllt und nur das **gezeichnete Bild**
  darin kleiner ist. Die alte Prüfung misst den Kasten, die neue das Bild — wer nur den Kasten
  misst, sieht den Unterschied zwischen cover und contain überhaupt nicht.
- ⚠️ **Gegenprobe in die andere Richtung:** ein hochkantes Foto muss die Kachel weiterhin
  füllen. Sonst hätte der Umbau das häufigste Foto verschlechtert, um das seltenere zu retten.

**620 Prüfungen grün** (von 610). Zwei eigene Fehler unterwegs, beide gefangen:

1. **Die Farbprüfungen hätten grün sein können, ohne etwas zu messen.** Gegenprobe gemacht —
   Farblogik ausgebaut, drei Prüfungen fielen sofort. Erst danach war klar, dass sie greifen.
2. **`getComputedStyle` ist eine lebende Ansicht.** Die Werte wurden erst nach `el.remove()`
   gelesen — dort steht dann nichts mehr. Die Prüfung meldete „objectFit ist leer", während die
   Geometrie daneben bewies, dass es wirkt: ein Fehlschlag aus dem falschen Grund.

## 13.08.2026 (v48) — Die Benachrichtigung nennt den App-Namen nicht zweimal

Karls Meldung, direkt nach dem ersten echten Push: am iPhone standen drei Zeilen —

```
angel-log
from angel-log
Neue Antwort auf deine Meldung.
```

*„from angel-log weg bitte."*

**Die erste Zeile setzt iOS selbst davor** — das ist der Name der Verknüpfung auf dem
Home-Bildschirm, den schreibt die App nicht. **Die zweite war unser Titel.**
`showNotification('Angel-Log', { body: 'Neue Antwort …' })` hat den Namen ein zweites Mal
hingeschrieben, direkt unter den, der ohnehin schon dastand.

➡️ **Jetzt trägt der Titel den Satz, einen Rumpf gibt es nicht mehr.** Eine Zeile Inhalt statt
zweimal derselbe Name.

⚠️ Auch auf Android und am PC ist das die bessere Fassung: dort steht der Titel groß und der
Rumpf klein darunter — „Angel-Log / Neue Antwort" hätte die einzige echte Auskunft ins
Kleingedruckte gesetzt.

⚠️ **Die neue Prüfung fiel zuerst am behobenen Fehler.** Sie suchte im Quelltext nach
`showNotification('…'` und fand den alten Aufruf **im Kommentar daneben**, der erklärt, warum er
weg ist — dieselbe Falle wie am 11. und 12.08., diesmal andersherum: nicht fälschlich grün,
sondern fälschlich rot. Sie nimmt jetzt erst die Kommentare heraus. Gegenprobe gemacht: alte
Fassung zurückgespielt → sie fällt.

⚠️ **Der kleine `angel-log` in der ersten Zeile ist eine alte Verknüpfung**, kein Fehler in der
App: das Manifest heißt seit jeher `Angel-Log`. iOS merkt sich den Namen beim **Anlegen** der
Verknüpfung — dieselbe Sache wie beim App-Symbol (steht seit dem 08.08. als offener Punkt).
Alte Verknüpfung löschen, Seite in Safari öffnen, Teilen → „Zum Home-Bildschirm".

**610 Prüfungen grün** (von 609).

## 13.08.2026 (v47) — 🔔 Benachrichtigung, wenn dein Ticket beantwortet wurde

Karls Ansage: *„Ja mit pushbenachrichtigung, nur von wegen neue antwort auf dein ticket, ganz
einfach."*

In den Einstellungen, direkt beim Postfach: **🔔 Bei Antwort benachrichtigen.**

### Der Weg, von hinten

Karl antwortet in Discord → der Bot trägt die Antwort ein → **der Bot** schickt einen Anstoß an
alle Geräte, die dieser Melder angemeldet hat → der Service Worker zeigt „Neue Antwort auf deine
Meldung."

⚠️ **Verschickt wird ohne Nutzlast**, der Text steht fest im Service Worker. Zwei Gründe: der
Ticket-Text ginge sonst durch die Server von Apple bzw. Google — er enthält, was jemand an der App
auszusetzen hat — und eine Nutzlast müsste je Empfänger verschlüsselt werden (aes128gcm, ECDH).
Ohne sie genügt die VAPID-Signatur, und das ist deutlich weniger, was schiefgehen kann.

⚠️ **Verschickt wird vom Bot, nicht von der Datenbank.** Die Anfrage muss mit dem privaten
VAPID-Schlüssel signiert sein, und der gehört nirgends hin, wo App oder RLS ihn sehen könnten.
Der Preis, ehrlich benannt: **läuft der Bot nicht, geht keine Benachrichtigung raus.** Genau
deshalb startet er seit heute von selbst.

⚠️ **Am iPhone geht das nur mit Verknüpfung auf dem Home-Bildschirm** (ab iOS 16.4). In Safari
selbst gibt es kein `PushManager`. Die App sagt das an der Stelle, statt einen Knopf zu zeigen,
der nie etwas tut.

⚠️ **Die Erlaubnis wird nur auf Tippen erfragt.** Ein Dialog beim Start ist das, was man wegtippt
— und ein einmal abgelehnter lässt sich nicht erneut stellen.

⚠️ **404 und 410 vom Push-Dienst sind kein Fehler, sondern eine Auskunft:** dieses Gerät gibt es
nicht mehr. Die Zeile wird dann gelöscht, sonst sammelt die Tabelle tote Adressen.

⚠️ **Schlägt das Speichern in der Datenbank fehl, wird die Anmeldung im Gerät wieder aufgelöst.**
Sonst stünde der Schalter auf „an", während niemand weiß, wohin gesendet werden soll.

### Geprüft wird, was hier prüfbar ist

Der Versand selbst läuft im Bot und braucht einen echten Push-Dienst. Geprüft wird die App-Seite:
dass der öffentliche Schlüssel ein gültiger P-256-Punkt ist (65 Byte, führendes `0x04` — sonst
weist `subscribe()` ihn erst am Gerät ab, wo es niemand mehr sieht), dass die base64url-Umrechnung
stimmt, dass der Schalter ohne Konto nichts behauptet, und dass der Service Worker **bei jedem**
Push etwas anzeigt — wer das nicht tut, wird von den Browsern von der Zustellung ausgeschlossen.

🔒 **Und eine Prüfung sucht im Quelltext nach einem privaten Schlüssel.** Ein privater
VAPID-Schlüssel wäre für jeden lesbar, der die Seite öffnet, und wer ihn hat, kann im Namen dieser
App an jedes angemeldete Gerät senden.

**609 Prüfungen grün** (von 603).

### ➡️ Zwei Schritte, die bei Karl liegen

1. **`supabase.sql` ausführen** — Abschnitt 7 legt die Tabelle `angel_push` an. Ohne sie meldet
   der Bot beim Senden `404`.
2. In der App **einmal einschalten** (Einstellungen → 🔔), dann eine Meldung abschicken und in
   Discord antworten.

## 13.08.2026 (v46) — Sortieren, ein Ausweg aus der gelben Leiste, Logo zurück

### 🔤 Filter für die Suche

Karls Ansage: *„Filter für suchfunktion für datum von alt bis jung und anders herum und fische
a-z und gewicht."* Ein Auswahlfeld neben der Suche: **Neueste / Älteste / Fischart A–Z /
Schwerste / Längste zuerst.** Die Wahl bleibt gespeichert.

⚠️ **Bewusst ein Auswahlfeld und keine Filterzeile.** Es geht um die Reihenfolge, nicht um eine
zweite Auswahl neben der Suche — zwei Bedienelemente, die beide die Liste kürzen, verwechselt man
sofort.

⚠️ **`localeCompare` statt `<`:** sonst landet „Äsche" hinter „Zander", weil Umlaute in der
Zeichentabelle hinter Z stehen. Bei deutschen Fischnamen ist das kein Randfall.

⚠️ **Fänge ohne Gewicht stehen hinten, nicht vorn.** Mit 0 statt „fehlt" lägen genau die Fänge,
die zur Frage nichts sagen, mitten in der Liste.

⚠️ **Sortiert wird eine Kopie.** `state.catches` ist die Reihenfolge, in der die App überall sonst
rechnet — unter anderem sucht die Wetterkarte darin den jüngsten Fang mit Koordinaten. Sie
umzudrehen, weil jemand nach Gewicht sortiert, wäre ein Nebeneffekt an ganz anderer Stelle.

### 🟡 Ein Ausweg aus der gelben Leiste

Karls Ansage: *„eine info wenn man auf den fang klickt für entwurf oder nur auf diesem gerät, was
man tun muss damit das weggeht."*

**Ein Warnschild ohne Ausweg ist die schlechtere Hälfte einer Warnung.** In der Liste stand „nur
hier" — und nirgends, was zu tun ist. Wer das liest, kann nur raten, ob er etwas falsch gemacht
hat. Im Fang steht jetzt eine Karte „Woran es noch hängt": beim Entwurf, wie er fertig wird; beim
ungesicherten Fang, dass er von selbst hochgeht — mit einem Knopf, der es sofort tut.

### 🖼 Das Logo ist auf dem Ladebildschirm zurück

Karls Ansage: *„Ich brauche doch wieder das Logo auf dem Ladescreen … aber mach das mehr oben."*
Am 08.08. war es auf seine Ansage hin verschwunden — das ist kein Widerspruch, sondern ein Blick
auf das fertige Ergebnis.

⚠️ **Der Verlauf musste oben mit zurück** (0,12 → 0,45). Seit dem 08.08. war der obere Rand fast
durchsichtig, weil dort nichts stand; weiße Schrift auf hellem Wasser ist sonst schlicht weg. Die
Bildmitte bleibt frei.

**603 Prüfungen grün** (von 590).

## 13.08.2026 (v45) — 🔴 Ein Fang ging bei jedem Abgleich neu hoch

### Karls Meldung

*„habe gerade einen auf dem handy bei dem steht nur hier dran, der ist aber auf meinem pc, und
wenn ich auf jetzt abgleichen gehe steht jedes mal dran ein fang geht hoch, aber das tag
verschwindet nicht."*

**Der Befund war echt, und es war eine Schleife ohne Ende — mit Fotos, bei jedem Antippen.**

`cloudMerken()` schreibt den Vermerk „diese Fassung liegt oben" in den **Speicher**
(IndexedDB). `hochladen()` ging aber die Liste im **Arbeitsspeicher** durch — und neu gelesen
wurde nur, wenn beim Abgleich auch etwas *heruntergekommen* war. Nach einem reinen Hochladen also
nie. Damit trug das Objekt im Arbeitsspeicher weiterhin kein `cloud`, der nächste Lauf hielt
denselben Fang für ungesichert, und das Schild „nur hier" hing an derselben veralteten Fassung.

Zwei Quellen für dieselbe Wahrheit, und die ältere hat entschieden. Behoben an beiden Enden:

- **`hochladen()` liest jetzt aus dem Speicher.** `herunterladen()` und `cloudMerken()` tun das
  längst, mit genau dieser Begründung — diese Stelle war die letzte, die es nicht tat.
- **Aufgefrischt wird nach `rauf || runter`**, nicht nur nach `runter`. Neuzeichnen allein hätte
  nicht gereicht: es hätte die veraltete Fassung neu gezeichnet.

### ⚠️ Und der Prüfrahmen war hier grün aus dem falschen Grund

Es gab längst eine Prüfung *„und geht danach nicht ein zweites Mal hoch"* — sie war grün, während
der Fehler auf Karls Handy lief. Grund: der Testspeicher gab **dieselben Objekte** zurück, die
auch in `state.catches` lagen (`[...fakeDB.values()]`). Jede Änderung im „Speicher" war damit
sofort auch im Arbeitsspeicher zu sehen. IndexedDB verhält sich nicht so: was dort herauskommt,
ist frisch aufgebaut.

**Der Testspeicher gibt jetzt Kopien zurück.** Damit fiel die bestehende Prüfung sofort — der
Fehler war reproduziert, bevor eine Zeile Anwendungscode angefasst wurde. Ein Rahmen, der
großzügiger ist als die Wirklichkeit, prüft nichts.

Drei neue Prüfungen dazu, darunter eine, die Karls Fall wörtlich nachstellt (kein Auffrischen
zwischen zwei Läufen). Gegenprobe gemacht: Fix zurückgenommen → beide fallen.

### 📷 Hochkant-Fotos: die Kachel ist jetzt selbst hochkant

Karls Meldung: *„auf dem handy machen hochkant fotos gerade probleme, das sieht sehr komisch aus,
kriegen wir das irgendwie schöner hin, vielleicht sogar den text über dem foto."*

Er hat recht, und der Grund ist nicht Geschmack: die Kachel war quer (4:3), ein Handyfoto ist
hochkant — `object-fit:cover` schnitt oben und unten je ein Viertel weg, und **dort steht der
Fisch**.

➡️ Die Kachel ist jetzt **3:4**, das Foto füllt sie ganz, der Text liegt darauf (Karls eigener
Vorschlag). Beschnitten wird jetzt das Querformat statt des Hochformats — der bessere Tausch, weil
fast jedes Foto hier vom Handy kommt. Ohne Foto steht der Text auf der Karte selbst, ohne
Abdunklung; sonst läge auf den hellen Paletten ein grauer Streifen ohne Anlass.

### 🟡 „Entwurf" und „nur hier" stehen jetzt auf der gelben Leiste

Karls Ansage: *„kannst du die oben sozusagen auf die gelbe linie machen wenn sie da sind."*
Vorher war die gelbe Linie ein Streifen **links ohne Text**, und die Schilder standen unten in der
Kachel — zwei Dinge, die dasselbe sagten. Jetzt trägt die Linie selbst die Beschriftung, oben,
und nur wenn es etwas zu sagen gibt.

**590 Prüfungen grün** (von 583). Kachelform und Leistenposition werden **gemessen**, nicht im
CSS-Text nachgeschlagen — inklusive der Lehre, dass ein ausgeblendeter Abschnitt 0×0 groß ist.

## 13.08.2026 (v44) — Home: Angelzeit, Wetter am Wasser und eine Fangprognose

Karls Ansage: *„Leiste unten neue anordnung: als erstes soll jetzt ein home button kommen wo die
angelzeit steht und vorraussage für wetter (alles was in der statistik auch vorkommt)
fangprognose auch."*

Vier Kacheln statt drei, **Home steht vorn**, und die App öffnet dort. Die Angelzeit ist
umgezogen, sie steht nicht doppelt — sie gehörte ohnehin nie zur Fangliste, man startet sie,
bevor der erste Fang existiert.

### 🌤 Wetter am Wasser

Jetzt-Werte und die nächsten 24 Stunden: Wetterlage, Lufttemperatur, Luftdruck **mit Tendenz**,
Wind, Bewölkung, Regen, Mondphase, Sonnenauf- und -untergang. Das ist Karls Klammer („alles was
in der statistik auch vorkommt") wörtlich genommen.

**Der Ort kommt vom zuletzt erfassten Fang mit Koordinaten** — nicht aus einer GPS-Abfrage beim
Öffnen. Ein Standortdialog, den niemand ausgelöst hat, ist das Erste, was man wegtippt; danach
stünde die Karte für immer leer. Von Hand setzen geht über den 📍-Knopf.

⚠️ **Die Vorhersage wird gespeichert.** Am Wasser ist oft kein Netz — lieber die Werte von heute
früh mit sichtbarem Zeitstempel („Stand …", und ab 30 Minuten „nicht mehr taufrisch") als eine
leere Karte.

⚠️ **`dirLabel(null)` liefert „N", nicht nichts** — `null % 360` ist 0. Ohne die Abfrage hätte
bei fehlender Windrichtung eine erfundene Himmelsrichtung dagestanden, ununterscheidbar von einer
echten. Eigene Prüfung dafür.

### 🎣 Die Fangprognose — und was sie ausdrücklich nicht ist

Sie rechnet **ausschließlich mit Karls eigenen Fängen**. Keine Beißformel, keine Solunar-Tabelle,
keine geliehene Faustregel. Sie fragt eine einzige Sache: *wie ähnlich sind die vorhergesagten
Bedingungen denen, unter denen dieser Angler bisher gefangen hat?*

Verglichen wird an sechs Maßen, alle sechs stehen auch in der Auswertung auf der X-Achse:
**Uhrzeit** (±1 h Fenster — wer um 5:50 gefangen hat, hat nicht „um 5" gefangen), **Tageszeit,
Wetter, Mondphase, Luftdruck** (5-hPa-Stufen), **Lufttemperatur** (2-°C-Stufen). Ausgegeben wird
für heute und morgen das beste zusammenhängende **Drei-Stunden-Fenster**, dazu eine von drei
Stufen und die zwei stärksten Gründe.

⚠️ **Wassertemperatur, Tiefe und Trübung fehlen bewusst** — dafür gibt es keine Vorhersage. Die
Pegel der WSV melden Messwerte, keine Prognose, und die Trübung trägt Karl von Hand ein. Ein
geschätzter Wert wäre eine erfundene Zahl in einer Rechnung, die sonst nur mit echten arbeitet.

⚠️ **Drei Stufen, keine Prozentzahl.** „73 %" liest sich wie eine Messung und wäre keine.

⚠️ **Unter zehn Fängen wird gar nichts gerechnet.** Eine Prognose aus vier Fängen ist kein
ungenaues Ergebnis, sondern gar keins — und sie sähe genauso aus wie eine aus vierhundert. Statt
einer Stufe steht dann da, wie weit es noch ist („Erst 4 von 10 Fängen sind eingetragen").

⚠️ **Und der wichtigste Satz steht in der Karte selbst: das ist keine Beißvorhersage.** Die App
zählt nur Fänge, keine Ansitze ohne Fang — der Nenner fehlt. Wer meistens samstags früh losfährt,
bekommt samstags früh die besten Werte, weil er dann da war. Eine eigene Prüfung wacht darüber,
dass dieser Satz nicht verschwindet.

### Nebenbei gefunden und behoben

⚠️ **Der Prüfrahmen kannte zusammengesetzte Wörterbuch-Schlüssel nicht.** Lange Sätze stehen als
`['a ' + 'b']: '…'` da; die Prüfung las nur `'a':`-Zeilen und meldete fünf Übersetzungen als
fehlend, die zwei Zeilen weiter oben standen. Jetzt liest sie beides.

⚠️ **Ein Syntaxfehler in einem Wörterbuch-Schlüssel reißt den ganzen Skriptblock mit.**
`'a' + 'b': 'c'` ist ungültig — die App meldete daraufhin `gateZeigen is not defined`, 3000 Zeilen
vom eigentlichen Fehler entfernt.

⚠️ **Vier Kacheln passen auf 320 px nur mit 10 px Schrift und `min-width:0`.** Eine Flex-Kachel
ist sonst mindestens so breit wie ihr Inhalt, und „Einstellungen" hätte die Leiste seitlich aus
dem Bild geschoben.

**583 Prüfungen grün** (von 568). Gegenprobe gemacht: die Prognose-Rechnung flachgelegt (jedes Maß
liefert 0,5) → die beiden Prüfungen, die den Unterschied messen, fallen.

## 13.08.2026 (v43) — Die Fangliste zeigt weniger und passt zu zweit nebeneinander

Karls Ansage: *„Bei der Suche will ich weniger Infos direkt sehen erst wenn ich draufclicke will
ich mehr sehen. bitte zeig nur Bild Fischname länge gewicht datum ort und mach die kacheln dann
auch kleiner nur wenns geht sodas 2 nebeneinander möglich wären."*

Weggefallen sind damit **Tageszeit, Wetter, Köder, Köderfarbe, Luftdruck und Wind** — die stehen
alle im Fang selbst, einen Tipper entfernt. Geblieben: Bild, Fischart, Maße, Tag, Gewässer.

⚠️ **Die Kachel ist dafür hochkant geworden, nicht nur kleiner.** Eine Zeile mit 56-px-Bild links
und Text rechts hat auf 320 px Bildschirmbreite rund 130 px je Kachel für den Text — dort passt
kein Fischname neben ein Bild. Hochkant bekommt das Bild die volle Kachelbreite und der Text
darunter auch.

⚠️ **Zwei Schilder bleiben, und das ist kein Übergehen der Ansage.** „Entwurf" und „nur hier"
sind keine Fangdaten, sondern **Zustände der App**: das eine sagt, dass der Eintrag halb ist, das
andere, dass er nirgendwo sonst liegt. Das zweite ist am 08.08. gebaut worden, nachdem zwei Fänge
des Kollegen verloren waren — es aus der Liste zu nehmen hieße, genau die Warnung abzuschalten,
die der Anlass war. Beide sind auf Kachelgröße geschrumpft, „nur auf diesem Gerät" heißt jetzt
**„nur hier"**.

⚠️ **Die Uhrzeit ist aus der Kachel raus**, das Datum nicht. „12.08.2026 · 10:00" stünde auf 130 px
allein über die ganze Zeile und schöbe das Gewässer heraus.

⚠️ **Weniger anzeigen heißt nicht weniger finden.** Gesucht wird weiter über Köder, Farbe, Wetter,
Mondphase und Notiz — die Suchleiste bietet den Köder ausdrücklich an. Eine eigene Prüfung wacht
darüber.

Nebenbei: Fischart und Gewässer laufen in der Kachel jetzt durch `esc()`. Ein offener Punkt aus
der Sicherheitsdurchsicht vom 12.08., an dieser Stelle mit erledigt.

**Prüfungen:** die Geometrie wird im 320-px-Fenster **gemessen** (stehen Kachel 1 und 2 in
derselben Zeile, Kachel 3 eine tiefer, ragt nichts heraus) — nicht im CSS-Text nachgeschlagen.
Gegenprobe gemacht: Raster ausgehängt → sie fällt. **568 grün** (von 560).

## 13.08.2026 (v42) — Antworten kommen an, und die Auswertung erklärt sich

### 🐞 Karls Meldung: Ticket beantwortet, am Handy kam nichts an

**Der Befund war echt.** Die rote Zahl hängt an `postfachHolen()`, das hängt an `syncJetzt()` —
und ausgelöst wurde ein Abgleich bisher nur beim **Start**, beim Speichern eines Fangs, beim
Wiederkommen des Netzes und von Hand. Eine PWA am iPhone wird aber fast nie gestartet: man holt
sie aus dem App-Switcher zurück, und dabei lief kein einziger Abgleich. Wer die App offen liegen
lässt, während die Antwort geschrieben wird, sah sie bis zum nächsten Neustart nicht.

Zurück in die App löst jetzt einen stillen Abgleich aus — **gedrosselt auf einmal je Minute**.
Ohne die Drossel liefe am iPhone bei jedem Blick in die App eine volle Übertragung, über
Mobilfunk, mitten im Angeln.

⚠️ **Das ist keine Push-Nachricht.** Bei geschlossener App zeigt das Handy weiterhin nichts an.
Dafür bräuchte es Web Push mit Berechtigung, Push-Dienst und einem Server, der sendet — ein
eigener Bau und keine stille Zugabe.

⚠️ **Die Prüfung dazu fiel zuerst aus dem falschen Grund.** Als synchrones `t()` geschrieben lief
sie, bevor `init()` den Zuhörer überhaupt angemeldet hatte — sie maß den Zeitpunkt, nicht den
Code. Jetzt wartet sie darauf. Gegenprobe gemacht: Aufruf entfernt → sie fällt.
Eine Prüfung für `document.hidden` gibt es bewusst **nicht** — sie käme erst nach der
Registrierung dran, und dann steht die Drossel; sie wäre grün, ohne je etwas gemessen zu haben.

### ⓘ Ein Info-Zeichen am Baukasten der Auswertung

Karls Ansage: *„ein kleines info symbol wo es noch einmal erklärt wird wie das genau funktioniert
wozu das gut ist."* Klappt neben dem Baukasten auf, statt ein Fenster zu öffnen — man liest es,
während man den Baukasten bedient, nicht statt seiner.

Darin: wozu eine Auswertung gut ist, die vier Schritte (Zählen / Über / Aufteilen / Gewässer),
und wie man sie speichert.

⚠️ **Der wichtigste Absatz ist der letzte, und er sagt, was dort *nicht* steht:** wie gut es
beißt. Gezählt werden nur Fänge — **Ansitze ohne Fang trägt die App nicht ein**. Ein hoher Punkt
heißt „so oft hast du hier gefangen", nicht „hier fängst du am besten". Wer meistens samstags
morgens loszieht, hat zwangsläufig samstagmorgens seinen besten Wert. Eine eigene Prüfung wacht
darüber, dass dieser Satz beim nächsten Kürzen nicht als Erstes verschwindet.

⚠️ **Zurückgenommen während des Bauens:** eine CSS-Regel `.iconbtn svg{width:20px}` hätte das ⓘ
sauber gemacht — und dabei **jeden bestehenden Icon-Knopf mit verkleinert**, vom Abbrechen-Kreuz
bis zum Zurück-Pfeil. Ohne Größenangabe füllt ein `svg` mit viewBox seinen Kasten.

**560 Prüfungen grün** (von 552).

## 12.08.2026 (8) — Die Einführung führt jetzt wirklich durch die App

Karls Liste, Punkt für Punkt abgearbeitet.

### 🐞 Zuerst ein echter Fehler: die rote 0 am Postfach

Am Postfach klebte eine **rote 0**, obwohl nichts ungelesen war. Ursache war eine
Reihenfolge im CSS: `.badge[hidden]{display:none}` stand **vor** `.badge.inline{…display:
inline-block}`. Beide sind gleich stark, und bei Gleichstand gewinnt die spätere Regel — das
Verstecken wurde also wieder aufgehoben. Am Zahnrad fiel es nicht auf, das trägt kein
`.inline`. Die Regel steht jetzt hinten.

### Die Einführung

| Karls Ansage | Umgesetzt |
|---|---|
| „ich will keine punkte, ich brauche eine progress leiste" | Balken + „3 / 7" |
| „überspringen soll man das nicht" | Knopf ist weg |
| „dein fangbuch die beschreibung ist schlecht" | neu geschrieben, sagt konkret, was man tut |
| „auf welchen fisch man es abgesehen hat kann weg" | Karte raus |
| „in der einführung steht immer fischen, es ist angeln" | Spinnangeln, Fliegenangeln |
| „schreib was in die richtung viele updates und aktiver support" | neue Schluss-Karte |

⚠️ **Ohne „Überspringen" wird die Länge zur Zusage.** Sieben Schritte, davon zwei mit einer
Frage — wer nicht raus kann, darf nicht lange festgehalten werden.

### 🔦 Der große Punkt: der erste Fang wird geführt

Karls Ansage: *„ich will das einmal ein fang erstellt werden muss mit hilfe, am besten mit so
einer umkreisung, und der restliche teil der app ist abgedunkelt und nicht antippbar."*

Die Karte „Das Drumherum kommt von allein" **behauptet** es nicht mehr, sie **zeigt** es: der
Knopf heißt „Ersten Fang eintragen" und schaltet ins Formular. Dort läuft eine Führung in fünf
Schritten — Fischart, Maße, Standort, Bedingungen, Speichern —, jeweils mit Ring um das
gemeinte Element und abgedunkeltem Rest.

⚠️ **Gebaut mit vier Balken um das Loch herum, nicht mit einem ausgestanzten Rechteck.** Ein
`box-shadow: 0 0 0 9999px` wäre kürzer gewesen, **fängt aber keine Tipper ab** — und genau das
Abfangen ist der Zweck. Die vier Balken sind antippbar und schlucken den Tipp, der Ring selbst
ist durchlässig.

⚠️ **Der gefährlichste Teil ist nicht das Abdunkeln, sondern das Wiederherauskommen.** Eine
Führung, die hängenbleibt, sperrt die App genauso zu wie ein Ladebildschirm, der nicht weggeht.
Es gibt deshalb **vier voneinander unabhängige Ausgänge**: durchklicken, „Führung beenden",
Speichern — und ein Schritt, dessen Element fehlt, wird übersprungen statt zu warten.

⚠️ **Nach der Führung läuft die Einführung weiter**, statt zu enden. Hinter ihr stehen noch drei
Karten; ohne das fielen sie unter den Tisch, weil die Führung mittendrin abzweigt.

⚠️ **Sie zeichnet sofort und danach noch einmal.** Mit nur dem Wecker lag 60 ms lang ein
dunkler Schirm **ohne Text** über der App — kurz, aber ausgerechnet beim ersten Eindruck.

### Prüfungen

**552 grün** (von 539). Die wichtigsten sind nicht „sie geht an", sondern die vier Ausgänge.
Gegengeprobt: sperrt man einen zu, fällt genau die Prüfung, die ihn bewacht — und die anderen
drei bleiben grün, weil sie wirklich unabhängig sind.

Die alte Prüfung „sie lässt sich überspringen" ist **umgedreht** statt gelöscht: der Knopf soll
nachweislich weg sein, sonst käme er beim nächsten Umbau unbemerkt zurück.

## 12.08.2026 (7) — Zu breit am Handy, und „Größter" ist weg

Karls Meldung: *„die website ist zu breit auf dem handy, pack mal größter fisch weg auf der
liste page."*

**Beides erledigt — aber die Ursache war nicht die Pille.**

Die Zeile mit den Pillen über der Liste (`0 Fänge`, `3 Gewässer`, `Größter: …`, `4 Entwürfe`,
Cloud-Hinweis) ist ein Flex-Kasten **ohne Umbruch**, und jede Pille trägt `white-space:nowrap`.
Mit echten Fängen wird sie länger als der Bildschirm und schiebt die ganze Seite seitlich
heraus.

- **Die Pille „Größter: 87 cm Regenbogenforelle" ist weg** (Karls Ansage). Sie war die längste
  der Reihe — die größte Zahl steht ohnehin in der Auswertung, wo man sie sucht.
- ⚠️ **Der eigentliche Flick ist `flex-wrap:wrap`.** Eine Pille zu entfernen behebt den Fall,
  der Umbruch behebt die Ursache: sonst schiebt die nächste lange Pille die Zeile genauso wieder
  heraus. Gemessen ohne Umbruch: **444 px auf einem 320-px-Bildschirm.**

### Prüfungen

**539 grün.** Neu sind drei, die auf **320, 360 und 390 px** durch alle fünf Seiten gehen und
jedes Element melden, das über den Rand ragt — **mit Namen**, nicht nur „zu breit".

⚠️ **Es gab schon Breiten-Prüfungen, aber nur für die Statistik.** Die Listen-Seite hatte keine,
und genau dort ist es aufgefallen. Eine Prüfung, die nur die halbe App abdeckt, sagt über den
Rest nichts — und das sieht von außen aus wie grün.

### ⚠️ Zwei Fehlversuche auf dem Weg zu dieser Prüfung, beide lehrreich

1. **Erste Fassung: leere App.** Auf allen drei Breiten grün, während Karl das Gegenteil sah.
   Eine Breiten-Prüfung ohne Inhalt prüft die Breite von nichts.
2. **Zweite Fassung: Inhalt vor `go()` gesetzt.** `go('log')` zeichnet die Pillen neu und hat
   die langen Texte sofort wieder überschrieben — die Prüfung maß erneut den leeren Zustand
   und blieb **auch dann grün, wenn man den Umbruch wieder herausnahm.**

Beides ist nur aufgefallen, **weil die Gegenprobe gemacht wurde**: Fix herausnehmen, Lauf muss
fallen. Er fiel nicht. Eine Prüfung, die den Fehler nicht fängt, ist keine — dieselbe Lehre wie
am 11.08., diesmal zweimal hintereinander.

## 12.08.2026 (6) — Konto und Abgleich stehen jetzt ganz unten

Karls Ansage: *„der ganze sync konto löschen kram bitte nach ganz unten."*

Der Konto-Block stand als **Drittes von oben**, direkt unter der Farbpalette. Das passte nicht
dazu, wie die Einstellungen benutzt werden: Sprache und Palette stellt man **einmal** ein, den
Abgleich schaut man an, **wenn etwas klemmt** — und „Konto löschen" hoffentlich **nie**.

Neue Reihenfolge: Sprache · Farbpalette · Hilfe & Fehler melden · Datenschutz · **Konto & Sync**

⚠️ **Der eigentliche Grund ist der Löschen-Knopf.** Ein Knopf, der alles löscht, gehört nicht
dorthin, wo man beim Suchen nach etwas anderem vorbeikommt. Ganz unten steht er nur noch vor
dem, der ihn sucht.

### Prüfungen

**536 grün** (von 534). Drei neue: der Konto-Block ist das Letzte auf der Seite, nach dem
Download kommt nur noch er, und er steht nicht mehr vor der Hilfe.

⚠️ Die Prüfung „Download ist das Letzte auf der Seite" von vorhin **stimmte damit nicht mehr**
und ist umgeschrieben — sie war keine zwei Stunden alt. Beim Verschieben wäre sie sonst
gefallen und hätte eine gewollte Änderung wie einen Fehler aussehen lassen.

## 12.08.2026 (5) — Die Einstellungen sind eine Seite, kein Vorhang mehr

Karls Ansage: *„einstellung muss nicht mehr so ein fliegendes fenster sein, das ist jetzt eine
normale seite wie neuer fang auch."*

Folgt direkt aus der Änderung davor: sobald die Einstellungen eine eigene Kachel unten haben,
sind sie ein Ort wie jeder andere — und ein Ort, der über allem schwebt, passt nicht zu einer
Kachel, die neben zwei anderen steht.

### Was ersatzlos weggefallen ist

Der ganze Vorhang-Apparat, rund **140 Zeilen**:

- der dunkle Hintergrund und das von unten einfahrende Blatt
- der **Griff** zum Wegwischen und die komplette Wisch-Erkennung
- das **Schließen-Kreuz** oben und der **„Schließen"-Knopf** unten
- das Wegtippen auf der Rückseite
- die eigene Überschrift „Einstellungen"

⚠️ **Eine Seite schließt man nicht** — man geht auf eine andere Kachel. Und die Überschrift wäre
dieselbe Auskunft zweimal: unten leuchtet ja die Kachel.

⚠️ **Der stillste Gewinn ist der eigene Scrollbereich.** Das Blatt hatte `max-height:86vh` und
scrollte innen; damit gab es zwei Scrollbereiche ineinander. Genau daran hing der heikelste
Teil der Wisch-Erkennung: unterscheiden, ob ein Wisch nach unten das Blatt ziehen oder den
Inhalt scrollen soll. **Die Seite scrollt jetzt wie jede andere**, und das Problem existiert
nicht mehr.

`sheetZu()` bleibt als Einzeiler, weil mehrere Stellen es rufen (Anmelde-Schirm, Konto löschen,
Einführung). Es heißt jetzt schlicht: geh zurück zur Liste.

### Prüfungen

**534 grün — und das sind acht weniger als vorher (542).**

⚠️ **Die Zahl ist gesunken, weil rund 100 Zeilen Prüfungen entfernt wurden**: alles rund ums
Schließen des Vorhangs (Kreuz, Knopf, Griff, Rückseite, fünf Wisch-Fälle). **Sie sind nicht
gefallen — das Geprüfte gibt es nicht mehr.**

Der Unterschied gehört festgehalten: hätte man sie stattdessen „repariert", prüften sie ein
Verhalten, das niemand mehr will, und stünden dem nächsten Umbau im Weg, statt ihn abzusichern.
Eine sinkende Zahl ist kein schlechtes Zeichen, wenn die App kleiner geworden ist.

Neu dazu, damit vom Vorhang nichts unbemerkt zurückkommt:
- die Einstellungen sind eine Ansicht wie jede andere (Kachel tauscht wirklich aus)
- Kopf und Umschalter verschwinden auch dort
- **vom Vorhang ist nichts übriggeblieben** — `#sheet`, `#sheet-griff`, `#btn-close-sheet` und
  `#btn-sheet-zu` existieren nicht mehr

⚠️ Zwei bestehende Prüfungen zur Reihenfolge in den Einstellungen hingen am Behälter
`#sheet .inner`. Eine davon prüfte „Download steht vor dem Schließen-Knopf" — den Knopf gibt es
nicht mehr, gemeint war aber „der Download ist das Letzte". Genau das prüft sie jetzt, ohne
sich an einen Knopf zu hängen.

## 12.08.2026 (4) — Drei Kacheln statt vier

Karls Ansage: *„Als erstes müssen log, karte und statistiken zusammengeworfen werden irgendwie,
dann kommt neuer fang und dann einstellungen."*

```
┌──────────────────────────────┐
│ 🐟 Angel-Log            [8]  │  ← ein Kopf für alle drei
├──────────────────────────────┤
│ [ Liste ][ Karte ][Auswert.] │  ← Umschalter
├──────────────────────────────┤
│  Fänge   Neuer Fang    ⚙️    │  ← nur noch drei Kacheln
└──────────────────────────────┘
```

**Das „irgendwie":** Liste, Karte und Auswertung zeigen alle **denselben Bestand**, nur aus drei
Blickwinkeln. Sie waren nie drei Aufgaben. Deshalb stecken sie jetzt in einem Umschalter unter
dem Kopf, und die untere Leiste beantwortet *„was will ich tun?"* statt *„welche Ansicht?"*.

### Was dabei verschwunden ist, und warum

- **Die Überschriften „Karte" und „Statistiken".** Zusammengelegt wären das drei Überschriften
  für einen Ort — der Umschalter sagt schon, wo man ist.
  ⚠️ Die **Zähler** daneben (`#map-count`, `#stats-pill`) sind **mitgezogen**, nicht gelöscht:
  sie werden aus dem laufenden Betrieb beschrieben. Sichtbar ist immer nur der zur Ansicht
  passende. Wären sie weggefallen, schriebe der Betrieb ins Leere — ohne Fehler, nur ohne
  Wirkung. Eine Prüfung wacht darüber.
- **Das Zahnrad oben rechts.** Zwei Eingänge zu derselben Schublade wären einer zu viel.
  Die **rote Zahl ist mitgewandert** an die Einstellungs-Kachel.

⚠️ **Die Einstellungs-Kachel tauscht die Ansicht nicht aus.** Sie ist eine Schublade über allem,
keine Ansicht: wer sie schließt, steht wieder da, wo er war. Sonst wäre nach jedem Blick in die
Einstellungen die Karte weg.

⚠️ **Die Kachel „Fänge" bleibt an, solange man irgendwo in dieser Gruppe ist** — auch in Karte,
Auswertung und im einzelnen Fang. Sonst leuchtete unten nichts und die Leiste behauptete, man
sei nirgends.

⚠️ **Beinahe-Absturz beim Umbau:** `$('#btn-menu').onclick` blieb stehen, nachdem das Zahnrad
weg war. Das hätte die App **beim Start** über ein `null` fallen lassen — nicht irgendwo im
Betrieb, sondern sofort und vollständig.

### Prüfungen

**542 grün** (von 532). Elf neue rund um den Umbau, darunter: alle drei Ansichten bleiben über
den Umschalter erreichbar, „Fänge" leuchtet auch in Karte und Auswertung, Kopf und Umschalter
verschwinden beim Erfassen, beide Zähler existieren noch und stehen nur zur passenden Ansicht.

⚠️ **Zwei bestehende Prüfungen hingen an `#v-log .head`** und fielen, weil der Kopf
herausgewandert ist — am geprüften Verhalten war nichts falsch. Sie zeigen jetzt auf `#kopf`.

⚠️ **Und eine meiner neuen Prüfungen las die Reihenfolge über `textContent`** — darin steckte
die rote Zahl mit drin, und übersetzt ist die Beschriftung auch noch. Sie prüft jetzt die
Kennung statt der Beschriftung.

## 12.08.2026 (3) — Die Einführung richtet die App jetzt ein

Karls Ansage: *„ich will vor allem, da ich das so aus anderen apps kenne, ein tutorial haben,
damit man gehookt wird von der app — ein tutorial wo man sich einrichtet, es wird abgefragt
wofür man die app braucht, was man damit macht, was man am meisten nutzen wird."*

Aus vier Erklärkarten werden **sieben Schritte: drei davon fragen, vier erklären.**

| | Frage | Was sie ändert |
|---|---|---|
| 🗺️ | Süßwasser, Meer oder beides? | welche **Fischarten** vorgeschlagen werden |
| 🎯 | Spinnfischen, Ansitz, Fliege? (mehrfach) | welche **Köder** oben stehen |
| 🏆 | Zielfische? (mehrfach) | sie stehen beim Eintragen **ganz oben** |

⚠️ **Jede Frage muss etwas ändern, sonst ist es eine Umfrage** — und das merkt der Benutzer
beim ersten Fang, nicht der Prüflauf. Deshalb hängt an jeder eine sichtbare Folge, und die
Zielfisch-Karte baut ihre Auswahl aus der Antwort davor: wer „Meer" gewählt hat, bekommt dort
Dorsch und Hering zur Auswahl und nicht Karpfen.

### 🌊 Dabei kam ein echter Mangel heraus: die App kannte nur Süßwasser

Sie holt seit jeher Wassertemperaturen von der **Meeresoberfläche** und rechnet mit
Küstenpegeln — aber die Vorschlagsliste bestand aus Hecht, Karpfen und Schleie. Wer damit auf
Dorsch ging, bekam eine Liste, in der sein Fisch nicht vorkam.

Neu dazu: **14 Meeresfische** (Dorsch, Hering, Makrele, Meerforelle, Scholle, Flunder, Wittling,
Hornhecht, Seelachs, Kliesche, Steinbutt, Lachs, Knurrhahn, Seeskorpion) und **6 Meeresköder**
(Pilker, Gummimakk, Heringspaternoster, Wattwurm, Seeringelwurm, Buttlöffel), alle mit
englischer Fassung.

⚠️ **Die Liste hat nie behauptet, vollständig zu sein — aber sie hat entschieden, was
naheliegt, und Meeresangeln lag danach nie nahe.**

### Drei Regeln, an die sich die Einrichtung hält

1. ⚠️ **Sie nimmt nichts weg, sie sortiert um.** Wer „Spinnfischen" angibt und dann doch mit
   Wurm ansitzt, findet den Wurm weiter unten in der Liste. Eine Einrichtung, die die App
   beschneidet statt sie einzustellen, wäre schlechter als keine. (Einzige Ausnahme: „Meer"
   blendet die Süßwasserarten aus — sonst stünden 38 Fische in einer Liste, die 12 zeigt.)
2. ⚠️ **Keine Frage ist Pflicht.** „Weiter" ohne Auswahl geht überall, und dann bleibt alles
   wie vorher. Eine Einrichtung, die man nicht überspringen kann, ist eine Hürde vor der App,
   nicht ein Weg hinein.
3. ⚠️ **Ohne Profil ändert sich gar nichts.** Wer die App schon benutzt, verliert durch die
   Einführung nichts, was er kannte. Hart geprüft.

Die Antworten werden **sofort** wirksam, nicht erst am Ende — wer mittendrin abbricht, behält,
was er eingestellt hat. Über *Einstellungen → Kurze Einführung ansehen* lässt sich alles
jederzeit neu setzen.

⚠️ **Das Profil bleibt auf dem Gerät** und geht nicht ins Konto. Es verlässt die App nicht,
also ändert sich am Datenschutztext nichts. Preis: auf einem zweiten Gerät wird es neu gesetzt.

⚠️ **Die Auswahl hängt nicht allein an der Farbe** (Rand + Fettschrift + Haken) — auf den
helleren Paletten wäre ein farbiger Rand sonst kaum zu sehen.

### Prüfungen

**532 grün** (von 520). Zwölf neue, und der Kern ist nicht, dass die Fragen erscheinen, sondern
dass die Antworten wirken: „Meer" bringt Dorsch und lässt Karpfen weg, Zielfische stehen oben,
kein Köder verschwindet, keine Doppelten — und zuletzt die Probe am echten `<datalist>` des
Formulars statt an der Hilfsfunktion.

⚠️ **Diese letzte Prüfung ist erst gefallen, obwohl der Code stimmte:** die Vorschlagsliste
füllt sich absichtlich erst beim Tippen. Sie tippt jetzt, statt auf ein leeres Feld zu schauen.

## 12.08.2026 (2) — Tickets: Sperre, Postfach, Antwort per Discord

Karls Ansage: *„Support zeitlich limitieren … und ich möchte das der user ein feedback bekommt
wenn sich um sein ticket gekümmert wurde … ein beantwortetes ticket soll dann in den
einstellungen auftauchen, man sieht eine rote 1 am einstellungs logo … und dann ist da neben
dem support ein kleines postfach … da kann man dann drauf drücken und sieht alle tickets aus
den letzten 30 tagen."*

Aus einem Melde-Briefkasten wird damit ein Gespräch. Der Weg: App → Datenbank → Discord →
Karls Antwort → Datenbank → App.

### Der Rückweg

Jede Meldung bekommt eine **Nummer** und steht in Discord als „Meldung #12". Karl antwortet
dort mit der **Antworten-Funktion**; der Bot liest die Nummer aus der Nachricht, auf die
geantwortet wurde, und trägt den Text bei genau diesem Ticket ein.

⚠️ **Ohne „Antworten" passiert nichts.** Eine Nachricht, die einfach so im Kanal steht, hat
keinen Bezug zu einem Ticket — und geraten wird nichts. Wer nur mitredet, löst nichts aus.

⚠️ **Der Bot läuft nur, wenn Karls Rechner läuft**, und das ist in Ordnung: er beantwortet
Tickets ohnehin nur am Rechner. Damit „der Bot war aus" trotzdem nichts kostet, **holt er beim
Start die letzten 200 Nachrichten nach**. Aus einem Verlust wird eine Verzögerung.

⚠️ **Eine korrigierte Antwort setzt den Gelesen-Vermerk zurück** — sonst stünde die neue
Fassung im Postfach, ohne dass die rote Zahl noch einmal ruft.

### Das Postfach

Neuer Knopf direkt unter „Fehler melden" — dasselbe Thema von der anderen Seite: dort geht die
Frage raus, hier kommt die Antwort an. Darin alle Tickets der letzten 30 Tage, offene mit ⏳,
beantwortete mit ✅. Die **rote Zahl** steht am Zahnrad und am Postfach, aus derselben Quelle.

⚠️ **Die Antworten werden beim Abgleich geholt, nicht beim Öffnen des Postfachs.** Die rote
Zahl ist die einzige Stelle, an der jemand von einer Antwort erfährt — holte man sie erst beim
Hineinsehen, erschiene sie nur dem, der ohnehin schon nachschaut.

⚠️ **Der Bestand wird lokal gespiegelt**, sonst wäre das Postfach am Wasser leer — genau dort,
wo die App benutzt wird.

⚠️ **Markiert wird vor dem Abhaken.** Würde erst abgehakt und dann gezeichnet, wäre die
Markierung schon weg, bevor man sie sieht.

### Die Sperre — und warum sie nicht ist, was verlangt war

In der App: **60 Sekunden**, mit Countdown im Knopf, genau wie angesagt.

In der Datenbank steht bewusst etwas anderes: **höchstens 5 Meldungen je 10 Minuten**.

⚠️ **Eine 60-Sekunden-Regel auf dem Server wäre eine Falle gewesen.** Eine Meldung liegt erst
im Gerät und geht mit dem nächsten Abgleich raus. Wer ohne Netz zwei schreibt, schickt beim
Wiederverbinden zwei auf einmal — die zweite ist dann zwangsläufig binnen 60 Sekunden nach der
ersten da. Sie wäre abgewiesen worden, bei jedem weiteren Abgleich erneut, **für immer**. Aus
einer Bremse gegen Spam wäre ein Loch geworden, in dem echte Meldungen verschwinden.

⚠️ **Und deshalb geht jede Meldung jetzt einzeln raus statt als Stapel.** In PostgreSQL nimmt
eine abgewiesene Zeile die ganze Anweisung mit — im Stapel wären die Meldungen daneben
mitgefallen, die völlig in Ordnung waren.

⚠️ **Die App-Sperre ist die sichtbare, nicht die wirksame.** Was nur der Browser verbietet,
verbietet niemandem etwas, der den Browser umgeht. Sie ist dafür da, dass man nicht dreimal
drückt, weil nichts passiert.

### 🔴 Nebenbei geschlossen: `@everyone` in einer Fehlermeldung

Gefunden bei Karls Frage nach Angriffsflächen. Der Webhook-Aufruf hatte **kein
`allowed_mentions`**, und Discord löst Erwähnungen im Text standardmäßig auf. In diesen Text
schreibt ein Fremder — jeder, der die App hat. Wer `@everyone` ins Meldefeld tippte, pingte
Karls ganzen Server, so oft er wollte.

Jetzt `{"parse": []}`: @everyone, @here und Rollen stehen als Text da, was sie sein sollen.
⚠️ Der Text selbst bleibt unangetastet — entschärft wird die Wirkung, nicht der Inhalt.

### ➡️ Karl muss `supabase.sql` einmal erneut ausführen

Neue Spalten (`nummer`, `antwort`, `antwort_am`, `gelesen_am`), die Bremse, die
Abhak-Funktion und der `allowed_mentions`-Flick. Der Block ist gefahrlos wiederholbar.

### Prüfungen

**520 grün** (von 509). Neu sind neun fürs Postfach und zwei für die Bremse.

⚠️ **Die wichtigste ist „eine gebremste Meldung bleibt liegen, die davor ist durch"** — genau
das Verschlucken, um das es bei der ganzen Änderung geht.

⚠️ **HTML in Meldung und Antwort wird entschärft**, hier hart geprüft: im Postfach steht Text,
den ein **anderer** geschrieben hat. (In der Fang-Ansicht ist dasselbe nicht entschärft — dort
fast harmlos, weil niemand fremde Fänge sieht. Steht als offener Punkt.)

⚠️ **Eine bestehende Prüfung hing an einem festen Fenster von 2600 Zeichen** und fiel, weil
`syncJetzt` um ein paar Zeilen wuchs — mit „Stelle nicht gefunden", obwohl am geprüften
Verhalten nichts falsch war. Eine Prüfung, die an der Länge einer Funktion hängt, meldet
Wachstum als Fehler. Sie endet jetzt an der nächsten Funktion.

## 12.08.2026 — In der Fang-Ansicht stand „false", wo nichts eingetragen war

Karls Meldung: *„Wenn ich auf einen Fang draufklicke, dann steht bei allem, wo ich nichts
eingegeben habe, `false` dran."*

**Acht Zeilen waren betroffen:** Wassertemperatur, Wassertiefe, Lufttemperatur, Luftdruck,
Bewölkung, Regen davor (24 h), Köder-Größe, Köder-Gewicht.

### Was passiert war

Die Zeilen der Fang-Ansicht entstehen alle über einen Helfer `kv(name, wert)`, der leere Werte
weglässt. Er kannte drei Arten von „leer": `null`, `undefined` und den leeren String.

Die Aufrufer schreiben aber:

```js
kv('Wassertemperatur', c.wasser != null && dec(c.wasser) + ' °C')
```

Ist das Feld leer, ist `c.wasser != null` **falsch**, und damit ist der ganze Ausdruck der
Boolean `false` — keine der drei bekannten Arten von leer. Er wurde also brav angezeigt.

⚠️ **Nicht deutsch-spezifisch**, obwohl es dort aufgefallen ist. Durch die Übersetzung läuft
nur die Beschriftung links, der Wert rechts nie — auf Englisch stand dort dasselbe.

### Behoben

`kv()` filtert `false` jetzt mit weg, **zentral statt an den acht Aufrufern**. Jeder künftige
`!= null &&`-Aufruf stellte sonst dieselbe Falle neu auf; ein anzeigbarer Wert ist nie der
Boolean `false`.

⚠️ **Was hier fast schiefgegangen wäre:** der naheliegende Flick `if (!v) return ''` hätte
`false` ebenfalls weggeräumt — und dabei still die **Null** mitgenommen. 0 °C Wasser ist im
Winter ein echter Messwert, 0 % Bewölkung ein wolkenloser Tag. Ein Flick, der Messwerte
verschluckt, wäre schlimmer gewesen als der Fehler.

### Prüfungen

**509 grün** (von 503). ⚠️ **Die Fang-Ansicht hatte bis heute keine einzige Prüfung** — deshalb
konnte dort acht Zeilen lang „false" stehen, ohne dass etwas gefallen wäre. Gemeldet hat es
Karl, nicht der Prüflauf.

Neu sind sechs, davon drei Gegenproben:
- leere Felder erzeugen kein „false", kein „undefined"/„null"/„NaN", und gar keine Zeile
- gesetzte Werte stehen weiterhin da (alle acht, mit Einheit)
- **0 °C und 0 % überleben** — die Gegenprobe gegen den falschen Flick
- der nachgebaute alte Filter liefert nachweislich noch „false"; fällt diese Prüfung, prüft
  die erste nichts mehr

Gegengeprobt: mit zurückgenommenem Fix fällt die Prüfung und nennt alle acht Zeilen namentlich.

⚠️ Geprüft wird der **sichtbare Text**, nicht der Quelltext der Vorlage. Eine
Quelltext-Prüfung hätte die Falle vom 11.08. wiederholt: sie findet ihren Suchbegriff im
Kommentar daneben und bleibt grün.

## 11.08.2026 (2) — Der Abgleich läuft jetzt hinter dem Ladebildschirm

Karls Ansage direkt danach: *„mach das bitte währenddessen das intro lädt und wenn es länger
dauert soll auch das intro länger dauern."*

**Er hat recht, und der Grund ist die Änderung von eben.** Seit heute holt der Abgleich beim
Start den ganzen Bestand statt nur der Änderungen. Der Ladebildschirm ging bisher **vor** allem
weg, was Zeit kostet — man sah also die Liste einen Moment lang unvollständig, und Fänge
purzelten hinterher hinein. Eine Sekunde länger Foto ist besser als eine Liste, die sich unter
den Augen ändert.

- Der Schirm steht jetzt, **bis der erste Abgleich durch ist**. Untergrenze bleibt 1,8 s.
- Die Prozentzahl bleibt so lange bei **96 %**. Das ist keine neue Regel, sondern erst jetzt
  wörtlich wahr: „die letzten Prozent gehören dem tatsächlichen Fertigwerden" stand seit dem
  08.08. da, nur war das Fertigwerden bis heute eine Sache von Millisekunden.

### ⚠️ Was daran gefährlich ist

**Ein Abgleich kann hängen** — kein Empfang am Wasser, ein Hotspot ohne Anmeldung, ein Server,
der die Verbindung offen lässt statt abzulehnen. Ein Schirm, der darauf wartet, würde die App
**hinter einem Foto sperren**, und zwar genau dort, wo sie gebraucht wird.

Es gibt deshalb eine **Höchstzeit von 6 Sekunden** (`SPLASH_HOECHSTENS`). Sie zählt ab dem
Öffnen der Seite, steht im Kopf der Datei und kennt weder `init()` noch Netz — sie ist die
einzige Zusage hier, die nichts kaputtmachen kann. Das war vorher der „Notausstieg" bei 4,5 s
für den Fall, dass `init()` nie durchläuft; er hat jetzt zwei Aufgaben und heißt danach.

⚠️ **Die Anmeldung ans Wiederkommen der Verbindung steht bewusst *vor* dem Warten.** Hinge sie
dahinter, wäre sie ausgerechnet dann noch nicht da, wenn der erste Abgleich gerade am Netz
hängt — und das Wiederkommen liefe ins Leere.

### Prüfungen

**503 grün** (von 501). Zwei davon fassen den neuen Fall an echtem Verhalten an: `haengt.html`
ist dieselbe App mit einem ersten Abgleich, der **nie** fertig wird. Nach 2,4 s muss der Schirm
noch stehen (sonst wartet er nicht), nach 6,6 s muss er weg sein (sonst sperrt er die App).
**Nur eine der beiden zu prüfen wäre wertlos** — die erste allein beschriebe eine App, die sich
bei schlechtem Netz selbst aussperrt, die zweite allein eine, die Karls Ansage gar nicht umsetzt.

⚠️ **Gegengeprobt, zweimal einzeln.** Höchstzeit auf 60 s: beide Sperr-Prüfungen fallen.
Ladebildschirm wieder nach vorn: beide Warte-Prüfungen fallen.

⚠️ **Und dieselbe Falle wie eine Stunde vorher, zum zweiten Mal:** die Reihenfolge-Prüfung
suchte `splashWeg()` im Quelltext — und fand es im Kommentar direkt darüber („Hier stand
`splashWeg()`"). Sie meldete „Wegnehmen bei 809" und fiel, obwohl alles stimmte. Beide
Quelltext-Prüfungen verlangen jetzt einen echten Aufruf: Zeilenanfang, Semikolon.

## 11.08.2026 — Der letzte Gerätemarker ist weg

Karls Wahl aus meinen zwei Vorschlägen. Keine neue Funktion — **eine Bauart weniger, die
falsch stehen kann.**

### Was hier stand

Beim Herunterladen merkte sich jedes Gerät ein Datum (`angellog-sync`) und fragte den
Server: *„was ist seit dem letzten Mal passiert?"* Danach rückte das Datum vor.

⚠️ **Genau diese Bauart hat in drei Tagen dreimal ein Loch gehabt:**

| | wo | was |
|---|---|---|
| 08.08. | Push-Stand | rückte auf die Uhr statt auf das Verschickte → zwei Fänge fielen durch, für immer |
| 10.08. | Push-Stand | konnte nicht ausdrücken, dass ein Fang von drüben kam → beide Richtungen falsch |
| 09.08. | Herunterlade-Stand | läuft nur vorwärts → verliert ein Gerät seine IndexedDB, kommt nie wieder etwas herunter |

⚠️ **Der Fehler war nie der jeweilige Rechenfehler, sondern die Bauart.** Ein Stand ist eine
**Behauptung** dieses Geräts über den Server, und sie kann falsch sein, ohne dass irgendetwas
auffällt. Der Push-Stand ist am 10.08. abgeschafft worden; das hier war der letzte.

### Was jetzt passiert

Bei jedem Abgleich kommen die **Kennzahlen des ganzen Bestands** (id, updated, geloescht — keine
Fotos), und verglichen wird Fang für Fang. **Nicht mehr behauptet, sondern nachgesehen.**

Der Gewinn steckt weniger im Finden als im **Vergessen**: der Vergleich heilt sich bei jedem
Lauf von selbst. Bricht ein Durchgang mitten im Holen ab, fehlt beim nächsten schlicht wieder
dasselbe und wird wieder geholt. Ein Stand hätte an dieser Stelle vermerkt, er sei fertig.

⚠️ **Was es kostet, ehrlich benannt:** je Abgleich einmal die Kennzahlen statt nur der
Änderungen. Bei 8 Fängen ein paar hundert Byte, bei 1.000 rund 50 KB — weniger als **ein
einziges** der Fotos, die ohnehin durch dieselbe Leitung gehen. Grabsteine zählen mit und
sammeln sich an; sie sind ohne `daten` und `fotos` die kleinsten Zeilen überhaupt.

⚠️ **Ein neues stilles Loch hätte dabei fast aufgemacht.** Der Server gibt je Anfrage höchstens
`max-rows` Zeilen zurück (bei Supabase ab Werk 1.000) und **sagt nicht dazu, dass er gekürzt
hat.** Wer die erste Seite für den ganzen Bestand hält, sieht den Rest nie — dieselbe Blindheit,
nur eine Etage tiefer. Es wird deshalb geblättert, und zwar **über die zuletzt gesehene id, nicht
über `offset`**: mit `offset` verschiebt sich das Fenster, wenn währenddessen eine Zeile
dazukommt, und genau ein Fang rutscht zwischen zwei Seiten hindurch.

### 🚨 Dabei gefunden: „liegt oben" überlebte das Abmelden

**Das war eine echte Lücke, kein Aufräumen.** Bis zum 10.08. hing die Notiz „liegt im Konto" an
einem Stand im localStorage, und den löschte das Abmelden. Seither hängt sie als `cloud` **am
Fang** — und dort hat sie das Abmelden überlebt.

Wer sich abmeldet und ein **zweites Konto** anlegt, hätte ein leeres Konto vor sich, während
jeder Fang von sich behauptet, er liege schon oben: der Abgleich schickt nichts und meldet
**„alles schon aktuell"**. Dasselbe nach *Konto löschen* — dort ist die Zeile nachweislich weg.
Beides löst die Notizen jetzt. Kostet beim nächsten Anmelden einmal das Datenvolumen für alle
Fotos; verlieren kann man dabei nichts.

### Nebenwirkungen

- **„⇄ Abgleich prüfen"** fragt dieselben Kennzahlen ab wie der Abgleich selbst — eine Abfrage
  statt zweier, die dasselbe zählen sollen. ⚠️ Und die eigene hatte denselben stillen Rand: ohne
  Blättern hört sie bei `max-rows` auf. Eine Prüfung, die selbst kürzt, meldet „beide Seiten sind
  gleich", während drüben etwas liegt.
- **„⟲ Alles neu laden"** heißt jetzt „vergisst, was dieses Gerät für gesichert hält" statt
  „setzt beide Stände zurück". Die Herunterlade-Richtung ist bei jedem Abgleich schon
  zurückgesetzt; übrig bleibt die Gegenrichtung. Der Knopf **bleibt** — er ist zwar für ein Loch
  gebaut worden, das es nicht mehr gibt, aber ihn abzuschaffen hieße, auf den nächsten
  unbekannten Fehler wieder blind zu sein.
- ➡️ **`supabase.sql` muss *nicht* erneut ausgeführt werden.** An der Datenbank ändert sich
  nichts. `serverzeit` bleibt stehen: sie steuert nichts mehr, ist aber die einzige Uhr hier, der
  man trauen kann.

### Prüfungen

**501 grün** (von 489). Neu: der Abgleich merkt sich keinen Stand mehr; er fragt nicht mehr nach
`serverzeit`; ein voller Block wird weitergeblättert; geblättert wird über die id, nicht über
`offset`; eine kurze Seite löst keine zweite Anfrage aus; ein Grabstein zählt nicht zum Bestand
im Konto; Abmelden löst die Notizen und die Fänge gehen danach wieder mit hoch.

⚠️ **Gegengeprobt — und die Gegenprobe hat einen Fehler in einer Prüfung gefunden.** Alles wieder
eingebaut: vier Prüfungen fallen wie vorgesehen. Die fünfte, „Abmelden ruft das auch wirklich
auf", blieb **grün, obwohl der Aufruf entfernt war** — sie suchte den Namen im Quelltext, und der
stand im Kommentar direkt daneben. Jetzt muss ein echter Aufruf dastehen (Zeilenanfang,
Semikolon). Danach fällt sie. **Eine Prüfung, die den Fehler nicht fängt, ist keine.**

## 10.08.2026 (5) — Umlaut-Salat, und der Technik-Kasten ist raus

### Die Discord-Nachricht kam als Buchstabensalat an

Karl: *„sie sieht ein bisschen komisch aus, mach doch die komischen Zeichen raus."*
Nachgesehen — die Nachricht stand so im Kanal:

```
ðŸž **Angel-Log â€" neue Fehlermeldung**
FÃ¤nge: 8 Â· ungesichert: 0
```

⚠️ **Das war kein Geschmacksthema, sondern ein Fehler — aber nicht der, den ich zuerst
diagnostiziert habe.** Erste These: der Kopf `Content-Type: application/json` habe keine
Zeichensatz-Angabe, also lese Discord Latin-1. Falsch, und der „Fix" hat alles lahmgelegt
(siehe unten).

**Die echte Ursache stand in Karls Fehlermeldung**, in meinem eigenen Kommentar:

```
CONTEXT: PL/pgSQL function http_post(...)
    /* âš ï¸ ... "FÃ¤nge" ... */
```

Der Salat stand **schon im Quelltext der Funktion in der Datenbank**. Discord hat nur
wiedergegeben, was dort stand. Hereingekommen ist er auf dem Weg in die Zwischenablage:
`Get-Content` ohne `-Encoding UTF8` liest unter Windows PowerShell als Windows-1252, und
damit war jedes deutsche Zeichen zerlegt, **bevor** Karl überhaupt eingefügt hat.

⚠️ **Und der falsche Fix war schlimmer als der Fehler.** `pg_net` prüft den Kopf selbst und
wirft bei allem außer exakt `application/json` eine Ausnahme. Die fliegt in einem Trigger —
**damit fällt die ganze INSERT-Anweisung mit.** Zwanzig Minuten lang nahm die App keine
Meldung mehr an, nicht einmal in die Tabelle. Aus einem kaputten Zustellweg war eine kaputte
Meldefunktion geworden. Beides steht jetzt als Warnung im SQL.

**Merksatz für alles Weitere hier:** eine Ausnahme in einem AFTER-INSERT-Trigger ist kein
Nebenweg, der ausfällt — sie nimmt die Hauptsache mit.

Dazu die Auszeichnung raus (`**fett**`, `> Zitat`, `` `Code` ``, `-# klein`): eine Meldung ist
kein Aushang, und jedes Zeichen, das der Empfänger im Zweifel roh sieht statt gerendert, macht
sie schlechter lesbar. Der Zeitpunkt des letzten Abgleichs steht jetzt als `10.08. 20:44` da
statt als `2026-08-10T18:44:48.343Z`.

### Der „Das geht automatisch mit"-Kasten ist raus

Karls Ansage: *„nimm bei meldungen das: das wird mitgeschickt raus und wenn wir das unbedingt
brauchen dann pack es in die Datenschutzerklärung."*

Er hat recht: der Kasten war länger als das Eingabefeld darüber und bestand zur Hälfte aus
einer User-Agent-Zeile. Wer melden will, dass etwas kaputt ist, bekam zuerst eine Wand aus
Technik.

⚠️ **Die zweite Hälfte seines Satzes ist die wichtigere.** Der Kasten war die einzige Stelle,
an der stand, was mitgeht. Fiele er weg, ohne dass es woanders vollständig steht, würde aus
einer offenen Erhebung eine heimliche. Die Datenschutzerklärung nennt deshalb jetzt **jede
einzelne Angabe** — Fassung, User-Agent, Bildschirmgröße, Sprache, ob vom Home-Bildschirm
gestartet, online/offline, Anzahl Fänge, ungesicherte Fänge, letzter Abgleich.
**Eine Prüfung leitet die Liste aus `umfeldSammeln()` ab**: kommt später ein Feld dazu, das im
Datenschutztext nicht vorkommt, fällt sie. Sonst wächst still mit, was niemand mehr nennt.

### Am Prüfrahmen

⚠️ **Das Zeitbudget stand seit 424 Prüfungen auf 20 Sekunden.** Bei 489 brach der Lauf
**viermal in Folge** ohne Ergebnis ab — auch mit dem Stand von einer Stunde vorher, der noch
grün durchgelaufen war. Genau daran war es zu erkennen: **nicht der Code, die Decke.** Jetzt 45
Sekunden. Virtuelle Zeit kostet keine echte, das Budget also nichts außer Luft nach oben.

Damit ist auch das „sporadische Wackeln" vom 09.08. erklärt — es war nie zufällig, sondern der
Lauf am Rand seiner Grenze.

**493 Prüfungen grün** (von 489).

## 10.08.2026 (4) — Fehlermeldungen kommen an, statt herumzuliegen

Karls Frage: *„wie kann ich die reports empfangen?"* — bis hierher gar nicht. Sie lagen in
der Tabelle und man musste von sich aus nachsehen. **Eine Meldung, von der niemand erfährt,
ist so gut wie keine.**

Jede neue Meldung geht jetzt als **Discord-Nachricht** hinaus — Text als Zitatblock, darunter
Fassung, Bildschirm, Netz, Anzahl Fänge, ungesicherte Fänge, letzter Abgleich und das Gerät.
Gebaut als Auslöser in der Datenbank (`supabase.sql`, Abschnitt 3b), nicht in der App: so
greift er auch bei einer Meldung, die Tage später aus der Warteschlange eines Handys kommt.

⚠️ **`net.http_post` ist asynchron, und das ist der Grund, warum es überhaupt in einem
Trigger stehen darf.** Würde der Versand auf Discord warten, hinge das Abschicken einer
Meldung an der Erreichbarkeit eines fremden Servers — und ausgerechnet die Fehlermeldung wäre
das Erste, was bei Störungen nicht mehr durchkommt.

⚠️ **Die Webhook-Adresse steht nicht im Repo.** Das Repo ist öffentlich; wer die Adresse hat,
kann in den Kanal schreiben. Sie liegt in `angel_konfig` — RLS an, **keine einzige Policy**,
damit kommt nur das Dashboard dran. Ohne Eintrag passiert schlicht nichts. Eine Prüfung wacht
darüber, dass keine Webhook-Adresse in den ausgelieferten Quelltext gerät.

⚠️ **Damit verlässt ein Meldungstext die EU** (Discord Inc., USA). Dieselbe Lage wie beim
Essens-Foto in Gym-Log und dieselbe Regel: **es steht ehrlich in der Datenschutzerklärung
oder es passiert nicht.** Steht jetzt drin, deutsch und englisch, mit der Einschränkung, dass
ohne abgeschickte Meldung nichts auf diesem Weg hinausgeht.

**489 Prüfungen grün** (von 486).

## 10.08.2026 (3) — Entwürfe gehen jetzt mit

Karls Ansage: *„5 entwürfe die sollen bitte auch synchronisiert werden."*

Entwürfe blieben bis heute **absichtlich** lokal — „halbe Sachen bleiben hier". Diese
Begründung ist hinfällig: ein Entwurf ist getippte Arbeit, und getippte Arbeit nur auf
einem Gerät liegen zu lassen war schon bei den Fängen der Fehler.

- Entwürfe gehen mit hoch und kommen auf dem anderen Gerät an — **als Entwurf**, nicht als
  fertiger Fang. Sie zählen weiterhin in keiner Auswertung mit.
- Sie zählen jetzt in **„⇄ Abgleich prüfen"** mit. Vorher stand dort „Entwürfe (bleiben
  absichtlich lokal)"; jetzt „davon Entwürfe (gehen mit)".
  ⚠️ Wären sie weiter ausgenommen, meldete die Prüfung „beide Seiten sind gleich", während
  fünf Entwürfe nur auf einem Gerät liegen — derselbe Fehlalarm, nur mit umgekehrtem
  Vorzeichen.
- Der Cloud-Hinweis zählt sie mit und heißt deshalb **„… Einträge nur auf diesem Gerät"**
  statt „Fänge". Ein halb ausgefüllter Entwurf ist kein Fang.

⚠️ **Gewollte sichtbare Folge:** ein Entwurf, den du am PC halb ausfüllst, taucht auch am
Handy auf. Wer denselben Entwurf auf zwei Geräten anfasst, bekommt die jüngere Fassung —
dieselbe Regel wie bei den Fängen.

**486 Prüfungen grün** (von 484). Drei Prüfungen mussten umgedreht werden, weil sich die
Regel geändert hat; eine vierte hat den Umbau von selbst gefunden („Erster Abgleich schiebt
vorhandene Fänge hoch" erwartete zwei Zeilen, es waren drei).

## 10.08.2026 (2) — Der Anmelde-Schirm

Zwei Ansagen von Karl, beide auf demselben Bildschirm.

- ✅ **Das echte App-Symbol steht jetzt im Anmelde-Schirm.** Dort stand eine gezeichnete
  Fischsilhouette aus der Zeit vor dem eigenen Icon.
  ⚠️ **Es war die letzte Stelle, an der das alte Bild überlebt hatte** — und ausgerechnet
  der erste Bildschirm, den man von der App überhaupt zu sehen bekommt. Am 07.08. ist das
  Symbol überall ausgetauscht worden, am 08.08. kam es zusätzlich in die Kopfzeile; gesucht
  wurde beide Male an den Stellen, die man beim *Benutzen* sieht. Der Anmelde-Schirm kommt
  davor.
- ✅ **Passwort anzeigen** — Auge rechts im Feld, ein Tipp zeigt es, der nächste verbirgt es.
  ⚠️ Die Schreibmarke bleibt stehen, wo sie war: ein Wechsel des Feldtyps setzt sie sonst
  ans Ende, und am Handy schließt ein verlorener Fokus die Tastatur — mitten im Tippen.
  Die Beschriftung wechselt mit („Passwort anzeigen" / „Passwort verbergen"), sonst ist der
  Knopf für alle unbrauchbar, die ihn vorgelesen bekommen.

**484 Prüfungen grün** (von 476). Gegengeprobt: altes Symbol und toter Knopf wieder
eingebaut → genau die vier zuständigen Prüfungen fallen.

## 10.08.2026 — Ein Fang weiß jetzt selbst, ob er im Konto liegt

Karls Meldung: *„wieso habe ich 11 fänge auf meinem pc und nur 5 auf meinem handy?"* und
kurz darauf *„irgendwas funktioniert allgemein in der datenübertragung nicht"*.

**Es waren zwei Fehler und ein Missverständnis, und das Missverständnis war meins.**

### 1. Der Stand für das ganze Gerät ist abgeschafft

Bis heute entschied **ein einziges Datum je Gerät** (`angellog-sync-push`), ob ein Fang schon
im Konto liegt. Das kann die Frage gar nicht beantworten — es kennt nur „später als".

- **Nach oben falsch:** ein gerade **heruntergeladener** Fang trägt die Uhr des *anderen*
  Geräts. Die ist neuer als das letzte Hochladen hier → er wurde als „nur auf diesem Gerät"
  angeschrieben. Genau Karls Beobachtung: *„bei dem einen, der neu ist, steht nur auf diesem
  Gerät dabei. Das stimmt aber nicht. Der ist auch auf meinem Handy."*
- **Nach unten falsch, und das ist die teure Richtung:** steht der Stand einmal zu hoch, wird
  ein älterer Fang **stillschweigend übersprungen** — bei jedem Abgleich, für immer. Das ist
  derselbe Verlust wie am 08.08., nur durch eine andere Tür.
- **Nebenbefund, in der Gegenprobe schwarz auf weiß:** jeder heruntergeladene Fang wurde beim
  nächsten Abgleich **samt Fotos sofort wieder hochgeschoben** (`zurueckgeschoben: ["n"]`).

Jetzt trägt jeder Fang sein eigenes `cloud` — die Fassung, die nachweislich oben angekommen
ist. Gesetzt wird es an genau zwei Stellen: nach erfolgreichem Hochladen und beim
Herunterladen (denn von dort kam der Fang ja).

⚠️ **Der Wächter beim Vermerken ist der Kern, nicht Beiwerk.** Vermerkt wird nur, wenn der
Fang im Speicher noch dieselbe Fassung hat, die verschickt wurde. Wer während des Hochladens
denselben Fang ändert — am Handy im Mobilfunk dauert ein Foto zehn Sekunden bis eine Minute —,
bekommt kein `cloud` und geht in der nächsten Runde mit. Damit ist der Verlust vom 08.08.
durch die **Bauweise** verhindert und nicht mehr durch ein sorgfältig gesetztes Datum.

⚠️ **Die einmalige Reparatur vom 08.08. ist ersatzlos weg** — sie wird überflüssig, nicht
ersetzt. Ein Fang ohne `cloud` gilt als ungesichert und geht beim nächsten Abgleich mit hoch.
Das kostet einmal je Gerät das Datenvolumen für alle Fotos und heilt dabei jeden Bestand, der
hinter einem zu hohen Stand feststeckte.

### 2. Zwei Wahrheiten auf einem Bildschirm

Karl zählte **elf Fänge** am PC. Es waren **acht** — plus vier Entwürfe. Die Liste zeigt
Entwürfe mit an, die Zählung darüber ließ sie weg. **Gezählt wird, was man sieht.**

Steht ein Entwurf in der Liste, steht seine Zahl jetzt auch oben (`4 Entwürfe`, gelb, neben
`8 Fänge`). Eine Prüfung hält fest, dass Fänge plus Entwürfe immer die Zeilenzahl ergeben.

⚠️ **Daran hing der halbe Abend.** Wir haben einen Datenverlust gesucht, den es nie gab, weil
der Bildschirm zwei verschiedene Zahlen behauptete und ich der falschen geglaubt habe.

### Prüfungen

**476 grün** (von 464). Neu unter anderem: ein geholter Fang trägt sein `cloud`, er gilt nicht
als ungesichert, er wird nicht zurückgeschoben; eine Änderung während des Hochladens gilt
nicht als gesichert; Liste und Zählung widersprechen sich nie.

⚠️ **Gegengeprobt:** beide Fehler zur Kontrolle wieder eingebaut → **genau vier Prüfungen
fallen**, und zwar die vier, die es sollen. Eine Prüfung, die den Fehler nicht fängt, ist keine.

⚠️ **Am Prüfrahmen nachgebessert:** bricht der Lauf ohne Ergebnis ab, starb bisher die
**Fehlermeldung selbst** an einem `UnicodeEncodeError` (Windows-Konsole auf cp1252). Der
Abbruch war sichtbar, sein Grund nicht. Heute dreimal passiert.

⚠️ **Unverändert offen:** der Lauf bricht weiter sporadisch ohne Ergebnis ab (heute drei von
sechs Läufen) und geht beim Wiederholen ohne Änderung durch. Chrome wackelt unter virtueller
Zeit. Nicht behoben, nur benannt.

## 09.08.2026 (4) — Abgleich prüfen, und ein Loch gestopft

Karls Meldung: *„fänge auf meinem handy und auf meinem pc sind nicht gleich warum auch
immer."*

⚠️ **„Warum auch immer" ist der eigentliche Befund.** Der Abgleich läuft still, und wenn
etwas fehlt, sagt einem nichts, auf welcher Seite. Das ist dasselbe Muster wie beim
Datenverlust am 08.08. — nicht der Fehler kostet, sondern dass man ihn nicht sieht.

**Neu in den Einstellungen: „⇄ Abgleich prüfen".** Zeigt beide Seiten nebeneinander und
benennt die **Richtung**:

- *Im Konto: 14 · Auf diesem Gerät: 12*
- *2 liegen im Konto und fehlen hier* → dieses Gerät hat etwas nicht geholt
- *3 liegen hier und fehlen im Konto* → dieses Gerät hat etwas nicht hochgeladen
- *Entwürfe (bleiben absichtlich lokal): 1* → gehören in keine der beiden Richtungen

Stimmt etwas nicht, steht darunter **„⟲ Alles neu laden"**: setzt beide Stände zurück und
zieht alles einmal durch. Verlieren kann man dabei nichts (`merge-duplicates` beim Hochladen,
je Fang gewinnt die jüngere Fassung beim Herunterladen); es kostet einmal Datenvolumen für
alle Fotos, deshalb auf Ansage statt selbsttätig.

⚠️ **Und damit ist ein echtes Loch zu.** Der Herunterlade-Stand läuft **nur vorwärts** und
wurde nie zurückgesetzt. Verliert ein Gerät seine lokale Datenbank, behält aber den
localStorage — das passiert wirklich, Safari räumt IndexedDB nach längerer Nichtbenutzung
weg, der localStorage bleibt —, dann fragt es beim nächsten Abgleich „was ist seit gestern
passiert?" und bekommt: nichts. **Die Fänge liegen im Konto und kommen trotzdem nie wieder
herunter.** Für den Hochlade-Stand gibt es seit dem 08.08. eine Reparatur, für diese Richtung
gab es keine.

**464 Prüfungen grün** (von 460). Gegengeprobt: setzt man nur den Hochlade-Stand zurück,
schlägt die Prüfung an.

## 09.08.2026 (3) — Deutsch und Englisch

Karls Ansage: *„sprach einstellung deutsch + englisch."* Umschaltbar ganz oben in den
Einstellungen; ohne eigene Wahl entscheidet die Sprache des Geräts.

**Wie es gebaut ist — und warum so:**

⚠️ **Der Schlüssel ist der deutsche Satz selbst**, nicht ein Kürzel wie `log.empty`. Zwei
Gründe, und beide zählen bei einer App, die eine Person pflegt:
1. **Der Quelltext bleibt lesbar** — ein Aufruf mit dem Satz darin sagt beim Lesen, was dort
   steht. Bei Kürzeln müsste man jedes Mal in einer Tabelle nachschlagen.
2. **Eine fehlende Übersetzung fällt weich** — was fehlt, kommt auf Deutsch heraus. Ein
   Kürzel-System zeigte an derselben Stelle das Kürzel: kaputt statt bloß unübersetzt.

⚠️ **Übersetzt wird die Oberfläche, nicht die Daten.** Ein Fang, der als „Hecht" eingetragen
wurde, heißt „Hecht" — auch auf Englisch. Alles andere wäre gelogen: die App weiß nicht, ob
wirklich ein Hecht gemeint war, und ein einmal übersetzter Eintrag ließe sich nicht mehr
zurückrechnen. Die **Vorschlagslisten** (Fischarten, Köder) sind Vorschläge und werden
übersetzt; was eingetippt und gespeichert ist, bleibt stehen. Eine Prüfung wacht darüber.

⚠️ **Der gefährlichste Fall steckte in den Statistiken.** Bei festen Achsen (Wetter,
Tageszeit, Mondphase, Trübung) werden die Stufen über den **angezeigten Text** zugeordnet.
Stünde links „Bewölkt" und der Fang lieferte „Cloudy", fiele auf Englisch jeder Fang aus
seiner Stufe — **die Kurve läge flach auf null, ohne Fehlermeldung**, und sähe aus wie
„keine Fänge". Deshalb geht dort beides durch dieselbe Übersetzung, oder keines von beidem.
Eine eigene Prüfung stellt genau das nach; baut man den Fehler ein, schlägt sie an.

⚠️ **Die Datenschutzerklärung liegt zweimal ganz vor**, statt Satz für Satz nachgeschlagen zu
werden. Ein Rechtstext, der aus Einzelteilen entsteht, kann bei einer Lücke halb deutsch und
halb englisch herauskommen — und dann etwas anderes sagen, als er soll. **Maßgeblich ist die
deutsche Fassung**, das steht im englischen Text auch drin.

⚠️ **Die Sprachnamen selbst bleiben stehen** — „Deutsch" und „English", nicht „German".
Wer kein Deutsch kann und die App auf Deutsch vorfindet, sucht nach „English".

**Ein Wächter, den es vorher nicht gab:** Fehlt ein Eintrag im Wörterbuch, fällt das *nicht*
als Fehler auf — es kommt still Deutsch heraus, und das sieht nach Absicht aus statt nach
Lücke. Der Prüflauf bricht deshalb ab, wenn ein fester Aufruf ohne englische Fassung
dasteht. **401 Einträge, alle 166 festen Schlüssel gedeckt.**

**Nebenbei behoben:** Der Hinweis unter den Trübungs-Chips stand fest im HTML, in einem
Behälter, den der Sprach-Rundgang bewusst nicht anfasst — er wäre auf Englisch deutsch
stehen geblieben. Er kommt jetzt ganz aus dem Skript.

**460 Prüfungen grün** (von 449). Gegengeprobt an der Achsen-Zuordnung.

## 09.08.2026 (2) — Fehler melden und eine kurze Einführung

Zwei Ansagen von Karl: *„support für bugs"* und *„tutorial für die app, kleine vorstellung
wofür nutzt du die app, um die leute neugierig zu machen, nach dem registrieren."*

**Fehler melden** — in den Einstellungen unter „Hilfe & Fehler melden".

⚠️ **Der Kern ist nicht das Formular, sondern dass eine Meldung ohne Netz nicht
verlorengeht.** Kaputtes fällt beim Benutzen auf, und benutzt wird die App am Wasser — also
dort, wo oft kein Empfang ist. Eine Meldung, die nur mit Verbindung abzuschicken geht,
erreicht genau die Fälle nicht, für die sie gebaut ist. Sie liegt deshalb erst im Gerät und
geht mit dem nächsten Abgleich hinaus, wie ein Fang.

- Die Rückmeldung sagt **„ist notiert"**, nicht „ist abgeschickt". Ohne Netz wäre das zweite
  gelogen — und eine App, die so etwas behauptet, ist genau das Problem vom 08.08.
- **Ein Umfeld geht mit:** Fassung, Gerät, Bildschirm, Netz, ob vom Home-Bildschirm
  gestartet, Anzahl Fänge, ungesicherte Fänge, letzter Abgleich. Ohne das steht dort „geht
  nicht" und niemand kann etwas damit anfangen. **Was mitgeht, steht vor dem Abschicken
  sichtbar da** — nichts wird heimlich erhoben.
- Schlägt das Verschicken fehl, **bleibt die Meldung liegen** und geht beim nächsten Mal mit.
  Dieselbe Regel wie beim Push-Stand: nie einen Stand behaupten, für den nichts rausging.
- Neue Tabelle `angel_meldungen` in `supabase.sql`. **Absichtlich ohne Änderungs- und
  Löschrecht** — eine abgeschickte Meldung soll nicht nachträglich verschwinden können.

⚠️ **Neu: `FASSUNG` in `index.html`**, gekoppelt an den Cache-Namen in `sw.js`, eine Prüfung
wacht darüber. Eine Meldung mit falscher Fassungsangabe ist schlimmer als keine — bei einer
PWA läuft am iPhone wochenlang eine alte Seite weiter, das ist der Normalfall.

**Kurze Einführung** — vier Karten nach dem Registrieren, jederzeit wieder über die
Einstellungen.

⚠️ **Das ist bewusst keine Bedienungsanleitung.** Wer gerade ein Konto angelegt hat, weiß
noch nicht, warum sich das lohnt — er weiß nur, dass er Fische fängt. Jede Karte sagt, *was
die App für ihn tut*, nicht wo welcher Knopf sitzt. Knöpfe findet man; einen Grund nicht.

⚠️ **Nur nach dem Registrieren, nicht bei jedem Anmelden**, und an jeder Stelle
überspringbar. Eine Einführung, die man nicht wegklicken kann, macht niemanden neugierig,
sondern ungeduldig.

**449 Prüfungen grün** (von 434).

➡️ **Karl muss einmal `supabase.sql` erneut ausführen**, sonst laufen die Meldungen ins
Leere. Der Block ist gefahrlos wiederholbar.

## 09.08.2026 (1) — Sichtbar, was noch nicht in der Cloud liegt

Der Vorschlag vom 08.08., jetzt freigegeben. **Er behebt keinen Fehler — er behebt eine
Blindheit.**

Am 08.08. hat ein Fehler im Push-Stand zwei Fänge des Kollegen nie hochladen lassen; sie
lagen nur auf seinem iPhone, eine Neuinstallation hat sie mitgenommen. Der Fehler ist
behoben. **Aber der Fehler allein hat die Fänge nicht gekostet — seine Unsichtbarkeit hat
es.** Die App sah genauso aus wie eine, bei der alles oben liegt. Wer neu installiert, tut
das im Vertrauen darauf, dass die Cloud die Daten hat.

Deshalb ist das hier keine zweite Absicherung gegen denselben Fehler, sondern der Blick auf
das, was tatsächlich noch nicht gesichert ist. Das trägt auch bei allem, woran niemand
gedacht hat: kein Netz am Wasser, abgelaufene Sitzung, Server nicht erreichbar, ein
künftiger Fehler an derselben Stelle.

- **Oben in der Liste** steht ein Hinweis „*N* Fänge nur auf diesem Gerät", sobald etwas
  offen ist. **Antippen gleicht sofort ab.**
- **Jeder betroffene Fang ist einzeln markiert** — die Zahl allein genügt nicht, man muss
  sehen, *welche* es sind.
- **In den Einstellungen** steht die Warnung ausführlich: dort landet man, bevor man
  abmeldet, das Konto löscht oder neu installiert. Genau dort hat der Kollege nichts gesehen.

⚠️ **Maßstab ist derselbe, nach dem `hochladen()` auswählt** — alles mit `updated` über dem
Push-Stand. Eine eigene Buchführung wäre eine zweite Wahrheit neben der ersten, und die
zweite läge irgendwann falsch.

⚠️ **Entwürfe zählen nicht** (die sind absichtlich lokal und schon markiert), **Grabsteine
auch nicht** (eine nicht gemeldete Löschung kann keine Daten kosten).

⚠️ **Der Hinweis muss nach dem Hochladen verschwinden**, auch wenn dabei nichts
heruntergeladen wurde. Dafür ist das Auffrischen aus dem `runter`-Zweig herausgerückt. Eine
Warnung, die falsch stehen bleibt, wird bald übersehen — und trägt dann nichts mehr, wenn
sie einmal stimmt.

**434 Prüfungen grün** (von 424). Gegengeprobt: macht man die Anzeige blind, fallen fünf.

## 08.08.2026 (10) — Ladeleiste nach unten, Mitte ganz frei

Karls Ansage: *„der ladebalken soll nach unten und angel log soll aus der mitte weg."*
Übrig bleibt der Schirm in seiner einfachsten Form: **das Foto, und unten der Stand.**

- Die Leiste steht jetzt **unten**, mit Abstand über `env(safe-area-inset-bottom)` — sonst
  läge sie bei einer vom Home-Bildschirm gestarteten App teils unter dem Home-Strich.
  Dasselbe Thema wie eben oben bei der Dynamic Island, nur andersherum.
- **Name und Zeichen sind raus.** In der Mitte steht nichts mehr.

⚠️ **Der Schleier ist mitgewandert.** Er dunkelte oben und unten ab, damit die Beschriftung
lesbar bleibt. Oben steht jetzt nichts mehr — dort weiter abzudunkeln kostete Bild ohne
Gegenwert, und genau darum ging es ja. Er ist jetzt **unten kräftig und oben fast weg**.

**424 Prüfungen grün** (von 423).

## 08.08.2026 (9) — Ladeleiste oben statt Zeichen in der Mitte

Karls Ansage: *„das logo soll in der mitte weg dafür aber eine loading leiste ganz oben etwas
größer und mit prozenten."*

- **Das Zeichen in der Mitte ist raus.** Der Name bleibt — sonst sagt der Schirm nicht mehr,
  welche App startet.
- **Die Leiste steht ganz oben**, über die volle Breite, **7 px** statt 3, mit **Prozentzahl**
  darunter.
- ⚠️ **Abstand zur Statusleiste** über `env(safe-area-inset-top)`. Eine vom Home-Bildschirm
  gestartete App läuft bis unter die Dynamic Island; ohne den Abstand läge die Leiste teils
  darunter.
- Die Füllung folgt jetzt einem **Stand**, nicht mehr einer Animation. Vorher lief ein Strich
  endlos hin und her — das zeigte Bewegung, aber keinen Fortschritt.

⚠️ **Ehrlich benannt: die Zahl ist die Standzeit, kein gemessener Ladefortschritt.** Einen
solchen gibt es hier nicht — die Oberfläche steht nach wenigen Millisekunden, die Fänge kommen
aus dem Gerät, und weder Menge noch Dauer sind vorher bekannt. Was der Balken zeigt, ist die
verlässlichste ehrliche Auskunft, die zu geben ist: **wie lange es noch dauert**, bis der
Schirm weggeht.

⚠️ **Er läuft nur bis 96 %.** Die letzten Prozent gehören dem tatsächlichen Fertigwerden —
stünde er auf 100, während die App noch arbeitet, wäre das eine Lüge, die jeder sieht. Ist
alles fertig, springt er auf 100, und der Schirm blendet **220 ms später** weg; ohne diese
Pause wäre die 100 nie zu sehen.

⚠️ **Der Notausstieg räumt den Ticker mit ab.** Sonst zählte alle 60 ms etwas weiter, das
niemand mehr sieht — und zwar für immer, denn in diesem Fall ist der reguläre Weg ja nie
gelaufen.

**423 Prüfungen grün** (von 412).

## 08.08.2026 (8) — Neue Fassungen kommen auch am Handy an

**Karl sah die neue Fassung auf seinem iPhone nicht, sein Kollege schon.** Ursache war nicht
der Cache, sondern der **Lebenszyklus einer PWA**: der neue Service Worker übernimmt zwar
sofort (`skipWaiting` + `clients.claim`), aber er lädt die **bereits offene Seite nicht neu**.
Eine vom Home-Bildschirm gestartete App liegt am iPhone wochenlang im App-Switcher und wird
nie neu geladen — sie zeigt weiter das HTML von damals. Der Kollege hatte neu installiert und
deshalb eine frische Seite.

Drei Bausteine dagegen:

- **Beim Start nachsehen** (`registration.update()`). Von sich aus prüft der Browser nur
  gelegentlich.
- **Auch beim Zurückkommen aus dem Hintergrund** (`visibilitychange`). Bei einer PWA ist das
  der häufigste „Start" — ohne das bliebe sie beliebig lange alt.
- **Übernimmt ein neuer Worker, wird die Seite neu geladen.** Sonst läuft das alte HTML weiter
  und die Änderung bleibt unsichtbar.

⚠️ **Nicht mitten im Erfassen.** Wer gerade einen Fang eintippt, verlöre den sichtbaren Stand.
Der Entwurf wäre zwar gesichert, aber ein Neuladen unter den Händen ist trotzdem ein Übergriff
— dann kommt die neue Fassung beim nächsten Start, mit einem kurzen Hinweis.

⚠️ **Ein Riegel gegen die Endlosschleife.** Ein Worker, der beim Aktivieren erneut wechselt,
könnte die Seite sonst in eine Dauerschleife aus Neuladen schicken.

⚠️ **Geprüft am Quelltext, nicht am Verhalten:** der Service-Worker-Lebenszyklus lässt sich im
Prüfrahmen nicht nachstellen (kein echter Worker unter `file://` und keiner im iframe). Das
steht so in den Prüfungen und ist dort begründet.

**412 Prüfungen grün** (von 407).

## 08.08.2026 (7) — Der Ladebildschirm bleibt stehen

**Er stand nur Millisekunden** (Karls Meldung) — die Oberfläche ist nach wenigen Millisekunden
fertig, und damit war das Foto weg, bevor man es gesehen hatte. Jetzt steht er **mindestens
1,8 Sekunden**.

- ⚠️ **Gezählt wird ab dem Öffnen der Seite**, nicht ab dem Moment, in dem die App fertig ist.
  Sonst käme die Wartezeit oben drauf: ein langsames Gerät, das eine Sekunde zum Starten
  braucht, stünde dann 2,8 Sekunden hinter dem Schirm. So ist die Zeit eine **Obergrenze für
  das Warten** und keine Strafe für ein langsames Gerät.
- ⚠️ **Die Mindestzeit muss unter dem Notausstieg (4,5 s) liegen** — sonst räumt der den Schirm
  weg, während die Mindestzeit ihn noch halten will: zwei Uhren, die gegeneinander laufen.
  Dafür gibt es eine eigene Prüfung.
- Geprüft wird **beides**: dass er nach 500 ms noch steht und nach 2,4 s weg ist. Nur das
  Zweite zu prüfen ließe offen, ob die Mindestzeit überhaupt wirkt.

⚠️ **Am Prüfrahmen gelernt:** Chrome arbeitet unter `--virtual-time-budget` **CSS-Transitions
nicht ab**. Deckkraft und `visibility` bleiben dort auf ihrem Anfangswert, egal wie lange man
wartet. Was an einer Transition hängt, lässt sich im Rahmen nur als Regel prüfen, nicht am
Verhalten — steht jetzt so in den Prüfungen und ist dort auch begründet.

**407 Prüfungen grün** (von 404).

## 08.08.2026 (6) — Angelfotos als Ladebildschirm

**Karls sechs eigene Angelfotos füllen jetzt den Ladebildschirm**, bei jedem Öffnen ein
anderes. Zeichen und Name stehen darauf.

**Was mit den Bildern passiert ist:** sie kamen als PNG mit zusammen **14,8 MB** und im
Verhältnis 0,78 (fast quadratisch). Daraus wurden **987 KB** — sieben Prozent:

- **Zugeschnitten auf 9:19,5**, also randloses Handy-Hochformat, mittig. Bei allen sechs
  sitzt das Motiv in der Mitte (Fische, Angler, Köder, Steg). ⚠️ Dabei fällt rund die Hälfte
  der Breite weg — der Preis für vollflächig.
- **JPEG statt PNG.** Fotos, keine Grafik; PNG speichert hier jedes Rauschkorn verlustfrei mit.
- **Nicht hochgerechnet.** Der Ausschnitt behält seine echte Auflösung; ihn auf volle
  iPhone-Höhe zu blasen würde Schärfe erfinden und die Datei aufblähen. Das Hochskalieren
  macht der Browser, und bei einem Foto für eine Sekunde sieht man es kaum.
- Progressiv gespeichert: zeigt sich grob vorab statt zeilenweise einzulaufen.

⚠️ **Der Schirm wartet nie auf das Bild.** Er ist ab der ersten Zeile sichtbar — Palettenfarbe,
Zeichen, Name —, und das Foto blendet sich ein, sobald es geladen ist. Andersherum gebaut wäre
ein Ladebildschirm mit Foto **langsamer als gar keiner**, und beim allerersten Start ohne Cache
stünde die App sekundenlang hinter einer leeren Fläche. Kommt das Bild nicht, bleibt der Schirm
in Palettenfarbe: schlichter, aber nie leer.

⚠️ **Reihum, nicht zufällig.** Ein Zähler im Speicher geht bei jedem Start eins weiter. Bei
sechs Bildern fiele Zufall auf — dreimal dasselbe hintereinander wirkt kaputt, nicht
abwechslungsreich.

⚠️ **Ein Schleier liegt zwischen Foto und Beschriftung** (oben und unten dunkel, in der Mitte
durchsichtig). Ohne ihn ist der Name auf hellem Himmel oder auf Wasser unlesbar. Auf einem Foto
wird die Schrift zusätzlich hell gesetzt — auf den vier hellen Paletten ist `--txt` fast
schwarz und verschwände sonst.

⚠️ **Die Fotos liegen im Service-Worker-Cache.** Ohne das stünde am Wasser ohne Netz ein
Ladebildschirm ohne Bild — und genau dort wird die App benutzt. Knapp 1 MB einmalig; je Start
wird nur eines gezeigt.

⚠️ **Eine Prüfung hält die Zahl der Bilder an drei Stellen zusammen** (die Zahl im Skript, die
Liste im Service Worker, die Dateien auf der Platte). Laufen sie auseinander, zeigt die App
eine 404 statt eines Bildes — und zwar nur bei jedem n-ten Start, was beim Ausprobieren fast
sicher durchrutscht.

⚠️ **Am Prüfrahmen nachgebessert:** der Fehler-Melder von vorhin stand im selben `<script>` wie
die Prüfungen — ein Syntaxfehler dort hätte ihn gar nicht erst registriert, und genau dann
braucht man ihn. Er steht jetzt in einem eigenen Block.

**404 Prüfungen grün** (von 396).

## 08.08.2026 (5) — Bedienung an der Statistik statt in einer Liste

**Die Liste „Meine Auswertungen" über dem Baukasten ist weg** (Karls Ansage). Bearbeitet,
umbenannt und gelöscht wird jetzt **unten an der jeweiligen Statistik-Karte** — man sieht das
Bild, das man meint, statt es in einer Liste wiederzufinden.

- Unter dem Namen jeder gespeicherten Karte steht in einem Satz, **was eingestellt ist**
  („Hecht über Wassertiefe · nach Köderfarbe"). Bei mehreren Karten untereinander ist genau
  das die Frage, und der Name allein beantwortet sie nicht.
- ⚠️ **Die gerade geladene bekommt keinen „Bearbeiten"-Knopf**, sondern den Hinweis „Liegt oben
  im Baukasten". Ein Knopf, der nichts tut, gehört nicht hin.
- ⚠️ **„Bearbeiten" scrollt zum Baukasten hoch.** Ohne den Sprung tippt man unten auf einen
  Knopf und sieht nichts passieren, weil die Wirkung außerhalb des Bildes liegt.
- **Der Baukasten sagt oben, welche Auswertung offen ist** und ob es ungesicherte Änderungen
  gibt. Seit die Liste weg ist, ist das die einzige Stelle, an der das steht — sonst käme
  „Änderungen sichern" aus dem Nichts.
- Neu: **„Neu anfangen"** löst die Verbindung zur geladenen Auswertung. ⚠️ Nur die Verbindung —
  die Einstellungen bleiben stehen. Wer eine gespeicherte als Ausgangspunkt für eine neue
  nimmt, hätte sonst alles von vorn einzustellen. Gelöscht wird dabei nichts.

**Bearbeiten heißt jetzt die ganze Auswertung, nicht nur der Name** (Karls Ansage): über
„Bearbeiten" landet sie im Baukasten, dort lässt sich jede der vier Angaben ändern, und
„Änderungen sichern" schreibt sie zurück. Umbenennen gibt es weiterhin eigens.

**„Aufteilen nach Köder" ist raus, die Köderfarbe bleibt** (Karls Ansage). Der Köder steht
weiterhin als **X-Achse** zur Wahl — weg ist nur das Aufteilen mehrerer Kurven nach ihm.
⚠️ Gespeicherte Auswertungen mit `teilen: 'koeder'` kann es noch geben; sie zeichnen dann eine
einzelne Kurve statt einer aufgeteilten. Das ist der richtige Rückfall und kein leeres Bild.

⚠️ **Am Prüfrahmen nachgebessert:** brach ein Durchlauf durch eine Ausnahme **außerhalb** einer
Prüfung ab, meldete er nur „Kein Ergebnis" und warf den Quelltext aus — eine Meldung, die
nichts sagt und in der Fehlersuche mehrere Runden gekostet hat. Jetzt steht die Ausnahme
mitsamt Zeile im Ergebnis.

**396 Prüfungen grün** (von 388).

## 08.08.2026 (4) — Ködergewicht

**Neues Feld „Ködergewicht (g)"** beim Erfassen, direkt neben der Ködergröße — bei Kunstködern
stehen beide Angaben zusammen auf der Packung (12 cm / 25 g) und werden zusammen eingetippt.
Es steht in der Detailansicht und **als eigene Auswertung** zur Wahl.

- Die Achse läuft in **5-g-Stufen**: bei 1 g wäre sie ein Kamm aus lauter Einzelfängen, bei
  10 g fielen 20er und 25er in einen Topf.
- Sie zählt zu den **geordneten** Achsen — 20 g liegt zwischen 15 und 25, die Reihenfolge
  trägt hier eine Aussage.
- Ein leeres Feld bleibt leer und wird **nicht** zu 0 g. Eine Null wäre eine Aussage („wiegt
  nichts"), eine Lücke ist keine — dieselbe Regel wie bei allen anderen Messwerten.

⚠️ **Zur Frage, ob gespeicherte Auswertungen abgeglichen werden: ja.** Sie hängen seit dem
07.08. im selben Mechanismus wie die Angelzeit (Tabelle `angel_werte`, Schlüssel
`auswertungen`) — und sie hatten damit auch denselben Fehler, der heute behoben wurde: ohne
Zeitstempel gingen sie nie hoch.

**388 Prüfungen grün** (von 379).

## 08.08.2026 (3) — 🚨 Datenverlust behoben, Karte, Einstellungen, Statistiken am Handy

### 🚨 Zwei Fänge des Kollegen waren weg — Ursache gefunden und behoben

**Der Push-Stand wurde auf die Uhr gesetzt statt auf das, was hochgeladen wurde.**
Am Ende von `hochladen()` stand `Date.now()` — der Zeitpunkt **nach** dem Verschicken.
Ausgewählt werden die Fänge aber **davor**. Dazwischen liegt echte Zeit: Fotos verkleinern
und hochladen dauert am Handy im Mobilfunk zehn Sekunden bis eine Minute.

⚠️ **Jeder Fang, der in diesem Fenster entstand, fiel durch.** Für die laufende Runde war er
zu spät, und der neue Stand erklärte ihn zugleich für erledigt — beim nächsten Abgleich
übersprungen, und bei jedem weiteren auch. Er lag noch im Gerät, kam aber nie in die Cloud
und damit auf kein zweites Gerät. **Genau die Lage am Wasser: zwei Fische kurz nacheinander
eintragen, während der erste mit seinem Foto noch hochlädt.**

Jetzt rückt der Stand nur bis zum größten **tatsächlich verschickten** `updated` vor.
Grabsteine zählen dabei nicht mit — sie hängen an `gemeldet`, und ihr Zeitstempel könnte den
Stand sonst über Fänge schieben, die noch gar nicht dran waren.

⚠️ **Den Fehler zu beheben genügt nicht.** Auf jedem Gerät, das ihn erlebt hat, steht der
Stand bereits zu hoch: die durchgefallenen Fänge liegen zwar noch im Gerät, ihr `updated` ist
aber kleiner — sie würden auch mit repariertem Code weiter übersprungen, für immer. Deshalb
setzt die neue Fassung den Stand **einmalig je Gerät** auf 0 zurück. Der nächste Abgleich
prüft dann jeden Fang erneut und schickt hoch, was drüben fehlt. Verloren gehen kann dabei
nichts (`merge-duplicates` trifft dieselbe Zeile); es kostet einmal Datenvolumen für alle Fotos.

⚠️ **Zweiter Fehler in derselben Ecke:** `grabMarkieren` setzte `updated: Date.now()`. Ein
Grabstein bekam beim Melden einen **jüngeren** Stempel als den, mit dem er hochgeladen wurde —
und gewänne damit gegen eine echte spätere Wiederherstellung. Der Todeszeitpunkt bleibt jetzt
stehen; gemeldet wird ein Grabstein, sterben tut er nur einmal.

⚠️ **Gegengeprobt:** der Fehler wurde zur Kontrolle wieder eingebaut — die neuen Prüfungen
schlagen dann fehl. Eine Prüfung, die den Fehler nicht fängt, ist keine.

### Die Karte

**Wer während des Abgleichs auf der Karte stand, sah die neuen Fänge nicht.** Nach dem
Herunterladen wurde nur die Liste aufgefrischt — die Karte zeichnet erst beim nächsten
Ansichtswechsel neu. Jetzt wird aufgefrischt, was gerade zu sehen ist (Karte und Statistiken).
⚠️ Einen eigenen Abgleich hat die Karte nicht, sie zeigt schlicht `state.catches`. Fehlten dort
Fänge, war es der Fehler oben — auf der Karte fällt das am stärksten auf, weil alles auf einen
Blick liegt.

### Einstellungen schließen

**Oben ein Kreuz, und das Blatt lässt sich herunterwischen** (Karls Ansage — beides gebaut).
Bisher stand der einzige Knopf ganz unten; man musste erst durch alle Einstellungen scrollen.
Ein **Griff** oben zeigt, dass gewischt werden kann.
⚠️ Der heikle Teil ist die Abgrenzung zum Scrollen: das Blatt scrollt innen. Ein Wisch nach
unten zieht deshalb **nur**, wenn der Inhalt bereits ganz oben steht — sonst nähme man beim
Zurückscrollen versehentlich das ganze Blatt mit. Am Griff gilt das nicht, der ist zum Ziehen da.
⚠️ Nach oben wird nichts gezogen: ein Blatt, das nach oben geht, verspricht Inhalt, den es
nicht gibt. Und die Verschiebung wird beim Schließen zurückgesetzt, sonst wäre es beim nächsten
Öffnen verrutscht.

### Statistiken am Handy

**Auch am Handy stehen jetzt alle gespeicherten Auswertungen da, untereinander.** Das war
bisher auf den großen Bildschirm beschränkt, mit der Begründung „am Handy wäre alles andere
Scrollen". Karl hat recht: Scrollen ist am Handy das normale Mittel, und ohne die
gespeicherten muss man dort jede einzeln laden.

**379 Prüfungen grün** (von 367).

## 08.08.2026 (2) — Gewässer per Standort, Angelzeit-Fehler, Punkte-Auswahl raus

**🐞 Die Angelzeit kam an keinem zweiten Gerät an — behoben.** Karls Meldung, und es war
weder das Netz noch die Tabelle, sondern eine Bedingung im Abgleich: ein Wert mit
`updated: 0` galt als „nichts zu melden" und ging **nie** hoch.

- ⚠️ Genau das trifft auf **jede Angelzeit zu, die vor dem 07.08. entstanden ist**: sie lag
  im `localStorage`, lange bevor es ein `updated` gab. Das Gerät mit der Zeit lud sie nie
  hoch, das andere sah nie etwas. Sie wäre erst mitgekommen, wenn Karl sie von Hand geändert
  hätte. **„Kein Stempel" heißt nicht „nichts da"** — steht hier etwas und drüben nichts,
  bekommt es jetzt einen Stempel und geht hoch, auch lokal.
- ⚠️ **Der Wächter `hier.updated &&` musste trotzdem bleiben.** Beim ersten Anlauf hatte ich
  ihn mit entfernt; dadurch galt eine Null-Zeit als „jünger als nichts" und ging mit
  `updated: 0` hoch, womit sie drüben sofort wieder als älteste galt. Eine bestehende
  Prüfung hat das gefangen.
- ⚠️ **Und der Grund, warum es niemandem auffiel:** jeder selbsttätige Abgleich läuft still.
  Der Werte-Abgleich hat jetzt einen eigenen Fang-Block, und ein Fehler dort wird gemeldet —
  einmal je Sitzung. Vorher zogen die Fänge munter weiter durch und alles sah heil aus.

**Das Gewässer kommt automatisch aus dem Standort** und steht dafür **unten bei den anderen
geholten Werten** statt oben beim Fisch (beides Karls Ansage). Quelle ist OpenStreetMap über
Overpass — dieselbe Datenbasis wie die Karte. Wer laut Standort nicht am Wasser ist, bekommt
das nächstgelegene.

- ⚠️ **`around` allein findet den See nicht, in dem man steht.** Es misst zur Uferlinie:
  mitten auf dem Steinhuder Meer ist das Ufer über 1,5 km weg, die Umkreissuche kam leer
  zurück — ausgerechnet im Normalfall „ich bin am Wasser". Deshalb steht `is_in` davor.
  Das muss **vor** der Union stehen, sonst kommen Land, Bundesland und Gemeinde mit.
- ⚠️ **Das nächste ist nicht das richtige.** An der Elbe bei Hamburg gewinnt nach reiner
  Entfernung „Guanofleet" (213 m) gegen die Norderelbe (217 m). Deshalb ein Aufschlag je
  Art: ein Fluss oder See in 400 m ist wahrscheinlicher gemeint als ein Graben in 200 m.
  Damit gewinnt die Norderelbe. Weil es ein Ratespiel bleibt, stehen **die übrigen Funde als
  Knöpfe darunter** — eintippen muss man auch dann nichts, wenn der erste danebenliegt.
- Erst 1,5 km, nur bei leerem Ergebnis 20 km; zwei Server nacheinander. Overpass antwortet
  gelegentlich mit 429 oder 504 — das läuft nebenher und zieht die Luftwerte nicht mit runter.
- Die **Datenschutzerklärung** nennt Overpass jetzt als Empfänger der Koordinaten.

**Die Punkte-Auswahl in den Statistiken ist wieder raus** (Karls Ansage) — die Achse zeigt
immer alle Punkte. Sie stand genau einen Tag.
⚠️ Auswertungen, die am 07./08.08. mit einer Punkte-Liste gespeichert wurden, tragen das Feld
noch; es fällt beim ersten Anfassen weg. Bliebe es stehen, schnitte eine alte Auswertung
unsichtbar Werte ab, ohne dass es dafür noch eine Bedienung gäbe.
Mit ihr sind rund fünfzehn Prüfungen gegangen — was es nicht gibt, wird nicht geprüft.

**Das Symbol auf dem Home-Bildschirm:** eigenes `apple-touch-icon.png` in **180×180**, der
Größe, die iOS dafür tatsächlich anlegt. Vorher stand dort die 192er, die iOS zwar nimmt und
herunterrechnet — geraten wird an der einzigen Stelle, an der ein falsches Symbol auffällt,
aber nicht.
⚠️ **Am iPhone reicht Neuladen weiterhin nicht.** iOS merkt sich das Symbol beim **Anlegen**
der Verknüpfung: alte löschen, Seite in Safari öffnen, Teilen → „Zum Home-Bildschirm".

**362 Prüfungen grün**, darunter neue zum Angelzeit-Fall (Wert ohne Stempel, Stempel lokal,
kein Hochstempeln wenn drüben etwas liegt), zur Gewässer-Auswertung (Guanofleet-Fall,
mittendrin, Verwaltungsgrenzen, ein Fluss in vielen Abschnitten) und zum Symbol.

## 08.08.2026 — Ladebildschirm, das Zeichen in der App, `testrun/` raus

**Ein Ladebildschirm beim Start.** Symbol, Name und ein laufender Strich, in den Farben der
eingestellten Palette. Er deckt die Zeit ab, in der bisher kurz eine leere Fläche stand.

- ⚠️ **Er geht weg, sobald die Oberfläche steht — nicht erst, wenn die Fänge geladen sind.**
  Zuerst hing er hinter `await reload()`; dann stünde er bei einem vollen Fangbuch so lange
  wie das Laden dauert, und bei klemmender Datenbank (privates Safari-Fenster) bis zum
  Notausstieg. Beides hinter einer Fläche, unter der die fertige App längst liegt. Die Liste
  füllt sich sichtbar nach, sie hat ihren eigenen Leerzustand.
- ⚠️ **Notausstieg im Kopf der Seite, nicht in `init()`.** Der Schirm deckt die ganze Fläche
  ab — bliebe er stehen, wäre die App nicht hässlich, sondern unbedienbar. Ein Wecker nimmt
  ihn nach 4,5 s in jedem Fall weg, auch wenn `init()` nie erreicht wird (Skriptfehler,
  abgebrochener Download). Genau dieser Fall wird geprüft, mit einer absichtlich kaputten
  Fassung der App.
- ⚠️ **Die Palettenfarbe wird vor dem ersten Bild gesetzt.** Wer eine der vier hellen
  Paletten benutzt, sah bisher beim Start kurz Dunkelblau aufblitzen — die Palette wird erst
  in `init()` gesetzt. Ein Ladebildschirm in der falschen Farbe wäre genau das Aufblitzen,
  das er verhindern soll. Ein kleines Skript im Kopf liest dafür ein **Abbild von vier
  Farben** aus dem Speicher; `PALETTEN` bleibt die einzige Wahrheit, das Abbild schreibt
  `setPalette` bei jedem Wechsel mit — auch beim Durchtippen ohne Speichern, sonst zeigte
  der Schirm beim nächsten Start eine Farbe, die nicht mehr an ist.
- Wer Bewegung abgeschaltet hat (`prefers-reduced-motion`), bekommt einen ruhenden Strich.

**Das Symbol steht jetzt auch in der App**, klein neben „Angel-Log" in der Kopfzeile. Bis
heute war es nur auf dem Home-Bildschirm und im Browser-Tab zu sehen — in der App selbst
nirgends. Das war der Grund für den Eindruck, das neue Symbol vom 07.08. sei „gar nicht
drin": es ist ausgeliefert und richtig verdrahtet, nur an keiner Stelle sichtbar, die man
beim Benutzen zu Gesicht bekommt.

⚠️ **Am iPhone reicht Neuladen nicht für das Symbol auf dem Home-Bildschirm.** iOS merkt es
sich beim Anlegen der Verknüpfung. Alte Verknüpfung löschen, Seite in Safari öffnen, Teilen →
„Zum Home-Bildschirm" neu anlegen.

**`testrun/` ist aus dem Repo raus** — eine 441 KB große Kopie der ganzen App, versehentlich
eingecheckt, wurde unter `…github.io/angel-log/testrun/` mit ausgeliefert. Wer die Adresse
erwischte, benutzte eine App von vor Wochen mit eigener Datenbank. Der Prüfrahmen legt seinen
Arbeitsordner als `.testrun/` an (mit Punkt), der steht in `.gitignore`.

**362 Prüfungen grün** (von 353), neun davon zum Ladebildschirm.
⚠️ Dabei aufgefallen: **die Prüfungen ersetzen `putCatch`, die echte IndexedDB läuft im
Rahmen also nie mit.** Deshalb war nicht zu messen, wie lange `reload()` wirklich braucht —
im Testrahmen löst es unter Chromes virtueller Zeit überhaupt nicht auf. Die Reihenfolge
„Schirm weg, dann laden" ist deshalb als Quelltext-Prüfung abgesichert, nicht am Verhalten.

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
