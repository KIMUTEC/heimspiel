---
name: release
description: Macht eine fertige Änderung für Nutzer sichtbar, indem die Cache-Versionen der Service Worker erhöht werden, prüft und committet. Nutzen, wenn eine Änderung fertig ist oder der Nutzer "veröffentlichen", "release" oder "ausliefern" sagt.
---

1. Mit `git diff --name-only origin/main...HEAD` und `git status` feststellen, welche App betroffen ist (Dateien unter `vital/` = Vital, sonst Heimspiel; `fonts/` betrifft beide).
2. Heimspiel betroffen: in `sw.js` `const V='heimspiel-vN'` auf N+1 setzen.
3. Vital betroffen: in `vital/sw.js` `const V='vital-vN'` auf N+1 setzen und in `vital/index.html` `const VERSION='JJJJ-MM-TT.N'` auf das heutige Datum setzen (gleicher Tag: N+1, neuer Tag: `.1`).
4. Neue Dateien, die offline gebraucht werden, in `ASSETS` des passenden `sw.js` ergänzen.
5. Skill `pruefen` ausführen.
6. Mit kurzer deutscher Commit-Nachricht committen und auf den aktuellen Branch pushen.
