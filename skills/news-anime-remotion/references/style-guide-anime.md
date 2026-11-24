# Style Guide: Dynamic 2D Sports-Manga Anime

Gunakan panduan ini sebagai standar gaya visual tunggal untuk semua prompt Flow agar seluruh karakter, properti, dan latar belakang dari episode berbeda tetap terlihat berasal dari satu dunia animasi yang sama.

## 1. Core Style Tokens (Wajib Ada di Setiap Prompt)

Sisipkan blok gaya berikut secara konsisten:

- **Character & Props Base:** `dynamic 2D Japanese sports anime style, modern shonen manga aesthetic, bold clean black ink lineart, crisp high-contrast cel shading, vibrant athletic colors, sharp expressive eyes, Studio MAPPA and Blue Lock inspired energy, flat 2D illustration, no 3D render, no photorealism`
- **Background Base:** `dynamic 2D Japanese anime background art, dramatic cinematic lighting, crisp cel-shaded architecture, subtle halftone speedlines, vibrant sky and rim light, vertical 9:16 framing, no characters in frame`

## 2. Transparent-Ready Isolation Rules (Untuk Remotion)

Karena aset karakter dan properti akan dianimasikan secara terpisah di Remotion, hindari latar ramai pada aset modular:

- **Karakter & Properti:** Tambahkan `isolated full-body character` (atau `waist-up character`), `centered composition, solid pure white #FFFFFF background, clean sharp outline edges, no background scenery, no floor shadow, no text, no watermark`.
- **Alternatif untuk objek dominan putih** (misal bola atau jersey putih): Ganti latar menjadi `solid bright chroma green #00FF00 background` agar proses *remove background* tetap bersih.

## 3. Character Consistency Formula

Untuk menjaga satu tokoh tetap mirip di berbagai ekspresi dan episode:

1. Kunci **Character Anchor** (simpan di `asset-registry.json` field `styleAnchor`): deskripsi usia, bentuk rambut, warna rambut, ciri wajah (misal janggut tipis, bentuk alis), warna jersey/pakaian, dan nomor punggung.
2. Saat membuat ekspresi baru, salin `styleAnchor` secara persis dan hanya ubah bagian `[POSE & EXPRESSION]`.
3. Batasi maksimal 3 ekspresi standar per tokoh:

- `action`: pose bergerak, fokus, tatapan tajam.
- `celebrate`: pose penuh emosi, tangan mengepal, aura energi.
- `dramatic`: kaget, kecewa, atau tersenyum tipis penuh ironi.

## 4. Reusable Prop & FX Library

Prioritaskan membuat properti umum sekali saja agar bisa dipakai ulang di berbagai berita:

- `prop-red-card`: tangan wasit mengangkat kartu merah menyala dengan efek garis kejut manga.
- `prop-var-monitor`: layar monitor VAR bergaya anime dengan bingkai neon biru.
- `prop-breaking-banner`: pita *breaking news* bergaya komik Jepang.
- `fx-speedlines-radial`: garis kecepatan radial hitam-putih untuk transisi klimaks.
- `fx-fire-aura`: aura api energi untuk momen *comeback* atau rekor baru.

## 5. Aspect Ratio Standards

- **Karakter (waist-up / full-body):** `1:1` atau `3:4`
- **Properti & Emblem:** `1:1`
- **Latar Belakang & Adegan Penuh:** `9:16`
