# Erzeugt eine Ansage mit einer Microsoft-Neural-Stimme (edge-tts) und liefert Zeitmarken.
# Aufruf: python3 reels/stimme.py <stimme> <tempo> <ausgabe.mp3>   (Text über stdin)
#   tempo: z. B. "-5%" (langsamer) oder "+0%"
# Ein "|" im Text markiert eine Stelle. Ausgabe (JSON): {"marken": [Sekunden, …]} – Zeitpunkt des ersten Worts nach jedem "|".
import asyncio, json, re, sys, os

# Hinter dem Proxy der Cloud-Session braucht edge-tts dessen Zertifikat
ca = '/root/.ccr/ca-bundle.crt'
if os.path.exists(ca):
    import certifi
    certifi.where = lambda: ca
import edge_tts

stimme, tempo, ziel = sys.argv[1:4]
roh = sys.stdin.read().strip()
norm = lambda w: re.sub(r'[^0-9a-zäöüß]', '', w.lower())

# Für jede Marke: wie vielte Wort-Nummer folgt danach?
teile = roh.split('|')
woerter_vor = []
n = 0
for t in teile[:-1]:
    n += len([w for w in t.split() if norm(w)])
    woerter_vor.append(n)
text = ' '.join(' '.join(teile).split())

async def los():
    grenzen = []
    c = edge_tts.Communicate(text, stimme, rate=tempo, boundary='WordBoundary')
    with open(ziel, 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                grenzen.append((ch['offset'] / 1e7, norm(ch['text'])))
    return grenzen

grenzen = asyncio.run(los())
# Wörter aus dem Text den gemeldeten Wörtern zuordnen (Bindestrich-Wörter können geteilt gemeldet werden)
tokens = [norm(w) for w in text.split() if norm(w)]
start_zeit, g = [], 0
for tok in tokens:
    while g < len(grenzen) and grenzen[g][1] and not (tok.startswith(grenzen[g][1]) or grenzen[g][1].startswith(tok[:3])):
        g += 1
    start_zeit.append(grenzen[min(g, len(grenzen) - 1)][0] if grenzen else 0)
    # alle Teile dieses Worts überspringen
    rest = tok
    while g < len(grenzen) and rest:
        teil = grenzen[g][1]
        if rest.startswith(teil) and teil:
            rest = rest[len(teil):]; g += 1
        else:
            g += 1; break
marken = [start_zeit[i] if i < len(start_zeit) else (grenzen[-1][0] if grenzen else 0) for i in woerter_vor]
print(json.dumps({'marken': [round(m, 3) for m in marken]}))
