import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 65)
print("MEDINTELOPS NLI SCHEMA")
print("=" * 65)

existing = {
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(telemetry)"
    ).fetchall()
}

columns = {
    "nli_contradiction": "REAL",
    "nli_entailment": "REAL",
    "nli_neutral": "REAL"
}

for column, dtype in columns.items():

    if column not in existing:

        cursor.execute(
            f"ALTER TABLE telemetry ADD COLUMN {column} {dtype}"
        )

        print(f"Added: {column}")

    else:

        print(f"Already exists: {column}")

conn.commit()

print("\nNLI schema upgrade completed.")

conn.close()