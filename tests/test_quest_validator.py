import unittest
from types import SimpleNamespace
from verification.rules.quest_validator import validate_quest

def make_plan():
    return SimpleNamespace(
        quest_type=SimpleNamespace(value="explorer"),
        difficulty=2,
        duration_minutes=30
    )

def make_quest():
    return {
        "title": "The Garden Explorer",
        "type": "explorer",
        "duration_minutes": 30,
        "difficulty": 2,
        "story": "Explore the garden and notice something new.",
        "instructions": [
            "Visit the garden with permission.",
            "Observe a plant without touching it.",
            "Share two observations with an adult."
        ],
        "verification": "The child shares two observations.",
        "safety_notes": ["Do not eat or damage plants."]
    }

class TestQuestValidator(unittest.TestCase):
    def test_valid_quest_passes(self):
        valid, errors = validate_quest(make_quest(), make_plan())
        self.assertTrue(valid, errors)

    def test_missing_field_fails(self):
        quest = make_quest()
        del quest["story"]
        valid, errors = validate_quest(quest, make_plan())
        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_invalid_difficulty_fails(self):
        quest = make_quest()
        quest["difficulty"] = 8
        valid, errors = validate_quest(quest, make_plan())
        self.assertFalse(valid)

    def test_wrong_quest_type_fails(self):
        quest = make_quest()
        quest["type"] = "scientist"
        valid, errors = validate_quest(quest, make_plan())
        self.assertFalse(valid)

    def test_unsafe_content_fails(self):
        quest = make_quest()
        quest["story"] = "Pick the flower and eat it."
        valid, errors = validate_quest(quest, make_plan())
        self.assertFalse(valid)

if __name__ == "__main__":
    unittest.main()

