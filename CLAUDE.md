# Heimspiel – Hinweise für Claude

Zwei Offline-PWAs ohne Build-Schritt und ohne Abhängigkeiten, gehostet über GitHub Pages.

- `index.html` – **Heimspiel**: Fußball-/Basketball-Training für Kinder (6–17). HTML, CSS und JS in einer Datei.
- `vital/index.html` – **Vital**: Erwachsenen-App (Ernährung, Trinken, Training, Gen-/Blutwerte). Ebenfalls eine Datei.
- `sw.js`, `vital/sw.js` – Service Worker (Offline-Cache). `fonts/` und `icons/` nutzen beide Apps.

## Regeln
- Oberfläche, Commits und PRs auf **Deutsch**: einfach und kindgerecht (Heimspiel), klar (Vital).
- Keine externen Bibliotheken, CDNs oder Server. Alles muss offline laufen; Daten bleiben im `localStorage` des Geräts.
- Keine Build-Tools einführen. Code bleibt in der jeweiligen `index.html`.
- iOS Safari (Home-Bildschirm-App) ist Zielplattform Nr. 1: Safe-Area und große Touch-Flächen beachten.
- Hell- und Dunkelmodus über die CSS-Variablen in `:root` pflegen, keine festen Farben im Markup.
- Neue Dateien, die offline gebraucht werden, in `ASSETS` des passenden `sw.js` eintragen.

## Nach jeder Änderung
1. `node scripts/pruefen.mjs` ausführen (Syntax-Check und Browser-Start beider Apps). Skill: `/pruefen`.
2. Cache-Version erhöhen, sonst sehen Nutzer die Änderung nicht. Skill: `/release`.
   - Heimspiel: `const V='heimspiel-vN'` in `sw.js`
   - Vital: `const V='vital-vN'` in `vital/sw.js` **und** `const VERSION='JJJJ-MM-TT.N'` in `vital/index.html`
