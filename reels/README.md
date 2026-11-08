# KIMUTEC-Reels

Animierte Erklär-Reels (1080×1920, 30 fps, mit Sprecher) im KIMUTEC-Stil: dunkler Hintergrund,
Montserrat, beige Akzente, Linien-Zeichnungen, die passend zum Sprecher erscheinen.

## So entsteht ein Reel
1. Einmal einrichten: `bash reels/einrichten.sh`
2. Ordner `reels/projekte/<nr>-<thema>/` mit einer `drehbuch.json` anlegen (Vorlage: `projekte/06-aufmass-montage`).
3. Rendern: `node reels/render.mjs reels/projekte/<nr>-<thema>/drehbuch.json`
   - `--schnell` erzeugt nur `vorschau.jpg` und den Ton (ca. 20 s statt 2 min).
4. Prüfen: `vorschau.jpg` ansehen, `python3 reels/pruefe-ton.py …/reel.mp4` liest den Sprecher mit.

Ergebnis im Projektordner: `reel.mp4`, `vorschau.jpg`, `untertitel.srt` (für Instagram-Untertitel), `sprecher.wav`.
Videos und Ton werden nicht ins Repo eingecheckt.

## Drehbuch
```json
{
  "stimme": "de_DE-thorsten-high", "tempo": 1.0,
  "aussprache": { "KIMUTEC": "Kimutek" },
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
   Die Ausgabe zeigt pro Abschnitt Sprechdauer/Platz. Zu lange Ansagen werden bis 15 % schneller gesprochen, sonst Text kürzen.
4. Mit `pruefe-ton.py` gegenlesen und falsch ausgesprochene Wörter in `aussprache` umschreiben.
