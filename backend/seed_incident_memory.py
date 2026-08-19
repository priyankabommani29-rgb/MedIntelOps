import os
import sqlite3
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)


def determine_resolution(
    latency,
    confidence,
    reliability,
    error_status
):

    # --------------------------------------------------
    # SEVERE LATENCY + LOW CONFIDENCE
    # --------------------------------------------------

    if latency >= 5 and confidence < 0.60:

        root_cause = (
            "Severe inference latency combined with "
            "reduced model confidence caused overall "
            "service reliability degradation."
        )

        resolution = (
            "Reduce inference workload, inspect model "
            "serving latency, verify upstream dependencies, "
            "and temporarily route requests through the "
            "stable inference path."
        )

        outcome = (
            "Latency returned toward the normal operating "
            "range and reliability improved."
        )

    # --------------------------------------------------
    # SEVERE LATENCY
    # --------------------------------------------------

    elif latency >= 5:

        root_cause = (
            "Inference latency exceeded the expected "
            "operational threshold."
        )

        resolution = (
            "Inspect model-serving resources, request "
            "queue depth, and upstream service latency. "
            "Scale or restart the affected inference "
            "worker when required."
        )

        outcome = (
            "Response latency decreased after inference "
            "capacity was stabilized."
        )

    # --------------------------------------------------
    # LOW CONFIDENCE
    # --------------------------------------------------

    elif confidence < 0.60:

        root_cause = (
            "The model produced unusually low-confidence "
            "responses, reducing the reliability score."
        )

        resolution = (
            "Review the affected request distribution, "
            "validate input quality, and route uncertain "
            "responses for additional verification."
        )

        outcome = (
            "Low-confidence requests were isolated and "
            "system reliability recovered."
        )

    # --------------------------------------------------
    # EXPLICIT OPERATIONAL ERROR
    # --------------------------------------------------

    elif error_status == 1:

        root_cause = (
            "An operational request-processing error "
            "contributed to service degradation."
        )

        resolution = (
            "Inspect application logs and dependency "
            "health, retry failed requests, and verify "
            "service connectivity."
        )

        outcome = (
            "The request-processing path recovered and "
            "error frequency decreased."
        )

    # --------------------------------------------------
    # RELIABILITY DEGRADATION
    # --------------------------------------------------

    elif reliability < 70:

        root_cause = (
            "Multiple telemetry indicators contributed "
            "to degraded system reliability."
        )

        resolution = (
            "Review latency, confidence, token usage, "
            "and application health together and apply "
            "the corresponding operational mitigation."
        )

        outcome = (
            "Reliability improved after the degraded "
            "telemetry indicators returned toward baseline."
        )

    # --------------------------------------------------
    # GENERAL ANOMALY
    # --------------------------------------------------

    else:

        root_cause = (
            "Telemetry deviated from the established "
            "normal operating pattern."
        )

        resolution = (
            "Review the anomalous telemetry request and "
            "continue monitoring for repeated deviations."
        )

        outcome = (
            "The anomaly was monitored and subsequent "
            "telemetry returned to the expected range."
        )

    return root_cause, resolution, outcome


def seed_memory():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            request_id,
            latency,
            confidence,
            reliability_score,
            error_status

        FROM telemetry

        WHERE LOWER(TRIM(anomaly)) = 'yes'

        ORDER BY request_id
        """
    )

    incidents = cursor.fetchall()

    inserted = 0

    for incident in incidents:

        root_cause, resolution, outcome = (
            determine_resolution(
                float(incident["latency"]),
                float(incident["confidence"]),
                float(
                    incident["reliability_score"]
                ),
                int(incident["error_status"])
            )
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO incident_memory (

                request_id,
                root_cause,
                resolution,
                outcome,
                resolution_status,
                resolved_at
            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                incident["request_id"],
                root_cause,
                resolution,
                outcome,
                "Resolved",
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )
        )

        inserted += 1

    conn.commit()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM incident_memory
        """
    )

    total = cursor.fetchone()[0]

    conn.close()

    print("=" * 65)
    print("MEDINTELOPS HISTORICAL INCIDENT MEMORY")
    print("=" * 65)

    print(
        f"Anomalous incidents processed : "
        f"{len(incidents)}"
    )

    print(
        f"Resolution records generated  : "
        f"{inserted}"
    )

    print(
        f"Total incident memories       : "
        f"{total}"
    )

    print("=" * 65)


if __name__ == "__main__":

    seed_memory()