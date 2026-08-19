import os
import sys
import json
import sqlite3
from typing import Dict, Any

import google.generativeai as genai


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BASE_DIR)

from backend.rag_context_retriever import RAGContextRetriever
from backend.rag_incident_memory import SQLITE_PATH

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )

genai.configure(
    api_key=API_KEY
)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)


# ============================================================
# RAG + GEMINI ANALYZER
# ============================================================

class RAGGeminiAnalyzer:

    def __init__(self):

        self.retriever = RAGContextRetriever()

    # ========================================================
    # BUILD GROUNDED PROMPT
    # ========================================================

    def build_prompt(
        self,
        context: Dict[str, Any]
    ) -> str:

        current = context[
            "current_incident"
        ]

        historical_incidents = context[
            "similar_incidents"
        ]

        historical_context = []

        for index, incident in enumerate(
            historical_incidents,
            start=1
        ):

            historical_context.append(
                f"""
Historical Incident #{index}

Request ID:
{incident["request_id"]}

Similarity Score:
{incident["similarity_score"]:.4f}

Severity:
{incident["severity"]}

Latency:
{incident["latency"]} seconds

Model Confidence:
{incident["confidence"]}

Reliability Score:
{incident["reliability_score"]}%

Error Status:
{incident["error_status"]}

Historical Root Cause:
{incident["root_cause"]}

Historical Resolution:
{incident["resolution"]}

Historical Outcome:
{incident["outcome"]}
"""
            )

        historical_text = "\n".join(
            historical_context
        )

        prompt = f"""
You are the incident intelligence component of MedIntelOps,
a monitoring platform for AI systems used in medical
applications.

Your task is OPERATIONAL INCIDENT ANALYSIS.

You are NOT providing medical diagnosis, treatment,
or patient-specific medical advice.

Analyze the CURRENT INCIDENT using the retrieved
HISTORICAL INCIDENT MEMORY below.

IMPORTANT RULES:

1. Ground your analysis primarily in the telemetry
   and retrieved historical incidents provided.

2. Do not invent infrastructure events, failures,
   root causes, or remediation steps that are not
   reasonably supported by the evidence.

3. If the evidence is insufficient for a definitive
   root cause, explicitly describe the root cause
   as a hypothesis.

4. Similarity scores are retrieval similarity scores,
   not probabilities.

5. Historical resolutions are synthetic operational
   incident records used by this research prototype.

6. Keep recommendations operational and related to
   AI-system monitoring, inference performance,
   reliability, model confidence, and service health.

============================================================
CURRENT INCIDENT
============================================================

Request ID:
{current["request_id"]}

Timestamp:
{current["timestamp"]}

Severity:
{current["severity"]}

Latency:
{current["latency"]} seconds

Tokens Used:
{current["tokens_used"]}

Model Confidence:
{current["confidence"]}

Error Status:
{current["error_status"]}

Reliability Score:
{current["reliability_score"]}%

============================================================
RETRIEVED HISTORICAL INCIDENT MEMORY
============================================================

{historical_text}

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Do not use Markdown.

Use exactly this structure:

{{
    "incident_assessment": "Concise assessment of the current operational incident",

    "likely_root_cause": "Evidence-grounded root cause hypothesis",

    "historical_pattern": "Explain the important pattern shared with retrieved historical incidents",

    "recommended_actions": [
        "Action 1",
        "Action 2",
        "Action 3"
    ],

    "expected_outcome": "Likely operational outcome if the recommendations are effective",

    "evidence_request_ids": [
        123,
        456
    ],

    "confidence": "High, Medium, or Low"
}}
"""

        return prompt

    # ========================================================
    # CLEAN GEMINI JSON
    # ========================================================

    @staticmethod
    def clean_json_response(
        response_text: str
    ) -> str:

        text = response_text.strip()

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    # ========================================================
    # ANALYZE INCIDENT
    # ========================================================
    def save_analysis(
    self,
    analysis: Dict[str, Any]
    ) -> None:

     conn = sqlite3.connect(SQLITE_PATH)
     cursor = conn.cursor()

     cursor.execute(
        """
        INSERT INTO rag_analysis (

            request_id,
            incident_assessment,
            likely_root_cause,
            historical_pattern,
            recommended_actions,
            expected_outcome,
            evidence_request_ids,
            confidence,
            retrieved_incidents

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            analysis["request_id"],

            analysis.get(
                "incident_assessment",
                ""
            ),

            analysis.get(
                "likely_root_cause",
                ""
            ),

            analysis.get(
                "historical_pattern",
                ""
            ),

            json.dumps(
                analysis.get(
                    "recommended_actions",
                    []
                )
            ),

            analysis.get(
                "expected_outcome",
                ""
            ),

            json.dumps(
                analysis.get(
                    "evidence_request_ids",
                    []
                )
            ),

            analysis.get(
                "confidence",
                "Unknown"
            ),

            json.dumps(
                analysis.get(
                    "retrieved_incidents",
                    []
                )
            )
        )
    )

     conn.commit()
     conn.close()
    def analyze_incident(
        self,
        request_id: int,
        top_k: int = 5
    ) -> Dict[str, Any]:

        context = self.retriever.retrieve_context(
            request_id=request_id,
            top_k=top_k
        )

        if context["retrieved_count"] == 0:

            raise ValueError(
                "No historical incidents were retrieved."
            )

        prompt = self.build_prompt(
            context
        )

        print(
            "Sending grounded incident context "
            "to Gemini..."
        )

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "response_mime_type":
                    "application/json"
            }
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        cleaned_response = (
            self.clean_json_response(
                response.text
            )
        )

        try:

            analysis = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError as error:

            print("\nRAW GEMINI RESPONSE:")
            print(response.text)

            raise RuntimeError(
                "Gemini response was not valid JSON."
            ) from error

        # Attach retrieval metadata.
        analysis["request_id"] = (
            request_id
        )

        analysis["retrieved_incidents"] = [
    {
        "request_id":
            incident["request_id"],

        "similarity_score":
            incident["similarity_score"]
    }

    for incident in context[
        "similar_incidents"
    ]
]

# Save grounded RAG analysis to SQLite
        self.save_analysis(analysis)

        return analysis


# ============================================================
# TEST
# ============================================================

def main():

    print("=" * 72)
    print("MEDINTELOPS RAG + GEMINI INCIDENT INTELLIGENCE")
    print("=" * 72)

    analyzer = RAGGeminiAnalyzer()

    request_id = 214

    analysis = analyzer.analyze_incident(
        request_id=request_id,
        top_k=5
    )

    print("\nGROUNDED INCIDENT ANALYSIS")
    print("=" * 72)

    print(
        json.dumps(
            analysis,
            indent=2
        )
    )

    print("=" * 72)


if __name__ == "__main__":

    main()