# Font emoji bundled — Noto Color Emoji

File yang harus ada di folder ini:

- `NotoColorEmoji.ttf` — versi 2.042, 10.980.856 byte,
  SHA-256 `e5899ed38b8ed83e08bd3ac5de09791e9d19d288333a796de1d35ad17396f1ec`
  (sama persis dengan font di CasaOS dari paket Debian
  `fonts-noto-color-emoji` 2.042).

Lisensi: SIL Open Font License 1.1, lihat `OFL.txt` di folder ini.
Redistribusi diizinkan selama lisensi ini ikut disertakan.

## Kenapa dibundel

Render Remotion di mesin Linux tanpa font emoji sistem menampilkan
semua emoji sebagai kotak (kasus video bulutangkis v01, 14 Nov 2026).
Font ini dimuat langsung dari proyek oleh `src/emojiFont.ts`
(FontFace API), sehingga Linux, Windows, dan CasaOS me-render emoji
yang sama persis tanpa instalasi font di sistem.

## Bila file belum ada

Render tetap jalan memakai font emoji sistem bila tersedia
(mis. Segoe UI Emoji di Windows) dan peringatan tampil di konsol.
Di mesin Linux tanpa font emoji sistem, emoji akan jadi kotak
sampai file ini ditambahkan.

## Menambahkan file

File ini biner dan tidak bisa di-push lewat konektor GitHub
(hanya file teks). Tambahkan dari laptop:

1. Salin `NotoColorEmoji.ttf` ke folder ini.
2. `git add public/fonts/NotoColorEmoji.ttf`
3. Commit + push seperti biasa.
