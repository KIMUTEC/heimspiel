# Natürliche KI-Stimme (Chatterbox, läuft lokal) für mehrere Ansagen auf einmal.
# Aufruf (mit der Python-Umgebung, in der chatterbox-tts und faster-whisper installiert sind):
#   python stimme_chatterbox.py <auftrag.json> <ergebnis.json>
# auftrag.json: {"texte": ["Text mit |Marken", …], "ordner": "…", "referenz": "stimme.wav" (optional, Stimme klonen)}
# ergebnis.json: [{"wav": "…", "marken": [Sekunden …], "treffer": 0.97}, …]
#
# Ablauf je Text: erzeugen → mit Spracherkennung Wortzeiten holen → angehängte Silben abschneiden →
# bei schlechter Übereinstimmung mit anderem Zufallswert neu erzeugen (bis zu 4 Versuche, bester gewinnt).
import json, re, sys, difflib
import numpy as np, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel

auftrag, ziel = sys.argv[1:3]
a = json.load(open(auftrag))
ZAHL = {'1': 'eins', '2': 'zwei', '3': 'drei', '4': 'vier', '5': 'fünf', '6': 'sechs', '7': 'sieben', '8': 'acht', '9': 'neun', '10': 'zehn'}
def norm(w):
    w = re.sub(r'[^0-9a-zäöüß]', '', w.lower())
    return ZAHL.get(w, w)

tts = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
asr = WhisperModel('small', device='cpu', compute_type='int8')
sr = tts.sr

def wortzeiten(wav):
    ton = ta.functional.resample(wav, sr, 16000)[0].numpy().astype(np.float32)
    teile, _ = asr.transcribe(ton, language='de', word_timestamps=True, beam_size=5)
    return [(norm(w.word), w.start, w.end) for s in teile for w in s.words if norm(w.word)]

ergebnis = []
for i, roh in enumerate(a['texte']):
    teile = roh.split('|')
    text = ' '.join(' '.join(teile).split())
    tokens = [norm(w) for w in text.split() if norm(w)]
    vor, n = [], 0
    for t in teile[:-1]:
        n += len([w for w in t.split() if norm(w)]); vor.append(n)
    bestes = None
    for versuch in range(4):
        torch.manual_seed(1000 * i + versuch)
        kw = dict(language_id='de', exaggeration=0.5, cfg_weight=0.5)
        if a.get('referenz'): kw['audio_prompt_path'] = a['referenz']
        wav = tts.generate(text, **kw)
        wz = wortzeiten(wav)
        sm = difflib.SequenceMatcher(a=tokens, b=[w for w, _, _ in wz], autojunk=False)
        zuord = {}
        for blk in sm.get_matching_blocks():
            for k in range(blk.size): zuord[blk.a + k] = blk.b + k
        treffer = len(zuord) / max(1, len(tokens))
        # Ende = letztes erkanntes Wort, das zum Text gehört (dahinter angehängte Silben abschneiden)
        if zuord:
            letzt = wz[zuord[max(zuord)]][2]
            # gibt es nach dem letzten Textwort noch erkannte Wörter, ist das ein Anhängsel
            ende = min(wav.shape[-1] / sr, letzt + 0.25)
        else:
            ende = wav.shape[-1] / sr
        if bestes is None or treffer > bestes[0]:
            bestes = (treffer, wav, wz, zuord, ende)
        print(f'Ansage {i+1}: Versuch {versuch+1}, Übereinstimmung {treffer:.0%}', flush=True)
        if treffer >= 0.95: break
    treffer, wav, wz, zuord, ende = bestes
    def zeit(k):  # Startzeit von Text-Wort k, fehlende Wörter aus Nachbarn schätzen
        if k in zuord: return wz[zuord[k]][1]
        vorher = [j for j in zuord if j < k]; nachher = [j for j in zuord if j > k]
        if vorher and nachher:
            a0, a1 = max(vorher), min(nachher)
            t0, t1 = wz[zuord[a0]][1], wz[zuord[a1]][1]
            return t0 + (t1 - t0) * (k - a0) / (a1 - a0)
        return wz[zuord[max(vorher)]][2] if vorher else 0.0
    marken = [round(zeit(k), 3) for k in vor]
    stueck = wav[:, : int(ende * sr)]
    # weich ausblenden
    f = min(stueck.shape[-1], int(0.08 * sr)); stueck[:, -f:] *= torch.linspace(1, 0, f)
    pfad = a['ziele'][i] + '.wav' if a.get('ziele') else f"{a['ordner']}/cb_{i}.wav"
    ta.save(pfad, stueck, sr)
    erg = {'wav': pfad, 'marken': marken, 'treffer': round(treffer, 3), 'text': roh}
    if a.get('ziele'):   # sofort speichern: ein Abbruch verliert keine fertigen Ansagen
        json.dump(erg, open(a['ziele'][i] + '.json', 'w'))
    ergebnis.append(erg)
json.dump(ergebnis, open(ziel, 'w'))
