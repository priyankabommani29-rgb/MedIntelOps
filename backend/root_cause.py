import pandas as pd

df = pd.read_csv(
    "datasets/reliability_results.csv"
)

root_causes = []

for _, row in df.iterrows():

    causes = []

    if row["latency"] > 3:
        causes.append(
            "High latency due to retrieval delay"
        )

    if row["confidence"] < 0.6:
        causes.append(
            "Low confidence due to insufficient evidence"
        )

    if row["tokens_used"] > 1000:
        causes.append(
            "Excessive token consumption"
        )

    if row["error_status"] == 1:
        causes.append(
            "System/API failure detected"
        )

    if len(causes) == 0:
        causes.append(
            "System operating normally"
        )

    root_causes.append(
        " | ".join(causes)
    )

df["root_cause"] = root_causes

df.to_csv(
    "datasets/root_cause_results.csv",
    index=False
)

print(df)