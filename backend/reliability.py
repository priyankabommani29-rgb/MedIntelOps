import pandas as pd

df = pd.read_csv("datasets/anomaly_results.csv")

def latency_score(latency):
    if latency <= 1.5:
        return 100
    elif latency <= 3:
        return 80
    else:
        return 40

def error_score(error):
    return 100 if error == 0 else 40

reliability_scores = []

for _, row in df.iterrows():

    confidence = row["confidence"] * 100

    latency = latency_score(
        row["latency"]
    )

    error = error_score(
        row["error_status"]
    )

    reliability = (
        0.5 * confidence +
        0.3 * latency +
        0.2 * error
    )

    reliability_scores.append(
        round(reliability,2)
    )

df["reliability_score"] = reliability_scores

df.to_csv(
    "datasets/reliability_results.csv",
    index=False
)

print(df)