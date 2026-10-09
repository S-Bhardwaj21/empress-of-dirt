
const apiKey = process.env.ELEVENLABS_API_KEY;

if (!apiKey) {
  console.error("Missing ELEVENLABS_API_KEY environment variable.");
  process.exit(1);
}

async function main() {
  const response = await fetch(
    "https://api.elevenlabs.io/v1/voices?page_size=30",
    { headers: { "xi-api-key": apiKey } }
  );

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`ElevenLabs API returned HTTP ${response.status}: ${message}`);
  }

  const data = await response.json();
  const voices = data.voices ?? [];

  console.log(`Available voices returned: ${voices.length}\n`);

  for (const voice of voices) {
    console.log(`Name: ${voice.name}`);
    console.log(`ID: ${voice.voice_id}`);
    console.log(`Description: ${voice.description ?? "Not provided"}`);
    console.log("---");
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});