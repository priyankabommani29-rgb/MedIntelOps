import os
import sys
import sqlite3
from typing import Dict, Any, List


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BASE_DIR)

from backend.rag_incident_memory import (
    RAGIncidentMemory,
    SQLITE_PATH
)


class RAGContextRetriever:

    def __init__(self):

        self.memory = RAGIncidentMemory()

    # ========================================================
    # GET INCIDENT FROM SQLITE
    # ========================================================

    def get_incident(
        self,
        request_id: int
    ) -> Dict[str, Any]:

        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                request_id,
                timestamp,
                latency,
                tokens_used,
                confidence,
                error_status,
                anomaly,
                reliability_score,
                severity,
                prompt_text,
                response_text

            FROM telemetry

            WHERE request_id = ?
            """,
            (request_id,)
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:
            return {}

        return dict(row)

    # ========================================================
    # GET HISTORICAL RESOLUTION
    # ========================================================

    def get_resolution(
        self,
        request_id: int
    ) -> Dict[str, Any]:

        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                root_cause,
                resolution,
                outcome,
                resolution_status,
                resolved_at

            FROM incident_memory

            WHERE request_id = ?
            """,
            (request_id,)
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:

            return {
                "root_cause": None,
                "resolution": None,
                "outcome": None,
                "resolution_status": "Unknown",
                "resolved_at": None
            }

        return dict(row)

    # ========================================================
    # RETRIEVE FULL RAG CONTEXT
    # ========================================================

    def retrieve_context(
        self,
        request_id: int,
        top_k: int = 5
    ) -> Dict[str, Any]:

        current_incident = self.get_incident(
            request_id
        )

        if not current_incident:

            raise ValueError(
                f"Request {request_id} was not found."
            )

        # Retrieve one extra because the current incident
        # itself may be returned by ChromaDB.
        raw_results = (
            self.memory.search_similar_incidents(
                current_incident,
                top_k=top_k + 1
            )
        )

        historical_incidents: List[
            Dict[str, Any]
        ] = []

        for result in raw_results:

            historical_request_id = int(
                result["request_id"]
            )

            # Don't use the current incident as its own memory.
            if historical_request_id == request_id:
                continue

            resolution = self.get_resolution(
                historical_request_id
            )

            metadata = result["metadata"]

            historical_incidents.append(
                {
                    "request_id":
                        historical_request_id,

                    "similarity_score":
                        float(
                            result["similarity"]
                        ),

                    "severity":
                        metadata.get("severity"),

                    "latency":
                        metadata.get("latency"),

                    "confidence":
                        metadata.get("confidence"),

                    "reliability_score":
                        metadata.get(
                            "reliability_score"
                        ),

                    "error_status":
                        metadata.get(
                            "error_status"
                        ),

                    "root_cause":
                        resolution.get(
                            "root_cause"
                        ),

                    "resolution":
                        resolution.get(
                            "resolution"
                        ),

                    "outcome":
                        resolution.get(
                            "outcome"
                        ),

                    "resolution_status":
                        resolution.get(
                            "resolution_status"
                        ),

                    "resolved_at":
                        resolution.get(
                            "resolved_at"
                        )
                }
            )

            if len(historical_incidents) >= top_k:
                break

        return {
            "current_incident":
                current_incident,

            "similar_incidents":
                historical_incidents,

            "retrieved_count":
                len(historical_incidents)
        }


# ============================================================
# TEST
# ============================================================

def main():

    print("=" * 72)
    print("MEDINTELOPS RAG CONTEXT RETRIEVER")
    print("=" * 72)

    retriever = RAGContextRetriever()

    # Our known critical test incident
    request_id = 214

    context = retriever.retrieve_context(
        request_id=request_id,
        top_k=5
    )

    current = context["current_incident"]

    print("\nCURRENT INCIDENT")
    print("-" * 72)

    print(
        f"Request ID   : "
        f"{current['request_id']}"
    )

    print(
        f"Severity     : "
        f"{current['severity']}"
    )

    print(
        f"Latency      : "
        f"{current['latency']} seconds"
    )

    print(
        f"Confidence   : "
        f"{current['confidence']}"
    )

    print(
        f"Reliability  : "
        f"{current['reliability_score']}%"
    )

    print("\nRETRIEVED HISTORICAL MEMORY")
    print("=" * 72)

    for index, incident in enumerate(
        context["similar_incidents"],
        start=1
    ):

        print(f"\nHISTORICAL INCIDENT #{index}")
        print("-" * 72)

        print(
            f"Request ID       : "
            f"{incident['request_id']}"
        )

        print(
            f"Similarity Score : "
            f"{incident['similarity_score'] * 100:.2f}%"
        )

        print(
            f"Severity         : "
            f"{incident['severity']}"
        )

        print(
            f"Latency          : "
            f"{incident['latency']} seconds"
        )

        print(
            f"Confidence       : "
            f"{incident['confidence']}"
        )

        print(
            f"Reliability      : "
            f"{incident['reliability_score']}%"
        )

        print(
            f"Resolution Status: "
            f"{incident['resolution_status']}"
        )

        print("\nROOT CAUSE")
        print(
            incident["root_cause"]
            or "Not available"
        )

        print("\nRESOLUTION")
        print(
            incident["resolution"]
            or "Not available"
        )

        print("\nOUTCOME")
        print(
            incident["outcome"]
            or "Not available"
        )

    print("\n" + "=" * 72)

    print(
        f"Retrieved "
        f"{context['retrieved_count']} "
        f"historical incidents."
    )

    print("=" * 72)


if __name__ == "__main__":

    main()