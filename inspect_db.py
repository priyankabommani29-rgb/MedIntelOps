import sqlite3

conn = sqlite3.connect("database/logs.db")
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\nTABLES FOUND:")
print(tables)

# Show columns for every table
for table in tables:
    table_name = table[0]

    print(f"\n{'=' * 50}")
    print(f"TABLE: {table_name}")
    print("=" * 50)

    cursor.execute(f"PRAGMA table_info({table_name});")

    columns = cursor.fetchall()

    for column in columns:
        print(column)

conn.close()