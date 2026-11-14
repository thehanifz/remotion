import {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

/**
 * Font emoji bundled (Noto Color Emoji v2.042, OFL-1.1).
 *
 * Kenapa dibundel: render di mesin Linux tanpa font emoji sistem
 * menampilkan emoji sebagai kotak (kasus video bulutangkis v01 di
 * CasaOS, 14 Nov 2026). Dengan font ini di public/fonts/, Chromium
 * memuatnya langsung dari proyek — Linux, Windows, dan CasaOS
 * me-render emoji yang sama persis tanpa instalasi sistem.
 *
 * File font: public/fonts/NotoColorEmoji.ttf (biner, ~10,5 MB).
 * File itu TIDAK bisa di-push lewat konektor GitHub (hanya teks),
 * jadi ditambahkan manual dari laptop. Bila file belum ada, render
 * tetap jalan memakai font emoji sistem (bila ada) dan peringatan
 * tampil di konsol.
 *
 * Supaya emoji memakai font ini, sertakan 'Noto Color Emoji' di
 * fontFamily setiap teks, mis. lewat FONT_STACK di bawah.
 */

export const EMOJI_FONT_FAMILY = 'Noto Color Emoji';

/** Stack font teks SkorNalar: font utama + fallback emoji bundled. */
export const FONT_STACK = `'Noto Sans', '${EMOJI_FONT_FAMILY}', sans-serif`;

let fontPromise: Promise<void> | null = null;

function loadEmojiFont(): Promise<void> {
  if (fontPromise) {
    return fontPromise;
  }
  fontPromise = (async () => {
    const face = new FontFace(
      EMOJI_FONT_FAMILY,
      `url(${staticFile('fonts/NotoColorEmoji.ttf')})`,
    );
    const loaded = await face.load();
    document.fonts.add(loaded);
  })().catch((err: unknown) => {
    console.warn(
      '[SkorNalar] Font emoji bundled tidak termuat. ' +
        'Pastikan public/fonts/NotoColorEmoji.ttf ada di repo. ' +
        'Render lanjut dengan font emoji sistem bila tersedia.',
      err,
    );
  });
  return fontPromise;
}

/**
 * Muat font emoji sebelum frame pertama di-render.
 * Dipanggil sekali di RemotionRoot; render ditahan sampai font
 * siap (atau dipastikan tidak ada) lewat delayRender/continueRender.
 */
export const useEmojiFont = (): void => {
  const [handle] = useState(() => delayRender('Menunggu font emoji'));
  useEffect(() => {
    loadEmojiFont().then(() => continueRender(handle));
  }, [handle]);
};
