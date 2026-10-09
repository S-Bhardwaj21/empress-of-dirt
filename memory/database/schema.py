
from memory.database.connection import get_connection

def initialize_database():
    connection = get_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_type TEXT NOT NULL,
            title TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            completed INTEGER NOT NULL,
            completed_at TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS garden_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            location TEXT NOT NULL,
            plants_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()