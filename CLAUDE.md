# Heimspiel – Übergabe für Claude

Heimspiel ist eine Offline-Web-App (PWA) für Fußball- und Basketball-Training von Kindern (6–17 Jahre) zu Hause. Läuft über GitHub Pages, wird auf iPhone/iPad per „Zum Home-Bildschirm" installiert. Kein Server, kein Konto, keine Daten verlassen das Gerät.

Deine Rolle: Senior-Engineer, der mitdenkt – kein Autocomplete. Bei Unklarheit erst fragen, bei größeren Änderungen erst einen Plan zeigen.

## Aufbau

- `index.html` – die ganze App: CSS, HTML und ein `<script>`-Block. Keine Build-Tools, keine Abhängigkeiten.
- `sw.js` – Service Worker, speichert alle Dateien für offline. Liste `ASSETS`, Cache-Name `V`.
- `manifest.webmanifest` – PWA-Manifest (Name, Farben, Icons).
- `fonts/` – Big Shoulders Display + Figtree (woff2, lokal eingebunden).
- `icons/` – App-Icons und Favicon.
- `tools/check.mjs` – Schnell-Check (Syntax + Offline-Dateien).

Abschnitte im Script von `index.html` (Suche nach `/* ====`):
1. **Übungen & Animationen** – `EX` (alle Übungen: Name `n`, Kategorie `cat`, Anleitung `c`, Animation `a`), Posen als Zahlen-Arrays (`STAND`, `PLANK` …), `TESTS`, `PROGRAMS`, `LEVELS`, `RANKS`.
2. **Hilfsfunktionen** – `$`, `esc`, Datums-Helfer (`today`, `addDays`, `keyOf`, Format `JJJJ-MM-TT`).
3. **Animations-Engine** – `poseAt`, `drawFig` zeichnen Strichfiguren auf `canvas.anim`.
4. **Zustand & Speicher** – Zustand `S`, `localStorage`-Schlüssel `heimspiel.v1`. `markDirty(key)` speichert lokal und synct optional (nur wenn `window.claude.use('db')` verfügbar ist).
5. **Profil & Coach** – Trainingsplan, Streak, Ränge.
6. **Ansichten** – `render()`, `viewCoach`, `viewUnits`, `viewProfil`, `viewOnboard`, `renderSheet`.
7. **Player** – Workout-Ablauf im Vollbild (`start`, `work`, `next`, `tick`, `draw`), Ton (`beep`), Sprache (`say`, de-DE), Wake Lock.
8. **Aktionen** – `ACT`: Klick-Handler, angesprochen über `data-act="name"` im HTML.

## Muster (an Bestehendem orientieren)

- Neue Übung → wie `jog` / `jack` in `EX`. Pose-Arrays: Paare aus x/y-Werten auf einem 100×97-Raster.
- Neues Programm → wie `ballzauber` in `PROGRAMS` (`id`, `n`, `sport: 'f'|'b'`, `d`, `items`).
- Neuer Button → Handler in `ACT` ergänzen, im HTML `data-act="…"` setzen.
- Neue Ansicht/Abschnitt → als Template-String zurückgeben wie `viewUnits`; Nutzertext immer durch `esc()`.
- Farben nur über CSS-Variablen in `:root` (`--acc`, `--soft`, `--ink` …). Hell- und Dunkelmodus beide pflegen.
- `localStorage` immer in `try/catch` (Safari Privatmodus wirft Fehler).

## Regeln

- **Code-Stil:** kompakt wie der Bestand (kurze Namen, wenig Leerzeilen). Keine Frameworks, keine CDN-Skripte, keine npm-Pakete – die App muss komplett offline laufen.
- **Sprache:** Alle Texte in der App auf Deutsch, kindgerecht, ermutigend, Du-Form. Commit-Messages auf Deutsch.
- **Datenformat:** Struktur von `S.app` und `S.days` nicht brechen. Alte Sicherungen und gespeicherte Daten müssen weiter laden. Wenn nötig: Migration beim Laden, nicht Schlüssel umbenennen.
- **Offline-Cache:** Wenn sich `index.html` oder eine andere gecachte Datei ändert, Cache-Version in `sw.js` erhöhen (`heimspiel-v3` → `heimspiel-v4`). Neue Dateien in `ASSETS` eintragen.
- **iOS zuerst:** Safari/iOS ist die Hauptplattform. Keine APIs ohne Fallback (Wake Lock, Speech, Share sind optional).
- **Sicherheit fürs Kind:** keine externen Links, kein Tracking, keine Analyse-Dienste.
- **Git:** Nicht direkt auf `main` committen, wenn nicht ausdrücklich gewünscht. Vor größeren Änderungen Checkpoint-Commit. Nie force-pushen.

## Prüfen

```bash
node tools/check.mjs          # Syntax + Offline-Dateien
python3 -m http.server 8000   # lokal testen: http://localhost:8000
```

Nach jeder Änderung `node tools/check.mjs` laufen lassen. Bei sichtbaren Änderungen die App lokal öffnen (Playwright ist verfügbar) und einen Screenshot in Handy-Breite (390 px) prüfen.

## Eigene Befehle (`.claude/commands/`)

`/plan`, `/diff-review`, `/fehler`, `/security-scan`, `/performance`, `/refactor-plan`, `/bug-repro`, `/blame`, `/recovery`, `/doku`, `/checkpoint`
