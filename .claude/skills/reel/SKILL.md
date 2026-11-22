---
name: reel
description: Erstellt, verbessert oder vertont animierte KIMUTEC-Erklär-Reels für Instagram (1080×1920, Sprecher, Strichmännchen mit Gelenken) zu Fenstern, Türen, Toren, Sonnenschutz und zum Ablauf bei KIMUTEC. Immer nutzen, wenn Ramiz ein Reel, Video, Erklärvideo oder einen Instagram-Clip will, ein Reel „besser machen“, neu vertonen oder mit ElevenLabs-Stimme haben möchte, ein Video zum Nachbauen schickt oder „wie Reel 6/9“ sagt – auch wenn das Wort „Reel“ nicht fällt.
---

# KIMUTEC-Reels

Alles liegt in `reels/`. Anleitung mit allen Bausteinen: `reels/README.md`. Beste Vorlage: `reels/projekte/09-ablauf/bauen.py`
(Python-Generator → `drehbuch.json`, Strichmännchen mit echten Tätigkeiten, ElevenLabs-Stimme). Stand und offene Punkte: `reels/UEBERGABE.md`.

## Was Ramiz will (immer einhalten)
- **Stil:** dunkler KIMUTEC-Stil wie Reel 6/9: Montserrat, beige Akzente `#D8B79C`, Karten mit Verlauf und Schatten, Lichtwischer.
  Nur das echte Logo `reels/marke/kimutec-logo.png`, nie das KIMU-Badge.
- **Figuren:** Strichmännchen ja, aber nur die Gelenk-Figuren aus `reels/figur.py`: Ellbogen und Knie, weiche Übergänge, Hände greifen
  wirklich (Griffziele). Die alten Wackel-Figuren in `reels/figuren.py` sahen unprofessionell aus. Monteure beige mit Kappe, Kunde hell,
  Arbeiter beim Hersteller grau. Jede Szene zeigt eine echte Tätigkeit (messen, tragen, einsetzen, bohren, unterschreiben …).
- **Stimme:** ruhig, erklärend, fachlich, Hochdeutsch ohne Akzent, nicht gehetzt, richtige Aussprache (`aussprache` im Drehbuch,
  z. B. KIMUTEC → „Kimutek“). Standard: ElevenLabs, Stimme `5KvpaGteYkNayiswuX2h`, Eleven Multilingual v2. Keine Musik oder nur ganz leise.
- **Synchron:** Schrift und Bild erscheinen genau beim passenden Wort: `|` im Sprechertext, `data-t="mN"` an Elementen, `"mN"` in Figuren-Keys.
- **Länge:** höchstens 3 Minuten (Instagram-Grenze). `render.mjs` warnt darüber.
- **Inhalt:** fachlich korrekt, nichts erfinden. Fachliches mit Quelle prüfen (z. B. RAL-Montage: innen dichter als außen).
  Firmenangaben nur, wenn Ramiz sie bestätigt hat: Die „5,0 Kundenbewertung“ ist echt. Konkrete Liefer-KW oder Preise vorher nachfragen.
- **Instagram-Text:** starke erste Zeile, 2–4 kurze Sätze, Sie-Form, 5–8 passende Hashtags, keine Telefonnummer, keine Adresse.
- Bei großen Aufgaben offene Punkte zuerst kurz klären. Den Sprechertext freigeben lassen, bevor die Stimme erzeugt wird,
  denn jede Ansage kostet ElevenLabs-Guthaben.

## Ablauf
1. `bash reels/einrichten.sh`. Die Cloud erreicht nur Paketquellen und GitHub: ElevenLabs, Microsoft-Stimme und Hugging Face sind gesperrt.
2. **Sprechertext** pro Szene schreiben (Sie-Form, erklärend, 1–3 Sätze, `|` vor Wörtern, an die etwas gekoppelt wird) und freigeben lassen.
   Ablegen in `sprechertext.txt`. Etwa 330 Wörter ergeben mit Pausen knapp 3 Minuten.
3. **Szenen bauen** (Generator nach Vorlage) und ohne Stimme prüfen, bevor die Stimme da ist:
   `node reels/render.mjs <drehbuch> --schaetzen --szene=N` → `vorschau-szeneN.jpg` (alle 0,5 s, mit Zeitstempel),
   `--bild=Sekunden,…` für Details in voller Größe. Achten auf: nichts überlappt oder ist abgeschnitten, Hände erreichen ihre Ziele,
   keine Phase über 2 s ohne Bewegung, Inhalt bleibt über dem unteren Instagram-Bereich (Bild endet spätestens bei ca. y = 1450).
4. **Stimme holen** (ElevenLabs mit Zeitpunkt jedes Zeichens, Abschnitt „Stimme von ElevenLabs“ in `reels/README.md`):
   Ist ein ElevenLabs-Connector mit Werkzeugen in der Sitzung geladen, zuerst den versuchen. Sonst über den PC von Ramiz:
   `python3 reels/elevenlabs.py skript <drehbuch> <ordner>` → Dateien per SendUserFile + device_commit_files in den verbundenen
   PC-Ordner legen. Ramiz startet „Stimme holen.cmd“. Danach den Ordner `ton` mit device_stage_files holen und
   `python3 reels/elevenlabs.py pruefen <drehbuch>` ausführen. Ist kein Ordner verbunden: Ramiz bitten, in der Desktop-App über
   „+“ → „Ordner hinzufügen“ einen Ordner zu verbinden und `elevenlabs.txt` mit dem Schlüssel hineinzulegen (Schlüssel nie in den Chat).
5. **Rendern** mit `setsid nohup node reels/render.mjs <drehbuch> > log 2>&1 &`, sonst bricht die App lange Läufe ab
   (ein 3-Minuten-Reel braucht in der Cloud etwa 15–20 Minuten). Danach Einzelbilder mitten in Animationen ansehen und den Ton mit
   `python3 reels/pruefe-ton.py reel.mp4` gegenlesen. Falsch gesprochene Wörter über `aussprache` umschreiben und die Szene neu holen.
6. **Abliefern:** `reel.mp4` und `vorschau.jpg` mit SendUserFile schicken, Instagram-Text dazu. Generator, Drehbuch und Sprechertext
   committen und pushen. Videos, Ton und Vorschauen schließt `.gitignore` aus.

## Figuren richtig einsetzen (Kurzfassung, Details in reels/README.md)
- `figur(typ, boden, [k(-9, x=…, b=1), k('m2', pose='messen', zV=[x, y], pV='laser'), …], s=1)` – erster Key immer bei `t=-9`.
- Laufen: `k('m1-1.5', x=…, gehen=True, d=2.1)` kommt genau bei Marke 1 an. Blickrichtung und Laufrichtung dürfen verschieden sein
  (rückwärts gehen, etwa beim Tragen zu zweit).
- Greifen: `zV=an('fenster-id', x, y)` hängt die Hand an ein Element mit `spur(…)`; so tragen zwei Monteure ein Fenster mit.
- Reichweite: Schulter ≈ `boden − 225·s`, Arm ≈ `108·s` px. Fensterhöhen realistisch wählen (Brüstung etwa 140 px, Fenster etwa 190–250 px
  bei `s=1`), sonst greifen die Hände ins Leere.
- Spuren blenden zwischen zwei Keys immer weich über. Für „stehen bis m3, dann bewegen“ einen Halte-Key bei `m3` setzen.

Fertiges Video ohne Ton vertonen: Abschnitt „Fertiges Video vertonen“ in `reels/README.md` (`reels/vertonen.mjs`).
Sprechertext dort nur aus dem ableiten, was im Video steht.
