# -*- coding: utf-8 -*-
"""Gegenprobe zu pruefungen.py (angelegt am 22.09.2026 mit dem Admin-Teil, v60).

    python gegenprobe.py

Baut die App in einem Wegwerf-Ordner nach, macht dort **je einen Handgriff
kaputt** und erwartet, dass genau die Pruefung rot wird, die ihn bewachen soll.

🔴 Warum das noetig ist: eine Pruefung, die nicht rot werden kann, ist keine
   Pruefung. Beim Bau des Admin-Teils ist es sofort passiert — zwei der neuen
   Pruefungen waren gruen, weil sie gegen eine Attrappe liefen, die eine fruehere
   Pruefung stehen gelassen hatte. Sie haetten nie etwas bemerkt.

⚠️ Kaputt gemacht wird die **Aufrufstelle**, nicht die Funktion. Wer nur die
   Funktion entfernt, prueft, ob sie existiert — nicht, ob sie benutzt wird.
⚠️ Greift ein Handgriff nicht (Textstelle nicht gefunden), meldet die Gegenprobe
   das laut. Eine Probe, die ins Leere zeigt, sieht sonst aus wie eine bestandene.
"""
import subprocess, sys, pathlib, shutil, tempfile

SRC = pathlib.Path(__file__).resolve().parent

# (Name, Datei, Suchtext, Ersatz, erwarteter Wortlaut in der roten Zeile)
PROBEN = [
    # ---- Fremde Daten im eigenen Browser: alles muss Text bleiben ----
    ('Fischart der anderen nicht entschaerfen',
     'index.html',
     "const kopf = [`<b>${esc(text(f.art) || T('Fang'))}</b>`];",
     "const kopf = [`<b>${text(f.art) || T('Fang')}</b>`];",
     'Schadcode im Fischnamen'),

    ('Benutzernamen der anderen nicht entschaerfen',
     'index.html',
     "${esc(text(f.name) || T('ohne Benutzernamen'))}",
     "${text(f.name) || T('ohne Benutzernamen')}",
     'Schadcode im Fischnamen'),

    ('Gewaesser der anderen nicht entschaerfen',
     'index.html',
     "if (text(f.gewaesser)) kopf.push(esc(f.gewaesser));",
     "if (text(f.gewaesser)) kopf.push(f.gewaesser);",
     'Schadcode im Fischnamen'),

    # v61: seit alle Angaben im Popup stehen, gehen Koeder, Wind, Messstelle ... durch kv().
    ('Die Werte-Zeilen im Popup nicht entschaerfen',
     'index.html',
     "<b>${esc(v)}</b></div>`;",
     "<b>${v}</b></div>`;",
     'Schadcode in JEDEM Feld'),

    ('Die Notiz der anderen nicht entschaerfen',
     'index.html',
     "${esc(notiz).replace(/\\n/g, '<br>')}",
     "${notiz.replace(/\\n/g, '<br>')}",
     'Schadcode in JEDEM Feld'),

    ('Das Popup laesst Angaben der Fang-Ansicht weg (Koeder)',
     'index.html',
     "            kv('Köder', text(f.koeder)),\n",
     "",
     'das Popup zeigt alle Angaben'),

    ('Koordinaten der anderen nicht pruefen',
     'index.html',
     ".filter(f => f && zahl(f.lat) != null && zahl(f.lon) != null\n"
     "                   && Math.abs(f.lat) <= 90 && Math.abs(f.lon) <= 180)",
     ".filter(f => f)",
     'kaputte Koordinaten'),

    # ---- Kein Fehlschlag darf wie eine Antwort aussehen ----
    ('Fehlende Funktion wie jeden anderen Fehler behandeln',
     'index.html',
     "  if (code === 'PGRST202' || r.status === 404) throw adminFehler('fehlt', r.status);\n",
     "",
     'fehlt die Funktion'),

    ('Ohne Zugangs-Token fragen',
     'index.html',
     "try { r = await api('/rest/v1/rpc/' + fn, { method: 'POST', body: '{}' }); }",
     "try { r = await fetch(SUPA_URL + '/rest/v1/rpc/' + fn, { method: 'POST', body: '{}', headers: kopf(false) }); }",
     'mit dem Zugangs-Token'),

    ('Scheitern auf der Karte still lassen',
     'index.html',
     "    $('#map-count').textContent = eigeneText + ' · ' + T('andere: Fehler');\n",
     "",
     'scheitert die Abfrage'),

    # ---- Ohne Schalter fragt niemand, und Veraltetes zeichnet nichts ----
    ('Karte fragt schon, wenn nur der Admin offen ist',
     'index.html',
     "const fremdP = adminKarteAn() ? adminAbfrage('angel_admin_faenge') : null;",
     "const fremdP = adminAn() ? adminAbfrage('angel_admin_faenge') : null;",
     'ohne Karten-Schalter fragt sie niemanden'),

    ('Ueberholte Antwort trotzdem zeichnen',
     'index.html',
     "  if (lauf !== fremdLauf) return;\n  /* ⚠️ maxHeight:",
     "  /* ⚠️ maxHeight:",
     'ueberholte Antwort'),

    # ---- Die rote Nadel (v61): "genauso wie meine nur in rot" ----
    ('Fremde Faenge wieder als Kreis statt als Nadel',
     'index.html',
     "L.marker([f.lat, f.lon], { icon: nadelRot(L) })",
     "L.circleMarker([f.lat, f.lon], { radius: 7 })",
     'mit Schalter stehen die fremden Faenge drauf'),

    ('Rote Nadel mit anderen Massen als die eigene',
     'index.html',
     "iconSize: [25, 41], iconAnchor: [12, 41],",
     "iconSize: [20, 33], iconAnchor: [10, 33],",
     'mit Schalter stehen die fremden Faenge drauf'),

    ('Popup ohne Hoehengrenze (laenger als das Handy)',
     'index.html',
     "{ maxHeight: 320, maxWidth: 280, minWidth: 220 }",
     "{ maxWidth: 280, minWidth: 220 }",
     'mit Schalter stehen die fremden Faenge drauf'),

    ('Rote Nadel fehlt im Service Worker',
     'sw.js',
     "'./nadel-rot.png', './nadel-rot-2x.png'];",
     "'./nadel-rot.png'];",
     'nadel-rot-2x.png fehlt im Service Worker'),

    # Datei-Hebel: statt Text zu ersetzen, wird die Datei durch eine andere ersetzt.
    ('Rote Nadel ist in Wahrheit blau',
     'nadel-rot-2x.png',
     None,
     'leaflet/images/marker-icon-2x.png',
     'das ist kein Rot'),

    # ---- Die Geste und das Zumachen ----
    ('Geste sperrt wieder zu (der Fehler von Gym-Log, 27.08.2026)',
     'index.html',
     "if (adminAn()){ toast(T('Admin ist schon offen — steht unten in den Einstellungen')); return; }",
     "if (adminAn()){ try { localStorage.removeItem(ADMIN_KEY); } catch {} return; }",
     'sperren NICHT wieder zu'),

    ('Zumachen laesst den Karten-Schalter stehen',
     'index.html',
     "try { localStorage.removeItem(ADMIN_KEY); localStorage.removeItem(ADMIN_KARTE_KEY); } catch {}",
     "try { localStorage.removeItem(ADMIN_KEY); } catch {}",
     'raeumt auch den Karten-Schalter'),

    ('Sprachwechsel zeichnet den Admin-Block nicht neu',
     'index.html',
     "  try { renderAdmin(); } catch {}\n",
     "",
     'Umschalten auf Englisch'),

    # ---- Die Datenbank: wer fragt, und was herausgeht ----
    ('Admin-Pruefung vor den Faengen streichen',
     'supabase.sql',
     "  if not public.angel_ist_admin() then\n"
     "    raise exception 'kein Admin' using errcode = '42501';\n"
     "  end if;\n"
     "  -- ⚠️ `- 'photos'`",
     "  -- ⚠️ `- 'photos'`",
     'angel_admin_faenge(): die Admin-Pruefung fehlt'),

    ('Admin-Pruefung vor der Kontenzahl streichen',
     'supabase.sql',
     "  if not public.angel_ist_admin() then\n"
     "    raise exception 'kein Admin' using errcode = '42501';\n"
     "  end if;\n"
     "  return jsonb_build_object('konten'",
     "  return jsonb_build_object('konten'",
     'angel_admin_zahlen(): die Admin-Pruefung fehlt'),

    ('Admin-Pruefung hinter den Datenzugriff schieben',
     'supabase.sql',
     "  if not public.angel_ist_admin() then\n"
     "    raise exception 'kein Admin' using errcode = '42501';\n"
     "  end if;\n"
     "  return jsonb_build_object('konten', (select count(*) from auth.users));",
     "  perform (select count(*) from auth.users);\n"
     "  if not public.angel_ist_admin() then\n"
     "    raise exception 'kein Admin' using errcode = '42501';\n"
     "  end if;\n"
     "  return jsonb_build_object('konten', (select count(*) from auth.users));",
     'angel_admin_zahlen(): die Admin-Pruefung fehlt oder steht HINTER'),

    ('Faenge fuer anon freigeben',
     'supabase.sql',
     "grant execute on function public.angel_admin_faenge() to authenticated;",
     "grant execute on function public.angel_admin_faenge() to anon, authenticated;",
     'ist fuer anon freigegeben'),

    ('Das revoke vor der Faenge-Funktion streichen',
     'supabase.sql',
     "revoke all on function public.angel_admin_faenge() from public, anon;\n",
     "",
     'angel_admin_faenge(): das "revoke'),

    ('search_path der Kontenzahl streichen',
     'supabase.sql',
     "security definer\nset search_path = public, auth\nas $$\nbegin\n  if not public.angel_ist_admin()",
     "security definer\nas $$\nbegin\n  if not public.angel_ist_admin()",
     'gehoeren zusammen in den Kopf'),

    ('Admin bei jedem SQL-Lauf neu setzen (do update)',
     'supabase.sql',
     "where p.username in ('karl', 'tibo')\non conflict (name) do nothing;",
     "where p.username in ('karl', 'tibo')\non conflict (name) do update set user_id = excluded.user_id;",
     'on conflict (name) do nothing'),

    ('Fotos der anderen mit herausgeben',
     'supabase.sql',
     "jsonb_agg((f.daten - 'photos') || jsonb_build_object('name', p.username))",
     "jsonb_agg((f.daten - 'photos') || jsonb_build_object('name', p.username, 'bilder', f.fotos))",
     'gibt Fotos heraus'),

    ('Fotos aus alten Faengen im Datensatz mitgeben',
     'supabase.sql',
     "jsonb_agg((f.daten - 'photos') || jsonb_build_object",
     "jsonb_agg(f.daten || jsonb_build_object",
     'nimmt Fotos, die in alten Faengen'),

    # ---- Die Admin-Liste (v61) ----
    ('angel_ist_admin liest die Liste, vergleicht aber nicht',
     'supabase.sql',
     "select 1 from public.angel_admins a where a.user_id = auth.uid());",
     "select 1 from public.angel_admins a);",
     'vergleicht nicht mehr das angemeldete Konto'),

    ('Die Admin-Liste bekommt eine Policy',
     'supabase.sql',
     "alter table public.angel_admins enable row level security;",
     "alter table public.angel_admins enable row level security;\n"
     "create policy \"alle lesen\" on public.angel_admins for select using (true);",
     'angel_admins hat eine Policy'),

    ('Die Admin-Liste ohne Row Level Security',
     'supabase.sql',
     "alter table public.angel_admins enable row level security;",
     "",
     'angel_admins ohne Row Level Security'),

    ('Die Admin-Liste haengt an auth.users (cascade)',
     'supabase.sql',
     "  user_id  uuid        not null,\n  seit",
     "  user_id  uuid        not null references auth.users(id) on delete cascade,\n  seit",
     'angel_admins haengt an auth.users'),

    ('Ein dritter Admin, den der Text nicht kennt',
     'supabase.sql',
     "where p.username in ('karl', 'tibo')",
     "where p.username in ('karl', 'tibo', 'bruder')",
     'setzt 3 Admins'),

    # ---- Was der Code tut, muss der Text sagen ----
    ('Admin-Absatz aus der deutschen Erklaerung nehmen',
     'index.html',
     "<p><b>Admin-Ansicht:</b>",
     "<p><b>Hinweis:</b>",
     'die Datenschutzerklaerung sagt es nicht'),

    ('Das alte Versprechen zurueckholen',
     'index.html',
     "keine Auswertung deiner Daten zu anderen als den hier genannten\n    Zwecken.",
     "keine Auswertung deiner Daten zu anderen Zwecken.",
     'das alte "keine Auswertung zu anderen Zwecken"'),

    ('Englisch verschweigt, dass Fotos fehlen',
     'index.html',
     " Only the photos are not\n    shown there.",
     "",
     'Datenschutz (englisch): zur Admin-Ansicht fehlt'),

    ('Der Text verschweigt die Notiz',
     'index.html',
     "Zeitpunkt, Fisch, Wetter, Wasser, Köder und <b>Notiz</b>, dazu der",
     "Zeitpunkt, Fisch, Wetter, Wasser und Köder, dazu der",
     'zur Admin-Ansicht fehlt "Notiz"'),

    ('Der Text verschweigt den zweiten Admin',
     'index.html',
     "der Betreiber und ein zweiter Admin,",
     "der Betreiber und ein Helfer,",
     'der Text nennt keinen zweiten'),

    ('Der alte Satz "Andere Nutzer sehen deine Faenge nicht" kommt zurueck',
     'index.html',
     "Außer ihnen sieht niemand deine Fänge.",
     "Andere Nutzer sehen deine Fänge nicht.",
     'der zweite Admin IST'),
]


def lauf(ordner):
    r = subprocess.run([sys.executable, 'pruefungen.py'], cwd=str(ordner),
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=900)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def zeigen(s):
    enc = sys.stdout.encoding or 'utf-8'
    print(s.encode(enc, errors='replace').decode(enc, errors='replace'), flush=True)


# Erst sicherstellen, dass unveraendert alles gruen ist. Sonst sagt eine rote
# Gegenprobe nichts — sie waere auch ohne den Handgriff rot gewesen.
code, aus = lauf(SRC)
if code != 0:
    zeigen('Der Pruefstand ist schon UNVERAENDERT rot. Erst das klaeren.')
    zeigen(aus[-2000:])
    sys.exit(1)
zeigen('Unveraendert: gruen. Jetzt die Handgriffe.\n')

#   python gegenprobe.py Nadel      -> nur die Hebel, in deren Namen "Nadel" vorkommt.
# Fuer einen einzeln nachgezogenen Hebel, statt 20 Minuten alles neu.
if len(sys.argv) > 1:
    PROBEN = [p for p in PROBEN if sys.argv[1].lower() in p[0].lower()]
    zeigen(f'Nur {len(PROBEN)} Hebel mit "{sys.argv[1]}".\n')

fehler = 0
for name, datei, alt, neu, erwartet in PROBEN:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        ziel = pathlib.Path(tmp) / 'app'
        shutil.copytree(SRC, ziel, ignore=shutil.ignore_patterns('.testrun', '.git'))
        pfad = ziel / datei
        if alt is None:
            # Datei-Hebel: `neu` ist die Datei, die an die Stelle von `datei` tritt.
            vorher = pfad.read_bytes()
            pfad.write_bytes((ziel / neu).read_bytes())
            if pfad.read_bytes() == vorher:
                zeigen(f'HEBEL GRIFF NICHT: {name}\n   {datei} ist nach dem Austausch '
                       f'unveraendert — die Gegenprobe zeigt ins Leere.')
                fehler += 1
                continue
        else:
            text = pfad.read_text(encoding='utf-8')
            if alt not in text:
                zeigen(f'HEBEL GRIFF NICHT: {name}\n   Textstelle nicht gefunden in {datei} — '
                       f'die Gegenprobe zeigt ins Leere.')
                fehler += 1
                continue
            pfad.write_text(text.replace(alt, neu, 1), encoding='utf-8')

        code, aus = lauf(ziel)
        zeilen = aus.splitlines()
        rote = [z.strip() for z in zeilen if z.startswith(('FAIL', 'ERR'))]
        # Die statischen Pruefungen brechen mit einem Satz ab, nicht mit FAIL-Zeilen.
        if not rote:
            rote = [' '.join(z.strip() for z in zeilen[-3:])]
        traf = any(erwartet in z for z in rote)

        if code == 0:
            zeigen(f'ROT ERWARTET, kam aber gruen: {name}')
            zeigen(f'   -> "{erwartet}" bewacht diesen Handgriff nicht.')
            fehler += 1
        elif not traf:
            zeigen(f'Rot, aber an der falschen Stelle: {name}')
            zeigen(f'   erwartet: {erwartet}')
            zeigen(f'   bekommen: {rote[:3]}')
            fehler += 1
        else:
            treffer = [z for z in rote if erwartet in z][0]
            # Ab der Fundstelle zeigen -- bei den statischen steht davor nur Grünes.
            vorn = treffer.find('FAIL') if treffer.startswith(('FAIL', 'ERR')) else treffer.find(erwartet)
            zeigen(f'ok  {name}')
            zeigen(f'    -> rot: {treffer[max(vorn, 0):][:110]}')

zeigen('')
zeigen(f'=== {len(PROBEN) - fehler} von {len(PROBEN)} Handgriffen werden bemerkt ===')
sys.exit(0 if fehler == 0 else 1)
