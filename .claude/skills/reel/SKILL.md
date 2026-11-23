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
- **Szenenwechsel dezent:** Ramiz fand starke Übergänge störend. Standard in `buehne.html` ist leise (Wischer 0,3, Unschärfe 3 px,
  Versatz 18 px). Stärker nur auf Wunsch über `"uebergang": {"wisch": …, "unschaerfe": …, "versatz": …}` im Drehbuch.
- **Figuren:** Strichmännchen ja, aber nur die Gelenk-Figuren aus `reels/figur.py`: Ellbogen und Knie, weiche Übergänge, Hände greifen
  wirklich (Griffziele). Die alten Wackel-Figuren in `reels/figuren.py` sahen unprofessionell aus. Monteure beige mit Kappe, Kunde hell,
  Arbeiter beim Hersteller grau. Jede Szene zeigt eine echte Tätigkeit (messen, tragen, einsetzen, bohren, unterschreiben …).
- **Stimme:** ruhig, erklärend, fachlich, Hochdeutsch ohne Akzent, nicht gehetzt. Standard: ElevenLabs, Stimme `5KvpaGteYkNayiswuX2h`,
  Eleven Multilingual v2. Keine Musik oder nur ganz leise. Nie schneller abspielen, um Zeit zu sparen.
- **Aussprache (von Ramiz festgelegt):** KIMUTEC wird „Kimu-Tek“ gesprochen (`aussprache` im Drehbuch, gilt auch für „kimutec.com“ →
  „Kimu-Tek Punkt com“). Das Wort „Montage“ spricht die Stimme falsch: im Sprechertext „Einbau“ oder „Einbau der Elemente“ sagen,
  auf dem Bild darf „Montage“ stehen. Allgemein: Spricht die Stimme ein Wort falsch, erst umschreiben (Lautschrift in `aussprache`),
  und wenn das nicht reicht, ein anderes Wort wählen. Bei Zweifeln vorher eine kurze Probe mit 2–3 Varianten erzeugen und Ramiz wählen lassen.
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
4. **Stimme holen** (Abschnitt „Stimme von ElevenLabs“ in `reels/README.md`). Jede Erzeugung kostet Guthaben: nie wiederholen,
   um es „nochmal zu versuchen“, und vorher den Text freigeben lassen.
   - **Weg A, bewährt (ElevenLabs-Connector):** Den ganzen Sprechertext als *eine* Ansage erzeugen (`creative_generate_speech`,
     Stimme und Modell wie oben, Absätze = Szenen, Aussprache schon eingesetzt, ohne `|`). Ein Durchgang klingt gleichmäßiger als
     12 Einzelteile. Die Audio-Links sperrt der Cloud-Proxy: Ramiz lädt die gewählte Variante herunter und schickt die MP3 in den Chat.
     Dann `python3 reels/elevenlabs.py zerlegen <mp3> <drehbuch>`: Spracherkennung (Parakeet) richtet jedes Wort am Text aus und
     schreibt `ton/sNN.json` mit Zeitmarken. Die Ausgabe zeigt je Szene die Trefferzahl; unter ca. 90 % den Text vergleichen.
   - **Nur einzelne Szenen ändern:** nur diese Absätze als eine Ansage erzeugen und `… zerlegen <mp3> <drehbuch> --szenen=1,5,8,12`.
     Die übrigen Szenen in `ton/` bleiben unverändert.
   - **Weg B (PC von Ramiz, mit Zeitstempeln direkt von ElevenLabs):** `python3 reels/elevenlabs.py skript <drehbuch> <ordner>` →
     Dateien per device_commit_files in den verbundenen PC-Ordner legen, Ramiz startet „Stimme holen.cmd“, danach `ton` mit
     device_stage_files holen und `python3 reels/elevenlabs.py pruefen <drehbuch>`. Der Schlüssel liegt als `elevenlabs.txt` in seinem
     Ordner und kommt nie in den Chat.
5. **Länge prüfen:** `node reels/render.mjs <drehbuch> --schnell` zeigt die Gesamtzeit. Über 180 s: erst `pause` je Szene und
   `sprechStart` kürzen (nicht unter ca. 0,5 s Pause zwischen Szenen), dann Text kürzen. Die Stimme nie beschleunigen.
6. **Rendern** mit `setsid nohup node reels/render.mjs <drehbuch> > log 2>&1 &`, sonst bricht die App lange Läufe ab
   (ein 3-Minuten-Reel braucht in der Cloud etwa 11–20 Minuten). Danach Einzelbilder mitten in Animationen ansehen und den Ton mit
   `python3 reels/pruefe-ton.py reel.mp4` Szene für Szene gegen den Sprechertext lesen – besonders das letzte Wort jeder Szene
   (abgeschnittene Satzenden fallen sonst erst Ramiz auf). Die Spracherkennung schreibt „Kimu-Tek“ als „ChemoTech“ – das ist normal.
   Falsch gesprochene Wörter über `aussprache` umschreiben und die Szene neu holen.
7. **Abliefern:** `reel.mp4` und `vorschau.jpg` mit SendUserFile schicken, Instagram-Text dazu, und in einem Satz sagen, was geprüft
   ist und was offen bleibt. Generator, Drehbuch und Sprechertext committen und pushen. Videos, Ton und Vorschauen schließt `.gitignore` aus.

## Figuren richtig einsetzen (Kurzfassung, Details in reels/README.md)
- `figur(typ, boden, [k(-9, x=…, b=1), k('m2', pose='messen', zV=[x, y], pV='laser'), …], s=1)` – erster Key immer bei `t=-9`.
- Ein Key läuft von `t` bis `t + d`. Laufen: `k('m1-2.1', x=…, gehen=True, d=2.1)` kommt genau bei Marke 1 an.
  Blickrichtung und Laufrichtung dürfen verschieden sein (rückwärts gehen, etwa beim Tragen zu zweit).
- Kommt die erste Tätigkeit erst spät im Satz (z. B. nach „Schritt sieben: der Einbau der Elemente.“), die Figuren zu Szenenbeginn
  hereinlaufen lassen (`k(-9, x=-130)` links bzw. `x=1050` rechts, dann `k(0.15, x=…, gehen=True, d=2.4)`), statt sie stehen zu lassen.
- Greifen: `zV=an('fenster-id', x, y)` hängt die Hand an ein Element mit `spur(…)`; so tragen zwei Monteure ein Fenster mit.
- Reichweite: Schulter ≈ `boden − 225·s`, Arm ≈ `108·s` px. Fensterhöhen realistisch wählen (Brüstung etwa 140 px, Fenster etwa 190–250 px
  bei `s=1`), sonst greifen die Hände ins Leere.
- Spuren blenden zwischen zwei Keys immer weich über. Für „stehen bis m3, dann bewegen“ einen Halte-Key bei `m3` setzen.

Fertiges Video ohne Ton vertonen: Abschnitt „Fertiges Video vertonen“ in `reels/README.md` (`reels/vertonen.mjs`).
Sprechertext dort nur aus dem ableiten, was im Video steht.
