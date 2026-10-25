---
description: Entwurf aus Claude Design (Screenshot, HTML, Beschreibung) in die echte App übernehmen
argument-hint: [Entwurf anhängen oder beschreiben, welcher Screen]
effort: high
---
<entwurf>
$ARGUMENTS
</entwurf>

<context>
Ein Entwurf liefert den Look, nicht die App. Heimspiel hat ein festes System: CSS-Variablen in `:root` (Hell- und Dunkelmodus, Sportfarben `--acc-f` Fußball / `--acc-b` Basketball), Schriften Big Shoulders Display (`--display`) und Figtree (`--body`), eine Spalte bis 720 px, Tabs Coach/Einheiten/Profil, Workouts im Vollbild auf dunkler Bühne.
</context>

<task>
1. Beschreib in 3–5 Stichpunkten, was der Entwurf am bestehenden Screen ändert.
2. Ordne jede Farbe, Schrift und Größe einer vorhandenen Variable zu. Wo keine passt: sag es und schlag eine neue Variable vor (mit Wert für hell und dunkel), statt Farben fest einzubauen.
3. Nenn die Stellen in `index.html` (Ansicht, CSS-Block), die sich ändern.
4. Warte auf mein „los“. Dann umsetzen, nach den Mustern in `CLAUDE.md`.
</task>

<constraints>
- Keine fremden Bibliotheken, Schriften oder Bilder von außen übernehmen, auch wenn der Entwurf sie nutzt. Alles muss offline laufen.
- Funktionen, Datenformat und Abläufe bleiben, wie sie sind, wenn ich nichts anderes sage. Der Entwurf ändert nur das Aussehen.
- Bedienbar für Kinderhände: Tippflächen mindestens 44 px, gut lesbarer Kontrast.
</constraints>

<verification>
Nach dem Umsetzen: `node tools/check.mjs`, Cache-Version in `sw.js` erhöhen, Screenshots mit Playwright in 390 px Breite, hell und dunkel, und mit dem Entwurf vergleichen. Abweichungen ehrlich nennen.
</verification>
