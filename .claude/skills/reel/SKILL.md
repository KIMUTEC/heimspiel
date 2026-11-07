---
name: reel
description: Erstellt ein animiertes KIMUTEC-Erklär-Reel (Instagram, 1080×1920, mit Sprecher) zu einem Thema rund um Fenster, Türen, Tore und Sonnenschutz. Nutzen, wenn der Nutzer ein Reel, Video, Instagram-Clip oder "so ein Video wie Reel 6" möchte, oder ein Reel-Video zum Nachbauen schickt.
---

Anleitung und Bausteine: `reels/README.md`. Vorlage: `reels/projekte/06-aufmass-montage/drehbuch.json`.

1. Einrichten, falls `~/.cache/piper/de_DE-thorsten-high.onnx` fehlt: `bash reels/einrichten.sh`.
2. Thema klären. Schickt der Nutzer ein Video: Bilder mit ffmpeg als Kontaktbogen ansehen und den Ton mit `python3 reels/pruefe-ton.py <video>` mitschreiben.
3. Drehbuch schreiben (`reels/projekte/<nr>-<thema>/drehbuch.json`), Aufbau wie Reel 6:
   - Einstieg mit starker Aussage, 5–7 Fachszenen mit je einer Kernbotschaft, Szene „aus einer Hand“, Abschluss mit Kontakt.
   - Titel kurz (max. 3 Zeilen à ca. 16 Zeichen), Label im Format `THEMA | UNTERTHEMA`.
   - Sprechertext pro Szene 1–2 Sätze, Sie-Form, sachlich, ca. 55–65 s gesamt.
   - Fachlich korrekt bleiben (RAL-Montage, Dämmebene, Abdichtung). Bei Unsicherheit den Nutzer fragen statt raten.
   - Zeichnungen schlicht, Element-Einblendungen per `data-t` mit Prozentwerten an den Sprechertext koppeln.
4. `node reels/render.mjs <drehbuch> --schnell`, `vorschau.jpg` ansehen, Layout korrigieren (nichts darf überlappen oder abgeschnitten sein).
5. Vollständig rendern, einige Bilder mitten in Szenen prüfen und den Ton mit `pruefe-ton.py` gegenlesen.
6. `reel.mp4` und `vorschau.jpg` mit SendUserFile schicken, Drehbuch committen und pushen (Videos sind per .gitignore ausgeschlossen).
