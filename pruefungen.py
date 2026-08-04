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
  t('Wetter allein zählt als Inhalt', () => {
    resetForm(null);
    ['#f-art','#f-laenge','#f-gewicht','#f-gewaesser','#f-luft','#f-druck','#f-windstaerke',
     '#f-wasser','#f-tiefe','#f-bewoelkung','#f-koeder','#f-koedergroesse','#f-notiz']
      .forEach(s => document.querySelector(s).value = '');
    const vorher = formHatInhalt();
    setWetter('gewitter');
    const nachher = formHatInhalt();
    return (vorher === false && nachher === true) || (vorher + '/' + nachher);
  });
  t('Bewölkung allein zählt als Inhalt', () => {
    resetForm(null);
    ['#f-art','#f-laenge','#f-gewicht','#f-gewaesser','#f-luft','#f-druck','#f-windstaerke',
     '#f-wasser','#f-tiefe','#f-bewoelkung','#f-koeder','#f-koedergroesse','#f-notiz']
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
     '#f-wasser','#f-tiefe','#f-bewoelkung','#f-koeder','#f-koedergroesse','#f-notiz']
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
    const mk = (o) => Object.assign({ id: Math.random().toString(36).slice(2), entwurf: false,
      when: '2026-07-15T06:30', ts: new Date('2026-07-15T06:30').getTime() }, o);
    const setzeFaenge = arr => { state.catches = arr; };
    const alleFilterAus = (zeige) => { state.stats = { gewaesser: '', art: '', zeit: 'alles',
                                                      zeige: zeige || 'wasser' }; };
  
    // ---- Stufenreihe für die Kurven ----
    const R = arr => arr.map(v => ({ w: v }));
    t('Stufenreihe deckt den Bereich ab', () => {
      const r = stufenReihe(R([8.2, 13.9]), c => c.w, 2);   // 13,9 faellt in die Stufe 12
      return r.map(e => e.x).join('|') === '8|10|12' || r.map(e => e.x).join('|');
    });
    t('leere Stufe steht mit 0 drin', () => {
      const r = stufenReihe(R([8.2, 13.9]), c => c.w, 2);
      return (r[0].wert === 1 && r[1].wert === 0 && r[2].wert === 1)
          || r.map(e => e.x + ':' + e.wert).join(' ');
    });
    t('Stufenreihe zählt richtig', () => {
      const r = stufenReihe(R([8.1, 8.9, 9.5, 12.0]), c => c.w, 2);
      return (r[0].wert === 3 && r[r.length-1].wert === 1) || r.map(e => e.x + ':' + e.wert).join(' ');
    });
    t('Stufenreihe ohne Werte ist leer', () => stufenReihe(R([]), c => c.w, 2).length === 0 || 'nicht leer');
    t('Stufenreihe ignoriert null', () => {
      const r = stufenReihe([{w:null},{w:10},{w:undefined}], c => c.w, 2);
      return (r.length === 1 && r[0].wert === 1) || JSON.stringify(r);
    });
    t('Stufenreihe bricht bei Ausreissern ab', () => stufenReihe(R([1, 5000]), c => c.w, 2).length === 0 || 'zu viele Stufen');
    t('Stufenreihe rechnet auch bei 0', () => {
      const r = stufenReihe(R([0, 0.5]), c => c.w, 1);
      return (r.length === 1 && r[0].wert === 2) || JSON.stringify(r);
    });
    t('Stufenreihe mit Komma-Beschriftung', () => stufenReihe(R([0.2]), c => c.w, 0.5)[0].x === '0' || stufenReihe(R([0.2]), c => c.w, 0.5)[0].x);
  
    // ---- Kurve ----
    t('Kurve zeichnet ein SVG', () => {
      const h = kurvenBlock('T', [{x:'8',wert:1},{x:'10',wert:3},{x:'12',wert:2}]);
      return (h.includes('<svg') && h.includes('<path')) || 'kein SVG';
    });
    t('Kurve beschriftet jeden Punkt', () => {
      const h = kurvenBlock('T', [{x:'8',wert:1},{x:'10',wert:3},{x:'12',wert:2}]);
      return (h.includes('>1</text>') && h.includes('>3</text>') && h.includes('>2</text>')) || 'Zahlen fehlen';
    });
    t('Kurve setzt keinen Punkt auf 0', () => {
      const h = kurvenBlock('T', [{x:'8',wert:2},{x:'10',wert:0},{x:'12',wert:2}]);
      return (h.match(/<circle/g) || []).length === 2 || (h.match(/<circle/g) || []).length;
    });
    t('Kurve glättet nicht (keine Bézier)', () => {
      const h = kurvenBlock('T', [{x:'8',wert:1},{x:'10',wert:3},{x:'12',wert:2}]);
      return !/[CQST]\d/.test(h.replace(/<text[^>]*>[^<]*<\/text>/g, '')) || 'Kurvenbefehl gefunden';
    });
    t('zu wenige Punkte -> Balken statt Kurve', () => {
      const h = kurvenBlock('T', [{x:'8',wert:1},{x:'10',wert:3}]);
      return (!h.includes('<svg') && h.includes('class="bar"')) || 'trotzdem Kurve';
    });
    t('Kurve bei vielen Stufen kürzt die Achse', () => {
      const p = []; for (let i = 0; i < 20; i++) p.push({ x: String(i), wert: i % 5 });
      const h = kurvenBlock('T', p);
      const achse = (h.match(/y="141"/g) || []).length;
      return achse <= 9 || ('Achsentexte: ' + achse);
    });
  
    t('Entwürfe zählen nicht mit', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Zander', entwurf:true })]);
      alleFilterAus();
      return statsRows().length === 1 || statsRows().length;
    });
    t('Filter Gewässer', () => {
      setzeFaenge([mk({ gewaesser:'Kanal' }), mk({ gewaesser:'Weser' })]);
      alleFilterAus(); state.stats.gewaesser = 'Kanal';
      return statsRows().length === 1 || statsRows().length;
    });
    t('Filter Fischart', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Barsch' })]);
      alleFilterAus(); state.stats.art = 'Barsch';
      return statsRows().length === 1 || statsRows().length;
    });
    t('Filter 30 Tage schliesst Altes aus', () => {
      const alt = new Date(Date.now() - 200*864e5).toISOString().slice(0,16);
      setzeFaenge([mk({ when: new Date().toISOString().slice(0,16), ts: Date.now() }),
                   mk({ when: alt, ts: Date.now() - 200*864e5 })]);
      alleFilterAus(); state.stats.zeit = '30t';
      return statsRows().length === 1 || statsRows().length;
    });
    t('Filter Alles nimmt beide', () => { state.stats.zeit = 'alles'; return statsRows().length === 2 || statsRows().length; });
  
    t('zaehle summiert', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Hecht' }), mk({ art:'Barsch' })]);
      alleFilterAus();
      const m = zaehle(statsRows(), c => c.art);
      return (m.get('Hecht') === 2 && m.get('Barsch') === 1) || JSON.stringify([...m]);
    });
    t('zaehle überspringt Leeres', () => {
      setzeFaenge([mk({ art:'' }), mk({ art:null }), mk({ art:'Aal' })]);
      alleFilterAus();
      return zaehle(statsRows(), c => c.art).size === 1 || zaehle(statsRows(), c => c.art).size;
    });
    t('Mehrfachfarben zählen in jeder', () => {
      setzeFaenge([mk({ farben:['Rot','Gelb'] }), mk({ farben:['Rot'] })]);
      alleFilterAus();
      const m = zaehle(statsRows(), c => farbenVon(c));
      return (m.get('Rot') === 2 && m.get('Gelb') === 1) || JSON.stringify([...m]);
    });
    t('alter Fang mit einzelner Farbe zählt mit', () => {
      setzeFaenge([mk({ farbe:'Schwarz' })]);
      alleFilterAus();
      return zaehle(statsRows(), c => farbenVon(c)).get('Schwarz') === 1 || 'nicht gezählt';
    });
  
    t('ausMap sortiert nach Menge', () => {
      const m = new Map([['A',1],['B',5],['C',3]]);
      return ausMap(m).map(e => e.label).join('') === 'BCA' || ausMap(m).map(e => e.label).join('');
    });
  
    t('balkenBlock leer gibt nichts', () => balkenBlock('X', []) === '' || 'nicht leer');
    t('balkenBlock zeigt die Zahl', () => balkenBlock('X', [{label:'A',wert:7}]).includes('<b>7</b>') || 'Zahl fehlt');
    t('längster Balken ist 100 %', () => balkenBlock('X', [{label:'A',wert:4},{label:'B',wert:2}]).includes('width:100%') || 'kein 100%');
    t('kleiner Balken bleibt sichtbar', () => {
      const h = balkenBlock('X', [{label:'A',wert:200},{label:'B',wert:1}]);
      return /width:4%/.test(h) || h.match(/width:\d+%/g).join();
    });
  
    t('Statistik rendert', () => {
      setzeFaenge([
        mk({ art:'Hecht', gewaesser:'Kanal', laenge:78, gewicht:3.2, druck:1013, wasser:19.4,
             tiefe:2.5, phase:'morgen', wetter:'bedeckt', koeder:'Gummifisch', farben:['Firetiger'] }),
        mk({ art:'Zander', gewaesser:'Kanal', laenge:55, druck:1002, wasser:17.1,
             phase:'nacht', wetter:'regen', koeder:'Wobbler', farben:['Rot','Gelb'] })
      ]);
      alleFilterAus('wasser'); renderStats();
      const h = document.querySelector('#stats-body').innerHTML;
      return h.includes('Wassertemperatur') || 'Block fehlt';
    });
    t('nur Gewaehltes wird gezeigt', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      const koerper = h.slice(h.indexOf('id="st-wahl"'));
      return !koerper.includes('Fänge nach Köder') || 'ungewaehlter Block ist da';
    });
    t('Messwerte kommen als Kurve (genug Spanne)', () => {
      // Weniger als drei Stufen faellt bewusst auf Balken zurueck — eine "Kurve"
      // durch zwei Punkte waere eine Gerade ohne Aussage. Also Spanne geben.
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 13 }), mk({ wasser: 17 }), mk({ wasser: 21 })]);
      alleFilterAus('wasser'); renderStats();
      return document.querySelector('#stats-body').innerHTML.includes('class="kurve"') || 'kein SVG';
    });
    t('zu wenig Spanne -> Balken statt Kurve', () => {
      setzeFaenge([mk({ wasser: 17.1 }), mk({ wasser: 19.4 })]);
      alleFilterAus('wasser'); renderStats();
      const h = document.querySelector('#stats-body').innerHTML;
      return (!h.includes('class="kurve"') && h.includes('class="bar"')) || 'trotzdem Kurve';
    });
    t('Kategorien bleiben Balken', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Barsch' })]);
      alleFilterAus('art'); renderStats();
      const h = document.querySelector('#stats-body').innerHTML;
      const i = h.indexOf('<h2>Fänge nach Fischart</h2>');
      return (i > 0 && h.slice(i, i + 900).includes('class="bar"')) || 'Fischart ist keine Balkenliste';
    });
    t('Waehler zeigt jede Auswertung', () => {
      const n = document.querySelectorAll('#st-wahl .chip').length;
      return n === AUSWERTUNGEN.length || n;
    });
    // Der Entwurf vom 02.08. hatte 17 Auswertungen und wurde deshalb wieder
    // herausgenommen: eine Wand aus Knoepfen, hinter der jedes Mal ein fast leeres
    // Diagramm steht. Diese Pruefung haelt die Kuerzung fest — wer eine achte
    // dazunimmt, soll darueber stolpern und es bewusst entscheiden.
    t('die Auswahl bleibt schmal', () =>
       AUSWERTUNGEN.length <= 7 || ('wieder ' + AUSWERTUNGEN.length + ' Auswertungen'));
    t('Statistik-Reiter ist erreichbar', () => {
      const tab = document.querySelector('.tab[data-go="stats"]');
      if (!tab) return 'kein Reiter in der Leiste';
      go('stats');
      const panel = document.querySelector('#v-stats');
      if (!panel) return 'kein Panel #v-stats';
      if (panel.classList.contains('hidden')) return 'Panel bleibt versteckt';
      if (!tab.classList.contains('on')) return 'Reiter wird nicht markiert';
      go('log');
      return true;
    });
    t('genau ein Chip ist markiert', () => {
      setzeFaenge([mk({ art:'Hecht' })]);
      alleFilterAus('art'); renderStats();
      const on = [...document.querySelectorAll('#st-wahl .chip.on')].map(c => c.dataset.wahl);
      return (on.length === 1 && on[0] === 'art') || on.join();
    });
    t('Antippen wechselt die Auswertung', () => {
      setzeFaenge([mk({ art:'Hecht', koeder:'Wobbler' }), mk({ art:'Barsch', koeder:'Gummifisch' })]);
      alleFilterAus('art'); renderStats();
      document.querySelector('[data-wahl="koeder"]').click();
      return document.querySelector('#stats-body').innerHTML.includes('Fänge nach Köder') || 'nicht gewechselt';
    });
    t('die vorherige Auswertung ist danach weg', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      return !h.slice(h.indexOf('id="st-wahl"')).includes('<h2>Fänge nach Fischart</h2>') || 'beide da';
    });
    t('immer nur eine Auswertung sichtbar', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      const koerper = h.slice(h.indexOf('id="st-wahl"'));
      const bloecke = (koerper.match(/<h2>/g) || []).length;
      return bloecke === 1 || ('Bloecke: ' + bloecke);
    });
    t('nochmal denselben Chip tippen aendert nichts', () => {
      const vorher = document.querySelector('#stats-body').innerHTML;
      document.querySelector('[data-wahl="koeder"]').click();
      return document.querySelector('#stats-body').innerHTML === vorher || 'hat sich geaendert';
    });
    t('Auswertung ohne Daten sagt es statt zu verschwinden', () => {
      setzeFaenge([mk({ art:'Hecht' })]);          // keine Wassertemperatur erfasst
      alleFilterAus('wasser'); renderStats();
      const h = document.querySelector('#stats-body').innerHTML;
      return (h.includes('Wassertemp') && h.includes('noch kein Fang')) || 'still verschwunden';
    });
    t('unbekannte Auswahl faellt auf die erste zurueck', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Barsch' })]);
      alleFilterAus('gibtsnicht'); renderStats();
      return document.querySelector('#stats-body').innerHTML.includes('Fänge nach Fischart') || 'nichts gezeigt';
    });
    t('Kacheln bleiben immer', () => {
      return document.querySelector('#stats-body').innerHTML.includes('class="tiles"') || 'Kacheln weg';
    });
    t('jede Auswertung laeuft ohne Absturz', () => {
      for (const a of AUSWERTUNGEN){
        alleFilterAus(a.key);
        try { renderStats(); } catch (e){ return a.key + ': ' + e.message; }
      }
      return true;
    });
    t('jede Auswertung haelt leere Daten aus', () => {
      const merk = state.catches;
      setzeFaenge([mk({})]);
      for (const a of AUSWERTUNGEN){
        alleFilterAus(a.key);
        try { renderStats(); } catch (e){ return a.key + ': ' + e.message; }
      }
      setzeFaenge(merk);
      return true;
    });
    // Ab hier wieder mit eigenem Datensatz, damit die Reihenfolge der Tests egal ist.
    const zweiFaenge = () => {
      setzeFaenge([
        mk({ art:'Hecht', gewaesser:'Kanal', laenge:78, gewicht:3.2, koeder:'Gummifisch' }),
        mk({ art:'Zander', gewaesser:'Kanal', laenge:55, koeder:'Wobbler' })
      ]);
    };
    t('Statistik nennt den grössten Fisch', () => {
      zweiFaenge(); alleFilterAus('art'); renderStats();
      return document.querySelector('#stats-body').innerHTML.includes('78 cm') || 'fehlt';
    });
    t('Statistik warnt bei wenig Daten',
       () => document.querySelector('#stats-body').innerHTML.includes('zu wenige') || 'keine Warnung');
    t('Statistik sagt nirgends "bester"',
       () => !/bester|beste Köder|Bester/.test(document.querySelector('#stats-body').innerHTML) || 'steht doch drin');
    t('Statistik weist auf fehlende Leer-Ansitze hin', () => {
      zweiFaenge(); alleFilterAus('koeder'); renderStats();
      return document.querySelector('#stats-body').innerHTML.includes('ohne Fang') || 'Hinweis fehlt';
    });
    t('Zähler in der Kopfzeile', () => {
      zweiFaenge(); alleFilterAus(); renderStats();
      return document.querySelector('#stats-pill').textContent === '2 Fänge'
          || document.querySelector('#stats-pill').textContent;
    });
    t('Statistik ohne Fänge', () => {
      setzeFaenge([]); alleFilterAus(); renderStats();
      return document.querySelector('#stats-body').innerHTML.includes('Noch keine fertigen') || 'falscher Text';
    });
    t('Statistik mit leerem Filterergebnis', () => {
      setzeFaenge([mk({ art:'Hecht' })]);
      alleFilterAus(); state.stats.art = 'Wels'; renderStats();
      return document.querySelector('#stats-body').innerHTML.includes('keinen Fang') || 'falscher Text';
    });
    t('Filterliste behält die aktive Auswahl', () => {
      setzeFaenge([mk({ art:'Hecht' }), mk({ art:'Wels' })]);
      alleFilterAus(); state.stats.art = 'Wels'; renderStats();
      return document.querySelector('#st-art').value === 'Wels' || document.querySelector('#st-art').value;
    });
    t('Zeitraum-Chips gebaut', () => document.querySelectorAll('#st-zeit .chip').length === ZEITRAEUME.length
                                    || document.querySelectorAll('#st-zeit .chip').length);
    t('Statistik-Reiter existiert', () => !!document.querySelector('[data-go="stats"]') || 'fehlt');
    t('go("stats") zeigt die Ansicht', () => {
      setzeFaenge([mk({ art:'Hecht' })]); alleFilterAus(); go('stats');
      return (!document.querySelector('#v-stats').classList.contains('hidden')
              && document.querySelector('#v-log').classList.contains('hidden')) || 'falsche Ansicht';
    });
    t('Monatskurve laeuft Jan bis Dez', () => {
      setzeFaenge([mk({ when:'2026-09-01T08:00', ts:new Date('2026-09-01T08:00').getTime() }),
                   mk({ when:'2026-03-01T08:00', ts:new Date('2026-03-01T08:00').getTime() }),
                   mk({ when:'2026-03-05T08:00', ts:new Date('2026-03-05T08:00').getTime() })]);
      alleFilterAus('monat'); renderStats();
      const h = document.querySelector('#stats-body').innerHTML;
      const i = h.indexOf('Fänge nach Monat');
      const teil = h.slice(i);
      return (teil.indexOf('>Jan<') < teil.indexOf('>Mär<')
           && teil.indexOf('>Mär<') < teil.indexOf('>Sep<')) || 'falsche Reihenfolge';
    });
    t('Monatskurve zeigt alle 12 Monate', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      const teil = h.slice(h.indexOf('Fänge nach Monat'));
      return teil.includes('>Dez<') || 'Dezember fehlt';
    });
  
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
    sandbox([mkC('a', 5000), mkC('b', 50)]);
    localStorage.setItem('angellog-sync-push', '1000');
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return (raus.length === 1 && raus[0].id === 'a') || JSON.stringify(raus.map(r => r.id));
  });
  ta('Entwuerfe bleiben lokal', async () => {
    sandbox([mkC('a', 5000, { entwurf: true }), mkC('b', 5000)]);
    localStorage.setItem('angellog-sync-push', '0');
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    return (raus.length === 1 && raus[0].id === 'b') || JSON.stringify(raus.map(r => r.id));
  });
  ta('Geloeschtes geht als Grabstein hoch', async () => {
    sandbox([], [{ id: 'weg', updated: 9000, gemeldet: false }]);
    localStorage.setItem('angellog-sync-push', '0');
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    const g = raus.find(r => r.id === 'weg');
    return (g && g.geloescht === true && g.daten === null) || JSON.stringify(raus);
  });
  ta('Ein gemeldeter Grabstein geht nicht nochmal hoch', async () => {
    sandbox([], [{ id: 'weg', updated: 9000, gemeldet: false }]);
    localStorage.setItem('angellog-sync-push', '0');
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    await hochladen();
    await hochladen();
    return (raus.length === 0) || 'zweiter Lauf schickte ' + raus.length;
  });

  // ---- Herunterladen ----
  const antwort = daten => ({ ok: true, json: async () => daten });
  ta('Neuer Fang vom Server kommt an', async () => {
    sandbox([]);
    localStorage.removeItem('angellog-sync');
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'neu', updated: 100, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'neu', updated: 100, geloescht: false, daten: { art: 'Zander' }, fotos: [] }]);
    await herunterladen();
    return (fakeDB.has('neu') && fakeDB.get('neu').art === 'Zander') || 'fehlt';
  });
  ta('Aeltere Fassung vom Server ueberschreibt nicht', async () => {
    sandbox([mkC('a', 9000, { art: 'Wels' })]);
    localStorage.removeItem('angellog-sync');
    let vollGeholt = false;
    api = async pfad => { if (!pfad.includes('select=id,')) vollGeholt = true;
      return antwort([{ id: 'a', updated: 100, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }]); };
    await herunterladen();
    return (fakeDB.get('a').art === 'Wels' && !vollGeholt) || 'lokale Fassung wurde ueberschrieben';
  });
  ta('Juengere Fassung vom Server gewinnt', async () => {
    sandbox([mkC('a', 100, { art: 'Wels' })]);
    localStorage.removeItem('angellog-sync');
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'a', updated: 9000, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'a', updated: 9000, geloescht: false, daten: { art: 'Hecht' }, fotos: [] }]);
    await herunterladen();
    return (fakeDB.get('a').art === 'Hecht') || fakeDB.get('a').art;
  });
  ta('Geholter Fang behaelt sein updated', async () => {
    sandbox([]);
    localStorage.removeItem('angellog-sync');
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'n', updated: 4242, geloescht: false, serverzeit: '2026-08-03T10:00:00Z' }])
      : antwort([{ id: 'n', updated: 4242, geloescht: false, daten: { art: 'Aal' }, fotos: [] }]);
    await herunterladen();
    return (fakeDB.get('n').updated === 4242) || 'updated wurde auf ' + fakeDB.get('n').updated + ' gesetzt';
  });
  ta('Grabstein vom Server loescht lokal', async () => {
    sandbox([mkC('weg', 100)]);
    localStorage.removeItem('angellog-sync');
    api = async () => antwort([{ id: 'weg', updated: 9000, geloescht: true, serverzeit: '2026-08-03T10:00:00Z' }]);
    await herunterladen();
    return (!fakeDB.has('weg')) || 'Fang ist noch da';
  });
  ta('Grabstein fuer Unbekanntes tut nichts', async () => {
    sandbox([mkC('a', 100)]);
    localStorage.removeItem('angellog-sync');
    api = async () => antwort([{ id: 'nie-gehabt', updated: 9000, geloescht: true, serverzeit: '2026-08-03T10:00:00Z' }]);
    await herunterladen();
    return (fakeDB.size === 1 && fakeDB.has('a')) || 'Bestand veraendert';
  });
  ta('Sync-Stand wandert mit', async () => {
    sandbox([]);
    localStorage.removeItem('angellog-sync');
    api = async pfad => pfad.includes('select=id,')
      ? antwort([{ id: 'x', updated: 1, geloescht: true, serverzeit: '2026-08-03T11:22:33Z' }])
      : antwort([]);
    await herunterladen();
    return (localStorage.getItem('angellog-sync') === '2026-08-03T11:22:33Z') || localStorage.getItem('angellog-sync');
  });
  ta('Nichts Neues laesst den Stand stehen', async () => {
    sandbox([]);
    localStorage.setItem('angellog-sync', '2026-08-01T00:00:00Z');
    api = async () => antwort([]);
    const n = await herunterladen();
    return (n === 0 && localStorage.getItem('angellog-sync') === '2026-08-01T00:00:00Z') || 'Stand veraendert';
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
    localStorage.removeItem('angellog-sync');
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
    sandbox([mkC('alt1', 5000), mkC('alt2', 6000), mkC('entw', 7000, { entwurf: true })]);
    localStorage.setItem('angellog-sync-push', String(Date.now() + 60000));  // alles schon gemeldet
    let raus = null; zeilenSchreiben = async z => { raus = z; };
    api = async () => ({ ok: true, json: async () => [] });
    konto = { access_token: 'tok' };
    await ersterAbgleich();
    konto = null;
    // Trotz gesetzter Marke muessen beide fertigen Faenge hoch — der Entwurf nicht.
    const ids = (raus || []).map(r => r.id).sort();
    return (ids.length === 2 && ids[0] === 'alt1' && ids[1] === 'alt2') || JSON.stringify(ids);
  });

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
  t('Download steht unter der Datenschutzerklaerung', () => {
    const inner = document.querySelector('#sheet .inner');
    const kinder = [...inner.children];
    return (kinder.indexOf(document.querySelector('#btn-export'))
            > kinder.indexOf(document.querySelector('#btn-datenschutz'))) || 'steht davor';
  });
  t('Download steht vor dem Schliessen-Knopf', () => {
    const inner = document.querySelector('#sheet .inner');
    const kinder = [...inner.children];
    return (kinder.indexOf(document.querySelector('#btn-export'))
            < kinder.indexOf(document.querySelector('#btn-close-sheet'))) || 'steht dahinter';
  });
  t('Datenschutztext verweist auf den Download', () =>
    /Meine Daten herunterladen/.test(datenschutzText()) || 'Text nennt ihn nicht');
  t('Datenschutztext spricht nicht mehr von Backup', () =>
    (!/Backup/.test(datenschutzText())) || 'Backup steht noch drin');

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

html = (WORK / 'index.html').read_text(encoding='utf-8')
(WORK / 'test.html').write_text(html + TESTS, encoding='utf-8')

r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--virtual-time-budget=20000', '--allow-file-access-from-files',
                    '--dump-dom', (WORK / 'test.html').as_uri()],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
m = re.search(r'<pre id="testout">(.*?)</pre>', r.stdout, re.S)
if not m:
    print('Kein Ergebnis. Chrome-Ausgabe (Ende):')
    print(r.stdout[-3000:]); print(r.stderr[-3000:]); sys.exit(1)
txt = m.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
print(txt)
sys.exit(0 if ', 0 fehlgeschlagen' in txt else 1)
