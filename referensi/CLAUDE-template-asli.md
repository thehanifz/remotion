Template CLAUDE.md — simpan file ini dengan nama CLAUDE.md di folder utama project kamu.

# CLAUDE.md — Editor Video AI
(Ganti semua tulisan dalam [ ] dengan isi channel kamu)

## Tentang project
Channel: [tema channel]. Bahasa: Indonesia.
Penonton: [siapa penontonnya].

## Struktur folder
proyek-video/
├─ CLAUDE.md          file aturan ini
├─ naskah/            naskah .md, nama = nama video
├─ raw-footage/       video mentah, JANGAN diubah/dihapus
├─ references/        video contoh gaya, hanya dianalisis
├─ assets/
│  ├─ vo/             suara (mp3 ElevenLabs)
│  ├─ bahan_video/    screenshot PNG, ikon SVG
│  └─ (logo, font, musik, SFX)
├─ tools/             semua script buatan Claude
│  └─ remotion/       project animasi
├─ work/              file sementara, boleh dihapus
│  └─ day1/, day2/    satu folder per video
└─ export/            hanya video final
   └─ thumbnail/      cover JPG
Nama klip: 01_topik_keterangan.mp4

## Spesifikasi export
- 1920x1080 (Reels/Shorts 1080x1920), 30 fps
- H.264 CRF 18, yuv420p
- Audio AAC 48 kHz, -14 LUFS, true peak -1 dBTP
- Nama file: YYYY-MM-DD_judul-singkat_v01.mp4

## Gaya visual
- Warna: [kode warna]
- Font judul: [font]. Font caption: [font]
- Transisi: cut biasa

## Caption
- faster-whisper, language="id", model large-v3
- Maks 2 baris, 42 karakter per baris
- Simpan .srt di work/
- Koreksi istilah pakai glosarium

## Glosarium
[istilah khusus channel kamu, pisahkan koma]
Claude, Claude Code, Remotion, faster-whisper, ElevenLabs

## Aturan keamanan (WAJIB)
- Blur wajah tanpa izin, plat nomor, layar/dokumen
- Tanya dulu sebelum menampilkan angka/data
- Jangan tampilkan logo/nama klien tanpa izin

## Alur kerja
1. Baca naskah. Belum ada? Tanya dulu.
2. Cek footage (ffprobe): durasi, resolusi, fps
3. Potong jeda (auto-editor) ke work/
4. Buat caption, koreksi glosarium
5. Cocokkan transkrip dengan naskah
6. Usulkan timeline, TUNGGU persetujuan saya
7. Susun di Remotion
8. Normalisasi audio -14 LUFS
9. Render ke export/
10. Laporkan durasi, ukuran file, bagian yang di-blur

## Cara kerja
- Jelaskan singkat setiap perintah
- Tanya dulu sebelum menghapus file di luar work/
