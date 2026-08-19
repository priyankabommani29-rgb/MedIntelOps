from sentence_transformers import CrossEncoder
import sqlite3
import os
import torch

# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

MODEL_NAME = "cross-encoder/nli-deberta-v3-small"


# ==================================================
# START
# ==================================================

print("=" * 65)
print("MEDINTELOPS NLI HALLUCINATION ENGINE")
print("=" * 65)
print()

print("Loading DeBERTa NLI model...")

model = CrossEncoder(MODEL_NAME)

print("Model loaded successfully.")
print()


# ==================================================
# DATABASE
# ==================================================

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("""
SELECT
    id,
    prompt_text,
    response_text
FROM telemetry
WHERE prompt_text IS NOT NULL
AND response_text IS NOT NULL
""")

records = cursor.fetchall()

print(f"Telemetry records: {len(records)}")
print()


# ==================================================
# PROCESS RECORDS
# ==================================================

processed = 0

total_contradiction = 0.0
total_entailment = 0.0
total_neutral = 0.0

for record_id, prompt, response in records:

    prompt = str(prompt or "").strip()
    response = str(response or "").strip()

    if not prompt or not response:
        continue

    # ----------------------------------------------
    # NLI prediction
    # ----------------------------------------------

    logits = model.predict(
        [(prompt, response)]
    )[0]

    # ----------------------------------------------
    # Convert logits → probabilities
    # ----------------------------------------------

    probabilities = torch.softmax(
        torch.tensor(logits),
        dim=0
    ).numpy()

    contradiction = float(probabilities[0])
    entailment = float(probabilities[1])
    neutral = float(probabilities[2])

    # ----------------------------------------------
    # Save results
    # ----------------------------------------------

    cursor.execute("""
        UPDATE telemetry
        SET
            nli_contradiction = ?,
            nli_entailment = ?,
            nli_neutral = ?
        WHERE id = ?
    """, (
        contradiction,
        entailment,
        neutral,
        record_id
    ))

    processed += 1

    total_contradiction += contradiction
    total_entailment += entailment
    total_neutral += neutral

    # Commit every 25 records
    if processed % 25 == 0:

        conn.commit()

        print(
            f"Processed {processed}/{len(records)} records"
        )


# ==================================================
# FINAL COMMIT
# ==================================================

conn.commit()


# ==================================================
# STATISTICS
# ==================================================

if processed > 0:

    avg_contradiction = (
        total_contradiction / processed
    )

    avg_entailment = (
        total_entailment / processed
    )

    avg_neutral = (
        total_neutral / processed
    )

else:

    avg_contradiction = 0
    avg_entailment = 0
    avg_neutral = 0


# ==================================================
# CLOSE DATABASE
# ==================================================

conn.close()


# ==================================================
# RESULTS
# ==================================================

print()
print("=" * 65)
print("NLI PROCESSING COMPLETE")
print("=" * 65)

print()
print(f"Processed Records       : {processed}")
print(
    f"Average Contradiction   : "
    f"{avg_contradiction:.4f}"
)
print(
    f"Average Entailment      : "
    f"{avg_entailment:.4f}"
)
print(
    f"Average Neutral         : "
    f"{avg_neutral:.4f}"
)

print()
print("Telemetry updated successfully.")
print("=" * 65)