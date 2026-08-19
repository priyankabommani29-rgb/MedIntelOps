import pandas as pd
import google.generativeai as genai
import os

# -----------------------------
# CONFIGURE GEMINI
# -----------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)

# -----------------------------
# PROJECT PATH
# -----------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# -----------------------------
# LOAD DATASET
# -----------------------------

csv_path = os.path.join(
    BASE_DIR,
    "datasets",
    "final_dashboard.csv"
)

df = pd.read_csv(csv_path)

# -----------------------------
# FILTER ANOMALIES
# -----------------------------

anomaly_rows = df[
    df["anomaly"] == "Anomaly"
]

# -----------------------------
# CREATE PROMPT
# -----------------------------

prompt = f"""
You are an expert AIOps engineer.

Analyze the following incident records from a
medical LLM monitoring system.

{anomaly_rows.to_string(index=False)}

Provide:

1. Total number of anomalies
2. Main root causes
3. Overall system health assessment
4. Reliability concerns
5. Recommended corrective actions

Keep response under 250 words.
"""

# -----------------------------
# GEMINI RESPONSE
# -----------------------------

response = model.generate_content(
    prompt
)

summary = response.text

print("\n===== GEMINI SUMMARY =====\n")
print(summary)

# -----------------------------
# SAVE FILE
# -----------------------------

summary_file = os.path.join(
    BASE_DIR,
    "datasets",
    "incident_summary.txt"
)

with open(
    summary_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(summary)

print("\nFile saved successfully:")
print(summary_file)

print("\nGemini analysis completed.")