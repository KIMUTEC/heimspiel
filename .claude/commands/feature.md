---
description: Feature komplett durchziehen – planen, bauen, testen, unabhängig reviewen, Urteil SHIP / nochmal ran
argument-hint: [Feature in normalem Deutsch, z. B. „Seilspringen als neue Übung mit Animation“]
effort: xhigh
---
<feature>
$ARGUMENTS
</feature>

Arbeite das Feature als Pipeline ab. Halte dich an `CLAUDE.md`.

1. **Planen** – betroffene Stellen in `index.html` finden, 1–2 Ansätze mit Nachteilen, Empfehlung, Liste der Dateien. Dann STOPP und auf mein „los“ warten. Ausnahme: Ich habe schon „ohne Rückfrage“ geschrieben und die Änderung fasst weder Datenformat noch Sicherung an.
2. **Checkpoint** – `git add -A && git commit -m "Checkpoint vor <Feature>"`, falls es offene Änderungen gibt.
3. **Bauen** – nach den Mustern in `CLAUDE.md`. Texte kindgerecht (Regeln wie in `/texte`). Cache-Version in `sw.js` erhöhen.
4. **Testen** – `node tools/check.mjs`. App mit `python3 -m http.server` starten und mit Playwright in 390 px Breite durchklicken: neues Feature, ein Workout starten und beenden, Neuladen (Daten noch da?), hell und dunkel. Fehler selbst beheben und erneut testen.
5. **Review** – einen Sub-Agent mit frischem Blick den Diff prüfen lassen (Bugs, gebrochene Daten, iOS-Fallbacks, `esc()` bei Nutzertext, Texte). Berechtigte Funde beheben.
6. **Ergebnis** – kurz fürs Handy:
   - **SHIP** oder **NOCHMAL RAN** (mit Grund)
   - was neu ist, in 2–3 Sätzen
   - Screenshot(s) mitschicken
   - was ich selbst auf dem iPhone prüfen sollte (höchstens 3 Punkte)

Commit auf einem eigenen Branch, nicht auf `main`. Pushen erst nach meinem Okay.
