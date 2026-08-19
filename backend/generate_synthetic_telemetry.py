import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "database/logs.db"

random.seed(42)

medical_examples = [
    (
        "What are common symptoms of iron deficiency anemia?",
        "Common symptoms can include fatigue, weakness, dizziness, pale skin, and shortness of breath."
    ),
    (
        "What are common symptoms associated with dehydration?",
        "Symptoms may include thirst, dry mouth, reduced urination, dizziness, and fatigue."
    ),
    (
        "What are common symptoms of seasonal influenza?",
        "Influenza commonly causes fever, cough, muscle aches, fatigue, headache, and sometimes sore throat."
    ),
    (
        "What are common risk factors for hypertension?",
        "Risk factors can include age, family history, high sodium intake, obesity, physical inactivity, and excessive alcohol use."
    ),
    (
        "What are common symptoms associated with migraine?",
        "Migraine may cause moderate to severe headache, nausea, sensitivity to light, and sensitivity to sound."
    ),
    (
        "What are common symptoms of low blood sugar?",
        "Symptoms of hypoglycemia may include sweating, trembling, hunger, dizziness, confusion, and weakness."
    ),
    (
        "What lifestyle measures are commonly recommended for maintaining cardiovascular health?",
        "Common measures include regular physical activity, a balanced diet, avoiding tobacco, maintaining a healthy weight, and managing blood pressure."
    ),
    (
        "What are common symptoms associated with asthma?",
        "Asthma may cause wheezing, shortness of breath, chest tightness, and coughing."
    ),
    (
        "What are common symptoms of a urinary tract infection?",
        "Common symptoms can include painful urination, frequent urination, urgency, and lower abdominal discomfort."
    ),
    (
        "What are common signs associated with vitamin B12 deficiency?",
        "Possible signs include fatigue, weakness, numbness or tingling, balance problems, and changes in the tongue."
    ),
]


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def generate_metrics(request_id):

    # --------------------------------------------------
    # PHASE 1 — NORMAL OPERATION
    # --------------------------------------------------

    if request_id <= 120:

        latency = random.gauss(1.4, 0.25)
        confidence = random.gauss(0.93, 0.025)
        reliability = random.gauss(94, 2)

        anomaly_probability = 0.01

    # --------------------------------------------------
    # PHASE 2 — LATENCY DEGRADATION
    # --------------------------------------------------

    elif request_id <= 170:

        progress = (request_id - 120) / 50

        latency = random.gauss(
            1.5 + (progress * 2.0),
            0.35
        )

        confidence = random.gauss(
            0.92 - (progress * 0.06),
            0.03
        )

        reliability = random.gauss(
            93 - (progress * 10),
            3
        )

        anomaly_probability = 0.08 + progress * 0.12

    # --------------------------------------------------
    # PHASE 3 — RELIABILITY DEGRADATION
    # --------------------------------------------------

    elif request_id <= 210:

        progress = (request_id - 170) / 40

        latency = random.gauss(
            3.2 + progress,
            0.45
        )

        confidence = random.gauss(
            0.86 - progress * 0.12,
            0.04
        )

        reliability = random.gauss(
            82 - progress * 18,
            4
        )

        anomaly_probability = 0.25 + progress * 0.35

    # --------------------------------------------------
    # PHASE 4 — CRITICAL INCIDENT CLUSTER
    # --------------------------------------------------

    elif request_id <= 240:

        latency = random.gauss(5.8, 0.8)
        confidence = random.gauss(0.61, 0.08)
        reliability = random.gauss(55, 8)

        anomaly_probability = 0.82

    # --------------------------------------------------
    # PHASE 5 — RECOVERY
    # --------------------------------------------------

    elif request_id <= 330:

        progress = (request_id - 240) / 90

        latency = random.gauss(
            4.5 - progress * 2.8,
            0.4
        )

        confidence = random.gauss(
            0.70 + progress * 0.20,
            0.035
        )

        reliability = random.gauss(
            65 + progress * 27,
            3
        )

        anomaly_probability = max(
            0.03,
            0.35 - progress * 0.32
        )

    # --------------------------------------------------
    # PHASE 6 — SECOND INCIDENT
    # --------------------------------------------------

    elif request_id <= 370:

        latency = random.gauss(4.8, 0.7)
        confidence = random.gauss(0.69, 0.07)
        reliability = random.gauss(63, 7)

        anomaly_probability = 0.62

    # --------------------------------------------------
    # PHASE 7 — STABLE OPERATION
    # --------------------------------------------------

    else:

        latency = random.gauss(1.5, 0.3)
        confidence = random.gauss(0.92, 0.03)
        reliability = random.gauss(93, 2.5)

        anomaly_probability = 0.02

    latency = clamp(latency, 0.4, 8.0)
    confidence = clamp(confidence, 0.30, 0.99)
    reliability = clamp(reliability, 25, 99)

    anomaly = random.random() < anomaly_probability

    # Strong degradation should also trigger anomaly status.
    if reliability < 60 or confidence < 0.55 or latency > 6.0:
        anomaly = True

    return latency, confidence, reliability, anomaly


def calculate_severity(reliability, anomaly):

    if not anomaly:
        return "Low"

    if reliability < 55:
        return "Critical"

    if reliability < 70:
        return "High"

    if reliability < 82:
        return "Medium"

    return "Low"


def generate_data():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # We want this synthetic dataset to be reproducible.
    cursor.execute("DELETE FROM telemetry")
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='telemetry'"
    )

    start_time = datetime.now() - timedelta(hours=50)

    for request_id in range(1, 501):

        latency, confidence, reliability, anomaly_bool = (
            generate_metrics(request_id)
        )

        prompt, response = random.choice(medical_examples)

        tokens_used = random.randint(80, 650)

        # Incident periods tend to generate larger responses.
        if 171 <= request_id <= 240 or 331 <= request_id <= 370:
            tokens_used += random.randint(150, 450)

        timestamp = (
            start_time +
            timedelta(minutes=request_id * 6)
        )

        severity = calculate_severity(
            reliability,
            anomaly_bool
        )

        error_status = 0

        # Some anomalous requests simulate operational errors.
        if anomaly_bool and random.random() < 0.18:
            error_status = 1

        anomaly = "Yes" if anomaly_bool else "No"

        cursor.execute(
            """
            INSERT INTO telemetry (
                request_id,
                latency,
                tokens_used,
                confidence,
                error_status,
                anomaly,
                reliability_score,
                severity,
                timestamp,
                prompt_text,
                response_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                round(latency, 3),
                tokens_used,
                round(confidence, 3),
                error_status,
                anomaly,
                round(reliability, 2),
                severity,
                timestamp.isoformat(timespec="seconds"),
                prompt,
                response
            )
        )

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM telemetry")
    count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM telemetry
        WHERE anomaly = 'Yes'
        """
    )

    anomalies = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM telemetry
        WHERE severity = 'Critical'
        """
    )

    critical = cursor.fetchone()[0]

    conn.close()

    print("=" * 60)
    print("MEDINTELOPS SYNTHETIC TELEMETRY")
    print("=" * 60)
    print(f"Records generated : {count}")
    print(f"Anomalies         : {anomalies}")
    print(f"Critical incidents: {critical}")
    print("=" * 60)


if __name__ == "__main__":
    generate_data()