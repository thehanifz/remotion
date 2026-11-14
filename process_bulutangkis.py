import json
import subprocess
import sys
import os
import shutil
import re

RAW_AUDIO = "/root/main-app/remotion/raw/bulutangkis.mp3"
PUBLIC_AUDIO = "/root/main-app/remotion/public/narasi/bulutangkis.mp3"
WORK_DIR = "/root/main-app/remotion/work"
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs("/root/main-app/remotion/public/narasi", exist_ok=True)

# Copy to public/narasi if not exists or if different
shutil.copy2(RAW_AUDIO, PUBLIC_AUDIO)
print(f"Disalin ke {PUBLIC_AUDIO}")

print("\n=== 1. FFPROBE INFO ===")
try:
    probe = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,bit_rate:stream=codec_name,sample_rate,channels",
        "-of", "json",
        PUBLIC_AUDIO
    ]).decode()
    probe_data = json.loads(probe)
    duration = float(probe_data["format"]["duration"])
    print(f"Durasi: {duration:.2f} detik ({duration*30:.0f} frames @ 30fps)")
    print(f"Stream: {probe_data.get('streams', [{}])[0]}")
    print(f"Format: {probe_data.get('format', {})}")
except Exception as e:
    print(f"Gagal ffprobe: {e}")

print("\n=== 2. DETEKSI JEDA / SILENCE ===")
try:
    cmd = [
        "ffmpeg", "-i", PUBLIC_AUDIO,
        "-af", "silencedetect=noise=-30dB:d=0.25",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    silence_starts = [float(x) for x in re.findall(r"silence_start: ([\d\.]+)", res.stderr)]
    silence_ends = [float(x) for x in re.findall(r"silence_end: ([\d\.]+)", res.stderr)]
    for s, e in zip(silence_starts, silence_ends):
        print(f"Jeda: {s:.2f}s -> {e:.2f}s (durasi: {e-s:.2f}s)")
except Exception as e:
    print(f"Gagal deteksi silence: {e}")

print("\n=== 3. WHISPER TRANSKRIP (large-v3, id, word_timestamps) ===")
try:
    from faster_whisper import WhisperModel
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"Device Whisper: {device} ({compute_type})")

    model = WhisperModel("large-v3", device=device, compute_type=compute_type)
    segments, info = model.transcribe(PUBLIC_AUDIO, language="id", word_timestamps=True)

    results = []
    print(f"Bahasa terdeteksi: {info.language} ({info.language_probability:.2f})")

    # Glosarium replacer
    GLOSSARY_MAP = {
        r"(?i)\bkaohsiung\b": "Kaohsiung",
        r"(?i)\bkaosiung\b": "Kaohsiung",
        r"(?i)\bgaoxiong\b": "Kaohsiung",
        r"(?i)\bmutiara ayu\b": "Mutiara Ayu",
        r"(?i)\blo sin yan\b": "Lo Sin Yan",
        r"(?i)\bloh sin yan\b": "Lo Sin Yan",
        r"(?i)\bisyana\b": "Isyana",
        r"(?i)\brinjani\b": "Rinjani",
        r"(?i)\byuan chi liao\b": "Yuan Chi Liao",
        r"(?i)\bong dan ting\b": "Ong dan Ting",
        r"(?i)\bong & ting\b": "Ong & Ting",
    }

    for segment in segments:
        text = segment.text.strip()
        for pattern, replacement in GLOSSARY_MAP.items():
            text = re.sub(pattern, replacement, text)

        words = []
        if segment.words:
            for w in segment.words:
                w_text = w.word
                for pattern, replacement in GLOSSARY_MAP.items():
                    w_text = re.sub(pattern, replacement, w_text)
                words.append({
                    "word": w_text,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                })

        results.append({
            "id": segment.id,
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": text,
            "words": words
        })
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s]: {text}")

    # Save json
    out_json = f"{WORK_DIR}/transcript_bulutangkis.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nTranskrip berhasil disimpan ke {out_json}")

    # Generate SRT
    def format_srt_time(sec):
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        millis = int((sec - int(sec)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    out_srt = f"{WORK_DIR}/bulutangkis.srt"
    with open(out_srt, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(results, 1):
            f.write(f"{idx}\n")
            f.write(f"{format_srt_time(seg['start'])} --> {format_srt_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
    print(f"SRT berhasil disimpan ke {out_srt}")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error Whisper: {e}")
