# KIMUTEC-Reels

Animierte Erklär-Reels (1080×1920, 30 fps, mit Sprecher) im KIMUTEC-Stil: dunkler Hintergrund,
Montserrat, beige Akzente, Linien-Zeichnungen, die passend zum Sprecher erscheinen.

## So entsteht ein Reel
1. Einmal einrichten: `bash reels/einrichten.sh`
2. Ordner `reels/projekte/<nr>-<thema>/` mit einer `drehbuch.json` anlegen (Vorlage: `projekte/06-aufmass-montage`).
3. Rendern: `node reels/render.mjs reels/projekte/<nr>-<thema>/drehbuch.json` (lange Läufe mit `setsid nohup … &`)
   - `--schnell` erzeugt nur `vorschau.jpg` und den Ton.
   - `--schaetzen` rechnet ohne Stimme mit geschätzten Sprechzeiten (stille Vorschau zum Bauen).
   - `--szene=N` erzeugt nur einen Kontaktbogen der Szene N (`vorschau-szeneN.jpg`, alle `--raster=0.5` s, mit Zeitstempel);
     `--szene=N --video` ein kurzes Video nur dieser Szene; `--bild=12.5,30` Einzelbilder in voller Größe.
4. Prüfen: `vorschau.jpg` ansehen, `python3 reels/pruefe-ton.py …/reel.mp4` liest den Sprecher mit
   (faster-whisper, sonst Parakeet über sherpa-onnx – das Modell kommt von GitHub).

Ergebnis im Projektordner: `reel.mp4`, `vorschau.jpg`, `untertitel.srt` (für Instagram-Untertitel), `sprecher.wav`.
Videos und Ton werden nicht ins Repo eingecheckt.

## Drehbuch
```json
{
  "stimme": "de_DE-thorsten-high", "tempo": 1.0,
  "aussprache": { "KIMUTEC": "Kimu-Tek" },
  "tonspur": "eigene-aufnahme.mp3",
  "szenen": [ { "label": "…", "titel": "Zeile 1\nZeile 2", "sprecher": "…", "bild": "<svg-Inhalt>", "text": […] } ]
}
```
- `tonspur` (optional): eigene Sprachaufnahme statt Computerstimme. Dann braucht jede Szene `dauer` in Sekunden.
- Szene: `label`, `titel` (`\n` = neue Zeile), `sprecher`, optional `bild` + `bildHoehe` (Standard 560), `text`, `pause`, `dauer`.
- `text`: Liste aus Strings oder `{ "s": "…", "punkt": true, "klein": true, "t": "40%" }`.
- Abschluss-Szene: `"art": "abschluss"` mit `unter`, `kontakt.zeilen` und `motto`.

### Zeichnungen (`bild`)
SVG-Inhalt mit Breite 920. Attribute in einfachen Anführungszeichen schreiben.
- Zeitsteuerung: `data-t` = Einblenden (Sekunden ab Szenenstart oder `"60%"` der Sprechzeit), `data-aus` = Ausblenden,
  `data-d` = Dauer, `data-bewegung="dx,dy,start,dauer"` = verschieben (nur an Elementen ohne `transform`).
- Klasse `zeichnen` = Linie wird gezeichnet statt eingeblendet.
- Bausteine: `wand` (Schraffur), `daemmung`, `offen` (Öffnung), `rahmen`, `glas`, `linie`, `duenn`, `akzent`,
  `akzent-linie`, `mass` (Maßlinie, mit `marker-start/end='url(#pfeil)'`), Schrift: `schrift`, `schrift-klein`,
  `schrift-akzent`, `schrift-text`, `schrift-gross`, `schrift-punkt`.

Vorschau im Browser ohne Ton: `engine/buehne.html?drehbuch=../projekte/<name>/drehbuch.json` über einen lokalen Server öffnen.

Das Logo in `engine/buehne.html` ist nachgezeichnet. Für das Original-Logo die SVG-Datei dort einsetzen.

## Fertiges Video vertonen
Für Videos, die schon fertig animiert sind (z. B. aus Canva), aber noch keinen Ton haben:
1. Abschnittswechsel finden (Kontaktbogen mit ffmpeg, Titelbereich vergleichen) und pro Abschnitt einen Sprechertext schreiben.
2. `vertonung.json` anlegen (Vorlage: `projekte/07-fensterglas/vertonung.json`): `teile` mit `start` (Sekunde) und `text`, dazu `aussprache` für Abkürzungen und Fremdwörter.
3. `node reels/vertonen.mjs <vertonung.json> <video.mp4>` → `vertont.mp4` und `untertitel.srt`.
   - Synchron zu Schrift und Bild (empfohlen): `"anhalten": true, "kuerzen": true`. Pro Element, das im Video erscheint, ein Teil mit dessen Startzeit und genau dem Text aus dem Bild (fette Zeilen). Das Bild hält an, bis die Ansage fertig ist; langes Stehen danach wird gekürzt. Teile ohne `text` markieren Szenenwechsel.
   - Startzeiten der Elemente: Bildunterschiede pro Zeile messen (Elemente erscheinen von oben nach unten) und mit Einzelbildern kontrollieren. Ansage nie vor dem Element starten.
   - Tempo: `"tempo": 1.08` (größer = langsamer). Reels unter 3 Minuten halten, sonst Text kürzen.
   - Ohne `anhalten` bleibt die Videolänge gleich; zu lange Ansagen werden bis 15 % schneller gesprochen.
4. Mit `pruefe-ton.py` gegenlesen und falsch ausgesprochene Wörter in `aussprache` umschreiben.

## Stimme und Zeitmarken (empfohlen)
- `"stimme": "edge:de-DE-ConradNeural"` nutzt eine Microsoft-Neural-Stimme: flüssig und natürlich, braucht Internet. `"tempo": "+0%"` (z. B. `"-6%"` = langsamer).
  Ohne `edge:` wird die lokale Piper-Stimme genutzt (weniger natürlich).
- Im `sprecher`-Text markiert `|` eine Stelle. Elemente mit `data-t="m1"`, `"m2"` … (oder `"t": "m3+0.5"` bei Texten) erscheinen genau, wenn das Wort nach dem 1., 2. … `|` gesprochen wird.
  So bleibt die Stimme durchgehend flüssig und Schrift und Bild kommen trotzdem passend.
- Bausteine für `html`: `tabelle` (Zeilen mit zwei Werten), `karten` / `karten zwei` mit `karte` bzw. `karte voll`, `nummern` (nummerierte Liste).
  Text: `{"s": "…", "hinweis": "GUT ZU WISSEN"}` ergibt eine Hinweisbox. Im Titel hebt `<em>…</em>` ein Wort beige hervor.
- Logo: `marke/kimutec-logo.png` (aus dem Original-Reel ausgeschnitten, transparent).
- Hinweis: Die edge-Stimmen kommen vom Vorlesedienst des Edge-Browsers. Für bezahlte Werbung ist der Azure-Sprachdienst mit denselben Stimmen die lizenzrechtlich saubere Variante.
- Instagram-Reels dürfen höchstens 3 Minuten lang sein.

## Effekte (seit Reel 9)
- `class='pop'`: Element ploppt mit leichtem Überschwingen auf (auch für SVG-Gruppen; dann kein `transform`-Attribut an derselben Gruppe, sondern eine innere `<g transform=…>`).
- `data-drehen="90"`: dreht sich ab dem Einblenden mit 90 °/s (Zahnräder, Räder).
- `data-schweben="4"`: schwebt sanft auf und ab (z. B. Handy).
- `data-zahl="1012" data-einheit=" mm"`: Zahl zählt beim Einblenden hoch.
- `data-ursprung="left bottom"`: Drehpunkt für pop/drehen.
- Szene mit `"schritt": 3` (und optional `"schrittVon": 8`) zeigt oben rechts „SCHRITT 3 / 8“ mit Punkten.
- Größere Reels mit eigenem Generator bauen: Vorlage `projekte/09-ablauf/bauen.py` (Hilfen für Chips, Sprechblasen, Sterne, Zahnräder, Fenster).
- Szenenwechsel sind bewusst dezent (Wunsch von Ramiz): Wischer 0,3, Unschärfe 3 px, Versatz 18 px. Anpassen nur auf Wunsch mit
  `"uebergang": {"wisch": 0.3, "unschaerfe": 3, "versatz": 18}` im Drehbuch (`"unschaerfe": 0` schaltet die Unschärfe ab).

## Figuren und Spuren (seit Reel 9, Version 2)
Strichmännchen mit Gelenken (Ellbogen, Knie), weichen Übergängen und echten Handgriffen. Python-Helfer: `reels/figur.py`,
Engine: `reels/engine/bewegung.js`. Vorlage mit allen Möglichkeiten: `projekte/09-ablauf/bauen.py`.
- `figur(typ, boden, [k(t, …), …], s=1)` – Typen `monteur` (beige, Kappe), `kunde`, `kundin`, `arbeiter` (Hersteller, grau).
  Keys: `x`, `b` (Blick 1/−1), `pose` (stehen zeigen erklaeren tippen telefon messen tragen heben hocken knien bohren schreiben
  jubeln daumen sitzen winken haende), Winkel (`aV eV aH eH bV kV bH kH ru ko`), `gehen=True` (läuft zur neuen x-Position, auch rückwärts),
  `zV`/`zH` = Griffziel der Hand (`[x, y]` oder `an('id', x, y)` = Punkt eines Elements mit Spur, die Hand folgt ihm; `None` = loslassen),
  `pV`/`pH` = Werkzeug (handy laser klemmbrett stift bohrer kartusche tasse tablet daumen; `{'art': 'laser', 'w': 90}` = gedreht),
  `osz=[osz('eV', 6, 3.5, dauer=1.2)]` = Schwingen (Tippen, Schreiben, Nicken `ko`, Händeschütteln `zyV`), `d` = Dauer, `e` = Kurve.
- Zeiten wie überall: Sekunden, `"40%"` oder `"m3+0.5"`. Ein Key läuft von `t` bis `t + d`.
  Ankunft genau zu einem Wort: `k('m1-2.1', x=…, gehen=True, d=2.1)`. Hereinlaufen von außen: Start bei `x=-130` (links) oder `x=1050` (rechts).
  Erster Key mit `t=-9` (Startzustand), sonst überschreibt er spätere Keys mit negativer Zeit.
- Reichweite: Schulter ≈ `boden − 225·s`, Arm ≈ `108·s` px. Fenster und Griffpunkte so legen, dass die Hand hinkommt (Fensterhöhen realistisch).
- `spur(inhalt, [k(t, x=, y=, r=, s=, sx=, sy=, o=, e=)], id=…, ursprung='460px 300px')` bewegt beliebige Elemente mit Keyframes.
  Zwischen zwei Keys wird immer weich übergeblendet – für „bis m3 stehen, dann bewegen“ einen Halte-Key setzen (`k('m3', x=0)`).
- `data-fallen="dx,dy,periode"` verschiebt wiederkehrend (Regen hinter Glas mit clipPath, Schallwellen).
- Die alten Wackel-Figuren in `reels/figuren.py` nicht mehr verwenden.

## Stimme von ElevenLabs (Standard)
Die Cloud erreicht `api.elevenlabs.io` nicht (auch nicht Hugging Face und den Microsoft-Vorlesedienst). Zwei Wege:

### Weg A: ElevenLabs-Connector + MP3 hochladen (bei Reel 9 genutzt)
1. Den ganzen Sprechertext als eine Ansage erzeugen (Connector-Werkzeug `creative_generate_speech`, Stimme `5KvpaGteYkNayiswuX2h`,
   Modell `eleven_multilingual_v2`). Text: je Szene ein Absatz, ohne `|`, mit eingesetzter `aussprache` (z. B. „Kimu-Tek“).
   Jede Erzeugung kostet Guthaben – nicht „zur Sicherheit“ wiederholen.
2. Die Audio-Links (elevenlabsusercontent.com) sperrt der Cloud-Proxy. Ramiz lädt die gewählte Variante herunter und schickt die MP3 in den Chat.
3. `python3 reels/elevenlabs.py zerlegen <take.mp3> <drehbuch.json>`: Parakeet (sherpa-onnx, Modell von GitHub) erkennt jedes Wort mit
   Zeitpunkt, die Wörter werden am Sprechertext ausgerichtet und je Szene als `ton/sNN.json` (gleiches Format wie Weg B) und `sNN.mp3`
   gespeichert. Ausgabe: Treffer je Szene und erkannter Text – bei wenigen Treffern Text und Take vergleichen.
4. Nur einige Szenen neu (z. B. andere Aussprache): nur diese Absätze als eine Ansage erzeugen und
   `python3 reels/elevenlabs.py zerlegen <take.mp3> <drehbuch.json> --szenen=1,5,8,12`. Die anderen Dateien in `ton/` bleiben.

### Weg B: Ansagen über den PC von Ramiz (Zeitstempel direkt von ElevenLabs)
1. Drehbuch: `"stimme": "elevenlabs"`, `"elevenlabs": {"voice_id": "5KvpaGteYkNayiswuX2h", "model_id": "eleven_multilingual_v2", "voice_settings": {…}}`.
2. `python3 reels/elevenlabs.py skript <drehbuch.json> <ordner>` → `Stimme holen.cmd` + `stimme_holen.ps1`. Beides in den verbundenen
   PC-Ordner legen (SendUserFile, dann device_commit_files). Daneben liegt `elevenlabs.txt` mit dem API-Schlüssel (nie in den Chat).
3. Doppelklick auf „Stimme holen.cmd“ → `ton\s01.json …` (Ton + Zeitpunkt jedes Zeichens). Den Ordner `ton` zurückholen
   (device_stage_files) nach `reels/projekte/<name>/ton/` und `python3 reels/elevenlabs.py pruefen <drehbuch.json>` ausführen.
4. Rendern: `render.mjs` legt die Marken `|` exakt auf die Wörter. Der gesendete Text ist der Sprechertext ohne `|` mit `aussprache`.
   Ändert sich danach nur die Lage der `|`, muss nichts neu erzeugt werden; ändert sich ein Wort, Szene neu holen.
- Für Werbung braucht ElevenLabs ein bezahltes Abo (das kostenlose hat keine kommerzielle Lizenz).
