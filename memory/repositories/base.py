from abc import ABC, abstractmethod
from typing import List
from memory.models.quest_record import QuestRecord

class MemoryRepository(ABC):
    @abstractmethod
    def add_quest(self, quest: QuestRecord) -> None:
        pass

    @abstractmethod
    def get_recent_quests(self, limit: int = 5) -> List[QuestRecord]:
        pass