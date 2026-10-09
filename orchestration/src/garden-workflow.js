
import { createStep, createWorkflow } from "@mastra/core/workflows";
import { z } from "zod";

const API_URL = "http://127.0.0.1:8000";

const checkGardenAPI = createStep({
  id: "check-garden-api",
  description: "Check that the Empress of Dirt Python API is available.",
  inputSchema: z.object({}),
  outputSchema: z.object({
    status: z.string(),
    app: z.string()
  }),
  execute: async () => {
    const response = await fetch(`${API_URL}/api/health`);
    if (!response.ok) {
      throw new Error(`Garden API health check failed: HTTP ${response.status}`);
    }
    const health = await response.json();
    return {
      status: health.status,
      app: health.app
    };
  }
});

const generateGardenQuest = createStep({
  id: "generate-garden-quest",
  description: "Request a personalized garden quest from the existing Python engine.",
  inputSchema: z.object({
    status: z.string(),
    app: z.string()
  }),
  outputSchema: z.object({
    quest: z.unknown(),
    target_area: z.string(),
    target_plant: z.string(),
    reason: z.string(),
    garden_source: z.string()
  }),
  execute: async () => {
    const response = await fetch(`${API_URL}/api/quest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const body = await response.text();
    if (!response.ok) {
      throw new Error(`Garden quest request failed: HTTP ${response.status}\n${body}`);
    }
    const result = JSON.parse(body);
    return {
      quest: result.quest,
      target_area: result.target_area,
      target_plant: result.target_plant,
      reason: result.reason,
      garden_source: result.garden_source
    };
  }
});

export const gardenWorkflow = createWorkflow({
  id: "empress-garden-quest",
  inputSchema: z.object({}),
  outputSchema: z.object({
    quest: z.unknown(),
    target_area: z.string(),
    target_plant: z.string(),
    reason: z.string(),
    garden_source: z.string()
  })
})
  .then(checkGardenAPI)
  .then(generateGardenQuest)
  .commit();