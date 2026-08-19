import sqlite3


DB_PATH = "database/logs.db"


# ==================================================
# DECISION ENGINE
# ==================================================

def classify_incident(row):

    final_hallucination = row["final_hallucination_score"] or 0
    contradiction = row["nli_contradiction"] or 0
    reliability = row["reliability_score"] or 100

    anomaly = str(row["anomaly"]).lower()
    severity = str(row["severity"]).lower()

    # ----------------------------------------------
    # CRITICAL
    # ----------------------------------------------

    if (
        final_hallucination >= 0.60
        or contradiction >= 0.80
        or (
            severity == "critical"
            and reliability < 50
        )
    ):

        return (
            "Critical",
            "Immediate Action",
            "High hallucination/contradiction risk or severe reliability degradation."
        )

    # ----------------------------------------------
    # INVESTIGATE
    # ----------------------------------------------

    elif (
        final_hallucination >= 0.40
        or contradiction >= 0.50
        or anomaly == "anomaly"
        or severity == "high"
        or reliability < 70
    ):

        return (
            "Investigate",
            "Investigation Required",
            "Anomaly or elevated reliability/hallucination risk detected."
        )

    # ----------------------------------------------
    # MONITOR
    # ----------------------------------------------

    elif (
        final_hallucination >= 0.20
        or contradiction >= 0.20
        or reliability < 85
    ):

        return (
            "Monitor",
            "Monitor",
            "Moderate operational or medical-response risk detected."
        )

    # ----------------------------------------------
    # NORMAL
    # ----------------------------------------------

    else:

        return (
            "Normal",
            "No Immediate Action",
            "System behaviour is within acceptable operating conditions."
        )


# ==================================================
# MAIN
# ==================================================

def main():

    print("=" * 65)
    print("MEDINTELOPS AUTOMATED INCIDENT DECISION ENGINE")
    print("=" * 65)

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # ----------------------------------------------
    # ADD DECISION COLUMNS
    # ----------------------------------------------

    existing_columns = [
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(telemetry)"
        ).fetchall()
    ]

    columns = {
        "decision_class": "TEXT",
        "decision_action": "TEXT",
        "decision_reason": "TEXT"
    }

    for column, datatype in columns.items():

        if column not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE telemetry
                ADD COLUMN {column} {datatype}
                """
            )

            print(f"Added: {column}")

    conn.commit()

    # ----------------------------------------------
    # LOAD TELEMETRY
    # ----------------------------------------------

    rows = cursor.execute(
        """
        SELECT *
        FROM telemetry
        """
    ).fetchall()

    print()
    print(f"Processing Records : {len(rows)}")

    # ----------------------------------------------
    # CLASSIFY
    # ----------------------------------------------

    counts = {
        "Normal": 0,
        "Monitor": 0,
        "Investigate": 0,
        "Critical": 0
    }

    for row in rows:

        decision_class, action, reason = classify_incident(row)

        cursor.execute(
            """
            UPDATE telemetry

            SET
                decision_class = ?,
                decision_action = ?,
                decision_reason = ?

            WHERE request_id = ?
            """,

            (
                decision_class,
                action,
                reason,
                row["request_id"]
            )
        )

        counts[decision_class] += 1

    conn.commit()

    # ----------------------------------------------
    # RESULTS
    # ----------------------------------------------

    print()
    print("DECISION RESULTS")
    print("-" * 65)

    print(
        f"Normal       : {counts['Normal']}"
    )

    print(
        f"Monitor      : {counts['Monitor']}"
    )

    print(
        f"Investigate  : {counts['Investigate']}"
    )

    print(
        f"Critical     : {counts['Critical']}"
    )

    print("-" * 65)

    print("Decision engine completed successfully.")

    conn.close()


if __name__ == "__main__":
    main()