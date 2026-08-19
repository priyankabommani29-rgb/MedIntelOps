import sqlite3
import pandas as pd

conn = sqlite3.connect("database/logs.db")

df = pd.read_sql_query(
    "SELECT * FROM telemetry",
    conn
)

print("\nColumns:\n")
print(df.columns)

conn.close()