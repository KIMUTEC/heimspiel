# Übergabe: KIMUTEC-Reels (Stand 22.11.2026)

Repo `kimutec/heimspiel`, Branch `claude/funny-pascal-o9fjc2`, Ordner `reels/`.
Ich (Ramiz, KIMUTEC Fenstertechnik, Pforzheim) lasse hier animierte Instagram-Reels erstellen.

## Aktuelles Video: Reel 9 „So arbeiten wir – vom Kontakt bis zur Abnahme“
- Projekt: `reels/projekte/09-ablauf/` – Generator `bauen.py` erzeugt `drehbuch.json`.
- Länge 2:10 min, 1080×1920, 30 fps. 11 Szenen: Einstieg (Weg mit 8 Stationen, Lichtpunkt), Kontakt (Handy, Chat-Blasen),
  Beratung (Haus, „KOSTENLOS“, Wärme/Sicherheit/Design/Budget), Aufmaß (Laser, Maße zählen hoch, „Kleinstes zählt“),
  Angebot (Dokument, Stempel „FREIGEGEBEN“, Pfeil zum Hersteller), Produktion (Zahnräder, Fließband, „KW 12“),
  Lieferung (KIMUTEC-Lkw fährt vors Haus), Montage (altes Fenster raus, neues rein, leuchtende Dichtung),
  Abnahme (Häkchen, Unterschrift), Ergebnis (Karte „5,0 Kundenbewertung“, Sterne, Konfetti, Zitat), Abschluss (Logo, Kontakt).
- Oben rechts Schritt-Anzeige „SCHRITT x / 8“.
- Instagram-Text: `reels/projekte/09-ablauf/instagram.txt`, Sprechertext mit Zeiten: `sprechertext.txt`.
- Noch offen/zu prüfen: „5,0“ und „KW 12“ sind Beispielwerte.

## So wird gerendert
1. `bash reels/einrichten.sh` (installiert edge-tts, Piper, faster-whisper)
2. `python3 reels/projekte/09-ablauf/bauen.py && node reels/render.mjs reels/projekte/09-ablauf/drehbuch.json`
   (`--schnell` = nur Vorschaubild `vorschau.jpg`). Ergebnis: `reel.mp4`, `untertitel.srt`.
3. Lange Läufe mit `setsid nohup … &` starten, sonst bricht die App sie ab.
4. Prüfen: Einzelbilder mitten in Animationen ansehen, Ton mit faster-whisper „medium“ abhören.
Anleitung und alle Bausteine/Effekte: `reels/README.md`. Skill: `/reel`.

## Meine Wünsche (bitte immer beachten)
- **Stil:** Original-KIMUTEC-Stil wie Reel 6: dunkler Hintergrund, Montserrat, beige Akzente (#D8B79C), echtes Logo `reels/marke/kimutec-logo.png`.
- **Stimme:** ruhig, erklärend, Hochdeutsch, akzent- und dialektfrei. Aktuell `edge:de-DE-FlorianMultilingualNeural`, Tempo `-8%`.
  Nicht Chatterbox (Akzent), nicht Piper (zu künstlich). Besser wäre ElevenLabs – der gespeicherte API-Schlüssel wurde
  aber als ungültig abgelehnt; ich gebe bei Bedarf einen neuen (beginnt mit `sk_`).
- **Synchron:** Schrift und Bild erscheinen genau beim passenden Wort (Marken `|` im Sprechertext, `data-t="m1"` …).
- **Animation:** professionell und flüssig (Titel Wort für Wort, Lichtwischer, leuchtende Linien, Karten mit Verlauf/Schatten,
  Konfetti). Keine Strichmännchen/Figuren – die sahen nicht professionell aus.
- **Länge:** höchstens 3 Minuten (Instagram-Grenze).
- **Inhalt:** fachlich korrekt, nichts erfinden; Unklares nachfragen.
- **Instagram-Texte:** starke erste Zeile, 2–4 kurze Sätze, Sie-Form, 5–8 passende Hashtags, keine Telefonnummer/Adresse.

## Weitere Reels im Repo
- `06-aufmass-montage` – Nachbau meines Reels 6 (Aufmaß und Montage).
- `08-fensterglas` – Fensterglas im KIMUTEC-Stil (Isolierglas, Werte, ESG, VSG, Sonnenschutz, Checkliste).
- `07-fensterglas` – nur Vertonung meines hellen Canva-Videos (veraltet).
