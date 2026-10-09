import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from memory.models.quest_record import QuestRecord
from memory.repositories.sqlite_memory import SQLiteMemoryRepository
from memory.database.schema import initialize_database

class TestSQLiteMemory(unittest.TestCase):
    def test_quest_persists_and_can_be_retrieved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "test_empress.db"
            with patch("memory.database.connection.DB_PATH", test_db):
                initialize_database()
                memory = SQLiteMemoryRepository()
                quest = QuestRecord(
                    quest_type=__import__("quests.quest_types.types", fromlist=["QuestType"]).QuestType.EXPLORER,
                    title="The Tulsi Explorer",
                    difficulty=2,
                    completed=True,
                    completed_at=datetime.now()
                )
                memory.add_quest(quest)
                retrieved = memory.get_recent_quests(limit=5)
                self.assertEqual(len(retrieved), 1)
                self.assertEqual(retrieved[0].title, "The Tulsi Explorer")
                self.assertTrue(retrieved[0].completed)
                self.assertEqual(retrieved[0].difficulty, 2)

if __name__ == "__main__":
    unittest.main()

