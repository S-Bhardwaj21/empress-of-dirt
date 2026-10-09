from dataclasses import dataclass
from typing import List

@dataclass
class QuestConstraints:
    min_duration_minutes: int = 20
    max_duration_minutes: int = 45
    min_difficulty: int = 1
    max_difficulty: int = 5
    avoid_recent_quest_types: List[str] = None
    avoid_recent_targets: List[str] = None

    def __post_init__(self):
        if self.avoid_recent_quest_types is None:
            self.avoid_recent_quest_types = []
        if self.avoid_recent_targets is None:
            self.avoid_recent_targets = []