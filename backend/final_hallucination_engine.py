import sqlite3
import os

# ==================================================
# DATABASE
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 65)
print("MEDINTELOPS FINAL HALLUCINATION ENGINE")
print("=" * 65)
print()


# ==================================================
# LOAD TELEMETRY
# ==================================================

cursor.execute("""
SELECT
    id,
    evidence_score,
    nli_contradiction
FROM telemetry
""")

records = cursor.fetchall()

print(f"Telemetry records: {len(records)}")
print()


# ==================================================
# PROCESS
# ==================================================

processed = 0

risk_counts = {
    "Low": 0,
    "Medium": 0,
    "High": 0,
    "Critical": 0
}

total_score = 0.0


for record_id, evidence_score, nli_contradiction in records:

    evidence_score = (
        float(evidence_score)
        if evidence_score is not None
        else 0.0
    )

    nli_contradiction = (
        float(nli_contradiction)
        if nli_contradiction is not None
        else 0.0
    )

    # ------------------------------------------------
    # Final hallucination score
    #
    # 40% evidence failure
    # 60% semantic contradiction
    # ------------------------------------------------

    evidence_risk = 1.0 - evidence_score

    final_score = (
        0.40 * evidence_risk
        +
        0.60 * nli_contradiction
    )

    final_score = max(
        0.0,
        min(1.0, final_score)
    )

    # ------------------------------------------------
    # Risk classification
    # ------------------------------------------------

    if final_score < 0.20:

        risk = "Low"

    elif final_score < 0.40:

        risk = "Medium"

    elif final_score < 0.70:

        risk = "High"

    else:

        risk = "Critical"

    # ------------------------------------------------
    # Save
    # ------------------------------------------------

    cursor.execute("""
        UPDATE telemetry
        SET
            final_hallucination_score = ?,
            final_hallucination_risk = ?
        WHERE id = ?
    """, (
        final_score,
        risk,
        record_id
    ))

    processed += 1
    total_score += final_score
    risk_counts[risk] += 1


# ==================================================
# COMMIT
# ==================================================

conn.commit()


# ==================================================
# STATISTICS
# ==================================================

average_score = (
    total_score / processed
    if processed > 0
    else 0
)

conn.close()


# ==================================================
# RESULTS
# ==================================================

print("=" * 65)
print("FINAL HALLUCINATION ANALYSIS")
print("=" * 65)

print()
print(f"Processed Records : {processed}")
print()

print(
    f"Low Risk          : "
    f"{risk_counts['Low']}"
)

print(
    f"Medium Risk       : "
    f"{risk_counts['Medium']}"
)

print(
    f"High Risk         : "
    f"{risk_counts['High']}"
)

print(
    f"Critical Risk     : "
    f"{risk_counts['Critical']}"
)

print()
print(
    f"Average Final Hallucination Score : "
    f"{average_score:.4f}"
)

print()
print("Telemetry updated successfully.")
print("=" * 65)