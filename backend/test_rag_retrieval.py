import os
import sys
import sqlite3

# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BASE_DIR)

from backend.rag_incident_memory import (
    RAGIncidentMemory,
    SQLITE_PATH
)


# ============================================================
# LOAD A CRITICAL INCIDENT
# ============================================================

def load_critical_incident():

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

        WHERE LOWER(TRIM(severity)) = 'critical'

        ORDER BY reliability_score ASC

        LIMIT 1
        """
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return dict(row)


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("=" * 70)
    print("MEDINTELOPS RAG RETRIEVAL TEST")
    print("=" * 70)

    incident = load_critical_incident()

    if incident is None:

        print("No critical incident found.")
        return

    print("\nCURRENT INCIDENT")
    print("-" * 70)

    print(
        f"Request ID       : "
        f"{incident['request_id']}"
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
        f"Error Status     : "
        f"{incident['error_status']}"
    )

    # ========================================================
    # INITIALIZE MEMORY
    # ========================================================

    memory = RAGIncidentMemory()

    # ========================================================
    # RETRIEVE MORE THAN 5
    #
    # The current incident itself is already stored in ChromaDB,
    # so retrieve 6 and remove the identical request ID.
    # ========================================================

    results = memory.search_similar_incidents(
        incident,
        top_k=6
    )

    results = [
        result
        for result in results
        if str(result["request_id"])
        != str(incident["request_id"])
    ]

    results = results[:5]

    print("\nTOP 5 SIMILAR HISTORICAL INCIDENTS")
    print("=" * 70)

    if not results:

        print("No similar incidents found.")
        return

    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = result["metadata"]

        similarity_percentage = (
            result["similarity"] * 100
        )

        print(
            f"\n#{index}"
        )

        print(
            f"Request ID       : "
            f"{result['request_id']}"
        )

        print(
            f"Similarity       : "
            f"{similarity_percentage:.2f}%"
        )

        print(
            f"Severity         : "
            f"{metadata.get('severity')}"
        )

        print(
            f"Latency          : "
            f"{metadata.get('latency')} seconds"
        )

        print(
            f"Confidence       : "
            f"{metadata.get('confidence')}"
        )

        print(
            f"Reliability      : "
            f"{metadata.get('reliability_score')}%"
        )

        print(
            f"Error Status     : "
            f"{metadata.get('error_status')}"
        )

        print("-" * 70)

    print("\nRAG retrieval test completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()