import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface StoryboardLayer {
  type: "background" | "character" | "prop" | "fx" | "textOverlay";
  assetId?: string;
  filePath?: string;
  text?: string;
  zIndex: number;
  position?: { xPercent?: number; yPercent?: number; scale?: number };
  animationPreset:
    | "slam-in"
    | "slide-left"
    | "slide-right"
    | "bounce-pop"
    | "shake-impact"
    | "freeze-zoom"
    | "float-idle"
    | "fade-in";
}

export interface StoryboardScene {
  id: string;
  name: string;
  startFrame: number;
  durationInFrames: number;
  voiceoverText: string;
  highlightWords?: string[];
  cameraMotion?: "static" | "slow-zoom-in" | "slow-zoom-out" | "punch-zoom" | "shake-impact";
  layers: StoryboardLayer[];
}

export interface StoryboardData {
  meta: {
    episodeId: string;
    title: string;
    sourceUrl: string;
    width: number;
    height: number;
    fps: number;
    totalDurationInFrames: number;
  };
  audio?: {
    voiceoverFile?: string;
  };
  scenes: StoryboardScene[];
}

const AnimatedLayer: React.FC<{ layer: StoryboardLayer; durationInFrames: number }> = ({
  layer,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const x = layer.position?.xPercent ?? 50;
  const y = layer.position?.yPercent ?? 50;
  const baseScale = layer.position?.scale ?? 1;

  const spr = spring({ frame, fps, config: { damping: 12, stiffness: 160 } });
  let translateX = 0;
  let translateY = 0;
  let scale = baseScale;
  let opacity = 1;

  switch (layer.animationPreset) {
    case "slam-in":
      scale = interpolate(spr, [0, 1], [baseScale * 1.6, baseScale]);
      opacity = interpolate(frame, [0, 5], [0, 1], { extrapolateRight: "clamp" });
      break;
    case "slide-left":
      translateX = interpolate(spr, [0, 1], [320, 0]);
      break;
    case "slide-right":
      translateX = interpolate(spr, [0, 1], [-320, 0]);
      break;
    case "bounce-pop":
      scale = interpolate(spr, [0, 1], [0.2, baseScale]);
      break;
    case "shake-impact":
      translateX = frame < 14 ? Math.sin(frame * 2.5) * 18 : 0;
      translateY = frame < 14 ? Math.cos(frame * 2.2) * 10 : 0;
      break;
    case "freeze-zoom":
      scale = interpolate(frame, [0, durationInFrames], [baseScale, baseScale * 1.12], {
        extrapolateRight: "clamp",
      });
      break;
    case "float-idle":
      translateY = Math.sin(frame / 10) * 10;
      break;
    case "fade-in":
      opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
      break;
  }

  if (layer.type === "background" && layer.filePath) {
    return (
      <AbsoluteFill style={{ zIndex: layer.zIndex, overflow: "hidden" }}>
        <Img
          src={staticFile(layer.filePath)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale})`,
            opacity,
          }}
        />
      </AbsoluteFill>
    );
  }

  if (layer.type === "textOverlay" && layer.text) {
    return (
      <div
        style={{
          position: "absolute",
          left: `${x}%`,
          top: `${y}%`,
          transform: `translate(-50%, -50%) translate(${translateX}px, ${translateY}px) scale(${scale})`,
          zIndex: layer.zIndex,
          opacity,
          fontFamily: "Impact, Arial Black, sans-serif",
          fontSize: 64,
          color: "#FFFFFF",
          textAlign: "center",
          textShadow: "0 6px 0 #000000, 0 0 24px rgba(0,0,0,0.85)",
          WebkitTextStroke: "3px #000000",
          maxWidth: "84%",
          lineHeight: 1.1,
        }}
      >
        {layer.text}
      </div>
    );
  }

  if (!layer.filePath) return null;

  return (
    <img
      src={staticFile(layer.filePath)}
      alt={layer.assetId ?? layer.type}
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y}%`,
        transform: `translate(-50%, -50%) translate(${translateX}px, ${translateY}px) scale(${scale})`,
        zIndex: layer.zIndex,
        opacity,
        maxWidth: "90%",
        maxHeight: "75%",
        objectFit: "contain",
      }}
    />
  );
};

const HighlightedCaption: React.FC<{ text: string; highlights?: string[] }> = ({
  text,
  highlights = [],
}) => {
  const lowerHighlights = highlights.map((w) => w.toLowerCase());
  const words = text.split(/\s+/);

  return (
    <div
      style={{
        position: "absolute",
        bottom: "18%",
        left: "8%",
        right: "8%",
        zIndex: 99,
        textAlign: "center",
        backgroundColor: "rgba(10, 12, 20, 0.78)",
        border: "3px solid #FFD60A",
        borderRadius: 18,
        padding: "18px 24px",
        fontFamily: "Arial Black, sans-serif",
        fontSize: 42,
        lineHeight: 1.25,
        color: "#FFFFFF",
      }}
    >
      {words.map((word, idx) => {
        const clean = word.replace(/[.,!?"]/g, "").toLowerCase();
        const isHit = lowerHighlights.some((h) => clean.includes(h) || h.includes(clean));
        return (
          <span
            key={idx}
            style={{
              color: isHit ? "#FFD60A" : "#FFFFFF",
              marginRight: 10,
              display: "inline-block",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

export const AnimeNewsVideo: React.FC<{ storyboard: StoryboardData }> = ({ storyboard }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0D14" }}>
      {storyboard.audio?.voiceoverFile ? (
        <Audio src={staticFile(storyboard.audio.voiceoverFile)} />
      ) : null}

      {storyboard.scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationInFrames}
        >
          <AbsoluteFill>
            {[...scene.layers]
              .sort((a, b) => a.zIndex - b.zIndex)
              .map((layer, idx) => (
                <AnimatedLayer
                  key={`${scene.id}-layer-${idx}`}
                  layer={layer}
                  durationInFrames={scene.durationInFrames}
                />
              ))}
            <HighlightedCaption text={scene.voiceoverText} highlights={scene.highlightWords} />
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
