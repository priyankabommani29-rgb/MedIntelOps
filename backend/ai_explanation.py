import pandas as pd

df = pd.read_csv(
    "datasets/final_results.csv"
)

explanations = []

for _, row in df.iterrows():

    if row["severity"] == "Critical":

        explanation = """
Critical incident detected.
High latency and low confidence indicate
possible retrieval failure or system instability.
Immediate investigation is recommended.
"""

    elif row["severity"] == "High":

        explanation = """
High severity anomaly detected.
System performance degradation observed.
Review retrieval performance and API health.
"""

    elif row["severity"] == "Medium":

        explanation = """
Moderate reliability issue detected.
Monitor system metrics and confidence trends.
"""

    else:

        explanation = """
System operating within expected limits.
No immediate action required.
"""

    explanations.append(
        explanation.strip()
    )

df["ai_explanation"] = explanations

df.to_csv(
    "datasets/ai_results.csv",
    index=False
)

print(df)