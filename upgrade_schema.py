import sqlite3

DB_PATH = "database/logs.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(telemetry)")
existing_columns = {
    row[1] for row in cursor.fetchall()
}

print("Existing columns:")
print(existing_columns)

# Columns required for the upgraded MedIntelOps telemetry schema
new_columns = {
    "timestamp": "TEXT",
    "prompt_text": "TEXT",
    "response_text": "TEXT",
}

for column_name, column_type in new_columns.items():

    if column_name not in existing_columns:

        cursor.execute(
            f"ALTER TABLE telemetry "
            f"ADD COLUMN {column_name} {column_type}"
        )

        print(f"Added column: {column_name}")

    else:

        print(
            f"Column already exists: {column_name}"
        )

conn.commit()

# Verify final schema
cursor.execute("PRAGMA table_info(telemetry)")
columns = cursor.fetchall()

print("\nUPDATED TELEMETRY SCHEMA")
print("=" * 60)

for column in columns:
    print(column)

conn.close()

print("\nSchema upgrade completed successfully.")