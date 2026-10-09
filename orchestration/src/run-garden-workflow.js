
import { gardenWorkflow } from "./garden-workflow.js";

async function main() {
  console.log("Empress of Dirt — Mastra Workflow");
  console.log("=================================");

  const run = await gardenWorkflow.createRun();
  const result = await run.start({ inputData: {} });

  console.log("\nWorkflow status:", result.status);

  if (result.status !== "success") {
    console.error(JSON.stringify(result, null, 2));
    process.exitCode = 1;
    return;
  }

  console.log("\nGarden quest generated successfully!");
  console.log(JSON.stringify(result.result, null, 2));
}

main().catch((error) => {
  console.error("\nWorkflow failed:", error);
  process.exitCode = 1;
});