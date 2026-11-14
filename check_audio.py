import subprocess
import json
import os

mp3_file = "/root/main-app/remotion/raw/ElevenLabs_2026-11-14T12_12_29_Zephlyn_pvc_s50_v3.mp3"
cmd = [
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration,bit_rate:stream=codec_name,sample_rate,channels",
    "-of", "json",
    mp3_file
]
res = subprocess.check_output(cmd).decode()
print("PROBE_RESULT:")
print(res)
