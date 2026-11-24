#!/usr/bin/env python3
"""Sinkronkan durasi frame pada 03-storyboard.json dengan durasi asli audio VO eksternal via ffprobe."""

import argparse
import json
import math
import os
import subprocess
import sys


def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync storyboard scene durations to external VO audio duration.")
    parser.add_argument("--storyboard", required=True, help="Path to 03-storyboard.json")
    parser.add_argument("--audio", required=True, help="Path to external VO audio (.mp3 or .wav)")
    parser.add_argument("--tail-padding-sec", type=float, default=0.6, help="Extra ending buffer in seconds")
    args = parser.parse_args()

    if not os.path.isfile(args.storyboard):
        print(f"ERROR: Storyboard not found: {args.storyboard}", file=sys.stderr)
        return 1
    if not os.path.isfile(args.audio):
        print(f"ERROR: Audio file not found: {args.audio}", file=sys.stderr)
        return 1

    duration_sec = get_audio_duration(args.audio) + args.tail_padding_sec

    with open(args.storyboard, "r", encoding="utf-8") as f:
        data = json.load(f)

    fps = int(data.get("meta", {}).get("fps", 30))
    target_total_frames = max(fps, math.ceil(duration_sec * fps))
    scenes = data.get("scenes", [])
    if not scenes:
        print("ERROR: No scenes found in storyboard.", file=sys.stderr)
        return 1

    orig_total = sum(int(s.get("durationInFrames", fps * 5)) for s in scenes)
    if orig_total <= 0:
        orig_total = len(scenes) * fps * 5

    current_frame = 0
    for idx, scene in enumerate(scenes):
        orig_dur = int(scene.get("durationInFrames", fps * 5))
        if idx == len(scenes) - 1:
            new_dur = max(fps, target_total_frames - current_frame)
        else:
            new_dur = max(fps, round(orig_dur * (target_total_frames / orig_total)))
        scene["startFrame"] = current_frame
        scene["durationInFrames"] = new_dur
        current_frame += new_dur

    data.setdefault("meta", {})["totalDurationInFrames"] = current_frame
    data.setdefault("audio", {})["voiceoverFile"] = f"assets/{os.path.basename(args.audio)}"

    with open(args.storyboard, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(
        f"OK: Synced {len(scenes)} scenes to {duration_sec:.2f}s "
        f"({current_frame} frames @ {fps}fps) -> {args.storyboard}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
