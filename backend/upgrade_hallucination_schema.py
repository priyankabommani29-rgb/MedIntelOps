import os
import sqlite3

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

NEW_COLUMNS = {

    "hallucination_score":
        "REAL",

    "hallucination_risk":
        "TEXT",

    "hallucination_type":
        "TEXT",

    "evidence_score":
        "REAL",

    "supported_claims":
        "INTEGER",

    "unsupported_claims":
        "INTEGER",

    "contradicted_claims":
        "INTEGER"
}


def column_exists(
    cursor,
    table,
    column
):

    cursor.execute(
        f"PRAGMA table_info({table})"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    return column in columns


def main():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    print("=" * 65)
    print("MEDINTELOPS HALLUCINATION SCHEMA")
    print("=" * 65)

    for column, datatype in NEW_COLUMNS.items():

        if not column_exists(
            cursor,
            "telemetry",
            column
        ):

            cursor.execute(
                f"""
                ALTER TABLE telemetry
                ADD COLUMN
                {column}
                {datatype}
                """
            )

            print(
                f"Added: {column}"
            )

        else:

            print(
                f"Exists: {column}"
            )

    conn.commit()

    print("\nUPDATED SCHEMA\n")

    cursor.execute(
        "PRAGMA table_info(telemetry)"
    )

    for row in cursor.fetchall():

        print(row)

    conn.close()

    print("\nDone.")


if __name__ == "__main__":

    main()