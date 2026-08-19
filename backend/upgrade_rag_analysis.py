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
        CREATE TABLE IF NOT EXISTS rag_analysis (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            request_id INTEGER NOT NULL,

            incident_assessment TEXT,

            likely_root_cause TEXT,

            historical_pattern TEXT,

            recommended_actions TEXT,

            expected_outcome TEXT,

            evidence_request_ids TEXT,

            confidence TEXT,

            retrieved_incidents TEXT,

            generated_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (request_id)
                REFERENCES telemetry(request_id)
        )
        """
    )

    conn.commit()

    print("=" * 65)
    print("MEDINTELOPS RAG ANALYSIS MIGRATION")
    print("=" * 65)

    print("rag_analysis table created successfully.")

    cursor.execute(
        "PRAGMA table_info(rag_analysis)"
    )

    print("\nTABLE SCHEMA")
    print("-" * 65)

    for column in cursor.fetchall():
        print(column)

    conn.close()

    print("\nMigration completed successfully.")
    print("=" * 65)


if __name__ == "__main__":
    upgrade_database()