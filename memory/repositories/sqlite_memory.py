from typing import List
from memory.models.quest_record import QuestRecord
from memory.database.connection import get_connection
from memory.repositories.base import MemoryRepository

class SQLiteMemoryRepository(MemoryRepository):
    def add_quest(self, quest: QuestRecord) -> None:
        connection = get_connection()
        connection.execute(
            """
            INSERT INTO quests
            (quest_type, title, difficulty, completed, completed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                quest.quest_type.value,
                quest.title,
                quest.difficulty,
                int(quest.completed),
                quest.completed_at.isoformat()
            )
        )
        connection.commit()
        connection.close()

    def get_recent_quests(self, limit: int = 5) -> List[QuestRecord]:
        connection = get_connection()
        rows = connection.execute(
            """
            SELECT quest_type, title, difficulty, completed, completed_at
            FROM quests
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        connection.close()

        return [
            QuestRecord.from_dict({
                "quest_type": row[0],
                "title": row[1],
                "difficulty": row[2],
                "completed": bool(row[3]),
                "completed_at": row[4]
            })
            for row in rows
        ]