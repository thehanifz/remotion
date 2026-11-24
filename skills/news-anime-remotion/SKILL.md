---
name: news-anime-remotion
description: Ubah artikel berita dari URL mana saja menjadi video animasi pendek 9:16 siap unggah (MP4). Alur terbaru: gambar dibuat di Google Flow (karakter dari foto asli + adegan per penjelasan), semua editing dan perakitan dilakukan Muse di Remotion — storyboard JSON, sinkronisasi durasi ke VO, render otomatis. Gunakan skill ini setiap kali pengguna memberikan tautan berita, meminta pembuatan video animasi berita sampai jadi MP4, atau meminta lanjut render setelah audio voiceover selesai dibuat.
---

# news-anime-remotion

Ubah artikel berita dari URL web mana saja menjadi video animasi pendek 9:16 (**final-video.mp4**) bergaya **Anime 2D dinamis ala manga olahraga** dengan alur: ekstraksi berita, naskah *voiceover*, gambar adegan di **Flow**, *storyboard* JSON, hingga render otomatis lewat proyek **Remotion** yang sudah ada di server.

**Versi alur: v3.2 (24 Nov 2026).** Perubahan v3.2 (revisi pengguna): (1) subtitle per adegan dipecah jadi segmen MAKS 2 baris, durasi tiap segmen mengikuti pengucapan kata-katanya — TIDAK ada lagi subtitle 1 paragraf; (2) karakter Flow dibuat untuk SEMUA tokoh bernama di artikel, termasuk LAWAN — bukan hanya tokoh utama. Alur ini menggantikan v3.1 setelah lima episode (Peralta, Megawati, Umuh, STY, Nawaf/Indah). Episode referensi: `projects/episodes/2026-11-23-peralta-absen-lawan-persita/` (v6 Flow), `projects/episodes/2026-11-23-megawati-mvp-perdana-hillstate/` (v3 Flow), dan `projects/episodes/2026-11-24-umuh-muchtar-hadiah-juara-belum-cair/` (v1 Flow).

## Pembagian Kerja — ATURAN UTAMA (keputusan pengguna 24 Nov 2026)

- **Flow KHUSUS gambar.** Di Flow hanya dua hal: (1) buat karakter dulu dari foto asli + jersey asli, (2) generate gambar adegan dari prompt Muse. **JANGAN** merakit adegan/scene/video di Flow.
- **Gambar SELALU di Flow — tanpa kecuali.** Termasuk saat pengguna berkata "kamu yg buat sampai beres" / "buat sampai videonya jadi" / "aku tinggal nunggu hasil": artinya Muse yang menjalankan Flow lewat browser (cari foto, buat karakter, generate adegan satu per satu, unduh), BUKAN generate gambar sendiri dengan image tool. **Image tool TIDAK dipakai untuk gambar episode** — pelajaran Umuh 24 Nov 2026: 7 gambar image tool ditolak pengguna ("kan aku minta semua di flow saja") dan diarsipkan tanpa dipakai; adegan amplop yang gagal di image tool justru berhasil di Flow.
- **Satu adegan = satu prompt, proses sampai jadi, baru prompt adegan berikutnya.** JANGAN gabung beberapa adegan dalam satu prompt (percobaan "3 adegan sekaligus" menghasilkan kolase 3-panel yang tidak terpakai) dan JANGAN kirim beberapa prompt sekaligus dalam satu batch.
- **Semua editing oleh Muse di Remotion.** VO, caption, susun adegan, render — semuanya di Remotion. Jangan tawarkan merakit video di Flow.
- **Satu project Flow per cerita.** Jangan campur cerita berbeda dalam satu project (project Peralta: "Nov 24 - 09:09"; project Megawati: "Nov 24 - 09:53").

## When to Use

Gunakan skill ini ketika pengguna:

- Memberikan URL berita dari situs mana saja dan meminta dibuatkan video animasi pendek.
- Meminta prompt adegan untuk digenerate sendiri di Flow, atau meminta video dibuat sampai beres.
- Memberi tahu bahwa file audio VO eksternal (`vo-main.mp3` atau `vo-main.wav`) sudah siap dan meminta **lanjut render** ke MP4 lewat Remotion.

## Prerequisites on Server

Pastikan lingkungan server memiliki:

- `ffmpeg` / `ffprobe` (untuk sinkronisasi durasi audio VO dan verifikasi render).
- Proyek Remotion yang sudah terpasang di server (simpan path-nya di environment variable `REMOTION_PROJECT_DIR`, atau tanyakan ke pengguna sekali saat pertama kali render). Proyek saat ini: `~/workspace/news-anime-remotion/remotion/` (Remotion 4.0.540, komposisi `AnimeNewsVideo` 1080x1920 30fps terdaftar di `src/Root.tsx`).
- Python venv dengan `rembg[cpu]` + `pillow` (hanya untuk alur legacy v1; alur v3 tidak memakai rembg).

## Output Directory Structure

```text
projects/
├── asset-registry.json                 # Registri aset (dipakai alur legacy v1; v3 mencatat karakter Flow di 04-flow-prompts.md)
├── shared-assets/                      # Pustaka PNG transparan alur legacy v1 (characters, props, backgrounds, emblems)
└── episodes/
    └── YYYY-MM-DD-<slug-berita>/
        ├── 01-news-brief.md            # Ringkasan fakta terverifikasi & sudut cerita
        ├── 02-voiceover-script.md      # Naskah VO + teks bersih siap TTS
        ├── 03-storyboard.json          # Data scene & animasi siap baca oleh Remotion
        ├── 04-flow-prompts.md          # Log prompt Flow + catatan karakter & revisi
        ├── assets/
        │   ├── raw/                    # Foto referensi karakter, gambar mentah
        │   ├── flow/                   # Gambar adegan final (scene-01.jpg … scene-NN.jpg)
        │   └── vo-main.mp3             # Audio VO
        └── output/
            ├── final-video.mp4         # Hasil render terakhir (ditiban tiap render)
            ├── final-video-vN-<label>.mp4  # Salinan bernama tiap versi (jangan timpa)
            └── check/                  # Frame hasil render untuk verifikasi visual
```

## Workflow Steps

### Step 1: Baca dan Ekstrak Fakta Berita

1. Buka dan baca isi penuh artikel dari URL yang diberikan pengguna (gunakan alat baca web atau WP API bila artikel dari berita.thehanifz.my.id).
2. Ekstrak fakta inti tanpa menambah asumsi di luar artikel:

- **Tokoh utama & peran:** Nama lengkap, klub/instansi, dan peran dalam cerita.
- **SEMUA tokoh bernama lainnya (v3.2):** Lawan, rekan, pelatih, wasit, atau siapa pun yang disebut namanya di artikel — lengkap dengan peran dan tim/klubnya. Mereka BUKAN figuran generik: tiap tokoh bernama yang muncul di adegan WAJIB punya karakter Flow sendiri (lihat Step 4). Contoh: di artikel Nawaf/Indah, lawannya Harry Wakefield/Sian Kelly (Inggris) adalah tokoh adegan, bukan "pemain generik".
- **Konflik atau plot twist:** Momen paling dramatis untuk *hook* 5 detik pertama.
- **Kronologi & angka kunci:** Menit kejadian, skor, tanggal, nominal, atau statistik penting.
- **Dampak & lanjutan:** Konsekuensi langsung dan jadwal atau peristiwa berikutnya.
- **Sumber artikel:** Judul asli, nama situs, tanggal terbit, dan URL asli untuk CTA trafik web.

3. Simpan hasil ekstraksi ke `01-news-brief.md`.

### Step 2: Verifikasi Fakta Visual Sebelum Menulis Prompt

Sebelum menulis prompt apa pun, verifikasi dua hal dengan pencarian web:

1. **Nomor punggung asli pemain.** Cari dan konfirmasi nomor skuad pemain di klubnya saat ini (contoh terverifikasi: Peralta = 10 di Persib; Megawati = 88 di Hillstate). Tulis nomor yang sudah terverifikasi ke dalam prompt — jangan menebak atau membiarkan generator mengarang nomor.
2. **Penampilan asli tokoh.** Periksa apakah tokoh memakai hijab, manset lengan panjang, atau ciri khas lain saat bertanding. Tulis ciri itu ke dalam deskripsi karakter dan tiap prompt (pelajaran Megawati 24 Nov 2026: prompt v2 salah tulis "long dark hair in a ponytail" padahal Mega berhijab — karakter hasil generate ditolak pengguna).
3. **Verifikasi lawan juga (v3.2).** Untuk tiap tokoh bernama lain dari Step 1 (lawan, rekan, pelatih): verifikasi penampilan + jersey/seragam timnya dengan cara yang sama seperti tokoh utama. Lawan yang tampil di adegan tanpa verifikasi akan digenerate sebagai orang generik — itu yang dilarang v3.2.
4. Simpan hasil verifikasi di `01-news-brief.md` dan `04-flow-prompts.md`.

### Step 3: Tulis Naskah Voiceover

Tulis naskah di `02-voiceover-script.md` dengan target durasi **35-45 detik** (90-120 kata Bahasa Indonesia lugas dan bertenaga) menggunakan struktur 5 babak:

1. **Hook (0-5 detik):** Langsung masuk ke kontras atau *plot twist* terbesar.
2. **Setup & Aksi Utama (5-15 detik):** Kejadian kunci beserta angka/momen spesifik.
3. **Klimaks / Plot Twist (15-26 detik):** Titik balik dramatis.
4. **Dampak & Konteks Lanjutan (26-36 detik):** Konsekuensi nyata atau jadwal berikutnya.
5. **Cliffhanger & CTA Trafik (36-42 detik):** Sisakan satu detail menarik dari artikel, pancing komentar, lalu arahkan penonton membaca artikel lengkap di web (link di bio/komentar).

Sertakan versi **Teks Bersih (Siap Copy-Paste ke TTS)** di bagian atas `02-voiceover-script.md`.

**Audio VO:** Default-nya Muse yang generate VO (suara Helio via `tts`) dari teks bersih, atas persetujuan pengguna; atau pengguna mengirim audio VO-nya sendiri. Bila pengguna mengirim audio VO sendiri, ganti `assets/vo-main.mp3`, jalankan ulang sinkronisasi (Step 7), render ulang, dan kirim ulang.

### Step 4: Karakter di Flow (dari Foto Asli) — Utama + Lawan

Karakter dibuat di Flow SEBELUM adegan, dari foto asli — **untuk tokoh utama DAN semua tokoh bernama lain yang muncul di adegan (v3.2)**, terutama lawan:

1. Cari foto asli tiap tokoh yang jelas (tampak depan, memakai jersey klub) dari sumber resmi (Instagram resmi klub / artikel berita). Simpan ke `<episode>/assets/raw/`. Untuk lawan: cari foto dari sumber resmi tim/turnamen mereka juga — jangan pakai foto acak.
2. Di project Flow episode itu, buat SATU karakter per tokoh dari foto tersebut sebagai ingredient. Deskripsi karakter: gaya **anime 2D** (tambahkan token `animestyle japan 2d`: bold ink lineart, cel shading, MAPPA/Blue Lock inspired, no photorealism), ciri penampilan terverifikasi dari Step 2 (mis. hijab navy gelap, manset lengan panjang hitam), jersey klub + nomor punggung terverifikasi.
3. **Verifikasi karakter sebelum generate adegan:** karakter harus anime 2D (bukan fotorealistik — bila hasil pertama fotorealistik, buat ulang dengan permintaan gaya anime eksplisit) dan ciri penampilan harus benar (mis. berhijab). Bila karakter salah, JANGAN lanjut generate adegan. Berlaku untuk karakter lawan juga — lawan yang salah wajah/jersey sama fatalnya dengan tokoh utama yang salah.
4. Catat nama karakter, URL project/karakter, dan sumber foto tiap tokoh di `04-flow-prompts.md`.
5. **Biaya:** tiap karakter tambahan = waktu + kredit Flow ekstra. Itu konsekuensi yang sudah disetujui pengguna demi adegan yang hidup — jangan menghemat dengan menjadikan lawan karakter generik.

### Step 5: Prompt Adegan — Satu Adegan per Penjelasan

1. Bagi naskah VO menjadi adegan **satu per penjelasan/poin** (BUKAN per kata — per kata akan menghasilkan video ~6 menit untuk VO 46 detik; sudah diklarifikasi pengguna 24 Nov 2026). Satu episode biasanya 8-10 adegan.
2. Tulis prompt untuk tiap adegan ke file `~/workspace/your_files/prompts-<slug>-flow-N-adegan.txt` dalam DUA bagian: (a) versi ber-timestamp `MM-SS: prompt adegan` untuk dibaca, (b) versi bersih tanpa timestamp (1 baris = 1 prompt) untuk upload ZAPI FLOW. Tempel juga prompt lengkap di chat.
3. Tiap prompt bersifat **mandiri dan lengkap**: token gaya anime dari `references/style-guide-anime.md` + deskripsi karakter + jersey/nomor + aksi adegan + `vertical 9:16 framing` + `no text, no watermark`. Angka/nama di jersey ditulis ke dalam prompt supaya generator membuatnya secara native di dalam gambar.
4. **Pasang karakter lawan di adegannya (v3.2).** Di adegan yang melibatkan lawan (duel, jabat tangan, rally, selebrasi lawan, dsb.), lampirkan karakter lawan dari Step 4 sebagai ingredient — JANGAN tulis lawan sebagai deskripsi teks generik ("English opponents") bila mereka punya nama di artikel. Nama lawan disebut di prompt hanya sebagai pengenal karakter, bukan sebagai teks di gambar.
5. Durasi tiap adegan = panjang segmen VO-nya (kata × 12 frame), lalu sinkronisasi di Step 7. Adegan TIDAK bisa dipaksa 2-4 detik tanpa memotong penjelasan.
6. Log semua prompt + revisi ke `04-flow-prompts.md`.

### Step 6: Gambar Adegan — Dua Mode

**Mode A (default): pengguna generate di Flow.**
- Pengguna generate gambar adegan di project Flow episode itu memakai karakter Step 4 + prompt Step 5, lalu mengirim gambarnya ke Muse (atau Muse mengunduhnya lewat browser dari project Flow).
- File download browser mendarat di `~/workspace/browser_downloads/<sesi>/` — file itu ADA di workspace dan bisa diteruskan ke task browser lewat parameter `files`. Periksa dulu folder itu sebelum menyatakan file tidak ada.
- Simpan gambar final sebagai `<episode>/assets/flow/scene-01.jpg` … `scene-NN.jpg` (768x1376, 9:16) sesuai urutan adegan. Cek visual tiap gambar: hijab/ciri tokoh, nama + nomor jersey, dan isi adegan sesuai prompt.

**Mode B (bila pengguna berkata "kamu yg buat sampai beres" / "buat sampai videonya jadi"):** Muse yang menjalankan Flow lewat browser (task browser: cari foto asli, buat karakter, generate adegan satu per satu, unduh semua gambar), lalu rakit + render di Remotion seperti biasa. Gambar tetap berasal dari Flow — JANGAN generate gambar dengan image tool.

### Step 7: Storyboard JSON, Sinkronisasi & Render

1. Susun `03-storyboard.json` (`1080x1920`, `30 fps`): satu adegan per penjelasan dari Step 5, tiap adegan berisi **SATU layer `background`** berupa gambar Flow (`assets/flow/scene-NN.jpg`, `objectFit: cover`, full-bleed), `animationPreset` `freeze-zoom` (adegan hook: `slam-in`), **TANPA layer `textOverlay`** — caption berasal dari template `HighlightedCaption` yang membaca `voiceoverText` + `highlightWords`. `audio.voiceoverFile` = `assets/vo-main.mp3`.
2. **Subtitle MAKS 2 baris per segmen (v3.2) — JANGAN subtitle 1 paragraf.** Tiap adegan WAJIB memecah `voiceoverText`-nya menjadi array `captions`: tiap segmen **maks 12 kata** (≈ 2 baris di kotak caption 42px), dipecah di **batas frasa alami** (koma, jeda klausa, ganti subjek), dan `startFrame`/`durationInFrames` tiap segmen **sebanding dengan jumlah kata** supaya segmen tampil tepat selama kata-katanya diucapkan. Segmen berurutan tanpa celah, mulai dari frame 0 adegan. Template (`SceneCaption`) hanya menampilkan segmen yang aktif di frame itu; `sync_audio_duration.py` ikut mengskala segmen saat durasi adegan berubah. Contoh — adegan 150 frame dengan teks "Kemenangan ini melanjutkan tren positif, semifinal Malaysia Super 100, dan comeback atas pasangan Tiongkok di Kudus." (17 kata) dipecah jadi:
   ```json
   "captions": [
     { "text": "Kemenangan ini melanjutkan tren positif,", "highlightWords": ["tren"], "startFrame": 0, "durationInFrames": 62 },
     { "text": "semifinal Malaysia Super 100,", "highlightWords": ["Malaysia"], "startFrame": 62, "durationInFrames": 44 },
     { "text": "dan comeback atas pasangan Tiongkok di Kudus.", "highlightWords": ["comeback"], "startFrame": 106, "durationInFrames": 44 }
   ]
   ```
   (Pembagian 6 + 4 + 7 kata → 62 + 44 + 44 frame ≈ sebanding jumlah kata.) Bila adegan belum punya `captions`, template menampilkan `voiceoverText` utuh seperti dulu — itu hanya fallback untuk storyboard lama, BUKAN untuk episode baru.
3. Sinkronisasi durasi adegan ke VO asli:

```bash
python3 scripts/sync_audio_duration.py --storyboard "<episode>/03-storyboard.json" --audio "<episode>/assets/vo-main.mp3"
```

3. Render:

```bash
cd ~/workspace/news-anime-remotion && bash scripts/render_remotion.sh "<episode>" remotion AnimeNewsVideo
```

(Render ±3-6 menit; jalankan di background bila perlu. Skrip memverifikasi aset + VO, men-stage aset ke `remotion/public/episodes/<episodeId>/`, merender, dan memverifikasi MP4 > 0 byte.)
4. Salin hasil ke `output/final-video-vN-<label>.mp4` (nama berbeda tiap versi — jangan kirim file bernama sama seperti versi lama, aplikasi chat bisa menampilkan cache versi lama).
5. **Verifikasi sebelum kirim:** `ffprobe` (1080x1920 h264 + AAC, durasi cocok VO), ekstrak 3-4 frame (awal, tengah, akhir) ke `output/check/` dan baca visualnya — caption benar dan tidak menutupi wajah, nama/nomor jersey benar, gambar full-bleed. Baru kirim video sebagai lampiran di chat (pengguna TIDAK punya akses ke VM — jangan hanya menyebut nama file).

## Validation Checklist

Sebelum melaporkan video selesai, pastikan:

- [ ] Semua angka, nama tokoh, dan jadwal di naskah sesuai 100% dengan artikel sumber.
- [ ] Nomor punggung dan ciri penampilan tokoh terverifikasi via pencarian web dan tertulis benar di prompt.
- [ ] Karakter Flow terverifikasi anime 2D dan ciri penampilannya benar SEBELUM adegan digenerate.
- [ ] **Karakter lawan dibuat dari foto asli dan dipasang di adegannya (v3.2)** — tidak ada tokoh bernama yang digenerate sebagai orang generik.
- [ ] **Tiap adegan punya `captions` dengan segmen MAKS 12 kata / 2 baris (v3.2)** — tidak ada subtitle 1 paragraf di video.
- [ ] Semua gambar `assets/flow/scene-NN.jpg` dicek visual satu per satu.
- [ ] `03-storyboard.json` sudah tersinkron dengan durasi `vo-main.mp3`.
- [ ] `output/final-video-vN-<label>.mp4` berhasil dirender (1464/1464 frame dsb.), terverifikasi via `ffprobe` + frame, dan terkirim sebagai lampiran.

## Larangan & Pelajaran (dari episode Peralta & Megawati)

- **JANGAN tampilkan subtitle 1 paragraf (v3.2).** Subtitle per adegan HARUS dipecah jadi segmen maks 2 baris / 12 kata dengan durasi mengikuti pengucapan. Subtitle paragraf penuh = video cacat, render ulang.
- **JANGAN jadikan lawan karakter generik (v3.2).** Tiap tokoh bernama di artikel yang muncul di adegan WAJIB punya karakter Flow dari foto asli. "Pemain Inggris generik" atau "lawan generik" di prompt = adegan salah, regenerate.
- **JANGAN tempel teks jersey dengan PIL.** Teks nama/nomor/sponsor yang ditempel di atas gambar terlihat seperti tempelan dan DITOLAK pengguna (Peralta v4/v5). Teks jersey HARUS digenerate native di dalam gambar (tulis di prompt, atau pakai karakter Flow dari foto asli).
- **JANGAN generate gambar episode dengan image tool.** Semua gambar harus dari Flow (pelajaran Umuh 24 Nov 2026 — lihat Pembagian Kerja).
- **JANGAN gabung beberapa adegan dalam satu prompt.** Satu adegan = satu prompt, proses, baru prompt berikutnya (pelajaran Umuh 24 Nov 2026: gabungan 3 adegan jadi kolase 3-panel).
- **JANGAN merakit video di Flow.** Flow hanya untuk gambar; semua editan di Remotion.
- **Adegan satu per penjelasan, bukan per kata.** (Klarifikasi pengguna 24 Nov 2026.)
- **Periksa file draft & artikel asli sebelum menampilkan/mempublikasikan apa pun.** Ringkasan handoff/hook bisa berbeda dari file yang benar.
- **Nama file video tiap versi harus berbeda.** Nama sama memicu cache aplikasi chat menampilkan video lama.

## Gotchas

- **Area aman (*safe zone*) 9:16.** Pastikan teks caption dan wajah karakter berada di antara 15% hingga 78% tinggi layar agar tidak tertutup UI TikTok, Reels, atau Shorts. Caption template berada di 18% bawah — normal bila sedikit menutupi bagian bawah jersey, selama tidak menutupi wajah atau nomor.
- **rembg default model OOM di VM 6 GB.** Bila alur legacy v1 dipakai, pakai model `u2net` (bukan bria-rmbg-2.0) dan selalu dengan extra `[cpu]`.
- **Jika satu gambar adegan gagal atau salah:** regenerate adegan itu saja (sebut nomor adegannya), ganti file `scene-NN.jpg`, render ulang, verifikasi, kirim ulang dengan nama versi baru.
- **Jika pengguna mengirim VO-nya sendiri:** ganti `assets/vo-main.mp3`, sync ulang, render ulang, kirim ulang.
- **Alur legacy v1 (layer + rembg)** masih terdokumentasi di `04-flow-prompts.md` tiap episode dan di `references/`; dipakai Peralta v1–v5 dan Megawati v1. Jangan pakai lagi kecuali pengguna memintanya secara eksplisit.
