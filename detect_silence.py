import subprocess
import re
import json

audio_path = "/root/main-app/remotion/public/narasi/carrick.mp3"
fps = 30

# Run ffmpeg silencedetect
cmd = [
    "ffmpeg", "-i", audio_path,
    "-af", "silencedetect=noise=-28dB:d=0.25",
    "-f", "null", "-"
]

res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

silence_starts = [float(x) for x in re.findall(r"silence_start: ([\d\.]+)", res.stderr)]
silence_ends = [float(x) for x in re.findall(r"silence_end: ([\d\.]+)", res.stderr)]

print("=== SILENCE DETECTED ===")
for s, e in zip(silence_starts, silence_ends):
    print(f"Jeda: {s:.2f}s -> {e:.2f}s ({e-s:.2f}s)")

# Audio duration is 34.04s
total_dur = 34.04

# Calculate speech segments (between silences)
points = [0.0]
for s, e in zip(silence_starts, silence_ends):
    mid = (s + e) / 2.0
    points.append(mid)
points.append(total_dur)

print("\n=== TITIK POTONG (SPLIT POINTS) ===")
for i in range(len(points) - 1):
    start = points[i]
    end = points[i+1]
    dur = end - start
    frames = round(dur * fps)
    print(f"Bagian {i+1}: {start:.2f}s - {end:.2f}s | Durasi: {dur:.2f}s | Frames: {frames}")
