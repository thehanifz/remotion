#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
cd /root/main-app/remotion

OUTPUT_DIR="out"
mkdir -p "$OUTPUT_DIR"
FINAL_FILE="$OUTPUT_DIR/2026-11-14_carrick-dipecat_v01.mp4"

echo "=== MEMULAI RENDER REMOTION ==="
echo "Composition: CarrickVideo"
echo "Output: $FINAL_FILE"

npx remotion render src/index.ts CarrickVideo "$FINAL_FILE" --crf=18 --pixel-format=yuv420p

if [ -f "$FINAL_FILE" ]; then
  echo "=== RENDER BERHASIL ==="
  ls -lh "$FINAL_FILE"
  echo "=== NORMALISASI AUDIO -14 LUFS ==="
  ffmpeg -y -i "$FINAL_FILE" -af "loudnorm=I=-14:TP=-1:LRA=11" -c:v copy -c:a aac -b:a 192k -ar 48000 "$OUTPUT_DIR/2026-11-14_carrick-dipecat_v01_lufs.mp4"
  if [ -f "$OUTPUT_DIR/2026-11-14_carrick-dipecat_v01_lufs.mp4" ]; then
    mv "$OUTPUT_DIR/2026-11-14_carrick-dipecat_v01_lufs.mp4" "$FINAL_FILE"
    echo "Audio berhasil dinormalisasi ke -14 LUFS!"
  fi
  ls -lh "$FINAL_FILE"
fi
