# ElevenLabs-Ansagen für ein Reel (mit Wort-Zeiten für die Synchronisation).
#
# Die Cloud-Umgebung erreicht api.elevenlabs.io nicht. Deshalb holt der PC des Nutzers die Ansagen:
#   1. python3 reels/elevenlabs.py skript reels/projekte/<name>/drehbuch.json <ausgabeordner>
#      → "Stimme holen.cmd" + "stimme_holen.ps1" (Windows). In den verbundenen Ordner auf dem PC legen,
#        daneben elevenlabs.txt mit dem API-Schlüssel. Doppelklick holt ton\s01.json … (eine Datei pro Szene).
#   2. Den Ordner ton\ zurückholen nach reels/projekte/<name>/ton/ und prüfen:
#      python3 reels/elevenlabs.py pruefen reels/projekte/<name>/drehbuch.json
#   3. Rendern wie immer (Drehbuch: "stimme": "elevenlabs"). render.mjs liest Ton und Zeichen-Zeiten aus ton/sNN.json.
#
# Drehbuch-Felder: "elevenlabs": {"voice_id": "…", "model_id": "eleven_multilingual_v2", "voice_settings": {…}}
# Gesendet wird der Sprechertext ohne "|" und mit "aussprache"-Ersetzungen – dieselbe Regel wie sendeText() in render.mjs.
import base64, json, os, sys, subprocess

def sende_text(sprecher, aussprache):
    teile = sprecher.split('|')
    for i, t in enumerate(teile):
        for a, b in (aussprache or {}).items():
            t = t.replace(a, b)
        teile[i] = t
    return ' '.join(''.join(teile).split())

def texte(db):
    return [(i, sende_text(s['sprecher'], db.get('aussprache'))) for i, s in enumerate(db['szenen']) if s.get('sprecher')]

PS1 = r"""# KIMUTEC-Reel: Ansagen bei ElevenLabs holen (mit Wort-Zeiten). Start per Doppelklick auf "Stimme holen.cmd".
# Der Schluessel steht in elevenlabs.txt im selben Ordner und wird nur an ElevenLabs geschickt.
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ordner = Split-Path -Parent $MyInvocation.MyCommand.Path
$datei = Join-Path $ordner 'elevenlabs.txt'
if (-not (Test-Path $datei)) { Write-Host 'Die Datei elevenlabs.txt fehlt in diesem Ordner.' -ForegroundColor Red; exit 1 }
$key = (Get-Content $datei -Raw).Trim()
$ziel = Join-Path $ordner 'ton'
New-Item -ItemType Directory -Force -Path $ziel | Out-Null
$log = Join-Path $ziel 'protokoll.txt'
Set-Content -Path $log -Value ('Start ' + (Get-Date -Format s))
$url = '__URL__'
$nummern = @(__NUMMERN__)
$teile = @(
__TEILE__
)
$fehler = 0
for ($i = 0; $i -lt $teile.Count; $i++) {
  $nr = '{0:D2}' -f $nummern[$i]
  $anfrage = Join-Path $env:TEMP ('kimutec_anfrage_' + $nr + '.json')
  [IO.File]::WriteAllBytes($anfrage, [Convert]::FromBase64String($teile[$i]))
  $aus = Join-Path $ziel ('s' + $nr + '.json')
  Write-Host ('Ansage ' + ($i + 1) + ' von ' + $teile.Count + ' ...')
  try {
    Invoke-WebRequest -Uri $url -Method Post -Headers @{ 'xi-api-key' = $key } -ContentType 'application/json' -InFile $anfrage -OutFile $aus -UseBasicParsing
    Add-Content -Path $log -Value ('s' + $nr + ' ok')
  } catch {
    $fehler++
    $text = $_.Exception.Message
    try { $r = $_.Exception.Response; if ($r) { $sr = New-Object IO.StreamReader($r.GetResponseStream()); $text = $text + ' | ' + $sr.ReadToEnd() } } catch {}
    Add-Content -Path $log -Value ('s' + $nr + ' FEHLER: ' + $text)
    Write-Host ('Fehler bei Ansage ' + $nr + ': ' + $text) -ForegroundColor Red
    if (Test-Path $aus) { Remove-Item $aus }
    if ($text -match '401|403|invalid|quota|not_found|voice') { break }
  }
  Remove-Item $anfrage -ErrorAction SilentlyContinue
}
if ($fehler -eq 0) { Write-Host 'Fertig! Alle Ansagen liegen im Ordner ton. Sag Claude Bescheid.' -ForegroundColor Green }
else { Write-Host 'Es gab Fehler (siehe ton\protokoll.txt). Sag Claude Bescheid.' -ForegroundColor Yellow }
"""

CMD = '@echo off\r\ncd /d "%~dp0"\r\npowershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stimme_holen.ps1"\r\necho.\r\npause\r\n'

def skript(db_pfad, aus):
    db = json.load(open(db_pfad, encoding='utf-8'))
    e = db['elevenlabs']
    tx = texte(db)
    teile, nummern = [], []
    for j, (i, t) in enumerate(tx):
        body = {'text': t, 'model_id': e.get('model_id', 'eleven_multilingual_v2'), 'voice_settings': e.get('voice_settings', {}), 'seed': e.get('seed', 4711)}
        if j > 0:
            body['previous_text'] = tx[j - 1][1]
        if j < len(tx) - 1:
            body['next_text'] = tx[j + 1][1]
        teile.append("'" + base64.b64encode(json.dumps(body, ensure_ascii=False).encode('utf-8')).decode('ascii') + "'")
        nummern.append(str(i + 1))
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{e['voice_id']}/with-timestamps?output_format={e.get('output_format', 'mp3_44100_128')}"
    ps = PS1.replace('__URL__', url).replace('__NUMMERN__', ','.join(nummern)).replace('__TEILE__', ',\n'.join(teile))
    os.makedirs(aus, exist_ok=True)
    open(os.path.join(aus, 'stimme_holen.ps1'), 'w', encoding='ascii', newline='\r\n').write(ps)
    open(os.path.join(aus, 'Stimme holen.cmd'), 'w', encoding='ascii', newline='').write(CMD)
    zeichen = sum(len(t) for _, t in tx)
    print(f'{len(tx)} Ansagen, {zeichen} Zeichen → {aus}')

def pruefen(db_pfad):
    db = json.load(open(db_pfad, encoding='utf-8'))
    ordner = os.path.join(os.path.dirname(db_pfad), db.get('tonOrdner', 'ton'))
    ok = True
    gesamt = 0.0
    for i, t in texte(db):
        f = os.path.join(ordner, f's{i+1:02d}.json')
        if not os.path.exists(f):
            print(f'Szene {i+1}: fehlt'); ok = False; continue
        d = json.load(open(f, encoding='utf-8'))
        al = d.get('alignment') or {}
        gleich = ''.join(al.get('characters', [])) == t
        mp3 = f[:-5] + '.mp3'
        open(mp3, 'wb').write(base64.b64decode(d['audio_base64']))
        dauer = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3], capture_output=True, text=True).stdout)
        gesamt += dauer
        print(f"Szene {i+1}: {dauer:5.1f} s  Text {'stimmt' if gleich else 'WEICHT AB'}")
        ok &= gleich
    print(f'Sprechzeit gesamt: {gesamt:.1f} s')
    return ok

# ---------- Eine fertige MP3 (alle Szenen am Stück, z. B. aus dem ElevenLabs-Connector) in Szenen zerlegen ----------
# python3 reels/elevenlabs.py zerlegen <ganz.mp3> <drehbuch.json>
# Spracherkennung (Parakeet, sherpa-onnx) liefert Wortzeiten, die auf den Sprechertext ausgerichtet werden.
# Ergebnis: ton/s01.json … im selben Format wie ElevenLabs „with-timestamps“ – render.mjs merkt keinen Unterschied.
ZAHLEN = {'eins': '1', 'zwei': '2', 'drei': '3', 'vier': '4', 'fünf': '5', 'sechs': '6', 'sieben': '7', 'acht': '8', 'neun': '9', 'zehn': '10'}

def _norm(w):
    import re
    w = re.sub(r'[^0-9a-zäöüß]', '', w.lower())
    return ZAHLEN.get(w, w)

def _erkenner():
    import sherpa_onnx
    name = 'sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8'
    ordner = os.path.expanduser(f'~/.cache/sherpa/{name}')
    if not os.path.isdir(ordner):
        os.makedirs(os.path.dirname(ordner), exist_ok=True)
        subprocess.run(f'curl -sSfL https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{name}.tar.bz2 | tar xj -C "{os.path.dirname(ordner)}"', shell=True, check=True)
    p = lambda f: os.path.join(ordner, f)
    return sherpa_onnx.OfflineRecognizer.from_transducer(encoder=p('encoder.int8.onnx'), decoder=p('decoder.int8.onnx'), joiner=p('joiner.int8.onnx'),
                                                         tokens=p('tokens.txt'), model_type='nemo_transducer', num_threads=os.cpu_count() or 2)

def _woerter(ton, sr=16000):
    """Erkannte Wörter mit Start- und Endzeit; geschnitten wird an leisen Stellen etwa alle 14 s."""
    import numpy as np
    f = int(.1 * sr)
    pegel = np.sqrt(np.convolve(ton ** 2, np.ones(f) / f, 'same'))
    schnitte, pos = [0], 0
    while pos + 17 * sr < len(ton):
        a, b = pos + 11 * sr, pos + 17 * sr
        pos = a + int(np.argmin(pegel[a:b])); schnitte.append(pos)
    schnitte.append(len(ton))
    erk, w = _erkenner(), []
    for a, b in zip(schnitte, schnitte[1:]):
        st = erk.create_stream(); st.accept_waveform(sr, ton[a:b]); erk.decode_stream(st)
        r = st.result
        for tok, t0, du in zip(r.tokens, r.timestamps, r.durations or [0.08] * len(r.tokens)):
            t0 += a / sr
            if tok.startswith(' ') or not w or w[-1][3]:
                w.append([tok.strip(), t0, t0 + du, False])
            else:
                w[-1][0] += tok; w[-1][2] = t0 + du
        if w: w[-1][3] = True   # Abschnittsende: nächstes Token beginnt ein neues Wort
    return [(x[0], x[1], x[2]) for x in w], pegel

def _ausrichten(skript, erkannt):
    """Needleman-Wunsch auf normalisierten Wörtern (ähnliche Wörter zählen als Treffer, z. B. Kimutek/Chimotec)."""
    from difflib import SequenceMatcher
    n, m = len(skript), len(erkannt)
    sk, er = [_norm(x) for x in skript], [_norm(x[0]) for x in erkannt]
    def wert(i, j):
        if sk[i] == er[j]: return 2.0
        r = SequenceMatcher(None, sk[i], er[j]).ratio()
        return 1.0 if r >= .6 else -1.0
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): D[i][0] = -i
    for j in range(1, m + 1): D[0][j] = -j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = max(D[i-1][j-1] + wert(i-1, j-1), D[i-1][j] - 1, D[i][j-1] - 1)
    paar, i, j = {}, n, m
    while i > 0 and j > 0:
        if D[i][j] == D[i-1][j-1] + wert(i-1, j-1):
            if wert(i-1, j-1) > 0: paar[i-1] = j-1
            i, j = i - 1, j - 1
        elif D[i][j] == D[i-1][j] - 1: i -= 1
        else: j -= 1
    return paar

def zerlegen(mp3, db_pfad, nur=None):
    """nur = Liste von Szenennummern (1-basiert): die MP3 enthält nur diese Szenen, die übrigen Ansagen bleiben unverändert."""
    import numpy as np
    db = json.load(open(db_pfad, encoding='utf-8'))
    tx = [x for x in texte(db) if not nur or x[0] + 1 in nur]
    roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    ton = np.frombuffer(roh, np.int16).astype(np.float32) / 32768
    erkannt, pegel = _woerter(ton)
    skript, wo = [], []                       # alle Skriptwörter, dazu (Szene, Wortnummer)
    for k, (i, t) in enumerate(tx):
        for n, w in enumerate(t.split(' ')):
            skript.append(w); wo.append((k, n))
    paar = _ausrichten(skript, erkannt)
    start = [None] * len(skript)
    for a, b in paar.items(): start[a] = erkannt[b][1]
    # Lücken (nicht erkannte Wörter) linear füllen
    bek = [i for i, s in enumerate(start) if s is not None]
    for i in range(len(start)):
        if start[i] is None:
            vor = max([x for x in bek if x < i], default=None); nach = min([x for x in bek if x > i], default=None)
            if vor is None: start[i] = start[nach]
            elif nach is None: start[i] = start[vor] + .35 * (i - vor)
            else: start[i] = start[vor] + (start[nach] - start[vor]) * (i - vor) / (nach - vor)
    ordner = os.path.join(os.path.dirname(db_pfad), db.get('tonOrdner', 'ton'))
    os.makedirs(ordner, exist_ok=True)
    gesamt = len(ton) / 16000
    print(f'Erkannt: {len(erkannt)} Wörter, ausgerichtet: {len(paar)} von {len(skript)}')
    for k, (i, t) in enumerate(tx):
        idx = [x for x, (kk, _) in enumerate(wo) if kk == k]
        a = max(0.0, start[idx[0]] - .12)
        naechster = start[idx[-1] + 1] - .08 if idx[-1] + 1 < len(start) else gesamt
        # Ende der Stimme: letzter lauter Abschnitt vor dem Anfang der nächsten Szene. Nicht die erste Pause nach dem
        # letzten erkannten Wort nehmen – Sätze haben Pausen (z. B. „Kimu-Tek … Punkt com“), sonst fehlt das Satzende.
        p0 = int(start[idx[-1]] * 16000)
        grenze = int(min(naechster - (.15 if idx[-1] + 1 < len(start) else 0), gesamt) * 16000)
        leise = pegel < max(.012, float(np.percentile(pegel, 30)) * 1.5)
        laut = np.nonzero(~leise[p0:grenze])[0] if grenze > p0 else []
        ende = min(naechster, (p0 + int(laut[-1])) / 16000 + .18) if len(laut) else min(naechster, start[idx[-1]] + .6)
        seg = os.path.join(ordner, f's{i+1:02d}.mp3')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-to', f'{ende:.3f}', '-i', mp3, '-c:a', 'libmp3lame', '-b:a', '192k', seg], check=True)
        # Zeichen-Zeitleiste: jedes Zeichen bekommt den Start seines Wortes (Leerzeichen den des nächsten)
        woerter = t.split(' '); zeiten, ch = [], []
        for n, w in enumerate(woerter):
            ts = round(start[idx[n]] - a, 3)
            if n: ch.append(' '); zeiten.append(ts)
            for c in w: ch.append(c); zeiten.append(ts)
        json.dump({'audio_base64': base64.b64encode(open(seg, 'rb').read()).decode('ascii'),
                   'alignment': {'characters': ch, 'character_start_times_seconds': zeiten, 'character_end_times_seconds': zeiten},
                   'quelle': os.path.basename(mp3), 'von': round(a, 3), 'bis': round(ende, 3)},
                  open(os.path.join(ordner, f's{i+1:02d}.json'), 'w', encoding='utf-8'))
        treffer = sum(1 for x in idx if x in paar)
        print(f'Szene {i+1}: {a:6.2f}–{ende:6.2f} s ({ende-a:4.1f} s)  {treffer}/{len(idx)} Wörter erkannt')
    print('Gesprochen (zum Gegenlesen):', ' '.join(x[0] for x in erkannt))

if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'skript':
        skript(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == 'pruefen':
        sys.exit(0 if pruefen(sys.argv[2]) else 1)
    elif len(sys.argv) >= 4 and sys.argv[1] == 'zerlegen':
        nur = [int(x) for a in sys.argv[4:] if a.startswith('--szenen=') for x in a[9:].split(',')]
        zerlegen(sys.argv[2], sys.argv[3], nur or None)
    else:
        print('Aufruf: elevenlabs.py skript <drehbuch> <ordner> | pruefen <drehbuch> | zerlegen <mp3> <drehbuch> [--szenen=1,5]')
