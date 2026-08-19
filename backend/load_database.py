import sqlite3
import pandas as pd

def load_data():

    conn = sqlite3.connect(
        "database/logs.db"
    )

    df = pd.read_sql_query(
        "SELECT * FROM telemetry",
        conn
    )

    conn.close()

    return df