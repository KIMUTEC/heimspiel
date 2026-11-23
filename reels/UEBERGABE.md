# Übergabe: KIMUTEC-Reels (Stand 23.11.2026)

Repo `kimutec/heimspiel`, Branch `claude/funny-pascal-o9fjc2`, Ordner `reels/`. Skill `/reel` enthält alle Regeln und den Ablauf –
damit braucht ein neuer Chat keinen langen Übergabetext mehr: „/reel – mach Reel 9 fertig“ reicht.

## Aktuelles Video: Reel 9 „So arbeiten wir“ – Version 3
- Projekt `reels/projekte/09-ablauf/`: Generator `bauen.py` → `drehbuch.json`. Freigegebener Sprechertext: `sprechertext.txt`.
- 12 Szenen, erklärend und fachlich (ca. 2:50 min): Einstieg (Weg mit 8 Stationen, Handschlag), Kontakt, Beratung, Aufmaß
  (Laser an drei Stellen, Höhe, kleinstes Maß, Fuge), Angebot (Positionen, Freigabe, Hersteller), Produktion (Rahmen, Glas, Beschläge),
  Lieferung (Lkw, zwei Monteure tragen), Montage (alt raus, neu rein, Wasserwaage/Lot, bohren), Abdichtung in drei Ebenen (Schnitt),
  Abnahme (öffnen/kippen/schließen, Protokoll, Handschlag), Ergebnis (5,0 – echt, laut Ramiz), Abschluss.
- Neue Strichmännchen mit Gelenken: `reels/figur.py` + `reels/engine/bewegung.js` (siehe README „Figuren und Spuren“).
- „KW 12“ wurde durch „Liefertermin ✓“ ersetzt (keine konkrete Woche versprechen).

## Stimme
- ElevenLabs, Stimme `5KvpaGteYkNayiswuX2h`, Eleven Multilingual v2, Stability 0,6 / Similarity 0,75 / Style 0 / Speed 1,0.
- Aussprache (von Ramiz gewählt): KIMUTEC = „Kimu-Tek“. „Montage“ wird nicht mehr gesprochen (klang falsch) – im Text steht
  „Einbau“ bzw. „der Einbau der Elemente“. Auf dem Bild bleibt „Montage“.
- Bewährter Weg: ElevenLabs-Connector im Chat erzeugt die Ansage (Flow `7PpyR7Fh4dWC6YQZNVoa`), Ramiz lädt die MP3 herunter und schickt sie,
  `elevenlabs.py zerlegen` schneidet sie in Szenen. Die Cloud erreicht ElevenLabs selbst nicht (Proxy 403), auch keine Audio-Links.
  Alternativ über den PC (Windows) von Ramiz: `reels/elevenlabs.py skript` → „Stimme holen.cmd“ (siehe README).
- Für Werbung braucht ElevenLabs ein bezahltes Abo (kommerzielle Lizenz, ab Starter).

## Stand
- Version 3 (23.11.): Szenen 1, 5, 8 und 12 neu vertont (Take „content_3.mp3“, mit `zerlegen --szenen=1,5,8,12` eingesetzt),
  übrige Szenen aus „content_2.mp3“. Szenenwechsel dezenter (Wischer 0,3, Unschärfe 3 px, Versatz 18 px).
  Szene 8: Monteure laufen jetzt zu Beginn herein, statt 4 s zu stehen. Abschluss-Szene blendet Logo, Titel und Kontakt wortgenau ein.
- Länge 2:58 (178,4 s): Pausen je Szene gekürzt, `sprechStart` 0,1 s – die Stimme selbst ist nicht beschleunigt.
- `zerlegen` schnitt früher bei der ersten Sprechpause nach dem letzten erkannten Wort ab – dadurch fehlte „Punkt com“ am Ende.
  Jetzt endet jede Szene beim letzten hörbaren Laut vor der nächsten Szene. Nach `zerlegen` immer `pruefe-ton.py` auf das fertige Reel laufen lassen.

## Weitere Reels im Repo
- `06-aufmass-montage` – Nachbau von Reel 6 (Aufmaß und Montage).
- `08-fensterglas` – Fensterglas im KIMUTEC-Stil.
- `07-fensterglas` – nur Vertonung des hellen Canva-Videos (veraltet).
