import sqlite3
import json
import os

import pandas as pd
import numpy as np
import shap

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

MODEL_FEATURES = [
    "latency",
    "tokens_used",
    "confidence",
    "error_status",
]


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_telemetry():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT
            request_id,
            latency,
            tokens_used,
            confidence,
            error_status,
            anomaly
        FROM telemetry
        """,
        conn
    )

    conn.close()

    return df


# ---------------------------------------------------------
# PREPARE DATA
# ---------------------------------------------------------

def prepare_data(df):

    data = df.copy()

    data["anomaly_target"] = (
        data["anomaly"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({
            "yes": 1,
            "no": 0
        })
    )

    data = data.dropna(
        subset=MODEL_FEATURES + ["anomaly_target"]
    )

    X = data[MODEL_FEATURES].copy()

    y = data["anomaly_target"].astype(int)

    return data, X, y


# ---------------------------------------------------------
# CREATE SHAP TABLE
# ---------------------------------------------------------

def create_shap_table():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS shap_explanations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            request_id INTEGER NOT NULL,

            predicted_anomaly INTEGER,

            anomaly_probability REAL,

            latency_shap REAL,

            tokens_used_shap REAL,

            confidence_shap REAL,

            error_status_shap REAL,

            strongest_feature TEXT,

            strongest_contribution REAL,

            explanation_text TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# NORMALIZE SHAP OUTPUT
# ---------------------------------------------------------

def extract_positive_class_shap(
    shap_values,
    row_index,
    feature_count
):

    values = np.asarray(shap_values)

    # Possible shape:
    # (samples, features, classes)
    if values.ndim == 3:

        return values[
            row_index,
            :,
            1
        ]

    # Possible shape:
    # (samples, features)
    if values.ndim == 2:

        return values[row_index]

    # Defensive fallback
    flattened = values.reshape(-1)

    if len(flattened) >= feature_count:
        return flattened[:feature_count]

    raise ValueError(
        "Unexpected SHAP output shape: "
        f"{values.shape}"
    )


# ---------------------------------------------------------
# HUMAN-READABLE EXPLANATION
# ---------------------------------------------------------

def create_explanation(
    feature_values,
    contributions
):

    contribution_map = dict(
        zip(
            MODEL_FEATURES,
            contributions
        )
    )

    strongest_feature = max(
        contribution_map,
        key=lambda feature: abs(
            contribution_map[feature]
        )
    )

    strongest_value = float(
        contribution_map[strongest_feature]
    )

    friendly_names = {
        "latency": "response latency",
        "tokens_used": "token usage",
        "confidence": "model confidence",
        "error_status": "error status",
    }

    direction = (
        "increased"
        if strongest_value > 0
        else "reduced"
    )

    explanation = (
        f"The strongest factor was "
        f"{friendly_names[strongest_feature]}. "
        f"Its SHAP contribution {direction} "
        f"the model's predicted anomaly risk."
    )

    return (
        strongest_feature,
        strongest_value,
        explanation
    )


# ---------------------------------------------------------
# TRAIN MODEL + GENERATE SHAP
# ---------------------------------------------------------

def train_and_explain():

    print("=" * 65)
    print("MEDINTELOPS SHAP ANOMALY EXPLAINABILITY")
    print("=" * 65)

    df = load_telemetry()

    data, X, y = prepare_data(df)

    print(f"Telemetry records: {len(data)}")
    print(f"Normal records   : {(y == 0).sum()}")
    print(f"Anomaly records  : {(y == 1).sum()}")

    # -----------------------------------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42,
            stratify=y
        )
    )

    # -----------------------------------------------------
    # RANDOM FOREST
    # -----------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    # -----------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    print("\nMODEL PERFORMANCE")
    print("-" * 65)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print("\nClassification Report")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    # -----------------------------------------------------
    # SHAP EXPLAINER
    # -----------------------------------------------------

    print("Generating SHAP explanations...")

    explainer = shap.TreeExplainer(
        model
    )

    shap_values = explainer.shap_values(
        X
    )

    all_probabilities = model.predict_proba(
        X
    )[:, 1]

    all_predictions = model.predict(
        X
    )

    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    create_shap_table()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Regenerate explanations each run.
    cursor.execute(
        "DELETE FROM shap_explanations"
    )

    for row_position in range(len(X)):

        contributions = (
            extract_positive_class_shap(
                shap_values,
                row_position,
                len(MODEL_FEATURES)
            )
        )

        feature_values = X.iloc[
            row_position
        ].to_dict()

        (
            strongest_feature,
            strongest_contribution,
            explanation
        ) = create_explanation(
            feature_values,
            contributions
        )

        request_id = int(
            data.iloc[row_position][
                "request_id"
            ]
        )

        shap_dict = dict(
            zip(
                MODEL_FEATURES,
                contributions
            )
        )

        cursor.execute(
            """
            INSERT INTO shap_explanations (

                request_id,
                predicted_anomaly,
                anomaly_probability,

                latency_shap,
                tokens_used_shap,
                confidence_shap,
                error_status_shap,

                strongest_feature,
                strongest_contribution,
                explanation_text
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,

                int(
                    all_predictions[
                        row_position
                    ]
                ),

                float(
                    all_probabilities[
                        row_position
                    ]
                ),

                float(
                    shap_dict["latency"]
                ),

                float(
                    shap_dict["tokens_used"]
                ),

                float(
                    shap_dict["confidence"]
                ),

                float(
                    shap_dict["error_status"]
                ),

                strongest_feature,

                strongest_contribution,

                explanation
            )
        )

    conn.commit()
    conn.close()

    print("\nSHAP explanations saved.")
    print(
        f"Explanations generated: {len(X)}"
    )

    print("=" * 65)


if __name__ == "__main__":

    train_and_explain()