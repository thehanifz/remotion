import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export const TOTAL_FRAMES = 1021;
export const FPS = 30;

// Palet Warna Manchester United & Broadcast
const COLORS = {
  bg: '#0a0d14',
  cardBg: 'rgba(25, 30, 45, 0.75)',
  border: 'rgba(255, 255, 255, 0.12)',
  red: '#DA020E',
  redBright: '#ff2d3b',
  yellow: '#FBE122',
  white: '#FFFFFF',
  gray: '#94a3b8',
  green: '#10b981',
  darkOverlay: 'rgba(10, 13, 20, 0.85)',
};

// Subtitle bar di bagian bawah
const CaptionBar: React.FC<{text: string; highlight?: string}> = ({text, highlight}) => {
  if (!text) return null;
  const parts = highlight ? text.split(new RegExp(`(${highlight})`, 'gi')) : [text];

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 140,
        left: 50,
        right: 50,
        display: 'flex',
        justifyContent: 'center',
        textAlign: 'center',
        zIndex: 50,
      }}
    >
      <div
        style={{
          background: 'rgba(10, 13, 20, 0.88)',
          backdropFilter: 'blur(16px)',
          padding: '16px 28px',
          borderRadius: 24,
          border: '1px solid rgba(255,255,255,0.15)',
          maxWidth: '90%',
          boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
        }}
      >
        <span
          style={{
            color: COLORS.white,
            fontSize: 34,
            fontWeight: 800,
            fontFamily: 'system-ui, -apple-system, sans-serif',
            lineHeight: 1.35,
            letterSpacing: '-0.02em',
          }}
        >
          {parts.map((p, i) =>
            p.toLowerCase() === highlight?.toLowerCase() ? (
              <span
                key={i}
                style={{
                  color: COLORS.yellow,
                  background: 'rgba(251, 225, 34, 0.18)',
                  padding: '2px 8px',
                  borderRadius: 8,
                }}
              >
                {p}
              </span>
            ) : (
              <span key={i}>{p}</span>
            )
          )}
        </span>
      </div>
    </div>
  );
};

// ==========================================
// SCENE 1: BREAKING NEWS - CARRICK DIPECAT
// Frame: 0 - 75 (0.00s - 2.50s)
// ==========================================
const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const titleSpring = spring({frame, fps, config: {damping: 10, mass: 0.6, stiffness: 120}});
  const badgeSpring = spring({frame: frame - 6, fps, config: {damping: 12, mass: 0.5, stiffness: 140}});
  const pulse = Math.sin(frame * 0.2) * 0.05 + 1;

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: `radial-gradient(circle at center, #2e080a 0%, ${COLORS.bg} 85%)`,
        padding: 50,
      }}
    >
      {/* Background Red Glow & Stripes */}
      <div
        style={{
          position: 'absolute',
          width: 800,
          height: 800,
          borderRadius: '50%',
          background: 'rgba(218, 2, 14, 0.18)',
          filter: 'blur(100px)',
        }}
      />

      {/* Breaking News Tag */}
      <div
        style={{
          transform: `scale(${badgeSpring})`,
          opacity: badgeSpring,
          background: COLORS.red,
          color: COLORS.white,
          fontSize: 28,
          fontWeight: 900,
          letterSpacing: '0.25em',
          padding: '12px 32px',
          borderRadius: 100,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          boxShadow: '0 0 40px rgba(218, 2, 14, 0.6)',
          marginBottom: 40,
        }}
      >
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: '50%',
            background: COLORS.white,
            transform: `scale(${pulse})`,
          }}
        />
        BREAKING NEWS
      </div>

      {/* Main Title Banner */}
      <div
        style={{
          transform: `scale(${titleSpring})`,
          opacity: titleSpring,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontSize: 42,
            color: COLORS.gray,
            fontWeight: 800,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: 10,
          }}
        >
          MANCHESTER UNITED
        </div>
        <div
          style={{
            fontSize: 92,
            color: COLORS.white,
            fontWeight: 950,
            lineHeight: 1.05,
            letterSpacing: '-0.04em',
            textTransform: 'uppercase',
            textShadow: '0 10px 40px rgba(0,0,0,0.8)',
          }}
        >
          MICHAEL<br />
          <span style={{color: COLORS.redBright, textShadow: '0 0 50px rgba(255, 45, 59, 0.7)'}}>
            CARRICK
          </span><br />
          DIPECAT!
        </div>
      </div>

      <CaptionBar
        text="Michael Carrick dipecat Manchester United."
        highlight="dipecat"
      />
    </AbsoluteFill>
  );
};

// ==========================================
// SCENE 2: INTERIM -> FINIS KE-3 -> PERMANEN
// Frame: 75 - 258 (2.50s - 8.60s)
// ==========================================
const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const card1 = spring({frame: frame - 5, fps, config: {damping: 12, mass: 0.6}});
  const card2 = spring({frame: frame - 40, fps, config: {damping: 12, mass: 0.6}});
  const stampSpring = spring({frame: frame - 90, fps, config: {damping: 8, mass: 0.8, stiffness: 140}});

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: `radial-gradient(circle at center, #131c2e 0%, ${COLORS.bg} 90%)`,
        padding: 50,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 920,
          display: 'flex',
          flexDirection: 'column',
          gap: 30,
        }}
      >
        {/* Step 1: Dari Interim */}
        <div
          style={{
            transform: `scale(${card1}) translateY(${(1 - card1) * 40}px)`,
            opacity: card1,
            background: COLORS.cardBg,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 28,
            padding: '36px 44px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 15px 35px rgba(0,0,0,0.4)',
          }}
        >
          <div>
            <div style={{fontSize: 24, color: COLORS.gray, fontWeight: 700, letterSpacing: '0.1em'}}>
              STATUS AWAL
            </div>
            <div style={{fontSize: 50, color: COLORS.white, fontWeight: 900}}>
              Pelatih Interim
            </div>
          </div>
          <div
            style={{
              background: 'rgba(255,255,255,0.1)',
              padding: '16px 28px',
              borderRadius: 18,
              fontSize: 32,
              fontWeight: 800,
              color: COLORS.yellow,
            }}
          >
            ⏳ SEMENTARA
          </div>
        </div>

        {/* Step 2: Finis Ketiga */}
        <div
          style={{
            transform: `scale(${card2}) translateY(${(1 - card2) * 40}px)`,
            opacity: card2,
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(25, 30, 45, 0.8) 100%)',
            border: '2px solid rgba(16, 185, 129, 0.4)',
            borderRadius: 28,
            padding: '36px 44px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 20px 45px rgba(16, 185, 129, 0.2)',
          }}
        >
          <div>
            <div style={{fontSize: 24, color: '#6ee7b7', fontWeight: 700, letterSpacing: '0.1em'}}>
              PRESTASI GEMILANG
            </div>
            <div style={{fontSize: 52, color: COLORS.white, fontWeight: 950}}>
              Bawa MU Finis Ke-3
            </div>
          </div>
          <div style={{fontSize: 60}}>🏆</div>
        </div>

        {/* Step 3: Kontrak Permanen Stamp */}
        <div
          style={{
            position: 'relative',
            marginTop: 20,
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              transform: `scale(${stampSpring}) rotate(-5deg)`,
              opacity: stampSpring,
              border: `6px solid ${COLORS.yellow}`,
              color: COLORS.yellow,
              padding: '20px 50px',
              borderRadius: 24,
              fontSize: 48,
              fontWeight: 950,
              letterSpacing: '0.08em',
              textAlign: 'center',
              textTransform: 'uppercase',
              background: 'rgba(251, 225, 34, 0.12)',
              boxShadow: '0 0 50px rgba(251, 225, 34, 0.3)',
            }}
          >
            DIANGKAT PERMANEN<br />
            <span style={{fontSize: 34, color: COLORS.white}}>MEI 2026</span>
          </div>
        </div>
      </div>

      <CaptionBar
        text="Dari interim, dia bawa United finis ketiga, lalu diangkat permanen Mei dua ribu dua puluh enam."
        highlight="finis ketiga"
      />
    </AbsoluteFill>
  );
};

// ==========================================
// SCENE 3: KRISIS - 1 DARI 10 LAGA, PERINGKAT 18
// Frame: 258 - 441 (8.60s - 14.70s)
// ==========================================
const Scene3: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const dangerPulse = Math.sin(frame * 0.18) * 0.08 + 1;
  const stat1 = spring({frame: frame - 5, fps, config: {damping: 10, mass: 0.5}});
  const stat2 = spring({frame: frame - 50, fps, config: {damping: 10, mass: 0.5}});

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: `radial-gradient(circle at center, #35080b 0%, ${COLORS.bg} 90%)`,
        padding: 50,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 920,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 36,
        }}
      >
        <div
          style={{
            color: COLORS.redBright,
            fontSize: 30,
            fontWeight: 900,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}
        >
          ⚠️ MUSIM INI HANCUR TOTAL
        </div>

        {/* Card 1: 1 Kemenangan */}
        <div
          style={{
            transform: `scale(${stat1})`,
            opacity: stat1,
            width: '100%',
            background: COLORS.cardBg,
            border: `2px solid rgba(239, 68, 68, 0.4)`,
            borderRadius: 32,
            padding: '36px 40px',
            textAlign: 'center',
            boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
          }}
        >
          <div style={{fontSize: 26, color: COLORS.gray, fontWeight: 700}}>
            HASIL PERTANDINGAN
          </div>
          <div
            style={{
              fontSize: 108,
              fontWeight: 950,
              color: COLORS.white,
              lineHeight: 1.1,
              marginTop: 6,
            }}
          >
            <span style={{color: COLORS.redBright}}>1</span> MENANG
          </div>
          <div style={{fontSize: 36, color: COLORS.gray, fontWeight: 700}}>
            DARI 10 LAGA
          </div>
        </div>

        {/* Card 2: Peringkat 18 - 8 Poin */}
        <div
          style={{
            transform: `scale(${stat2 * dangerPulse})`,
            opacity: stat2,
            width: '100%',
            background: 'linear-gradient(135deg, rgba(220, 38, 38, 0.3) 0%, rgba(25, 30, 45, 0.9) 100%)',
            border: `3px solid ${COLORS.redBright}`,
            borderRadius: 32,
            padding: '40px',
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            boxShadow: '0 0 60px rgba(220, 38, 38, 0.4)',
          }}
        >
          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: 24, color: '#fca5a5', fontWeight: 800}}>PERINGKAT</div>
            <div style={{fontSize: 110, fontWeight: 950, color: COLORS.yellow, lineHeight: 1}}>
              #18
            </div>
            <div style={{fontSize: 22, color: '#f87171', fontWeight: 800, marginTop: 4}}>
              ZONA DEGRADASI
            </div>
          </div>

          <div style={{width: 3, height: 120, background: 'rgba(255,255,255,0.15)'}} />

          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: 24, color: '#fca5a5', fontWeight: 800}}>TOTAL PEROLEHAN</div>
            <div style={{fontSize: 110, fontWeight: 950, color: COLORS.white, lineHeight: 1}}>
              8
            </div>
            <div style={{fontSize: 22, color: COLORS.gray, fontWeight: 800, marginTop: 4}}>
              POIN
            </div>
          </div>
        </div>
      </div>

      <CaptionBar
        text="Musim ini, cuma satu kemenangan dari sepuluh laga. Peringkat delapan belas, delapan poin."
        highlight="Peringkat delapan belas"
      />
    </AbsoluteFill>
  );
};

// ==========================================
// SCENE 4: PENGGANTI - POCHETTINO & KLAUSUL 10 JUTA
// Frame: 441 - 642 (14.70s - 21.40s)
// ==========================================
const Scene4: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const titleSpring = spring({frame: frame - 5, fps, config: {damping: 12, mass: 0.6}});
  const moneySpring = spring({frame: frame - 45, fps, config: {damping: 10, mass: 0.5, stiffness: 130}});
  const stampSpring = spring({frame: frame - 85, fps, config: {damping: 8, mass: 0.7, stiffness: 150}});

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: `radial-gradient(circle at center, #191b2e 0%, ${COLORS.bg} 90%)`,
        padding: 50,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 920,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 32,
        }}
      >
        <div style={{fontSize: 26, color: COLORS.yellow, fontWeight: 800, letterSpacing: '0.15em'}}>
          PENGGANTI RESMI
        </div>

        {/* Nama Pochettino */}
        <div
          style={{
            transform: `scale(${titleSpring})`,
            opacity: titleSpring,
            fontSize: 78,
            color: COLORS.white,
            fontWeight: 950,
            textAlign: 'center',
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
          }}
        >
          MAURICIO<br />
          <span style={{color: '#60a5fa'}}>POCHETTINO</span>
        </div>

        {/* Klausul Lepas $10 Juta */}
        <div
          style={{
            transform: `scale(${moneySpring})`,
            opacity: moneySpring,
            width: '100%',
            background: 'linear-gradient(135deg, rgba(234, 179, 8, 0.15) 0%, rgba(25, 30, 45, 0.8) 100%)',
            border: '2px solid rgba(234, 179, 8, 0.4)',
            borderRadius: 32,
            padding: '36px',
            textAlign: 'center',
            boxShadow: '0 20px 45px rgba(0,0,0,0.5)',
          }}
        >
          <div style={{fontSize: 24, color: COLORS.gray, fontWeight: 700}}>
            KLAUSUL PELEPASAN KONTRAK
          </div>
          <div
            style={{
              fontSize: 100,
              fontWeight: 950,
              color: COLORS.yellow,
              letterSpacing: '-0.03em',
              margin: '8px 0',
            }}
          >
            $10.000.000
          </div>
          <div style={{fontSize: 28, color: COLORS.white, fontWeight: 700}}>
            (SEPULUH JUTA DOLAR)
          </div>
        </div>

        {/* Stamp: Rugi Dua Kali */}
        <div
          style={{
            transform: `scale(${stampSpring}) rotate(4deg)`,
            opacity: stampSpring,
            border: `6px solid ${COLORS.redBright}`,
            color: COLORS.redBright,
            padding: '16px 48px',
            borderRadius: 20,
            fontSize: 48,
            fontWeight: 950,
            background: 'rgba(218, 2, 14, 0.18)',
            boxShadow: '0 0 50px rgba(218, 2, 14, 0.4)',
            textTransform: 'uppercase',
          }}
        >
          💥 RUGI DUA KALI!
        </div>
      </div>

      <CaptionBar
        text="Penggantinya: Mauricio Pochettino, dengan klausul lepas sepuluh juta dolar. Rugi dua kali."
        highlight="Rugi dua kali"
      />
    </AbsoluteFill>
  );
};

// ==========================================
// SCENE 5: UJIAN PERTAMA - LIVERPOOL DI ANFIELD
// Frame: 642 - 771 (21.40s - 25.70s)
// ==========================================
const Scene5: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const fixtureSpring = spring({frame: frame - 5, fps, config: {damping: 12, mass: 0.6}});
  const vsSpring = spring({frame: frame - 25, fps, config: {damping: 10, mass: 0.5, stiffness: 140}});

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: `radial-gradient(circle at center, #2b0b14 0%, ${COLORS.bg} 90%)`,
        padding: 50,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 920,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 36,
        }}
      >
        <div
          style={{
            background: COLORS.red,
            color: COLORS.white,
            fontSize: 26,
            fontWeight: 900,
            letterSpacing: '0.2em',
            padding: '10px 32px',
            borderRadius: 100,
          }}
        >
          UJIAN PERTAMA LANGSUNG NERAKA
        </div>

        {/* Fixture Matchup Card */}
        <div
          style={{
            transform: `scale(${fixtureSpring})`,
            opacity: fixtureSpring,
            width: '100%',
            background: COLORS.cardBg,
            border: `2px solid ${COLORS.border}`,
            borderRadius: 36,
            padding: '50px 30px',
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            boxShadow: '0 25px 60px rgba(0,0,0,0.6)',
          }}
        >
          {/* Liverpool */}
          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: 70}}>🔴</div>
            <div style={{fontSize: 48, fontWeight: 950, color: '#f87171', marginTop: 10}}>
              LIVERPOOL
            </div>
            <div style={{fontSize: 22, color: COLORS.gray, fontWeight: 700}}>TUAN RUMAH</div>
          </div>

          {/* VS Badge */}
          <div
            style={{
              transform: `scale(${vsSpring})`,
              background: COLORS.yellow,
              color: '#000',
              fontSize: 36,
              fontWeight: 950,
              width: 80,
              height: 80,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 40px rgba(251, 225, 34, 0.6)',
            }}
          >
            VS
          </div>

          {/* Man United */}
          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: 70}}>⚪</div>
            <div style={{fontSize: 48, fontWeight: 950, color: COLORS.white, marginTop: 10}}>
              MAN UNITED
            </div>
            <div style={{fontSize: 22, color: COLORS.gray, fontWeight: 700}}>TIM TAMU</div>
          </div>
        </div>

        {/* Venue & Date */}
        <div style={{textAlign: 'center'}}>
          <div style={{fontSize: 38, color: COLORS.white, fontWeight: 900, letterSpacing: '0.05em'}}>
            STADION ANFIELD
          </div>
          <div style={{fontSize: 52, color: COLORS.yellow, fontWeight: 950, marginTop: 6}}>
            22 NOVEMBER
          </div>
        </div>
      </div>

      <CaptionBar
        text="Ujian pertama: Liverpool di Anfield, dua puluh dua November."
        highlight="Liverpool di Anfield"
      />
    </AbsoluteFill>
  );
};

// ==========================================
// SCENE 6: ANALOGI - GONTA-GANTI DOKTER, OBAT TAK DIMINUM
// Frame: 771 - 930 (25.70s - 31.00s)
// ==========================================
const Scene6: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const c1 = spring({frame: frame - 5, fps, config: {damping: 12, mass: 0.6}});
  const c2 = spring({frame: frame - 45, fps, config: {damping: 12, mass: 0.6}});

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: `radial-gradient(circle at center, #1b2030 0%, ${COLORS.bg} 90%)`,
        padding: 50,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 920,
          display: 'flex',
          flexDirection: 'column',
          gap: 32,
        }}
      >
        <div
          style={{
            textAlign: 'center',
            fontSize: 26,
            color: COLORS.gray,
            fontWeight: 800,
            letterSpacing: '0.15em',
          }}
        >
          ANALOGI MASALAH MAN UNITED
        </div>

        {/* Card 1: Gonta-ganti dokter */}
        <div
          style={{
            transform: `scale(${c1})`,
            opacity: c1,
            background: COLORS.cardBg,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 28,
            padding: '36px 40px',
            display: 'flex',
            alignItems: 'center',
            gap: 24,
          }}
        >
          <div style={{fontSize: 60}}>🩺</div>
          <div>
            <div style={{fontSize: 42, color: COLORS.white, fontWeight: 900}}>
              Gonta-ganti Dokter
            </div>
            <div style={{fontSize: 24, color: COLORS.gray, marginTop: 4}}>
              Pelatih terus diganti tanpa arah jelas
            </div>
          </div>
        </div>

        {/* Card 2: Obat tidak diminum */}
        <div
          style={{
            transform: `scale(${c2})`,
            opacity: c2,
            background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(25, 30, 45, 0.8) 100%)',
            border: `2px solid rgba(239, 68, 68, 0.4)`,
            borderRadius: 28,
            padding: '36px 40px',
            display: 'flex',
            alignItems: 'center',
            gap: 24,
          }}
        >
          <div style={{fontSize: 60}}>💊</div>
          <div>
            <div style={{fontSize: 42, color: COLORS.redBright, fontWeight: 900}}>
              Obatnya Tidak Diminum
            </div>
            <div style={{fontSize: 24, color: COLORS.gray, marginTop: 4}}>
              Struktur manajemen & mentalitas tim tak diubah
            </div>
          </div>
        </div>

        {/* Kesimpulan: Penyakitnya Tetap */}
        <div
          style={{
            marginTop: 10,
            background: 'rgba(218, 2, 14, 0.25)',
            border: `2px dashed ${COLORS.redBright}`,
            borderRadius: 24,
            padding: '24px',
            textAlign: 'center',
          }}
        >
          <span style={{fontSize: 44, color: COLORS.white, fontWeight: 950}}>
            AKHIRNYA: <span style={{color: COLORS.yellow}}>PENYAKITNYA TETAP.</span>
          </span>
        </div>
      </div>

      <CaptionBar
        text="Seperti pasien gonta-ganti dokter, tapi obatnya tidak diminum. Penyakitnya tetap."
        highlight="Penyakitnya tetap"
      />
    </AbsoluteFill>
  );
};

// ==========================================
// SCENE 7: CTA / POLLING - POCHETTINO TAHAN BERAPA LAMA?
// Frame: 930 - 1021 (31.00s - 34.04s)
// ==========================================
const Scene7: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const titleSpring = spring({frame, fps, config: {damping: 10, mass: 0.6, stiffness: 120}});
  const pulse = Math.sin(frame * 0.25) * 0.06 + 1;

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: `radial-gradient(circle at center, #261608 0%, ${COLORS.bg} 90%)`,
        padding: 50,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 920,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          gap: 36,
        }}
      >
        <div style={{fontSize: 32, color: COLORS.yellow, fontWeight: 900, letterSpacing: '0.15em'}}>
          PERTANYAAN UNTUK KALIAN
        </div>

        {/* Main Question */}
        <div
          style={{
            transform: `scale(${titleSpring})`,
            fontSize: 78,
            color: COLORS.white,
            fontWeight: 950,
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
          }}
        >
          POCHETTINO<br />
          TAHAN BERAPA LAMA?
        </div>

        {/* Comment CTA Box */}
        <div
          style={{
            transform: `scale(${pulse})`,
            background: COLORS.red,
            color: COLORS.white,
            fontSize: 40,
            fontWeight: 900,
            padding: '24px 60px',
            borderRadius: 100,
            boxShadow: '0 0 50px rgba(218, 2, 14, 0.6)',
            display: 'flex',
            alignItems: 'center',
            gap: 16,
          }}
        >
          💬 Tulis Prediksimu di Bawah!
        </div>
      </div>

      <CaptionBar
        text="Menurut kalian, Pochettino tahan berapa lama?"
        highlight="Pochettino tahan berapa lama"
      />
    </AbsoluteFill>
  );
};

// ==========================================
// MAIN COMPOSITION
// ==========================================
export const CarrickVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      {/* 1 Full Voice Over Audio Track */}
      <Audio src={staticFile('narasi/carrick.mp3')} />

      {/* 7 Scenes Synchronized to Audio Timestamps */}
      <Sequence from={0} durationInFrames={75}>
        <Scene1 />
      </Sequence>

      <Sequence from={75} durationInFrames={183}>
        <Scene2 />
      </Sequence>

      <Sequence from={258} durationInFrames={183}>
        <Scene3 />
      </Sequence>

      <Sequence from={441} durationInFrames={201}>
        <Scene4 />
      </Sequence>

      <Sequence from={642} durationInFrames={129}>
        <Scene5 />
      </Sequence>

      <Sequence from={771} durationInFrames={159}>
        <Scene6 />
      </Sequence>

      <Sequence from={930} durationInFrames={91}>
        <Scene7 />
      </Sequence>
    </AbsoluteFill>
  );
};
