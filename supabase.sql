-- =====================================================================
--  Angel-Log — Konto & Cloud-Sync
--  Einmal im Supabase-SQL-Editor ausführen (Dashboard → SQL Editor → New query).
--  Danach oben in index.html SUPA_URL und SUPA_KEY eintragen.
--
--  Der Block ist gefahrlos wiederholbar: alles ist "if not exists" bzw.
--  "create or replace". Zweimal ausführen richtet keinen Schaden an.
-- =====================================================================

-- ---------------------------------------------------------------------
--  1. Tabelle
--
--  id ist TEXT, nicht UUID. Die App erzeugt IDs per crypto.randomUUID(),
--  hat aber einen Rückfall für alte Safari-Versionen, der kein gültiges
--  UUID-Format liefert. Mit TEXT passt beides — mit UUID würde die App auf
--  genau den alten Geräten scheitern, für die der Rückfall gebaut wurde.
--
--  Zwei Zeitstempel mit verschiedenen Aufgaben:
--    updated    = Uhr des Geräts. Entscheidet Konflikte (jüngere gewinnt).
--    serverzeit = Uhr des Servers. Wann diese Zeile zuletzt angefasst wurde.
--
--  ⚠️ Seit dem 11.08.2026 steuert serverzeit nichts mehr. Hier stand
--  "Steuert, was ein Gerät nachladen muss" — die App merkte sich einen Stand
--  und fragte "was ist seither passiert?". Genau diese Bauart hat in drei
--  Tagen dreimal Löcher gehabt; sie ist abgeschafft. Die App holt jetzt bei
--  jedem Abgleich die Kennzahlen des ganzen Bestands (id, updated, geloescht)
--  und vergleicht Fang für Fang.
--
--  Die Spalte bleibt trotzdem: sie kostet nichts und ist die einzige Uhr hier,
--  der man trauen kann — die des Geräts kann falsch gestellt sein. Wer im
--  Dashboard nachsehen muss, wann eine Zeile zuletzt angefasst wurde, braucht
--  genau sie. Nichts an dieser Datei muss deshalb erneut ausgeführt werden.
-- ---------------------------------------------------------------------
create table if not exists public.angel_faenge (
  id          text        primary key,
  user_id     uuid        not null default auth.uid()
                          references auth.users(id) on delete cascade,
  updated     bigint      not null,
  serverzeit  timestamptz not null default now(),
  geloescht   boolean     not null default false,
  daten       jsonb,
  fotos       jsonb
);

-- ⚠️ Der Abgleich benutzt diesen Index seit dem 11.08.2026 nicht mehr — er
-- fragte "was ist seit X passiert, für mich?", und diese Frage gibt es nicht
-- mehr. Er bleibt stehen: ihn zu entfernen hieße, dass Karl diese Datei erneut
-- ausführen muss, und ein ungenutzter Index auf einem Bestand dieser Größe
-- kostet nichts Messbares. Sortiert wird jetzt nach id, dafür trägt schon der
-- Primärschlüssel.
create index if not exists angel_faenge_sync_idx
  on public.angel_faenge (user_id, serverzeit);

-- ---------------------------------------------------------------------
--  2. serverzeit bei jeder Änderung neu setzen
--
--  Ohne diesen Trigger bleibt serverzeit auf dem Wert vom Anlegen stehen und
--  hieße dann "angelegt am" statt "zuletzt angefasst am".
--  ⚠️ Bis zum 11.08.2026 hing daran der ganze Abgleich: eine Änderung wäre für
--  das zweite Gerät unsichtbar gewesen. Das ist vorbei — heute ist es nur noch
--  eine Angabe zum Nachsehen, und der Trigger hält sie ehrlich.
-- ---------------------------------------------------------------------
create or replace function public.angel_serverzeit()
returns trigger language plpgsql as $$
begin
  new.serverzeit := now();
  return new;
end $$;

drop trigger if exists angel_faenge_serverzeit on public.angel_faenge;
create trigger angel_faenge_serverzeit
  before insert or update on public.angel_faenge
  for each row execute function public.angel_serverzeit();

-- ---------------------------------------------------------------------
--  3. Zugriffsregeln (Row Level Security)
--
--  ⚠️ Der wichtigste Teil der Datei. Ohne RLS kann jeder, der den
--  öffentlichen anon-Key aus dem Quelltext liest, den kompletten Bestand
--  aller Nutzer abrufen. Der Key ist per Konstruktion öffentlich —
--  er steht in index.html und damit in jedem Browser. Was schützt, ist
--  ausschließlich diese Regel: jeder sieht nur seine eigenen Zeilen.
--
--  with check beim Schreiben ist genauso wichtig wie using beim Lesen:
--  sonst könnte man zwar nichts Fremdes lesen, aber Zeilen unter fremder
--  user_id anlegen.
-- ---------------------------------------------------------------------
alter table public.angel_faenge enable row level security;

drop policy if exists "eigene faenge lesen"    on public.angel_faenge;
drop policy if exists "eigene faenge anlegen"  on public.angel_faenge;
drop policy if exists "eigene faenge aendern"  on public.angel_faenge;
drop policy if exists "eigene faenge loeschen" on public.angel_faenge;

create policy "eigene faenge lesen"    on public.angel_faenge
  for select using (auth.uid() = user_id);
create policy "eigene faenge anlegen"  on public.angel_faenge
  for insert with check (auth.uid() = user_id);
create policy "eigene faenge aendern"  on public.angel_faenge
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "eigene faenge loeschen" on public.angel_faenge
  for delete using (auth.uid() = user_id);

-- ---------------------------------------------------------------------
--  3b. Kleine Werte am Konto (Angelzeit, eigene Auswertungen)
--
--  Nicht alles in dieser App ist ein Fang. Die aufsummierte Angelzeit und die
--  selbst gebauten Auswertungen hängen an keiner ID, es gibt sie je Konto genau
--  einmal, und ein "Grabstein" ergibt für sie keinen Sinn. Sie passen deshalb
--  nicht in angel_faenge, sondern in diese sehr kleine zweite Tabelle: eine
--  Zeile je Konto und Schlüssel.
--
--  ⚠️ Warum es sie überhaupt gibt: die Angelzeit lag bis zum 07.08.2026 nur im
--  localStorage des Geräts. Gerettet hat sie einzig das Backup — und das ist am
--  04.08. ausgebaut worden. Damit war die aufsummierte Zeit das Einzige in der
--  ganzen App, das ein Gerätewechsel oder gelöschte Browserdaten wirklich
--  gekostet hätten; alle Fänge kommen über den Sync zurück.
--
--  updated ist wie bei den Fängen die Uhr des Geräts und entscheidet Konflikte:
--  die jüngere Bearbeitung gewinnt. Bewusst NICHT "der größere Wert gewinnt" —
--  das wäre bei einer Zeit naheliegend und würde "Gesamtzeit direkt setzen"
--  unmöglich machen, weil eine Korrektur nach unten nie durchkäme.
-- ---------------------------------------------------------------------
create table if not exists public.angel_werte (
  user_id     uuid   not null default auth.uid()
                     references auth.users(id) on delete cascade,
  schluessel  text   not null,
  updated     bigint not null,
  serverzeit  timestamptz not null default now(),
  wert        jsonb,
  primary key (user_id, schluessel)
);

alter table public.angel_werte enable row level security;

drop policy if exists "eigene werte lesen"    on public.angel_werte;
drop policy if exists "eigene werte anlegen"  on public.angel_werte;
drop policy if exists "eigene werte aendern"  on public.angel_werte;
drop policy if exists "eigene werte loeschen" on public.angel_werte;

create policy "eigene werte lesen"    on public.angel_werte
  for select using (auth.uid() = user_id);
create policy "eigene werte anlegen"  on public.angel_werte
  for insert with check (auth.uid() = user_id);
create policy "eigene werte aendern"  on public.angel_werte
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "eigene werte loeschen" on public.angel_werte
  for delete using (auth.uid() = user_id);

-- ---------------------------------------------------------------------
--  3c. Fehlermeldungen aus der App
--
--  Karls Ansage vom 09.08.2026: „support für bugs". Wer beim Angeln etwas
--  Kaputtes findet, soll es aus der App heraus melden können — nicht über
--  einen Umweg per WhatsApp, der bis zum Abend vergessen ist.
--
--  ⚠️ Warum eine eigene Tabelle und nicht eine E-Mail: eine Meldung am Wasser
--  entsteht typischerweise ohne Empfang. Eine Mail-App aufzurufen heißt, die
--  Angel-App zu verlassen; kommt danach kein Netz, ist der Text weg. Diese
--  Tabelle wird wie die Fänge behandelt — die Meldung liegt erst im Gerät und
--  geht mit dem nächsten Abgleich hinaus.
--
--  ⚠️ Absichtlich KEIN Leserecht für den Melder auf fremde Zeilen und keine
--  Änderung/Löschung: eine abgeschickte Meldung soll nicht nachträglich
--  verschwinden können. Karl liest sie im Supabase-Dashboard (dort gilt RLS
--  nicht), der Melder sieht nur seine eigenen.
--
--  `umfeld` enthält, was eine Meldung erst brauchbar macht: Fassung der App,
--  Gerät, Bildschirm, Netz, Anzahl Fänge, ungesicherte Fänge, letzter Abgleich.
--  Ohne das steht dort „geht nicht" und niemand kann etwas damit anfangen.
--  Was drinsteht, wird dem Melder vor dem Abschicken gezeigt.
-- ---------------------------------------------------------------------
create table if not exists public.angel_meldungen (
  id       text        primary key,
  user_id  uuid        not null default auth.uid()
                       references auth.users(id) on delete cascade,
  erstellt timestamptz not null default now(),
  text     text        not null,
  umfeld   jsonb
);

create index if not exists angel_meldungen_zeit_idx
  on public.angel_meldungen (erstellt desc);

alter table public.angel_meldungen enable row level security;

drop policy if exists "eigene meldungen lesen"   on public.angel_meldungen;
drop policy if exists "eigene meldungen anlegen" on public.angel_meldungen;

create policy "eigene meldungen lesen"   on public.angel_meldungen
  for select using (auth.uid() = user_id);
create policy "eigene meldungen anlegen" on public.angel_meldungen
  for insert with check (auth.uid() = user_id);

-- ---------------------------------------------------------------------
--  3b. Meldungen zustellen statt nachsehen  (10.08.2026)
--
--  Karls Frage: "wie kann ich die reports empfangen?" -- bis hierher gar nicht.
--  Sie lagen in der Tabelle und man musste von sich aus nachschauen. Eine
--  Meldung, von der niemand erfaehrt, ist so gut wie keine.
--
--  Jede neue Zeile geht deshalb als Nachricht an einen Discord-Webhook.
--
--  ⚠️ Die Webhook-Adresse steht NICHT in dieser Datei. Dieses Repo ist
--  oeffentlich; wer die Adresse hat, kann in den Kanal schreiben. Sie liegt in
--  einer eigenen Tabelle, die per API fuer niemanden lesbar ist (RLS an, keine
--  einzige Policy -- damit kommt nur das Dashboard bzw. die service_role dran).
--  Eingetragen wird sie einmal von Hand:
--
--      insert into public.angel_konfig (schluessel, wert)
--      values ('discord_webhook', 'https://discord.com/api/webhooks/...')
--      on conflict (schluessel) do update set wert = excluded.wert;
--
--  Ohne Eintrag passiert schlicht nichts -- die App laeuft unveraendert weiter.
--
--  ⚠️ Der Kanal gehoert den Meldungen allein (#bug-reports-angel-log, ab 10.08.2026).
--  Vorher liefen sie in einen Kanal mit Zugangsdaten -- Meldungen von Testern kaemen
--  dort zwischen Passwoerter zu liegen, und ein Kanal, den man deshalb nicht teilen
--  kann, ist als Posteingang fuer fremde Meldungen unbrauchbar.
--
--  ⚠️ Zum Kopieren dieser Datei: als UTF-8 lesen. Wird sie als Windows-1252 gelesen
--  (PowerShell-Standard), stehen die Umlaute schon beim Einfuegen verdorben in der
--  Funktion -- und die Nachricht gibt danach nur wieder, was hier steht.
--
--  ⚠️ net.http_post() aus pg_net ist ASYNCHRON: es legt die Anfrage in eine
--  Warteschlange und kehrt sofort zurueck. Das ist hier keine Feinheit, sondern
--  der Grund, warum es ueberhaupt in einem Trigger stehen darf. Wuerde der
--  Versand auf Discord warten, haenge das Abschicken einer Meldung an der
--  Erreichbarkeit eines fremden Servers -- und ausgerechnet die Fehlermeldung
--  waere das Erste, was bei Stoerungen nicht mehr durchkommt.
-- ---------------------------------------------------------------------
create extension if not exists pg_net;

create table if not exists public.angel_konfig (
  schluessel text primary key,
  wert       text not null
);
alter table public.angel_konfig enable row level security;
-- Absichtlich keine Policy. Kein Nutzer, auch kein angemeldeter, kommt hier ran.

create or replace function public.angel_meldung_zustellen()
returns trigger
language plpgsql
security definer                      -- der Melder darf angel_konfig nicht lesen
set search_path = public, net, extensions
as $$
declare
  ziel     text;
  txt      text;
  abgleich text;
begin
  select wert into ziel from public.angel_konfig where schluessel = 'discord_webhook';
  if ziel is null or ziel = '' then return new; end if;

  -- Ein Zeitpunkt in ISO-Schreibweise ist zum Lesen nichts. 'nie' bleibt 'nie'.
  abgleich := coalesce(new.umfeld->>'letzterAbgleich', '?');
  if abgleich ~ '^\d{4}-\d{2}-\d{2}' then
    abgleich := to_char(abgleich::timestamptz at time zone 'Europe/Berlin',
                        'DD.MM. HH24:MI');
  end if;

  /* ⚠️ Bewusst OHNE Discord-Auszeichnung (**fett**, > Zitat, `Code`, -# klein).
     Karl am 10.08.2026: "mach doch die komischen zeichen raus". Eine Meldung ist
     kein Aushang -- und jedes Zeichen, das der Empfaenger im Zweifel roh sieht
     statt gerendert, macht sie schlechter lesbar statt besser. Leerzeile statt
     Zitatblock trennt genauso gut und kann nicht schiefgehen. */
  txt := '🐞 Angel-Log — neue Fehlermeldung' || E'\n\n'
      || coalesce(new.text, '') || E'\n\n'
      || 'Fassung ' || coalesce(new.umfeld->>'fassung', '?')
      || ' · ' || coalesce(new.umfeld->>'netz', '?')
      || ' · ' || coalesce(new.umfeld->>'bildschirm', '?')
      || ' · ' || coalesce(new.umfeld->>'faenge', '?') || ' Fänge, '
      || coalesce(new.umfeld->>'ungesichert', '?') || ' ungesichert' || E'\n'
      || 'Letzter Abgleich: ' || abgleich || E'\n'
      || 'Gerät: ' || coalesce(new.umfeld->>'geraet', '?');

  perform net.http_post(
    url     := ziel,
    /* ⚠️ Genau `application/json`, ohne Zeichensatz dahinter. pg_net prueft den Kopf
       selbst und bricht bei allem anderen mit einer Ausnahme ab
       ("Content-Type header must be application/json").

       ⚠️ Und weil diese Ausnahme in einem Trigger geworfen wird, faellt die ganze
       INSERT-Anweisung mit -- die Meldung landet dann nicht einmal in der Tabelle.
       Aus einem Zustellweg, der nicht funktioniert, wird so eine Meldefunktion, die
       nichts mehr annimmt. Am 10.08.2026 genau so passiert.

       ⚠️ Der Umlaut-Salat, gegen den hier kurzzeitig "; charset=utf-8" stand, kam
       nie von hier. Er kam daher, dass der SQL-Text auf dem Weg in die Zwischenablage
       als Windows-1252 statt UTF-8 gelesen wurde -- er stand also schon verdorben im
       Quelltext dieser Funktion, und die Nachricht gab nur wieder, was hier stand.
       Wer diese Datei kopiert, kopiert sie als UTF-8. Sonst wandert derselbe Salat
       beim naechsten Mal wieder herein, und man sucht ihn wieder an der falschen
       Stelle. */
    headers := '{"Content-Type": "application/json"}'::jsonb,
    -- Discord nimmt hoechstens 2000 Zeichen. Lieber gekuerzt ankommen als
    -- vollstaendig abgewiesen werden.
    body    := jsonb_build_object('content', left(txt, 1900))
  );
  return new;
end $$;

drop trigger if exists angel_meldungen_zustellen on public.angel_meldungen;
create trigger angel_meldungen_zustellen
  after insert on public.angel_meldungen
  for each row execute function public.angel_meldung_zustellen();

-- ---------------------------------------------------------------------
--  4. Konto löschen
--
--  Muss es geben, sobald fremde Daten im Spiel sind: Art. 17 DSGVO gibt
--  jedem das Recht, seine Daten löschen zu lassen — und zwar selbst, nicht
--  per Bitte an den Betreiber.
--
--  security definer, weil ein normaler Nutzer nicht in auth.users schreiben
--  darf. Deshalb ist die Funktion eng gehalten: sie nimmt kein Argument und
--  löscht ausschließlich auth.uid(). Es gibt keinen Weg, ihr ein fremdes
--  Konto unterzuschieben. Das search_path-Setzen gehört dazu — ohne das
--  ließe sich einer security-definer-Funktion eine untergeschobene Tabelle
--  in den Weg legen.
--
--  Die Fänge verschwinden über das "on delete cascade" der user_id mit.
-- ---------------------------------------------------------------------
create or replace function public.konto_loeschen()
returns void
language plpgsql
security definer
set search_path = public, auth
as $$
declare wer uuid := auth.uid();
begin
  if wer is null then
    raise exception 'Nicht angemeldet';
  end if;
  delete from auth.users where id = wer;
end $$;

revoke all on function public.konto_loeschen() from public, anon;
grant execute on function public.konto_loeschen() to authenticated;

-- ---------------------------------------------------------------------
--  5. Benutzernamen
--
--  Supabase kennt beim Anmelden nur E-Mail + Passwort. Ein Benutzername
--  braucht deshalb eine eigene Tabelle und einen Umweg: beim Anmelden wird
--  aus dem Namen erst die zugehoerige E-Mail geholt, damit angemeldet wird.
--
--  Gespeichert wird klein geschrieben und ohne Leerzeichen aussenrum, damit
--  "Karl" und "karl" nicht zwei verschiedene Leute sind.
-- ---------------------------------------------------------------------
create table if not exists public.profil (
  id       uuid primary key references auth.users(id) on delete cascade,
  username text unique not null
);

alter table public.profil enable row level security;
drop policy if exists "eigenes profil lesen" on public.profil;
create policy "eigenes profil lesen" on public.profil
  for select using (auth.uid() = id);

-- Beim Registrieren legt die App den Namen als Zusatzangabe mit; dieser
-- Ausloeser holt ihn dort heraus und schreibt die Zeile.
-- Ohne Namen wird nichts geschrieben — dann geht die Anmeldung eben nur
-- ueber die E-Mail, statt dass die ganze Registrierung scheitert.
create or replace function public.angel_profil_anlegen()
returns trigger
language plpgsql
security definer
set search_path = public, auth
as $$
declare name text := lower(trim(new.raw_user_meta_data->>'username'));
begin
  if name is not null and name <> '' then
    insert into public.profil (id, username) values (new.id, name);
  end if;
  return new;
end $$;

drop trigger if exists angel_profil_anlegen on auth.users;
create trigger angel_profil_anlegen
  after insert on auth.users
  for each row execute function public.angel_profil_anlegen();

-- Ist der Name noch frei? Wird vor dem Registrieren gefragt.
create or replace function public.username_frei(uname text)
returns boolean
language sql
security definer
set search_path = public
as $$
  select not exists (
    select 1 from public.profil where username = lower(trim(uname))
  );
$$;

-- Welche E-Mail gehoert zu diesem Namen? Wird beim Anmelden gebraucht.
--
-- ⚠️ Das ist bewusst oeffentlich aufrufbar und muss es auch sein — gefragt
--    wird, BEVOR jemand angemeldet ist. Die Folge: wer einen Benutzernamen
--    kennt oder errraet, erfaehrt die zugehoerige E-Mail-Adresse. Das ist der
--    Preis fuer "Anmelden mit Benutzername" und bei Supabase der uebliche Weg
--    (Gym-Log macht es genauso). Fuer eine App mit einer Handvoll bekannter
--    Leute vertretbar; wuerde sie oeffentlich beworben, gehoerte das neu
--    bewertet — dann lieber nur E-Mail-Anmeldung.
create or replace function public.email_fuer_username(uname text)
returns text
language sql
security definer
set search_path = public, auth
as $$
  select u.email
    from auth.users u
    join public.profil p on p.id = u.id
   where p.username = lower(trim(uname));
$$;

revoke all on function public.username_frei(text)        from public;
revoke all on function public.email_fuer_username(text)  from public;
grant execute on function public.username_frei(text)       to anon, authenticated;
grant execute on function public.email_fuer_username(text) to anon, authenticated;

-- ---------------------------------------------------------------------
--  6. Noch von Hand im Dashboard (nicht per SQL):
--
--  Authentication → Sign In / Providers → Email:
--    "Confirm email" ausschalten.
--    Sonst kommt man nach dem Registrieren nicht sofort hinein, sondern
--    muss erst eine Mail bestätigen — am Wasser mit halbem Empfang ist das
--    die Stelle, an der jemand aufgibt. (Bei Gym-Log genauso gelöst.)
-- ---------------------------------------------------------------------
