from dataclasses import dataclass, field
from typing import List
from quests.quest_types.types import QuestType

@dataclass
class QuestPlan:
    quest_type: QuestType
    target_area: str
    target_plant: str
    difficulty: int
    duration_minutes: int
    reason: str
    constraints: List[str] = field(default_factory=list)