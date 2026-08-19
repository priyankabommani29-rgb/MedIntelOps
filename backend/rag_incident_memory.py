import os
import sqlite3
from typing import Dict, List, Any

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

SQLITE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "logs.db"
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "database",
    "chroma_incident_memory"
)

COLLECTION_NAME = "medintelops_incidents"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# RAG INCIDENT MEMORY
# ============================================================

class RAGIncidentMemory:

    def __init__(self):

        print("Initializing MedIntelOps Incident Memory...")

        # ----------------------------------------------------
        # Sentence Transformer
        # ----------------------------------------------------

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

        # ----------------------------------------------------
        # Persistent ChromaDB
        # ----------------------------------------------------

        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = (
            self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={
                    "description":
                    "MedIntelOps historical incident memory"
                }
            )
        )

        print(
            "Incident memory initialized successfully."
        )

    # ========================================================
    # INCIDENT → TEXT
    # ========================================================

    def build_incident_document(
    self,
    incident: Dict[str, Any]
    ) -> str:

     latency = float(
        incident.get("latency", 0) or 0
    )

     confidence = float(
        incident.get("confidence", 0) or 0
    )

     reliability = float(
        incident.get("reliability_score", 0) or 0
    )

     error_status = int(
        incident.get("error_status", 0) or 0
    )

     severity = str(
        incident.get("severity", "Unknown")
    )

    # ----------------------------------------------------
    # Convert numerical telemetry into semantic
    # operational categories.
    # ----------------------------------------------------

     if latency >= 5:
        latency_pattern = "severe latency spike"
     elif latency >= 3:
        latency_pattern = "elevated response latency"
     else:
        latency_pattern = "normal response latency"

     if confidence < 0.60:
        confidence_pattern = "critically low model confidence"
     elif confidence < 0.75:
        confidence_pattern = "reduced model confidence"
     else:
        confidence_pattern = "stable model confidence"

     if reliability < 55:
        reliability_pattern = "critical reliability degradation"
     elif reliability < 70:
        reliability_pattern = "major reliability degradation"
     elif reliability < 85:
        reliability_pattern = "moderate reliability degradation"
     else:
        reliability_pattern = "stable system reliability"

     if error_status == 1:
        error_pattern = "operational error present"
     else:
        error_pattern = "no explicit operational error"

     document = f"""
Medical AI operational incident.

Severity: {severity}.

Latency condition: {latency_pattern}.
Measured latency: {latency:.3f} seconds.

Confidence condition: {confidence_pattern}.
Measured model confidence: {confidence:.3f}.

Reliability condition: {reliability_pattern}.
Measured reliability score: {reliability:.2f} percent.

Error condition: {error_pattern}.

Incident pattern:
{severity} medical AI incident involving
{latency_pattern},
{confidence_pattern},
{reliability_pattern},
and {error_pattern}.
"""

     return document.strip()

    # ========================================================
    # EMBEDDING
    # ========================================================

    def create_embedding(
        self,
        text: str
    ) -> List[float]:

        embedding = self.embedding_model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    # ========================================================
    # STORE INCIDENT
    # ========================================================

    def store_incident(
        self,
        incident: Dict[str, Any]
    ):

        request_id = str(
            incident["request_id"]
        )

        document = self.build_incident_document(
            incident
        )

        embedding = self.create_embedding(
            document
        )

        metadata = {
            "request_id": request_id,

            "severity": str(
                incident.get(
                    "severity",
                    "Unknown"
                )
            ),

            "latency": float(
                incident.get(
                    "latency",
                    0
                ) or 0
            ),

            "confidence": float(
                incident.get(
                    "confidence",
                    0
                ) or 0
            ),

            "reliability_score": float(
                incident.get(
                    "reliability_score",
                    0
                ) or 0
            ),

            "error_status": int(
                incident.get(
                    "error_status",
                    0
                ) or 0
            ),

            "timestamp": str(
                incident.get(
                    "timestamp",
                    ""
                )
            )
        }

        # UPSERT prevents duplicate request IDs
        self.collection.upsert(
            ids=[request_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )

    # ========================================================
    # RETRIEVE SIMILAR INCIDENTS
    # ========================================================

    def search_similar_incidents(
        self,
        incident: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        collection_count = self.collection.count()

        if collection_count == 0:
            return []

        document = self.build_incident_document(
            incident
        )

        embedding = self.create_embedding(
            document
        )

        number_results = min(
            top_k,
            collection_count
        )

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=number_results,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        similar_incidents = []

        ids = results.get("ids", [[]])[0]
        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        for (
            incident_id,
            incident_document,
            metadata,
            distance
        ) in zip(
            ids,
            documents,
            metadatas,
            distances
        ):

            similarity = max(
                0.0,
                min(
                    1.0,
                    1.0 - float(distance)
                )
            )

            similar_incidents.append({
                "request_id":
                    incident_id,

                "similarity":
                    similarity,

                "document":
                    incident_document,

                "metadata":
                    metadata
            })

        return similar_incidents

    # ========================================================
    # MEMORY STATS
    # ========================================================

    def get_memory_stats(self):

        return {
            "stored_incidents":
                self.collection.count(),

            "collection":
                COLLECTION_NAME,

            "embedding_model":
                EMBEDDING_MODEL_NAME,

            "embedding_dimension":
                self.embedding_model
                .get_sentence_embedding_dimension(),

            "storage_path":
                CHROMA_PATH
        }


# ============================================================
# LOAD INCIDENTS FROM SQLITE
# ============================================================

def load_incidents_from_sqlite():

    conn = sqlite3.connect(
        SQLITE_PATH
    )

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

        WHERE LOWER(TRIM(anomaly)) = 'yes'

        ORDER BY request_id
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# BUILD INITIAL MEMORY
# ============================================================

def build_initial_memory():

    print("=" * 65)
    print("MEDINTELOPS RAG INCIDENT MEMORY")
    print("=" * 65)

    incidents = (
        load_incidents_from_sqlite()
    )

    print(
        f"Anomalous incidents found: "
        f"{len(incidents)}"
    )

    memory = RAGIncidentMemory()

    for index, incident in enumerate(
        incidents,
        start=1
    ):

        memory.store_incident(
            incident
        )

        if (
            index % 10 == 0
            or index == len(incidents)
        ):

            print(
                f"Stored "
                f"{index}/{len(incidents)} "
                f"incidents"
            )

    stats = memory.get_memory_stats()

    print("\nMEMORY STATISTICS")
    print("-" * 65)

    print(
        "Stored incidents     :",
        stats["stored_incidents"]
    )

    print(
        "Embedding model      :",
        stats["embedding_model"]
    )

    print(
        "Embedding dimension  :",
        stats["embedding_dimension"]
    )

    print(
        "Collection           :",
        stats["collection"]
    )

    print("\nRAG incident memory built successfully.")

    print("=" * 65)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_initial_memory()