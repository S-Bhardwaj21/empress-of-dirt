import json
REQUIRED_KEYS = {
    "title", "type", "duration_minutes", "difficulty",
    "story", "instructions", "verification", "safety_notes"
}
FORBIDDEN_PHRASES = [
    "eat the plant", "drink the plant", "pick the flower",
    "damage the plant", "hidden door", "secret garden",
    "dangerous path", "magical creature"
]

def validate_quest(quest: dict, plan) -> tuple[bool, list[str]]:
    errors = []
    if not isinstance(quest, dict):
        return False, ["Quest must be a JSON object."]

    missing = REQUIRED_KEYS - quest.keys()
    if missing:
        errors.append(f"Missing fields: {', '.join(sorted(missing))}")

    if errors:
        return False, errors

    if quest["type"] != plan.quest_type.value:
        errors.append("Quest type does not match the plan.")
    if type(quest["difficulty"]) is not int or not 1 <= quest["difficulty"] <= 5:
        errors.append("Difficulty must be an integer from 1 to 5.")
    if type(quest["duration_minutes"]) is not int:
        errors.append("Duration must be an integer.")
    elif not 20 <= quest["duration_minutes"] <= 45:
        errors.append("Duration must be between 20 and 45 minutes.")
    if not isinstance(quest["instructions"], list) or len(quest["instructions"]) != 3:
        errors.append("Exactly three instructions are required.")
    if not isinstance(quest["safety_notes"], list):
        errors.append("Safety notes must be a list.")

    text = json.dumps(quest, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            errors.append(f"Unsafe or disallowed phrase: {phrase}")

    return len(errors) == 0, errors

