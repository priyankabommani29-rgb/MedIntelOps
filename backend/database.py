import sqlite3

conn = sqlite3.connect(
    "database/logs.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS telemetry(
id INTEGER PRIMARY KEY AUTOINCREMENT,
request_id INTEGER,
latency REAL,
tokens_used INTEGER,
confidence REAL,
error_status INTEGER,
anomaly TEXT,
reliability_score REAL,
severity TEXT
)
""")

conn.commit()