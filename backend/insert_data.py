import sqlite3
import pandas as pd

df = pd.read_csv(
    "datasets/final_dashboard.csv"
)

conn = sqlite3.connect(
    "database/logs.db"
)

for _, row in df.iterrows():

    conn.execute("""
    INSERT INTO telemetry(
    request_id,
    latency,
    tokens_used,
    confidence,
    error_status,
    anomaly,
    reliability_score,
    severity
    )
    VALUES(?,?,?,?,?,?,?,?)
    """,
    (
        int(row["request_id"]),
        float(row["latency"]),
        int(row["tokens_used"]),
        float(row["confidence"]),
        int(row["error_status"]),
        row["anomaly"],
        float(row["reliability_score"]),
        row["severity"]
    ))

conn.commit()
conn.close()

print("Data inserted successfully")