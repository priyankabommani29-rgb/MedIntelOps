import pandas as pd

df = pd.read_csv(
    "datasets/root_cause_results.csv"
)

severity = []

for _, row in df.iterrows():

    if row["reliability_score"] < 50:
        severity.append("Critical")

    elif row["reliability_score"] < 70:
        severity.append("High")

    elif row["reliability_score"] < 85:
        severity.append("Medium")

    else:
        severity.append("Low")

df["severity"] = severity

df.to_csv(
    "datasets/final_results.csv",
    index=False
)

print(df)