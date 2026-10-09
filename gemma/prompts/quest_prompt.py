from quests.quest_engine.plan import QuestPlan

def build_quest_prompt(plan: QuestPlan) -> str:
    constraints = "\n".join(f"- {constraint}" for constraint in plan.constraints)
    return f"""You are the creative quest designer for Empress of Dirt, an offline-first outdoor adventure game for children.
Create one real-world garden quest using the structured quest plan below.
Quest plan:
- Quest type: {plan.quest_type.value}
- Target area: {plan.target_area}
- Target plant: {plan.target_plant}
- Difficulty: {plan.difficulty}
- Duration: {plan.duration_minutes} minutes
- Reason: {plan.reason}
Constraints:
{constraints}
Rules:
- The child must spend most of the quest physically outside.
- Do not require a phone, internet, or screen during the quest.
- Do not ask the child to damage, eat, or remove plants or animals.
- Make the quest playful, specific, and age-appropriate.
- Use the target area and plant meaningfully.
- Do not invent objects that are guaranteed to exist.
- Return ONLY valid JSON.
Return this exact structure:
{{
  "title": "string",
  "type": "{plan.quest_type.value}",
  "duration_minutes": {plan.duration_minutes},
  "difficulty": {plan.difficulty},
  "story": "string",
  "instructions": ["string", "string", "string"],
  "verification": "string",
  "safety_notes": ["string"]
}}"""