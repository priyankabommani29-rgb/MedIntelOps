import json
import os
import sys 

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, BASE_DIR)

from backend.claim_extractor import (
    ClaimExtractor,
    load_json,
    KB_DIR
)

# ------------------------------------
# Load Medical Knowledge
# ------------------------------------

DISEASES = load_json("diseases.json")


class EvidenceVerifier:

    def __init__(self):

        self.extractor = ClaimExtractor()

    # ------------------------------------

    def verify(
        self,
        prompt,
        response
    ):

        claims = self.extractor.extract(
            prompt,
            response
        )

        supported = 0
        unsupported = 0
        contradicted = 0

        details = []

        diseases = claims["diseases"]

        medications = claims["medications"]

        tests = claims["laboratory_tests"]

        # ----------------------------------
        # Disease verification
        # ----------------------------------

        for disease in diseases:

            if disease in DISEASES:

                disease_data = DISEASES[disease]

                # --------------------------
                # Medication Verification
                # --------------------------

                for medication in medications:

                    if medication in disease_data["treatments"]:

                        supported += 1

                        details.append({
                            "claim": medication,
                            "status": "Supported",
                            "reason":
                                f"{medication} is a known treatment for {disease}"
                        })

                    else:

                        contradicted += 1

                        details.append({
                            "claim": medication,
                            "status": "Contradicted",
                            "reason":
                                f"{medication} is not listed as a treatment for {disease}"
                        })

                # --------------------------
                # Test Verification
                # --------------------------

                for test in tests:

                    if test in disease_data["tests"]:

                        supported += 1

                        details.append({
                            "claim": test,
                            "status": "Supported",
                            "reason":
                                f"{test} is commonly used for {disease}"
                        })

                    else:

                        unsupported += 1

                        details.append({
                            "claim": test,
                            "status": "Unsupported",
                            "reason":
                                f"No evidence for {test} in {disease}"
                        })

        total = (
            supported +
            unsupported +
            contradicted
        )

        if total == 0:

            evidence_score = 1.0

        else:

            evidence_score = supported / total

        return {

            "claims": claims,

            "supported_claims":
                supported,

            "unsupported_claims":
                unsupported,

            "contradicted_claims":
                contradicted,

            "evidence_score":
                round(
                    evidence_score,
                    3
                ),

            "details":
                details

        }


# ------------------------------------
# TEST
# ------------------------------------

if __name__ == "__main__":

    verifier = EvidenceVerifier()

    prompt = (
        "Patient has hypertension."
    )

    response = (
        "Hypertension is treated with "
        "Metformin. CBC is recommended."
    )

    result = verifier.verify(
        prompt,
        response
    )

    print("=" * 60)
    print("EVIDENCE VERIFICATION")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=4
        )
    )