#!/usr/bin/env bash
set -euo pipefail

# Integrasi aset episode + 03-storyboard.json ke proyek Remotion yang sudah ada dan render ke MP4.
# Pemakaian: bash scripts/render_remotion.sh <EPISODE_DIR> <REMOTION_PROJECT_DIR> [COMPOSITION_ID]

EPISODE_DIR="${1:-}"
REMOTION_DIR="${2:-${REMOTION_PROJECT_DIR:-}}"
COMPOSITION_ID="${3:-AnimeNewsVideo}"

if [[ -z "$EPISODE_DIR" || -z "$REMOTION_DIR" ]]; then
  echo "Usage: bash scripts/render_remotion.sh <EPISODE_DIR> <REMOTION_PROJECT_DIR> [COMPOSITION_ID]" >&2
  exit 1
fi

STORYBOARD_PATH="$EPISODE_DIR/03-storyboard.json"
if [[ ! -f "$STORYBOARD_PATH" ]]; then
  echo "ERROR: Storyboard not found at $STORYBOARD_PATH" >&2
  exit 1
fi

if [[ ! -d "$REMOTION_DIR" ]]; then
  echo "ERROR: Remotion project directory not found: $REMOTION_DIR" >&2
  exit 1
fi

EPISODE_ID="$(basename "$EPISODE_DIR")"
PUBLIC_EPISODE_DIR="$REMOTION_DIR/public/episodes/$EPISODE_ID"
OUTPUT_DIR="$EPISODE_DIR/output"
RENDER_PROPS_PATH="$OUTPUT_DIR/remotion-props.json"
OUTPUT_MP4="$OUTPUT_DIR/final-video.mp4"

mkdir -p "$PUBLIC_EPISODE_DIR" "$OUTPUT_DIR"

# Salin semua aset (PNG + audio VO) ke folder public Remotion dan buat props JSON dengan path staticFile()
python3 - "$STORYBOARD_PATH" "$EPISODE_DIR" "$PUBLIC_EPISODE_DIR" "$EPISODE_ID" "$RENDER_PROPS_PATH" <<'PYEOF'
import json
import os
import shutil
import sys

storyboard_path, episode_dir, public_dir, episode_id, props_out = sys.argv[1:6]

with open(storyboard_path, "r", encoding="utf-8") as f:
    sb = json.load(f)

missing = []

def stage_file(src_path: str) -> str:
    if not src_path:
        return ""
    candidates = [
        src_path,
        os.path.join(episode_dir, src_path),
        os.path.abspath(src_path),
    ]
    found = next((c for c in candidates if os.path.isfile(c)), None)
    if not found:
        missing.append(src_path)
        return src_path
    fname = os.path.basename(found)
    dst = os.path.join(public_dir, fname)
    shutil.copy2(found, dst)
    return f"episodes/{episode_id}/{fname}"

vo_file = sb.get("audio", {}).get("voiceoverFile", "")
if vo_file:
    sb["audio"]["voiceoverFile"] = stage_file(vo_file)

for scene in sb.get("scenes", []):
    for layer in scene.get("layers", []):
        if layer.get("filePath"):
            layer["filePath"] = stage_file(layer["filePath"])

if missing:
    print("ERROR: Missing asset files referenced in storyboard:", file=sys.stderr)
    for m in missing:
        print(f"  - {m}", file=sys.stderr)
    sys.exit(2)

with open(props_out, "w", encoding="utf-8") as f:
    json.dump({"storyboard": sb}, f, indent=2, ensure_ascii=False)

print(f"OK: Staged assets to {public_dir} and wrote {props_out}")
PYEOF

echo "Rendering Remotion composition '$COMPOSITION_ID' -> $OUTPUT_MP4"
(
  cd "$REMOTION_DIR"
  npx remotion render "$COMPOSITION_ID" "$(realpath "$OUTPUT_MP4")" --props="$(realpath "$RENDER_PROPS_PATH")"
)

if [[ ! -s "$OUTPUT_MP4" ]]; then
  echo "ERROR: Render finished but output MP4 is missing or empty: $OUTPUT_MP4" >&2
  exit 3
fi

echo "SUCCESS: Video rendered -> $OUTPUT_MP4"
