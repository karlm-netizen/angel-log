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
--    serverzeit = Uhr des Servers. Steuert, was ein Gerät nachladen muss.
--  Getrennt, weil ein Handy mit falsch gestellter Uhr sonst entweder alles
--  doppelt zieht oder nie wieder etwas zu sehen bekommt.
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

-- Das Nachladen fragt immer "was ist seit X passiert, für mich?".
create index if not exists angel_faenge_sync_idx
  on public.angel_faenge (user_id, serverzeit);

-- ---------------------------------------------------------------------
--  2. serverzeit bei jeder Änderung neu setzen
--
--  Ohne diesen Trigger bleibt serverzeit auf dem Wert vom Anlegen stehen.
--  Eine Änderung wäre dann für das zweite Gerät unsichtbar: es fragt nach
--  allem, was neuer als sein letzter Stand ist — und bekäme nichts.
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
