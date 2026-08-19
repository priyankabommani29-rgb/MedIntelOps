import sqlite3
import random
import json
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

KB_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base"
)
def load_json(filename):

    with open(
        os.path.join(KB_PATH, filename),
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


DISEASES = load_json("diseases.json")
PROMPTS = [

"A patient has {}. What is the recommended treatment?",

"What medications are commonly prescribed for {}?",

"A patient is diagnosed with {}. Which laboratory tests should be ordered?",

"How should {} be managed?",

"What are the symptoms of {}?",

"How do you diagnose {}?",

"A patient presents with {}. What investigations are recommended?",

"What is the first-line therapy for {}?",

"What follow-up should be performed for {}?"

]
def generate_correct_response(disease):

    info = DISEASES[disease]

    treatment = ", ".join(
        info["treatments"]
    )

    symptoms = ", ".join(
        info["symptoms"]
    )

    tests = ", ".join(
        info["tests"]
    )

    return (
        f"{disease} commonly presents with "
        f"{symptoms}. "
        f"Recommended treatment includes "
        f"{treatment}. "
        f"Suggested investigations include "
        f"{tests}."
    )
WRONG_MEDICATIONS = [

"Insulin",

"Chocolate",

"Vitamin C",

"Paracetamol",

"Morphine"

]

WRONG_TESTS = [

"MRI Brain",

"PET Scan",

"ECG",

"CT Brain"

]

FABRICATED_DRUGS = [

"Cardioxin",

"Medicinex",

"UltraCure",

"HealFast"

]
def generate_hallucinated_response(disease):

    mode = random.choice(

        [

            "medication",

            "test",

            "fabricated"

        ]

    )

    if mode == "medication":

        med = random.choice(
            WRONG_MEDICATIONS
        )

        return (
            f"The primary treatment for "
            f"{disease} is {med}. "
            f"This completely cures the disease."
        )

    elif mode == "test":

        test = random.choice(
            WRONG_TESTS
        )

        return (
            f"The gold standard diagnostic test "
            f"for {disease} is {test}."
        )

    else:

        drug = random.choice(
            FABRICATED_DRUGS
        )

        return (
            f"{drug} is the recommended therapy "
            f"for {disease}."
        )
# =====================================================
# CONNECT TO SQLITE
# =====================================================

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute(
    """
    SELECT id
    FROM telemetry
    ORDER BY id
    """
)

records = cursor.fetchall()

print("=" * 60)
print("GENERATING MEDICAL CONVERSATIONS")
print("=" * 60)

correct = 0
hallucinated = 0

# =====================================================
# GENERATE CONVERSATIONS
# =====================================================

for row in records:

    record_id = row[0]

    disease = random.choice(
        list(DISEASES.keys())
    )

    prompt = random.choice(
        PROMPTS
    ).format(disease)

    # --------------------------
    # 75% Correct
    # --------------------------

    if random.random() < 0.75:

        response = generate_correct_response(
            disease
        )

        correct += 1

    # --------------------------
    # 25% Hallucinated
    # --------------------------

    else:

        response = generate_hallucinated_response(
            disease
        )

        hallucinated += 1

    cursor.execute(
        """
        UPDATE telemetry

        SET
            prompt_text=?,
            response_text=?

        WHERE id=?
        """,
        (
            prompt,
            response,
            record_id
        )
    )

conn.commit()

conn.close()
# =====================================================
# SUMMARY
# =====================================================

print()

print("Medical conversations generated.")

print(f"Correct responses      : {correct}")

print(f"Hallucinated responses : {hallucinated}")

print(f"Total                  : {correct + hallucinated}")

print("=" * 60)