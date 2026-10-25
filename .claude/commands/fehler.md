---
description: Fehler oder Problem lösen – Diagnose, Optionen, Abwägung, Empfehlung
argument-hint: [kompletter Fehlertext oder Beschreibung, was passiert]
---
<problem>
$ARGUMENTS
</problem>

<context>
Heimspiel: Offline-PWA, Hauptplattform Safari auf iPhone/iPad, ganze App in `index.html`, Offline-Cache in `sw.js`, Daten in `localStorage` (`heimspiel.v1`). Fehlertext immer vollständig nehmen, nicht zusammenfassen.
</context>

<task>
Arbeite in vier Schritten und gib jeden vollständig aus, bevor du zum nächsten gehst. Noch nichts ändern.

1. **Diagnose** – 3–5 mögliche Ursachen mit genauer Code-Stelle (Datei:Zeile), sortiert nach Wahrscheinlichkeit (hoch/mittel/niedrig) und warum. Falls möglich: reproduzieren (z. B. Playwright in 390 px Breite), statt zu raten.
2. **Optionen** – für die wahrscheinlichste Ursache 2–3 Lösungswege.
3. **Abwägung** – Tabelle: Option | Aufwand (S/M/L) | Risiko (S/M/L) | Rückgängig machbar (ja/nein) | Gefahr für gespeicherte Daten (ja/nein).
4. **Empfehlung** – einen Weg wählen, Begründung in 2 Sätzen, und den kleinsten ersten Schritt.
</task>

<constraints>
- Nicht direkt zur Lösung springen.
- Keine Empfehlung ohne genannten Nachteil.
- Ist die Ursache unklar, sag das und nenn, was sie klären würde (Log, Gerät, iOS-Version).
</constraints>

Warte auf mein „los“, dann setz den gewählten Weg um, lass `node tools/check.mjs` laufen und erhöh bei Bedarf die Cache-Version in `sw.js`.
