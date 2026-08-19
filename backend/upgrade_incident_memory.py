import os
import sqlite3


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)


def upgrade_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS incident_memory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            request_id INTEGER NOT NULL UNIQUE,

            root_cause TEXT,

            resolution TEXT,

            outcome TEXT,

            resolution_status TEXT DEFAULT 'Unresolved',

            resolved_at TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (request_id)
                REFERENCES telemetry(request_id)
        )
        """
    )

    conn.commit()

    print("=" * 65)
    print("MEDINTELOPS INCIDENT MEMORY MIGRATION")
    print("=" * 65)

    print(
        "incident_memory table created successfully."
    )

    cursor.execute(
        "PRAGMA table_info(incident_memory)"
    )

    columns = cursor.fetchall()

    print("\nTABLE SCHEMA")
    print("-" * 65)

    for column in columns:
        print(column)

    conn.close()

    print("\nMigration completed successfully.")
    print("=" * 65)


if __name__ == "__main__":

    upgrade_database()