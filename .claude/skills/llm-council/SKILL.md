---
name: llm-council
description: "Wichtige Entscheidung von 5 unabhängigen Beratern prüfen lassen, die sich anonym gegenseitig bewerten; ein Vorsitzender fasst zu einem Urteil zusammen. Auslöser: 'council this', 'Lass das Council drüberlaufen', 'stress-test this', 'pressure-test this', /llm-council. Nur für echte Entscheidungen mit Abwägung (z. B. neues Feature ja/nein, Variante A oder B, Datenformat ändern, App aufteilen). NICHT für Faktenfragen, einfache Ja/Nein-Fragen oder reine Umsetzungsaufgaben."
---

# LLM-Council

Methode nach Andrej Karpathys „LLM Council“, Skill-Idee von Ole Lehmann (github.com/aiwithremy/claude-skills-llm-council), für Heimspiel angepasst.

Eine Antwort ist eine Sicht. Das Council liefert fünf, lässt sie sich gegenseitig prüfen und macht daraus ein klares Urteil.

## Die fünf Berater

1. **Kritiker** – sucht den Fehler, der alles kippt. Was geht kaputt, was fehlt, was wird scheitern?
2. **Erste-Prinzipien-Denker** – fragt: Welches Problem lösen wir eigentlich? Sagt auch mal „falsche Frage“.
3. **Chancen-Sucher** – was wäre möglich, wenn es besser läuft als gedacht? Was wird unterschätzt?
4. **Außenblick (Kind & Eltern)** – kennt weder Code noch Vorgeschichte. Sieht die App wie ein 8-jähriges Kind oder ein Elternteil, das sie zum ersten Mal öffnet. Findet, was Insidern selbstverständlich scheint.
5. **Macher** – nur eins zählt: Wie setzen wir das um, und was ist der erste konkrete Schritt?

Spannungen: Kritiker ↔ Chancen-Sucher, Erste Prinzipien ↔ Macher. Der Außenblick hält alle ehrlich.

## Ablauf

### 1. Frage rahmen
- Kurz Kontext lesen: `CLAUDE.md`, betroffene Stellen in `index.html`, Dateien, die der Nutzer nennt. Höchstens 2–3 Dateien, nicht lange suchen.
- Daraus eine neutrale Frage formulieren: die Entscheidung, der Kontext (Kinder-App, offline, iOS, Daten auf dem Gerät), was auf dem Spiel steht. Keine eigene Meinung hineinlegen.
- Ist die Frage zu vage: genau eine Rückfrage stellen, dann weiter.

### 2. Berater befragen (5 Sub-Agents parallel)
Alle fünf gleichzeitig starten, nicht nacheinander. Vorlage:

```
Du bist der [Name] in einem LLM-Council.
Deine Denkweise: [Beschreibung von oben]
Die Frage an das Council:
---
[gerahmte Frage]
---
Antworte aus deiner Sicht. Direkt und konkret, nicht ausgewogen – die anderen decken die anderen Blickwinkel ab.
150–300 Wörter, auf Deutsch, ohne Einleitung. Erfinde keine Quellen oder Zahlen; wenn du etwas nicht weißt, sag es.
```

### 3. Anonymes Peer-Review (5 Sub-Agents parallel)
Antworten zufällig als A–E mischen (keine feste Zuordnung). Jeder Prüfer sieht alle fünf und beantwortet, unter 200 Wörtern:
1. Welche Antwort ist am stärksten, und warum?
2. Welche hat den größten blinden Fleck, und welchen?
3. Was haben ALLE fünf übersehen?

### 4. Urteil des Vorsitzenden
Ein Agent bekommt Frage, alle Antworten (mit Namen) und alle Reviews. Er darf der Mehrheit widersprechen, wenn die Begründung der Minderheit stärker ist. „Kommt drauf an“ ist keine Empfehlung.

### 5. Im Chat ausgeben (keine Dateien)

```
## Council-Urteil: [Thema]
### Hier sind sich alle einig
### Hier gibt es Streit
### Blinde Flecken aus dem Review
### Empfehlung
### Der erste Schritt
```

Kurz, Stichpunkte, für das Handy lesbar. Ein Protokoll nur speichern, wenn der Nutzer es will (`docs/council/JJJJ-MM-TT-thema.md`).
