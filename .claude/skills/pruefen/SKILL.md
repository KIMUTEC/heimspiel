---
name: pruefen
description: Prüft Heimspiel und Vital nach einer Änderung (JS-Syntax, Start im Browser ohne Fehler, Handy-Screenshot). Nutzen nach jeder Code-Änderung und bevor committet wird.
---

1. `node scripts/pruefen.mjs` ausführen. Bei Fehlern die Ursache beheben und erneut ausführen.
2. Bei sichtbaren Änderungen mit Playwright einen Screenshot in Handygröße (390×844) der betroffenen App machen, einmal hell und einmal dunkel (`colorScheme: 'dark'`), im Scratchpad speichern und anschauen.
3. Kurz berichten: was geprüft wurde, was in Ordnung ist, was nicht.
