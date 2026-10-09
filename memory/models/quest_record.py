from dataclasses import dataclass
from datetime import datetime
from quests.quest_types.types import QuestType

@dataclass
class QuestRecord:
    quest_type: QuestType
    title: str
    difficulty: int
    completed: bool
    completed_at: datetime

    def to_dict(self) -> dict:
        return {
            "quest_type": self.quest_type.value,
            "title": self.title,
            "difficulty": self.difficulty,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            quest_type=QuestType(data["quest_type"]),
            title=data["title"],
            difficulty=data["difficulty"],
            completed=data["completed"],
            completed_at=datetime.fromisoformat(data["completed_at"])
        )