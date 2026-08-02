# Lädt die echte index.html in Chrome headless, hängt Prüfungen an und liest das Ergebnis.
import subprocess, re, pathlib, shutil, sys

SRC  = pathlib.Path(r'c:\Users\karlm\OneDrive\Desktop\angel-log')
WORK = pathlib.Path(__file__).parent / 'testrun'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

if WORK.exists(): shutil.rmtree(WORK)
shutil.copytree(SRC, WORK, ignore=shutil.ignore_patterns('.git'))

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
      return !koerper.includes('Fänge nach Luftdruck') || 'ungewaehlter Block ist da';
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
      const i = h.indexOf('<h2>Fischart</h2>');
      return (i > 0 && h.slice(i, i + 900).includes('class="bar"')) || 'Fischart ist keine Balkenliste';
    });
    t('Waehler zeigt jede Auswertung', () => {
      const n = document.querySelectorAll('#st-wahl .chip').length;
      return n === AUSWERTUNGEN.length || n;
    });
    t('genau ein Chip ist markiert', () => {
      setzeFaenge([mk({ art:'Hecht' })]);
      alleFilterAus('art'); renderStats();
      const on = [...document.querySelectorAll('#st-wahl .chip.on')].map(c => c.dataset.wahl);
      return (on.length === 1 && on[0] === 'art') || on.join();
    });
    t('Antippen wechselt die Auswertung', () => {
      setzeFaenge([mk({ druck: 1000 }), mk({ druck: 1010 }), mk({ druck: 1020 })]);
      alleFilterAus('art'); renderStats();
      document.querySelector('[data-wahl="druck"]').click();
      return document.querySelector('#stats-body').innerHTML.includes('Fänge nach Luftdruck') || 'nicht gewechselt';
    });
    t('die vorherige Auswertung ist danach weg', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      return !h.slice(h.indexOf('id="st-wahl"')).includes('<h2>Fischart</h2>') || 'beide da';
    });
    t('immer nur eine Auswertung sichtbar', () => {
      const h = document.querySelector('#stats-body').innerHTML;
      const koerper = h.slice(h.indexOf('id="st-wahl"'));
      const bloecke = (koerper.match(/<h2>/g) || []).length;
      return bloecke === 1 || ('Bloecke: ' + bloecke);
    });
    t('nochmal denselben Chip tippen aendert nichts', () => {
      const vorher = document.querySelector('#stats-body').innerHTML;
      document.querySelector('[data-wahl="druck"]').click();
      return document.querySelector('#stats-body').innerHTML === vorher || 'hat sich geaendert';
    });
    t('Auswertung ohne Daten sagt es statt zu verschwinden', () => {
      setzeFaenge([mk({ art:'Hecht' })]);          // kein Luftdruck erfasst
      alleFilterAus('druck'); renderStats();
      const h = document.querySelector('#stats-body').innerHTML;
      return (h.includes('Luftdruck') && h.includes('noch kein Fang')) || 'still verschwunden';
    });
    t('unbekannte Auswahl faellt auf die erste zurueck', () => {
      setzeFaenge([mk({ wasser: 9 }), mk({ wasser: 13 }), mk({ wasser: 17 })]);
      alleFilterAus('gibtsnicht'); renderStats();
      return document.querySelector('#stats-body').innerHTML.includes('Wassertemperatur') || 'nichts gezeigt';
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

  const pre = document.createElement('pre');
  pre.id = 'testout';
  pre.textContent = out.join('\n') + '\n=== ' + ok + ' ok, ' + bad + ' fehlgeschlagen ===';
  document.body.appendChild(pre);
})();
</script>
"""

html = (WORK / 'index.html').read_text(encoding='utf-8')
(WORK / 'test.html').write_text(html + TESTS, encoding='utf-8')

r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--virtual-time-budget=6000', '--allow-file-access-from-files',
                    '--dump-dom', (WORK / 'test.html').as_uri()],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
m = re.search(r'<pre id="testout">(.*?)</pre>', r.stdout, re.S)
if not m:
    print('Kein Ergebnis. Chrome-Ausgabe (Ende):')
    print(r.stdout[-3000:]); print(r.stderr[-3000:]); sys.exit(1)
txt = m.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
print(txt)
sys.exit(0 if ', 0 fehlgeschlagen' in txt else 1)
