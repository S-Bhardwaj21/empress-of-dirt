from memory.repositories.base import MemoryRepository
from sensors.simulator.garden_state import GardenState
from quests.quest_types.types import QuestType
from quests.quest_engine.plan import QuestPlan
from quests.constraints.constraints import QuestConstraints

class QuestEngine:
    def __init__(self, memory: MemoryRepository):
        self.memory = memory

    def choose_quest_type(self, garden: GardenState) -> QuestType:
        recent = self.memory.get_recent_quests(limit=6)
        recent_types = [quest.quest_type for quest in recent]
        available = []
        if garden.unexplored_areas:
            available.extend([QuestType.EXPLORER, QuestType.TREASURE])
        if garden.plants:
            available.extend([QuestType.DETECTIVE, QuestType.SCIENTIST, QuestType.ARTIST, QuestType.RESCUE])
        for quest_type in available:
            if quest_type not in recent_types:
                return quest_type
        for quest_type in available:
            if not recent_types or quest_type != recent_types[0]:
                return quest_type
        return available[0] if available else QuestType.EXPLORER

    def build_constraints(self, garden: GardenState) -> QuestConstraints:
        recent = self.memory.get_recent_quests(limit=6)
        return QuestConstraints(
            avoid_recent_quest_types=[quest.quest_type.value for quest in recent],
            avoid_recent_targets=[quest.title for quest in recent]
        )

    def choose_difficulty(self) -> int:
        recent = self.memory.get_recent_quests(limit=3)
        if not recent:
            return 1
        latest = recent[0]
        if latest.completed:
            return min(5, latest.difficulty + 1)
        return max(1, latest.difficulty - 1)

    def choose_target(self, items: list, recent_titles: list, fallback: str) -> str:
        if not items:
            return fallback
        for item in items:
            if item.lower().replace("_", " ") not in " ".join(recent_titles).lower():
                return item
        return items[0]

    def create_plan(self, garden: GardenState) -> QuestPlan:
        quest_type = self.choose_quest_type(garden)
        constraints = self.build_constraints(garden)
        recent_titles = constraints.avoid_recent_targets
        target_area = self.choose_target(
            garden.unexplored_areas,
            recent_titles,
            garden.location
        )
        target_plant = self.choose_target(
            garden.plants,
            recent_titles,
            "garden"
        )
        reasons = {
            QuestType.EXPLORER: "Investigate a garden area and look for details you have not noticed before.",
            QuestType.TREASURE: "Search for a natural pattern, colour, or shape in the garden.",
            QuestType.DETECTIVE: "Compare details in the garden and look for clues.",
            QuestType.SCIENTIST: "Make observations and compare them with the garden's sensor readings.",
            QuestType.ARTIST: "Find natural shapes, colours, and patterns to turn into a creative challenge.",
            QuestType.RESCUE: "Look for signs that a plant may need an adult's care."
        }
        difficulty = self.choose_difficulty()
        duration = min(30, max(10, 10 + difficulty * 4))
        return QuestPlan(
            quest_type=quest_type,
            target_area=target_area,
            target_plant=target_plant,
            difficulty=difficulty,
            duration_minutes=duration,
            reason=reasons.get(quest_type, "Explore the garden carefully."),
            constraints=[
                "Stay in the permitted garden area.",
                "Do not eat, pick, or damage plants.",
                "Observe insects and animals without touching them.",
                "Ask an adult before moving objects or approaching unfamiliar areas."
            ]
        )

