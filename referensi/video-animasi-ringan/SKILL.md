---
name: video-animasi-ringan
description: Membuat video animasi teks (Reels/Shorts 9:16 atau YouTube 16:9) dari naskah + file voice-over mp3 (misalnya dari ElevenLabs), dengan alur kerja motion design profesional (konsep → styleframe → animasi → finishing), gerak kamera, transisi, SFX berlapis, subtitle, dan file .srt. Pakai saat user minta "buatkan video dari naskah/VO ini", "bikin Reels animasi", atau mengunggah mp3 VO dan naskah.
---

# Video animasi ringan (Python + Pillow + FFmpeg)

Semua berjalan di sandbox ini. Tidak perlu internet, API key, atau instal apa pun.
Alurnya meniru cara kerja studio motion design, versi ringan: **pra-produksi dulu (paling lama), baru animasi, lalu finishing.**

## Kamu motion designer-nya
Video buatan AI punya ciri: semua teks fade + naik pelan dengan kurva yang sama, jarak antar-elemen rata, lalu diam.
Skill ini menolak kebiasaan itu. **Baca `LIBRARY.md` (di folder skill ini) sebelum membuat rencana adegan.**
- Putuskan dulu video ini harus terasa seperti apa, baru pilih `rasa`, `kurva`, dan cara masuk. Dua video jangan bergerak sama.
- Tentukan gerak itu APA sebelum bagaimana easing-nya: judul ini langsung hadir, diketik, memantul, atau dihantamkan?
- **Layar = ilustrasi yang bergerak + subtitle yang hidup.** Bawaan: TANPA judul besar dan TANPA bar progres; subtitle sudah
  membawa kalimatnya, jadi judul hanya mengulang. Pakai `judul` hanya kalau ada istilah/angka yang harus tetap terbaca di layar.
- **Gambar mengikuti suara.** Yang tampil di layar harus benda atau kejadian yang SEDANG diucapkan. Ganti kalimat = ganti gambar.
  Tes: matikan suara; kalau gambar saja tidak menceritakan kalimatnya, gambarnya salah. Jangan pakai ulang gambar untuk kalimat lain.
- **Tidak ada benda yang diam.** Tiap ilustrasi dipecah jadi lapisan, dan tiap lapisan datang dan bergerak sendiri.
- **Kalau memakai judul, sebagian besar `potong`.** Gerak khusus (`pop`, `slam`, `fokus`, `whip`, `zoom`) hanya di titik cerita berbelok.
- Pantulan itu pilihan, bukan hiasan. Satu transisi andalan per video; sisanya kerajinan yang tidak terasa.
- Jangan menambah ciri AI: fade di semua teks, blur-in, bola cahaya, teks shimmer, garis bawah judul, pil/chip label,
  pola garis atau grid hiasan. Layar hanya berisi yang membawa isi: gambar dan subtitle (judul/keterangan hanya kalau perlu).

## Yang dibutuhkan dari user
1. **Naskah**: teks yang dibacakan di VO (ditempel di chat atau diunggah sebagai file).
2. **File VO mp3** yang sudah FINAL (misalnya dibuat di ElevenLabs, lalu diunggah ke chat).
   API ElevenLabs tidak bisa diakses dari sandbox, jadi VO harus dibuat dan diunggah sendiri oleh user.
3. **Format**: `9:16` (Reels/Shorts/TikTok) atau `16:9` (YouTube). Kalau user tidak menyebut, tanyakan.

Kalau naskah atau mp3 belum ada, minta dulu. Jangan mengarang isi naskah.

## Fase 1 — Pra-produksi (paling penting)
1. **Concept statement.** Tulis 1 kalimat pesan utama video, lalu pilih satu `rasa` (kepribadian gerak) sesuai emosi yang dituju:
   | rasa | emosi | gerak |
   |---|---|---|
   | `tegas` (default) | informatif, urgent, edukasi | masuk cepat, henti halus, pantul kecil |
   | `mewah` | elegan, premium, tenang | pelan, anggun, hampir tanpa pantul, jeda antar-elemen lebar |
   | `teknologi` | high-tech, presisi | sangat cepat, rapat, tajam |
   | `ceria` | playful, santai | memantul, kurva lewat 100% |
   Tunjukkan concept statement + rasa ke user. Satu rasa untuk seluruh video, jangan dicampur.
2. **Audio dulu.** VO harus final sebelum adegan dirancang. Waktu adegan dihitung dari jeda di mp3, jadi VO = grid waktu seluruh gerakan.
3. **Design system.** Maksimal 3–4 warna (`tema`), satu jenis judul, satu rasa. Jangan menambah warna per adegan.
4. **Rencana adegan = animatic.** Pecah naskah jadi adegan: SATU kalimat (satu gagasan) per adegan, 3–7 detik.
   Kalimat panjang yang menyebut beberapa hal dipecah lagi, atau tiap hal diberi lapisan ber-`saat` (langkah 8).
   Script memberi tanda `!` kalau satu gambar tampil lebih dari 8 detik atau ada adegan tanpa gambar: perbaiki dulu sebelum menunjukkan rencana.
   `ucapan` berisi teks VO apa adanya dan berurutan. Apit kata/frasa TERPENTING dengan bintang, misalnya
   `"Tanah pucuk ini *tidak dibuang*, tapi disimpan."`: di subtitle kata itu mendapat kotak kuning (di file .srt bintangnya hilang).
   Maksimal 1 frasa (1–3 kata) per kalimat: angka, istilah, atau kata yang membalik makna. Kalau semua disorot, tidak ada yang penting.
   Untuk tiap adegan:
   - `gambar`: ilustrasi BERLAPIS yang mewakili adegan (lihat langkah 8). **Setiap adegan wajib punya**; inilah isi utama layar.
   - `judul` (opsional, bawaan kosong): 1–5 kata besar. Hanya untuk istilah/angka yang harus tetap terbaca; bukan salinan ucapan.
   - `label` (opsional): teks kecil huruf besar di atas gambar/judul, misalnya "1/7".
   - `keterangan` (opsional): 1 baris pendukung.
   - `kamera` (opsional): `dorong` (zoom in pelan), `tarik` (zoom out pelan), `fokus` (zoom ke gambar, atau ke judul kalau ada; mendarat dengan pegas), `diam`.
     Dikosongkan = dorong/tarik bergantian. `fokus` untuk kalimat penting, kira-kira 1 dari 3 adegan.
   - `transisi` (opsional, cara adegan MASUK): `potong` (default), `whip` (sapuan kamera + motion blur),
     `zoom` (push-through: kamera menembus gambar adegan lama ke adegan baru). Hanya di pergantian bagian besar, sekitar 1 per menit.
   - `masuk` (opsional, cara JUDUL datang): `potong` (langsung hadir; pilihan untuk sebagian besar adegan),
     `ketik` (terbuka per huruf: perintah, nama file, kutipan), `pop` (pegas, bawaan kalau dikosongkan; untuk poin penting),
     `slam` (dihantamkan dari besar; hook/penutup, maksimal 1–2 per video). Lihat LIBRARY.md bagian 3.
   - `sfx` (opsional): tambahan di awal adegan: `ding` (benar/berhasil), `error` (salah/kendala), `thud`, `pop`, `tick`, `klik`, `sub`.
5. **Cek alur mata (eye-tracking)** sebelum menunjukkan rencana:
   - Satu fokus per adegan: ilustrasinya. Subtitle di bawahnya, selalu di tempat yang sama.
   - Di tiap ilustrasi ada SATU bagian yang paling hidup (yang sedang dibicarakan); bagian lain bergerak lebih kecil.
   - Whip selalu ke arah yang sama. Jangan dua transisi besar berturut-turut.
   - Info penting jangan di tepi atau dekat subtitle.
   - Jalankan daftar periksa LIBRARY.md bagian 6 (jumlah alat gerak, variasi cara masuk).
6. Tampilkan concept statement, rasa, dan tabel rencana (no, ucapan dengan *kata penting*, isi gambar + lapisan dan geraknya, kamera, transisi, sfx). **Tunggu persetujuan.**
7. Tulis `rencana.json` di folder kerja:
   ```json
   {
     "nama": "tahapan-tambang",
     "format": "9:16",
     "audio": "/mnt/user-data/uploads/vo.mp3",
     "rasa": "tegas",
     "kurva": "kit.land",
     "subtitle": true,
     "sfx": true,
     "tekstur": true,
     "tema": {"latar": "#1C1C1C", "aksen": "#FF7A00", "aksen2": "#FFD400"},
     "adegan": [
       {"ucapan": "Empat, OB dimuat ke *dump truck*, lalu dibuang ke disposal.", "kamera": "dorong",
        "gambar": ["a4_tanah.png",
                   {"file": "a4_badan.png", "saat": "dump truck", "masuk": "kiri", "hidup": "apung"},
                   {"file": "a4_roda1.png", "saat": "dump truck", "masuk": "kiri", "hidup": "putar"},
                   {"file": "a4_roda2.png", "saat": "dump truck", "masuk": "kiri", "hidup": "putar"},
                   {"file": "a4_muatan.png", "saat": "dibuang", "masuk": "atas", "hidup": "apung"}]},
       {"ucapan": "Angkanya *tujuh tahap*.", "gambar": ["a5_peta.png"], "judul": "7 Tahap", "masuk": "slam", "transisi": "whip"}
     ]
   }
   ```
   Semua kunci selain `format`, `audio`, dan `adegan` opsional. `subtitle`, `sfx`, `tekstur` default true.
   `kurva` = nama kurva masuk dari LIBRARY.md bagian 2, menggantikan kurva bawaan `rasa` (kosongkan kalau ragu).
   `penanda` = bar progres + penanda berjalan: `tidak` (bawaan, tanpa bar), `titik`, `truk`. Pakai hanya kalau user memintanya.
8. **Ilustrasi berlapis per adegan.** `gambar` = daftar lapisan, dari belakang ke depan. Tiap lapisan satu PNG transparan.
   - Gambar sendiri dengan Pillow (atau pakai foto/screenshot user sebagai satu lapisan diam: `"gambar": "foto.png"`).
   - **Semua lapisan satu adegan digambar di kanvas berukuran sama** (2000x2000, lalu `resize((1000, 1000), Image.LANCZOS)`),
     masing-masing hanya berisi bagiannya di posisi akhirnya. Script menumpuknya dan membuang tepi kosong.
   - Pecah benda menurut bagian yang di dunia nyata bergerak sendiri: roda, muatan, layar, lengan, asap, panah, jarum. 3–6 lapisan per adegan.
   - Tiap lapisan: `{"file": "...", "saat": ..., "masuk": ..., "hidup": ...}`. Nama file saja = lapisan diam (tanah, meja).
   - **`saat` = kata atau frasa dari `ucapan` adegan itu.** Lapisan baru datang tepat ketika kata itu diucapkan, jadi gambar
     terbangun mengikuti suara: `"...digali excavator, dimuat ke dump truck, lalu dibuang ke disposal"` → gundukan `"saat": "digali"`,
     truk `"saat": "dump truck"`, muatan `"saat": "dibuang"`. Tulis persis seperti di ucapan (tanpa bintang). Tanpa `saat`, lapisan datang di awal adegan.
     Setiap benda yang disebut di kalimat sebaiknya punya lapisan ber-`saat` sendiri; hanya latar (tanah, meja) yang tanpa `saat`.
     | `masuk` (cara datang) | | `hidup` (gerak terus-menerus) | cocok untuk |
     |---|---|---|---|
     | `potong` (bawaan) | langsung ada | `diam` (bawaan) | tanah, meja, latar |
     | `bawah` `atas` `kiri` `kanan` | meluncur dari arah itu | `apung` | naik-turun pelan: badan kendaraan, muatan, awan |
     | `pop` | membesar dengan pegas | `ayun` | bergoyang kiri-kanan: helm, papan, daun |
     | | | `napas` | membesar-mengecil halus: layar menyala, lampu, tombol |
     | | | `putar` | berputar terus: roda, kipas, gir (beri tanda/jari-jari supaya putarannya terlihat) |
     | | | `geser` | bolak-balik mendatar: awan, ombak, panah |
   - Lapisan datang berurutan dengan jeda tidak rata (urutan daftar = urutan datang), dan `hidup` tiap lapisan berbeda fase.
     Pilih arah `masuk` yang masuk akal (truk dari samping, muatan dari atas), bukan sama semua.
   - Gambarkan BENDA atau KEJADIAN yang disebut di ucapan adegan itu, bukan ikon umum (bola lampu, roket, roda gigi, centang).
   - Bentuk datar dan tebal dari `polygon`, `rectangle`, `ellipse`, `pieslice`; 2–3 warna dari `tema` + putih + abu gelap.
     Tanpa gradien, glow, bayangan, dan tanpa teks. Gaya sama di semua adegan.
     ```python
     from PIL import Image, ImageDraw
     def lapis(nama, gambar):                      # satu bagian = satu PNG di kanvas yang sama
         img = Image.new("RGBA", (2000, 2000), (0, 0, 0, 0)); gambar(ImageDraw.Draw(img))
         img.resize((1000, 1000), Image.LANCZOS).save(nama)
     lapis("a4_tanah.png", lambda d: d.rectangle([100, 1660, 1900, 1720], fill="#3A3A3A"))
     lapis("a4_badan.png", lambda d: (d.polygon([(280, 900), (1340, 900), (1240, 1380), (380, 1380)], fill="#FF7A00"),
                                      d.rectangle([1380, 960, 1800, 1380], fill="#FF7A00")))
     lapis("a4_roda1.png", lambda d: (d.ellipse([390, 1290, 770, 1670], fill="#111111"),
                                      d.rectangle([560, 1300, 600, 1400], fill="#FFD400")))   # tanda supaya putaran terlihat
     ```
   - Kalau script berhenti dengan "tidak cukup ruang untuk gambar", perpendek atau hapus `judul`/`keterangan` adegan itu.
9. **Styleframe.** `python <folder skill>/buat_video.py rencana.json --preview` → satu gambar grid, satu frame per adegan
   (diambil menjelang akhir adegan, saat semua lapisan sudah datang). Cocokkan tiap frame dengan kalimatnya sebelum dikirim.
   Kirim ke user, minta persetujuan sebelum render. Revisi di tahap ini jauh lebih murah daripada setelah render.

## Fase 2 — Animasi (otomatis oleh script)
Yang sudah dikerjakan script, tidak perlu diatur manual:
- **Kurva kecepatan ekstrem:** kamera Easy Ease influence ±80–85%; entri elemen ease-out kuat sesuai `rasa` atau `kurva`.
- **Teks pendukung langsung hadir** (cut), tanpa fade.
- **Inersia:** zoom `fokus` dan pop judul memakai pegas (mulai dari diam, lewat sedikit, mengendap).
- **Ilustrasi hidup:** tiap lapisan datang sendiri (saat katanya diucapkan, atau berurutan di awal adegan) lalu terus bergerak dengan fase berbeda.
- **Subtitle hidup:** kata muncul satu per satu mengikuti ucapan, tiap kata melompat masuk dengan pegas; kata bertanda `*...*` diberi kotak kuning.

## Fase 3 — Finishing & audio (otomatis)
- **Tekstur (`tekstur`):** grain halus bergerak, vignette, aberasi kromatik 1 px, color grade (kontras S + sedikit hangat),
  untuk menghilangkan kesan vektor yang terlalu bersih. Matikan dengan `"tekstur": false` untuk tampilan flat/bersih.
- **SFX 3 lapis** (sintetis, bebas lisensi, dicampur pelan di bawah VO):
  1. sub-bass (`sub`): bobot saat judul/kamera mendarat,
  2. mid whoosh: udara saat kamera atau transisi bergerak,
  3. high (`pop`, `klik`): detail kecil saat elemen muncul.
- Render: `python <folder skill>/buat_video.py rencana.json` → `<nama>.mp4` (H.264, AAC 48 kHz, sekitar -14 LUFS) dan `<nama>.srt`
  di `/mnt/user-data/outputs/`. Sekitar 3–4 menit render per 1 menit video (bisa beda di sandbox).
- Berikan file mp4 dan srt ke user, plus tabel pembagian waktu adegan yang dicetak script.

## Batasan (sampaikan jujur kalau user meminta)
Versi ringan ini hanya 2D: lapisan gambar yang bergeser, berputar, dan membesar-mengecil (bentuknya sendiri tidak berubah). Tidak ada: 3D (Cinema 4D/Blender), rigging karakter, animasi frame-by-frame,
match cut otomatis antar-bentuk, depth of field, lens distortion, atau file LUT. Untuk itu perlu After Effects/Remotion di komputer.

## Kalau ada masalah
- Gambar terasa "itu-itu saja" atau tidak nyambung dengan suara: adegan terlalu panjang atau lapisan tanpa `saat`.
  Pecah adegan per kalimat, gambar ulang sesuai isi kalimat, dan beri `saat` pada tiap benda yang disebut.
- Subtitle atau adegan meleset dari suara: geser kalimat antar-adegan atau pecah adegan yang panjang, lalu render ulang.
  Waktu dihitung dari jeda di mp3, bukan pengenalan suara.
- Teks keluar layar: perpendek `judul` atau `keterangan`. Zoom `fokus` otomatis dibatasi supaya judul tetap muat.
- Gerak terasa berlebihan: ganti `masuk` ke `potong`, `rasa` ke `mewah`, `kamera` ke `diam`, `transisi` ke `potong`, atau `"sfx": false`.
- Gerak terasa datar/sama semua: beri SATU `slam` di hook dan satu `fokus` di poin terpenting, bukan menambah gerak di semua adegan.
- Font sendiri: minta file .ttf, salin ke `<folder skill>/fonts/judul.ttf` dan/atau `isi.ttf`.
- Jangan menambah musik, logo, atau data angka yang tidak ada di naskah user.
