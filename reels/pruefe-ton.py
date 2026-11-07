# Schreibt mit, was im Reel gesprochen wird (zum Prüfen von Aussprache und Timing).
# Aufruf: python3 reels/pruefe-ton.py reels/projekte/<name>/reel.mp4
import subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
ton = np.frombuffer(roh, np.int16).astype(np.float32) / 32768
modell = WhisperModel('small', device='cpu', compute_type='int8')
teile, _ = modell.transcribe(ton, language='de', beam_size=5)
for t in teile:
    print(f'{t.start:5.1f}–{t.end:5.1f}  {t.text.strip()}')
