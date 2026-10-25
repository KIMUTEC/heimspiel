---
description: Bug reproduzieren, Test schreiben, dann fixen
argument-hint: [Bug-Report]
---
Bug-Report: $ARGUMENTS

1. Bau eine minimale Reproduktion: Schritte, erwartetes Verhalten, tatsächliches Verhalten.
2. Schreib ein kleines Playwright-Skript (Handy-Breite 390 px, Datei im Scratchpad), das den Bug zeigt und fehlschlägt.
3. Fix den Code, bis das Skript grün ist. `node tools/check.mjs` muss danach sauber laufen.
