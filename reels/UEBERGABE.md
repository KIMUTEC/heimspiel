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

## Stand
- Reel 9 Version 2 ist fertig gerendert (2:57 min) mit dem ElevenLabs-Take „content_2.mp3“ (Flow `7PpyR7Fh4dWC6YQZNVoa`, 4 Takes,
  zusammen 8.676 Zeichen verbraucht). Der Take wurde mit `elevenlabs.py zerlegen` in Szenen geschnitten (330 von 336 Wörtern zugeordnet).
- Pausen zwischen den Szenen wurden gekürzt (`sprechStart` 0,2 s), damit das Reel unter 3:00 bleibt.
- Tonprüfung: Text stimmt; „Kimutek“ hört die Spracherkennung als „Chemotec“ (macht sie bei jeder Stimme), „Montage“ in Szene 5 weich wie „Garage“.
- Download von elevenlabsusercontent.com ist in der Cloud gesperrt – Ramiz schickt Takes als MP3 oder gibt die Domain frei.

## Weitere Reels im Repo
- `06-aufmass-montage` – Nachbau von Reel 6 (Aufmaß und Montage).
- `08-fensterglas` – Fensterglas im KIMUTEC-Stil.
- `07-fensterglas` – nur Vertonung des hellen Canva-Videos (veraltet).
