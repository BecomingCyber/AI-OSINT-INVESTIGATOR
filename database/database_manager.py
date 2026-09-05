import json
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "osint.db"


def initialize_database():
    """
    Create the investigations table if it does not already exist.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                collected_data TEXT NOT NULL,
                ai_analysis TEXT,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()


def save_investigation(target, collected_data, analysis_result):
    """
    Save collected OSINT evidence and AI analysis to SQLite.
    """

    collected_json = json.dumps(
        collected_data,
        default=str
    )

    status = analysis_result.get("status", "unknown")
    ai_analysis = analysis_result.get("analysis")

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO investigations (
                target,
                collected_data,
                ai_analysis,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                target,
                collected_json,
                ai_analysis,
                status,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def get_investigation(investigation_id):
    """
    Retrieve one investigation by its database ID.
    """

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM investigations
            WHERE id = ?
            """,
            (investigation_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        result = dict(row)

        result["collected_data"] = json.loads(
            result["collected_data"]
        )

        return result


def get_all_investigations():
    """
    Retrieve all saved investigations,
    newest first.
    """

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                target,
                status,
                created_at
            FROM investigations
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


if __name__ == "__main__":
    initialize_database()

    print("Database ready:")
    print(DB_PATH)
