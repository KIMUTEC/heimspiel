# Schreibt mit, was im Reel gesprochen wird (zum Prüfen von Aussprache und Timing).
# Aufruf: python3 reels/pruefe-ton.py reels/projekte/<name>/reel.mp4
# Nutzt faster-whisper, wenn dessen Modell geladen werden kann. Sonst (z. B. in der Cloud ohne Hugging Face)
# Parakeet über sherpa-onnx; das Modell kommt von GitHub und wird in ~/.cache/sherpa gespeichert.
import os, subprocess, sys
import numpy as np

roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
ton = np.frombuffer(roh, np.int16).astype(np.float32) / 32768
SR = 16000

def mit_whisper():
    from faster_whisper import WhisperModel
    modell = WhisperModel('small', device='cpu', compute_type='int8')
    teile, _ = modell.transcribe(ton, language='de', beam_size=5)
    for t in teile:
        print(f'{t.start:5.1f}–{t.end:5.1f}  {t.text.strip()}')

def stille_schnitte(ziel=14.0, such=3.0):
    """Schnittpunkte in leisen Stellen, etwa alle `ziel` Sekunden (damit keine Wörter zerschnitten werden)."""
    fenster = int(.1 * SR)
    pegel = np.sqrt(np.convolve(ton ** 2, np.ones(fenster) / fenster, 'same'))
    schnitte, pos = [0], 0
    while pos + (ziel + such) * SR < len(ton):
        a, b = int(pos + (ziel - such) * SR), int(pos + (ziel + such) * SR)
        pos = a + int(np.argmin(pegel[a:b]))
        schnitte.append(pos)
    return schnitte + [len(ton)]

def mit_parakeet():
    import sherpa_onnx
    name = 'sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8'
    ordner = os.path.expanduser(f'~/.cache/sherpa/{name}')
    if not os.path.isdir(ordner):
        os.makedirs(os.path.dirname(ordner), exist_ok=True)
        url = f'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{name}.tar.bz2'
        print('Lade Spracherkennung von GitHub …', file=sys.stderr)
        subprocess.run(f'curl -sSfL "{url}" | tar xj -C "{os.path.dirname(ordner)}"', shell=True, check=True)
    p = lambda f: os.path.join(ordner, f)
    erk = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=p('encoder.int8.onnx'), decoder=p('decoder.int8.onnx'), joiner=p('joiner.int8.onnx'),
                                                        tokens=p('tokens.txt'), model_type='nemo_transducer', num_threads=os.cpu_count() or 2)
    s = stille_schnitte()
    for a, b in zip(s, s[1:]):
        st = erk.create_stream(); st.accept_waveform(SR, ton[a:b]); erk.decode_stream(st)
        print(f'{a/SR:5.1f}–{b/SR:5.1f}  {st.result.text.strip()}')

try:
    mit_whisper()
except Exception as fehler:
    print(f'(faster-whisper nicht nutzbar: {type(fehler).__name__} – nehme Parakeet)', file=sys.stderr)
    mit_parakeet()
