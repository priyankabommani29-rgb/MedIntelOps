import pandas as pd

def load_logs():
    return pd.read_csv(
        "datasets/telemetry_logs.csv"
    )