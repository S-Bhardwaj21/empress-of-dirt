
const API_URL = "http://127.0.0.1:8000";

async function main() {
  console.log("Empress of Dirt — Orchestration Client");
  console.log("--------------------------------------");

  try {
    console.log("\n1. Checking Python API...");
    const healthResponse = await fetch(`${API_URL}/api/health`);
    if (!healthResponse.ok) {
      throw new Error(`Health check failed: HTTP ${healthResponse.status}`);
    }
    const health = await healthResponse.json();
    console.log("API status:", health.status);
    console.log("App:", health.app);

    console.log("\n2. Requesting a garden quest...");
    const questResponse = await fetch(`${API_URL}/api/quest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const responseText = await questResponse.text();
    if (!questResponse.ok) {
      throw new Error(`Quest request failed: HTTP ${questResponse.status}\n${responseText}`);
    }

    const quest = JSON.parse(responseText);
    console.log("\nQuest received successfully!");
    console.log(JSON.stringify(quest, null, 2));
  } catch (error) {
    console.error("\nOrchestration request failed:", error.message);
    process.exitCode = 1;
  }
}

main();