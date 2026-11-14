"""Video animasi teks dari VO mp3 + rencana adegan (JSON). Hanya butuh Python, Pillow, dan FFmpeg.

Pakai:  python buat_video.py rencana.json [--preview] [--out FOLDER]
        python buat_video.py --uji      (cek logika pembagian waktu)
"""
import json, math, os, re, shutil, subprocess, sys, tempfile
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FPS = 30
UKURAN = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
# posisi relatif tinggi layar; 9:16 dijaga di zona aman Reels/Shorts (y 15%-75%)
TATA = {"9:16": dict(progres=0.16, isi=0.30, sub=0.68, judul_px=120, sub_px=58, ket_px=52, margin=90, sub_maks=32),
        "16:9": dict(progres=0.07, isi=0.22, sub=0.86, judul_px=110, sub_px=48, ket_px=46, margin=160, sub_maks=42)}
TEMA = {"latar": "#1C1C1C", "aksen": "#FF7A00", "aksen2": "#FFD400", "teks": "#FFFFFF", "redup": "#B8B8B8"}
DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG = shutil.which("ffmpeg") or sys.exit("FFmpeg tidak ditemukan.")
KAMERA = ("dorong", "tarik", "fokus", "diam")  # gerak kamera dalam adegan
TRANSISI = ("potong", "whip", "zoom")         # cara adegan MASUK
PENANDA = ("titik", "truk", "tidak")          # elemen continuity yang berjalan di bar progres
MASUK = ("pop", "potong", "ketik", "slam")    # cara JUDUL datang (LIBRARY.md bagian 3)
LMASUK = ("potong", "bawah", "atas", "kiri", "kanan", "pop")   # cara tiap LAPISAN gambar datang
HIDUP = ("diam", "apung", "ayun", "napas", "putar", "geser")  # gerak terus-menerus tiap lapisan gambar
REACT = (0, 4, 9, 15, 22, 30)  # jeda antar-lapisan (frame @60 fps): tidak rata, seperti rantai sebab-akibat
TR = 0.22  # setengah durasi transisi (detik) di tiap sisi batas adegan
# SFX sintetis (bebas lisensi), dibuat FFmpeg saat render
SFX = {
    "whoosh": "anoisesrc=color=pink:d=0.45:a=0.6:seed=7,bandpass=f=1800:w=1.2,afade=t=in:d=0.2:curve=qsin,afade=t=out:st=0.2:d=0.25:curve=qsin",
    "pop": "sine=f=520:d=0.09,afade=t=out:d=0.09:curve=exp",
    "tick": "sine=f=2200:d=0.025,afade=t=out:d=0.025",
    "ding": "aevalsrc='0.35*sin(2*PI*1320*t)*exp(-6*t)+0.2*sin(2*PI*1980*t)*exp(-8*t)':d=0.7",
    "thud": "aevalsrc='0.9*sin(2*PI*65*t)*exp(-14*t)':d=0.35",
    "riser": "aevalsrc='0.3*sin(2*PI*(200*t+875*t*t))*t/0.8':d=0.8,highpass=f=250",
    "error": "aevalsrc='0.25*sgn(sin(2*PI*120*t))*(lt(t,0.14)+between(t,0.2,0.34))':d=0.36,lowpass=f=2500",
    # lapis sub-bass: bobot saat sesuatu mendarat (pelan, terasa lebih dari terdengar)
    "sub": "aevalsrc='0.9*sin(2*PI*48*t)*exp(-7*t)':d=0.6,lowpass=f=150",
    # lapis high-end: klik mekanis kecil untuk detail
    "klik": "aevalsrc='0.5*sin(2*PI*3200*t)*exp(-120*t)':d=0.04",
}


def cari_font(nama):
    f = os.path.join(DIR, "fonts", nama)  # pengguna boleh menaruh judul.ttf / isi.ttf sendiri
    if os.path.exists(f):
        return f
    if shutil.which("fc-match"):
        r = subprocess.run(["fc-match", "-f", "%{file}", "sans:bold"], capture_output=True, text=True)
        if r.stdout and os.path.exists(r.stdout):
            return r.stdout
    return next((p for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf")
                 if os.path.exists(p)), None)


FONT_JUDUL, FONT_ISI = cari_font("judul.ttf"), cari_font("isi.ttf")
def font(path, px):
    return ImageFont.truetype(path, px) if path else ImageFont.load_default(px)


def analisis_audio(audio):
    """Durasi + daftar jeda (diam) dari FFmpeg silencedetect."""
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", audio, "-af", "silencedetect=noise=-35dB:d=0.2",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        sys.exit(f"Audio tidak terbaca: {audio}")
    durasi = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    awal = [max(0.0, float(x)) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    akhir = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    akhir += [durasi] * (len(awal) - len(akhir))  # diam sampai file habis
    return durasi, list(zip(awal, akhir))


def filter_loudnorm(audio):
    """Ukur loudness, naikkan/turunkan tepat ke -14 LUFS, lalu limiter memotong puncak.
    loudnorm biasa tertahan puncak VO dan berhenti di -15/-16 LUFS; limiter juga mengurangi loudness,
    jadi hasil rantai diukur ulang dan volume dikoreksi."""
    def rantai(g):  # limit 0.79 = -2 dBFS: sisa ruang untuk true peak & encode AAC, hasil tetap < -1 dBTP
        return f"aresample=192000,volume={g:.2f}dB,alimiter=limit=0.79:level=false,aresample=48000"
    def ukur(af):
        r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", audio, "-af", f"{af}loudnorm=print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True)
        return float(json.loads(re.findall(r"\{[^{}]+\}", r.stderr)[-1])["input_i"])
    g = -14 - ukur("")
    for _ in range(2):
        g += -14 - ukur(rantai(g) + ",")
    return rantai(g)


def bagi_waktu(bobot, jeda, t0, t1, toleransi=2.0):
    """Batas antar bagian: perkiraan proporsional panjang teks, lalu digeser ke jeda TERPANJANG di sekitarnya
    (jeda antar-kalimat lebih panjang dari jeda dalam kalimat). Perkiraan berikutnya dihitung dari batas terakhir.
    shortcut: tanpa transkrip per kata, kalimat yang sangat cepat/lambat bisa meleset < toleransi detik."""
    mulai, akhir = t0, t1
    for a, b in jeda:
        if a <= mulai + 0.05 < b: mulai = b
        if a < akhir - 0.05 <= b: akhir = a
    if akhir <= mulai:
        mulai, akhir = t0, t1
    dalam = [((a + b) / 2, b - a) for a, b in jeda if mulai < a and b < akhir]
    batas, sisa, pos = [t0], sum(bobot), mulai
    for w in bobot[:-1]:
        t = pos + (akhir - pos) * w / sisa
        calon = [(m, p) for m, p in dalam if abs(m - t) <= toleransi and m > batas[-1]]
        if calon:
            t = max(calon, key=lambda c: (round(c[1], 1), -abs(c[0] - t)))[0]
        batas.append(t)
        sisa, pos = sisa - w, t
    return batas + [t1]


def potong_sub(teks, maks):
    hasil, cur = [], ""
    for k in teks.split():
        if cur and len(cur) + 1 + len(k) > maks:
            hasil.append(cur); cur = k
        else:
            cur = (cur + " " + k).strip()
        if cur.endswith((".", "?", "!")) and len(cur) > maks // 2:
            hasil.append(cur); cur = ""
    return hasil + [cur] if cur else hasil


def tandai(teks):
    """"Tanah pucuk *tidak dibuang*." -> ("Tanah pucuk tidak dibuang.", [False, False, True, True]). Tanda * = kata penting."""
    kata, penting, nyala = [], [], False
    for k in teks.split():
        n = k.count("*")
        penting.append(nyala or n > 0)
        nyala ^= n % 2 == 1
        kata.append(k.replace("*", ""))
    return " ".join(kata), penting


def bungkus(teks, fnt, maks_px):
    baris, cur = [], ""
    for k in teks.split():
        coba = (cur + " " + k).strip()
        if cur and fnt.getlength(coba) > maks_px:
            baris.append(cur); cur = k
        else:
            cur = coba
    return baris + [cur] if cur else baris


def gambar_teks(baris, fnt, warna, stroke=0):
    asc, desc = fnt.getmetrics()
    tinggi = int((asc + desc) * 1.12)
    lebar = int(max(fnt.getlength(b) for b in baris)) + stroke * 2 + 4
    img = Image.new("RGBA", (lebar, tinggi * len(baris) + stroke * 2 + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, b in enumerate(baris):
        d.text(((lebar - fnt.getlength(b)) / 2, i * tinggi + stroke + 2), b, font=fnt, fill=warna,
               stroke_width=stroke, stroke_fill="black")
    return img


def kata_sub(baris, penting, fnt):
    """Subtitle per kata: ([(gambar, x, y, bobot)], (lebar, tinggi) blok). Kata penting = kotak kuning + teks gelap,
    sisanya putih ber-outline. penting = satu bool per kata, berurutan. bobot = perkiraan lama kata diucapkan."""
    asc, desc = fnt.getmetrics()
    th, tinggi = asc + desc + 12, int((asc + desc) * 1.3)
    lebar = int(max(fnt.getlength(b) for b in baris)) + 40
    hasil, k = [], 0
    for i, b in enumerate(baris):
        x = (lebar - fnt.getlength(b)) / 2
        for kata in b.split():
            w = int(fnt.getlength(kata)) + 16
            im = Image.new("RGBA", (w, th), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            if penting[k]:  # kotak bersebelahan saling bersentuhan, jadi frasa penting terlihat satu kotak
                d.rounded_rectangle([0, 3, w - 1, th - 3], radius=10, fill=TEMA["aksen2"])
                d.text((8, 6), kata, font=fnt, fill=TEMA["latar"])
            else:
                d.text((8, 6), kata, font=fnt, fill=TEMA["teks"], stroke_width=5, stroke_fill="black")
            hasil.append((im, int(x) - 8, i * tinggi + 4, len(kata) + 1))
            x += fnt.getlength(kata) + fnt.getlength(" ")
            k += 1
    return hasil, (lebar, tinggi * len(baris) + 20)


def judul_pas(teks, maks_px, px):
    while True:  # kecilkan sampai muat <= 3 baris
        fnt = font(FONT_JUDUL, px)
        baris = bungkus(teks, fnt, maks_px)
        if px <= 40 or (len(baris) <= 3 and max(fnt.getlength(b) for b in baris) <= maks_px):
            img = gambar_teks(baris, fnt, TEMA["teks"])
            img.info["baris"] = len(baris)  # dipakai "ketik" untuk membuka baris satu per satu
            return img
        px = int(px * 0.9)


# --- gerak ---
def bezier(x1, y1, x2, y2):
    """Kurva easing cubic-bezier (sama seperti grafik kecepatan After Effects / CSS)."""
    def f(x):
        if x <= 0 or x >= 1:
            return 0.0 if x <= 0 else 1.0
        a, b = 0.0, 1.0
        for _ in range(25):  # cari t dengan bagi dua: bx(t) = x
            t = (a + b) / 2
            bx = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3
            a, b = (t, b) if bx < x else (a, t)
        t = (a + b) / 2
        return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3
    return f
# Easy Ease dengan influence tinggi (±80% masuk / 85% keluar): mulai halus, berhenti dengan rem panjang, tidak kaku
ease_io = bezier(0.8, 0, 0.15, 1)
def pegas_kamera(t, hz=1.6, redam=0.75):
    """Kamera yang punya berat: mulai dari diam (kecepatan 0), lewat sedikit (±3%), lalu mengendap."""
    if t <= 0:
        return 0.0
    w = 2 * math.pi * hz
    wd = w * math.sqrt(1 - redam ** 2)
    return 1 - math.exp(-redam * w * t) * (math.cos(wd * t) + redam * w / wd * math.sin(wd * t))
def zoom_kamera(jenis, ta, durasi, maks=1.32):
    """Zoom kamera di dalam adegan, antara 1 (tepi layar tidak pernah kosong) dan maks (isi tetap muat di layar)."""
    p = ta / max(0.01, durasi)
    pelan = min(0.07, maks - 1)
    if jenis == "dorong":
        return 1 + pelan * ease_io(p)
    if jenis == "tarik":
        return 1 + pelan * (1 - ease_io(p))
    if jenis == "fokus":  # mendekat ke judul setelah judul muncul, mendarat dengan pegas, lalu bertahan
        return 1 + (maks - 1) * pegas_kamera(ta - 0.7)
    return 1.0
# Kurva bernama (LIBRARY.md bagian 2): angka cubic-bezier yang sama dengan CSS / grafik kecepatan After Effects.
# Hanya kurva yang cocok untuk gerak MASUK (berakhir diam). Dipilih lewat "kurva" di rencana.json.
KURVA = {
    "kit.land": (0.1, 0.75, 0.15, 1), "kit.heavy": (0.75, 0, 0.18, 1), "kit.whip": (0.85, 0, 0.15, 1),
    "kit.reveal": (0.22, 1, 0.36, 1), "kit.drift": (0.4, 0, 0.6, 1),
    "easings.outSine": (0.61, 1, 0.88, 1), "easings.outQuad": (0.5, 1, 0.89, 1), "easings.outCubic": (0.33, 1, 0.68, 1),
    "easings.outQuart": (0.25, 1, 0.5, 1), "easings.outQuint": (0.22, 1, 0.36, 1), "easings.outExpo": (0.16, 1, 0.3, 1),
    "easings.outCirc": (0, 0.55, 0.45, 1), "easings.outBack": (0.34, 1.56, 0.64, 1),
    "m3.standard": (0.2, 0, 0, 1), "m3.standardDecelerate": (0, 0, 0, 1), "m3.emphasizedDecelerate": (0.05, 0.7, 0.1, 1),
    "carbon.productive.entrance": (0, 0, 0.38, 0.9), "carbon.expressive.entrance": (0, 0, 0.3, 1),
}
kurva_slam = bezier(*KURVA["kit.heavy"])  # judul "slam": menggantung besar, lalu mendarat tegas
# kepribadian gerak (motion personality), satu untuk seluruh video:
# kurva masuk (ease-out kuat = entri cepat, henti halus), durasi masuk (dtk), pegas pop (hz, redaman), pengali jeda antar-elemen
RASA = {
    "tegas": (bezier(0.16, 1, 0.3, 1), 0.35, (2.2, 0.55), 1.0),      # informatif/urgent (default), pantul ±12%
    "mewah": (bezier(0.25, 0.1, 0.1, 1), 0.7, (1.2, 0.9), 1.6),      # pelan, anggun, hampir tanpa pantul
    "teknologi": (bezier(0.05, 0.9, 0.1, 1), 0.25, (3.0, 0.65), 0.7),  # cepat, presisi, rapat
    "ceria": (bezier(0.34, 1.56, 0.64, 1), 0.45, (1.8, 0.35), 1.2),  # memantul (kurva lewat 100%)
}
G = dict(zip(("kurva", "durasi", "pegas", "jeda"), RASA["tegas"]))
def ease(x):
    return G["kurva"](min(max(x, 0.0), 1.0))
def redup(img, a):
    if a >= 1:
        return img
    im = img.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


def siapkan(rencana, durasi, jeda):
    W, H = UKURAN[rencana["format"]]
    L = TATA[rencana["format"]]
    adegan = rencana["adegan"]
    batas = bagi_waktu([len(tandai(a["ucapan"])[0]) for a in adegan], jeda, 0.0, durasi)
    lebar_isi = W - 2 * L["margin"]
    hasil, subs = [], []
    for i, a in enumerate(adegan):
        t0, t1 = batas[i], batas[i + 1]
        bersih, penting = tandai(a["ucapan"])
        potongan = potong_sub(bersih, L["sub_maks"])
        bt = bagi_waktu([len(p) for p in potongan], jeda, t0, t1, toleransi=0.8)
        ucap = []  # (kata, perkiraan detik diucapkan): dipakai subtitle per kata dan lapisan gambar ber-"saat"
        for j, p in enumerate(potongan):  # potong_sub tidak mengubah urutan kata, jadi tanda penting dibagi per jumlah kata
            kata = p.split()
            subs.append((bt[j], bt[j + 1], p, penting[:len(kata)]))
            penting = penting[len(kata):]
            total, jalan = sum(len(k) + 1 for k in kata), 0
            for k in kata:  # rumus yang sama dengan subtitle per kata di buat_bingkai
                ucap.append((re.sub(r"\W", "", k.lower()), bt[j] + (bt[j + 1] - bt[j]) * 0.85 * jalan / total))
                jalan += len(k) + 1
        el, y = [], int(H * (L["isi"] - (0.10 if a.get("gambar") else 0)))
        fokus, lebar_judul, j = (W / 2, H * 0.4), 1, G["jeda"]
        batas_bawah = H * L["sub"] - L["sub_px"] * 1.4 - 20  # isi paling bawah tidak boleh menabrak subtitle
        if a.get("label"):  # kicker polos huruf besar warna aksen
            fnt = font(FONT_ISI, int(L["ket_px"] * 0.8))
            img = gambar_teks([a["label"].upper()], fnt, TEMA["aksen"])
            el.append(dict(img=img, x=(W - img.width) // 2, y=y, gerak="geser", tunda=0.0)); y += img.height + 28
        awal_teks, y_gbr = len(el), y
        if a.get("judul"):
            img = judul_pas(a["judul"], lebar_isi, int(L["judul_px"] * (0.8 if a.get("gambar") else 1)))  # judul mengalah ke gambar
            el.append(dict(img=img, x=(W - img.width) // 2, y=y, gerak=a.get("masuk", "pop"), tunda=0.08 * j,
                           huruf=len(a["judul"])))
            fokus, lebar_judul = (W / 2, y + img.height / 2), img.width; y += img.height + 30
        if a.get("keterangan"):
            fnt = font(FONT_ISI, L["ket_px"])
            img = gambar_teks(bungkus(a["keterangan"], fnt, lebar_isi), fnt, TEMA["redup"])
            el.append(dict(img=img, x=(W - img.width) // 2, y=y, gerak="potong", tunda=0.25 * j)); y += img.height
        if a.get("gambar"):  # ilustrasi berlapis di atas teks, setinggi ruang yang tersisa
            sisa = min(H * (0.3 if a.get("judul") else 0.42), batas_bawah - y - 40)
            if sisa < 120:
                sys.exit(f"Adegan {i + 1}: tidak cukup ruang untuk gambar. Perpendek judul atau keterangan.")
            lapis = [Image.open(l["file"]).convert("RGBA") for l in a["gambar"]]
            kw, kh = lapis[0].size
            if any(im.size != (kw, kh) for im in lapis):
                sys.exit(f"Adegan {i + 1}: semua lapisan gambar harus berukuran sama (kanvas yang sama).")
            kotak = [im.getbbox() for im in lapis if im.getbbox()] or [(0, 0, kw, kh)]
            tepi = (min(k[0] for k in kotak), min(k[1] for k in kotak), max(k[2] for k in kotak), max(k[3] for k in kotak))
            lapis = [im.crop(tepi) for im in lapis]  # buang tepi kosong kanvas supaya benda mengisi ruang yang ada
            kw, kh = lapis[0].size
            f = min(lebar_isi / kw, sisa / kh, 1)
            gw, gh = int(kw * f), int(kh * f)
            bagian = []
            for n, (im, l) in enumerate(zip(lapis, a["gambar"])):
                im = im.resize((gw, gh), Image.LANCZOS)
                box = im.getbbox() or (0, 0, gw, gh)  # tiap lapisan dipotong ke isinya; putar/skala berpusat di tengah isi
                tunda = REACT[min(n, 5)] / 60
                if l.get("saat"):  # lapisan datang tepat saat kata/frasa itu diucapkan, supaya gambar mengikuti suara
                    kunci = [re.sub(r"\W", "", k.lower()) for k in l["saat"].split()]
                    kena = [ucap[m][1] for m in range(len(ucap)) if [k for k, _ in ucap[m:m + len(kunci)]] == kunci]
                    if not kena:
                        sys.exit(f"Adegan {i + 1}: \"saat\": \"{l['saat']}\" tidak ada di ucapan adegan ini.")
                    tunda = max(0.0, kena[0] - t0 - 0.15)  # mendarat sedikit sebelum katanya terdengar
                bagian.append(dict(img=im.crop(box), cx=(box[0] + box[2]) / 2, cy=(box[1] + box[3]) / 2, fase=n * 1.7,
                                   masuk=l.get("masuk", "potong"), hidup=l.get("hidup", "diam"), tunda=tunda))
            turun = max(0, int(batas_bawah - y - gh - 40) // 2)  # gambar + teks ditaruh di tengah ruang yang ada
            for e in el[awal_teks:]:
                e["y"] += gh + 40 + turun
            y += gh + 40 + turun
            if a.get("judul"):
                fokus = (fokus[0], fokus[1] + gh + 40 + turun)
            else:
                fokus, lebar_judul = (W / 2, y_gbr + turun + gh / 2), gw
            el.insert(awal_teks, dict(lapis=bagian, x=(W - gw) // 2, y=y_gbr + turun, gerak="lapis", tunda=0.0))
        # zoom maksimum: judul tetap muat selebar layar dan isi paling bawah tidak menabrak subtitle
        maks = max(1.0, min(1.32, (W - 60) / lebar_judul, (batas_bawah - fokus[1]) / max(1, y - fokus[1])))
        hasil.append(dict(t0=t0, t1=t1, el=el, fokus=fokus, maks=maks, kamera=a.get("kamera") or ("dorong", "tarik")[i % 2],
                          transisi=a.get("transisi", "potong") if i else "potong", sfx=a.get("sfx", [])))
    return hasil, subs


def kamera(img, z, fx, fy, dx=0.0, blur=0):
    """Zoom z dengan titik fokus (fx,fy) tetap di tempat, geser dx px, blur gerak horizontal."""
    W, H = img.size
    if abs(z - 1) > 1e-3 or abs(dx) > 0.5:
        img = img.transform((W, H), Image.AFFINE, (1 / z, 0, fx - (fx + dx) / z, 0, 1 / z, fy - fy / z), resample=Image.BILINEAR,
                            fillcolor=TEMA["latar"])
    if blur > 1:  # motion blur horizontal murah: kecilkan lebar lalu besarkan lagi
        img = img.resize((max(8, int(W / blur)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    return img


def gambar_truk(d, x, y, s, warna):
    """Dump truck sederhana (bak + kabin + 2 roda), titik (x,y) = tengah bawah roda."""
    r = 9 * s
    d.polygon([(x - 34 * s, y - 32 * s), (x + 6 * s, y - 32 * s), (x + 2 * s, y - 14 * s), (x - 30 * s, y - 14 * s)], fill=warna)
    d.rectangle([x + 8 * s, y - 30 * s, x + 26 * s, y - 14 * s], fill=warna)
    d.rectangle([x + 12 * s, y - 27 * s, x + 22 * s, y - 21 * s], fill="#3A4A55")
    for cx in (x - 22 * s, x + 16 * s):
        d.ellipse([cx - r, y - 2 * r, cx + r, y], fill="#111111")


def siapkan_finishing(W, H):
    """Bahan finishing (dihitung sekali): vignette, 4 lembar grain, dan LUT grade (kontras S + hangat tipis)."""
    v = Image.radial_gradient("L").resize((W, H), Image.BILINEAR).point(lambda x: 255 - int(x * 0.32))
    vign = Image.merge("RGB", (v, v, v))
    grain = [Image.merge("RGB", (g, g, g)) for g in
             (Image.effect_noise((W // 2, H // 2), 30).resize((W, H), Image.BILINEAR) for _ in range(4))]
    def kurva(x, geser):
        y = x / 255
        y = y + 0.08 * math.sin(2 * math.pi * (y - 0.5)) * (y * (1 - y)) * 4 / 2  # S lembut: bayangan turun, terang naik
        return min(255, max(0, int(y * 255 + geser * y)))
    lut = [kurva(x, 6) for x in range(256)] + [kurva(x, 0) for x in range(256)] + [kurva(x, -6) for x in range(256)]
    return vign, grain, lut


def finishing(img, bahan, k):
    """Kesan film: aberasi kromatik 1 px, vignette, grain bergerak, color grade."""
    vign, grain, lut = bahan
    r, g, b = img.split()
    img = Image.merge("RGB", (ImageChops.offset(r, 1, 0), g, ImageChops.offset(b, -1, 0)))
    img = ImageChops.multiply(img, vign)
    img = Image.blend(img, grain[k % len(grain)], 0.05)
    return img.point(lut)


def buat_bingkai(rencana, adegan, subs, cache_sub):
    W, H = UKURAN[rencana["format"]]
    L = TATA[rencana["format"]]
    latar = Image.new("RGB", (W, H), TEMA["latar"])
    sub_fnt = font(FONT_ISI, L["sub_px"])
    pakai_sub = rencana.get("subtitle", True)
    penanda = rencana.get("penanda", "tidak")
    bahan = siapkan_finishing(W, H) if rencana.get("tekstur", True) else None

    def konten(a, t):
        img = latar.copy()
        ta = t - a["t0"]
        for e in a["el"]:
            u = ta - e["tunda"]
            if u < 0:
                continue
            if e["gerak"] == "lapis":  # tiap lapisan datang sendiri lalu terus bergerak sendiri (fase berbeda)
                for l in e["lapis"]:
                    v = u - l["tunda"]
                    if v < 0:
                        continue
                    im, m, h = l["img"], l["masuk"], l["hidup"]
                    k = 1 - ease(v / 0.45)  # sisa jarak masuk
                    dx = {"kiri": -160, "kanan": 160}.get(m, 0) * k
                    dy = {"atas": -160, "bawah": 160}.get(m, 0) * k
                    sk = pegas_kamera(v, 2.2, 0.6) if m == "pop" else 1.0
                    putar = 0.0
                    if h == "apung":
                        dy += 10 * math.sin(v * 2.2 + l["fase"])
                    elif h == "geser":
                        dx += 14 * math.sin(v * 1.6 + l["fase"])
                    elif h == "ayun":
                        putar = 4 * math.sin(v * 2.6 + l["fase"])
                    elif h == "napas":
                        sk *= 1 + 0.04 * math.sin(v * 3 + l["fase"])
                    elif h == "putar":
                        putar = -120 * v
                    if sk < 0.03:
                        continue
                    if putar:
                        im = im.rotate(putar, resample=Image.BICUBIC, expand=True)
                    if abs(sk - 1) > 0.004:
                        im = im.resize((max(1, int(im.width * sk)), max(1, int(im.height * sk))), Image.BILINEAR)
                    img.paste(im, (int(e["x"] + l["cx"] + dx - im.width / 2), int(e["y"] + l["cy"] + dy - im.height / 2)), im)
            elif e["gerak"] == "potong":  # langsung hadir, tanpa fade
                img.paste(e["img"], (e["x"], e["y"]), e["img"])
            elif e["gerak"] == "ketik":  # terbuka per huruf (bertangga), baris demi baris
                # shortcut: lebar per huruf dianggap rata dan baris dihitung dari tepi kiri blok; ganti ke gambar per huruf kalau terlihat kasar
                im, nb = e["img"], e["img"].info["baris"]
                lh, langkah = im.height / nb, max(1, e["huruf"] // nb)
                p = min(1.0, u / (0.03 * e["huruf"])) * nb
                penuh = int(p)
                lebar = im.width * int((p - penuh) * langkah) // langkah
                for box in ((0, 0, im.width, int(penuh * lh)), (0, int(penuh * lh), lebar, int(min(nb, penuh + 1) * lh))):
                    if box[2] > box[0] and box[3] > box[1]:
                        c = im.crop(box)
                        img.paste(c, (e["x"] + box[0], e["y"] + box[1]), c)
            elif e["gerak"] in ("pop", "slam"):
                s = pegas_kamera(u, *G["pegas"]) if e["gerak"] == "pop" else 2.2 - 1.2 * kurva_slam(u / 0.3)
                if abs(s - 1) < 0.002:
                    img.paste(e["img"], (e["x"], e["y"]), e["img"])
                elif s > 0.02:
                    im = e["img"].resize((max(1, int(e["img"].width * s)), max(1, int(e["img"].height * s))), Image.BILINEAR)
                    img.paste(im, (e["x"] + (e["img"].width - im.width) // 2, e["y"] + (e["img"].height - im.height) // 2), im)
            else:  # geser (label)
                k = ease(u / G["durasi"])
                im = redup(e["img"], min(1.0, max(0.0, k)))
                img.paste(im, (e["x"] + int((1 - k) * -200), e["y"]), im)
        return img

    def dengan_kamera(i, t, z_ekstra=1.0, dx=0.0, blur=0):
        a = adegan[i]
        ta = max(0.0, t - a["t0"])
        z = zoom_kamera(a["kamera"], ta, a["t1"] - a["t0"], a["maks"]) * z_ekstra
        return kamera(konten(a, t), z, *a["fokus"], dx, blur)

    def bingkai(t):
        si = max(i for i, a in enumerate(adegan) if a["t0"] <= t or i == 0)
        a = adegan[si]
        # transisi di sekitar batas adegan: adegan lama keluar TR detik sebelum batas, adegan baru masuk TR detik sesudahnya
        nxt = adegan[si + 1] if si + 1 < len(adegan) else None
        jenis = None
        if nxt and nxt["transisi"] != "potong" and t > nxt["t0"] - TR:
            jenis, q, keluar = nxt["transisi"], (t - nxt["t0"]) / TR, True
        elif a["transisi"] != "potong" and t < a["t0"] + TR:
            jenis, q, keluar = a["transisi"], (t - a["t0"]) / TR, False
        if jenis == "whip":  # kamera menyapu cepat ke kiri: lama keluar ke kiri, baru masuk dari kanan
            g = ease_io((q + 1) / 2)
            img = dengan_kamera(si, t, dx=-g * W if keluar else (1 - g) * W, blur=2 + 10 * math.sin(math.pi * g))
        elif jenis == "zoom":  # kamera menerjang masuk: lama membesar, baru datang dari besar ke normal
            g = ease_io((q + 1) / 2)
            img = dengan_kamera(si, t, z_ekstra=1 + 0.8 * (g if keluar else 1 - g))
            img = img.filter(ImageFilter.GaussianBlur(6 * math.sin(math.pi * g)))
        else:
            img = dengan_kamera(si, t)

        if penanda != "tidak":  # bar progres + penanda hanya kalau diminta
            d = ImageDraw.Draw(img)
            # progres per adegan: selesai = oranye, sedang jalan = kuning terisi
            n, gap = len(adegan), 10
            lb = (W - 2 * L["margin"] - gap * (n - 1)) / n
            yp = int(H * L["progres"])
            for k in range(n):
                x0 = L["margin"] + k * (lb + gap)
                d.rectangle([x0, yp, x0 + lb, yp + 12], fill="#3A3A3A")
                isi = 1 if k < si else (min(1, (t - a["t0"]) / max(0.01, a["t1"] - a["t0"])) if k == si else 0)
                if isi:
                    d.rectangle([x0, yp, x0 + lb * isi, yp + 12], fill=TEMA["aksen"] if k < si else TEMA["aksen2"])
            # continuity: penanda yang terus berjalan di bar progres dari awal sampai akhir video
            p = si + min(1, (t - a["t0"]) / max(0.01, a["t1"] - a["t0"]))
            xm = L["margin"] + p * (lb + gap) - gap * (p >= n)
            if penanda == "truk":
                gambar_truk(d, xm, yp - 6, 1.3, TEMA["aksen"])
            else:
                d.ellipse([xm - 13, yp - 7, xm + 13, yp + 19], fill=TEMA["aksen2"], outline=TEMA["latar"], width=4)
        if pakai_sub:
            aktif = next((s for s in subs if s[0] <= t < s[1]), None)
            if aktif:
                if aktif[0] not in cache_sub:
                    cache_sub[aktif[0]] = kata_sub(bungkus(aktif[2], sub_fnt, W - 2 * L["margin"])[:2], aktif[3], sub_fnt)
                kata, (bw, bh) = cache_sub[aktif[0]]
                x0, y0 = (W - bw) // 2, int(H * L["sub"]) - bh // 2
                # shortcut: tanpa transkrip per kata, waktu kata dibagi menurut panjangnya di 85% awal potongan (sisanya jeda napas);
                # ganti ke waktu per kata kalau terlihat meleset dari suara
                lama, total, jalan = (aktif[1] - aktif[0]) * 0.85, sum(k[3] for k in kata), 0
                for im, x, y, bobot in kata:
                    u = t - aktif[0] - lama * jalan / total
                    jalan += bobot
                    sk = pegas_kamera(u, 3.0, 0.6)  # kata melompat masuk lalu mengendap
                    if sk < 0.05:
                        break
                    if abs(sk - 1) > 0.01:
                        k2 = im.resize((max(1, int(im.width * sk)), max(1, int(im.height * sk))), Image.BILINEAR)
                        img.paste(k2, (x0 + x + (im.width - k2.width) // 2, y0 + y + (im.height - k2.height) // 2), k2)
                    else:
                        img.paste(im, (x0 + x, y0 + y), im)
        return finishing(img, bahan, int(t * FPS)) if bahan else img
    return bingkai


def daftar_sfx(adegan):
    """SFX otomatis per adegan: [(nama, detik, volume)]. Volume kecil supaya VO tetap utama."""
    ev = []
    for a in adegan:
        t0 = a["t0"]
        # 3 lapis: mid whoosh = udara saat bergerak, sub = bobot saat mendarat, high (pop/klik) = detail
        if a["transisi"] == "whip":
            ev += [("whoosh", t0 - TR, 0.5), ("sub", t0 + TR * 0.6, 0.35)]
        elif a["transisi"] == "zoom":
            ev += [("riser", t0 - 0.8, 0.3), ("whoosh", t0 - TR, 0.4), ("sub", t0 + TR * 0.6, 0.4)]
        for e in a["el"]:
            if "img" in e:
                if e["gerak"] in ("pop", "slam"):
                    ev += [("thud" if e["gerak"] == "slam" else "pop", t0 + e["tunda"], 0.35), ("sub", t0 + e["tunda"] + 0.1, 0.2)]
                else:
                    ev.append(("klik", t0 + e["tunda"], 0.35))
        if a["kamera"] == "fokus":
            ev += [("whoosh", t0 + 0.6, 0.18), ("sub", t0 + 0.95, 0.4)]
        ev += [(n, t0 + 0.3, 0.35) for n in a["sfx"]]
    return [(n, max(0.0, t), v) for n, t, v in ev]


def filter_audio(audio, ev, idx0):
    """VO dinormalisasi + SFX (input ke-idx0 dst) dicampur, lalu limiter menjaga puncak."""
    rantai = f"[1:a]{filter_loudnorm(audio)}[vo];"
    for j, (_, t, v) in enumerate(ev):
        ms = int(t * 1000)
        rantai += f"[{idx0 + j}:a]adelay={ms}|{ms},volume={v}[s{j}];"
    masuk = "[vo]" + "".join(f"[s{j}]" for j in range(len(ev)))
    return rantai + f"{masuk}amix=inputs={len(ev) + 1}:normalize=0:duration=first,alimiter=limit=0.79:level=false[a]"


def buat_file_sfx(folder):
    for n, src in SFX.items():
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", src, "-ar", "48000", "-ac", "2",
                        os.path.join(folder, n + ".wav")], check=True)


def detik_srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def periksa(rencana, folder):
    if rencana.get("format") not in UKURAN:
        sys.exit(f"format harus salah satu dari {list(UKURAN)}")
    if not rencana.get("adegan") or not all(str(a.get("ucapan", "")).strip() for a in rencana["adegan"]):
        sys.exit("Setiap adegan wajib punya 'ucapan' (kalimat VO).")
    for i, a in enumerate(rencana["adegan"], 1):
        for kunci, boleh in (("kamera", KAMERA), ("transisi", TRANSISI), ("masuk", MASUK)):
            if a.get(kunci) and a[kunci] not in boleh:
                sys.exit(f"Adegan {i}: '{kunci}' harus salah satu dari {list(boleh)}")
        if any(n not in SFX for n in a.get("sfx", [])):
            sys.exit(f"Adegan {i}: 'sfx' hanya boleh {list(SFX)}")
    if rencana.get("rasa", "tegas") not in RASA:
        sys.exit(f"'rasa' harus salah satu dari {list(RASA)}")
    if rencana.get("kurva") and rencana["kurva"] not in KURVA:
        sys.exit(f"'kurva' harus salah satu dari {list(KURVA)}")
    if rencana.get("penanda", "tidak") not in PENANDA:
        sys.exit(f"'penanda' harus salah satu dari {list(PENANDA)}")
    def cari(nama, apa):
        for cand in (nama, os.path.join(folder, nama), os.path.join("/mnt/user-data/uploads", os.path.basename(nama))):
            if cand and os.path.isfile(cand):
                return cand
        sys.exit(f"File {apa} tidak ditemukan: {nama}")
    for i, a in enumerate(rencana["adegan"], 1):  # "gambar": "a.png" atau daftar lapisan ["a.png", {"file": "b.png", "masuk": .., "hidup": ..}]
        if a.get("gambar"):
            daftar = a["gambar"] if isinstance(a["gambar"], list) else [a["gambar"]]
            a["gambar"] = [dict(l) if isinstance(l, dict) else {"file": l} for l in daftar]
            for l in a["gambar"]:
                l["file"] = cari(l.get("file", ""), "gambar")
                if l.get("masuk", "potong") not in LMASUK or l.get("hidup", "diam") not in HIDUP:
                    sys.exit(f"Adegan {i}: lapisan gambar hanya boleh masuk {list(LMASUK)} dan hidup {list(HIDUP)}")
    return cari(rencana.get("audio", ""), "audio")


def utama(argv):
    if "--uji" in argv:
        return uji()
    berkas = next((a for a in argv if a.endswith(".json")), None) or sys.exit(__doc__)
    out = argv[argv.index("--out") + 1] if "--out" in argv else (
        "/mnt/user-data/outputs" if os.path.isdir("/mnt/user-data/outputs") else os.getcwd())
    with open(berkas, encoding="utf-8") as f:
        rencana = json.load(f)
    TEMA.update(rencana.get("tema", {}))
    audio = periksa(rencana, os.path.dirname(os.path.abspath(berkas)))
    G.update(zip(("kurva", "durasi", "pegas", "jeda"), RASA[rencana.get("rasa", "tegas")]))
    if rencana.get("kurva"):  # kurva masuk pilihan sendiri menggantikan kurva bawaan rasa
        G["kurva"] = bezier(*KURVA[rencana["kurva"]])
    nama = re.sub(r"[^a-z0-9_-]+", "-", rencana.get("nama", "video").lower()).strip("-") or "video"
    durasi, jeda = analisis_audio(audio)
    adegan, subs = siapkan(rencana, durasi, jeda)
    bingkai = buat_bingkai(rencana, adegan, subs, {})
    W, H = UKURAN[rencana["format"]]

    print("Pembagian waktu adegan:")
    for i, a in enumerate(adegan, 1):
        print(f"  {i:2}. {a['t0']:6.2f} - {a['t1']:6.2f} dtk  {a['transisi']:6} {a['kamera']:6}  {rencana['adegan'][i-1]['ucapan'][:40]}")
        gbr = rencana["adegan"][i - 1].get("gambar") or []
        if not gbr:
            print("      ! tanpa gambar: layar hanya subtitle. Beri gambar yang mewakili kalimat ini.")
        elif a["t1"] - a["t0"] > 8 and not any(l.get("saat") for l in gbr):  # gambar yang sama terlalu lama = tidak mengikuti suara
            print(f"      ! {a['t1'] - a['t0']:.0f} dtk dengan gambar yang sama. Pecah jadi adegan per kalimat, atau beri \"saat\" pada lapisan.")

    if "--preview" in argv:  # satu frame per adegan, digabung jadi grid
        tw = 360 if H > W else 480
        th = tw * H // W
        kol = 3
        grid = Image.new("RGB", (tw * kol, th * math.ceil(len(adegan) / kol)), "black")
        for i, a in enumerate(adegan):
            t = a["t0"] + (a["t1"] - a["t0"]) * 0.85  # menjelang akhir adegan: semua lapisan ber-"saat" sudah datang
            grid.paste(bingkai(t).resize((tw, th), Image.BILINEAR), (i % kol * tw, i // kol * th))
        f = os.path.join(out, f"{nama}_preview.png")
        grid.save(f)
        return print(f"Preview: {f}")

    srt = os.path.join(out, f"{nama}.srt")
    with open(srt, "w", encoding="utf-8") as f:
        for i, (a, b, teks, _) in enumerate(subs, 1):
            f.write(f"{i}\n{detik_srt(a)} --> {detik_srt(b)}\n{teks}\n\n")
    mp4 = os.path.join(out, f"{nama}.mp4")
    tmp = tempfile.mkdtemp()
    ev = daftar_sfx(adegan) if rencana.get("sfx", True) else []
    if ev:
        buat_file_sfx(tmp)
    masuk_sfx = [x for n, _, _ in ev for x in ("-i", os.path.join(tmp, n + ".wav"))]
    p = subprocess.Popen([FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, *masuk_sfx,
                          "-filter_complex", filter_audio(audio, ev, 2), "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                          "-movflags", "+faststart", "-shortest", mp4], stdin=subprocess.PIPE)
    total = math.ceil(durasi * FPS)
    for k in range(total):
        p.stdin.write(bingkai(k / FPS).tobytes())
        if k % (FPS * 10) == 0:
            print(f"  render {k / FPS:5.1f} / {durasi:.1f} dtk", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("FFmpeg gagal menyandikan video.")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Selesai: {mp4}\nSubtitle: {srt}")


def uji():
    j = [(0, 0.5), (3.0, 3.6), (7.0, 7.4), (9.5, 10)]
    b = bagi_waktu([30, 30, 20], j, 0, 10)
    assert b[0] == 0 and b[-1] == 10 and abs(b[1] - 3.3) < 1e-9 and abs(b[2] - 7.2) < 1e-9, b
    assert bagi_waktu([1, 1], [], 0, 4) == [0, 2, 4]
    assert abs(bagi_waktu([1, 1], [(4.9, 5.0), (5.8, 6.4)], 0, 10)[1] - 6.1) < 1e-9  # jeda panjang menang
    assert potong_sub("Satu dua. Tiga empat lima enam tujuh delapan", 16) == ["Satu dua.", "Tiga empat lima", "enam tujuh", "delapan"]
    assert zoom_kamera("dorong", 0, 5) == 1 and abs(zoom_kamera("tarik", 5, 5) - 1) < 1e-9
    assert zoom_kamera("fokus", 0.5, 5) == 1 and abs(zoom_kamera("fokus", 3, 5) - 1.32) < 1e-3
    assert all(1 <= zoom_kamera(k, t, 4, m) <= m + 0.04 * (m - 1) + 1e-9 for k in KAMERA for t in (0, 1, 1.1, 2, 4) for m in (1.0, 1.05, 1.32))
    assert ease_io(0) == 0 and abs(ease_io(1) - 1) < 1e-6 and ease_io(0.1) < 0.02 and ease_io(0.9) > 0.98  # mulai & berhenti halus
    ev = daftar_sfx([dict(t0=5.0, transisi="whip", kamera="fokus", sfx=["ding"], el=[dict(img=1, gerak="pop", tunda=0.08)])])
    assert [n for n, _, _ in ev] == ["whoosh", "sub", "pop", "sub", "whoosh", "sub", "ding"] and abs(ev[0][1] - (5 - TR)) < 1e-9
    for kurva, durasi, (hz, redam), _ in RASA.values():  # tiap rasa: mulai 0, berakhir 1, pegas mengendap di 1
        assert kurva(0) == 0 and kurva(1) == 1 and abs(pegas_kamera(4, hz, redam) - 1) < 1e-3
    assert RASA["ceria"][0](0.6) > 1 and RASA["teknologi"][0](0.2) > 0.8  # ceria memantul, teknologi cepat di awal
    assert tandai("Tanah *tidak dibuang*, tapi *disimpan*.") == ("Tanah tidak dibuang, tapi disimpan.", [False, True, True, False, True])
    kata, ukuran = kata_sub(["tidak dibuang"], [True, False], font(FONT_ISI, 40))
    assert len(kata) == 2 and kata[0][1] < kata[1][1] and ukuran[1] > 40
    for k in KURVA.values():  # semua kurva bernama: mulai 0, berakhir 1 (aman untuk gerak masuk)
        assert bezier(*k)(0) == 0 and bezier(*k)(1) == 1
    assert kurva_slam(0) == 0 and abs(2.2 - 1.2 * kurva_slam(1) - 1) < 1e-9  # slam: dari 220% ke 100%
    img = Image.new("RGB", (64, 64), "#1C1C1C")
    assert finishing(img, siapkan_finishing(64, 64), 0).size == (64, 64)
    print("uji OK")


if __name__ == "__main__":
    utama(sys.argv[1:])
