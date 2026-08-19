import pandas as pd

df = pd.read_csv(
    "datasets/ai_results.csv"
)

recommendations = []

for _, row in df.iterrows():

    if row["severity"] == "Critical":

        rec = """
Reduce retrieval latency,
verify medical knowledge base,
and investigate API failures.
"""

    elif row["severity"] == "High":

        rec = """
Monitor retrieval performance
and optimize token usage.
"""

    elif row["severity"] == "Medium":

        rec = """
Continue monitoring system health.
"""

    else:

        rec = """
No action required.
"""

    recommendations.append(
        rec.strip()
    )

df["recommendation"] = recommendations

df.to_csv(
    "datasets/final_dashboard.csv",
    index=False
)