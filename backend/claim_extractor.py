import json
import os
import re


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

KB_DIR = os.path.join(
    BASE_DIR,
    "knowledge_base"
)


def load_json(filename):

    with open(
        os.path.join(KB_DIR, filename),
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ------------------------------------
# Load Knowledge Base
# ------------------------------------

DISEASES = load_json("diseases.json")

MEDICATIONS = load_json("medications.json")

SYMPTOMS = load_json("symptoms.json")

PROCEDURES = load_json("procedures.json")

LAB_TESTS = load_json("laboratory_tests.json")


# ------------------------------------
# Normalize text
# ------------------------------------

def normalize(text):

    return re.sub(
        r"\s+",
        " ",
        text.lower()
    )


# ------------------------------------
# Claim Extractor
# ------------------------------------

class ClaimExtractor:

    def __init__(self):

        self.diseases = list(
            DISEASES.keys()
        )

        self.medications = MEDICATIONS

        self.symptoms = SYMPTOMS

        self.procedures = PROCEDURES

        self.lab_tests = LAB_TESTS

    # ------------------------------

    def find_matches(
        self,
        text,
        candidates
    ):

        found = []

        text = normalize(text)

        for item in candidates:

            if item.lower() in text:

                found.append(item)

        return sorted(
            list(set(found))
        )

    # ------------------------------

    def extract(
        self,
        prompt,
        response
    ):

        combined = (
            prompt +
            " " +
            response
        )

        return {

            "diseases":
                self.find_matches(
                    combined,
                    self.diseases
                ),

            "medications":
                self.find_matches(
                    combined,
                    self.medications
                ),

            "symptoms":
                self.find_matches(
                    combined,
                    self.symptoms
                ),

            "procedures":
                self.find_matches(
                    combined,
                    self.procedures
                ),

            "laboratory_tests":
                self.find_matches(
                    combined,
                    self.lab_tests
                )

        }


# ------------------------------------
# Test
# ------------------------------------

if __name__ == "__main__":

    extractor = ClaimExtractor()

    prompt = (
        "Patient has hypertension."
    )

    response = (
        "The patient has hypertension. "
        "Metformin was prescribed. "
        "CBC should be performed. "
        "Blood Pressure Measurement is recommended."
    )

    claims = extractor.extract(
        prompt,
        response
    )

    print("=" * 60)
    print("CLAIM EXTRACTION")
    print("=" * 60)

    print(
        json.dumps(
            claims,
            indent=4
        )
    )