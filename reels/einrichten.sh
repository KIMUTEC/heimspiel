#!/usr/bin/env bash
# Richtet alles für Reels ein: Spracherkennung zum Prüfen (Parakeet über sherpa-onnx, Modell von GitHub)
# und – falls erreichbar – die lokalen Ersatzstimmen. Die eigentliche Stimme kommt von ElevenLabs (siehe reels/elevenlabs.py).
# Braucht: python3, ffmpeg, node, Playwright mit Chromium (in Claude-Cloud-Sessions vorhanden).
# Hinweis Cloud: Hugging Face, ElevenLabs und der Microsoft-Vorlesedienst sind dort gesperrt, GitHub und PyPI gehen.
set -uo pipefail
pip install -q --break-system-packages sherpa-onnx edge-tts piper-tts faster-whisper 2>/dev/null || pip install -q sherpa-onnx edge-tts piper-tts faster-whisper

# Spracherkennung für pruefe-ton.py (GitHub, ca. 650 MB)
mkdir -p "$HOME/.cache/sherpa"
asr=sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8
if [ ! -d "$HOME/.cache/sherpa/$asr" ]; then
  curl -sSfL "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/$asr.tar.bz2" | tar xj -C "$HOME/.cache/sherpa" \
    && echo "Spracherkennung: $HOME/.cache/sherpa/$asr" || echo "Spracherkennung konnte nicht geladen werden"
fi

# Piper-Stimme (nur Notlösung, klingt künstlich) – von Hugging Face, in der Cloud meist gesperrt
STIMME="${1:-de_DE-thorsten-high}"
mkdir -p "$HOME/.cache/piper" && cd "$HOME/.cache/piper"
basis="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/${STIMME#de_DE-}"
basis="${basis%-*}/${STIMME##*-}"
for f in "$STIMME.onnx" "$STIMME.onnx.json"; do
  [ -s "$f" ] || curl -sSfL -o "$f" "$basis/$f" 2>/dev/null || { rm -f "$f"; echo "Piper-Stimme nicht erreichbar (egal, Standard ist ElevenLabs)"; break; }
done
echo "Fertig."
