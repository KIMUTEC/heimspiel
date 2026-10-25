---
description: Sicherheits-Check der App
---
Scan `index.html`, `sw.js` und `manifest.webmanifest` auf: XSS (Nutzertext ohne `esc()` in innerHTML), unsicheres Laden fremder Ressourcen, Secrets im Code, fehlende Input-Validierung (Profil-Formular, Sicherung laden/Import), Datenlecks nach außen (Tracking, externe Links – das ist eine Kinder-App). Pro Finding: Severity, Stelle (Datei:Zeile), Risiko, Fix. Noch nichts ändern.
