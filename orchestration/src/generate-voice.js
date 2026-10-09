
const apiKey = process.env.ELEVENLABS_API_KEY;
const voiceId = "cgSgspJ2msm6clMCkdW9";
const text = "Young explorer! A mystery awaits in your garden! Something has been visiting your flowers... and today, YOU are the detective!";

if (!apiKey) {
  console.error("Missing ELEVENLABS_API_KEY environment variable.");
  process.exit(1);
}

async function main() {
  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
    {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
      },
      body: JSON.stringify({
        text,
        model_id: "eleven_multilingual_v2",
        voice_settings: {
  stability: 0.25,
  similarity_boost: 0.75,
  style: 0.8,
  use_speaker_boost: true,
  speed: 1.08
}
      })
    }
  );

  if (!response.ok) {
    throw new Error(
      `ElevenLabs returned HTTP ${response.status}: ${await response.text()}`
    );
  }

  const audio = Buffer.from(await response.arrayBuffer());
  const fs = await import("node:fs/promises");
  const path = await import("node:path");
  const outputDir = path.join(process.cwd(), "output");
  await fs.mkdir(outputDir, { recursive: true });
  const outputPath = path.join(outputDir, "garden-quest-announcement.mp3");
  await fs.writeFile(outputPath, audio);

  console.log("Garden quest narration generated successfully!");
  console.log(`Saved to: ${outputPath}`);
  console.log(`Audio size: ${audio.length.toLocaleString()} bytes`);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});