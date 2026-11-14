import json
import subprocess
import sys
import os

AUDIO_PATH = "/root/main-app/remotion/public/narasi/carrick.mp3"
WORK_DIR = "/root/main-app/remotion/work"
os.makedirs(WORK_DIR, exist_ok=True)

print("=== 1. FFPROBE INFO ===")
try:
    probe = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,bit_rate:stream=codec_name,sample_rate,channels",
        "-of", "json",
        AUDIO_PATH
    ]).decode()
    probe_data = json.loads(probe)
    duration = float(probe_data["format"]["duration"])
    print(f"Durasi: {duration:.2f} detik ({duration*30:.0f} frames @ 30fps)")
    print(f"Format: {json.dumps(probe_data, indent=2)}")
except Exception as e:
    print(f"Gagal ffprobe: {e}")

print("\n=== 2. WHISPER TRANSKRIP DENGAN TIMESTAMPS ===")
try:
    from faster_whisper import WhisperModel
    model = WhisperModel("large-v3", device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu", compute_type="float16" if os.environ.get("CUDA_VISIBLE_DEVICES") else "int8")
    segments, info = model.transcribe(AUDIO_PATH, language="id", word_timestamps=True)
    results = []
    print(f"Bahasa terdeteksi: {info.language} ({info.language_probability:.2f})")
    for segment in segments:
        words = []
        if segment.words:
            for w in segment.words:
                words.append({"word": w.word, "start": w.start, "end": w.end, "probability": w.probability})
        results.append({
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "words": words
        })
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s]: {segment.text.strip()}")

    with open(f"{WORK_DIR}/transcript.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nTranskrip berhasil disimpan ke {WORK_DIR}/transcript.json")
except Exception as e:
    print(f"Catatan whisper: {e}")
