# Pustaka gerak (motion library)

Amunisi untuk merancang gerak, bukan gaya untuk ditiru. Kamu motion designer-nya: tentukan dulu apa yang mau
disampaikan video, pilih satu `rasa`, lalu pilih kurva dan cara masuk yang membawa pesan itu.
Dua video seharusnya tidak bergerak dengan cara yang sama. Aturan yang menunjuk ke sini ada di `SKILL.md`.

Diadaptasi dari skill "motion-designer" (motion-kit.js + LIBRARY.md, MIT, Hugh Phan) untuk mesin Python + Pillow
di skill ini. Versi aslinya memakai GSAP di browser, yang tidak tersedia di sandbox chat.

## 1. Pilih rasa dulu

| Register | Terasa seperti | `rasa` di skill ini | `kurva` yang cocok |
|---|---|---|---|
| Teknis / produk | Presisi, efisien | `teknologi` | `carbon.productive.entrance`, `m3.standard`, `kit.whip` |
| Penjelasan / edukasi | Sebab-akibat jelas, mata dituntun | `tegas` | `kit.land`, `kit.reveal`, `m3.emphasizedDecelerate` |
| Premium / sinematik | Berbobot, mengendap lama, hemat gerak | `mewah` | `easings.outExpo`, `kit.heavy` |
| Ekspresif / peluncuran | Momen yang sengaja ditonjolkan | `tegas` + beberapa `slam` | `carbon.expressive.entrance`, `kit.whip` |
| Ceria / santai | Elastis, memantul | `ceria` | `easings.outBack` (hemat) |
| Tenang | Bernapas, mengalir | `mewah` + kamera `dorong`/`tarik` | `easings.outSine`, `kit.drift` |

Satu rasa untuk seluruh video. Boleh ada SATU momen ekspresif di video yang tenang; semua rasa sekaligus terlihat seperti demo.

## 2. Kurva bernama (`"kurva"` di rencana.json)

Angkanya `cubic-bezier(x1, y1, x2, y2)`, sama dengan CSS dan grafik kecepatan After Effects.
Kurva ini menggantikan kurva masuk bawaan `rasa` (dipakai label dan garis judul). Kosongkan untuk memakai bawaan rasa.

| Nama | Bezier | Karakter |
|---|---|---|
| `kit.land` | 0.1, 0.75, 0.15, 1 | Datang cepat, mengendap panjang dan yakin. Masuk dari luar layar. |
| `kit.heavy` | 0.75, 0, 0.18, 1 | Mulai pelan, tiba dengan tegas. Benda besar. (Dipakai `slam`.) |
| `kit.whip` | 0.85, 0, 0.15, 1 | Diam, sentak, diam. Pergantian keadaan. |
| `kit.reveal` | 0.22, 1, 0.36, 1 | Hampir semua jarak ditempuh di sepertiga awal. |
| `kit.drift` | 0.4, 0, 0.6, 1 | Napas pelan dan rata. |
| `easings.outSine` … `outExpo` | Sine < Quad < Cubic < Quart < Quint < Expo | Makin ke kanan makin kuat remnya. |
| `easings.outCirc` | 0, 0.55, 0.45, 1 | Mulai mendadak. |
| `easings.outBack` | 0.34, 1.56, 0.64, 1 | Lewat sedikit lalu kembali (memantul). |
| `m3.standard` / `m3.standardDecelerate` / `m3.emphasizedDecelerate` | Material 3 (Google) | Rapi ala antarmuka; "emphasized" untuk gerak penting. |
| `carbon.productive.entrance` / `carbon.expressive.entrance` | IBM Carbon | Productive = efisien; expressive = sengaja terlihat. |

## 3. Cara judul masuk (`"masuk"` per adegan)

Kurva menjawab BAGAIMANA sesuatu bergerak; cara masuk menjawab gerak itu APA. Putuskan ini dulu, per adegan:
kenapa judul ini datang dengan cara itu? Kebiasaan buruk video buatan AI: semua teks fade + naik pelan.
Desainer memotong sebagian besar teks langsung hadir, dan menyimpan gerak khusus untuk yang benar-benar penting.

| `masuk` | Terbaca sebagai | Biaya perhatian | Pakai untuk |
|---|---|---|---|
| `potong` | Yakin, editorial | nol | Sebagian besar adegan (daftar, langkah, penjelasan) |
| `ketik` | Sesuatu yang benar-benar diketik | rendah | Perintah, prompt, nama file, kutipan, teks terminal |
| `pop` (bawaan) | Hidup, ada pegasnya | sedang | Poin penting; jangan di setiap adegan |
| `slam` | Penekanan, hantaman | tinggi | Hook, angka kejutan, penutup. Maksimal 1–2 per video |

Teks pendukung (`keterangan`) selalu langsung hadir (cut), tanpa fade.

Bawaan skill ini: layar tanpa judul. `masuk` hanya berlaku di adegan yang memang memakai `judul`.

## 4. Alat gerak: pilih, jangan ditumpuk

Setiap alat memakan perhatian penonton. Belanjakan di titik cerita berbelok.

| Alat | Kunci di rencana.json | Batas |
|---|---|---|
| Kamera mendekat ke judul | `"kamera": "fokus"` | ±1 dari 3 adegan |
| Sapuan kamera | `"transisi": "whip"` | ±1 per menit, selalu arah yang sama |
| Menembus ke adegan baru | `"transisi": "zoom"` | 1 per video (transisi andalan) |
| Hantaman judul | `"masuk": "slam"` | 1–2 per video |
| Lapisan gambar (`masuk` + `hidup`) | di tiap lapisan `gambar` | satu bagian paling hidup per adegan; sisanya gerak kecil. Jangan semua `putar`/`pop` |
| Kontras ritme | adegan `potong` + kamera `diam` sebelum momen besar | diam membuat sentakan berikutnya terasa |

## 5. Efek: mana yang wajar, mana ciri AI

| Efek | Status |
|---|---|
| Fade di semua teks | Ciri AI: semua terasa lembek dan terlambat. Skill ini sudah tidak memakainya. |
| Blur-in pada teks | Ciri template. Blur hanya untuk gerak cepat (whip), bukan untuk muncul. |
| Bola cahaya melayang, latar gradien radial, teks shimmer | Ciri halaman promosi AI. Jangan ditambahkan. |
| Garis bawah judul, pil/chip label, grid atau pita garis hiasan | Ciri template AI. Sudah dibuang dari skill ini; jangan dikembalikan lewat gambar. |
| Ikon umum (bola lampu, roket, roda gigi, centang) sebagai ilustrasi | Ciri AI. Gambar benda/kejadian yang benar-benar disebut di adegan. |
| Sorotan di semua kata subtitle | Kalau semua disorot, tidak ada yang penting. Maksimal 1 frasa per kalimat. |
| Potongan keras (cut) tepat di kata yang diucapkan | Wajar, murah, dan jarang dipakai AI. Utamakan. |
| Motion blur saat kamera menyapu | Wajar: begitulah kamera sungguhan. |
| Grain, aberasi kromatik, vignette (`"tekstur"`) | Pilihan gaya, bukan kewajiban. Untuk tampilan bersih/teknis: `"tekstur": false`. |
| Pantulan (overshoot) | Pilihan, bukan hiasan. Di semua judul terlihat murahan; video edukasi cukup di 1–3 poin penting. |

## 6. Periksa sebelum menunjukkan rencana

- Baca tiap `ucapan` lalu lihat gambarnya: apakah setiap benda yang disebut ada di gambar, dan datang `saat` katanya diucapkan?
- Adakah gambar yang tampil lebih dari 8 detik tanpa bagian baru yang datang? Pecah adegannya.
- Adakah adegan yang gambarnya satu lapisan diam? Pecah jadi bagian yang bergerak sendiri.
- Adakah dua adegan berurutan dengan susunan gerak lapisan yang persis sama? Bedakan arah datang dan jenis `hidup`-nya.
- Berapa adegan yang `masuk`-nya bukan `potong`? Kalau lebih dari separuh, kurangi.
- Hitung alatnya: lebih dari satu transisi `zoom`, lebih dari dua `slam`, atau alat di setiap adegan = terlalu banyak.
- Dua adegan berurutan memakai gerak besar yang sama? Selingi dengan adegan tenang.
- Judul yang berupa perintah/nama file/kutipan sudah `ketik`?
- Apakah video ini bergerak berbeda dari video sebelumnya, atau hanya menyalin rencana lama?
