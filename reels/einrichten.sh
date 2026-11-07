#!/usr/bin/env bash
# Richtet alles für Reels ein: deutsche Stimme (Piper) und Spracherkennung zum Prüfen.
# Braucht: python3, ffmpeg, node, Playwright mit Chromium (in Claude-Cloud-Sessions vorhanden).
set -euo pipefail
pip install -q piper-tts faster-whisper
STIMME="${1:-de_DE-thorsten-high}"
mkdir -p "$HOME/.cache/piper"
cd "$HOME/.cache/piper"
basis="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/${STIMME#de_DE-}"
basis="${basis%-*}/${STIMME##*-}"
for f in "$STIMME.onnx" "$STIMME.onnx.json"; do
  [ -s "$f" ] || curl -sSfL -o "$f" "$basis/$f"
done
echo "Fertig: Stimme $STIMME in $HOME/.cache/piper"
