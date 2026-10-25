---
description: App-Texte für Kinder schreiben oder prüfen – mit Ausschluss-Regeln und Selbstbewertung
argument-hint: [was für Texte, z. B. „Anleitung für neue Übung Seilspringen“ oder „alle Texte im Profil prüfen“]
effort: high
---
<task>
$ARGUMENTS
</task>

<context>
Heimspiel ist eine Trainings-App für Kinder von 6–17 Jahren, die allein oder mit Eltern zu Hause trainieren. Die Texte lesen Kinder auf dem Handy, oft mitten in der Übung, manche hören sie auch über die Sprachausgabe (`say`, Deutsch). Die Altersgruppen stehen in `AGEG` (mini 6–9, kids 10–13, teen 14–17).
</context>

<examples>
Lies zuerst vorhandene Texte als Vorbild für Ton und Länge: Übungs-Anleitungen `c` in `EX` (z. B. `jog`, `jack`), `CHEERS`, Programm-Beschreibungen `d` in `PROGRAMS`, Meldungen in `toast(...)`.
</examples>

<constraints>
- Du-Form, aktiv, Präsens. Kurze Sätze (höchstens etwa 12 Wörter), ein Gedanke pro Satz.
- Übungs-Anleitungen: höchstens 2 Sätze, erst die Bewegung, dann der eine wichtigste Tipp.
- Keine Fachbegriffe ohne Erklärung, kein Englisch, wenn es ein gutes deutsches Wort gibt.
- Kein Druck, keine Schuld, kein Schimpfen („Du hast schon wieder…“). Fehler sind normal.
- Kein Vergleich mit anderen Kindern, keine Aussagen zu Gewicht oder Aussehen.
- Keine Gesundheits- oder Leistungsversprechen („macht dich schneller als alle“), keine erfundenen Normwerte.
- Sicherheit vor Tempo: wo nötig, kurz sagen, worauf das Kind achten soll (Platz, Boden, Ball nicht gegen Fenster).
- Keine Emojis, keine Ausrufezeichen-Ketten, keine rhetorischen Fragen.
- Kein Text, der auch in jeder anderen Fitness-App stehen könnte.
</constraints>

<verification>
Intern, vor der Ausgabe: Jeden Text 1–10 bewerten nach (a) versteht ein 8-jähriges Kind ihn beim ersten Lesen, (b) klingt er ausgesprochen natürlich, (c) konkret statt allgemein, (d) hält alle Regeln oben ein. Liegt der Schnitt unter 8: neu schreiben, nicht nachbessern, höchstens 3 Runden. Streng bewerten.
</verification>

<output_format>
Tabelle: Stelle im Code | alter Text (falls vorhanden) | neuer Text | Score. Darunter in einem Satz, was am schwersten war. Erst nach meinem „los“ die Texte in `index.html` eintragen, `node tools/check.mjs` laufen lassen und die Cache-Version in `sw.js` erhöhen.
</output_format>
