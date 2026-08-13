"""
Prüfungen für Angel-Log.

Lädt die echte index.html in Chrome headless, hängt die Prüfungen unten an und
liest das Ergebnis aus dem DOM. Node ist auf dem PC nicht installiert, deshalb
der Umweg über den Browser — der hat den Vorteil, dass DOM und Formular echt
sind statt nachgebaut.

    python pruefungen.py

Die Statistik-Prüfungen laufen nur, wenn der Statistik-Reiter in dieser Fassung
enthalten ist (siehe Branch statistik-entwurf), sonst werden sie übersprungen.
"""
import subprocess, re, pathlib, shutil, sys, os

SRC  = pathlib.Path(__file__).resolve().parent
WORK = SRC / '.testrun'
CHROME = next((c for c in [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
] if pathlib.Path(c).exists()), None)
if not CHROME:
    sys.exit('Chrome nicht gefunden — Pfad in pruefungen.py anpassen.')

# OneDrive haelt Ordner gelegentlich fest, deshalb ueberschreiben statt loeschen.
if WORK.exists(): shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC, WORK, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns('.git', '.testrun', '*.py', '*.md'))

TESTS = r"""
<script>
/* ⚠️ Der Melder steht in einem EIGENEN script-Block. Stuende er im selben wie die
   Pruefungen, wuerde ihn ein Syntaxfehler dort gar nicht erst registrieren -- und genau
   dann braucht man ihn. Das hat einmal eine Runde gekostet. */
window.addEventListener('error', e => {
  if (document.getElementById('testout')) return;
  const pre = document.createElement('pre');
  pre.id = 'testout';
  pre.textContent = 'ABBRUCH ausserhalb einer Pruefung: ' + e.message
    + ' (Zeile ' + e.lineno + ')\n=== 0 ok, 1 fehlgeschlagen ===';
  document.body.appendChild(pre);
});
</script>
<script>
(function(){
  const out = [];
  let ok = 0, bad = 0;
  const t = (name, fn) => {
    try { const r = fn(); if (r === true) { ok++; out.push('OK   ' + name); }
          else { bad++; out.push('FAIL ' + name + '  -> ' + r); } }
    catch (e) { bad++; out.push('ERR  ' + name + '  -> ' + e.message); }
  };
  const near = (a, b, tol) => Math.abs(a - b) <= tol ? true : (a + ' != ' + b);

  // ---- Mondphase ----
  const NEU = Date.UTC(2000,0,6,18,14);
  const at = ms => mondFor(new Date(ms).toISOString());
  t('Neumond am Nullpunkt',        () => at(NEU).key === 'neumond' || at(NEU).key);
  t('Neumond hat ~0 % Licht',      () => near(at(NEU).licht, 0, 1));
  t('Vollmond nach halbem Monat',  () => at(NEU + 29.530588853/2*864e5).key === 'vollmond' || at(NEU + 29.530588853/2*864e5).key);
  t('Vollmond hat 100 % Licht',    () => near(at(NEU + 29.530588853/2*864e5).licht, 100, 1));
  t('Erstes Viertel',              () => at(NEU + 29.530588853/4*864e5).key === 'erstes-viertel' || at(NEU + 29.530588853/4*864e5).key);
  t('Erstes Viertel ~50 % Licht',  () => near(at(NEU + 29.530588853/4*864e5).licht, 50, 2));
  t('Letztes Viertel',             () => at(NEU + 29.530588853*0.75*864e5).key === 'letztes-viertel' || at(NEU + 29.530588853*0.75*864e5).key);
  t('Voller Zyklus = wieder Neumond', () => at(NEU + 29.530588853*864e5).key === 'neumond' || at(NEU + 29.530588853*864e5).key);
  t('Datum vor dem Nullpunkt geht', () => { const m = mondFor('1974-03-15T08:00'); return !!m && m.licht >= 0 && m.licht <= 100 || JSON.stringify(m); });
  t('Kaputtes Datum gibt null',     () => mondFor('quatsch') === null || 'nicht null');
  t('Leeres Datum gibt null',       () => mondFor('') === null || 'nicht null');
  t('Index bleibt in 0..7', () => {
    for (let d = 0; d < 60; d += 0.13){
      const m = mondFor(new Date(NEU + d*864e5).toISOString());
      if (!MONDPHASEN.some(p => p[0] === m.key)) return 'unbekannt bei Tag ' + d;
    }
    return true;
  });
  t('Licht bleibt 0..100', () => {
    for (let d = 0; d < 60; d += 0.07){
      const m = mondFor(new Date(NEU + d*864e5).toISOString());
      if (m.licht < 0 || m.licht > 100) return m.licht + ' bei Tag ' + d;
    }
    return true;
  });

  // ---- Wetterschlüssel (WMO) ----
  const w = [[0,'klar'],[1,'heiter'],[2,'bewoelkt'],[3,'bedeckt'],[45,'nebel'],[48,'nebel'],
             [51,'niesel'],[55,'niesel'],[57,'niesel'],[61,'regen'],[65,'regen'],[67,'regen'],
             [71,'schnee'],[77,'schnee'],[80,'schauer'],[82,'schauer'],[85,'schnee'],[86,'schnee'],
             [95,'gewitter'],[99,'gewitter']];
  w.forEach(([c, soll]) => t('WMO ' + c + ' -> ' + soll, () => wetterFor(c) === soll || wetterFor(c)));
  t('WMO null gibt leer',      () => wetterFor(null) === '' || wetterFor(null));
  t('WMO unbekannt gibt leer', () => wetterFor(4711) === '' || wetterFor(4711));
  t('Jeder Schlüssel hat ein Label', () => WETTER.every(([k]) => wetterLabel(k).length > 1) || 'fehlt');
  t('Jeder Schlüssel hat ein Zeichen', () => WETTER.every(([k]) => wetterIcon(k).length > 0) || 'fehlt');
  t('Alle wetterFor-Ergebnisse kennt WETTER', () => {
    for (let c = 0; c <= 100; c++){
      const k = wetterFor(c);
      if (k && !WETTER.some(x => x[0] === k)) return 'unbekannt: ' + k + ' bei ' + c;
    }
    return true;
  });

  // ---- Formular ----
  t('Wetter-Chips gebaut',   () => document.querySelectorAll('#ch-wetter .chip').length === WETTER.length
                                   || document.querySelectorAll('#ch-wetter .chip').length);
  t('Bewölkungsfeld da',     () => !!document.querySelector('#f-bewoelkung') || 'fehlt');
  t('Mondfeld da',           () => !!document.querySelector('#f-mond') || 'fehlt');
  t('Mondfeld ist kein Eingabefeld', () => document.querySelector('#f-mond').tagName === 'DIV' || document.querySelector('#f-mond').tagName);

  t('setWetter setzt', () => { setWetter('regen'); return state.form.wetter === 'regen' || state.form.wetter; });
  t('setWetter markiert den Chip', () => document.querySelector('[data-wetter="regen"]').classList.contains('on') || 'nicht markiert');
  t('setWetter setzt zweimal gleich (kein Umschalten)', () => { setWetter('regen'); return state.form.wetter === 'regen' || state.form.wetter; });
  t('selectWetter schaltet ab', () => { selectWetter('regen'); return state.form.wetter === '' || state.form.wetter; });
  t('selectWetter schaltet an',  () => { selectWetter('nebel'); return state.form.wetter === 'nebel' || state.form.wetter; });
  t('nur ein Wetter gleichzeitig', () => { setWetter('klar');
        return document.querySelectorAll('#ch-wetter .chip.on').length === 1
            || document.querySelectorAll('#ch-wetter .chip.on').length; });
  t('setWetter("") löscht', () => { setWetter(''); return document.querySelectorAll('#ch-wetter .chip.on').length === 0 || 'noch markiert'; });

  t('Mondanzeige folgt dem Datum', () => {
    document.querySelector('#f-zeit').value = '2026-01-03T06:00';
    renderMond();
    return /Vollmond/.test(document.querySelector('#f-mond').textContent)
        || document.querySelector('#f-mond').textContent;
  });
  t('Mondanzeige bei leerem Datum', () => {
    document.querySelector('#f-zeit').value = '';
    renderMond();
    return document.querySelector('#f-mond').textContent === '—' || document.querySelector('#f-mond').textContent;
  });

  t('buildRecord nimmt Wetter mit', () => {
    document.querySelector('#f-zeit').value = '2026-08-02T20:30';
    setWetter('schauer');
    document.querySelector('#f-bewoelkung').value = '75';
    const r = buildRecord(false);
    return (r.wetter === 'schauer' && r.bewoelkung === 75) || JSON.stringify([r.wetter, r.bewoelkung]);
  });
  t('leere Bewölkung wird null', () => {
    document.querySelector('#f-bewoelkung').value = '';
    return buildRecord(false).bewoelkung === null || buildRecord(false).bewoelkung;
  });
  t('Mond wird NICHT gespeichert (kommt aus dem Datum)',
     () => buildRecord(false).mond === undefined || 'doch gespeichert');

  // ---- Koedergewicht (Karls Ansage vom 08.08.) ----
  t('Koedergewicht laesst sich eintragen', () => {
    resetForm(null);
    document.querySelector('#f-koedergewicht').value = '25';
    return buildRecord(false).koederGewicht === 25 || buildRecord(false).koederGewicht;
  });
  t('leeres Koedergewicht bleibt leer, nicht null Gramm', () => {
    // Eine 0 waere eine Aussage ("wiegt nichts"), eine Luecke ist keine.
    resetForm(null);
    return buildRecord(false).koederGewicht === null || buildRecord(false).koederGewicht;
  });
  t('Koedergewicht allein zaehlt als Inhalt', () => {
    resetForm(null);
    const vorher = formHatInhalt();
    document.querySelector('#f-koedergewicht').value = '18';
    const nachher = formHatInhalt();
    document.querySelector('#f-koedergewicht').value = '';
    return (vorher === false && nachher === true) || (vorher + '/' + nachher);
  });
  t('es steht neben der Koedergroesse, nicht woanders', () => {
    const g = document.querySelector('#f-koedergroesse');
    const w = document.querySelector('#f-koedergewicht');
    return (g && w && g.closest('.card') === w.closest('.card'))
        || 'steht nicht in derselben Karte';
  });
  t('ein bestehender Fang bringt sein Koedergewicht mit', () => {
    resetForm({ id:'x', when:'2026-08-08T10:00', koederGewicht: 42 });
    const v = document.querySelector('#f-koedergewicht').value;
    resetForm(null);
    return v === '42' || v;
  });

  t('Wetter allein zählt als Inhalt', () => {
    resetForm(null);
    ['#f-art','#f-laenge','#f-gewicht','#f-gewaesser','#f-luft','#f-druck','#f-windstaerke',
     '#f-wasser','#f-tiefe','#f-bewoelkung','#f-koeder','#f-koedergroesse','#f-koedergewicht','#f-notiz']
      .forEach(s => document.querySelector(s).value = '');
    const vorher = formHatInhalt();
    setWetter('gewitter');
    const nachher = formHatInhalt();
    return (vorher === false && nachher === true) || (vorher + '/' + nachher);
  });
  t('Bewölkung allein zählt als Inhalt', () => {
    resetForm(null);
    ['#f-art','#f-laenge','#f-gewicht','#f-gewaesser','#f-luft','#f-druck','#f-windstaerke',
     '#f-wasser','#f-tiefe','#f-bewoelkung','#f-koeder','#f-koedergroesse','#f-koedergewicht','#f-notiz']
      .forEach(s => document.querySelector(s).value = '');
    setWetter('');
    document.querySelector('#f-bewoelkung').value = '40';
    return formHatInhalt() === true || 'nicht erkannt';
  });

  // ---- Altdaten: Fänge ohne die neuen Felder ----
  const alt = { id:'x', when:'2026-07-15T06:30', art:'Hecht', farbe:'Rot', laenge:78 };
  t('alter Fang: kein Wetter, kein Absturz', () => wetterLabel(alt.wetter) === '' || wetterLabel(alt.wetter));
  t('alter Fang: Mond kommt trotzdem', () => {
    const m = mondFor(alt.when);
    return (!!m && m.name.length > 3) || JSON.stringify(m);
  });
  t('alter Fang: Farben weiter lesbar', () => farbenVon(alt).join() === 'Rot' || farbenVon(alt).join());

  t('resetForm setzt Wetter zurück', () => {
    setWetter('regen');
    resetForm(null);
    return (state.form.wetter === '' && document.querySelectorAll('#ch-wetter .chip.on').length === 0)
        || (state.form.wetter + '/' + document.querySelectorAll('#ch-wetter .chip.on').length);
  });
  t('resetForm lädt Wetter eines Fangs', () => {
    resetForm({ id:'y', when:'2026-08-01T10:00', wetter:'nebel', bewoelkung:90 });
    return (state.form.wetter === 'nebel'
            && document.querySelector('#f-bewoelkung').value === '90')
        || (state.form.wetter + '/' + document.querySelector('#f-bewoelkung').value);
  });

  // ---- Angelzeit ----
  const zeitWeg = () => { try { localStorage.removeItem(ZEIT_KEY); } catch {} };

  t('Dauer: 0',            () => dauerText(0) === '0 min' || dauerText(0));
  t('Dauer: unter 1 min',  () => dauerText(59000) === '0 min' || dauerText(59000));
  t('Dauer: 1 min',        () => dauerText(60000) === '1 min' || dauerText(60000));
  t('Dauer: 90 min',       () => dauerText(90*60000) === '1 h 30 min' || dauerText(90*60000));
  t('Dauer: glatte Stunde',() => dauerText(3600000) === '1 h 0 min' || dauerText(3600000));
  t('Dauer: 25 h',         () => dauerText(25*3600000) === '25 h 0 min' || dauerText(25*3600000));
  t('Laufzeit: 0',         () => laufText(0) === '0:00:00' || laufText(0));
  t('Laufzeit: 1:01:01',   () => laufText(3661000) === '1:01:01' || laufText(3661000));
  t('Laufzeit: Sekunden zweistellig', () => laufText(9000) === '0:00:09' || laufText(9000));

  t('leerer Speicher gibt Null zurück', () => {
    zeitWeg();
    const z = zeitLesen();
    return (z.gesamt === 0 && z.start === null) || JSON.stringify(z);
  });
  t('kaputter Speicher stürzt nicht ab', () => {
    try { localStorage.setItem(ZEIT_KEY, 'kein json'); } catch {}
    const z = zeitLesen();
    return (z.gesamt === 0 && z.start === null) || JSON.stringify(z);
  });
  t('schreiben und lesen', () => {
    zeitSchreiben({ gesamt: 5000, start: 1234 });
    const z = zeitLesen();
    return (z.gesamt === 5000 && z.start === 1234) || JSON.stringify(z);
  });

  t('Start setzt den Startzeitpunkt', () => {
    zeitWeg(); renderZeit();
    document.querySelector('#btn-zeit').click();
    const z = zeitLesen();
    return (z.start != null && z.gesamt === 0) || JSON.stringify(z);
  });
  t('während des Laufens heisst der Knopf Stopp',
     () => document.querySelector('#btn-zeit').textContent.includes('Stopp')
        || document.querySelector('#btn-zeit').textContent);
  t('laufender Ansitz wird angezeigt',
     () => document.querySelector('#zeit-laeuft').hidden === false || 'versteckt');
  t('Stopp addiert auf die Gesamtzeit', () => {
    // Start künstlich 90 Minuten zurücklegen, dann stoppen.
    zeitSchreiben({ gesamt: 0, start: Date.now() - 90*60000 });
    document.querySelector('#btn-zeit').click();
    const z = zeitLesen();
    return (z.start === null && Math.abs(z.gesamt - 90*60000) < 3000) || JSON.stringify(z);
  });
  t('zweiter Ansitz addiert dazu', () => {
    zeitSchreiben({ gesamt: 90*60000, start: Date.now() - 30*60000 });
    document.querySelector('#btn-zeit').click();
    return Math.abs(zeitLesen().gesamt - 120*60000) < 3000 || zeitLesen().gesamt;
  });
  t('Gesamtzeit steht in der Anzeige', () => {
    renderZeit();
    return document.querySelector('#zeit-gesamt').textContent === '2 h 0 min'
        || document.querySelector('#zeit-gesamt').textContent;
  });
  t('laufender Ansitz zaehlt sichtbar mit', () => {
    zeitSchreiben({ gesamt: 60*60000, start: Date.now() - 30*60000 });
    renderZeit();
    return document.querySelector('#zeit-gesamt').textContent === '1 h 30 min'
        || document.querySelector('#zeit-gesamt').textContent;
  });
  t('gestoppt ist der laufende Hinweis weg', () => {
    zeitSchreiben({ gesamt: 60*60000, start: null }); renderZeit();
    return document.querySelector('#zeit-laeuft').hidden === true || 'noch sichtbar';
  });
  t('Uhr verstellt gibt keine negative Zeit', () => {
    // Start liegt in der Zukunft (Uhr zurueckgestellt) -- darf nicht abziehen.
    zeitSchreiben({ gesamt: 0, start: Date.now() + 60000 });
    renderZeit();
    document.querySelector('#btn-zeit').click();
    return zeitLesen().gesamt === 0 || zeitLesen().gesamt;
  });
  t('Angelzeit haengt nicht an den Faengen', () => {
    zeitSchreiben({ gesamt: 42*60000, start: null });
    state.catches = [];
    renderZeit();
    return document.querySelector('#zeit-gesamt').textContent === '42 min'
        || document.querySelector('#zeit-gesamt').textContent;
  });
  // ---- Vergessen zu stoppen ----
  const K = s => document.querySelector(s);
  t('kurzer Ansitz warnt nicht', () => {
    zeitSchreiben({ gesamt: 0, start: Date.now() - 3*3600000 });
    renderZeit();
    return K('#zeit-warnung').hidden === true || 'warnt zu frueh';
  });
  t('langer Ansitz warnt', () => {
    zeitSchreiben({ gesamt: 0, start: Date.now() - 14*3600000 });
    renderZeit();
    return (K('#zeit-warnung').hidden === false
            && K('#zeit-warnung').textContent.includes('vergessen')) || 'keine Warnung';
  });
  t('Korrekturfeld ist zuerst zu', () => {
    return K('#zeit-korr').hidden === true || 'steht offen';
  });
  t('Korrektur oeffnet und schliesst', () => {
    K('#btn-zeit-korr').click();
    const auf = K('#zeit-korr').hidden === false;
    K('#btn-zeit-korr').click();
    const zu = K('#zeit-korr').hidden === true;
    return (auf && zu) || (auf + '/' + zu);
  });
  t('Korrektur zeigt die Endzeit-Felder nur beim Laufen', () => {
    zeitSchreiben({ gesamt: 0, start: Date.now() - 14*3600000 });
    K('#btn-zeit-korr').click();                    // auf
    const beiLauf = K('#korr-laufend').hidden === false;
    K('#btn-zeit-korr').click();                    // zu
    zeitSchreiben({ gesamt: 0, start: null });
    K('#btn-zeit-korr').click();                    // auf
    const ohneLauf = K('#korr-laufend').hidden === true;
    K('#btn-zeit-korr').click();                    // zu
    return (beiLauf && ohneLauf) || (beiLauf + '/' + ohneLauf);
  });
  t('Korrektur ist mit der Gesamtzeit vorbelegt', () => {
    zeitSchreiben({ gesamt: 3*3600000 + 25*60000, start: null });
    K('#btn-zeit-korr').click();
    const ok = K('#korr-h').value === '3' && K('#korr-min').value === '25';
    K('#btn-zeit-korr').click();
    return ok || (K('#korr-h').value + ':' + K('#korr-min').value);
  });

  const stoppeUm = (startVorMs, endeIso) => {
    zeitSchreiben({ gesamt: 0, start: Date.now() - startVorMs });
    K('#btn-zeit-korr').click();
    K('#korr-ende').value = endeIso;
    K('#btn-korr-stop').click();
    const z = zeitLesen();
    if (K('#zeit-korr').hidden === false) K('#btn-zeit-korr').click();
    return z;
  };
  const isoVor = ms => {
    const d = new Date(Date.now() - ms), p = n => String(n).padStart(2,'0');
    return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
  };

  t('nachgetragene Endzeit kuerzt den Ansitz', () => {
    // Vor 14 h gestartet, tatsaechlich vor 10 h aufgehoert -> 4 h, nicht 14.
    const z = stoppeUm(14*3600000, isoVor(10*3600000));
    return (z.start === null && Math.abs(z.gesamt - 4*3600000) < 120000)
        || dauerText(z.gesamt);
  });
  t('Ende vor dem Start wird abgelehnt', () => {
    zeitSchreiben({ gesamt: 0, start: Date.now() - 2*3600000 });
    K('#btn-zeit-korr').click();
    K('#korr-ende').value = isoVor(5*3600000);       // vor dem Start
    K('#btn-korr-stop').click();
    const z = zeitLesen();
    K('#btn-zeit-korr').click();
    return (z.start != null && z.gesamt === 0) || JSON.stringify(z);
  });
  t('Ende in der Zukunft wird auf jetzt gekappt', () => {
    const z = stoppeUm(3*3600000, isoVor(-5*3600000));   // 5 h in der Zukunft
    return Math.abs(z.gesamt - 3*3600000) < 120000 || dauerText(z.gesamt);
  });
  t('leere Endzeit aendert nichts', () => {
    zeitSchreiben({ gesamt: 0, start: Date.now() - 2*3600000 });
    K('#btn-zeit-korr').click();
    K('#korr-ende').value = '';
    K('#btn-korr-stop').click();
    const z = zeitLesen();
    K('#btn-zeit-korr').click();
    return (z.start != null && z.gesamt === 0) || JSON.stringify(z);
  });

  t('Gesamtzeit direkt setzen', () => {
    zeitSchreiben({ gesamt: 99*3600000, start: null });
    K('#btn-zeit-korr').click();
    K('#korr-h').value = '12'; K('#korr-min').value = '30';
    K('#btn-korr-set').click();
    const z = zeitLesen();
    K('#btn-zeit-korr').click();
    return z.gesamt === 12*3600000 + 30*60000 || dauerText(z.gesamt);
  });
  t('Gesamtzeit setzen laesst den laufenden Ansitz laufen', () => {
    const start = Date.now() - 3600000;
    zeitSchreiben({ gesamt: 0, start });
    K('#btn-zeit-korr').click();
    K('#korr-h').value = '5'; K('#korr-min').value = '0';
    K('#btn-korr-set').click();
    const z = zeitLesen();
    K('#btn-zeit-korr').click();
    return (z.start === start && z.gesamt === 5*3600000) || JSON.stringify(z);
  });
  t('Gesamtzeit auf null setzen geht', () => {
    zeitSchreiben({ gesamt: 5*3600000, start: null });
    K('#btn-zeit-korr').click();
    K('#korr-h').value = '0'; K('#korr-min').value = '0';
    K('#btn-korr-set').click();
    const z = zeitLesen();
    K('#btn-zeit-korr').click();
    return z.gesamt === 0 || z.gesamt;
  });
  t('Unsinn in den Feldern wird zu null statt NaN', () => {
    zeitSchreiben({ gesamt: 5*3600000, start: null });
    K('#btn-zeit-korr').click();
    K('#korr-h').value = ''; K('#korr-min').value = 'abc';
    K('#btn-korr-set').click();
    const z = zeitLesen();
    K('#btn-zeit-korr').click();
    return z.gesamt === 0 || z.gesamt;
  });
  t('negative Eingabe wird nicht abgezogen', () => {
    zeitSchreiben({ gesamt: 0, start: null });
    K('#btn-zeit-korr').click();
    K('#korr-h').value = '-4'; K('#korr-min').value = '-10';
    K('#btn-korr-set').click();
    const z = zeitLesen();
    K('#btn-zeit-korr').click();
    return z.gesamt === 0 || z.gesamt;
  });
  zeitWeg();

  // ---- Trübung ----
  t('Trübungs-Chips gebaut', () => document.querySelectorAll('#ch-trueb .chip').length === TRUEBUNG.length
                                 || document.querySelectorAll('#ch-trueb .chip').length);
  t('setTrueb setzt',        () => { setTrueb('truebe'); return state.form.truebung === 'truebe' || state.form.truebung; });
  t('selectTrueb schaltet ab', () => { selectTrueb('truebe'); return state.form.truebung === '' || state.form.truebung; });
  t('nur eine Trübung gleichzeitig', () => { setTrueb('klar'); setTrueb('sehr');
        return document.querySelectorAll('#ch-trueb .chip.on').length === 1
            || document.querySelectorAll('#ch-trueb .chip.on').length; });
  t('truebLabel',            () => truebLabel('leicht') === 'Leicht trüb' || truebLabel('leicht'));
  t('truebLabel unbekannt',  () => truebLabel('quatsch') === '' || truebLabel('quatsch'));
  t('buildRecord nimmt Trübung mit', () => { setTrueb('sehr'); return buildRecord(false).truebung === 'sehr' || buildRecord(false).truebung; });
  t('Trübung allein zählt als Inhalt', () => {
    resetForm(null);
    ['#f-art','#f-laenge','#f-gewicht','#f-gewaesser','#f-luft','#f-druck','#f-windstaerke',
     '#f-wasser','#f-tiefe','#f-bewoelkung','#f-koeder','#f-koedergroesse','#f-koedergewicht','#f-notiz']
      .forEach(s => document.querySelector(s).value = '');
    const vorher = formHatInhalt();
    setTrueb('klar');
    return (vorher === false && formHatInhalt() === true) || (vorher + '/' + formHatInhalt());
  });
  t('resetForm lädt Trübung', () => {
    resetForm({ id:'z', when:'2026-08-01T10:00', truebung:'leicht' });
    return state.form.truebung === 'leicht' || state.form.truebung;
  });
  t('Hinweis ohne Daten', () => {
    resetForm(null);
    return document.querySelector('#trueb-info').textContent.includes('tipp an') || document.querySelector('#trueb-info').textContent;
  });
  t('Hinweis mit Regen', () => {
    resetForm(null);
    state.form.regen24 = 8.4; state.form.regen48 = 12.1; renderTruebHint();
    const s = document.querySelector('#trueb-info').textContent;
    return (s.includes('8,4 mm') && s.includes('12,1')) || s;
  });
  t('Hinweis nennt 48 h nur wenn mehr', () => {
    resetForm(null);
    state.form.regen24 = 5; state.form.regen48 = 5; renderTruebHint();
    return !document.querySelector('#trueb-info').textContent.includes('48 h') || 'doch genannt';
  });
  t('Hinweis mit Pegel steigend', () => {
    resetForm(null);
    state.form.pegel = { delta: 18, station: 'WESEL' }; renderTruebHint();
    const s = document.querySelector('#trueb-info').textContent;
    return (s.includes('+18 cm') && s.includes('steigend')) || s;
  });
  t('Hinweis mit Pegel fallend', () => {
    resetForm(null);
    state.form.pegel = { delta: -20, station: 'WESEL' }; renderTruebHint();
    return document.querySelector('#trueb-info').textContent.includes('fallend') || document.querySelector('#trueb-info').textContent;
  });
  t('kleiner Pegelunterschied heisst gleichbleibend', () => {
    resetForm(null);
    state.form.pegel = { delta: 1, station: 'X' }; renderTruebHint();
    return document.querySelector('#trueb-info').textContent.includes('gleichbleibend') || document.querySelector('#trueb-info').textContent;
  });
  t('alter Fang ohne Trübung stürzt nicht ab', () => truebLabel(undefined) === '' || truebLabel(undefined));

  // Der Statistik-Reiter ist am 02.08. vorerst aus der App genommen worden
  // (Branch statistik-entwurf / Tag statistik-v1). Diese Pruefungen laufen
  // deshalb nur, wenn der Reiter da ist -- so passt eine Testdatei auf beide Staende.
  if (typeof renderStats === "function"){
    // ---- Statistik ----
    // Seit dem 07.08. ein Baukasten statt einer festen Liste: eine Auswertung
    // besteht aus fuenf Angaben (art, x, teilen, gewaesser, zeit), laesst sich
    // speichern und wieder laden. Die Pruefungen darunter halten genau das fest.
    const mk = (o) => Object.assign({ id: Math.random().toString(36).slice(2), entwurf: false,
      when: '2026-07-15T06:30', ts: new Date('2026-07-15T06:30').getTime() }, o);
    const setzeFaenge = arr => { state.catches = arr; };
    const alleFilterAus = (x) => { state.stats = { gewaesser: '', art: '',
                                                   x: x || 'wasser', teilen: '',
                                                   aktiv: null }; };
    const R = arr => arr.map(v => ({ w: v }));
    // Eine Achse zum Durchreichen an reihenBauen, ohne den Umweg ueber die App.
    const wAchse = (stufe) => ({ key:'w', kurz:'W', stufe: stufe, hol: c => c.w });

    // ---- Stufen der X-Achse ----
    t('Stufen decken den Bereich ab', () => {
      const d = reihenBauen(R([8.2, 13.9]), wAchse(2), '');
      return d.stufen.map(e => e.x).join('|').includes('8|10|12') || d.stufen.map(e => e.x).join('|');
    });
    t('leere Stufe steht mit 0 drin', () => {
      const d = reihenBauen(R([8.2, 13.9]), wAchse(2), '');
      const i = d.stufen.findIndex(s => s.x === '8');
      const w = d.reihen[0].werte;
      return (w[i] === 1 && w[i+1] === 0 && w[i+2] === 1) || w.join(',');
    });
    t('Stufen zaehlen richtig', () => {
      const d = reihenBauen(R([8.1, 8.9, 9.5, 12.0]), wAchse(2), '');
      const i = d.stufen.findIndex(s => s.x === '8');
      return (d.reihen[0].werte[i] === 3 && d.reihen[0].werte[i+2] === 1) || d.reihen[0].werte.join(',');
    });
    // Karls Ansage vom 07.08.: "richtige Kurven, egal wieviele Faenge man hat."
    // Vorher fiel alles unter drei Stufen auf Balken zurueck.
    t('ein einziger Wert ergibt trotzdem mindestens fuenf Stufen', () => {
      const d = reihenBauen(R([12]), wAchse(2), '');
      return d.stufen.length >= 5 || ('nur ' + d.stufen.length);
    });
    t('die angehaengten Stufen sind leer, nicht erfunden', () => {
      const d = reihenBauen(R([12]), wAchse(2), '');
      const summe = d.reihen[0].werte.reduce((a, b) => a + b, 0);
      return summe === 1 || ('Summe ' + summe);
    });
    t('der echte Wert liegt in der Mitte der Stufen', () => {
      const d = reihenBauen(R([12]), wAchse(2), '');
      return d.stufen.some(s => s.x === '12') || d.stufen.map(s => s.x).join(',');
    });
    t('Stufen ohne Werte geben nichts zurueck', () => reihenBauen(R([]), wAchse(2), '') === null || 'nicht null');
    t('Stufen ignorieren null', () => {
      const d = reihenBauen([{w:null},{w:10},{w:undefined}], wAchse(2), '');
      return d.reihen[0].werte.reduce((a,b) => a+b, 0) === 1 || 'falsch gezaehlt';
    });
    t('Ausreisser brechen ab statt hundert leere Stufen zu bauen', () =>
      reihenBauen(R([1, 5000]), wAchse(2), '') === null || 'zu viele Stufen');
    t('Stufen rechnen auch bei 0', () => {
      const d = reihenBauen(R([0, 0.5]), wAchse(1), '');
      const i = d.stufen.findIndex(s => s.x === '0');
      return d.reihen[0].werte[i] === 2 || d.reihen[0].werte.join(',');
    });

    // ---- Reihen und Aufteilen ----
    t('ohne Aufteilen genau eine Reihe', () => {
      setzeFaenge([mk({ wasser: 9, koeder:'A' }), mk({ wasser: 13, koeder:'B' })]);
      alleFilterAus('wasser');
      const d = reihenBauen(statsRows(), achseVon('wasser'), '');
      return (d.reihen.length === 1 && d.reihen[0].name === 'Fänge') || d.reihen.map(r => r.name).join();
    });
    t('mit Aufteilen je Koederfarbe eine Reihe', () => {
      setzeFaenge([mk({ wasser: 9, farben:['Rot'] }), mk({ wasser: 13, farben:['Blau'] })]);
      alleFilterAus('wasser');
      const d = reihenBauen(statsRows(), achseVon('wasser'), 'farbe');
      return d.reihen.length === 2 || d.reihen.map(r => r.name).join();
    });
    // Karls Beispiel: Firetiger gegen Motoroil auf derselben Wassertiefe.
    t('Karls Beispiel: Farben getrennt ueber der Tiefe', () => {
      setzeFaenge([mk({ art:'Hecht', tiefe:2, farben:['Firetiger'] }),
                   mk({ art:'Hecht', tiefe:2, farben:['Firetiger'] }),
                   mk({ art:'Hecht', tiefe:5, farben:['Motoroil'] })]);
      alleFilterAus('tiefe'); state.stats.art = 'Hecht'; state.stats.teilen = 'farbe';
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      const ft = d.reihen.find(r => r.name === 'Firetiger');
      const mo = d.reihen.find(r => r.name === 'Motoroil');
      const i2 = d.stufen.findIndex(s => s.x === '2');
      const i5 = d.stufen.findIndex(s => s.x === '5');
      return (ft.werte[i2] === 2 && ft.werte[i5] === 0 && mo.werte[i5] === 1)
          || `FT ${ft.werte.join(',')} / MO ${mo.werte.join(',')}`;
    });
    t('Mehrfachfarben zaehlen in jeder Reihe', () => {
      setzeFaenge([mk({ tiefe:2, farben:['Rot','Gelb'] }), mk({ tiefe:2, farben:['Rot'] })]);
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      const rot = d.reihen.find(r => r.name === 'Rot'), gelb = d.reihen.find(r => r.name === 'Gelb');
      const i = d.stufen.findIndex(s => s.x === '2');
      return (rot.werte[i] === 2 && gelb.werte[i] === 1) || 'falsch gezaehlt';
    });
    t('alter Fang mit einzelner Farbe zaehlt mit', () => {
      setzeFaenge([mk({ tiefe:2, farbe:'Schwarz' })]);
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      return d.reihen.some(r => r.name === 'Schwarz') || d.reihen.map(r => r.name).join();
    });
    t('ein Fang zaehlt in derselben Stufe nur einmal', () => {
      // Zwei Farben, aber ein Fang: die Gesamtreihe darf ihn nicht doppelt zaehlen.
      setzeFaenge([mk({ tiefe:2, farben:['Rot','Gelb'] })]);
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), '');
      return d.reihen[0].werte.reduce((a,b) => a+b, 0) === 1 || 'doppelt gezaehlt';
    });
    // Mehr Farben als geprueft sind, gibt es nicht — die siebte waere geraten.
    t('hoechstens sechs Reihen', () => {
      setzeFaenge('ABCDEFGHIJ'.split('').map(k => mk({ tiefe:2, farben:[k] })));
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      return d.reihen.length <= 6 || ('es sind ' + d.reihen.length);
    });
    t('was nicht in die ersten fuenf passt, wird zusammengefasst', () => {
      setzeFaenge('ABCDEFGHIJ'.split('').map(k => mk({ tiefe:2, farben:[k] })));
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      return d.reihen.some(r => r.name === 'Übrige') || d.reihen.map(r => r.name).join();
    });
    t('nichts geht beim Zusammenfassen verloren', () => {
      setzeFaenge('ABCDEFGHIJ'.split('').map(k => mk({ tiefe:2, farben:[k] })));
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      const summe = d.reihen.reduce((a, r) => a + r.werte.reduce((x,y) => x+y, 0), 0);
      return summe === 10 || ('Summe ' + summe);
    });
    t('genau sechs Farben werden noch alle einzeln gezeigt', () => {
      setzeFaenge('ABCDEF'.split('').map(k => mk({ tiefe:2, farben:[k] })));
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      return (d.reihen.length === 6 && !d.reihen.some(r => r.name === 'Übrige'))
          || d.reihen.map(r => r.name).join();
    });
    t('keine Reihenfarbe kommt zweimal vor', () => {
      setzeFaenge('ABCDEFGHIJ'.split('').map(k => mk({ tiefe:2, farben:[k] })));
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'farbe');
      const f = d.reihen.map(r => r.farbe);
      return new Set(f).size === f.length || f.join();
    });
    t('helle Palette bekommt eigene Reihenfarben', () => {
      const merk = palAktiv;
      setPalette('tageslicht', false);
      const hell = reihenFarben()[0];
      setPalette('tiefes-wasser', false);
      const dunkel = reihenFarben()[0];
      setPalette(merk, false);
      return hell !== dunkel || 'dieselbe Farbe auf heller und dunkler Karte';
    });
    t('Aufteilen ohne eine einzige Farbe gibt nichts zurueck', () => {
      setzeFaenge([mk({ tiefe:2 })]);
      alleFilterAus('tiefe');
      return reihenBauen(statsRows(), achseVon('tiefe'), 'farbe') === null || 'nicht null';
    });

    // ---- Zeichnen: Kurve ----
    const einBild = (x, teilen) => { renderStats(); return document.querySelector('#stats-body').innerHTML; };
    t('Messwerte kommen als Kurve', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 13 }), mk({ wasser: 17 }), mk({ wasser: 21 })]);
      alleFilterAus('wasser');
      return einBild().includes('class="kurve"') || 'kein SVG';
    });
    // Genau der Fall, der vorher auf Balken zurueckfiel.
    t('auch zwei Faenge ergeben eine Kurve', () => {
      setzeFaenge([mk({ wasser: 17.1 }), mk({ wasser: 19.4 })]);
      alleFilterAus('wasser');
      return einBild().includes('class="kurve"') || 'wieder Balken';
    });
    t('sogar ein einziger Fang ergibt eine Kurve', () => {
      setzeFaenge([mk({ wasser: 17.1 })]);
      alleFilterAus('wasser');
      return einBild().includes('class="kurve"') || 'keine Kurve';
    });
    t('Kurve glaettet nicht (keine Bezier)', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 13 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      const h = einBild().replace(/<text[^>]*>[^<]*<\/text>/g, '');
      return !/[CQST]\d/.test(h) || 'Kurvenbefehl gefunden';
    });
    t('kein Punkt auf einer leeren Stufe', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 17 })]);   // 11, 13, 15 bleiben leer
      alleFilterAus('wasser');
      const h = einBild();
      return (h.match(/<circle/g) || []).length === 2 || (h.match(/<circle/g) || []).length;
    });
    // "Richtige Kurven" heisst auch: eine Y-Achse, an der man ablesen kann.
    t('die Y-Achse ist beschriftet', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 9 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      const h = einBild();
      return (h.includes('>0</text>') && /<line[^>]*stroke="var\(--line\)"/.test(h)) || 'keine Achse';
    });
    t('die Y-Achse laeuft nur ueber ganze Zahlen', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      const h = einBild();
      return !/>0,5<\/text>|>1,5<\/text>/.test(h) || 'halbe Faenge auf der Achse';
    });
    t('unter der Kurve steht, was auf der X-Achse liegt', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      return einBild().includes('Wassertemperatur (°C)') || 'kein Achsentitel';
    });
    // Nicht jeder Punkt traegt eine Zahl — bei sechs Kurven waeren das Dutzende
    // uebereinander. Beschriftet wird der hoechste Punkt je Kurve.
    t('nur die Spitze je Kurve traegt eine Zahl', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 9 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      const h = einBild();
      const svg = h.slice(h.indexOf('<svg'), h.indexOf('</svg>'));
      // Zahlen ueber Punkten haben font-weight 700; die Achsentexte nicht.
      return (svg.match(/font-weight="700"/g) || []).length === 1
          || (svg.match(/font-weight="700"/g) || []).length;
    });
    t('eine einzelne Kurve braucht keine Legende', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      return !einBild().includes('class="leg"') || 'Legende bei einer Reihe';
    });
    t('mehrere Kurven haben immer eine Legende', () => {
      setzeFaenge([mk({ wasser: 9, farben:['Firetiger'] }), mk({ wasser: 17, farben:['Motoroil'] })]);
      alleFilterAus('wasser'); state.stats.teilen = 'farbe';
      const h = einBild();
      return (h.includes('class="leg"') && h.includes('Firetiger') && h.includes('Motoroil'))
          || 'Legende fehlt oder unvollstaendig';
    });
    const achsenTexte = () => {
      const h = document.querySelector('#stats-body').innerHTML;
      const svg = h.slice(h.indexOf('<svg'), h.indexOf('</svg>'));
      return (svg.match(/text-anchor="middle"/g) || []).length;
    };
    t('kurze Achsentexte duerfen dicht stehen', () => {
      setzeFaenge([mk({ druck: 990 }), mk({ druck: 1040 })]);   // 5er-Stufen ueber 50 hPa
      alleFilterAus('druck'); einBild();
      const n = achsenTexte();
      return (n >= 6 && n <= 12) || ('Achsentexte: ' + n);
    });
    // Acht Mondphasen mit Zeichen und Namen — die passen nicht alle nebeneinander.
    t('lange Achsentexte werden ausgeduennt', () => {
      setzeFaenge([mk({ when:'2026-07-01T08:00', ts:1 }), mk({ when:'2026-07-15T08:00', ts:2 })]);
      alleFilterAus('mond'); einBild();
      const n = achsenTexte();
      return n <= 5 || ('Achsentexte: ' + n);
    });
    t('lange Achsentexte werden abgeschnitten, nicht gequetscht', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      return h.includes('…') || 'nichts gekuerzt';
    });
    t('die Ablesehilfe ist da', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      return einBild().includes('class="lupe"') || 'keine Ablesehilfe';
    });

    // ---- Kategorien ----
    // ⚠️ Karls Ansage vom 07.08., zweimal und ausdruecklich: ALLES als Kurve,
    // auch Fischart und Koeder. Mein Einwand (eine Linie zwischen "Hecht" und
    // "Barsch" behauptet eine Reihenfolge) steht als Hinweis unter dem Bild.
    t('auch Kategorien kommen als Kurve', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Barsch' })]);
      alleFilterAus('art');
      const h = einBild();
      return (h.includes('class="kurve"') && !h.includes('class="bar"')) || 'Fischart ist keine Kurve';
    });
    t('bei Kategorien steht der Hinweis auf die fehlende Reihenfolge', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      return h.includes('keine natürliche Reihenfolge') || 'Hinweis fehlt';
    });
    t('bei Messwerten steht der Hinweis nicht', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 17 })]);
      alleFilterAus('wasser');
      return !einBild().includes('keine natürliche Reihenfolge') || 'Hinweis steht faelschlich da';
    });
    t('Kategorien lassen sich aufteilen', () => {
      setzeFaenge([mk({ art:'Hecht', farben:['Firetiger'] }), mk({ art:'Hecht', farben:['Motoroil'] }),
                   mk({ art:'Barsch', farben:['Firetiger'] })]);
      alleFilterAus('art'); state.stats.teilen = 'farbe';
      const h = einBild();
      return (h.includes('Firetiger') && h.includes('Motoroil') && h.includes('class="leg"'))
          || 'keine zwei Kurven';
    });
    t('Koederfarbe kommt als Kurve', () => {
      setzeFaenge([mk({ farben:['Firetiger'] }), mk({ farben:['Rot'] })]);
      alleFilterAus('farbe');
      return einBild().includes('class="kurve"') || 'keine Kurve';
    });
    // Als Balkenliste war die Reihenfolge egal, als Kurve ist sie die halbe Aussage.
    t('die Tageszeit laeuft von morgens nach nachts', () => {
      setzeFaenge([mk({ phase:'nacht' }), mk({ phase:'morgen' })]);
      alleFilterAus('tageszeit');
      const d = reihenBauen(statsRows(), achseVon('tageszeit'), '');
      return d.stufen.map(s => s.x).join('|') === PHASEN.map(p => p[1]).join('|')
          || d.stufen.map(s => s.x).join('|');
    });
    t('leere Tageszeiten stehen mit null drin', () => {
      setzeFaenge([mk({ phase:'nacht' }), mk({ phase:'morgen' })]);
      alleFilterAus('tageszeit');
      const d = reihenBauen(statsRows(), achseVon('tageszeit'), '');
      return d.reihen[0].werte.join(',') === '1,0,0,1' || d.reihen[0].werte.join(',');
    });
    t('die Truebung laeuft von klar nach sehr trueb', () => {
      setzeFaenge([mk({ truebung:'sehr' }), mk({ truebung:'klar' })]);
      alleFilterAus('trueb');
      const d = reihenBauen(statsRows(), achseVon('trueb'), '');
      return d.stufen.map(s => s.x).join('|') === TRUEBUNG.map(x => x[1]).join('|')
          || d.stufen.map(s => s.x).join('|');
    });
    t('der Mond laeuft von Neumond nach Neumond', () => {
      const d = reihenBauen([{ when:'2026-07-01T08:00' }], achseVon('mond'), '');
      return d.stufen.length === MONDPHASEN.length || d.stufen.length;
    });
    t('das Wetter behaelt seine Reihenfolge von klar nach Schnee', () => {
      setzeFaenge([mk({ wetter:'schnee' }), mk({ wetter:'klar' })]);
      alleFilterAus('wetter');
      const d = reihenBauen(statsRows(), achseVon('wetter'), '');
      return (d.stufen.length === WETTER.length && d.stufen[0].x.includes('Klar'))
          || d.stufen.map(s => s.x).join('|');
    });
    t('ohne feste Liste steht das Haeufigste vorn', () => {
      setzeFaenge([mk({ art:'Barsch' }), mk({ art:'Hecht' }), mk({ art:'Hecht' })]);
      alleFilterAus('art');
      const d = reihenBauen(statsRows(), achseVon('art'), '');
      return d.stufen[0].x === 'Hecht' || d.stufen.map(s => s.x).join('|');
    });
    // Der hoechste Punkt muss die oberste Gitterlinie treffen, sonst verschenkt
    // die Kurve Hoehe und kleine Unterschiede verschwinden.
    t('die hoechste Kurve reicht bis zur obersten Linie', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Hecht' }), mk({ art:'Barsch' })]);
      alleFilterAus('art');
      const h = einBild();
      // Bei Maximum 2 ist die Obergrenze 2 — der Punkt sitzt auf pT (16).
      return /<circle[^>]*cy="16\.0"/.test(h) || 'Kurve reicht nicht nach oben';
    });

    // ---- Ansicht insgesamt ----
    t('Statistik rendert', () => {
      setzeFaenge([
        mk({ art:'Hecht', gewaesser:'Kanal', laenge:78, gewicht:3.2, druck:1013, wasser:19.4,
             tiefe:2.5, phase:'morgen', wetter:'bedeckt', koeder:'Gummifisch', farben:['Firetiger'] }),
        mk({ art:'Zander', gewaesser:'Kanal', laenge:55, druck:1002, wasser:17.1,
             phase:'nacht', wetter:'regen', koeder:'Wobbler', farben:['Rot','Gelb'] })
      ]);
      alleFilterAus('wasser');
      return einBild().includes('Wassertemperatur') || 'Block fehlt';
    });
    t('immer nur ein Diagramm', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      return (h.match(/<h2>/g) || []).length === 1 || ('Bloecke: ' + (h.match(/<h2>/g) || []).length);
    });
    t('Auswertung ohne Daten sagt es statt zu verschwinden', () => {
      setzeFaenge([mk({ art:'Hecht' })]);          // keine Wassertemperatur erfasst
      alleFilterAus('wasser');
      const h = einBild();
      return (h.includes('Wassertemperatur') && h.includes('noch kein Fang')) || 'still verschwunden';
    });
    t('unbekannte Achse faellt auf die erste zurueck', () => {
      setzeFaenge([mk({ art:'Hecht', wasser: 12 })]);
      alleFilterAus('gibtsnicht');
      return einBild().includes('Wassertemperatur') || 'nichts gezeigt';
    });
    t('jede Achse laeuft ohne Absturz', () => {
      setzeFaenge([mk({ art:'Hecht', gewaesser:'Kanal', laenge:78, druck:1013, wasser:19.4, luft:22,
                        tiefe:2.5, regen24:3, koederGroesse:8, phase:'morgen', wetter:'bedeckt',
                        truebung:'klar', koeder:'Gummifisch', farben:['Firetiger'] })]);
      for (const a of ACHSEN){
        alleFilterAus(a.key);
        try { renderStats(); } catch (e){ return a.key + ': ' + e.message; }
      }
      return true;
    });
    t('jede Achse haelt leere Daten aus', () => {
      setzeFaenge([mk({})]);
      for (const a of ACHSEN){
        alleFilterAus(a.key);
        try { renderStats(); } catch (e){ return a.key + ': ' + e.message; }
      }
      return true;
    });
    t('jede Achse haelt das Aufteilen aus', () => {
      setzeFaenge([mk({ art:'Hecht', wasser:19.4, tiefe:2.5, koeder:'Wobbler', farben:['Rot'] }),
                   mk({ art:'Barsch', wasser:12.0, tiefe:4.0, koeder:'Spinner', farben:['Gelb'] })]);
      for (const a of ACHSEN){
        for (const teiler of ['farbe']){
          alleFilterAus(a.key); state.stats.teilen = teiler;
          try { renderStats(); } catch (e){ return a.key + '/' + teiler + ': ' + e.message; }
        }
      }
      return true;
    });

    // ---- Filter ----
    t('Entwuerfe zaehlen nicht mit', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Zander', entwurf:true })]);
      alleFilterAus();
      return statsRows().length === 1 || statsRows().length;
    });
    t('Filter Gewaesser', () => {
      setzeFaenge([mk({ gewaesser:'Kanal' }), mk({ gewaesser:'Weser' })]);
      alleFilterAus(); state.stats.gewaesser = 'Kanal';
      return statsRows().length === 1 || statsRows().length;
    });
    t('Zaehlen auf eine Fischart einschraenken', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Barsch' })]);
      alleFilterAus(); state.stats.art = 'Barsch';
      return statsRows().length === 1 || statsRows().length;
    });
    // Der Zeitraum ist am 07.08. rausgeflogen -- an seiner Stelle waehlt man die
    // Punkte der X-Achse. Diese Pruefung haelt fest, dass das Alter eines Fangs
    // die Auswahl NICHT mehr einschraenkt.
    t('alte Faenge zaehlen weiter mit', () => {
      const alt = new Date(Date.now() - 200*864e5).toISOString().slice(0,16);
      setzeFaenge([mk({ when: new Date().toISOString().slice(0,16), ts: Date.now() }),
                   mk({ when: alt, ts: Date.now() - 200*864e5 })]);
      alleFilterAus();
      return statsRows().length === 2 || statsRows().length;
    });
    t('der Titel nennt die gezaehlte Fischart', () => {
      setzeFaenge([mk({ art:'Hecht', tiefe:2 }), mk({ art:'Barsch', tiefe:3 })]);
      alleFilterAus('tiefe'); state.stats.art = 'Hecht';
      return einBild().includes('Hecht nach Wassertiefe') || 'Titel nennt die Art nicht';
    });

    // ---- Kacheln ----
    const zweiFaenge = () => {
      setzeFaenge([
        mk({ art:'Hecht', gewaesser:'Kanal', laenge:78, gewicht:3.2, koeder:'Gummifisch' }),
        mk({ art:'Zander', gewaesser:'Kanal', laenge:55, koeder:'Wobbler' })
      ]);
    };
    t('Statistik nennt den groessten Fisch', () => {
      zweiFaenge(); alleFilterAus('art');
      return einBild().includes('78 cm') || 'fehlt';
    });
    t('Kacheln bleiben immer', () =>
      document.querySelector('#stats-body').innerHTML.includes('class="tiles"') || 'Kacheln weg');
    // Karls Ansage vom 07.08.: die obersten beiden Kacheln getauscht.
    t('Fischarten steht vor Faenge', () => {
      zweiFaenge(); alleFilterAus('art');
      const h = einBild();
      const k = h.slice(h.indexOf('class="tiles"'));
      return k.indexOf('Fischarten') < k.indexOf('>Fänge<') || 'Reihenfolge der Kacheln stimmt nicht';
    });

    // ---- Hinweise, die nicht wegfallen duerfen ----
    t('Statistik warnt bei wenig Daten', () => {
      zweiFaenge(); alleFilterAus('art');
      return einBild().includes('zu wenige') || 'keine Warnung';
    });
    t('die Warnung haelt das Zeichnen nicht mehr auf', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      return (h.includes('zu wenige') && h.includes('class="kurve"')) || 'kein Diagramm trotz Warnung';
    });
    t('Statistik sagt nirgends "bester"',
       () => !/bester|beste Köder|Bester/.test(document.querySelector('#stats-body').innerHTML) || 'steht doch drin');
    t('Statistik weist auf fehlende Leer-Ansitze hin', () => {
      zweiFaenge(); alleFilterAus('koeder');
      return einBild().includes('ohne Fang') || 'Hinweis fehlt';
    });
    t('bei Koederfarben steht die Mehrfachzaehlung dabei', () => {
      setzeFaenge([mk({ farben:['Rot','Gelb'] })]);
      alleFilterAus('farbe');
      return einBild().includes('zählt in jeder mit') || 'Hinweis fehlt';
    });
    t('das Zusammenfassen wird benannt', () => {
      setzeFaenge('ABCDEFGHIJ'.split('').map(k => mk({ tiefe:2, farben:[k] })));
      alleFilterAus('tiefe'); state.stats.teilen = 'farbe';
      return einBild().includes('häufigsten') || 'kein Hinweis auf Übrige';
    });
    t('Zaehler in der Kopfzeile', () => {
      zweiFaenge(); alleFilterAus(); renderStats();
      return document.querySelector('#stats-pill').textContent === '2 Fänge'
          || document.querySelector('#stats-pill').textContent;
    });
    t('Statistik ohne Faenge', () => {
      setzeFaenge([]); alleFilterAus();
      return einBild().includes('Noch keine fertigen') || 'falscher Text';
    });
    t('Statistik mit leerem Filterergebnis', () => {
      setzeFaenge([mk({ art:'Hecht' })]);
      alleFilterAus(); state.stats.art = 'Wels';
      return einBild().includes('keinen Fang') || 'falscher Text';
    });
    t('Auswahlliste behaelt die aktive Auswahl', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Wels' })]);
      alleFilterAus(); state.stats.art = 'Wels'; renderStats();
      return document.querySelector('#st-art').value === 'Wels' || document.querySelector('#st-art').value;
    });

    // ---- Der Baukasten ----
    // ---- Die Punkte-Auswahl gibt es nicht mehr ----
    // Sie stand vom 07. bis 08.08.2026 im Baukasten; Karl hat sie wieder
    // abbestellt: es sollen immer alle Punkte im Bild stehen. Die rund fuenfzehn
    // Pruefungen dazu sind mit ihr entfernt worden -- was es nicht gibt, wird
    // nicht geprueft. Was bleibt, steht unten: die Achse zeigt vollstaendig.
    const dreiArten = () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Hecht' }), mk({ art:'Barsch' }), mk({ art:'Zander' })]);
      alleFilterAus('art'); renderStats();
    };
    t('die Achse zeigt alle Punkte, ohne Auswahl', () => {
      dreiArten();
      const d = reihenBauen(statsRows(), achseVon('art'), '');
      return (d.stufen.length === 3) || ('Stufen: ' + JSON.stringify(d.stufen.map(s => s.x)));
    });
    t('es gibt keine Bedienung mehr, die Punkte abwaehlt', () => {
      dreiArten();
      const reste = ['#st-punkte', '#st-punkte-titel', '#st-alle', '#st-keine']
        .filter(sel => document.querySelector(sel));
      return reste.length === 0 || ('noch da: ' + reste.join(', '));
    });
    // ⚠️ Auswertungen, die am 07./08.08. mit einer Punkte-Liste gespeichert wurden,
    // tragen das Feld noch. Bliebe es stehen, schnitte eine alte Auswertung
    // unsichtbar Werte ab -- ohne dass es dafuer noch eine Bedienung gaebe.
    t('eine alte Punkte-Liste faellt beim Anfassen weg', () => {
      const a = auswNehmen({ art:'Hecht', x:'tiefe', teilen:'', gewaesser:'',
                             punkte:['Hecht','Barsch'] });
      return a.punkte === undefined || JSON.stringify(a);
    });

    state.auswertungen = []; localStorage.removeItem('angellog-auswertungen');
    t('die X-Achse ist waehlbar und vollstaendig', () => {
      const n = document.querySelectorAll('#st-x option').length;
      return n === ACHSEN.length || n;
    });
    // ---- Koedergewicht als Auswertung (Karls Ansage vom 08.08.) ----
    t('Koedergewicht steht als Achse zur Wahl', () => {
      const o = [...document.querySelectorAll('#st-x option')].find(x => x.value === 'koedergewicht');
      return (o && /Ködergewicht/.test(o.textContent)) || (o ? o.textContent : 'nicht in der Liste');
    });
    t('Koedergewicht steht bei den geordneten Achsen', () => {
      // Gramm haben eine natuerliche Reihenfolge — 20 g liegt zwischen 15 und 25.
      // Landete es bei "nach Haeufigkeit", stuende die Achse in falscher Ordnung da.
      const a = achseVon('koedergewicht');
      return hatOrdnung(a) === true || 'gilt als ungeordnet';
    });
    t('Koedergewicht wird in 5-g-Stufen gezeichnet', () => {
      setzeFaenge([mk({ koederGewicht: 12 }), mk({ koederGewicht: 14 }), mk({ koederGewicht: 27 })]);
      alleFilterAus('koedergewicht');
      const d = reihenBauen(statsRows(), achseVon('koedergewicht'), '');
      // 12 und 14 fallen in dieselbe Stufe, 27 liegt drei Stufen weiter.
      const summe = d.reihen[0].werte.reduce((a, b) => a + b, 0);
      return (summe === 3 && d.stufen.length >= 4)
          || `Summe ${summe}, Stufen ${JSON.stringify(d.stufen.map(s => s.x))}`;
    });
    t('die Achse traegt die Einheit Gramm', () => {
      setzeFaenge([mk({ koederGewicht: 20 })]);
      alleFilterAus('koedergewicht');
      const d = reihenBauen(statsRows(), achseVon('koedergewicht'), '');
      return /g/.test(d.xTitel) || d.xTitel;
    });
    // Die Gruppen sagen nicht mehr "Kurve oder Balken" — es ist alles eine
    // Kurve —, sondern ob die Reihenfolge der X-Achse etwas bedeutet.
    t('geordnete und ungeordnete Achsen stehen getrennt', () => {
      const g = [...document.querySelectorAll('#st-x optgroup')].map(o => o.label);
      return (g.length === 2 && /Reihenfolge/.test(g[0]) && /Häufigkeit/.test(g[1])) || g.join(' | ');
    });
    t('keine Achse gibt es doppelt oder gar nicht', () => {
      const keys = [...document.querySelectorAll('#st-x option')].map(o => o.value);
      return (keys.length === ACHSEN.length && new Set(keys).size === keys.length)
          || keys.join(',');
    });
    t('Aufteilen gibt es als Ankreuzkaestchen', () => {
      const n = document.querySelectorAll('#st-teilen .chip').length;
      return n === TEILER.length || n;
    });
    t('das Kaestchen ist erst leer', () => {
      setzeFaenge([mk({ tiefe:2, koeder:'A' })]);
      alleFilterAus('tiefe'); renderStats();
      return document.querySelector('#st-teilen .chip').textContent.startsWith('☐') || 'schon angekreuzt';
    });
    /* ⚠️ "Aufteilen nach Koeder" hat Karl am 08.08. abbestellt -- es bleibt nur die
       Koederfarbe. Der Koeder ist als X-Achse weiter da; weg ist nur das Aufteilen. */
    t('Aufteilen nach Koeder gibt es nicht mehr', () =>
      !document.querySelector('[data-teilen="koeder"]') || 'Koeder steht noch zur Wahl');
    t('die Koederfarbe ist die einzige Wahl', () => {
      const n = document.querySelectorAll('#st-teilen .chip').length;
      return (n === 1 && !!document.querySelector('[data-teilen="farbe"]')) || ('es sind ' + n);
    });
    t('Antippen kreuzt an', () => {
      document.querySelector('[data-teilen="farbe"]').click();
      return (state.stats.teilen === 'farbe'
              && document.querySelector('[data-teilen="farbe"]').textContent.startsWith('☑'))
          || 'nicht angekreuzt';
    });
    t('nochmal antippen nimmt es zurueck', () => {
      document.querySelector('[data-teilen="farbe"]').click();
      return state.stats.teilen === '' || state.stats.teilen;
    });
    /* ⚠️ Gespeicherte Auswertungen aus der Zeit davor koennen teilen:'koeder' tragen.
       teilerVon liefert dafuer null -- gezeichnet wird dann eine einzelne Kurve statt
       einer aufgeteilten. Das ist der richtige Rueckfall, kein leeres Bild. */
    t('eine alte Auswertung mit teilen:koeder zeichnet trotzdem', () => {
      setzeFaenge([mk({ tiefe:2, koeder:'Wobbler' }), mk({ tiefe:5, koeder:'Spinner' })]);
      alleFilterAus('tiefe');
      const d = reihenBauen(statsRows(), achseVon('tiefe'), 'koeder');
      return (d && d.reihen.length === 1) || (d ? ('Reihen: ' + d.reihen.length) : 'nichts gezeichnet');
    });

    // ---- Gespeicherte Auswertungen ----
    const ohneAuswertungen = () => { state.auswertungen = []; localStorage.removeItem('angellog-auswertungen'); };
    /* ⚠️ Bis zum 08.08. gab es ueber dem Baukasten eine Liste "Meine Auswertungen".
       Karl hat sie abbestellt: bedient wird an der jeweiligen Statistik-Karte.
       Die Pruefungen unten fassen deshalb die Knoepfe an der Karte an, nicht die Liste. */
    t('die Liste ueber dem Baukasten gibt es nicht mehr', () => {
      ohneAuswertungen(); setzeFaenge([mk({ tiefe:2 })]); alleFilterAus('tiefe'); renderStats();
      return !document.querySelector('#stats-gespeichert') || 'Liste steht noch da';
    });
    t('ohne gespeicherte gibt es an der Karte nichts zu bedienen', () => {
      ohneAuswertungen(); setzeFaenge([mk({ tiefe:2 })]); alleFilterAus('tiefe'); renderStats();
      return !document.querySelector('#stats-body .ausw-bed') || 'Knoepfe ohne gespeicherte Auswertung';
    });
    t('speichern legt eine an', () => {
      ohneAuswertungen();
      setzeFaenge([mk({ art:'Hecht', tiefe:2, koeder:'Wobbler' })]);
      alleFilterAus('tiefe'); state.stats.art = 'Hecht'; state.stats.teilen = 'farbe';
      const merk = window.prompt; window.prompt = () => 'Hecht tief';
      auswertungSpeichern(); window.prompt = merk;
      return (state.auswertungen.length === 1 && state.auswertungen[0].name === 'Hecht tief')
          || JSON.stringify(state.auswertungen);
    });
    t('die gespeicherte merkt sich alle fuenf Angaben', () => {
      const a = state.auswertungen[0];
      return (a.art === 'Hecht' && a.x === 'tiefe' && a.teilen === 'farbe'
              && a.gewaesser === '') || JSON.stringify(a);
    });
    t('ihr Name steht als Titel ueber ihrer Karte', () => {
      renderStats();
      const titel = [...document.querySelectorAll('#stats-body h2')].map(h => h.textContent);
      return titel.includes('Hecht tief') || titel.join(' | ');
    });
    t('unter dem Namen steht in einem Satz, was drinsteckt', () => {
      renderStats();
      return document.querySelector('#stats-body').textContent.includes('Hecht über Wassertiefe')
          || 'Beschreibung fehlt an der Karte';
    });
    t('sie liegt im Speicher, nicht nur im Arbeitsspeicher', () => {
      const j = JSON.parse(localStorage.getItem('angellog-auswertungen') || '{}');
      return (j.liste && j.liste.length === 1 && j.updated > 0) || 'nicht gesichert';
    });
    t('laden stellt die Einstellungen wieder her', () => {
      alleFilterAus('wasser');           // erst alles verstellen
      auswertungLaden(state.auswertungen[0].id);
      const s = state.stats;
      return (s.art === 'Hecht' && s.x === 'tiefe' && s.teilen === 'farbe') || JSON.stringify(s);
    });
    t('die geladene sagt an ihrer Karte, dass sie oben liegt', () => {
      renderStats();
      return document.querySelector('#stats-body').textContent.includes('Liegt oben im Baukasten')
          || 'kein Hinweis an der geladenen Karte';
    });
    t('die geladene hat keinen Bearbeiten-Knopf', () => {
      // Sie liegt bereits im Baukasten -- ein Knopf, der nichts tut, gehoert nicht hin.
      renderStats();
      const b = [...document.querySelectorAll('#stats-body [data-bearb]')]
        .map(x => x.dataset.bearb);
      return !b.includes(state.stats.aktiv) || 'Bearbeiten an der bereits offenen';
    });
    t('der Baukasten sagt oben, welche offen ist', () => {
      renderStats();
      const kopf = document.querySelector('#st-offen');
      return (kopf.style.display !== 'none'
              && document.querySelector('#st-offen-name').textContent === 'Hecht tief')
          || ('Kopf: ' + kopf.style.display + ' / ' + document.querySelector('#st-offen-name').textContent);
    });
    t('Bearbeiten an einer anderen Karte laedt sie', () => {
      alleFilterAus('wasser'); state.stats.aktiv = null; renderStats();
      const b = document.querySelector('#stats-body [data-bearb]');
      if (!b) return 'kein Bearbeiten-Knopf da';
      b.click();
      return state.stats.x === 'tiefe' || state.stats.x;
    });
    t('"Neu anfangen" loest die Verbindung, ohne zu loeschen', () => {
      renderStats();
      const vorher = state.auswertungen.length;
      document.querySelector('#st-neu').click();
      return (state.stats.aktiv === null && state.auswertungen.length === vorher)
          || `aktiv=${state.stats.aktiv}, ${state.auswertungen.length} statt ${vorher}`;
    });
    t('dabei bleiben die Einstellungen stehen', () => {
      // Wer eine gespeicherte als Ausgangspunkt nimmt, will nicht alles neu einstellen.
      return state.stats.x === 'tiefe' || state.stats.x;
    });
    t('danach steht der Kopf des Baukastens wieder auf zu', () => {
      renderStats();
      return document.querySelector('#st-offen').style.display === 'none'
          || 'Kopf steht noch offen';
    });
    /* Fuer die folgenden Pruefungen wieder eine geladene herstellen.
       ⚠️ Abgesichert: eine Ausnahme AUSSERHALB eines t()-Blocks bricht den ganzen
       Durchlauf ab, und dann meldet der Rahmen nur "kein Ergebnis" statt eines Fehlers. */
    if (state.auswertungen[0]) auswertungLaden(state.auswertungen[0].id);
    t('"Aendern sichern" erscheint erst nach einer Aenderung', () => {
      const vorher = document.querySelector('#st-sichern').hidden;
      state.stats.x = 'wasser'; renderStats();
      const nachher = document.querySelector('#st-sichern').hidden;
      return (vorher === true && nachher === false) || `vorher ${vorher}, nachher ${nachher}`;
    });
    t('sichern uebernimmt die Aenderung', () => {
      auswertungSichern();
      return state.auswertungen[0].x === 'wasser' || state.auswertungen[0].x;
    });
    t('nach dem Sichern ist der Knopf wieder weg', () =>
      document.querySelector('#st-sichern').hidden === true || 'steht noch da');
    t('umbenennen aendert nur den Namen', () => {
      const merk = window.prompt; window.prompt = () => 'Neuer Name';
      auswertungUmbenennen(state.auswertungen[0].id); window.prompt = merk;
      const a = state.auswertungen[0];
      return (a.name === 'Neuer Name' && a.x === 'wasser') || JSON.stringify(a);
    });
    t('abgebrochenes Umbenennen laesst alles stehen', () => {
      const merk = window.prompt; window.prompt = () => null;
      auswertungUmbenennen(state.auswertungen[0].id); window.prompt = merk;
      return state.auswertungen[0].name === 'Neuer Name' || state.auswertungen[0].name;
    });
    t('"Als neue speichern" legt eine zweite an', () => {
      const merk = window.prompt; window.prompt = () => 'Zweite';
      auswertungSpeichern(); window.prompt = merk;
      return state.auswertungen.length === 2 || state.auswertungen.length;
    });
    t('loeschen fragt nach', () => {
      const merkC = window.confirm; let gefragt = false;
      window.confirm = () => { gefragt = true; return false; };
      auswertungLoeschen(state.auswertungen[0].id); window.confirm = merkC;
      return (gefragt && state.auswertungen.length === 2) || 'ohne Rueckfrage geloescht';
    });
    t('loeschen entfernt genau eine', () => {
      const merkC = window.confirm; window.confirm = () => true;
      const id = state.auswertungen[0].id;
      auswertungLoeschen(id); window.confirm = merkC;
      return (state.auswertungen.length === 1 && state.auswertungen[0].id !== id)
          || state.auswertungen.length;
    });
    t('die geloeschte ist auch aus dem Speicher raus', () => {
      const j = JSON.parse(localStorage.getItem('angellog-auswertungen') || '{}');
      return j.liste.length === 1 || j.liste.length;
    });
    t('ein Name mit Anfuehrungszeichen zerreisst nichts', () => {
      ohneAuswertungen();
      const merk = window.prompt; window.prompt = () => 'Der "gute" Platz';
      setzeFaenge([mk({ tiefe:2 })]); alleFilterAus('tiefe');
      auswertungSpeichern(); window.prompt = merk;
      renderStats();
      const titel = [...document.querySelectorAll('#stats-body h2')].map(h => h.textContent);
      return titel.includes('Der "gute" Platz') || titel.join(' | ');
    });
    t('ein Koedername mit spitzen Klammern zerreisst nichts', () => {
      // Zwei Farben, damit es die Legende ueberhaupt gibt — bei einer einzelnen
      // Reihe steht der Name nirgends im Bild.
      ohneAuswertungen();
      setzeFaenge([mk({ tiefe:2, farben:['<b>Wobbler</b>'] }), mk({ tiefe:5, farben:['Spinner'] })]);
      alleFilterAus('tiefe'); state.stats.teilen = 'farbe';
      const h = einBild();
      return (!h.includes('<b>Wobbler</b>') && h.includes('&lt;b&gt;Wobbler')) || 'ungefiltert eingebaut';
    });
    ohneAuswertungen();
  
  } else {
    out.push('--   Statistik-Pruefungen uebersprungen (Reiter ist nicht in dieser Fassung)');
  }

  // ==================== Konto & Cloud-Sync ====================
  // Netz und Datenbank werden ersetzt. Geprueft wird der Ablauf selbst:
  // was hochgeht, was heruntergeholt wird, wer bei einem Konflikt gewinnt
  // und ob ein geloeschter Fang geloescht bleibt. IndexedDB laeuft unter
  // file:// nicht zuverlaessig, deshalb ein Speicher im Arbeitsspeicher.
  const asyncTests = [];
  const ta = (name, fn) => asyncTests.push([name, fn]);

  let fakeDB, fakeGrab;
  function sandbox(faenge, graeber){
    fakeDB   = new Map((faenge  || []).map(c => [c.id, c]));
    fakeGrab = new Map((graeber || []).map(g => [g.id, g]));
    state.catches = [...fakeDB.values()];
    putCatch = async (rec, vomServer) => {
      if (!vomServer || rec.updated == null) rec.updated = Date.now();
      fakeDB.set(rec.id, rec); fakeGrab.delete(rec.id); return rec;
    };
    /* cloudMerken() liest den Speicher, nicht state.catches -- sonst schriebe es
       eine veraltete Fassung zurueck. Im Rahmen ist der Speicher fakeDB.

       ⚠️ **Und der Speicher gibt KOPIEN zurueck, keine Verweise.** Genau so verhaelt
       sich IndexedDB: was dort herauskommt, ist frisch aufgebaut und hat mit dem
       Objekt im Arbeitsspeicher nichts mehr zu tun.
       Hier stand `[...fakeDB.values()]` -- dieselben Objekte, die auch in
       `state.catches` liegen. Damit war jede Aenderung, die cloudMerken() im
       "Speicher" machte, sofort auch im Arbeitsspeicher zu sehen, und die Pruefung
       "geht danach nicht ein zweites Mal hoch" blieb gruen, **obwohl derselbe Fang in
       der echten App bei jedem Abgleich erneut hochging**. Karls Meldung vom
       13.08.2026: „jedes mal steht da halt wird hochgeladen ... das tag verschwindet
       nicht." Ein Rahmen, der grosszuegiger ist als die Wirklichkeit, prueft nichts. */
    allCatches   = async () => [...fakeDB.values()].map(c => ({ ...c, photos: [...(c.photos || [])] }));
    removeCatch  = async (id) => { fakeDB.delete(id); fakeGrab.set(id, { id, updated: Date.now(), gemeldet: false }); };
    allGraeber   = async () => [...fakeGrab.values()];
    grabMarkieren = async (ids) => ids.forEach(id => fakeGrab.set(id, { ...fakeGrab.get(id), id, gemeldet: true }));
    reload = async () => { state.catches = [...fakeDB.values()]; };
    renderList = () => {};
  }
  const mkC = (id, updated, extra) => Object.assign({ id, updated, entwurf: false, art: 'Hecht', photos: [] }, extra || {});

  // ---- Fehlermeldungen beim Anmelden ----
  t('Schon registriert wird erklaert', () =>
    /schon ein Konto/.test(authFehler({ msg: 'User already registered' }, 'x')) || authFehler({ msg: 'User already registered' }, 'x'));
  t('Falsches Passwort wird erklaert', () =>
    /stimmt nicht/.test(authFehler({ error_description: 'Invalid login credentials' }, 'x')) || 'kein Text');
  t('Zu kurzes Passwort wird erklaert', () =>
    /6 Zeichen/.test(authFehler({ msg: 'Password should be at least 6 characters' }, 'x')) || 'kein Text');
  t('Unbekannter Fehler faellt auf den Standard zurueck', () =>
    authFehler({}, 'Standard') === 'Standard' || authFehler({}, 'Standard'));

  // ---- Konfiguration ----
  t('Cloud ist konfiguriert', () => cloudAn() === true || 'SUPA_URL/SUPA_KEY fehlen');
  t('Nur der oeffentliche Schluessel steht im Quelltext', () =>
    (!/sb_secret_/.test(SUPA_KEY) && !/service_role/.test(SUPA_KEY)) || 'GEHEIMER SCHLUESSEL IM QUELLTEXT');
  t('Konto-Kasten ist sichtbar', () => { konto = null; renderKonto(); return document.querySelector('#konto').hidden === false || 'unsichtbar'; });
  // Das Anmeldeformular sitzt seit dem 03.08. im Anmelde-Schirm, nicht mehr in
  // den Einstellungen. Dort steht nur noch ein Weg zurueck zum Schirm.
  t('In den Einstellungen steht kein Anmeldeformular mehr', () =>
    (!document.querySelector('#k-mail') && !!document.querySelector('#k-gate')) || 'altes Formular noch da');
  t('Ohne Anmeldung sagt der Sicherungstext, dass nichts abgeglichen wird', () =>
    /Nicht angemeldet/.test(document.querySelector('#sicherung-text').textContent)
      || document.querySelector('#sicherung-text').textContent.slice(0, 60));
  t('Angemeldet sagt der Sicherungstext etwas anderes', () => {
    konto = { email: 'x@y.z', access_token: 'tok' }; renderKonto();
    const s = document.querySelector('#sicherung-text').textContent;
    konto = null; renderKonto();
    return /und.*in deinem Konto/s.test(s) || s.slice(0, 60);
  });
  t('Ohne Konto laeuft syncJetzt ins Leere', () => { konto = null; syncJetzt(true); return true; });

  // ⚠️ Der neue sb_publishable_-Schluessel ist kein JWT. Steht er im
  // Authorization-Kopf, weist der Server die Anfrage ab.
  t('Ohne Sitzung kein Authorization-Kopf', () => {
    konto = null;
    return (kopf(true).Authorization === undefined && kopf(true).apikey === SUPA_KEY) || JSON.stringify(kopf(true));
  });
  t('Mit Sitzung steht der Sitzungs-Token drin', () => {
    konto = { access_token: 'TOKEN123' };
    const h = kopf(true); konto = null;
    return h.Authorization === 'Bearer TOKEN123' || h.Authorization;
  });
  t('Der Schluessel landet nie im Authorization-Kopf', () => {
    konto = { access_token: 'TOKEN123' };
    const a = kopf(false).Authorization, b = kopf(true).Authorization;
    konto = null;
    return (a === undefined && !String(b).includes(SUPA_KEY)) || `${a} / ${b}`;
  });

  // ---- Fotobudget ----
  t('Budget ist gesetzt und plausibel', () => (FOTO_BUDGET > 50e3 && FOTO_BUDGET < 400e3) || FOTO_BUDGET);
  t('Stufen werden kleiner', () => {
    for (let i = 1; i < STUFEN.length; i++)
      if (STUFEN[i][0] >= STUFEN[i-1][0] || STUFEN[i][1] >= STUFEN[i-1][1]) return 'Stufe ' + i + ' ist nicht kleiner';
    return true;
  });

  // ---- Hochladen ----
  ta('Nur Geaendertes geht hoch', async () => {
    // `cloud` = die Fassung, die nachweislich im Konto liegt. b ist damit durch, a nicht.
    sandbox([mkC('a', 5000, { cloud: 1000 }), mkC('b', 50, { cloud: 50 })]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return (raus.length === 1 && raus[0].id === 'a') || JSON.stringify(raus.map(r => r.id));
  });
  ta('Ein Fang ohne cloud-Vermerk geht hoch', async () => {
    /* Der Normalfall nach dem Umbau vom 10.08.2026 und zugleich die Wanderung der
       Altbestaende: wer kein `cloud` traegt, war nachweislich noch nie oben. Frueher
       brauchte es dafuer eine einmalige Ruecksetzung des Geraetestandes. */
    sandbox([mkC('alt', 50)]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return (raus.length === 1 && raus[0].id === 'alt') || JSON.stringify(raus.map(r => r.id));
  });
  ta('cloud faehrt nicht mit in die Cloud', async () => {
    /* `cloud` ist eine Notiz dieses Geraets ueber dieses Geraet. Ginge sie mit hoch,
       zoege das andere Geraet sie herunter und behauptete etwas ueber einen Speicher,
       den sie nie gesehen hat. */
    sandbox([mkC('a', 5000, { cloud: 1000 })]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return (raus[0].daten.cloud === undefined) || ('cloud steht in daten: ' + raus[0].daten.cloud);
  });
  ta('Nach dem Hochladen traegt der Fang seine Fassung', async () => {
    sandbox([mkC('a', 5000)]);
    zeilenSchreiben = async () => {};
    await hochladen();
    return (fakeDB.get('a').cloud === 5000) || ('cloud ist ' + fakeDB.get('a').cloud);
  });
  ta('und geht danach nicht ein zweites Mal hoch', async () => {
    sandbox([mkC('a', 5000)]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    await hochladen();
    return (raus.length === 0) || ('zweiter Lauf schickte ' + JSON.stringify(raus.map(r => r.id)));
  });
  /* ⚠️ **Karls Meldung vom 13.08.2026, wortgetreu nachgestellt:** „habe gerade einen auf
     dem handy bei dem steht nur hier dran, der ist aber auf meinem pc, und wenn ich auf
     jetzt abgleichen gehe steht jedes mal dran ein fang geht hoch, aber das tag
     verschwindet nicht."

     Der Kern ist die **Trennung von Arbeitsspeicher und Speicher**. cloudMerken()
     schreibt seinen Vermerk in den Speicher; solange hochladen() die Liste im
     Arbeitsspeicher durchging und nach einem reinen Hochladen nichts neu gelesen wurde,
     sah der naechste Lauf denselben Fang erneut als ungesichert. Mit Fotos, bei jedem
     Antippen, unbegrenzt oft.

     ⚠️ Deshalb wird hier `state.catches` **absichtlich veraltet gehalten** -- kein
     reload() zwischen den Laeufen. Genau so stand es in der App. */
  ta('ein hochgeladener Fang geht auch dann nicht wieder hoch, wenn niemand neu liest', async () => {
    sandbox([mkC('a', 5000)]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    // Der Arbeitsspeicher bleibt stehen, wie er war -- das ist der ganze Punkt.
    await hochladen();
    return (raus.length === 0)
        || ('zweiter Lauf schickte ' + JSON.stringify(raus.map(r => r.id))
            + ' -- die Schleife von Karls Meldung ist wieder da');
  });
  ta('und danach traegt er im Speicher seinen Vermerk', async () => {
    sandbox([mkC('a', 5000)]);
    zeilenSchreiben = async () => {};
    await hochladen();
    const rec = (await allCatches()).find(c => c.id === 'a');
    return (rec.cloud === 5000) || ('cloud ist ' + rec.cloud);
  });
  /* Die sichtbare Haelfte: das Schild haengt an `state.catches`. Bleibt der
     Arbeitsspeicher stehen, bleibt das Schild stehen -- deshalb muss nach einem reinen
     Hochladen neu gelesen werden, nicht nur neu gezeichnet. */
  ta('nach dem Auffrischen ist das Schild weg', async () => {
    sandbox([mkC('a', 5000)]);
    zeilenSchreiben = async () => {};
    await hochladen();
    const vorher = nichtGesichert().length;      // veralteter Arbeitsspeicher: noch offen
    await reload();
    const nachher = nichtGesichert().length;
    return (vorher === 1 && nachher === 0)
        || ('vor dem Auffrischen ' + vorher + ', danach ' + nachher);
  });

  ta('Entwuerfe gehen mit hoch', async () => {
    /* ⚠️ Hier stand bis zum 10.08.2026 das Gegenteil ("Entwuerfe bleiben lokal").
       Karls Ansage: "5 entwuerfe die sollen bitte auch synchronisiert werden."
       Ein Entwurf ist eine halbe Sache, aber getippte Arbeit -- und die nur auf
       einem Geraet liegen zu lassen war schon bei den Faengen der Fehler. */
    sandbox([mkC('a', 5000, { entwurf: true }), mkC('b', 5000)]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    const ids = raus.map(r => r.id).sort();
    return (ids.length === 2 && ids[0] === 'a' && ids[1] === 'b') || JSON.stringify(ids);
  });
  ta('und der Entwurf bleibt drueben ein Entwurf', async () => {
    // Sonst taucht er auf dem zweiten Geraet als fertiger Fang auf und faelscht
    // jede Auswertung -- Entwuerfe zaehlen nirgends mit.
    sandbox([mkC('a', 5000, { entwurf: true })]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return (raus[0].daten.entwurf === true) || ('entwurf ist ' + raus[0].daten.entwurf);
  });
  ta('Geloeschtes geht als Grabstein hoch', async () => {
    sandbox([], [{ id: 'weg', updated: 9000, gemeldet: false }]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    const g = raus.find(r => r.id === 'weg');
    return (g && g.geloescht === true && g.daten === null) || JSON.stringify(raus);
  });
  ta('Ein gemeldeter Grabstein geht nicht nochmal hoch', async () => {
    sandbox([], [{ id: 'weg', updated: 9000, gemeldet: false }]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    await hochladen();
    return (raus.length === 0) || 'zweiter Lauf schickte ' + raus.length;
  });

  // ---- Herunterladen ----
  const antwort = daten => ({ ok: true, json: async () => daten });
  ta('Neuer Fang vom Server kommt an', async () => {
    sandbox([]);
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'neu', updated: 100, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'neu', updated: 100, geloescht: false, daten: { art: 'Zander' }, fotos: [] }]);
    await herunterladen();
    return (fakeDB.has('neu') && fakeDB.get('neu').art === 'Zander') || 'fehlt';
  });
  ta('Aeltere Fassung vom Server ueberschreibt nicht', async () => {
    sandbox([mkC('a', 9000, { art: 'Wels' })]);
    let vollGeholt = false;
    api = async pfad => { if (!pfad.includes('select=id,')) vollGeholt = true;
      return antwort([{ id: 'a', updated: 100, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }]); };
    await herunterladen();
    return (fakeDB.get('a').art === 'Wels' && !vollGeholt) || 'lokale Fassung wurde ueberschrieben';
  });
  ta('Juengere Fassung vom Server gewinnt', async () => {
    sandbox([mkC('a', 100, { art: 'Wels' })]);
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'a', updated: 9000, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'a', updated: 9000, geloescht: false, daten: { art: 'Hecht' }, fotos: [] }]);
    await herunterladen();
    return (fakeDB.get('a').art === 'Hecht') || fakeDB.get('a').art;
  });
  ta('Geholter Fang behaelt sein updated', async () => {
    sandbox([]);
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'n', updated: 4242, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'n', updated: 4242, geloescht: false, daten: { art: 'Aal' }, fotos: [] }]);
    await herunterladen();
    return (fakeDB.get('n').updated === 4242) || 'updated wurde auf ' + fakeDB.get('n').updated + ' gesetzt';
  });
  /* ============ Karls Meldung vom 10.08.2026 ============
     "bei dem einen, der neu ist, steht nur auf diesem Geraet dabei. Das stimmt aber
     nicht. Der ist auch auf meinem Handy."

     Der Fang war gerade heruntergeladen worden. Er trug die Uhr des Handys, und die
     war neuer als das letzte Hochladen des PCs -- also galt er als ungesichert. Ein
     Stand fuer das ganze Geraet kann nicht ausdruecken, dass etwas von drueben kam.

     ⚠️ Die zweite Pruefung ist die teure Haelfte: derselbe Irrtum hat den Fang auch
     samt Fotos sofort wieder hochgeschoben, bei jedem Abgleich aufs Neue. */
  ta('Ein geholter Fang weiss, dass er im Konto liegt', async () => {
    sandbox([]);
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'n', updated: 4242, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'n', updated: 4242, geloescht: false, daten: { art: 'Aal' }, fotos: [] }]);
    await herunterladen();
    return (fakeDB.get('n').cloud === 4242) || ('cloud ist ' + fakeDB.get('n').cloud);
  });
  ta('und traegt deshalb nicht "nur auf diesem Geraet"', async () => {
    sandbox([]);
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'n', updated: 4242, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'n', updated: 4242, geloescht: false, daten: { art: 'Aal' }, fotos: [] }]);
    await herunterladen();
    state.catches = [...fakeDB.values()];
    const n = nichtGesichert().length;
    return (n === 0) || (n + ' Faenge gelten als ungesichert');
  });
  ta('und wird nicht sofort wieder hochgeschoben', async () => {
    sandbox([]);
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'n', updated: 4242, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'n', updated: 4242, geloescht: false, daten: { art: 'Aal' }, fotos: [] }]);
    await herunterladen();
    state.catches = [...fakeDB.values()];
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return (raus.length === 0) || ('zurueckgeschoben: ' + JSON.stringify(raus.map(r => r.id)));
  });
  ta('Grabstein vom Server loescht lokal', async () => {
    sandbox([mkC('weg', 100)]);
    api = async () => antwort([{ id: 'weg', updated: 9000, geloescht: true, serverzeit: '2026-08-03T10:00:00Z' }]);
    await herunterladen();
    return (!fakeDB.has('weg')) || 'Fang ist noch da';
  });
  ta('Grabstein fuer Unbekanntes tut nichts', async () => {
    sandbox([mkC('a', 100)]);
    api = async () => antwort([{ id: 'nie-gehabt', updated: 9000, geloescht: true, serverzeit: '2026-08-03T10:00:00Z' }]);
    await herunterladen();
    return (fakeDB.size === 1 && fakeDB.has('a')) || 'Bestand veraendert';
  });
  /* ====== Der Herunterlade-Stand ist abgeschafft (11.08.2026) ======
     Hier standen zwei Pruefungen, die genau das Gegenteil festhielten:
     "Sync-Stand wandert mit" und "Nichts Neues laesst den Stand stehen".
     Sie waren richtig, solange es einen Stand gab -- und der war der letzte
     Marker dieser Bauart in der App.

     ⚠️ Dieselbe Bauart hat innerhalb von drei Tagen dreimal Loecher gehabt
     (08.08. Push-Stand auf die Uhr gesetzt, 10.08. Push-Stand kann "kam von
     drueben" nicht ausdruecken, 09.08. Herunterlade-Stand laeuft nur vorwaerts).
     Der Fehler ist nicht der jeweilige Rechenfehler, sondern dass ein Stand
     eine Behauptung ist, die falsch sein kann, ohne dass etwas auffaellt.
     Jetzt wird nachgesehen statt behauptet. */
  ta('Der Abgleich merkt sich keinen Stand mehr', async () => {
    sandbox([]);
    localStorage.setItem('angellog-sync', '2026-08-01T00:00:00Z');
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'x', updated: 1, geloescht: true }])
      : antwort([]);
    await herunterladen();
    return (localStorage.getItem('angellog-sync') === '2026-08-01T00:00:00Z')
        || ('der Stand wurde angefasst: ' + localStorage.getItem('angellog-sync'));
  });
  ta('und fragt nicht mehr "was ist seit gestern passiert?"', async () => {
    /* ⚠️ Das ist die Gegenprobe zum Loch vom 09.08.: stand der Stand einmal zu
       weit vorne, kam nie wieder etwas herunter -- fuer immer und ohne Anzeichen.
       Hier steht er absichtlich in der Zukunft. Wer die Frage nicht mehr stellt,
       kann sie auch nicht falsch stellen. */
    sandbox([]);
    localStorage.setItem('angellog-sync', '2999-01-01T00:00:00Z');
    const pfade = [];
    api = async pfad => { pfade.push(pfad);
      return pfad.includes('select=id,')
        ? antwort([{ id: 'alt', updated: 100, geloescht: false }])
        : antwort([{ id: 'alt', updated: 100, geloescht: false, daten: { art: 'Aal' }, fotos: [] }]); };
    await herunterladen();
    if (pfade.some(p => /serverzeit/.test(p))) return 'fragt weiter nach serverzeit: ' + pfade[0];
    return fakeDB.has('alt') || 'der Fang im Konto kam nicht herunter';
  });
  ta('Ein voller Block wird weitergeblaettert', async () => {
    /* ⚠️ Ohne das haette der Umbau ein neues stilles Loch: der Server gibt je
       Anfrage hoechstens `max-rows` Zeilen zurueck (bei Supabase ab Werk 1.000)
       und sagt nicht dazu, dass er gekuerzt hat. Wer die erste Seite fuer den
       ganzen Bestand haelt, sieht den Rest nie -- genau die Sorte Blindheit,
       gegen die der ganze Umbau geht. */
    const seite1 = Array.from({ length: 500 }, (_, i) =>
      ({ id: 'a' + String(i).padStart(3, '0'), updated: 100, geloescht: false }));
    let ruf = 0;
    api = async () => { ruf++;
      return antwort(ruf === 1 ? seite1 : [{ id: 'b', updated: 100, geloescht: false }]); };
    const alle = await kopfzeilenHolen();
    return (ruf === 2 && alle.length === 501) || (ruf + ' Aufrufe, ' + alle.length + ' Kopfzeilen');
  });
  ta('und zwar ueber die letzte id, nicht ueber offset', async () => {
    /* ⚠️ Mit `offset` verschiebt sich das Fenster, wenn waehrend des Blaetterns
       eine Zeile dazukommt -- dann rutscht genau ein Fang zwischen zwei Seiten
       hindurch und fehlt, ohne dass es auffaellt. */
    const seite1 = Array.from({ length: 500 }, (_, i) =>
      ({ id: 'a' + String(i).padStart(3, '0'), updated: 100, geloescht: false }));
    let ruf = 0, zweiter = '';
    api = async pfad => { ruf++;
      if (ruf === 1) return antwort(seite1);
      zweiter = pfad;
      return antwort([]); };
    await kopfzeilenHolen();
    return (/id=gt\.a499/.test(zweiter) && !/offset/.test(zweiter)) || ('zweite Anfrage: ' + zweiter);
  });
  ta('Eine kurze Seite loest keine zweite Anfrage aus', async () => {
    // Sonst kostete jeder Abgleich eine Anfrage mehr als noetig -- bei acht Faengen.
    let ruf = 0;
    api = async () => { ruf++; return antwort([{ id: 'a', updated: 1, geloescht: false }]); };
    await kopfzeilenHolen();
    return (ruf === 1) || (ruf + ' Aufrufe fuer einen einzigen Fang');
  });
  ta('Fehler vom Server wird gemeldet, nicht verschluckt', async () => {
    sandbox([]);
    api = async () => ({ ok: false, status: 500, json: async () => ({}) });
    try { await herunterladen(); return 'kein Fehler geworfen'; }
    catch (e) { return /500/.test(e.message) || e.message; }
  });
  ta('Grosse Mengen werden gestueckelt geholt', async () => {
    const viele = Array.from({ length: 45 }, (_, i) =>
      ({ id: 'id' + i, updated: 100, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }));
    sandbox([]);
    let vollAufrufe = 0;
    api = async pfad => {
      if (pfad.includes('select=id,')) return antwort(viele);
      vollAufrufe++;
      const ids = decodeURIComponent(pfad.split('id=in.(')[1].slice(0, -1)).split(',');
      return antwort(ids.map(id => ({ id, updated: 100, geloescht: false, daten: { art: 'X' }, fotos: [] })));
    };
    await herunterladen();
    return (vollAufrufe === 3 && fakeDB.size === 45) || vollAufrufe + ' Aufrufe, ' + fakeDB.size + ' Faenge';
  });

  // ---- Fotos verkleinern ----
  ta('Ein grosses Foto landet unter dem Budget', async () => {
    const c = document.createElement('canvas');
    c.width = 2400; c.height = 1600;
    const g = c.getContext('2d');
    const img = g.createImageData(2400, 1600);
    for (let i = 0; i < img.data.length; i += 4){
      img.data[i] = (i * 7) % 255; img.data[i+1] = (i * 13) % 255;
      img.data[i+2] = (i * 29) % 255; img.data[i+3] = 255;
    }
    g.putImageData(img, 0, 0);
    const gross = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.95));
    if (gross.size <= FOTO_BUDGET) return 'Testbild war schon klein genug (' + gross.size + ')';
    const klein = await fotoFuerCloud(gross);
    return (klein && klein.size <= FOTO_BUDGET) || 'blieb bei ' + (klein && klein.size);
  });
  ta('Ein kleines Foto wird nicht angefasst', async () => {
    const c = document.createElement('canvas');
    c.width = 40; c.height = 40;
    c.getContext('2d').fillRect(0, 0, 40, 40);
    const klein = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.6));
    return ((await fotoFuerCloud(klein)) === klein) || 'wurde neu gerechnet';
  });
  ta('Unlesbares Format wird ausgelassen, nicht hochgeladen', async () => {
    const kaputt = new Blob([new Uint8Array(400000)], { type: 'image/heic' });
    return ((await fotoFuerCloud(kaputt)) === null) || 'kam etwas zurueck';
  });

  // ---- App-Icon ----
  // Karls Ansage vom 07.08. (Bild auf Discord): "Nimm das linke als app icon."
  const bildLaedt = (pfad) => new Promise(fertig => {
    const i = new Image();
    i.onload  = () => fertig({ ok: true, w: i.naturalWidth, h: i.naturalHeight });
    i.onerror = () => fertig({ ok: false });
    i.src = pfad;
  });
  const manifest = async () => await (await fetch('manifest.webmanifest')).json();

  ta('das Icon liegt in 192 und 512', async () => {
    const a = await bildLaedt('icon-192.png'), b = await bildLaedt('icon-512.png');
    return (a.ok && a.w === 192 && a.h === 192 && b.ok && b.w === 512 && b.h === 512)
        || JSON.stringify([a, b]);
  });
  // Android schneidet aus einem maskable Icon einen Kreis heraus. Ein Icon mit
  // "any maskable" muesste sein Motiv in der inneren 80 %-Zone halten -- dann ist
  // es ueberall zu klein. Deshalb zwei getrennte Dateien.
  ta('maskable ist ein eigenes Icon, kein doppelter Zweck', async () => {
    const m = await manifest();
    const zwecke = m.icons.map(i => i.purpose || 'any');
    const doppelt = zwecke.filter(p => p.includes('any') && p.includes('maskable'));
    return (doppelt.length === 0 && zwecke.includes('maskable')) || zwecke.join(' | ');
  });
  ta('das maskable Icon ist da', async () => {
    const r = await bildLaedt('icon-maskable-512.png');
    return (r.ok && r.w === 512) || JSON.stringify(r);
  });
  ta('jedes Icon im Manifest gibt es auch wirklich', async () => {
    const m = await manifest();
    for (const i of m.icons){
      const r = await bildLaedt(i.src);
      if (!r.ok) return 'fehlt: ' + i.src;
    }
    return true;
  });
  ta('das alte gruene Fisch-Symbol ist ueberall raus', async () => {
    const m = await manifest();
    const imManifest = m.icons.some(i => /\.svg$/.test(i.src));
    const imKopf = !!document.querySelector('link[rel="icon"][href$=".svg"]');
    return (!imManifest && !imKopf) || `Manifest ${imManifest}, Kopf ${imKopf}`;
  });
  ta('der Reiter im Browser hat ein Symbol', async () => {
    const l = document.querySelector('link[rel="icon"]');
    if (!l) return 'kein rel=icon im Kopf';
    const r = await bildLaedt(l.getAttribute('href'));
    return r.ok || ('laedt nicht: ' + l.getAttribute('href'));
  });
  ta('das Icon passt farblich zum Start der App', async () => {
    const m = await manifest();
    const meta = document.querySelector('meta[name="theme-color"]').content.toLowerCase();
    // Der Grund des Icons ist dieselbe Farbe -- sonst blitzt beim Start ein
    // andersfarbiges Rechteck auf.
    return (m.background_color.toLowerCase() === meta) || `${m.background_color} vs ${meta}`;
  });

  // ---- Angelzeit und Auswertungen am Konto ----
  // Bis zum 07.08.2026 lag die Angelzeit nur im localStorage. Gerettet hat sie
  // einzig das Backup, und das ist am 04.08. ausgebaut worden — sie war damit
  // das Einzige in der App, das ein Geraetewechsel wirklich gekostet haette.
  const zeitSetzen = (gesamt, updated, start) =>
    localStorage.setItem('angellog-zeit', JSON.stringify({ gesamt, updated, start: start || null }));
  // Das Netz antwortet mit dem, was drueben liegt; Schreibversuche werden nur notiert.
  const werteNetz = (drueben) => {
    const notiert = { geschrieben: null, geloescht: null };
    api = async (pfad, opt) => {
      if (!opt || !opt.method) return antwort(drueben);
      if (opt.method === 'DELETE'){ notiert.geloescht = pfad; return antwort(null); }
      notiert.geschrieben = JSON.parse(opt.body);
      return antwort(null);
    };
    return notiert;
  };

  ta('geaenderte Angelzeit geht hoch', async () => {
    zeitSetzen(3600000, 5000);
    const n = werteNetz([]);
    await werteAbgleichen();
    const z = (n.geschrieben || []).find(r => r.schluessel === 'zeit');
    return (z && z.wert.gesamt === 3600000) || JSON.stringify(n.geschrieben);
  });
  ta('nie geaenderte Angelzeit geht nicht hoch', async () => {
    zeitSetzen(0, 0);
    localStorage.removeItem('angellog-auswertungen'); state.auswertungen = [];
    const n = werteNetz([]);
    await werteAbgleichen();
    return n.geschrieben === null || JSON.stringify(n.geschrieben);
  });
  /* ⚠️ Karls Meldung vom 08.08.: "angelzeit gesamt ist nicht syncronisiert auf
     meinen geraeten". Ursache war nicht das Netz und nicht die Tabelle, sondern
     die Bedingung hier: ein Wert mit `updated: 0` galt als "nichts zu melden" und
     ging nie hoch. Genau das trifft aber auf jede Angelzeit zu, die vor dem
     07.08. entstanden ist -- sie lag im localStorage, lange bevor es ein
     `updated` gab. Das Geraet mit der Zeit lud sie nie hoch, das andere sah nie
     etwas, und weil jeder selbsttaetige Abgleich still laeuft, meldete niemand
     einen Fehler. */
  ta('eine Angelzeit ohne Stempel geht trotzdem hoch', async () => {
    zeitSetzen(7200000, 0);          // zwei Stunden, nie "geaendert" worden
    localStorage.removeItem('angellog-auswertungen'); state.auswertungen = [];
    const n = werteNetz([]);
    await werteAbgleichen();
    const z = (n.geschrieben || []).find(r => r.schluessel === 'zeit');
    return (z && z.wert.gesamt === 7200000) || JSON.stringify(n.geschrieben);
  });
  ta('und sie bekommt dabei einen echten Stempel', async () => {
    zeitSetzen(7200000, 0);
    const n = werteNetz([]);
    await werteAbgleichen();
    const z = (n.geschrieben || []).find(r => r.schluessel === 'zeit');
    // Ohne Stempel gaelte sie drueben sofort wieder als aelteste und der naechste
    // Abgleich wuerde sie mit irgendetwas ueberschreiben.
    return (z && z.updated > 1.7e12) || JSON.stringify(z);
  });
  ta('der Stempel steht danach auch lokal', async () => {
    zeitSetzen(7200000, 0);
    werteNetz([]);
    await werteAbgleichen();
    // Bliebe lokal die 0 stehen, liefe beim naechsten Durchgang dasselbe nochmal.
    return zeitLesen().updated > 1.7e12 || zeitLesen().updated;
  });
  ta('liegt drueben schon etwas, wird nichts gestempelt', async () => {
    zeitSetzen(7200000, 0);
    werteNetz([{ schluessel: 'zeit', updated: 9000, wert: { gesamt: 3600000 } }]);
    await werteAbgleichen();
    // Drueben ist etwas -> der Server gewinnt, hier wird nicht heimlich hochgestempelt.
    return zeitLesen().gesamt === 3600000 || zeitLesen().gesamt;
  });
  ta('juengere Angelzeit vom Server gewinnt', async () => {
    zeitSetzen(3600000, 5000);
    werteNetz([{ schluessel: 'zeit', updated: 9000, wert: { gesamt: 7200000 } }]);
    await werteAbgleichen();
    return zeitLesen().gesamt === 7200000 || zeitLesen().gesamt;
  });
  ta('der uebernommene Wert behaelt sein updated', async () => {
    zeitSetzen(3600000, 5000);
    werteNetz([{ schluessel: 'zeit', updated: 9000, wert: { gesamt: 7200000 } }]);
    await werteAbgleichen();
    // Bekaeme er ein frisches updated, ginge er beim naechsten Mal wieder hoch.
    return zeitLesen().updated === 9000 || zeitLesen().updated;
  });
  ta('aeltere Angelzeit vom Server ueberschreibt nicht', async () => {
    zeitSetzen(3600000, 9000);
    werteNetz([{ schluessel: 'zeit', updated: 5000, wert: { gesamt: 7200000 } }]);
    await werteAbgleichen();
    return zeitLesen().gesamt === 3600000 || zeitLesen().gesamt;
  });
  // ⚠️ Der Punkt, an dem "die groessere Zahl gewinnt" gescheitert waere: eine
  // Korrektur nach unten muss sich durchsetzen, sonst kaeme "Gesamtzeit direkt
  // setzen" nie gegen einen alten hohen Wert an.
  ta('eine Korrektur nach unten setzt sich durch', async () => {
    zeitSetzen(40 * 3600000, 5000);
    zeitSchreiben({ gesamt: 10 * 3600000, start: null });     // Karl zieht gerade
    const n = werteNetz([{ schluessel: 'zeit', updated: 5000, wert: { gesamt: 40 * 3600000 } }]);
    await werteAbgleichen();
    const z = (n.geschrieben || []).find(r => r.schluessel === 'zeit');
    return (zeitLesen().gesamt === 10 * 3600000 && z && z.wert.gesamt === 10 * 3600000)
        || `lokal ${zeitLesen().gesamt}, hoch ${JSON.stringify(n.geschrieben)}`;
  });
  ta('der laufende Ansitz geht nicht in die Cloud', async () => {
    zeitSetzen(3600000, 5000, 1234567);
    const n = werteNetz([]);
    await werteAbgleichen();
    const z = (n.geschrieben || []).find(r => r.schluessel === 'zeit');
    return (z && !('start' in z.wert)) || JSON.stringify(z);
  });
  ta('der laufende Ansitz ueberlebt einen Wert vom Server', async () => {
    zeitSetzen(3600000, 5000, 1234567);
    werteNetz([{ schluessel: 'zeit', updated: 9000, wert: { gesamt: 7200000 } }]);
    await werteAbgleichen();
    return zeitLesen().start === 1234567 || zeitLesen().start;
  });
  ta('Start und Stopp allein aendern das updated nicht', async () => {
    zeitSetzen(3600000, 5000);
    zeitSchreiben({ gesamt: 3600000, start: Date.now() });   // Start: gesamt bleibt
    return zeitLesen().updated === 5000 || zeitLesen().updated;
  });
  ta('gespeicherte Auswertungen gehen mit hoch', async () => {
    localStorage.setItem('angellog-auswertungen', JSON.stringify({
      liste: [{ id:'x', name:'A', art:'', x:'tiefe', teilen:'', gewaesser:'', zeit:'alles' }], updated: 7000 }));
    state.auswertungen = auswertungenLesen().liste;
    zeitSetzen(0, 0);
    const n = werteNetz([]);
    await werteAbgleichen();
    const a = (n.geschrieben || []).find(r => r.schluessel === 'auswertungen');
    return (a && a.wert.liste.length === 1) || JSON.stringify(n.geschrieben);
  });
  ta('Auswertungen vom Server kommen an', async () => {
    localStorage.setItem('angellog-auswertungen', JSON.stringify({ liste: [], updated: 100 }));
    state.auswertungen = [];
    werteNetz([{ schluessel: 'auswertungen', updated: 9000,
                 wert: { liste: [{ id:'y', name:'Vom Handy', art:'', x:'wasser', teilen:'', gewaesser:'', zeit:'alles' }] } }]);
    await werteAbgleichen();
    return (state.auswertungen.length === 1 && state.auswertungen[0].name === 'Vom Handy')
        || JSON.stringify(state.auswertungen);
  });
  ta('vor dem Hochladen wird das Alte weggeraeumt', async () => {
    zeitSetzen(3600000, 5000);
    localStorage.removeItem('angellog-auswertungen'); state.auswertungen = [];
    const n = werteNetz([]);
    await werteAbgleichen();
    return (n.geloescht && n.geloescht.includes('schluessel=in.')) || String(n.geloescht);
  });
  ta('ein Fehler vom Server wird gemeldet, nicht verschluckt', async () => {
    zeitSetzen(3600000, 5000);
    api = async () => ({ ok: false, status: 500, json: async () => ({}) });
    try { await werteAbgleichen(); return 'kein Fehler geworfen'; }
    catch (e){ return /Abrufen/.test(e.message) || e.message; }
  });

  // ---- Anmelde-Schirm (Pflicht) ----
  t('Gate existiert', () => !!document.querySelector('#gate') || 'fehlt');
  t('Ohne Konto ist der Schirm noetig', () => { konto = null; return gateNoetig() === true || 'nicht noetig'; });
  t('Mit Konto ist er nicht noetig', () => {
    konto = { access_token: 'tok', email: 'a@b.c' };
    const r = gateNoetig(); konto = null;
    return r === false || 'trotzdem noetig';
  });
  t('Schirm legt sich ueber die App', () => {
    konto = null; gateZeigen();
    const an = document.querySelector('#gate').classList.contains('on');
    const z = parseInt(getComputedStyle(document.querySelector('#gate')).zIndex, 10);
    return (an && z >= 1000) || `on=${an} z=${z}`;
  });
  t('Anmeldeformular ist da', () =>
    (!!document.querySelector('#g-mail') && !!document.querySelector('#g-pw')
     && !!document.querySelector('#g-los')) || 'Felder fehlen');
  t('Kein Weg an der Anmeldung vorbei', () => {
    // Ein Ueberspringen-Knopf waere genau das, was Karl NICHT wollte.
    const txt = document.querySelector('#gate').textContent.toLowerCase();
    return (!/ohne konto|überspringen|ueberspringen|später|spaeter/.test(txt)) || 'es gibt einen Ausweg';
  });
  /* ============ Anmelde-Schirm, 10.08.2026 ============
     Karl: "app icon wenn man sich anmelden / regstrieren will ist immernoch das
     alte". Hier stand eine gezeichnete Fischsilhouette aus der Zeit vor dem
     eigenen Symbol -- die letzte Stelle, an der sie ueberlebt hatte, und zugleich
     der erste Bildschirm, den man von der App ueberhaupt zu sehen bekommt. */
  t('Der Anmelde-Schirm zeigt das echte App-Symbol', () => {
    konto = null; gateModus = 'login'; gateZeigen();
    const bild = document.querySelector('#gate .hero img');
    return (bild && /icon-192\.png/.test(bild.getAttribute('src')))
        || (bild ? bild.getAttribute('src') : 'kein Bild im Kopf des Schirms');
  });
  t('und nicht mehr die gezeichnete Silhouette', () => {
    // Zwei Symbole fuer dieselbe App sind eins zu viel -- und das falsche steht vorn.
    return (!document.querySelector('#gate .hero svg')) || 'die alte SVG steht noch da';
  });
  /* ---- Passwort anzeigen (Karls Ansage vom 10.08.2026) ---- */
  t('Neben dem Passwort steht ein Auge', () => {
    const k = document.querySelector('#g-pw-auge');
    return (!!k && !!k.querySelector('svg')) || 'kein Knopf';
  });
  t('Ein Tipp macht das Passwort sichtbar', () => {
    const feld = document.querySelector('#g-pw');
    feld.value = 'geheim123';
    document.querySelector('#g-pw-auge').click();
    return feld.type === 'text' || ('Typ ist ' + feld.type);
  });
  t('und der naechste verbirgt es wieder', () => {
    document.querySelector('#g-pw-auge').click();
    return document.querySelector('#g-pw').type === 'password'
        || ('Typ ist ' + document.querySelector('#g-pw').type);
  });
  t('die Beschriftung sagt, was der naechste Tipp tut', () => {
    /* Sonst ist der Knopf fuer alle unbrauchbar, die ihn vorgelesen bekommen --
       und fuer jeden anderen zweideutig: zeigt das Auge den Zustand oder die Tat? */
    const k = document.querySelector('#g-pw-auge');
    const vorher = k.getAttribute('aria-label');
    k.click();
    const nachher = k.getAttribute('aria-label');
    k.click();
    return (/anzeigen/i.test(vorher) && /verbergen/i.test(nachher))
        || `vorher "${vorher}", nachher "${nachher}"`;
  });
  t('das Auge liegt nicht auf den letzten Zeichen', () => {
    /* Genau dort sieht man beim Tippen hin. Das Feld braucht rechts mindestens so
       viel Platz, wie der Knopf breit ist. */
    const feld = document.querySelector('#g-pw');
    const rechts = parseFloat(getComputedStyle(feld).paddingRight);
    const knopf  = document.querySelector('#g-pw-auge').getBoundingClientRect().width;
    return (rechts >= knopf * .9) || `Platz ${rechts}px, Knopf ${knopf}px`;
  });
  t('der Knopf ist gross genug zum Treffen', () => {
    const r = document.querySelector('#g-pw-auge').getBoundingClientRect();
    return (r.width >= 40 && r.height >= 40) || `${Math.round(r.width)}x${Math.round(r.height)}`;
  });
  // ---- Benutzername ----
  t('Beim Anmelden kein Namensfeld', () => {
    konto = null; gateModus = 'login'; gateZeigen();
    return (!document.querySelector('#g-name')) || 'Namensfeld beim Anmelden';
  });
  t('Beim Anmelden geht E-Mail ODER Name', () =>
    /E-Mail oder Benutzername/.test(document.querySelector('#g-mail').placeholder)
      || document.querySelector('#g-mail').placeholder);
  t('Beim Registrieren gibt es ein Namensfeld', () => {
    gateModus = 'reg'; renderGate();
    return !!document.querySelector('#g-name') || 'fehlt';
  });
  t('Name wird beim Tippen klein geschrieben', () => {
    const f = document.querySelector('#g-name');
    f.value = 'Karl Meyer'; f.oninput();
    return f.value === 'karlmeyer' || f.value;
  });
  t('Zu kurzer Name wird abgelehnt',  () => /mindestens 3/.test(namePruefen('ab') || '') || namePruefen('ab'));
  t('Zu langer Name wird abgelehnt',  () => /höchstens 20/.test(namePruefen('a'.repeat(21)) || '') || 'durchgelassen');
  t('Leerer Name wird abgelehnt',     () => !!namePruefen('') || 'durchgelassen');
  t('Umlaute werden abgelehnt',       () => !!namePruefen('köder') || 'durchgelassen');
  t('Leerzeichen werden abgelehnt',   () => !!namePruefen('karl meyer') || 'durchgelassen');
  // ⚠️ Am @ wird beim Anmelden unterschieden, ob es eine E-Mail oder ein Name ist.
  t('@ im Namen wird abgelehnt', () => /@/.test(namePruefen('karl@mail.de') || '') || 'durchgelassen');
  t('Normale Namen gehen durch', () =>
    (['karl','angler_42','max.mustermann','a-b-c'].every(n => namePruefen(n) === null)) || 'einer abgelehnt');
  t('Gross geschrieben ist derselbe Name', () => namePruefen('KARL') === null || namePruefen('KARL'));
  t('Registrieren ohne Namen wird abgefangen', () => {
    gateModus = 'reg'; renderGate();
    document.querySelector('#g-name').value = '';
    document.querySelector('#g-mail').value = 'a@b.c';
    document.querySelector('#g-pw').value = 'geheim123';
    document.querySelector('#g-los').click();
    return /Benutzernamen/.test(document.querySelector('#gate').textContent) || 'keine Meldung';
  });
  t('Angemeldet zeigen die Einstellungen den Namen', () => {
    konto = { access_token: 't', email: 'a@b.c', username: 'angler42' };
    renderKonto();
    const s = document.querySelector('#konto').textContent;
    konto = null; renderKonto();
    return (s.includes('angler42') && s.includes('a@b.c')) || s.slice(0, 80);
  });
  t('Datenschutztext nennt den Benutzernamen', () => /Benutzername/.test(datenschutzText()) || 'fehlt');

  gateModus = 'login'; gateZeigen();
  t('Umschalten auf Registrieren', () => {
    document.querySelector('#g-wechsel').click();
    return /Konto erstellen/.test(document.querySelector('#g-los').textContent) || document.querySelector('#g-los').textContent;
  });
  t('Und wieder zurueck', () => {
    document.querySelector('#g-wechsel').click();
    return /Anmelden/.test(document.querySelector('#g-los').textContent) || document.querySelector('#g-los').textContent;
  });
  t('Leere Felder werden abgefangen', () => {
    document.querySelector('#g-mail').value = ''; document.querySelector('#g-pw').value = '';
    document.querySelector('#g-los').click();
    return /Passwort eingeben/.test(document.querySelector('#gate').textContent) || 'keine Meldung';
  });
  t('Datenschutz ist schon vor dem Anmelden lesbar', () => {
    document.querySelector('#g-ds').click();
    const auf = !document.querySelector('#g-ds-text').hidden;
    return auf || 'laesst sich nicht oeffnen';
  });
  t('Verbergen nimmt den Schirm weg', () => {
    gateVerbergen();
    return document.querySelector('#gate').classList.contains('on') === false || 'noch da';
  });

  // ⚠️ Der teuerste Fall: am Wasser ohne Empfang. Eine gespeicherte Sitzung muss
  // reichen, sonst steht der Schirm genau dort im Weg, wo die App gebraucht wird.
  t('Gespeicherte Sitzung reicht ohne Netz', () => {
    const echt = Object.getOwnPropertyDescriptor(Navigator.prototype, 'onLine');
    Object.defineProperty(navigator, 'onLine', { value: false, configurable: true });
    konto = { access_token: 'tok', email: 'a@b.c' };
    const r = gateNoetig();
    konto = null;
    if (echt) Object.defineProperty(Navigator.prototype, 'onLine', echt);
    else delete navigator.onLine;
    return r === false || 'Schirm verlangt Netz, obwohl eine Sitzung da ist';
  });
  t('Anmelden ohne Netz sagt es statt zu haengen', () => {
    Object.defineProperty(navigator, 'onLine', { value: false, configurable: true });
    konto = null; gateZeigen();
    document.querySelector('#g-mail').value = 'a@b.c';
    document.querySelector('#g-pw').value = 'geheim123';
    document.querySelector('#g-los').click();
    const txt = document.querySelector('#gate').textContent;
    delete navigator.onLine;
    gateVerbergen();
    return /Kein Netz/.test(txt) || 'keine Meldung';
  });

  ta('Erster Abgleich schiebt vorhandene Faenge hoch', async () => {
    /* Wer die App vorher ohne Konto benutzt hat, hat seine Faenge im Geraet. Beim
       ersten Anmelden muessen sie mit, statt neben dem Konto liegen zu bleiben.
       ⚠️ Hier stand frueher eine kuenstlich in die Zukunft gesetzte Marke
       (`-push`), gegen die sich ersterAbgleich wehren musste. Die Marke gibt es
       seit dem 10.08.2026 nicht mehr -- und damit auch nichts mehr, wogegen man
       sich wehren muesste. */
    /* ⚠️ Der Entwurf geht seit dem 10.08.2026 mit (Karls Ansage). Vorher erwartete
       diese Pruefung hier genau zwei Zeilen; dass sie beim Umbau angeschlagen hat,
       ist die Pruefung, die ihre Arbeit tut -- die Regel hat sich geaendert, nicht
       der Code hat sich verlaufen. */
    sandbox([mkC('alt1', 5000), mkC('alt2', 6000), mkC('entw', 7000, { entwurf: true })]);
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    api = async () => ({ ok: true, json: async () => [] });
    konto = { access_token: 'tok' };
    await ersterAbgleich();
    konto = null;
    const ids = (raus || []).map(r => r.id).sort();
    return (ids.length === 3 && ids.join(',') === 'alt1,alt2,entw') || JSON.stringify(ids);
  });

  /* ==================== Der Datenverlust vom 08.08.2026 ====================
     Karls Meldung: "mein kollege sagt das 2 seiner fische auf einmal nicht mehr
     da waren."

     Ursache: der Push-Stand wurde auf `Date.now()` NACH dem Hochladen gesetzt,
     ausgewaehlt wird aber davor. Dazwischen liegt die Zeit fuers Verkleinern und
     Verschicken der Fotos -- am Handy im Mobilfunk zehn Sekunden bis eine Minute.
     Ein Fang aus diesem Fenster war fuer die laufende Runde zu spaet und galt
     durch den neuen Stand zugleich als erledigt. Er ging nie hoch, bei keinem
     spaeteren Abgleich, und lag nur noch auf dem einen Geraet.

     ⚠️ Die Pruefungen unten stellen genau dieses Fenster nach: waehrend
     zeilenSchreiben laeuft, kommt ein Fang dazu bzw. wird einer geaendert.

     ⚠️ Seit dem 10.08.2026 gibt es den Geraetestand nicht mehr -- jeder Fang traegt
     sein `cloud`. Die Pruefungen bleiben trotzdem stehen, nur der Massstab hat
     gewechselt: frueher "der Stand darf den Fang nicht ueberholt haben", jetzt "der
     Fang darf kein cloud tragen, das er nicht verdient hat". Der Fehler von damals
     wuerde beide fallen lassen. */
  ta('ein Fang aus dem Hochlade-Fenster geht nicht verloren', async () => {
    sandbox([mkC('erster', 1000)]);
    zeilenSchreiben = async z => {
      // Genau hier tippt der Kollege den zweiten Fisch ein: das Hochladen des
      // ersten laeuft noch, sein Foto ist unterwegs.
      const spaet = mkC('waehrenddessen', Date.now());
      fakeDB.set(spaet.id, spaet);
      state.catches = [...fakeDB.values()];
    };
    api = async () => ({ ok: true, json: async () => [] });
    await hochladen();
    const spaet = fakeDB.get('waehrenddessen');
    // Er war nie verschickt -- also darf ihn nichts fuer gesichert erklaeren.
    return !spaet.cloud || `cloud ist ${spaet.cloud} — der Fang faellt durch`;
  });
  ta('und er geht in der naechsten Runde wirklich hoch', async () => {
    sandbox([mkC('erster', 1000)]);
    let raus = null;
    zeilenSchreiben = async z => { raus = z; };
    api = async () => ({ ok: true, json: async () => [] });
    await hochladen();                      // Runde 1: nur 'erster'
    const spaet = mkC('waehrenddessen', 2000);
    fakeDB.set(spaet.id, spaet); state.catches = [...fakeDB.values()];
    await hochladen();                      // Runde 2: muss den spaeten mitnehmen
    const ids = (raus || []).map(r => r.id);
    return (ids.length === 1 && ids[0] === 'waehrenddessen') || JSON.stringify(ids);
  });
  ta('eine Aenderung waehrend des Hochladens gilt nicht als gesichert', async () => {
    /* Der gefaehrlichere Zwilling: nicht ein neuer Fang, sondern derselbe Fang,
       waehrend sein Foto laeuft. Verschickt wurde Fassung 1000, im Geraet steht
       danach 7000. Wuerde jetzt cloud=7000 vermerkt, waere die Aenderung fuer
       immer weg -- oben liegt die alte Fassung und niemand fragt mehr nach. */
    sandbox([mkC('a', 1000)]);
    zeilenSchreiben = async () => {
      fakeDB.set('a', mkC('a', 7000));
      state.catches = [...fakeDB.values()];
    };
    api = async () => ({ ok: true, json: async () => [] });
    await hochladen();
    return !fakeDB.get('a').cloud || ('cloud ist ' + fakeDB.get('a').cloud + ' statt leer');
  });
  ta('cloud springt nicht auf die Uhr, sondern auf das Verschickte', async () => {
    sandbox([mkC('a', 5000)]);
    zeilenSchreiben = async () => {};
    api = async () => ({ ok: true, json: async () => [] });
    await hochladen();
    // 5000 ist die verschickte Fassung. Date.now() waere ~1.7e12.
    return fakeDB.get('a').cloud === 5000 || ('cloud ist ' + fakeDB.get('a').cloud);
  });
  ta('ein Grabstein erklaert keinen offenen Fang fuer gesichert', async () => {
    /* Frueher konnte der Zeitstempel eines Grabsteins den Geraetestand ueber Faenge
       schieben, die noch nicht dran waren -- derselbe Verlust durch die Hintertuer.
       Am Fang selbst kann das gar nicht mehr passieren; die Pruefung haelt fest,
       dass es dabei bleibt. */
    sandbox([mkC('a', 5000)], [{ id: 'tot', updated: 9e12, gemeldet: false }]);
    zeilenSchreiben = async () => {};
    api = async () => ({ ok: true, json: async () => [] });
    await hochladen();
    return fakeDB.get('a').cloud === 5000 || ('cloud ist ' + fakeDB.get('a').cloud);
  });
  /* ============ Sichtbar machen, was noch nicht in der Cloud liegt ============
     Die Lehre aus dem 08.08.2026: der Fehler allein hat die zwei Faenge nicht
     gekostet, seine UNSICHTBARKEIT hat es. Die App sah aus wie eine, bei der
     alles oben liegt; der Kollege hat im Vertrauen darauf neu installiert.

     Diese Pruefungen haengen deshalb nicht am damaligen Fehler, sondern an der
     Anzeige — sie muss auch bei kuenftigen Ursachen tragen (kein Netz,
     abgelaufene Sitzung, Server weg).

     ⚠️ Bewusst als synchrone Pruefungen: sandbox() ersetzt renderList durch eine
     leere Funktion, und geprueft wird hier gerade die echte Liste. Synchrone
     Pruefungen laufen alle, bevor der erste sandbox()-Aufruf geschieht. */
  /* `stand` war frueher ein Datum fuer das ganze Geraet. Seit dem 10.08.2026 traegt
     jeder Fang selbst, welche Fassung im Konto liegt -- der Wert wird deshalb auf
     alle verteilt. Die Pruefungen darunter sind unveraendert geblieben: es ist
     dieselbe Frage, nur an der richtigen Stelle gestellt. */
  const cloudSetzen = (faenge, stand) => {
    state.catches = faenge.map(c => ({ ...c, cloud: stand }));
    renderList();
  };
  t('nicht gesicherte Faenge werden gezaehlt', () => {
    cloudSetzen([mkC('alt', 1000), mkC('neu1', 5000), mkC('neu2', 6000)], 3000);
    const n = nichtGesichert().length;
    return n === 2 || ('gezaehlt: ' + n);
  });
  t('ein ungesicherter Entwurf zaehlt mit', () => {
    /* ⚠️ Hier stand bis zum 10.08.2026 das Gegenteil. Solange Entwuerfe absichtlich
       lokal blieben, war ihre Ausnahme richtig. Seit sie mitgehen, waere dieselbe
       Ausnahme genau die Blindheit, die am 08.08. zwei Faenge gekostet hat: ein
       Entwurf, der noch nirgends liegt, liegt eben nur hier. */
    cloudSetzen([mkC('e', 5000, { entwurf: true })], 0);
    const n = nichtGesichert().length;
    return n === 1 || ('gezaehlt: ' + n);
  });
  t('ein gesicherter Entwurf zaehlt nicht mit', () => {
    cloudSetzen([mkC('e', 5000, { entwurf: true })], 9000);
    const n = nichtGesichert().length;
    return n === 0 || ('gezaehlt: ' + n);
  });
  /* ============ Zwei Wahrheiten auf einem Bildschirm (10.08.2026) ============
     Karl: "ich habe 11 Faenge auf meinem pc und nur 5 auf meinem handy". Es waren
     acht und fuenf. Die Liste zeigt Entwuerfe mit an, die Zaehlung darueber liess
     sie weg -- und gezaehlt wird, was man sieht. Wir haben daraufhin einen halben
     Abend lang einen Datenverlust gesucht, den es nie gab.

     ⚠️ Die Pruefung haengt an der Zahl, nicht am Aussehen: solange in der Liste
     mehr Zeilen stehen als "x Faenge" behauptet, muss die Differenz oben stehen. */
  t('Entwuerfe stehen mit ihrer Zahl ueber der Liste', () => {
    cloudSetzen([mkC('a', 1000), mkC('e1', 2000, { entwurf: true }),
                 mkC('e2', 3000, { entwurf: true })], 9000);
    const zeilen = document.querySelectorAll('#list .item').length;
    const zahl   = document.querySelector('#st-count').textContent;
    const draft  = document.querySelector('#st-drafts');
    return (zeilen === 3 && /^1 Fang/.test(zahl) && !draft.hidden && /^2 Entw/.test(draft.textContent))
        || `${zeilen} Zeilen, oben "${zahl}", Entwuerfe "${draft.hidden ? '(versteckt)' : draft.textContent}"`;
  });
  t('ohne Entwuerfe bleibt das Schild weg', () => {
    // Sonst stuende bei jedem normalen Blick eine 0 herum, die nichts erklaert.
    cloudSetzen([mkC('a', 1000)], 9000);
    return document.querySelector('#st-drafts').hidden === true
        || ('steht da: ' + document.querySelector('#st-drafts').textContent);
  });
  t('Liste und Zaehlung widersprechen sich nie', () => {
    /* Der eigentliche Satz, um den es geht -- unabhaengig davon, wie die Zahlen
       spaeter dargestellt werden: was in der Liste steht, muss oben vollstaendig
       aufgehen. Faenge plus Entwuerfe gleich Zeilen. */
    cloudSetzen([mkC('a', 1000), mkC('b', 1100), mkC('e', 2000, { entwurf: true })], 9000);
    const zeilen = document.querySelectorAll('#list .item').length;
    const f = parseInt(document.querySelector('#st-count').textContent, 10);
    const d = document.querySelector('#st-drafts').hidden
            ? 0 : parseInt(document.querySelector('#st-drafts').textContent, 10);
    return (f + d === zeilen) || `${f} Faenge + ${d} Entwuerfe != ${zeilen} Zeilen`;
  });
  t('der Hinweis steht in der Liste, wenn etwas offen ist', () => {
    cloudSetzen([mkC('neu', 5000)], 1000);
    const p = document.querySelector('#st-cloud');
    // „Eintrag", nicht „Fang": seit dem 10.08.2026 gehen Entwuerfe mit, und ein
    // halb ausgefuellter Entwurf ist kein Fang.
    return (!p.hidden && /1 Eintrag nur auf diesem Ger/.test(p.textContent))
        || ('hidden=' + p.hidden + ' text=' + p.textContent);
  });
  t('und er nennt die richtige Mehrzahl', () => {
    cloudSetzen([mkC('a', 5000), mkC('b', 6000)], 1000);
    return /2 Eintr.ge nur auf diesem Ger/.test(document.querySelector('#st-cloud').textContent)
        || document.querySelector('#st-cloud').textContent;
  });
  t('der Hinweis verschwindet, wenn alles gesichert ist', () => {
    /* ⚠️ Der wichtigere Teil. Eine Warnung, die nach erfolgreichem Hochladen
       stehen bleibt, behauptet eine Gefahr, die es nicht gibt — und wird bald
       uebersehen. Dann traegt sie nichts mehr, wenn sie einmal stimmt. */
    cloudSetzen([mkC('a', 5000), mkC('b', 6000)], 9000);
    return document.querySelector('#st-cloud').hidden === true
        || ('steht noch da: ' + document.querySelector('#st-cloud').textContent);
  });
  /* ⚠️ Die Markierung heisst seit dem 13.08.2026 „nur hier" statt „nur auf diesem
     Geraet" und steht seit dem zweiten Anlauf desselben Tages **oben auf der gelben
     Leiste** (Karls Ansage), nicht mehr als Pille unten in der Kachel. Gesucht wird
     deshalb nach der Leiste (.marks) und nicht nach einem Wortlaut: der ist Gestaltung
     und aendert sich wieder, die Warnung darf davon nicht abhaengen. */
  t('jeder offene Fang ist in der Liste einzeln markiert', () => {
    // Die Zahl allein genuegt nicht -- man muss sehen, WELCHE Faenge es sind.
    cloudSetzen([mkC('alt', 1000), mkC('neu1', 5000), mkC('neu2', 6000)], 3000);
    const zeilen = [...document.querySelectorAll('#list .item')];
    const markiert = zeilen.filter(z => z.querySelector('.marks'))
                           .map(z => z.dataset.id).sort();
    return (markiert.length === 2 && markiert[0] === 'neu1' && markiert[1] === 'neu2')
        || JSON.stringify(markiert);
  });
  t('ein gesicherter Fang traegt die Markierung nicht', () => {
    cloudSetzen([mkC('alt', 1000)], 3000);
    const z = document.querySelector('#list .item');
    return !z.querySelector('.marks') || 'faelschlich markiert';
  });
  /* Gegenprobe: die Leiste muss auch beschriftet sein. Ein leerer gelber Balken bestuende
     die Pruefung darueber und saehe aus wie ein Gestaltungsfehler. */
  t('und die Leiste traegt einen Text', () => {
    cloudSetzen([mkC('alt', 1000), mkC('neu1', 5000)], 3000);
    const p = document.querySelector('#list .item .marks');
    return (p && p.textContent.trim().length >= 4) || 'Leiste ohne Text';
  });
  t('die Einstellungen warnen vor dem Abmelden und Loeschen', () => {
    /* Die Seite, auf der man landet, bevor man abmeldet, das Konto loescht oder
       neu installiert. Genau dort hat der Kollege am 08.08. nichts gesehen. */
    cloudSetzen([mkC('neu', 5000)], 1000);
    const vorher = konto;
    konto = { access_token: 'tok', username: 'karl' };
    renderKonto();
    const txt = document.querySelector('#konto').textContent;
    konto = vorher; renderKonto();
    return (/nur auf diesem Ger/.test(txt) && /Neuinstallieren|neu ?installier/i.test(txt))
        || txt.slice(0, 200);
  });
  t('ohne eingerichtete Cloud bleibt der Hinweis stumm', () => {
    /* Ohne Cloud gibt es nichts zu sichern -- dann waere die Warnung sinnlos.
       ⚠️ Quelltext-Pruefung, weil cloudAn ein `const` ist und sich nicht
       ersetzen laesst. Geprueft wird, dass der Riegel die ERSTE Zeile ist:
       stuende er hinter dem Lesen des Push-Standes, meldete eine App ohne
       Cloud jeden Fang als ungesichert. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const a = js.indexOf('function nichtGesichert(');
    if (a < 0) return 'nichtGesichert nicht gefunden';
    const kopf = js.slice(a, js.indexOf('}', a));
    return /^[^\n]*\n\s*if \(!cloudAn\(\)\) return \[\];/.test(kopf)
        || 'kein Riegel als erste Zeile';
  });
  t('nach reinem Hochladen wird die Liste aufgefrischt', () => {
    /* ⚠️ Quelltext-Pruefung mit Absicht: der Fall braucht einen vollen
       syncJetzt-Durchlauf mit Netz, und im Rahmen laeuft kein Netz.
       Geprueft wird deshalb die Stelle selbst — renderList() muss NACH dem
       Auffrisch-Block stehen und nicht darin. Stand es darin, blieb der
       Hinweis nach erfolgreichem Hochladen stehen, weil dabei nichts
       heruntergeladen wird.
       ⚠️ Der Block heisst seit dem 13.08.2026 `if (rauf || runter)`. Vorher stand dort
       nur `runter` -- und genau das war die zweite Haelfte von Karls Meldung: nach einem
       reinen Hochladen wurde der Arbeitsspeicher nie neu gelesen, das Schild „nur hier"
       blieb stehen und der Fang ging beim naechsten Mal wieder hoch. Neuzeichnen allein
       hat nicht gereicht, weil es die veraltete Fassung neu zeichnete. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const a = js.indexOf('async function syncJetzt(');
    if (a < 0) return 'syncJetzt nicht gefunden';
    /* ⚠️ Hier stand ein festes Fenster von 2600 Zeichen. Das ist am 12.08.2026
       gerissen, als syncJetzt um ein paar Zeilen wuchs: das Fenster reichte
       nicht mehr bis `if (runter)`, und die Pruefung fiel mit "Stelle nicht
       gefunden" -- ohne dass am geprueften Verhalten irgendetwas falsch war.
       Eine Pruefung, die an der Laenge einer Funktion haengt, meldet Wachstum
       als Fehler. Jetzt endet das Fenster an der naechsten Funktion. */
    const rest = js.slice(a + 20);
    const ende = rest.search(/\n(async )?function /);
    const block = js.slice(a, ende < 0 ? js.length : a + 20 + ende);
    const zweig = block.indexOf('if (rauf || runter)');
    const rl    = block.indexOf('renderList();', zweig);
    const zu    = block.indexOf('\n    }', zweig);     // Ende des runter-Zweigs
    if (zweig < 0 || rl < 0 || zu < 0) return 'Stelle nicht gefunden';
    return rl > zu || 'renderList() steht im runter-Zweig — Hinweis bleibt stehen';
  });

  /* ==================== Sprache (09.08.2026) ====================
     Karls Ansage: "sprach einstllung deutsch +englisch".

     ⚠️ Am Ende dieses Blocks muss wieder Deutsch stehen -- alle folgenden
     Pruefungen vergleichen deutsche Texte. */
  t('Umschalten uebersetzt die feste Oberflaeche', () => {
    spracheSetzen('en');
    const txt = document.querySelector('#kopf h1').textContent.trim();
    const zeit = document.querySelector('#zeit-karte .f').textContent.trim();
    return (zeit === 'Total fishing time') || ('Kopfzeile: ' + txt + ' / ' + zeit);
  });
  t('und Zurueckschalten stellt Deutsch wieder her', () => {
    /* ⚠️ Das geht nur, weil der deutsche Urtext beim ersten Rundgang aufgehoben
       wurde. Ohne ihn gaebe es nach dem Umschalten nichts mehr, wonach man
       nachschlagen koennte -- die App waere englisch und bliebe es. */
    spracheSetzen('en');
    spracheSetzen('de');
    return document.querySelector('#zeit-karte .f').textContent.trim() === 'Angelzeit gesamt'
        || document.querySelector('#zeit-karte .f').textContent.trim();
  });
  t('gespeicherte Fangdaten werden NICHT uebersetzt', () => {
    /* ⚠️ Die wichtigste Pruefung des ganzen Blocks. "Hecht" steht als Vorschlag
       im Woerterbuch. Wuerde der Rundgang auch die Liste anfassen, wuerde aus
       einem eingetippten "Hecht" beim Umschalten ein "Pike" -- ein Wert, den
       niemand je erfasst hat. Uebersetzt wird die Oberflaeche, nicht die Daten. */
    state.catches = [mkC('a', 1000, { art: 'Hecht', when: '2026-07-15T06:30', gewaesser: 'Elbe' })];
    spracheSetzen('en');
    const txt = document.querySelector('#list .item .t1').textContent;
    spracheSetzen('de');
    state.catches = [];
    return (txt.indexOf('Hecht') >= 0 && txt.indexOf('Pike') < 0) || txt;
  });
  t('die Vorschlagsliste dagegen schon', () => {
    // Die Liste fuellt sich erst beim Tippen -- ohne Eingabe steht sie leer da.
    spracheSetzen('en');
    const feld = document.querySelector('#f-art');
    feld.value = 'pik';
    feld.dispatchEvent(new Event('input'));
    const opts = [...document.querySelectorAll('#dl-art option')].map(o => o.value);
    feld.value = '';
    feld.dispatchEvent(new Event('input'));
    spracheSetzen('de');
    return opts.includes('Pike') || ('[' + opts.join(',') + ']');
  });
  t('feste Achsen: Reihenfolge und Schluessel sprechen dieselbe Sprache', () => {
    /* ⚠️ Der Fall, der ohne Pruefung stumm durchginge: die Stufen einer festen
       Achse werden ueber den ANGEZEIGTEN Text zugeordnet. Stuende links
       "Bewoelkt" und der Fang lieferte "Cloudy", fiele er aus seiner Stufe --
       die Kurve laege flach auf null, ohne Fehlermeldung, und saehe aus wie
       "keine Faenge". */
    spracheSetzen('en');
    const fehler = [];
    for (const key of ['wetter', 'tageszeit', 'mond', 'trueb']){
      const a = achseVon(key);
      const stufen = new Set(a.reihe());
      const probe = { wetter: { wetter: 'bewoelkt' },
                      tageszeit: { phase: 'morgen' },
                      mond: { when: '2026-07-15T06:30' },
                      trueb: { truebung: 'leicht' } }[key];
      const s = a.schluessel(probe);
      if (!s || !stufen.has(s)) fehler.push(key + ' -> ' + s);
    }
    spracheSetzen('de');
    return fehler.length === 0 || fehler.join(' | ');
  });
  t('ein fehlender Schluessel faellt auf Deutsch zurueck', () => {
    // Nicht auf ein Kuerzel und nicht auf leer -- unuebersetzt ist besser als kaputt.
    spracheSetzen('en');
    const r = T('Diesen Satz gibt es im Woerterbuch nicht');
    spracheSetzen('de');
    return r === 'Diesen Satz gibt es im Woerterbuch nicht' || r;
  });
  t('die Sprachnamen selbst bleiben stehen', () => {
    /* „Deutsch" heisst auf Englisch „German" -- wer aber kein Deutsch kann und
       die App auf Deutsch vorfindet, sucht nach „English". Sprachnamen stehen
       ueberall in ihrer eigenen Sprache. */
    spracheSetzen('en');
    const o = [...document.querySelectorAll('#sprache option')].map(x => x.textContent);
    spracheSetzen('de');
    return (o.join(',') === 'Deutsch,English') || o.join(',');
  });
  t('die Wahl wird gemerkt', () => {
    spracheSetzen('en');
    const g = localStorage.getItem('angellog-sprache');
    spracheSetzen('de');
    return g === 'en' || String(g);
  });
  t('ohne Wahl entscheidet die Sprache des Geraets', () => {
    localStorage.removeItem('angellog-sprache');
    return (spracheLesen() === spracheStandard()) || spracheLesen();
  });
  t('die Datenschutzerklaerung kommt ganz, nicht halb uebersetzt', () => {
    /* Ein Rechtstext darf nicht aus einzeln nachgeschlagenen Saetzen bestehen --
       bei einer Luecke stuende dort halb Deutsch, halb Englisch. */
    spracheSetzen('en');
    const txt = datenschutzText();
    spracheSetzen('de');
    return (/Privacy/.test(txt) && !/[äöüßÄÖÜ]/.test(txt.replace(/Fänge|Gewässer/g, '')))
        || txt.slice(0, 160);
  });
  t('am Ende steht wieder Deutsch', () => SPRACHE === 'de' || SPRACHE);

  /* ============ Abgleich pruefen und heilen (09.08.2026) ============
     Karls Meldung: "fänge auf meinem handy und auf meinem pc sind nicht gleich
     warum auch immer."

     ⚠️ Das "warum auch immer" ist der Befund. Der Abgleich laeuft still, und
     wenn etwas fehlt, sagt einem nichts, auf welcher Seite -- dasselbe Muster
     wie beim Datenverlust am 08.08. Geprueft wird deshalb, dass die Richtung
     benannt wird und nicht nur "es ist unterschiedlich". */
  ta('der Abgleich-Test benennt, was hier fehlt', async () => {
    sandbox([mkC('a', 1000), mkC('b', 2000)]);
    api = async () => ({ ok: true, json: async () => [{ id: 'a' }, { id: 'b' }, { id: 'c' }] });
    konto = { access_token: 'tok' };
    const z = await abgleichPruefen();
    konto = null;
    return (z.imKonto === 3 && z.aufGeraet === 2 && z.fehltHier === 1 && z.fehltDort === 0)
        || JSON.stringify(z);
  });
  ta('und was dort fehlt', async () => {
    sandbox([mkC('a', 1000), mkC('b', 2000), mkC('c', 3000)]);
    api = async () => ({ ok: true, json: async () => [{ id: 'a' }] });
    konto = { access_token: 'tok' };
    const z = await abgleichPruefen();
    konto = null;
    return (z.fehltDort === 2 && z.fehltHier === 0) || JSON.stringify(z);
  });
  ta('Ein Entwurf, der nur hier liegt, wird als fehlend gemeldet', async () => {
    /* ⚠️ Hier stand bis zum 10.08.2026 das Gegenteil ("zaehlen in keiner der beiden
       Richtungen mit"). Seit Entwuerfe mitgehen, waere das Verschweigen der
       Fehlalarm mit umgekehrtem Vorzeichen: die Pruefung meldete "beide Seiten sind
       gleich", waehrend fuenf Entwuerfe nur auf einem Geraet liegen. */
    sandbox([mkC('a', 1000), mkC('e', 2000, { entwurf: true })]);
    api = async () => ({ ok: true, json: async () => [{ id: 'a' }] });
    konto = { access_token: 'tok' };
    const z = await abgleichPruefen();
    konto = null;
    return (z.fehltDort === 1 && z.entwuerfe === 1 && z.aufGeraet === 2) || JSON.stringify(z);
  });
  ta('Ein Grabstein zaehlt nicht zum Bestand im Konto', async () => {
    /* ⚠️ Seit dem 11.08.2026 fragt der Abgleich-Test dieselben Kopfzeilen ab wie
       der Abgleich selbst -- eine Abfrage statt zweier, die dasselbe zaehlen
       sollen. Damit kommen aber auch die Grabsteine mit, und die sind kein
       Bestand: wuerden sie mitgezaehlt, meldete die Anzeige nach jeder Loeschung
       "im Konto liegt mehr als hier" und schickte den Nutzer auf die Suche nach
       einem Fang, den er selbst weggeworfen hat. */
    sandbox([mkC('a', 1000)]);
    api = async () => antwort([{ id: 'a', updated: 1000, geloescht: false },
                               { id: 'weg', updated: 2000, geloescht: true }]);
    konto = { access_token: 'tok' };
    const z = await abgleichPruefen();
    konto = null;
    return (z.imKonto === 1 && z.fehltHier === 0 && z.fehltDort === 0) || JSON.stringify(z);
  });

  /* ====== Die Notiz "liegt oben" ueberlebt das Konto nicht (11.08.2026) ======
     ⚠️ Das war eine echte Luecke, keine Aufraeumarbeit. Bis zum 10.08. hing
     "liegt oben" an einem Stand im localStorage, und den loeschte das Abmelden.
     Seither haengt es als `cloud` am Fang -- und dort hat es das Abmelden
     ueberlebt. Wer sich abmeldet und ein zweites Konto anlegt, haette ein leeres
     Konto vor sich, waehrend jeder Fang von sich behauptet, er liege schon oben:
     der Abgleich schickt nichts und meldet "alles schon aktuell". */
  ta('Abmelden loest die Notiz "liegt oben" an jedem Fang', async () => {
    sandbox([mkC('a', 5000, { cloud: 5000 }), mkC('b', 6000, { cloud: 6000 })]);
    await cloudNotizenLoesen();
    const uebrig = [...fakeDB.values()].filter(c => c.cloud != null).map(c => c.id);
    return (uebrig.length === 0) || ('cloud steht noch an: ' + JSON.stringify(uebrig));
  });
  ta('und danach gehen die Faenge wieder mit hoch', async () => {
    // Die Notiz zu loesen nuetzt nichts, wenn der naechste Abgleich sie trotzdem auslaesst.
    sandbox([mkC('a', 5000, { cloud: 5000 })]);
    await cloudNotizenLoesen();
    state.catches = [...fakeDB.values()];
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return ((raus || []).some(r => r.id === 'a')) || 'der Fang blieb liegen';
  });
  /* ⚠️ Gesucht wird der **Aufruf**, nicht der Name. In der Gegenprobe ist der
     Aufruf in abmelden() durch einen Kommentar ersetzt worden -- und die
     Pruefung blieb gruen, weil im Kommentar daneben "cloudNotizenLoesen()"
     steht. Eine Pruefung, die den Fehler nicht faengt, ist keine. Deshalb muss
     der Name am Anfang einer Zeile stehen und ein Semikolon dahinter. */
  const ruftAuf = (js, ab) => /(^|\n)\s*(await\s+)?cloudNotizenLoesen\(\);/.test(js.slice(ab, ab + 900));
  t('Abmelden ruft das auch wirklich auf', () => {
    /* Quelltext-Pruefung: abmelden() haengt an der echten IndexedDB und am
       Anmelde-Schirm, beides laeuft im Rahmen nicht mit. Geprueft wird deshalb
       die Stelle selbst -- eine Funktion, die niemand aufruft, ist keine. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const a = js.indexOf('function abmelden(');
    if (a < 0) return 'abmelden nicht gefunden';
    return ruftAuf(js, a) || 'abmelden loest die Notizen nicht';
  });
  t('und das Loeschen des Kontos ebenso', () => {
    /* ⚠️ Der haertere der beiden Faelle: nach dem Loeschen ist die Zeile oben
       nachweislich weg, jede Notiz "liegt im Konto" also nachweislich falsch. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const a = js.indexOf("$('#k-del')");
    if (a < 0) return 'der Loesch-Knopf nicht gefunden';
    return ruftAuf(js, a) || 'das Loeschen laesst die Notizen stehen';
  });

  ta('"Alles neu laden" holt, was im Konto liegt und hier fehlt', async () => {
    /* ⚠️ Hier stand "setzt den Herunterlade-Stand zurueck". Der Knopf ist am
       09.08. genau dafuer gebaut worden: der Stand lief nur vorwaerts, und ein
       Geraet, das seine IndexedDB verloren hatte, fragte "was ist seit gestern
       passiert?" und bekam nichts.

       Seit dem 11.08.2026 gibt es keinen Stand mehr -- also auch nichts
       zurueckzusetzen. Geprueft wird deshalb, was der Knopf verspricht, und
       nicht, wie er es macht. Der Stand steht hier absichtlich in der Zukunft:
       frueher haette das genuegt, damit nichts herunterkommt. */
    sandbox([]);
    localStorage.setItem('angellog-sync', '2999-01-01T00:00:00Z');
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'da', updated: 100, geloescht: false }])
      : antwort([{ id: 'da', updated: 100, geloescht: false, daten: { art: 'Aal' }, fotos: [] }]);
    zeilenSchreiben = async () => {};
    konto = { access_token: 'tok' };
    await allesNeuLaden();
    konto = null;
    return fakeDB.has('da') || 'der Fang aus dem Konto kam nicht herunter';
  });
  ta('und es loest auch die cloud-Vermerke, sonst bliebe die Gegenrichtung aus', async () => {
    /* Wer den Knopf drueckt, glaubt dem Abgleich gerade nicht mehr. Dann darf keine
       Notiz von ihm stehen bleiben -- sonst zieht er nur herunter, und ein Fang, der
       faelschlich als gesichert gilt, bleibt genau so liegen wie vorher. */
    sandbox([mkC('a', 5000, { cloud: 5000 })]);
    localStorage.setItem('angellog-sync', '2026-08-09T00:00:00Z');
    let raus = null;
    api = async () => ({ ok: true, json: async () => [] });
    zeilenSchreiben = async z => { raus = z; };
    konto = { access_token: 'tok' };
    await allesNeuLaden();
    konto = null;
    return ((raus || []).some(r => r.id === 'a'))
        || ('nicht mitgeschickt: ' + JSON.stringify((raus || []).map(r => r.id)));
  });

  /* ==================== Fehler melden (09.08.2026) ====================
     Karls Ansage: "support für bugs". Der Kern ist nicht das Formular, sondern
     dass eine Meldung ohne Netz nicht verlorengeht -- Kaputtes faellt beim
     Benutzen auf, und benutzt wird die App am Wasser. */
  t('eine Meldung landet zuerst im Geraet', () => {
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('Die Karte bleibt weiss');
    const l = meldungenLesen();
    return (l.length === 1 && l[0].text === 'Die Karte bleibt weiss')
        || JSON.stringify(l);
  });
  t('die Meldung bringt ihr Umfeld mit', () => {
    /* Ohne das steht in der Tabelle "geht nicht" und niemand kann etwas damit
       anfangen. Die Fassung ist der wichtigste Teil: eine PWA am iPhone zeigt
       wochenlang eine alte Seite. */
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('irgendwas');
    const u = meldungenLesen()[0].umfeld;
    return (u.fassung && u.geraet && u.netz && typeof u.ungesichert === 'number')
        || JSON.stringify(u);
  });
  t('die Fassung in der Meldung ist die echte', () =>
    (typeof FASSUNG === 'string' && /^v\d+$/.test(FASSUNG)) || String(FASSUNG));
  t('sehr langer Text wird gekuerzt, nicht abgelehnt', () => {
    // Lieber gekuerzt ankommen als an einer Laengenbegrenzung scheitern.
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('x'.repeat(9000));
    return meldungenLesen()[0].text.length === 4000 || meldungenLesen()[0].text.length;
  });
  /* ⚠️ Seit dem 12.08.2026 geht jede Meldung EINZELN hinaus, nicht als Stapel.
     Der Grund ist die Bremse in der Datenbank: eine abgewiesene Zeile nimmt in
     PostgreSQL die ganze Anweisung mit. Im Stapel waeren damit auch die
     Meldungen daneben gefallen, die in Ordnung waren -- und beim naechsten
     Abgleich waeren sie wieder zusammen gegangen und wieder zusammen gefallen.
     Ein Stapel, der einmal haengt, haengt fuer immer. */
  ta('wartende Meldungen gehen einzeln raus, nicht als Stapel', async () => {
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('Fehler A'); meldungAnlegen('Fehler B');
    const rufe = [];
    api = async (pfad, opt) => { rufe.push(JSON.parse(opt.body)); return { ok: true, text: async () => '' }; };
    konto = { access_token: 'tok' };
    const n = await meldungenNachreichen();
    konto = null;
    return (n === 2 && rufe.length === 2 && !Array.isArray(rufe[0])
            && rufe[0].text === 'Fehler A' && meldungenLesen().length === 0)
        || `verschickt ${n}, Rufe ${rufe.length}, Rest ${meldungenLesen().length}`;
  });
  ta('schlaegt das Verschicken fehl, bleibt die Meldung liegen', async () => {
    /* ⚠️ Dieselbe Regel wie beim Push-Stand der Faenge: nie einen Stand
       behaupten, fuer den nichts verschickt wurde. Wuerde hier vorab geleert,
       waere die Meldung bei jedem Serverfehler still weg -- und der Melder
       glaubt, sie sei angekommen. */
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('Fehler A');
    api = async () => ({ ok: false, status: 500, text: async () => 'kaputt' });
    konto = { access_token: 'tok' };
    let geflogen = false;
    try { await meldungenNachreichen(); } catch { geflogen = true; }
    konto = null;
    return (geflogen && meldungenLesen().length === 1)
        || `geflogen ${geflogen}, Rest ${meldungenLesen().length}`;
  });

  /* ====== Die Bremse darf nichts verschlucken (12.08.2026) ======
     ⚠️ Das ist die Pruefung, um die es bei der ganzen Aenderung geht. Die Bremse
     soll Spam abweisen, nicht Meldungen fressen. Wird eine abgewiesen, muss sie
     liegenbleiben und beim naechsten Mal mitgehen -- und die davor, die
     durchgekommen ist, darf nicht ein zweites Mal rausgehen. */
  ta('eine gebremste Meldung bleibt liegen, die davor ist durch', async () => {
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('Fehler A'); meldungAnlegen('Fehler B'); meldungAnlegen('Fehler C');
    let nr = 0;
    api = async () => {
      nr++;
      return nr === 1 ? { ok: true, text: async () => '' }
                      : { ok: false, status: 400,
                          text: async () => '{"message":"ANGEL_BREMSE:42"}' };
    };
    konto = { access_token: 'tok' };
    const n = await meldungenNachreichen();
    konto = null;
    const rest = meldungenLesen();
    return (n === 1 && rest.length === 2 && rest[0].text === 'Fehler B')
        || `durch ${n}, Rest ${rest.length}: ${rest.map(m => m.text).join(',')}`;
  });
  ta('die Bremse wirft keinen Fehler in den Abgleich', async () => {
    /* Eine Bremse ist kein Fehlschlag, sondern eine Auskunft ("spaeter nochmal").
       Wuerde sie fliegen, meldete die App dem Angler einen Fehler fuer etwas,
       das voellig in Ordnung ist. */
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('Fehler A');
    api = async () => ({ ok: false, status: 400,
                         text: async () => '{"message":"ANGEL_BREMSE:9"}' });
    konto = { access_token: 'tok' };
    let geflogen = false;
    try { await meldungenNachreichen(); } catch { geflogen = true; }
    konto = null;
    return (!geflogen && meldungenLesen().length === 1)
        || `geflogen ${geflogen}, Rest ${meldungenLesen().length}`;
  });
  ta('ohne Konto wird nichts verschickt und nichts verworfen', async () => {
    localStorage.removeItem('angellog-meldungen');
    meldungAnlegen('Fehler A');
    konto = null;
    const n = await meldungenNachreichen();
    return (n === 0 && meldungenLesen().length === 1)
        || `verschickt ${n}, Rest ${meldungenLesen().length}`;
  });
  t('ein Fehler beim Melden haelt den Abgleich nicht an', () => {
    /* Quelltext-Pruefung: der Aufruf muss in einem eigenen try stehen. Ohne das
       wuerde eine kaputte Meldung den Abgleich der FAENGE mitreissen -- das
       Wichtige haengt dann am Unwichtigen. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const a = js.indexOf('async function syncJetzt(');
    const b = js.indexOf('meldungenNachreichen()', a);
    if (a < 0 || b < 0) return 'Stelle nicht gefunden';
    return /try \{ await meldungenNachreichen\(\); \} catch \{\}/.test(js.slice(a, b + 60))
        || 'steht nicht in einem eigenen try';
  });

  /* ==================== Kurze Einfuehrung (09.08.2026) ====================
     Karls Ansage: "tutorial für die app, kleine vorstellung wofür nutzt du die
     app, um die leute neugierig zu machen, nach dem registrieren." */
  t('die Einfuehrung hat mehrere Karten', () =>
    (Array.isArray(TOUR) && TOUR.length >= 3 && TOUR.every(k => k.titel && k.text))
    || 'TOUR ist nicht vollstaendig');
  t('sie laesst sich oeffnen und steht dann da', () => {
    tourZeigen();
    const auf = document.querySelector('#tour').classList.contains('on');
    const txt = document.querySelector('#tour-inner').textContent;
    return (auf && txt.indexOf(TOUR[0].titel) >= 0) || ('auf=' + auf);
  });
  /* ⚠️ Hier stand "sie laesst sich ueberspringen" mit der Begruendung, eine
     Einfuehrung, die man nicht wegklicken kann, mache ungeduldig. Karls Ansage
     vom 12.08.2026 dreht das um: "ueberspringen soll man das nicht". Die Pruefung
     ist deshalb umgedreht, nicht geloescht -- der Knopf soll nachweislich WEG
     sein, sonst kaeme er beim naechsten Umbau unbemerkt zurueck. */
  t('sie laesst sich NICHT mehr ueberspringen', () => {
    tourZeigen();
    const weg = document.querySelector('#tour-weg');
    const zu = document.querySelector('#tour').classList.contains('on');
    return (!weg && zu) || (weg ? 'Ueberspringen-Knopf ist noch da' : 'Tour steht nicht');
  });
  /* Karls Ansage: "ich will keine punkte, ich brauche eine progress leiste". */
  t('statt Punkten steht ein Fortschrittsbalken da', () => {
    tourZeigen();
    const punkte = document.querySelector('#tour .punkte');
    const balken = document.querySelector('#tour .fortschritt');
    return (!punkte && !!balken) || (punkte ? 'Punkte sind noch da' : 'kein Balken');
  });
  t('und der Balken waechst mit jeder Karte', () => {
    tourZeigen();
    const breit = () => parseFloat(document.querySelector('#tour .fortschritt i').style.width);
    const a = breit();
    document.querySelector('#tour-weiter').click();
    const b = breit();
    return (b > a) || `von ${a}% auf ${b}%`;
  });
  t('die Zielfisch-Karte ist raus', () =>
    !TOUR.some(k => k.feld === 'ziele') || 'sie ist noch drin');
  /* ⚠️ Karls Ansage: "in der einfuehrung steht immer fischen es ist angeln".
     Geprueft ueber alle Karten samt ihrer Auswahl-Beschriftungen. */
  t('in der Einfuehrung steht angeln, nicht fischen', () => {
    const alles = TOUR.map(k => [k.titel, k.text,
      (k.optionen || []).map(o => o.join(' ')).join(' ')].join(' ')).join(' ');
    const treffer = alles.match(/\w*[Ff]ischen/g) || [];
    // "Spinnangeln"/"Fliegenangeln" sind gewollt; blosses "fischen" nicht.
    return treffer.length === 0 || 'steht noch drin: ' + treffer.join(', ');
  });
  t('die Support-Karte verspricht ein bis zwei Tage', () => {
    const k = TOUR[TOUR.length - 1];
    return (/ein bis zwei Tagen/.test(k.text) && /Fehler melden/.test(k.text))
        || 'Karte: ' + k.titel;
  });

  t('durchklicken fuehrt bis zur letzten Karte und schliesst', () => {
    tourZeigen();
    for (let i = 0; i < TOUR.length; i++) document.querySelector('#tour-weiter').click();
    return document.querySelector('#tour').classList.contains('on') === false
        || 'bleibt nach der letzten Karte stehen';
  });
  /* ⚠️ "auf der letzten Karte steht kein Ueberspringen mehr" ist seit dem
     12.08.2026 gegenstandslos: es gibt gar keinen Ueberspringen-Knopf mehr.
     Dass er weg ist, prueft weiter oben "sie laesst sich NICHT mehr
     ueberspringen". */
  t('die Einfuehrung kommt nur nach dem Registrieren', () => {
    /* Wer sich anmeldet, hat die App schon -- ihm die Einfuehrung noch einmal
       vorzusetzen waere eine Belaestigung. Quelltext-Pruefung, weil der Fall
       einen echten Anmeldevorgang braeuchte. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const a = js.indexOf('async function gateLos(');
    const b = js.indexOf('tourZeigen()', a);
    if (a < 0 || b < 0) return 'Stelle nicht gefunden';
    return /if \(!anmeldenModus\) tourZeigen\(\);/.test(js.slice(a, b + 40))
        || 'kommt auch beim Anmelden';
  });
  t('sie ist aus den Einstellungen erreichbar', () =>
    !!document.querySelector('#btn-hilfe') || 'kein Knopf in den Einstellungen');

  t('ein gemeldeter Grabstein behaelt seinen Todeszeitpunkt', () => {
    /* ⚠️ Hier stand `updated: Date.now()`. Ein Grabstein bekam beim Melden einen
       juengeren Stempel als den, mit dem er hochgeladen wurde -- und gewaenne damit
       gegen eine echte spaetere Wiederherstellung, die ihn eigentlich aufheben soll.

       Geprueft am Quelltext: grabMarkieren schreibt in die echte IndexedDB, und die
       laeuft in diesem Rahmen nicht mit (die Pruefungen ersetzen putCatch). Lieber
       eine ehrliche Quelltext-Pruefung als eine Verhaltenspruefung, die den Fall
       gar nicht herstellen kann. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const ab = js.indexOf('async function grabMarkieren(');
    if (ab < 0) return 'grabMarkieren nicht gefunden';
    const block = js.slice(ab, ab + 700);
    return (block.includes('alte.get(id)') && !/updated:\s*Date\.now\(\)/.test(block))
        || 'setzt den Stempel neu: ' + block.slice(0, 400);
  });

  /* ============ Einstellungen: die frueheren Vorhang-Pruefungen ============
     Hier standen rund 100 Zeilen fuer das Schliessen des Einstellungs-Vorhangs:
     Kreuz oben, Knopf unten, Griff, Wegtippen auf der Rueckseite und fuenf
     Pruefungen rund ums Herunterwischen samt der heiklen Abgrenzung zum Scrollen.

     Alle weg am 12.08.2026. Karls Ansage: die Einstellungen sind jetzt eine
     normale Seite wie "Neuer Fang" -- eine Seite schliesst man nicht, man geht
     auf eine andere Kachel.

     ⚠️ Diese Pruefungen sind nicht gefallen, weil etwas kaputtging, sondern weil
        das Gepruefte abgeschafft wurde. Der Unterschied gehoert festgehalten:
        haette man sie "repariert", prueften sie ein Verhalten, das niemand mehr
        will -- und stuenden dem naechsten Umbau im Weg, statt ihn abzusichern.
        Was von der Sache bleibt, steht unter "Drei Kacheln statt vier": dort
        wacht eine Pruefung darueber, dass vom Vorhang nichts uebrigblieb.

     ⚠️ Der Helfer bleibt, er wird weiter unten gebraucht. */
  const sheetAuf = () => { document.querySelector('#tab-set').click(); };

  // ---- Datenschutz ----
  t('Datenschutz-Knopf da', () => !!document.querySelector('#btn-datenschutz') || 'fehlt');
  t('Datenschutztext ist zuerst zu', () => document.querySelector('#ds-text').hidden === true || 'offen');
  t('Knopf oeffnet und schliesst', () => {
    const b = document.querySelector('#btn-datenschutz'), d = document.querySelector('#ds-text');
    b.click(); if (d.hidden) return 'ging nicht auf';
    b.click(); return d.hidden === true || 'ging nicht zu';
  });
  t('Mit Cloud beschreibt der Text den Server', () => {
    const s = datenschutzText();
    return (/Supabase/.test(s) && /Fangorten/.test(s) && !/Konto gibt es in dieser Fassung nicht/.test(s))
      || 'Text passt nicht zur konfigurierten Cloud';
  });
  // ⚠️ Mit Anmelde-Pflicht waere "ohne Konto bleibt alles lokal" schlicht falsch.
  t('Text behauptet keine Freiwilligkeit des Kontos mehr', () => {
    const s = datenschutzText();
    // "freiwillig" darf noch vorkommen -- Karte und Wetter SIND freiwillig.
    // Nur beim Konto waere es jetzt falsch.
    return (/Konto benötigt/.test(s) && !/Konto[^.]*freiwillig|freiwillig[^.]*Konto/.test(s))
      || 'Text spricht beim Konto noch von freiwillig';
  });
  t('Text erklaert den Offline-Betrieb', () =>
    /ohne Netz funktioniert/.test(datenschutzText()) || 'fehlt');
  t('Text nennt Rechtsgrundlage und Loeschweg', () => {
    const s = datenschutzText();
    return (/Art. 6/.test(s) && /Konto löschen/.test(s)) || 'fehlt';
  });
  t('Text nennt die drei Fremd-Dienste', () => {
    const s = datenschutzText();
    return (/OpenStreetMap/.test(s) && /Open-Meteo/.test(s) && /PEGELONLINE/.test(s)) || 'ein Dienst fehlt';
  });
  t('Text nennt die Betroffenenrechte', () => /Art. 15/.test(datenschutzText()) || 'fehlt');
  /* ============ Fehlermeldungen gehen nach Discord (10.08.2026) ============
     Karls Frage "wie kann ich die reports empfangen?" hat einen Auslöser in der
     Datenbank ergeben, der jede Meldung an einen Discord-Webhook schiebt.

     ⚠️ Damit verlaesst ein Meldungstext samt Geraeteangaben die EU. Das ist
     dieselbe Lage wie beim Essens-Foto in Gym-Log, und es gilt dieselbe Regel:
     es steht ehrlich drin oder es passiert nicht. Diese Pruefung ist der Grund,
     warum es nicht stillschweigend passieren kann. */
  t('Text nennt die Weitergabe der Fehlermeldungen', () => {
    const s = datenschutzText();
    return (/Discord/.test(s) && /USA/.test(s)) || 'Discord/USA fehlt im Datenschutztext';
  });
  t('und sagt dazu, dass ohne Meldung nichts hinausgeht', () => {
    // Sonst liest es sich, als ginge staendig etwas an Discord.
    const s = datenschutzText();
    return /Ohne Fehlermeldung geht dabei nichts|Without a report nothing leaves/.test(s)
        || 'die Einschraenkung fehlt';
  });
  /* ---- Karls Ansage vom 10.08.2026: Umfeld-Kasten raus aus dem Formular ----
     "nimm bei meldungen das: das wird mitgeschickt raus und wenn wir das unbedingt
     brauchen dann pack es in die datenschutzerklaerung."

     ⚠️ Die zweite Haelfte des Satzes ist die wichtigere. Der Kasten war die einzige
     Stelle, an der stand, was mitgeht. Faellt er weg, ohne dass es woanders
     vollstaendig steht, wird aus einer offenen Erhebung eine heimliche. */
  t('Der Umfeld-Kasten ist raus aus dem Meldeformular', () =>
    (!document.querySelector('#bug-umfeld')) || 'der Kasten steht noch da');
  t('Mitgeschickt wird trotzdem dasselbe', () => {
    const u = umfeldSammeln();
    return !!(u.fassung && u.geraet && u.bildschirm) || JSON.stringify(u);
  });
  t('Der Datenschutztext nennt jede einzelne Angabe, die mitgeht', () => {
    /* ⚠️ Abgeleitet aus umfeldSammeln(), nicht aus einer Liste von Hand: kommt
       spaeter ein Feld dazu, das hier keinen Eintrag hat, faellt diese Pruefung.
       Sonst waechst still mit, was niemand mehr nennt. */
    const wort = {
      fassung:         /Fassung der App/,
      geraet:          /User-Agent/,
      bildschirm:      /Bildschirmgröße/,
      netz:            /online oder offline/,
      sprache:         /Spracheinstellung/,
      installiert:     /Home-Bildschirm/,
      faenge:          /Anzahl deiner Fänge/,
      ungesichert:     /nicht gesicherter Fänge/,
      letzterAbgleich: /letzten Abgleichs/
    };
    const s = datenschutzDE();
    const fehlt = Object.keys(umfeldSammeln())
      .filter(k => !wort[k] || !wort[k].test(s));
    return fehlt.length === 0 || ('im Datenschutztext nicht genannt: ' + fehlt.join(', '));
  });
  t('und das Formular verweist auf ihn', () => {
    // Sonst muss man raten, wo es steht -- und rät nicht, sondern schickt einfach ab.
    const box = document.querySelector('#bug-form');
    return /Datenschutzerklärung/.test(box.textContent) || box.textContent.slice(0, 120);
  });
  t('Die Webhook-Adresse steht nirgends im Quelltext', () => {
    /* ⚠️ Das Repo ist oeffentlich. Wer die Adresse hat, kann in Karls Kanal
       schreiben. Sie gehoert in die Tabelle angel_konfig, die per API fuer
       niemanden lesbar ist -- nie in eine Datei, die auf GitHub landet. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    return (!/discord(app)?\.com\/api\/webhooks/.test(js + document.body.innerHTML))
        || 'eine Webhook-Adresse steht im Quelltext';
  });
  t('Kontakt ist gesetzt, kein Platzhalter mehr', () =>
    (!/BITTE EINTRAGEN/.test(KONTAKT) && KONTAKT.length > 5) || KONTAKT);
  t('Kontakt nennt einen Namen und eine E-Mail', () =>
    (/\w+\s+\w+/.test(KONTAKT) && /@/.test(KONTAKT)) || KONTAKT);
  // ⚠️ Karls Entscheidung: keine Wohnanschrift auf einer oeffentlichen Seite.
  t('Keine Wohnanschrift im Datenschutztext', () => {
    const s = datenschutzText();
    return (!/\b\d{5}\b/.test(s) && !/Lindenhof/i.test(s)) || 'Adresse steht drin';
  });
  t('Verantwortlicher steht im Text', () =>
    datenschutzText().includes(KONTAKT) || 'fehlt');

  // ---- Daten herunterladen ----
  t('Download-Knopf da', () => !!document.querySelector('#btn-export') || 'fehlt');
  t('Einlesen ist raus', () =>
    (!document.querySelector('#btn-import') && !document.querySelector('#in-import'))
      || 'Import noch da');
  // ⚠️ Der Download setzt Art. 20 DSGVO um und gehoert deshalb zum Datenschutz,
  // nicht zur Datensicherung -- gesichert wird ueber das Konto.
  // ⚠️ Der Behaelter heisst seit dem 12.08.2026 `#v-set .wrap` (normale Seite)
  //    statt `#sheet .inner` (Vorhang).
  t('Download steht unter der Datenschutzerklaerung', () => {
    const kinder = [...document.querySelector('#v-set .wrap').children];
    return (kinder.indexOf(document.querySelector('#btn-export'))
            > kinder.indexOf(document.querySelector('#btn-datenschutz'))) || 'steht davor';
  });
  /* ⚠️ Hier stand "Download steht vor dem Schliessen-Knopf". Den Knopf gibt es
     nicht mehr -- auf einer normalen Seite schliesst man nichts. Was die Pruefung
     eigentlich sicherte, war: der Download ist das LETZTE in den Einstellungen.
     Genau das prueft sie jetzt, ohne sich an einen Knopf zu haengen. */
  /* ⚠️ Seit Karls Ansage vom 12.08.2026 ("der ganze sync konto loeschen kram
     bitte nach ganz unten") ist der Konto-Block das Letzte, nicht mehr der
     Download. Geprueft wird deshalb beides: der Download steht am Ende des
     Datenschutz-Teils, und darunter kommt nur noch das Konto. */
  t('nach dem Download kommt nur noch der Konto-Block', () => {
    const kinder = [...document.querySelector('#v-set .wrap').children];
    const danach = kinder.slice(kinder.indexOf(document.querySelector('#btn-export')) + 1)
      .filter(k => k.nodeType === 1);
    return (danach.length === 1 && danach[0].id === 'konto')
        || ('danach kommt: ' + danach.map(k => k.id || k.tagName).join(', '));
  });
  /* ⚠️ "Konto loeschen" steckt in diesem Block. Ein Knopf, der alles loescht,
     darf nicht dort stehen, wo man beim Suchen nach etwas anderem vorbeikommt. */
  t('der Konto-Block steht ganz unten', () => {
    const kinder = [...document.querySelector('#v-set .wrap').children].filter(k => k.nodeType === 1);
    return (kinder[kinder.length - 1].id === 'konto')
        || ('unten steht: ' + (kinder[kinder.length - 1].id || kinder[kinder.length - 1].tagName));
  });
  t('und nicht mehr oben zwischen Palette und Hilfe', () => {
    const kinder = [...document.querySelector('#v-set .wrap').children].filter(k => k.nodeType === 1);
    return (kinder.indexOf(document.getElementById('konto'))
            > kinder.indexOf(document.getElementById('btn-hilfe')))
        || 'steht noch vor der Hilfe';
  });
  t('Datenschutztext verweist auf den Download', () =>
    /Meine Daten herunterladen/.test(datenschutzText()) || 'Text nennt ihn nicht');
  t('Datenschutztext spricht nicht mehr von Backup', () =>
    (!/Backup/.test(datenschutzText())) || 'Backup steht noch drin');

  // ==================== Layout auf schmalen Geraeten ====================
  // ⚠️ Fallstrick, der am 02.08. zwei Runden gekostet hat: Chrome headless
  // ignoriert auf diesem PC --window-size fuers Layout — eine Seite meldet bei
  // 320, 390 und 500 px immer dieselbe Breite. Verlaesslich messen laesst es
  // sich nur, indem die App in einem iframe mit fester Breite laeuft und dort
  // scrollWidth gegen die Fensterbreite geprueft wird.
  const imRahmen = (breite, was) => new Promise((fertig, schief) => {
    const f = document.createElement('iframe');
    f.style.cssText = `width:${breite}px;height:720px;border:0;position:absolute;left:-9999px`;
    f.src = 'index.html';
    f.onload = () => {
      // Der App eine Runde geben, damit sie fertig gezeichnet hat.
      setTimeout(() => {
        try { const r = was(f.contentWindow, f.contentDocument); f.remove(); fertig(r); }
        catch (e){ f.remove(); schief(e); }
      }, 350);
    };
    f.onerror = () => { f.remove(); schief(new Error('iframe laedt nicht')); };
    document.body.appendChild(f);
  });

  for (const breite of [320, 360, 390]){
    ta(`Statistik passt auf ${breite} px`, async () => {
      return await imRahmen(breite, (w, d) => {
        w.go('stats');
        const ueber = d.documentElement.scrollWidth - w.innerWidth;
        return ueber <= 1 || (ueber + ' px zu breit');
      });
    });
  }
  ta('der Baukasten steht auf 320 px vollstaendig da', async () => {
    return await imRahmen(320, (w, d) => {
      w.go('stats');
      const fehlt = ['#st-art', '#st-x', '#st-teilen', '#st-gewaesser', '#st-speichern']
        .filter(s => { const el = d.querySelector(s); return !el || el.getBoundingClientRect().width < 1; });
      return fehlt.length === 0 || ('nicht sichtbar: ' + fehlt.join(', '));
    });
  });
  ta('kein Bedienelement ragt auf 320 px heraus', async () => {
    return await imRahmen(320, (w, d) => {
      const raus = [...d.querySelectorAll('#v-stats .in, #v-stats .btn, #v-stats .chip')]
        .filter(el => el.getBoundingClientRect().right > w.innerWidth + 1)
        .map(el => el.id || el.textContent.trim().slice(0, 18));
      return raus.length === 0 || raus.join(' | ');
    });
  });
  ta('das Diagramm bleibt auf 320 px im Bild', async () => {
    return await imRahmen(320, (w, d) => {
      w.go('stats');
      const svg = d.querySelector('#stats-body svg.kurve');
      if (!svg) return true;                       // ohne Faenge gibt es keins — kein Fehler
      return svg.getBoundingClientRect().right <= w.innerWidth + 1
          || 'Diagramm ragt heraus';
    });
  });

  // ---- Am grossen Bildschirm mehrere Auswertungen nebeneinander ----
  // Karls Ansage vom 07.08.: "mach die statistik auf dem pc kleiner das mehrere
  // nebeneinander passen." Die gespeicherten Auswertungen stehen dort neben der
  // eingestellten -- genau dafuer gibt es sie.
  // ⚠️ state ist im iframe ein `const` auf oberster Ebene und damit KEINE
  // Eigenschaft von window -- w.state ist undefined. Ueber w.eval laeuft der
  // Code dagegen im globalen Bereich des iframes und sieht die Bindung.
  const SEED = `
    state.catches = [
      { id:'a', entwurf:false, art:'Hecht',  when:'2026-07-15T06:30', ts:Date.now(), tiefe:2, wasser:12, koeder:'Wobbler', farben:['Firetiger'], photos:[] },
      { id:'b', entwurf:false, art:'Barsch', when:'2026-07-16T18:30', ts:Date.now(), tiefe:4, wasser:18, koeder:'Spinner', farben:['Motoroil'], photos:[] },
      { id:'c', entwurf:false, art:'Hecht',  when:'2026-07-17T09:30', ts:Date.now(), tiefe:3, wasser:15, koeder:'Wobbler', farben:['Firetiger'], photos:[] }
    ];
    state.auswertungen = [
      { id:'s1', name:'Nach Tiefe',  art:'', x:'tiefe',  teilen:'',       gewaesser:'', zeit:'alles' },
      { id:'s2', name:'Nach Waerme', art:'', x:'wasser', teilen:'',       gewaesser:'', zeit:'alles' },
      { id:'s3', name:'Nach Farbe',  art:'', x:'art',    teilen:'farbe',  gewaesser:'', zeit:'alles' }
    ];
    state.stats = { gewaesser:'', art:'', zeit:'alles', x:'stunde', teilen:'', aktiv:null };
    go('stats'); renderStats();
  `;
  const mitDreien = (w) => w.eval(SEED);

  ta('am PC stehen mehrere Auswertungen da', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      const n = d.querySelectorAll('#stats-body svg.kurve').length;
      return n === 4 || ('Diagramme: ' + n);       // die eingestellte + drei gespeicherte
    });
  });
  ta('am PC stehen sie nebeneinander, nicht untereinander', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      const k = [...d.querySelectorAll('#stats-body > .card')].filter(c => c.querySelector('svg.kurve'));
      if (k.length < 2) return 'zu wenige Karten';
      const oben = k[0].getBoundingClientRect(), zwei = k[1].getBoundingClientRect();
      return Math.abs(oben.top - zwei.top) < 2 || 'zweite Karte sitzt darunter';
    });
  });
  /* ⚠️ Hier stand "am Handy bleibt es bei einer" -- so war es bis zum 08.08.2026
     gebaut, mit der Begruendung "alles andere waere Scrollen". Karl hat die
     gespeicherten Auswertungen ausdrucklich auch am Handy verlangt: Scrollen ist
     dort das normale Mittel, und ohne sie muss man jede einzeln laden. */
  ta('am Handy stehen sie untereinander, nicht nur eine', async () => {
    return await imRahmen(390, (w, d) => {
      mitDreien(w);
      const n = d.querySelectorAll('#stats-body svg.kurve').length;
      return n > 1 || ('Diagramme: ' + n);
    });
  });
  ta('und sie stehen wirklich untereinander, nicht nebeneinander', async () => {
    return await imRahmen(390, (w, d) => {
      mitDreien(w);
      const karten = [...d.querySelectorAll('#stats-body > .card')]
        .filter(c => c.querySelector('svg.kurve'));
      if (karten.length < 2) return 'nur ' + karten.length + ' Karten';
      const a = karten[0].getBoundingClientRect(), b = karten[1].getBoundingClientRect();
      // Untereinander heisst: die zweite faengt unterhalb der ersten an.
      return b.top >= a.bottom - 1 || `zweite beginnt bei ${Math.round(b.top)}, erste endet bei ${Math.round(a.bottom)}`;
    });
  });
  ta('am Handy ragt dabei nichts heraus', async () => {
    return await imRahmen(390, (w, d) => {
      mitDreien(w);
      const ueber = d.documentElement.scrollWidth - w.innerWidth;
      return ueber <= 1 || (ueber + ' px zu breit');
    });
  });
  ta('die geladene Auswertung steht nicht doppelt da', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      w.eval("auswertungLaden('s1')");
      const titel = [...d.querySelectorAll('#stats-body h2')].map(h => h.textContent);
      return titel.filter(x => /Wassertiefe|Nach Tiefe/.test(x)).length === 1 || titel.join(' | ');
    });
  });
  ta('jedes Diagramm hat seine eigene Ablesehilfe', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      const svgs = d.querySelectorAll('#stats-body svg.kurve').length;
      const lupen = d.querySelectorAll('#stats-body .lupe').length;
      return svgs === lupen || `${svgs} Diagramme, ${lupen} Ablesehilfen`;
    });
  });
  ta('eine gespeicherte Auswertung bringt ihre eigenen Filter mit', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      // s3 teilt nach Koederfarbe auf -- nur dieses eine Bild darf eine Legende haben,
      // die eingestellte und die beiden anderen nicht.
      const mitLeg = [...d.querySelectorAll('#stats-body > .card')]
        .filter(c => c.querySelector('.leg')).length;
      return mitLeg === 1 || ('Karten mit Legende: ' + mitLeg);
    });
  });
  // Bei fuenf Auswertungen nebeneinander waere derselbe Absatz fuenfmal kein
  // Hinweis mehr, sondern Rauschen.
  ta('der Verteilungs-Hinweis steht genau einmal', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      const h = d.querySelector('#stats-body').innerHTML;
      const n = (h.match(/nicht, was besser fängt/g) || []).length;
      return n === 1 || ('steht ' + n + ' mal da');
    });
  });
  ta('kartenspezifische Hinweise stehen weiter je Karte', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      // Von den vier Bildern hat nur das nach Fischart keine natuerliche Reihenfolge.
      const h = d.querySelector('#stats-body').innerHTML;
      const n = (h.match(/keine natürliche Reihenfolge/g) || []).length;
      return n === 1 || ('steht ' + n + ' mal da');
    });
  });
  ta('die Kacheln laufen ueber die ganze Breite', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      const k = d.querySelector('#stats-body .tiles');
      const karte = d.querySelector('#stats-body > .card:not(.voll)');
      if (!k || !karte) return 'Kacheln oder Diagrammkarte fehlt';
      return k.getBoundingClientRect().width > karte.getBoundingClientRect().width
          || 'Kacheln sind nicht breiter als eine Diagrammkarte';
    });
  });
  ta('die Bedienelemente wachsen nicht mit', async () => {
    return await imRahmen(1400, (w, d) => {
      w.go('stats');
      const karte = d.querySelector('#v-stats > .wrap > .card');
      return karte.getBoundingClientRect().width <= 780
          || ('Baukasten ist ' + Math.round(karte.getBoundingClientRect().width) + ' px breit');
    });
  });
  ta('am PC ragt nichts heraus', async () => {
    return await imRahmen(1200, (w, d) => {
      mitDreien(w);
      return d.documentElement.scrollWidth - w.innerWidth <= 1
          || ((d.documentElement.scrollWidth - w.innerWidth) + ' px zu breit');
    });
  });

  // ==================== Ladebildschirm ====================
  // ⚠️ Das eigentliche Risiko hier ist nicht, dass er schlecht aussieht, sondern dass er
  // stehen bleibt: er deckt die ganze Flaeche ab, also waere die App dann unbedienbar.
  // Deshalb pruefen die Faelle unten vor allem, dass er WEGGEHT — auch dann, wenn init()
  // nie durchlaeuft.
  // ==================== Gewaesser aus dem Standort ====================
  // Karls Ansage vom 08.08. Geprueft wird die Auswertung der Antwort, nicht der
  // Netzaufruf -- Overpass ist ein Spendendienst und gehoert nicht in eine
  // Pruefung, die bei jedem Durchlauf mitlaeuft.
  const ovEl = (name, tags, geom) => ({ tags: Object.assign({ name }, tags), geometry: geom });
  const beiHH = (dlat) => [{ lat: 53.5411 + dlat, lon: 9.9737 }];

  t('das naechste benannte Gewaesser gewinnt', () => {
    const j = { elements: [ovEl('Ferner Bach', { waterway:'stream' }, beiHH(0.02)),
                           ovEl('Naher Fluss', { waterway:'river' },  beiHH(0.002))] };
    const r = gewaesserAuswerten(j, 53.5411, 9.9737);
    return r[0].name === 'Naher Fluss' || JSON.stringify(r.map(x => x.name));
  });
  /* ⚠️ Der Fall, der die Gewichtung ausgeloest hat: an der Elbe bei Hamburg liegt
     das Fleet "Guanofleet" naeher als die Norderelbe. Nach reiner Entfernung
     gewaenne der Graben -- gemeint ist aber der Fluss. */
  t('ein Fluss sticht einen naeheren Graben', () => {
    const j = { elements: [ovEl('Guanofleet', { waterway:'ditch' }, beiHH(0.0019)),
                           ovEl('Norderelbe', { waterway:'river' }, beiHH(0.0021))] };
    const r = gewaesserAuswerten(j, 53.5411, 9.9737);
    return r[0].name === 'Norderelbe' || JSON.stringify(r.map(x => `${x.name}/${Math.round(x.rang)}`));
  });
  /* ⚠️ Der Fall, an dem der erste Entwurf gescheitert ist: mitten auf dem
     Steinhuder Meer findet around den See nicht, weil es zur Uferlinie misst.
     Objekte aus is_in kommen ohne Geometrie -- das heisst "ich stehe drin". */
  t('mittendrin schlaegt jede Entfernung', () => {
    const j = { elements: [ovEl('Kleiner Graben', { waterway:'ditch' }, beiHH(0.0001)),
                           ovEl('Steinhuder Meer', { natural:'water' }, null)] };
    const r = gewaesserAuswerten(j, 52.46, 9.33);
    return (r[0].name === 'Steinhuder Meer' && r[0].drin && r[0].m === 0)
        || JSON.stringify(r.map(x => `${x.name}/drin=${x.drin}`));
  });
  t('Verwaltungsgrenzen fallen raus', () => {
    // is_in liefert auch Land, Bundesland und Gemeinde. Ohne diesen Filter stuende
    // "Deutschland" als Gewaesser im Formular.
    const j = { elements: [ovEl('Deutschland', { 'admin_level':'2' }, null),
                           ovEl('Niedersachsen', { boundary:'administrative' }, null),
                           ovEl('Steinhuder Meer', { natural:'water' }, null)] };
    const r = gewaesserAuswerten(j, 52.46, 9.33);
    return (r.length === 1 && r[0].name === 'Steinhuder Meer')
        || JSON.stringify(r.map(x => x.name));
  });
  t('ein Fluss in vielen Abschnitten steht nur einmal da', () => {
    const j = { elements: [ovEl('Weser', { waterway:'river' }, beiHH(0.01)),
                           ovEl('Weser', { waterway:'river' }, beiHH(0.002)),
                           ovEl('Weser', { waterway:'river' }, beiHH(0.03))] };
    const r = gewaesserAuswerten(j, 53.5411, 9.9737);
    return (r.length === 1 && Math.round(r[0].m) < 250)
        || JSON.stringify(r.map(x => `${x.name}/${Math.round(x.m)}m`));
  });
  t('Namenloses zaehlt nicht', () => {
    const j = { elements: [{ tags: { waterway:'river' }, geometry: beiHH(0.0001) },
                           ovEl('Mit Namen', { waterway:'river' }, beiHH(0.01))] };
    const r = gewaesserAuswerten(j, 53.5411, 9.9737);
    return (r.length === 1 && r[0].name === 'Mit Namen') || JSON.stringify(r.map(x => x.name));
  });
  t('hoechstens sechs Vorschlaege', () => {
    const j = { elements: Array.from({ length: 12 },
      (_, i) => ovEl('Gewaesser ' + i, { waterway:'river' }, beiHH(0.001 * (i + 1)))) };
    return gewaesserAuswerten(j, 53.5411, 9.9737).length === 6
        || gewaesserAuswerten(j, 53.5411, 9.9737).length;
  });
  t('das Gewaesser steht unten bei den geholten Werten', () => {
    // Karls Ansage: "das muss auch runter zu den anderen sachen".
    const feld = document.querySelector('#f-gewaesser');
    return (feld && feld.closest('.card') === document.querySelector('#wx-info').closest('.card'))
        || 'steht nicht in der Bedingungen-Karte';
  });
  t('Entfernungen lesen sich rund', () => {
    const f = [gwEntfernung(213), gwEntfernung(940), gwEntfernung(1113), gwEntfernung(2990)];
    return JSON.stringify(f) === JSON.stringify(['210 m', '940 m', '1,1 km', '3,0 km'])
        || JSON.stringify(f);
  });

  // ==================== Symbol auf dem Home-Bildschirm ====================
  t('apple-touch-icon ist eigens angegeben', () => {
    const l = document.querySelector('link[rel="apple-touch-icon"]');
    return (l && /apple-touch-icon\.png/.test(l.getAttribute('href')))
        || (l ? l.getAttribute('href') : 'keine Zeile da');
  });
  t('und in 180x180, der Groesse die iOS anlegt', () => {
    const l = document.querySelector('link[rel="apple-touch-icon"]');
    return (l && l.getAttribute('sizes') === '180x180') || (l ? l.getAttribute('sizes') : '—');
  });

  // ==================== Das Foto im Ladebildschirm ====================
  // Karls Ansage vom 08.08.: vollflaechige Angelfotos, bei jedem Oeffnen ein anderes.
  /* ==================== Neue Fassung kommt auch an ====================
     Karls Meldung vom 08.08.: „ich habe es bei mir auf dem handy nicht, mein kollege
     schon." Der neue Service Worker uebernimmt zwar sofort, laedt die bereits offene
     Seite aber nicht neu -- und eine PWA am iPhone liegt wochenlang im App-Switcher.
     Geprueft am Quelltext: der Lebenszyklus laesst sich in diesem Rahmen nicht
     nachstellen (kein echter Service Worker unter file:// bzw. im iframe). */
  t('beim Start wird nach einer neuen Fassung gesehen', () => {
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    return /reg\.update\(\)/.test(js) || 'kein update() nach der Registrierung';
  });
  t('auch beim Zurueckkommen aus dem Hintergrund', () => {
    // Bei einer PWA ist das der haeufigste "Start" -- ohne das bliebe sie ewig alt.
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    return /visibilitychange/.test(js) && /document\.hidden/.test(js)
        || 'kein Blick beim Zurueckkommen';
  });
  t('ein neuer Worker laedt die Seite neu', () => {
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    return /controllerchange/.test(js) && /location\.reload\(\)/.test(js)
        || 'kein Neuladen bei Worker-Wechsel';
  });
  t('aber nicht mitten im Erfassen', () => {
    /* ⚠️ Wer gerade einen Fang eintippt, verloere den sichtbaren Stand. Der Entwurf
       waere gesichert, ein Neuladen unter den Haenden ist trotzdem ein Uebergriff. */
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    const ab = js.indexOf('controllerchange');
    const block = js.slice(ab, ab + 700);
    return (/formHatInhalt\(\)/.test(block) && /state\.view === 'new'/.test(block))
        || 'laedt auch waehrend der Erfassung neu';
  });
  t('und nicht in einer Schleife', () => {
    // Ein Worker, der beim Aktivieren erneut wechselt, koennte die Seite endlos neu laden.
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    const ab = js.indexOf('controllerchange');
    return /neuGeladen/.test(js.slice(Math.max(0, ab - 300), ab + 700))
        || 'kein Riegel gegen die Endlosschleife';
  });

  /* ==================== Ladeleiste oben (Karls Ansage vom 08.08.) ====================
     „das logo soll in der mitte weg dafuer aber eine loading leiste ganz oben etwas
     groesser und mit prozenten." */
  t('das Zeichen in der Mitte ist raus', () =>
    !document.querySelector('#splash img.zeichen') || 'Zeichen steht noch da');
  t('die Leiste steht ganz unten', () => {
    const unten = document.querySelector('#splash .unten');
    if (!unten) return 'kein unterer Block';
    return unten.contains(document.querySelector('#splash .balken'))
        || 'die Leiste haengt nicht im unteren Block';
  });
  t('in der Mitte steht nichts mehr', () => {
    // Karls Ansage: Zeichen und Name raus -- uebrig bleibt das Foto.
    const reste = ['#splash .mitte', '#splash .name', '#splash img.zeichen']
      .filter(sel => document.querySelector(sel));
    return reste.length === 0 || ('noch da: ' + reste.join(', '));
  });
  t('sie laesst Platz fuer den Home-Strich', () => {
    // Bei einer vom Home-Bildschirm gestarteten App laeuft der Schirm bis unter den
    // Home-Strich. Ohne env(safe-area-inset-bottom) laege die Leiste teils darunter.
    const css = Array.from(document.styleSheets)
      .flatMap(sh => { try { return Array.from(sh.cssRules); } catch (e) { return []; } })
      .map(r => r.cssText).join(' ');
    return /#splash \.unten[^}]*safe-area-inset-bottom/.test(css)
        || 'kein Abstand zum Home-Strich';
  });
  t('sie ist deutlich groesser als der alte Strich', () => {
    const h = parseFloat(getComputedStyle(document.querySelector('#splash .balken')).height);
    return h >= 6 || ('nur ' + h + ' px hoch');
  });
  t('sie laeuft ueber die ganze Breite', () => {
    const b = document.querySelector('#splash .balken').getBoundingClientRect();
    return b.width > window.innerWidth * 0.7 || ('nur ' + Math.round(b.width) + ' px breit');
  });
  t('eine Prozentzahl steht dabei', () => {
    const el = document.querySelector('#splash .prozent');
    return (el && /\d+\s*%/.test(el.textContent)) || (el ? el.textContent : 'keine Zahl');
  });
  t('die Fuellung folgt der Zahl, nicht einer Animation', () => {
    /* ⚠️ Vorher lief ein Strich endlos hin und her -- das zeigte Bewegung, keinen Stand.
       Jetzt steuert die Breite den Stand. */
    const st = getComputedStyle(document.querySelector('#splash .balken i'));
    return st.animationName === 'none' || ('laeuft noch als Animation: ' + st.animationName);
  });
  t('splashStand setzt Breite, Zahl und Vorlese-Wert zusammen', () => {
    splashStand(42);
    const i = document.querySelector('#splash .balken i');
    const p = document.querySelector('#splash .prozent');
    const b = document.querySelector('#splash .balken');
    const ok = i.style.width === '42%' && /42\s*%/.test(p.textContent)
            && b.getAttribute('aria-valuenow') === '42';
    return ok || `${i.style.width} / ${p.textContent} / ${b.getAttribute('aria-valuenow')}`;
  });
  t('sie bleibt in ihren Grenzen', () => {
    splashStand(-20);
    const unten = document.querySelector('#splash .balken i').style.width;
    splashStand(300);
    const oben = document.querySelector('#splash .balken i').style.width;
    return (unten === '0%' && oben === '100%') || (unten + ' / ' + oben);
  });
  t('der Ticker laeuft nur bis 96 Prozent', () => {
    /* ⚠️ Die letzten Prozent gehoeren dem tatsaechlichen Fertigwerden. Stuende die Leiste
       auf 100, waehrend die App noch arbeitet, waere das eine Luege, die jeder sieht. */
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    // ⚠️ Kein [^)]* im Muster -- der Ausdruck enthaelt selbst Klammern, daran ist das
    // erste Muster gescheitert. Geprueft wird schlicht das Ende des Ausdrucks.
    return /SPLASH_MINDESTENS \* 100, 96\)/.test(js) || 'kein Deckel bei 96 %';
  });
  t('die Hoechstzeit raeumt den Ticker mit ab', () => {
    // Sonst zaehlt alle 60 ms etwas weiter, das niemand mehr sieht -- fuer immer.
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    const ab = js.indexOf('}, SPLASH_HOECHSTENS)');
    if (ab < 0) return 'der Wecker haengt nicht an SPLASH_HOECHSTENS';
    const block = js.slice(Math.max(0, ab - 500), ab);
    return /clearInterval\(splashTicker\)/.test(block) || 'Ticker laeuft weiter';
  });

  t('der Ladebildschirm hat ein Foto', () => {
    const f = document.querySelector('#splash .foto');
    return (f && /^splash-[1-6]\.jpg$/.test(f.getAttribute('src') || ''))
        || (f ? ('src ist "' + f.getAttribute('src') + '"') : 'kein Foto-Element');
  });
  t('das Foto liegt hinter der Leiste', () => {
    // Laege es davor, waere der Stand je nach Bild mal sichtbar und mal nicht.
    const foto  = getComputedStyle(document.querySelector('#splash .foto')).zIndex;
    const unten = getComputedStyle(document.querySelector('#splash .unten')).zIndex;
    return Number(unten) > Number(foto) || (`Foto ${foto}, Leiste ${unten}`);
  });
  t('es deckt die ganze Flaeche', () => {
    const st = getComputedStyle(document.querySelector('#splash .foto'));
    return (st.objectFit === 'cover' && st.position === 'absolute')
        || (st.objectFit + ' / ' + st.position);
  });
  /* ⚠️ Der Punkt, an dem ein Ladebildschirm mit Foto schlechter wird als einer ohne:
     wartet er auf das Bild, steht er beim ersten Start ohne Cache sekundenlang leer.
     Deshalb faengt das Foto unsichtbar an und blendet sich per onload ein. */
  t('das Foto faengt unsichtbar an', () => {
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const hatOnload = /el\.onload\s*=/.test(js) && /classList\.add\('da'\)/.test(js);
    return hatOnload || 'kein Einblenden per onload -- der Schirm wartet womoeglich';
  });
  t('die Rotation zaehlt reihum, nicht zufaellig', () => {
    // Bei sechs Bildern faellt Zufall auf: dreimal dasselbe wirkt kaputt, nicht abwechslungsreich.
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const ab = js.indexOf('angellog-splash-nr');
    if (ab < 0) return 'kein Zaehler im Speicher';
    return (!/Math\.random/.test(js.slice(Math.max(0, ab - 500), ab + 500)))
        || 'zaehlt zufaellig statt reihum';
  });
  t('der Zaehler bleibt im Bereich der sechs Bilder', () => {
    const n = Number(localStorage.getItem('angellog-splash-nr'));
    return (n >= 0 && n <= 5) || ('Zaehler steht auf ' + n);
  });
  t('auf einem Foto wird die Schrift hell gesetzt', () => {
    // Auf den vier hellen Paletten ist --txt fast schwarz und verschwaende auf dem Bild.
    const css = Array.from(document.styleSheets)
      .flatMap(sh => { try { return Array.from(sh.cssRules); } catch (e) { return []; } })
      .map(r => r.cssText).join(' ');
    return /#splash\.mitFoto \.prozent/.test(css) || 'keine eigene Schriftfarbe fuer Fotos';
  });
  t('ein Schleier sorgt fuer Lesbarkeit', () =>
    !!document.querySelector('#splash .schleier') || 'kein Schleier');

  t('der Ladebildschirm steht vor der Log-Ansicht im Markup', () => {
    const h = document.documentElement.innerHTML;
    const s = h.indexOf('id="splash"'), l = h.indexOf('id="v-log"');
    return (s > -1 && l > -1 && s < l) || ('splash bei ' + s + ', v-log bei ' + l);
  });
  t('das Zeichen steht in der Kopfzeile', () => {
    // ⚠️ Der Kopf sitzt seit dem 12.08.2026 als #kopf ueber allen drei Sammel-
    //    Ansichten, nicht mehr in #v-log. Sonst haette er beim Umschalten auf
    //    Karte oder Auswertung gefehlt.
    const img = document.querySelector('#kopf h1 img');
    return (img && /icon-192/.test(img.getAttribute('src'))) || 'kein Bild in der Kopfzeile';
  });
  t('setPalette schreibt vier Farben fuers Fruehskript', () => {
    setPalette('nebel', false);
    const f = (localStorage.getItem('angellog-splash') || '').split(' ');
    return (f.length === 4 && f[0] === PALETTEN['nebel'][1].bg && f[3] === PALETTEN['nebel'][1].line)
        || ('Abbild ist "' + f.join(' ') + '"');
  });
  t('das Abbild folgt auch einer Vorschau ohne Speichern', () => {
    // speichern===false kommt beim Durchtippen der Paletten vor. Wuerde das Abbild dabei
    // stehen bleiben, zeigte der Schirm beim naechsten Start eine Farbe, die nicht an ist.
    setPalette('papier', false);
    const a = localStorage.getItem('angellog-splash');
    setPalette('mitternacht', false);
    const anders = a !== localStorage.getItem('angellog-splash');
    setPalette('tiefes-wasser', false);   // aufraeumen, die iframes unten lesen dasselbe Abbild
    return anders || 'Abbild hat sich nicht geaendert';
  });

  // Eigener Rahmen: andere Quelldatei und laengeres Warten als imRahmen.
  const imRahmenVon = (datei, warten, was) => new Promise((fertig, schief) => {
    const f = document.createElement('iframe');
    f.style.cssText = 'width:390px;height:720px;border:0;position:absolute;left:-9999px';
    f.src = datei;
    f.onload = () => setTimeout(() => {
      try { const r = was(f.contentWindow, f.contentDocument); f.remove(); fertig(r); }
      catch (e){ f.remove(); schief(e); }
    }, warten);
    f.onerror = () => { f.remove(); schief(new Error(datei + ' laedt nicht')); };
    document.body.appendChild(f);
  });

  /* ⚠️ Karls Ansage vom 08.08.: der Schirm war „nur so ne millisekunde da". Er steht
     jetzt eine Mindestzeit (SPLASH_MINDESTENS). Die beiden Pruefungen unten fassen beide
     Seiten an: frueh muss er noch stehen, spaeter muss er weg sein. Nur das Zweite zu
     pruefen liesse offen, ob die Mindestzeit ueberhaupt wirkt. */
  ta('kurz nach dem Start steht er noch (Mindestzeit)', async () => {
    return await imRahmenVon('index.html', 500, (w, d) => {
      const s = d.getElementById('splash');
      return !s.classList.contains('weg')
          || 'schon nach 500 ms weg -- die Mindestzeit greift nicht';
    });
  });
  ta('nach der Mindestzeit ist der Ladebildschirm weg', async () => {
    return await imRahmenVon('index.html', 2400, (w, d) => {
      const s = d.getElementById('splash');
      return s.classList.contains('weg') || 'steht nach 2,4 s immer noch da';
    });
  });
  t('die Mindestzeit liegt unter der Hoechstzeit', () => {
    /* ⚠️ Laege sie darueber, raeumte die Hoechstzeit den Schirm weg, waehrend die
       Mindestzeit ihn noch halten will -- zwei Uhren, die gegeneinander laufen. */
    const js = Array.from(document.scripts).map(s => s.textContent).join(' ');
    const a = js.match(/SPLASH_MINDESTENS\s*=\s*(\d+)/);
    const b = js.match(/SPLASH_HOECHSTENS\s*=\s*(\d+)/);
    if (!a) return 'SPLASH_MINDESTENS nicht gefunden';
    if (!b) return 'SPLASH_HOECHSTENS nicht gefunden';
    return Number(a[1]) < Number(b[1])
        || ('Mindestzeit ' + a[1] + ' ms >= Hoechstzeit ' + b[1] + ' ms');
  });
  t('er wartet auf den ersten Abgleich', () => {
    /* ⚠️ Hier stand das Gegenteil ("er wartet nicht auf den Speicher"): das Wegnehmen
       musste VOR "await reload()" stehen, damit der Schirm an nichts haengt.

       Karls Ansage vom 11.08.2026 dreht das um -- "mach das bitte waehrenddessen das
       intro laedt und wenn es laenger dauert soll auch das intro laenger dauern" -- und
       der Grund ist neu: seit demselben Tag holt der Abgleich beim Start den ganzen
       Bestand. Ginge der Schirm vorher weg, saehe man die Liste unvollstaendig und die
       Faenge purzelten hinterher hinein.

       ⚠️ Der alte Einwand ist damit nicht erledigt, sondern nur woanders aufgehoben:
       SPLASH_HOECHSTENS im Kopf der Datei. Die zwei Pruefungen mit haengt.html unten
       fassen genau das an -- Quelltext-Reihenfolge allein wuerde die Sperre nicht sehen. */
    const js = Array.from(document.scripts).map(s => s.textContent).join('\n');
    const ab = js.indexOf('(async function init(){');
    if (ab < 0) return 'init()-Block nicht gefunden';
    /* ⚠️ Gesucht wird der Aufruf, nicht der Name -- zum zweiten Mal heute dieselbe Falle:
       im Kommentar direkt darueber steht "Hier stand splashWeg()", und ein schlichtes
       indexOf findet den. Die Pruefung meldete daraufhin "Wegnehmen bei 809" und faellt,
       obwohl die Reihenfolge stimmte. Deshalb: Zeilenanfang und Semikolon. */
    const block = js.slice(ab);
    const weg  = block.search(/\n\s*splashWeg\(\);/);
    const sync = block.search(/\n\s*else await syncJetzt\(true\);/);
    return (weg > -1 && sync > -1 && weg > sync)
        || ('in init(): Wegnehmen bei ' + weg + ', await syncJetzt bei ' + sync);
  });
  ta('und er faengt keine Tipper mehr ab', async () => {
    return await imRahmenVon('index.html', 2900, (w, d) => {
      const s = d.getElementById('splash');
      /* ⚠️ Geprueft wird `pointer-events` -- das wirkt sofort mit der Klasse. Deckkraft
         und `visibility` haengen an einer Transition, und Transitions arbeitet Chrome
         unter virtueller Zeit nicht ab; sie waeren hier immer 1 bzw. visible. Beide
         stehen deshalb als Regel-Pruefungen daneben. */
      const st = w.getComputedStyle(s);
      return (st.pointerEvents === 'none' && s.classList.contains('weg'))
          || ('pointer-events ' + st.pointerEvents + ', Klassen "' + s.className + '"');
    });
  });
  t('und er ist danach auch fuer Vorlesehilfen weg', () => {
    /* ⚠️ Geprueft an der CSS-Regel, nicht am Verhalten: `visibility` schaltet mit
       Verzoegerung um (transition ... visibility 0s .26s, damit das Bild nicht abreisst),
       und diese Verzoegerung arbeitet Chrome unter virtueller Zeit nicht ab. Lieber eine
       ehrliche Regel-Pruefung als eine Verhaltenspruefung, die im Rahmen nie gruen wird. */
    const regeln = Array.from(document.styleSheets)
      .flatMap(sh => { try { return Array.from(sh.cssRules); } catch (e) { return []; } })
      .map(r => r.cssText).filter(t2 => t2.indexOf('#splash.weg') === 0);
    return (regeln.length > 0 && /visibility:\s*hidden/.test(regeln.join(' ')))
        || ('Regeln: ' + regeln.join(' | '));
  });
  ta('die Hoechstzeit greift, wenn init() nie durchlaeuft', async () => {
    // kaputt.html ist dieselbe App mit absichtlich geworfenem Fehler in init().
    // Ohne den Wecker im Kopf bliebe der Schirm hier fuer immer stehen.
    return await imRahmenVon('kaputt.html', 6600, (w, d) => {
      const s = d.getElementById('splash');
      return s.classList.contains('weg') || 'Schirm klebt — App waere gesperrt';
    });
  });

  /* ====== Der Schirm wartet auf den Abgleich -- aber nicht ewig (11.08.2026) ======
     haengt.html ist dieselbe App, in der der erste Abgleich nie fertig wird. Genau das
     passiert in echt: kein Empfang am Wasser, ein Hotspot ohne Anmeldung, ein Server,
     der die Verbindung offen laesst statt abzulehnen.

     ⚠️ Beide Seiten muessen geprueft werden. Nur "er wartet" hiesse, eine App zu bauen,
     die sich bei schlechtem Netz hinter einem Foto selbst sperrt. Nur "er geht weg"
     hiesse, Karls Ansage gar nicht umgesetzt zu haben. */
  ta('bei haengendem Abgleich steht er ueber die Mindestzeit hinaus', async () => {
    return await imRahmenVon('haengt.html', 2400, (w, d) => {
      const s = d.getElementById('splash');
      return !s.classList.contains('weg')
          || 'schon nach 2,4 s weg -- er wartet nicht auf den Abgleich';
    });
  });
  ta('aber die Hoechstzeit holt ihn trotzdem weg', async () => {
    return await imRahmenVon('haengt.html', 6600, (w, d) => {
      const s = d.getElementById('splash');
      return s.classList.contains('weg')
          || 'Schirm klebt am haengenden Abgleich — die App waere gesperrt';
    });
  });
  ta('die Fangliste liegt hinter dem Schirm, nicht unter ihm', async () => {
    return await imRahmenVon('index.html', 500, (w, d) => {
      const s = d.getElementById('splash');
      return w.getComputedStyle(s).position === 'fixed'
          && d.documentElement.scrollWidth - w.innerWidth <= 1
          || 'Schirm schiebt das Layout';
    });
  });

  /* ====== Die Führung durch den ersten Fang (12.08.2026) ======
     Karls Ansage: der Fang soll einmal mit Hilfe erstellt werden, mit Umkreisung,
     der Rest abgedunkelt und nicht antippbar.

     ⚠️ Die wichtigsten Pruefungen hier sind nicht "sie geht an", sondern **"sie
     laesst wieder raus"**. Eine Fuehrung, die haengenbleibt, sperrt die App
     genauso zu wie ein Ladebildschirm, der nicht weggeht -- und dann sitzt jemand
     hinter einem grauen Schleier vor seiner eigenen Fangliste. */
  const fuAus = () => { try { fuehrungBeenden(); } catch (e) {} tourSchliessen(); go('log'); };

  t('die Fuehrung haengt an der Drumherum-Karte', () => {
    const k = TOUR.filter(x => x.fuehrung);
    return (k.length === 1 && /Drumherum/.test(k[0].titel))
        || 'Karten mit Fuehrung: ' + k.length;
  });
  t('sie schaltet in das Formular und dunkelt ab', () => {
    tourZeigen();
    fuehrungStarten();
    const an = document.getElementById('fuehrung').classList.contains('on');
    const wo = state.view;
    fuAus();
    return (an && wo === 'new') || `an: ${an}, Ansicht: ${wo}`;
  });
  t('der Schleier deckt vier Seiten ab, das Loch bleibt frei', () => {
    tourZeigen(); fuehrungStarten();
    const teile = ['fu-oben','fu-unten','fu-links','fu-rechts','fu-loch']
      .filter(id => !document.getElementById(id));
    fuAus();
    return teile.length === 0 || 'fehlt: ' + teile.join(', ');
  });
  /* ⚠️ Der Zweck des Schleiers ist das Abfangen von Tippern, nicht das Grau.
     Ein `box-shadow`-Loch haette gleich ausgesehen und nichts abgefangen. */
  t('der Schleier faengt Tipper wirklich ab', () => {
    tourZeigen(); fuehrungStarten();
    const s2 = window.getComputedStyle(document.getElementById('fu-oben'));
    const l = window.getComputedStyle(document.getElementById('fu-loch'));
    fuAus();
    return (s2.pointerEvents !== 'none' && l.pointerEvents === 'none')
        || `Schleier: ${s2.pointerEvents}, Loch: ${l.pointerEvents}`;
  });

  t('AUSGANG 1: durchklicken beendet sie', () => {
    tourZeigen(); fuehrungStarten();
    for (let i = 0; i < FUEHRUNG.length + 2; i++){
      const b = document.getElementById('fu-weiter');
      if (b) b.click();
    }
    const zu = !document.getElementById('fuehrung').classList.contains('on');
    fuAus();
    return zu || 'sie bleibt stehen -- die App waere gesperrt';
  });
  t('AUSGANG 2: "Fuehrung beenden" beendet sie sofort', () => {
    tourZeigen(); fuehrungStarten();
    document.getElementById('fu-ende').click();
    const zu = !document.getElementById('fuehrung').classList.contains('on');
    fuAus();
    return zu || 'sie bleibt stehen';
  });
  t('AUSGANG 3: ein Schritt ohne Ziel wird uebersprungen, nicht gewartet', () => {
    /* Zeigt ein Schritt auf ein Element, das es nicht gibt, darf er die ganze
       Fuehrung nicht anhalten. Geprueft, indem ein Ziel absichtlich verbogen wird. */
    const merk = FUEHRUNG[0].ziel;
    FUEHRUNG[0].ziel = '#gibtesnicht';
    tourZeigen(); fuehrungStarten();
    const steht = document.getElementById('fuehrung').classList.contains('on');
    const text = (document.getElementById('fu-sprech').textContent || '');
    FUEHRUNG[0].ziel = merk;
    fuAus();
    return (steht && text.indexOf(FUEHRUNG[1].titel) !== -1)
        || 'haengt beim fehlenden Ziel: ' + text.slice(0, 60);
  });
  t('AUSGANG 4: Speichern beendet sie ebenfalls', () => {
    tourZeigen(); fuehrungStarten();
    const an = document.getElementById('fuehrung').classList.contains('on');
    fuehrungBeenden();                       // das tut der Speichern-Knopf auch
    const zu = !document.getElementById('fuehrung').classList.contains('on');
    fuAus();
    return (an && zu) || `vorher an: ${an}, danach zu: ${zu}`;
  });
  /* ⚠️ Hinter der Fuehrung stehen noch drei Karten. Ohne dieses Weiterlaufen
     fielen sie unter den Tisch, weil die Fuehrung mittendrin abzweigt. */
  t('danach laeuft die Einfuehrung weiter statt zu enden', () => {
    tourZeigen();
    const nr = TOUR.findIndex(k => k.fuehrung);
    tourNr = nr; tourRendern();
    fuehrungStarten();
    fuehrungBeenden();
    const weiter = tourNr === nr + 1;
    fuAus();
    return weiter || `Tour steht auf ${tourNr}, erwartet ${nr + 1}`;
  });

  /* ====== Die Kacheln unten (12.08.2026, erweitert am 13.08.2026) ======
     Am 12.08. Karls Ansage: Liste, Karte und Statistiken zusammenwerfen, dann Neuer
     Fang, dann Einstellungen. Am 13.08. kam Home dazu, und zwar **vorn**:
     „als erstes soll jetzt ein home button kommen." */
  t('unten stehen genau vier Kacheln', () => {
    const n = document.querySelectorAll('.tabs .tab').length;
    return n === 4 || 'es sind ' + n;
  });
  t('und zwar in Karls Reihenfolge', () => {
    /* ⚠️ Geprueft wird die Kennung, nicht die Beschriftung. Die erste Fassung las
       `textContent` -- darin steckt die rote Zahl der Einstellungs-Kachel mit
       drin, und uebersetzt ist die Beschriftung auch noch. Die Pruefung fiel
       damit mit "Faenge | Neuer Fang | 0", obwohl die Reihenfolge stimmte. */
    const b = Array.from(document.querySelectorAll('.tabs .tab'))
      .map(t2 => t2.dataset.go || t2.id);
    return (b.join(',') === 'home,log,new,set') || 'Reihenfolge: ' + b.join(' | ');
  });
  /* Die erste Kachel ist die, auf der man landet. Steht das auseinander, leuchtet
     unten Home und man steht in der Fangliste -- der verwirrendste aller Zustaende. */
  t('die App oeffnet auf der ersten Kachel', () => {
    const erste = document.querySelector('.tabs .tab').dataset.go;
    const js = document.documentElement.innerHTML;
    return js.indexOf("go('" + erste + "');") !== -1
        || 'init() startet nicht auf ' + erste;
  });
  /* ⚠️ Die wichtigste hier: keine der drei Ansichten darf beim Zusammenlegen
     verlorengehen. Erreichbar bleiben muessen sie alle -- ueber den Umschalter. */
  t('alle drei Ansichten sind ueber den Umschalter erreichbar', () => {
    const fehlt = ['log', 'map', 'stats'].filter(v =>
      !document.querySelector('.segbtn[data-seg="' + v + '"]'));
    return fehlt.length === 0 || 'kein Schalter fuer: ' + fehlt.join(', ');
  });
  t('der Umschalter fuehrt wirklich zur Ansicht', () => {
    for (const v of ['map', 'stats', 'log']){
      document.querySelector('.segbtn[data-seg="' + v + '"]').click();
      if (document.getElementById('v-' + v).classList.contains('hidden'))
        return v + ' bleibt versteckt';
      if (state.view !== v) return 'state.view steht auf ' + state.view;
    }
    return true;
  });
  /* ⚠️ Sonst leuchtet unten nichts, sobald man auf Karte oder Auswertung geht --
     und die Leiste behauptet, man sei nirgends. */
  t('die Kachel "Faenge" bleibt an, auch in Karte und Auswertung', () => {
    for (const v of ['map', 'stats', 'detail']){
      go(v);
      const t2 = document.querySelector('.tabs .tab[data-go="log"]');
      if (!t2.classList.contains('on')) return 'bei ' + v + ' leuchtet sie nicht';
    }
    go('log');
    return true;
  });
  t('beim Erfassen sind Kopf und Umschalter weg', () => {
    go('new');
    const k = document.getElementById('kopf').hidden, s = document.getElementById('seg').hidden;
    go('log');
    return (k && s) || `Kopf versteckt: ${k}, Umschalter versteckt: ${s}`;
  });
  t('und in den drei Sammel-Ansichten sind sie da', () => {
    for (const v of ['log', 'map', 'stats']){
      go(v);
      if (document.getElementById('seg').hidden) return 'bei ' + v + ' fehlt der Umschalter';
    }
    go('log');
    return true;
  });
  /* ⚠️ Die zwei Zaehler sind beim Zusammenlegen aus ihren alten Koepfen in den
     gemeinsamen gewandert. Waeren sie dabei verlorengegangen, schriebe der
     laufende Betrieb ins Leere -- ohne Fehler, nur ohne Wirkung. */
  t('die Zaehler fuer Karte und Auswertung gibt es noch', () => {
    const da = !!document.getElementById('map-count') && !!document.getElementById('stats-pill');
    return da || 'ein Zaehler fehlt';
  });
  t('und es steht immer nur der zur Ansicht passende da', () => {
    go('map');
    const a = !document.getElementById('map-count').hidden
           && document.getElementById('stats-pill').hidden;
    go('stats');
    const b = document.getElementById('map-count').hidden
           && !document.getElementById('stats-pill').hidden;
    go('log');
    return (a && b) || `Karte richtig: ${a}, Auswertung richtig: ${b}`;
  });
  /* ⚠️ Hier stand bis zum 12.08.2026, die Einstellungs-Kachel duerfe die Ansicht
     NICHT austauschen -- sie war ein Vorhang ueber allem. Karls Ansage danach:
     "das ist jetzt eine normale seite wie neuer fang auch". Damit ist die
     Erwartung umgedreht, und die Pruefung muss mit, sonst haelt sie den
     gewollten Zustand fuer einen Fehler. */
  t('die Einstellungen sind eine Ansicht wie jede andere', () => {
    go('map');
    document.getElementById('tab-set').click();
    const da = !document.getElementById('v-set').classList.contains('hidden');
    const weg = document.getElementById('v-map').classList.contains('hidden');
    const stand = state.view === 'set';
    go('log');
    return (da && weg && stand)
        || `sichtbar: ${da}, Karte weg: ${weg}, state.view: ${state.view}`;
  });
  t('und dort verschwinden Kopf und Umschalter', () => {
    go('set');
    const k = document.getElementById('kopf').hidden, s = document.getElementById('seg').hidden;
    go('log');
    return (k && s) || `Kopf versteckt: ${k}, Umschalter versteckt: ${s}`;
  });
  /* ⚠️ Vom Vorhang darf nichts uebrigbleiben: ein zweiter Scrollbereich, ein
     dunkler Hintergrund oder ein Griff waeren auf einer normalen Seite nicht
     nur nutzlos, sondern im Weg. */
  t('vom Vorhang ist nichts uebriggeblieben', () => {
    const reste = ['#sheet', '#sheet-griff', '#btn-close-sheet', '#btn-sheet-zu']
      .filter(s => document.querySelector(s));
    return reste.length === 0 || 'noch da: ' + reste.join(', ');
  });

  /* ====== Die Einrichtung im Tutorial (12.08.2026) ======
     Karls Ansage: "ein tutorial wo man sich einrichtet ... es wird abgefragt
     wofuer man die app braucht".

     ⚠️ Der Kern dieser Pruefungen ist nicht, dass die Fragen erscheinen, sondern
     dass die Antworten **etwas aendern**. Eine Einrichtung, die nur fragt und
     danach dieselbe App hinstellt, ist eine Umfrage -- und die merkt der
     Benutzer beim ersten Fang, nicht der Prueflauf. */
  const profilSetzen = p => {
    if (p === null) localStorage.removeItem('angellog-profil');
    else localStorage.setItem('angellog-profil', JSON.stringify(p));
  };

  t('ohne Profil bleibt die Artenliste genau die alte', () => {
    profilSetzen(null);
    return (artenListe().join('|') === ARTEN.join('|'))
        || 'Liste veraendert, obwohl kein Profil gesetzt ist';
  });
  t('ohne Profil bleibt auch die Koederliste die alte', () => {
    profilSetzen(null);
    return (koederListe().join('|') === KOEDER.join('|'))
        || 'Koederliste veraendert ohne Profil';
  });

  t('"Meer" bringt Meeresfische und laesst Karpfen weg', () => {
    profilSetzen({ wo: 'meer' });
    const l = artenListe();
    return (l.indexOf('Dorsch') !== -1 && l.indexOf('Hering') !== -1
         && l.indexOf('Karpfen') === -1)
        || 'Liste: ' + l.slice(0, 6).join(', ');
  });
  t('"Beides" hat Dorsch und Karpfen', () => {
    profilSetzen({ wo: 'beides' });
    const l = artenListe();
    return (l.indexOf('Dorsch') !== -1 && l.indexOf('Karpfen') !== -1)
        || 'Liste: ' + l.slice(0, 6).join(', ');
  });
  t('Zielfische stehen ganz oben', () => {
    profilSetzen({ wo: 'see', ziele: ['Karpfen', 'Schleie'] });
    const l = artenListe();
    return (l[0] === 'Karpfen' && l[1] === 'Schleie')
        || 'oben steht: ' + l.slice(0, 3).join(', ');
  });
  /* ⚠️ Eine Wahl darf nichts wegnehmen, nur umsortieren. Wer "Spinnfischen"
     angibt und dann doch einmal mit Wurm ansitzt, braucht den Wurm trotzdem --
     sonst hat die Einrichtung ihm die App beschnitten statt sie einzustellen. */
  t('kein Koeder verschwindet, er rutscht nur nach hinten', () => {
    profilSetzen({ wo: 'see', wie: ['spinn'] });
    const l = koederListe();
    return (l[0] === 'Gummifisch' && l.indexOf('Tauwurm') !== -1
         && l.indexOf('Fliege') !== -1)
        || 'Liste: ' + l.join(', ');
  });
  t('am Meer stehen Pilker und Wattwurm vorn', () => {
    profilSetzen({ wo: 'meer', wie: ['spinn'] });
    const l = koederListe();
    return (l.indexOf('Pilker') < l.indexOf('Gummifisch') && l.indexOf('Wattwurm') !== -1)
        || 'Liste: ' + l.slice(0, 6).join(', ');
  });
  t('doppelte Eintraege gibt es nicht', () => {
    profilSetzen({ wo: 'beides', wie: ['spinn', 'ansitz', 'fliege'], ziele: ['Dorsch'] });
    for (const l of [artenListe(), koederListe()]){
      if (new Set(l).size !== l.length) return 'Doppelte in: ' + l.join(', ');
    }
    return true;
  });

  t('eine Frage im Tutorial schreibt ins Profil', () => {
    profilSetzen(null);
    tourWaehlen('wo', 'meer', false);
    return profilLesen().wo === 'meer' || 'Profil: ' + JSON.stringify(profilLesen());
  });
  t('bei Mehrfachauswahl schaltet dasselbe Feld wieder ab', () => {
    profilSetzen(null);
    tourWaehlen('wie', 'spinn', true);
    tourWaehlen('wie', 'ansitz', true);
    const zwei = (profilLesen().wie || []).length;
    tourWaehlen('wie', 'spinn', true);
    const eins = profilLesen().wie || [];
    return (zwei === 2 && eins.length === 1 && eins[0] === 'ansitz')
        || `nach zwei ${zwei}, danach ${JSON.stringify(eins)}`;
  });
  /* ⚠️ Die Zielfisch-Karte baut ihre Auswahl aus der Antwort davor. Wer "Meer"
     gewaehlt hat und dann Karpfen vorgeschlagen bekaeme, saehe sofort, dass die
     Frage davor folgenlos war. */
  t('die Zielfisch-Frage folgt der Gewaesser-Antwort', () => {
    profilSetzen({ wo: 'meer' });
    return (artenListe().slice(0, 12).indexOf('Dorsch') !== -1
         && artenListe().slice(0, 12).indexOf('Karpfen') === -1)
        || 'Auswahl: ' + artenListe().slice(0, 12).join(', ');
  });
  t('und die Vorschlagsliste im Formular zieht wirklich nach', () => {
    /* Der eigentliche Beweis: nicht die Hilfsfunktion, sondern das <datalist>,
       das beim Eintragen eines Fangs aufgeht.
       ⚠️ Es steht erst da, wenn jemand tippt (bindSuggest fuellt bei leerem Feld
       bewusst nichts) -- deshalb wird hier getippt statt nur gebaut. Die erste
       Fassung dieser Pruefung hat auf das leere <datalist> geschaut und ist
       gefallen, obwohl am Code nichts falsch war. */
    profilSetzen({ wo: 'meer' });
    buildStatics();
    const feld = document.getElementById('f-art');
    const tippen = s => {
      feld.value = s;
      feld.dispatchEvent(new Event('input'));
      return Array.from(document.querySelectorAll('#dl-art option')).map(o => o.value);
    };
    const meer = tippen('do');
    const suess = tippen('karpf');
    feld.value = '';
    feld.dispatchEvent(new Event('input'));
    return (meer.indexOf('Dorsch') !== -1 && suess.length === 0)
        || `bei "do": ${meer.join(', ')} — bei "karpf": ${suess.join(', ')}`;
  });

  profilSetzen(null);   // ⚠️ aufraeumen, sonst laufen die folgenden Pruefungen
  buildStatics();       //    mit einem Meer-Profil weiter

  /* ====== Das Postfach und die rote Zahl (12.08.2026) ======
     Karls Ansage: eine beantwortete Meldung soll in den Einstellungen auftauchen,
     rote Zahl am Zahnrad und am Postfach, darin alle Tickets der letzten 30 Tage. */
  const postSetzen = l => { localStorage.setItem('angellog-postfach', JSON.stringify(l)); };
  const T_OFFEN = { id: 'm1', nummer: 1, text: 'Karte laedt nicht',
                    erstellt: '2026-08-11T10:00:00.000Z' };
  const T_NEU   = { id: 'm2', nummer: 2, text: 'Fotos verdreht',
                    erstellt: '2026-08-11T11:00:00.000Z',
                    antwort: 'Ist behoben, bitte neu laden.',
                    antwort_am: '2026-08-12T09:00:00.000Z' };
  const T_ALT   = { ...T_NEU, id: 'm3', nummer: 3, gelesen_am: '2026-08-12T09:30:00.000Z' };

  t('die rote Zahl zaehlt nur beantwortete und ungelesene', () => {
    postSetzen([T_OFFEN, T_NEU, T_ALT]);
    return postfachUngelesen() === 1 || 'gezaehlt: ' + postfachUngelesen();
  });
  t('ohne Antwort bleibt die rote Zahl weg', () => {
    postSetzen([T_OFFEN]);
    badgesZeichnen();
    return (document.getElementById('badge-set').hidden === true
         && document.getElementById('badge-post').hidden === true)
        || 'Zahl steht da, obwohl nichts beantwortet ist';
  });
  t('mit Antwort steht sie an beiden Stellen und zeigt dieselbe Zahl', () => {
    postSetzen([T_NEU, { ...T_NEU, id: 'm9', nummer: 9 }]);
    badgesZeichnen();
    const a = document.getElementById('badge-set'), b = document.getElementById('badge-post');
    return (!a.hidden && !b.hidden && a.textContent === '2' && b.textContent === '2')
        || `Zahnrad "${a.textContent}" (hidden ${a.hidden}), Postfach "${b.textContent}"`;
  });

  t('das Postfach zeigt Frage und Antwort', () => {
    postSetzen([T_NEU]);
    postfachRendern();
    const txt = document.getElementById('postfach').textContent;
    return (txt.indexOf('Fotos verdreht') !== -1
         && txt.indexOf('Ist behoben') !== -1 && txt.indexOf('#2') !== -1)
        || 'Postfach zeigt: ' + txt;
  });
  t('eine unbeantwortete Meldung steht als offen da', () => {
    postSetzen([T_OFFEN]);
    postfachRendern();
    const txt = document.getElementById('postfach').textContent;
    return txt.indexOf('offen') !== -1 || 'Postfach zeigt: ' + txt;
  });
  t('ohne Tickets steht dort ein Satz und keine leere Flaeche', () => {
    postSetzen([]);
    postfachRendern();
    return document.getElementById('postfach').textContent.trim().length > 20
        || 'Postfach ist leer';
  });

  /* ⚠️ Der eigene Text geht durch esc(). In der Fang-Ansicht ist dasselbe nicht
     entschaerft (Befund vom 12.08.), dort ist es fast harmlos, weil niemand
     fremde Faenge sieht. Hier waere es das NICHT: in diesem Kasten steht Text,
     den ein anderer geschrieben hat -- Karls Antwort. Deshalb hier hart geprueft. */
  t('HTML in Meldung und Antwort wird entschaerft', () => {
    postSetzen([{ ...T_NEU, text: '<img src=x onerror=alert(1)>',
                  antwort: '<script>alert(2)<\/script>' }]);
    postfachRendern();
    const html = document.getElementById('postfach').innerHTML;
    return (html.indexOf('<img src=x') === -1 && html.indexOf('<script>alert(2)') === -1
         && html.indexOf('&lt;img') !== -1)
        || 'ungefiltertes HTML im Postfach';
  });

  /* ⚠️ Reihenfolge: erst zeichnen, dann abhaken. Andersherum waere die rote
     Markierung schon weg, bevor sie jemand gesehen hat -- die Zahl haette einen
     dann umsonst gerufen. */
  t('das Neue ist beim Aufschlagen noch als neu markiert', () => {
    postSetzen([T_NEU]);
    postfachRendern();
    return document.getElementById('postfach').textContent.indexOf('neu') !== -1
        || 'nichts als neu markiert';
  });
  t('und danach ist es abgehakt, die rote Zahl weg', () => {
    postSetzen([T_NEU]);
    postfachRendern();          // haakt im Anschluss ab
    return (postfachUngelesen() === 0
         && document.getElementById('badge-set').hidden === true)
        || 'noch ungelesen: ' + postfachUngelesen();
  });

  /* ====== Home: Wetter und Fangprognose (13.08.2026, Karls Ansage) ======
     „als erstes soll jetzt ein home button kommen wo die angelzeit steht und vorraussage
     fuer wetter (alles was in der statistik auch vorkommt) fangprognose auch."

     ⚠️ Der heikle Teil ist nicht das Zeichnen, sondern die **Rechnung**. Die Prognose
     darf nichts behaupten, was sie nicht aus Karls eigenen Faengen hat -- und sie darf
     sich nicht wie eine Beissquote lesen. Beides wird hier gemessen. */
  (function(){
    const pad2 = n => String(n).padStart(2, '0');
    const isoLokal = d => d.getFullYear() + '-' + pad2(d.getMonth()+1) + '-' + pad2(d.getDate())
                        + 'T' + pad2(d.getHours()) + ':00';
    /* Eine Vorhersage bauen, die von jetzt an 60 Stunden abdeckt. Alle Stunden tragen
       dieselben Werte ausser dem, was die einzelne Pruefung veraendert -- dann ist
       messbar, WORAN ein Unterschied liegt. */
    const vorhersageBauen = (aendern) => {
      const t0 = new Date(); t0.setMinutes(0, 0, 0);
      const time = [], temp = [], druck = [], code = [], wind = [], richt = [], wolken = [], regen = [];
      for (let k = -2; k < 58; k++){
        const d = new Date(t0.getTime() + k * 3600e3);
        time.push(isoLokal(d));
        temp.push(18); druck.push(1015); code.push(2); wind.push(9);
        richt.push(240); wolken.push(50); regen.push(0);
      }
      const tage = [];
      for (let k = 0; k < 4; k++){
        const d = new Date(t0.getTime() + (k - 1) * 864e5);
        tage.push(d.getFullYear() + '-' + pad2(d.getMonth()+1) + '-' + pad2(d.getDate()));
      }
      const v = {
        lat: 54.32, lon: 10.13, geholt: Date.now(),
        hourly: { time, temperature_2m: temp, pressure_msl: druck, weather_code: code,
                  wind_speed_10m: wind, wind_direction_10m: richt,
                  cloud_cover: wolken, precipitation: regen },
        daily: { time: tage,
                 sunrise: tage.map(s => s + 'T05:30'), sunset: tage.map(s => s + 'T21:15') }
      };
      if (aendern) aendern(v);
      return v;
    };
    /* Faenge, die alle unter derselben Bedingung entstanden sind: 1015 hPa, bewoelkt,
       18 Grad. Damit muss eine Stunde mit genau diesen Werten hoeher liegen als eine
       mit ganz anderen -- das ist die einzige Zusage, die die Prognose macht. */
    const faengeBauen = (n, aendern) => {
      const l = [];
      for (let k = 0; k < n; k++){
        const d = new Date(Date.now() - (k + 1) * 864e5);
        d.setHours(6, 0, 0, 0);
        const c = { id: 'p' + k, when: d.toISOString(), art: 'Hecht',
                    druck: 1015, luft: 18, wetter: 'bewoelkt', phase: 'morgen' };
        l.push(aendern ? aendern(c, k) : c);
      }
      return l;
    };

    t('das Modell benutzt nur Masse, die genug Faenge tragen', () => {
      const m = prognoseModell(faengeBauen(12));
      const keys = m.map(x => x.mass.key).sort();
      // Uhrzeit, Tageszeit, Wetter, Luftdruck, Lufttemperatur, Mondphase - alle gedeckt.
      return keys.length >= 5 || 'nur: ' + keys.join(',');
    });
    t('ein Mass mit zu wenigen Werten faellt raus', () => {
      // Nur zwei Faenge tragen einen Luftdruck, der Rest nicht.
      const l = faengeBauen(12, (c, k) => k < 2 ? c : { ...c, druck: null });
      const m = prognoseModell(l);
      return m.every(x => x.mass.key !== 'druck')
          || 'Luftdruck rechnet mit ' + m.find(x => x.mass.key === 'druck').werte.length + ' Werten';
    });
    /* Die Kernzusage: passende Bedingungen ergeben einen hoeheren Wert als unpassende.
       Ohne diese Pruefung koennte die Rechnung konstant 0,5 liefern und niemand saehe es. */
    t('passende Bedingungen liegen hoeher als unpassende', () => {
      const m = prognoseModell(faengeBauen(20));
      const gut = prognoseStunde(m, { stunde: 6, druck: 1015, luft: 18,
                                      wetter: 'bewoelkt', mond: null, phase: 'morgen' });
      const mau = prognoseStunde(m, { stunde: 14, druck: 985, luft: 30,
                                      wetter: 'gewitter', mond: null, phase: 'tag' });
      return (gut.wert > mau.wert) || `gut ${gut.wert} vs. mau ${mau.wert}`;
    });
    t('und die passende Stunde landet in der obersten Stufe', () => {
      const m = prognoseModell(faengeBauen(20));
      const gut = prognoseStunde(m, { stunde: 6, druck: 1015, luft: 18,
                                      wetter: 'bewoelkt', mond: null, phase: 'morgen' });
      return prognoseStufe(gut.wert).icon === '🟢' || 'Wert ' + gut.wert;
    });
    /* Gegenprobe zur Normierung: der Wert darf nie ueber 1 liegen, sonst waere die
       Stufengrenze 0,6 sinnlos geworden. */
    t('kein Wert liegt ueber 1', () => {
      const m = prognoseModell(faengeBauen(20));
      const p = prognoseStunde(m, { stunde: 6, druck: 1015, luft: 18,
                                    wetter: 'bewoelkt', mond: null, phase: 'morgen' });
      return p.wert <= 1.0000001 || 'Wert ' + p.wert;
    });
    t('die Uhrzeit zaehlt mit einem Fenster von einer Stunde', () => {
      const m = prognoseModell(faengeBauen(20)).find(x => x.mass.key === 'stunde');
      const nah = m.mass.nah;
      return (nah(6, 7) && nah(6, 5) && !nah(6, 9) && nah(23, 0))
          || 'Fenster stimmt nicht (auch ueber Mitternacht pruefen)';
    });
    t('das beste Fenster ist drei zusammenhaengende Stunden', () => {
      const v = vorhersageBauen();
      const m = prognoseModell(faengeBauen(20));
      const heute = v.hourly.time[2].slice(0, 10);
      const b = bestesFenster(m, v, heute);
      if (!b || !b.von) return 'kein Fenster gefunden';
      const spanne = new Date(b.bis).getTime() - new Date(b.von).getTime();
      return spanne === 2 * 3600e3 || 'Spanne: ' + (spanne / 3600e3) + ' h';
    });

    /* ---- Die Ansicht ---- */
    const homeBauen = async (faenge, vAendern) => {
      const alt = state.catches;
      localStorage.setItem('angellog-heimat',
        JSON.stringify({ lat: 54.32, lon: 10.13, name: 'Teststrecke' }));
      /* ⚠️ Frisch gestempelt abgelegt: dann liefert vorhersageHolen() aus dem Speicher
         und der Prueflauf haengt nicht am Netz. Eine Pruefung, die eine fremde API
         braucht, faellt irgendwann aus Gruenden, die nichts mit dem Code zu tun haben. */
      localStorage.setItem('angellog-vorhersage', JSON.stringify(vorhersageBauen(vAendern)));
      state.catches = faenge;
      state.view = 'home';
      try { await renderHome(); return {
        wetter: document.getElementById('home-wetter').textContent,
        prognose: document.getElementById('home-prognose').textContent
      }; }
      finally {
        state.catches = alt;
        localStorage.removeItem('angellog-heimat');
        localStorage.removeItem('angellog-vorhersage');
      }
    };

    ta('die Wetterkarte zeigt die Werte, die auch in der Auswertung vorkommen', async () => {
      const r = await homeBauen(faengeBauen(20));
      const fehlt = ['1015 hPa', '18 °C', '50 %', 'km/h', 'Teststrecke']
        .filter(s => r.wetter.indexOf(s) === -1);
      return fehlt.length === 0 || 'fehlt: ' + fehlt.join(', ') + '  |  ' + r.wetter.slice(0, 200);
    });
    ta('sie nennt Sonnenauf- und -untergang und die Mondphase', async () => {
      const r = await homeBauen(faengeBauen(20));
      return (r.wetter.indexOf('05:30') !== -1 && r.wetter.indexOf('21:15') !== -1
              && /Mond|Neumond|Vollmond|Viertel|Sichel/.test(r.wetter))
          || r.wetter.slice(0, 200);
    });
    /* ⚠️ Ohne Windrichtung darf dort keine stehen. `dirLabel(null)` liefert "N", weil
       `null % 360` gleich 0 ist -- eine erfundene Himmelsrichtung, die von einer echten
       nicht zu unterscheiden waere. */
    ta('ohne Windrichtung steht keine erfundene Richtung da', async () => {
      const r = await homeBauen(faengeBauen(20),
        v => { v.hourly.wind_direction_10m = v.hourly.time.map(() => null); });
      return /\d+ km\/h(?!\s*[NSOW])/.test(r.wetter) || 'Wind: ' + r.wetter.slice(0, 200);
    });
    ta('die Prognose steht mit Heute und Morgen da', async () => {
      const r = await homeBauen(faengeBauen(20));
      return (r.prognose.indexOf('Heute') !== -1 && r.prognose.indexOf('Morgen') !== -1)
          || r.prognose.slice(0, 200);
    });
    /* Der Satz, der die ganze Ansicht ehrlich haelt. Faellt er weg, liest sich die
       Stufe wie eine Beissquote -- und die App hat den Nenner dafuer gar nicht. */
    ta('und sie sagt dazu, dass sie keine Beissvorhersage ist', async () => {
      const r = await homeBauen(faengeBauen(20));
      return (/keine Beißvorhersage/.test(r.prognose)
              && /Ansitze ohne Fang/.test(r.prognose))
          || r.prognose.slice(0, 300);
    });
    ta('unter zehn Faengen wird gar keine Stufe gezeigt', async () => {
      const r = await homeBauen(faengeBauen(4));
      const stufen = ['🟢', '🟡', '⚪'].filter(s => r.prognose.indexOf(s) !== -1);
      // Und sie sagt, wie weit es noch ist -- „zu wenig" ohne Zahl ist eine Sackgasse.
      return (stufen.length === 0 && /zu wenige Fänge/.test(r.prognose)
              && /4 von 10/.test(r.prognose))
          || 'zeigt: ' + r.prognose.slice(0, 300);
    });
    ta('ohne Ort steht dort ein Weg statt einer leeren Karte', async () => {
      const alt = state.catches;
      state.catches = [];
      state.view = 'home';
      localStorage.removeItem('angellog-heimat');
      localStorage.removeItem('angellog-vorhersage');
      try {
        await renderHome();
        const txt = document.getElementById('home-wetter').textContent;
        return (txt.indexOf('Ort') !== -1 && !!document.getElementById('home-gps'))
            || 'zeigt: ' + txt.slice(0, 200);
      } finally { state.catches = alt; }
    });
  })();

  /* ====== Die Fangliste zeigt weniger (13.08.2026, Karls Ansage) ======
     „Bei der Suche will ich weniger Infos direkt sehen erst wenn ich draufclicke will ich
     mehr sehen. bitte zeig nur Bild Fischname laenge gewicht datum ort."

     ⚠️ Geprueft wird der **sichtbare Text der Kachel**, nicht die Vorlage im Quelltext.
     Eine Quelltext-Pruefung faende „Luftdruck" im Kommentar daneben und bliebe gruen --
     dieselbe Falle wie am 11. und 12.08. */
  (function(){
    const VOLL = {
      id: 'pruef-liste', when: '2026-08-12T10:30:00.000Z', art: 'Hecht',
      laenge: 78, gewicht: 4.2, gewaesser: 'Elbe',
      koeder: 'Gummifisch', koederFarbe: 'Firetiger', phase: 'morgens',
      wetter: 'bewoelkt', druck: 1013, windRichtung: 'NW', notiz: 'Sonnenaufgang'
    };
    const kachel = () => {
      const alt = state.catches;
      state.catches = [VOLL];
      try { renderList(); return document.querySelector('#list .item'); }
      finally { state.catches = alt; renderList(); }
    };

    t('die Kachel zeigt Fischart, Masse, Datum und Gewaesser', () => {
      const txt = kachel().textContent;
      return ['Hecht', '78 cm', '4,2 kg', '12.08.2026', 'Elbe'].every(s => txt.indexOf(s) !== -1)
          || 'Kachel zeigt: ' + txt;
    });
    /* Der eigentliche Punkt der Ansage: was NICHT mehr dasteht. */
    t('und nicht mehr Koeder, Wetter, Luftdruck, Wind oder Tageszeit', () => {
      const txt = kachel().textContent;
      const drin = ['Gummifisch', 'Firetiger', 'hPa', 'NW', 'morgens', 'Sonnenaufgang']
        .filter(s => txt.indexOf(s) !== -1);
      return drin.length === 0 || 'steht noch drin: ' + drin.join(', ');
    });
    /* Gegenprobe: „weniger anzeigen" darf nicht heissen „weniger finden". Gesucht wird
       weiter ueber alle Felder -- sonst waere ein Koeder ab jetzt unauffindbar, obwohl
       die Suchleiste ihn ausdruecklich anbietet. */
    t('gesucht wird trotzdem noch nach dem Koeder', () => {
      const alt = state.catches, q = document.getElementById('q');
      state.catches = [VOLL];
      q.value = 'gummifisch';
      try { renderList(); return document.querySelectorAll('#list .item').length === 1
                              || 'Koeder-Suche findet nichts mehr'; }
      finally { q.value = ''; state.catches = alt; renderList(); }
    });
    t('und die Uhrzeit steht nicht mehr in der Kachel, aber im Fang', () => {
      const txt = kachel().textContent;
      return txt.indexOf('10:30') === -1 || 'Uhrzeit steht noch in der Kachel';
    });
    /* Die zwei Schilder, die kein Fangdatum sind, sondern ein Zustand der App.
       „Entwurf" heisst: der Eintrag ist halb. Ohne das Schild sieht er fertig aus. */
    t('ein Entwurf ist in der Kachel weiter als Entwurf erkennbar', () => {
      const alt = state.catches;
      state.catches = [{ ...VOLL, entwurf: true }];
      try {
        renderList();
        const el = document.querySelector('#list .item');
        return (el.classList.contains('entwurf') && /Entwurf/.test(el.textContent))
            || 'Entwurf nicht erkennbar: ' + el.textContent;
      } finally { state.catches = alt; renderList(); }
    });
    /* ⚠️ Karls Meldung vom 13.08.2026: „hochkant fotos machen gerade probleme, das sieht
       sehr komisch aus." Die Kachel war quer (4:3), Handyfotos sind hochkant -- cover
       schnitt oben und unten je ein Viertel weg, und dort steht der Fisch.
       Gemessen wird die echte Geometrie, nicht der CSS-Text. */
    /* ⚠️ Sichtbar messen. Die Fangliste liegt in einem Abschnitt, der ausgeblendet ist,
       solange eine andere Ansicht offen steht -- und ein ausgeblendetes Element ist
       0×0 gross. Die erste Fassung dieser beiden Pruefungen mass genau das und meldete
       „Kachel ist 0×0". Gemessen wird nur, was auch zu sehen ist. */
    const kachelSichtbar = (rec) => {
      const alt = { c: state.catches, v: state.view };
      state.catches = [rec || VOLL];
      go('log');
      return { el: document.querySelector('#list .item'),
               zurueck: () => { state.catches = alt.c; go(alt.v); } };
    };
    t('die Kachel ist hochkant, nicht quer', () => {
      const { el, zurueck } = kachelSichtbar();
      try {
        const r = el.getBoundingClientRect();
        return (r.height > r.width * 1.15)
            || ('Kachel ist ' + Math.round(r.width) + '×' + Math.round(r.height));
      } finally { zurueck(); }
    });
    t('der Text liegt auf dem Foto, nicht darunter', () => {
      const { el, zurueck } = kachelSichtbar();
      try {
        const rf = el.querySelector('.th').getBoundingClientRect();
        const rt = el.querySelector('.txt').getBoundingClientRect();
        // Der Textkasten muss im Bildbereich liegen, nicht darunter beginnen.
        return (rt.top < rf.bottom && rt.bottom <= rf.bottom + 1)
            || ('Foto endet bei ' + Math.round(rf.bottom) + ', Text von '
                + Math.round(rt.top) + ' bis ' + Math.round(rt.bottom));
      } finally { zurueck(); }
    });
    /* Karls Ansage: „kannst du die oben sozusagen auf die gelbe linie machen wenn sie da
       sind." Die Leiste muss also oben sitzen -- und nur dann da sein, wenn es etwas zu
       sagen gibt. Eine Leiste an jeder Kachel waere keine Warnung mehr. */
    t('die gelbe Leiste sitzt oben in der Kachel', () => {
      const { el, zurueck } = kachelSichtbar({ ...VOLL, entwurf: true });
      try {
        const m = el.querySelector('.marks');
        if (!m) return 'keine Leiste';
        const re = el.getBoundingClientRect(), rm = m.getBoundingClientRect();
        return (Math.abs(rm.top - re.top) <= 2 && rm.width > re.width * 0.8)
            || ('Kachel oben ' + Math.round(re.top) + ', Leiste oben ' + Math.round(rm.top));
      } finally { zurueck(); }
    });
    t('ohne Grund gibt es keine Leiste', () => {
      const el = kachel();          // VOLL ist fertig und gilt im Rahmen als gesichert
      return !el.querySelector('.marks') || 'Leiste ohne Anlass';
    });
    /* ====== Sortierung (13.08.2026, Karls Ansage) ======
       „Filter für suchfunktion für datum von alt bis jung und anders herum und fische
       a-z und gewicht." */
    const sortSetzen = w => { localStorage.setItem('angellog-sortierung', w);
                              document.getElementById('sort').value = w; };
    const listeMit = (faenge, wie) => {
      const alt = state.catches, altS = localStorage.getItem('angellog-sortierung');
      state.catches = faenge;
      sortSetzen(wie);
      try { renderList();
            return [...document.querySelectorAll('#list .item')].map(z => z.dataset.id); }
      finally { state.catches = alt;
                if (altS) sortSetzen(altS); else localStorage.removeItem('angellog-sortierung');
                renderList(); }
    };
    const drei = [
      { ...VOLL, id: 'mittel', when: '2026-06-15T10:00:00.000Z', ts: Date.parse('2026-06-15T10:00:00Z'), art: 'Zander', gewicht: 3, laenge: 60 },
      { ...VOLL, id: 'alt',    when: '2026-01-02T10:00:00.000Z', ts: Date.parse('2026-01-02T10:00:00Z'), art: 'Äsche',  gewicht: 9, laenge: 40 },
      { ...VOLL, id: 'neu',    when: '2026-08-01T10:00:00.000Z', ts: Date.parse('2026-08-01T10:00:00Z'), art: 'Barsch', gewicht: 1, laenge: 80 }
    ];
    t('Neueste zuerst', () =>
      listeMit(drei, 'neu').join(',') === 'neu,mittel,alt' || listeMit(drei, 'neu').join(','));
    t('Aelteste zuerst', () =>
      listeMit(drei, 'alt').join(',') === 'alt,mittel,neu' || listeMit(drei, 'alt').join(','));
    /* ⚠️ „Äsche" muss VOR „Barsch" stehen. Ohne localeCompare landet sie hinter „Zander",
       weil Umlaute in der Zeichentabelle hinter Z liegen — bei deutschen Fischnamen ist
       das kein Randfall, sondern der Normalfall. */
    t('Fischart A-Z sortiert Umlaute richtig ein', () =>
      listeMit(drei, 'art').join(',') === 'alt,neu,mittel' || listeMit(drei, 'art').join(','));
    t('Schwerste zuerst', () =>
      listeMit(drei, 'gewicht').join(',') === 'alt,mittel,neu' || listeMit(drei, 'gewicht').join(','));
    t('Laengste zuerst', () =>
      listeMit(drei, 'laenge').join(',') === 'neu,mittel,alt' || listeMit(drei, 'laenge').join(','));
    /* ⚠️ Fehlende Werte gehoeren ans Ende. Stuenden die Faenge ohne Gewicht oben, saehe
       die Liste kaputt aus -- genau die, die zur Frage nichts sagen, laegen im Blick. */
    t('Faenge ohne Gewicht stehen hinten, nicht vorn', () => {
      const l = [...drei, { ...VOLL, id: 'ohne', gewicht: null, ts: Date.parse('2026-07-01T10:00:00Z') }];
      const r = listeMit(l, 'gewicht');
      return r[r.length - 1] === 'ohne' || r.join(',');
    });
    /* Die Sortierung darf `state.catches` nicht umdrehen -- daran haengen andere Stellen,
       etwa der Ort der Wetterkarte (juengster Fang mit Koordinaten). */
    t('die Sortierung dreht den Bestand nicht mit um', () => {
      const alt = state.catches;
      state.catches = drei.slice();
      const vorher = state.catches.map(c => c.id).join(',');
      sortSetzen('alt'); renderList();
      const nachher = state.catches.map(c => c.id).join(',');
      state.catches = alt; localStorage.removeItem('angellog-sortierung'); renderList();
      return vorher === nachher || (vorher + ' wurde zu ' + nachher);
    });
    t('die gewaehlte Sortierung bleibt gespeichert', () => {
      localStorage.setItem('angellog-sortierung', 'gewicht');
      const a = sortierungLesen();
      localStorage.setItem('angellog-sortierung', 'quatsch');
      const b = sortierungLesen();          // unbekannt -> Rueckfall, nicht Absturz
      localStorage.removeItem('angellog-sortierung');
      return (a === 'gewicht' && b === 'neu') || (a + ' / ' + b);
    });

    /* ====== Was die gelbe Leiste bedeutet (13.08.2026, Karls Ansage) ======
       „eine info wenn man auf den fang klickt für entwurf oder nur auf diesem gerät,
       was man tun muss damit das weggeht." Ein Warnschild ohne Ausweg ist die
       schlechtere Haelfte einer Warnung. */
    const detailVon = rec => {
      const alt = { c: state.catches, id: state.detailId };
      state.catches = [rec]; state.detailId = rec.id;
      try { renderDetail(); return document.getElementById('d-body'); }
      finally { state.catches = alt.c; state.detailId = alt.id; }
    };
    t('ein Entwurf erklaert im Fang, wie er fertig wird', () => {
      const txt = detailVon({ ...VOLL, entwurf: true }).textContent;
      return (/Entwurf/.test(txt) && /Haken/.test(txt)) || txt.slice(0, 200);
    });
    t('ein fertiger, gesicherter Fang bekommt keine solche Karte', () => {
      const txt = detailVon({ ...VOLL, cloud: VOLL.updated || 1 }).textContent;
      return !/Woran es noch hängt/.test(txt) || 'Karte ohne Anlass';
    });

    /* ====== Das Logo auf dem Ladebildschirm (13.08.2026, Karls Ansage) ======
       „Ich brauche doch wieder das Logo auf dem Ladescreen ... aber mach das mehr oben."
       Am 08.08. war es auf seine Ansage hin verschwunden — zurueck, und zwar oben.
       ⚠️ `visibility:hidden` (so wird der Schirm weggenommen) behaelt die Lage im Layout,
       anders als `display:none`. Deshalb laesst sich hier auch nach dem Start messen. */
    t('der Ladebildschirm traegt wieder Zeichen und Namen', () => {
      const o = document.querySelector('#splash .oben');
      return (o && o.querySelector('img') && /Angel-Log/.test(o.textContent))
          || (o ? 'unvollstaendig: ' + o.textContent : 'kein #splash .oben');
    });
    t('und beides steht oben, nicht in der Mitte', () => {
      const s = document.getElementById('splash');
      const o = document.querySelector('#splash .oben');
      const rs = s.getBoundingClientRect(), ro = o.getBoundingClientRect();
      return (ro.top - rs.top < rs.height * 0.25)
          || ('Zeichen sitzt bei ' + Math.round(ro.top - rs.top) + ' von ' + Math.round(rs.height));
    });
    /* Gegenprobe zur Lesbarkeit: weisse Schrift auf hellem Wasser ist weg. Der Verlauf
       war seit dem 08.08. oben fast durchsichtig (0,12), weil dort nichts stand -- jetzt
       steht dort etwas, also muss er zurueck sein. */
    t('der Verlauf dunkelt den oberen Rand wieder ab', () => {
      const css = Array.from(document.styleSheets)
        .flatMap(sh => { try { return [...sh.cssRules].map(r => r.cssText); } catch { return []; } })
        .filter(t2 => t2.indexOf('#splash .schleier') !== -1).join(' ');
      const m = css.match(/rgba\(0,\s*0,\s*0,\s*([0-9.]+)\)\s*0%/);
      return (m && parseFloat(m[1]) >= 0.3) || ('oben steht ' + (m ? m[1] : 'nichts'));
    });
    t('fmtTag liefert den Tag ohne Uhrzeit', () =>
      fmtTag('2026-08-12T10:30:00.000Z').indexOf(':') === -1
        || 'fmtTag: ' + fmtTag('2026-08-12T10:30:00.000Z'));
  })();

  /* ====== Antworten kommen an, ohne die App neu zu starten (13.08.2026) ======
     Karls Meldung: Ticket in Discord beantwortet, am Handy kam nichts an. Die rote Zahl
     haengt an postfachHolen(), das haengt an syncJetzt() -- und das lief beim Zurueckholen
     der App aus dem App-Switcher nie. Genau der Weg, auf dem eine PWA am iPhone benutzt
     wird.

     ⚠️ Behaviorale Pruefung, keine Quelltext-Suche. Mein eigener Kommentar an der Stelle
     enthaelt das Wort "visibilitychange" mehrfach -- eine Quelltext-Pruefung fiele damit
     in genau die Falle vom 11.08.: sie findet ihren Suchbegriff im Kommentar daneben und
     bleibt gruen, auch wenn der Aufruf raus ist.

     ⚠️ **Asynchron, und das ist keine Kosmetik.** Der Zuhoerer wird in init() angemeldet,
     und init() ist beim Durchlauf der synchronen Pruefungen noch nicht so weit. Als
     einfaches t() geschrieben fiel diese Pruefung zunaechst mit "Aufrufe: 0" -- sie hat
     nicht den Code gemessen, sondern den Zeitpunkt. Deshalb wird gewartet, bis der
     Zuhoerer wirklich da ist. */
  (function(){
    const sichtbar = () => document.dispatchEvent(new Event('visibilitychange'));
    const spionieren = async fn => {
      const echt = syncJetzt;
      const zaehler = { n: 0 };
      syncJetzt = () => { zaehler.n++; return Promise.resolve(); };
      try { await fn(zaehler); } finally { syncJetzt = echt; }
      return zaehler;
    };

    ta('zurueck in die App loest einen Abgleich aus', async () => {
      const z = await spionieren(async z => {
        // Warten, bis init() den Zuhoerer angemeldet hat -- nicht laenger.
        for (let i = 0; i < 80 && z.n === 0; i++){
          sichtbar();
          await new Promise(r => setTimeout(r, 50));
        }
      });
      return z.n > 0 || 'kein Abgleich, auch nach dem Warten auf init()';
    });
    /* Gegenprobe zur Drossel -- ohne sie liefe am iPhone bei JEDEM Blick in die App ein
       voller Abgleich, ueber Mobilfunk, mitten im Angeln. Laeuft direkt nach der
       Pruefung darueber, die Sperre steht also frisch. */
    ta('der zweite Blick sofort danach loest keinen zweiten aus', async () => {
      const z = await spionieren(async () => { sichtbar(); sichtbar(); sichtbar(); });
      return z.n === 0 || 'Aufrufe trotz Drossel: ' + z.n;
    });
    /* Und die Gegenprobe zur Gegenprobe: eine Drossel von einer Stunde waere dasselbe
       wie gar kein Abgleich. Die Antwort soll beim naechsten Hinsehen da sein.
       ⚠️ Keine Pruefung fuer `document.hidden`: sie kaeme nur nach der Registrierung
       dran, und dann steht die Drossel -- sie wuerde also gruen bleiben, ohne die
       Bedingung je gemessen zu haben. Lieber keine als eine, die aus dem falschen
       Grund gruen ist (die Lektion vom 11. und 12.08.). */
    t('die Drossel ist eine Minute, keine Stunde', () =>
      (SICHT_SYNC_PAUSE >= 15000 && SICHT_SYNC_PAUSE <= 300000)
        || 'SICHT_SYNC_PAUSE = ' + SICHT_SYNC_PAUSE);
  })();

  /* ====== Das ⓘ am Baukasten (13.08.2026, Karls Ansage) ====== */
  t('das Info-Zeichen steht am Baukasten', () =>
    !!document.getElementById('st-info-btn') || 'kein #st-info-btn');
  t('die Erklaerung ist zugeklappt, bis man tippt', () =>
    document.getElementById('st-info').hidden === true || 'steht offen da');
  t('ein Tipp klappt sie auf, der naechste wieder zu', () => {
    const b = document.getElementById('st-info-btn'), p = document.getElementById('st-info');
    b.click();
    const auf = p.hidden === false && b.getAttribute('aria-expanded') === 'true';
    b.click();
    const zu = p.hidden === true && b.getAttribute('aria-expanded') === 'false';
    return (auf && zu) || ('auf: ' + auf + ', zu: ' + zu);
  });
  /* Der Satz, der als Erstes verschwindet, wenn jemand den Text kuerzt -- und der
     einzige, der die Auswertung ehrlich haelt: gezaehlt werden Faenge, nicht Ansitze.
     Ohne ihn liest man aus einem hohen Punkt "hier faengt man am besten". */
  t('die Erklaerung sagt, dass Ansitze ohne Fang fehlen', () => {
    const txt = document.getElementById('st-info').textContent;
    return (txt.indexOf('Ansitze ohne Fang') !== -1 && txt.indexOf('nicht') !== -1)
        || 'Hinweis fehlt: ' + txt.slice(0, 120);
  });
  t('und sie erklaert die vier Schritte des Baukastens', () => {
    const txt = document.getElementById('st-info').textContent;
    return ['Zählen', 'Über', 'Aufteilen', 'Gewässer'].every(w => txt.indexOf(w) !== -1)
        || 'ein Schritt fehlt';
  });

  /* ====== Die Fang-Ansicht: leere Felder (12.08.2026) ======
     ⚠️ Diese Ansicht hatte bis heute KEINE einzige Pruefung. Genau deshalb konnte in acht
     Zeilen woertlich "false" stehen, ohne dass irgendetwas gefallen waere -- gemeldet hat
     es Karl, nicht der Prueflauf. Ein leeres Feld ergab in `kv()` nicht `undefined`,
     sondern den Boolean `false` (aus `c.wasser != null && ...`), und der alte Filter
     kannte nur null/undefined/''.

     ⚠️ Geprueft wird der sichtbare Text, nicht der Quelltext der Vorlage. Eine
     Quelltext-Pruefung haette hier genau die Falle vom 11.08. wiederholt: sie findet
     ihren Suchbegriff im Kommentar daneben und bleibt gruen. */
  const detailBauen = rec => {
    const alt = { c: state.catches, id: state.detailId };
    state.catches = [rec];
    state.detailId = rec.id;
    try { renderDetail(); return document.getElementById('d-body').textContent; }
    finally { state.catches = alt.c; state.detailId = alt.id; }
  };
  const LEER = { id: 'pruef-leer', when: '2026-08-12T10:00:00.000Z', art: 'Hecht' };

  t('leere Felder schreiben kein "false" in die Fang-Ansicht', () => {
    const txt = detailBauen(LEER);
    return txt.indexOf('false') === -1 || 'Ansicht enthaelt "false": ' + txt;
  });
  t('... und auch kein "undefined"/"null"/"NaN"', () => {
    const txt = detailBauen(LEER);
    const treffer = ['undefined', 'null', 'NaN'].filter(s => txt.indexOf(s) !== -1);
    return treffer.length === 0 || 'Ansicht enthaelt: ' + treffer.join(', ');
  });
  t('leere Felder erscheinen gar nicht erst als Zeile', () => {
    const txt = detailBauen(LEER);
    const da = ['Wassertemperatur', 'Luftdruck', 'Wassertiefe']
      .filter(s => txt.indexOf(s) !== -1);
    return da.length === 0 || 'leere Zeilen trotzdem gezeichnet: ' + da.join(', ');
  });

  /* ⚠️ Die Gegenprobe ist hier wichtiger als die Pruefung selbst. Der naheliegende Flick
     waere `if (!v) return ''` gewesen -- der haette "false" auch weggeraeumt und dabei
     still die Null mitgenommen. 0 °C Wasser ist im Winter ein echter Messwert, 0 %
     Bewoelkung ein wolkenloser Tag. Ein Flick, der Messwerte verschluckt, ist schlimmer
     als der Fehler, den er behebt. */
  t('Gegenprobe: gesetzte Werte stehen weiterhin da', () => {
    const txt = detailBauen({ ...LEER, wasser: 18.5, druck: 1013, tiefe: 2.5, luft: 22,
                              bewoelkung: 40, regen24: 1.2, koederGroesse: 7,
                              koederGewicht: 14 });
    const fehlt = ['18,5 °C', '1013 hPa', '2,5 m', '22 °C', '40 %', '1,2 mm',
                   '7 cm', '14 g'].filter(s => txt.indexOf(s) === -1);
    return fehlt.length === 0 || 'nicht gefunden: ' + fehlt.join(' | ');
  });
  t('Gegenprobe: 0 °C Wasser ist ein Messwert, keine Leere', () => {
    const txt = detailBauen({ ...LEER, wasser: 0, bewoelkung: 0 });
    return (txt.indexOf('0 °C') !== -1 && txt.indexOf('0 %') !== -1)
        || 'die Null ist verschwunden: ' + txt;
  });
  t('Gegenprobe: der alte Filter liesse "false" wirklich durch', () => {
    /* Baut den Altstand nach. Faellt diese Pruefung, prueft die erste oben nichts mehr --
       dann waere der Fehler gar nicht mehr ausdrueckbar und die Wache haette sich selbst
       abgeschafft, ohne dass es auffiele. */
    const alt = v => v == null || v === '' ? '' : String(v);
    return alt(false) === 'false'
        || 'der nachgebaute Altstand liefert kein "false" mehr — die Wache ist blind';
  });

  /* ====== Die Seite darf am Handy nicht breiter sein als das Handy (12.08.2026) ======
     Karls Meldung: "die website ist zu breit auf dem handy".

     ⚠️ Breiten-Pruefungen gab es schon, aber nur fuer die **Statistik**. Die
     Listen-Seite hatte keine -- und genau dort ist es aufgefallen. Eine Pruefung,
     die nur die halbe App abdeckt, sagt ueber den Rest nichts, und das sieht von
     aussen aus wie gruen.

     ⚠️ Gemeldet wird der **Name des Uebeltaeters**, nicht nur "zu breit". Ohne ihn
     sucht man ihn von Hand durch den ganzen Baum, und beim naechsten Mal wieder. */
  const zuBreit = (w, d) => {
    const grenze = w.innerWidth + 1;
    const schuld = [];
    d.querySelectorAll('body *').forEach(el => {
      if (!el.getClientRects().length) return;            // unsichtbar zaehlt nicht
      const r = el.getBoundingClientRect();
      if (r.right > grenze || r.left < -1){
        // Nur den obersten Schuldigen nennen, nicht seine ganze Verwandtschaft.
        if (!schuld.some(s => s.contains(el))) schuld.push(el);
      }
    });
    return schuld.map(el => {
      const kl = (typeof el.className === 'string' && el.className.trim())
        ? '.' + el.className.trim().split(/\s+/).join('.') : '';
      return el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + kl
           + ' bis ' + Math.round(el.getBoundingClientRect().right) + 'px';
    });
  };

  /* ⚠️ Drei Breiten, nicht eine. 390 px ist ein heutiges iPhone, 360 ein
     verbreitetes Android, 320 das schmalste, was noch vorkommt (iPhone SE 1.
     Generation, und jedes Geraet mit vergroesserter Schrift). Bei 390 allein war
     alles gruen, waehrend Karl auf seinem Geraet ein zu breites Bild sah -- eine
     einzige Breite zu pruefen heisst, den Fall zu verpassen.

     ⚠️ **Ein Rahmen je Breite, nicht einer je Seite.** Die erste Fassung machte
     neun Rahmen mit je 2,6 s Wartezeit auf -- damit brach der ganze Lauf ohne
     Ergebnis ab (Quelltext-Auswurf), weil das Zeitbudget von Chrome ueberschritten
     war. Das ist dieselbe Decke wie am 09. und 11.08.: nicht der Code, das Budget.
     Jetzt wird in einem Rahmen durch alle Seiten geschaltet. */
  const breitPruefen = (breite) => new Promise((fertig, schief) => {
    const f = document.createElement('iframe');
    f.style.cssText = 'width:' + breite + 'px;height:720px;border:0;position:absolute;left:-9999px';
    f.src = 'index.html';
    f.onload = () => setTimeout(() => {
      try {
        const w = f.contentWindow, d = f.contentDocument, klagen = [];
        /* ⚠️ **Mit Inhalt messen, nicht leer.** Die erste Fassung lief auf einer
           leeren App und war auf allen drei Breiten gruen -- waehrend Karl auf
           seinem Handy ein zu breites Bild sah. Genau das war der Fall: die
           Pillen-Zeile bricht nicht um, und erst echter Inhalt macht sie lang.
           Eine Breiten-Pruefung ohne Inhalt prueft die Breite von nichts.

           ⚠️ Gefuellt werden die Pillen direkt, nicht ueber `state`: `const state`
           auf oberster Ebene ist keine Eigenschaft des Fensters. Gemeint ist
           ohnehin die Zusage der Zeile -- sie muss umbrechen, **egal wie lang
           eine Pille wird**.

           ⚠️ Und gefuellt wird **nach** `go()`, nicht davor. Die zweite Fassung
           setzte die Texte vorher -- `go('log')` zeichnet die Pillen aber neu und
           hat sie sofort wieder auf "0 Faenge" gesetzt. Die Pruefung mass damit
           erneut den leeren Zustand und blieb auch dann gruen, wenn man den
           Umbruch wieder herausnahm. Aufgefallen ist es nur an der Gegenprobe. */
        const fuellen = () => {
          const lang = {
            '#st-count': '128 F\u00e4nge',
            '#st-waters': '17 Gew\u00e4sser',
            '#st-drafts': '4 Entw\u00fcrfe',
            '#st-cloud': '12 Eintr\u00e4ge nur auf diesem Ger\u00e4t'
          };
          for (const wahl of Object.keys(lang)){
            const el = d.querySelector(wahl);
            if (el){ el.textContent = lang[wahl]; el.hidden = false; }
          }
        };
        for (const seite of ['home', 'log', 'map', 'stats', 'new', 'set']){
          w.go(seite);
          fuellen();
          const raus = zuBreit(w, d);
          if (d.documentElement.scrollWidth > w.innerWidth + 1)
            raus.push('Seite scrollt seitlich (' + d.documentElement.scrollWidth + ')');
          if (raus.length) klagen.push(seite + ': ' + raus.join(', '));
        }
        f.remove();
        fertig(klagen.length === 0 || klagen.join('  |  '));
      } catch (e){ f.remove(); schief(e); }
    }, 2600);
    f.onerror = () => { f.remove(); schief(new Error('index.html laedt nicht')); };
    document.body.appendChild(f);
  });

  for (const breite of [320, 360, 390]){
    ta('nichts ragt heraus auf ' + breite + ' px', async () => await breitPruefen(breite));
  }

  /* ====== Zwei Kacheln nebeneinander (13.08.2026, Karls Ansage) ======
     „mach die kacheln dann auch kleiner nur wenns geht sodass 2 nebeneinander moeglich
     waeren." Gemessen wird die **Geometrie im 320-px-Fenster**, nicht der CSS-Text:
     `grid-template-columns` im Quelltext zu suchen sagt nichts darueber, ob die Kacheln
     dort auch wirklich nebeneinander landen -- ein zu breiter Inhalt sprengt jedes
     Raster, und genau das ist am Handy der Normalfall.

     ⚠️ Die Kacheln werden im Rahmen selbst gebaut statt ueber echte Faenge: `state` ist
     auf oberster Ebene ein const und keine Eigenschaft des Fensters, an den Bestand des
     iframes kommt man von hier also nicht heran. Gemeint ist ohnehin die Zusage des
     Rasters, und die haengt nicht am Inhalt. */
  const zweiNebeneinander = (breite) => new Promise((fertig, schief) => {
    const f = document.createElement('iframe');
    f.style.cssText = 'width:' + breite + 'px;height:720px;border:0;position:absolute;left:-9999px';
    f.src = 'index.html';
    f.onload = () => setTimeout(() => {
      try {
        const w = f.contentWindow, d = f.contentDocument;
        w.go('log');
        const liste = d.getElementById('list');
        liste.innerHTML = '';
        // Absichtlich lange Texte: ein Fischname und ein Gewaesser, an denen ein
        // Raster ohne minmax(0,1fr) auseinanderfaellt.
        for (let i = 0; i < 4; i++){
          const el = d.createElement('div');
          el.className = 'item';
          el.innerHTML = '<div class="th">\u{1F41F}</div>'
            + '<div class="t1">Regenbogenforelle</div>'
            + '<div class="t2">87 cm · 6,4 kg</div>'
            + '<div class="t3">12.08.2026 · Nord-Ostsee-Kanal</div>';
          liste.appendChild(el);
        }
        const k = [...liste.querySelectorAll('.item')];
        const klagen = [];
        if (k.length !== 4) klagen.push('nur ' + k.length + ' Kacheln');
        // Erste und zweite muessen dieselbe Zeile teilen, dritte eine Zeile tiefer.
        if (k[0].offsetTop !== k[1].offsetTop) klagen.push('1 und 2 stehen untereinander');
        if (k[0].offsetLeft === k[1].offsetLeft) klagen.push('1 und 2 stehen uebereinander');
        if (k[2].offsetTop <= k[0].offsetTop) klagen.push('3 steht nicht in der zweiten Reihe');
        // Drei nebeneinander waeren auf 320 px Briefmarken -- gemeint sind zwei.
        if (k[2].offsetTop === k[1].offsetTop) klagen.push('drei in einer Reihe');
        // Und nichts davon darf seitlich herausragen.
        for (const el of k){
          const r = el.getBoundingClientRect();
          if (r.right > breite + 1) klagen.push('Kachel ragt bis ' + Math.round(r.right) + ' px');
        }
        f.remove();
        fertig(klagen.length === 0 || klagen.join(', '));
      } catch (e){ f.remove(); schief(e); }
    }, 2600);
    f.onerror = () => { f.remove(); schief(new Error('index.html laedt nicht')); };
    document.body.appendChild(f);
  });
  ta('zwei Fang-Kacheln stehen auf 320 px nebeneinander', async () => await zweiNebeneinander(320));

  (async function(){
    for (const [name, fn] of asyncTests){
      try { const r = await fn(); if (r === true) { ok++; out.push('OK   ' + name); }
            else { bad++; out.push('FAIL ' + name + '  -> ' + r); } }
      catch (e) { bad++; out.push('ERR  ' + name + '  -> ' + e.message); }
    }
    const pre = document.createElement('pre');
    pre.id = 'testout';
    pre.textContent = out.join('\n') + '\n=== ' + ok + ' ok, ' + bad + ' fehlgeschlagen ===';
    document.body.appendChild(pre);
  })();
})();
</script>
"""

# ⚠️ Die Zahl der Ladebildschirm-Fotos steht an drei Stellen: als ANZAHL im Skript,
# als Liste im Service Worker und als Dateien auf der Platte. Laufen sie auseinander,
# zeigt die App eine 404 statt eines Bildes -- und zwar nur bei jedem n-ten Start,
# was beim Ausprobieren fast sicher durchrutscht.
splash_dateien = sorted(SRC.glob('splash-*.jpg'))
html_roh = (SRC / 'index.html').read_text(encoding='utf-8')
sw_roh   = (SRC / 'sw.js').read_text(encoding='utf-8')
m = re.search(r'var ANZAHL = (\d+);', html_roh)
if not m:
    sys.exit('ANZAHL der Splash-Fotos nicht im Quelltext gefunden.')
if int(m.group(1)) != len(splash_dateien):
    sys.exit(f'Splash-Fotos: ANZAHL sagt {m.group(1)}, auf der Platte liegen '
             f'{len(splash_dateien)}.')
fehlend = [f'./{d.name}' for d in splash_dateien if f"'./{d.name}'" not in sw_roh]
if fehlend:
    sys.exit(f'Diese Splash-Fotos fehlen im Service Worker: {fehlend} — '
             'ohne sie steht am Wasser ohne Netz ein Schirm ohne Bild.')
print(f'Splash-Fotos: {len(splash_dateien)} Dateien, ANZAHL und Service Worker stimmen ueberein.')

# ⚠️ Die Fassung steht in jeder Fehlermeldung mit drin. Zeigt sie eine andere als die
# tatsaechlich ausgelieferte, ist eine Meldung schlimmer als keine: sie schickt die
# Fehlersuche auf die falsche Fassung. Bei einer PWA ist das der Normalfall und nicht
# die Ausnahme -- am iPhone laeuft eine wochenalte Seite weiter (siehe 08.08.2026).
mf = re.search(r"const FASSUNG = '([^']+)';", html_roh)
mc = re.search(r"const CACHE\s*=\s*'angellog-([^']+)';", sw_roh)
if not mf or not mc:
    sys.exit('FASSUNG in index.html oder CACHE in sw.js nicht gefunden.')
if mf.group(1) != mc.group(1):
    sys.exit(f'FASSUNG sagt {mf.group(1)}, der Service-Worker-Cache heisst '
             f'angellog-{mc.group(1)} — eine Fehlermeldung nennte dann die falsche Fassung.')
print(f'Fassung: index.html und Service Worker stehen beide auf {mf.group(1)}.')

# ⚠️ Jeder T()-Aufruf braucht einen Eintrag im Woerterbuch. Fehlt einer, faellt das
# NICHT als Fehler auf: T() gibt dann den deutschen Text zurueck, und die englische
# App zeigt an der Stelle stillschweigend Deutsch. Genau solche Luecken sind die,
# die niemand meldet -- sie sehen nach Absicht aus. Deshalb hier hart geprueft.
# Vorlagen mit ${...} und aus Variablen gebaute Aufrufe (T(k.titel), T(name)) kann
# man von aussen nicht aufloesen; geprueft werden die festen Zeichenketten.
en_block = re.search(r'const EN = \{(.*?)\n\};', html_roh, re.S)
if not en_block:
    sys.exit('Das Woerterbuch EN wurde nicht gefunden.')
en_keys = set()
for km in re.finditer(r"^  '((?:[^'\\]|\\.)*)':", en_block.group(1), re.M):
    en_keys.add(km.group(1).replace("\\'", "'").replace('\\\\', '\\'))
# ⚠️ Lange Saetze stehen als zusammengesetzter Schluessel da: ['a ' + 'b']: '...'.
# Ohne diesen zweiten Durchgang gelten sie als NICHT vorhanden -- und dann meldet die
# Pruefung eine fehlende Uebersetzung, die zwei Zeilen weiter oben steht. Am 13.08.2026
# genau so passiert, mit fuenf Saetzen auf einmal.
for km in re.finditer(r"^  \[([\s\S]*?)\]:", en_block.group(1), re.M):
    teile = re.findall(r"'((?:[^'\\]|\\.)*)'", km.group(1))
    if teile:
        en_keys.add(''.join(teile).replace("\\'", "'").replace('\\\\', '\\'))

benutzt = set()
# T('a'), T("a"), T('a' + 'b'), T(bed ? 'a' : 'b')
for tm in re.finditer(r"T\(\s*((?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"
                      r"(?:\s*\+\s*(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"))*)\s*\)", html_roh):
    teile = re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", tm.group(1))
    benutzt.add(''.join(a or b for a, b in teile).replace("\\'", "'"))
for tm in re.finditer(r"T\([^)']*\?\s*('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")\s*:\s*"
                      r"('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")\s*\)", html_roh):
    for g in tm.groups():
        benutzt.add(g[1:-1].replace("\\'", "'"))

fehlen = sorted(k for k in benutzt if k and k not in en_keys)
if fehlen:
    sys.exit('Diese T()-Schluessel haben keine englische Fassung — die App zeigt dort '
             'still Deutsch:\n  ' + '\n  '.join(repr(f) for f in fehlen))
print(f'Woerterbuch: {len(en_keys)} Eintraege, alle {len(benutzt)} festen T()-Schluessel gedeckt.')

html = (WORK / 'index.html').read_text(encoding='utf-8')
(WORK / 'test.html').write_text(html + TESTS, encoding='utf-8')

# Dieselbe App, aber init() wirft sofort. Damit laesst sich pruefen, dass der Ladebildschirm
# auch dann weggeht, wenn er nie regulaer weggenommen wird — sonst waere die App gesperrt.
# ⚠️ Bricht der Ersatz unten ins Leere (Zeile umbenannt), soll das auffallen, nicht durchrutschen.
ANKER = '(async function init(){'
if ANKER not in html:
    sys.exit(f'init()-Anker nicht gefunden — {ANKER!r} in index.html gesucht. '
             'Wurde die Zeile umbenannt? Dann hier nachziehen, sonst prueft der '
             'Notausstieg-Fall nichts mehr.')
(WORK / 'kaputt.html').write_text(
    html.replace(ANKER, ANKER + " throw new Error('absichtlich kaputt');", 1),
    encoding='utf-8')

# Dieselbe App, aber init() wird vor dem Wegnehmen des Schirms nie fertig — so wie bei einem
# ersten Abgleich, der am Netz haengt. Seit dem 11.08.2026 wartet der Schirm absichtlich auf
# diesen Abgleich (Karls Ansage); ohne SPLASH_HOECHSTENS wuerde die App sich damit bei
# schlechtem Netz hinter einem Foto selbst sperren. Genau das prueft haengt.html.
# ⚠️ Ein Fehler wie in kaputt.html taugt dafuer nicht: der fliegt, bevor ueberhaupt gewartet
# wird. Gebraucht wird ein Warten, das nie zurueckkommt.
HAENGT = '  splashWeg();\n})();'
if HAENGT not in html:
    sys.exit(f'Splash-Anker nicht gefunden — {HAENGT!r} am Ende von init() gesucht. '
             'Wurde die Reihenfolge geaendert? Dann hier nachziehen, sonst prueft der '
             'Fall "haengender Abgleich" nichts mehr.')
(WORK / 'haengt.html').write_text(
    html.replace(HAENGT, '  await new Promise(function(){});\n' + HAENGT, 1),
    encoding='utf-8')

# ⚠️ Zeitbudget: 20000 stammt aus der Zeit mit 424 Pruefungen. Am 10.08.2026 brach
# der Lauf bei 489 Pruefungen viermal in Folge ohne Ergebnis ab -- auch mit dem
# Stand von einer Stunde vorher, der noch gruen durchgelaufen war. Das war also
# nicht der Code, sondern die Decke: die letzten (asynchronen) Pruefungen kamen
# nicht mehr unter die Grenze. Virtuelle Zeit kostet keine echte Zeit, ein
# groesseres Budget also nichts ausser Luft nach oben.
r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--virtual-time-budget=45000', '--allow-file-access-from-files',
                    '--dump-dom', (WORK / 'test.html').as_uri()],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
m = re.search(r'<pre id="testout">(.*?)</pre>', r.stdout, re.S)
if not m:
    # ⚠️ Die Ausgabe enthaelt Umlaute und Sonderzeichen; die Windows-Konsole laeuft
    # per Vorgabe auf cp1252. Ohne dieses Ersetzen stirbt die FEHLERMELDUNG selbst
    # an einem UnicodeEncodeError und verdeckt genau das, was man sehen muesste.
    # Am 10.08.2026 passiert: der Abbruch war da, der Grund unsichtbar.
    def zeigen(s):
        enc = sys.stdout.encoding or 'utf-8'
        print(s.encode(enc, errors='replace').decode(enc, errors='replace'))
    zeigen('Kein Ergebnis. Chrome-Ausgabe (Ende):')
    zeigen(r.stdout[-3000:]); zeigen(r.stderr[-3000:]); sys.exit(1)
txt = m.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
print(txt)
sys.exit(0 if ', 0 fehlgeschlagen' in txt else 1)
