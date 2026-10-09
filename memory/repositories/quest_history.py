from typing import List
from memory.models.quest_record import QuestRecord

class QuestHistory:
    def __init__(self):
        self._records: List[QuestRecord] = []

    def add(self, record: QuestRecord):
        self._records.append(record)

    def get_recent(self, limit: int = 5) -> List[QuestRecord]:
        return self._records[-limit:]

    def get_recent_types(self, limit: int = 5):
        return [record.quest_type for record in self._records[-limit:]]