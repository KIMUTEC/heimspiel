# Übergabe: KIMUTEC-Reels (Stand 22.11.2026, abends)

Repo `kimutec/heimspiel`, Branch `claude/funny-pascal-o9fjc2`, Ordner `reels/`. Skill `/reel` enthält alle Regeln und den Ablauf –
damit braucht ein neuer Chat keinen langen Übergabetext mehr: „/reel – mach Reel 9 fertig“ reicht.

## Aktuelles Video: Reel 9 „So arbeiten wir“ – Version 2
- Projekt `reels/projekte/09-ablauf/`: Generator `bauen.py` → `drehbuch.json`. Freigegebener Sprechertext: `sprechertext.txt`.
- 12 Szenen, erklärend und fachlich (ca. 2:50 min): Einstieg (Weg mit 8 Stationen, Handschlag), Kontakt, Beratung, Aufmaß
  (Laser an drei Stellen, Höhe, kleinstes Maß, Fuge), Angebot (Positionen, Freigabe, Hersteller), Produktion (Rahmen, Glas, Beschläge),
  Lieferung (Lkw, zwei Monteure tragen), Montage (alt raus, neu rein, Wasserwaage/Lot, bohren), Abdichtung in drei Ebenen (Schnitt),
  Abnahme (öffnen/kippen/schließen, Protokoll, Handschlag), Ergebnis (5,0 – echt, laut Ramiz), Abschluss.
- Neue Strichmännchen mit Gelenken: `reels/figur.py` + `reels/engine/bewegung.js` (siehe README „Figuren und Spuren“).
- „KW 12“ wurde durch „Liefertermin ✓“ ersetzt (keine konkrete Woche versprechen).

## Stimme
- ElevenLabs, Stimme `5KvpaGteYkNayiswuX2h`, Eleven Multilingual v2, Stability 0,6 / Similarity 0,75 / Style 0 / Speed 1,0.
- Die Cloud erreicht ElevenLabs nicht (Proxy 403 – das war auch die Ursache für „Schlüssel ungültig“). Weg über den PC (Windows) von Ramiz:
  `reels/elevenlabs.py skript` → „Stimme holen.cmd“ in den verbundenen Ordner, `elevenlabs.txt` mit Schlüssel daneben, Doppelklick,
  Ordner `ton` zurückholen. Der ElevenLabs-Connector ist mit seinem Konto verbunden, seine Werkzeuge waren im Chat aber noch nicht geladen.
- Für Werbung braucht ElevenLabs ein bezahltes Abo (kommerzielle Lizenz).

## Offen
- Ansagen von ElevenLabs holen, dann `node reels/render.mjs reels/projekte/09-ablauf/drehbuch.json` (mit `setsid nohup`).
- Danach Ton mit `pruefe-ton.py` gegenlesen, Länge ≤ 3:00 prüfen (sonst Pausen kürzen), `instagram.txt` an Version 2 anpassen.

## Weitere Reels im Repo
- `06-aufmass-montage` – Nachbau von Reel 6 (Aufmaß und Montage).
- `08-fensterglas` – Fensterglas im KIMUTEC-Stil.
- `07-fensterglas` – nur Vertonung des hellen Canva-Videos (veraltet).
