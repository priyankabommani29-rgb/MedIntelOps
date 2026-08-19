import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("datasets/telemetry_logs.csv")

features = df[
    ["latency", "tokens_used", "confidence"]
]

model = IsolationForest(
    contamination=0.2,
    random_state=42
)

df["anomaly"] = model.fit_predict(features)

df["anomaly"] = df["anomaly"].map(
    {1: "Normal", -1: "Anomaly"}
)

df.to_csv(
    "datasets/anomaly_results.csv",
    index=False
)

print(df)