import { getAudioDurationInSeconds } from "@remotion/media-utils";

async function main() {
  try {
    const duration = await getAudioDurationInSeconds("public/narasi/carrick.mp3");
    console.log("DURATION_SECONDS:", duration);
    console.log("TOTAL_FRAMES_30FPS:", Math.ceil(duration * 30));
  } catch (err) {
    console.error("Error:", err);
  }
}

main();
