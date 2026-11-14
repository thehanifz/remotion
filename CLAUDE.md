# CLAUDE.md — Editor Video AI SkorNalar

## Tentang project
Channel: SkorNalar (@skornalar) — berita.thehanifz.my.id
Bahasa: Indonesia
Penonton: Penggemar olahraga Indonesia
Cakupan: Semua cabang olahraga — sepakbola luar negeri, sepakbola lokal (Liga 1 + Timnas Indonesia), bulutangkis, voli, basket, futsal, esports, sepakbola putri.

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
- Font judul: Montserrat Bold / Inter Bold (tegas, modern)
- Font caption: Inter (keterbacaan tinggi)
- Transisi: cut biasa (opsional: whip/zoom halus untuk momen penentu)
- Palet Warna per Cabang Olahraga:
  * **Sepakbola Luar**: Gradien `#08452b` → `#052618` | Pill `#14532d` | Label `#4ade80` | Aksen `#22c55e`
  * **Sepakbola Lokal (Liga 1 + Timnas)**: Gradien `#0a337a` → `#061f49` | Pill `#1565c0` | Label `#60a5fa` | Aksen `#1565c0`
  * **Sepakbola Putri**: Sama persis dengan Sepakbola Lokal (Gradien `#0a337a` → `#061f49`, Pill `#1565c0`, Label `#60a5fa`, Aksen `#1565c0`)
  * **Bulutangkis**: Gradien `#6a1215` → `#440b11` | Pill `#b91c1c` | Label `#f87171` | Aksen `#ef4444`
  * **Voli**: Gradien `#7c2d12` → `#431407` | Pill `#c2410c` | Label `#fdba74` | Aksen `#f97316`
  * **Basket**: Gradien `#744f05` → `#4e3805` | Pill `#a16207` | Label `#fcd34d` | Aksen `#f59e0b`
  * **Futsal**: Gradien `#134e4a` → `#042f2e` | Pill `#0f766e` | Label `#5eead4` | Aksen `#14b8a6`
  * **Esports**: Gradien `#580f58` → `#2d0625` | Pill `#a21caf` | Label `#e879f9` | Aksen `#c026d3`

## Caption
- faster-whisper, language="id", model large-v3
- Maks 2 baris, 42 karakter per baris
- Simpan .srt di work/
- Koreksi istilah pakai glosarium

## Glosarium
SkorNalar, thehanifz, Timnas Indonesia, Garuda, Liga 1, PSSI, FIFA, AFC, Premier League, Champions League, La Liga, Serie A, Bundesliga, BWF, All England, Thomas Cup, Uber Cup, Indonesia Open, IBL, NBA, FIBA, Proliga, FIVB, MPL, MDL, M-Series, Shin Tae-yong, Remotion, ElevenLabs, faster-whisper

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
