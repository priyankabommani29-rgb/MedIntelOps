import sqlite3
import os

from evidence_verifier import EvidenceVerifier


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

verifier = EvidenceVerifier()
conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("""
SELECT
    id,
    prompt_text,
    response_text
FROM telemetry
""")

records = cursor.fetchall()
low = 0
medium = 0
high = 0
critical = 0

total_score = 0

print("=" * 65)
print("MEDINTELOPS HALLUCINATION ENGINE")
print("=" * 65)
for record in records:

    record_id = record[0]

    prompt = record[1] or ""

    response = record[2] or ""

    result = verifier.verify(
        prompt,
        response
    )

    evidence = result["evidence_score"]
    if evidence >= 0.90:

        score = 0.05

        risk = "Low"

        hall_type = "No Hallucination"

        low += 1

    elif evidence >= 0.70:

        score = 0.30

        risk = "Medium"

        hall_type = "Minor Unsupported Claim"

        medium += 1

    elif evidence >= 0.40:

        score = 0.60

        risk = "High"

        hall_type = "Unsupported Recommendation"

        high += 1

    else:

        score = 0.90

        risk = "Critical"

        hall_type = "Contradicted Medical Advice"

        critical += 1
    total_score += score

    cursor.execute(
        """
        UPDATE telemetry

        SET

        hallucination_score=?,

        hallucination_risk=?,

        hallucination_type=?,

        evidence_score=?,

        supported_claims=?,

        unsupported_claims=?,

        contradicted_claims=?

        WHERE id=?
        """,

        (

            score,

            risk,

            hall_type,

            evidence,

            result["supported_claims"],

            result["unsupported_claims"],

            result["contradicted_claims"],

            record_id

        )

    )
conn.commit()

conn.close()

print()

print(f"Processed Records : {len(records)}")

print()

print(f"Low Risk      : {low}")

print(f"Medium Risk   : {medium}")

print(f"High Risk     : {high}")

print(f"Critical Risk : {critical}")

print()

print(
    f"Average Hallucination Score : "
    f"{total_score/len(records):.3f}"
)

print()

print("=" * 65)

print("Telemetry updated successfully.")

print("=" * 65)